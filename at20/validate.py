#!/usr/bin/env python3
"""
AT20 Digital Twin — Validation physique : Prédit vs Mesuré
Pour chaque scénario, applique la charge sur le réseau réel,
mesure 60s, compare MAPE et RMSE par métrique.
Sortie : data/comparison.csv
"""
import csv, os, math, subprocess, time, json
from datetime import datetime, timezone
from twin import DigitalTwin
from scenarios import SCENARIOS, BASELINE

COMPARISON_CSV = "/home/ubuntu/at20/data/comparison.csv"
SSH_KEY = "/home/ubuntu/.ssh/6g-team-key.pem"

dt = DigitalTwin()

def ssh(host_ip, cmd, timeout=15):
    full = ["ssh", "-o", "StrictHostKeyChecking=no", "-i", SSH_KEY, f"ubuntu@{host_ip}", cmd]
    try:
        r = subprocess.run(full, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

def measure_real(duration_s=30):
    """Mesure les métriques réelles sur le réseau pendant duration_s secondes."""
    measurements = []
    start = time.time()
    while time.time() - start < duration_s:
        # Latence réelle via ping vers ogstun UPF
        ping_out = subprocess.run(
            ["ping", "-c", "3", "-W", "1", "10.45.0.1"],
            capture_output=True, text=True, timeout=5
        )
        lat = float("nan")
        loss = float("nan")
        for line in ping_out.stdout.splitlines():
            if "avg" in line and "/" in line:
                try:
                    lat = float(line.split("/")[4])
                except Exception:
                    pass
            if "packet loss" in line:
                try:
                    loss = float(line.split("%")[0].split()[-1])
                except Exception:
                    pass
        # CPU réel via kubectl top
        ktops = ssh("172.31.47.81", "sudo k3s kubectl top nodes --no-headers 2>/dev/null")
        cpu_vmcp = cpu_vmran = cpu_vmupf = float("nan")
        if ktops and "ERROR" not in ktops:
            for line in ktops.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0].lower()
                    try:
                        pct = float(parts[1].replace("m", "")) / 10.0
                    except Exception:
                        pct = float("nan")
                    if "cp" in name:
                        cpu_vmcp = pct
                    elif "ran" in name:
                        cpu_vmran = pct
                    elif "upf" in name:
                        cpu_vmupf = pct
        measurements.append({
            "latency_ms": lat,
            "loss_pct": loss,
            "cpu_vmcp_pct": cpu_vmcp,
            "cpu_vmran_pct": cpu_vmran,
            "cpu_vmupf_pct": cpu_vmupf,
        })
        time.sleep(5)
    return measurements

def safe_mean(vals):
    v = [x for x in vals if not math.isnan(x)]
    return sum(v) / len(v) if v else float("nan")

def mape(predicted, measured):
    if math.isnan(predicted) or math.isnan(measured) or measured == 0:
        return float("nan")
    return abs(predicted - measured) / abs(measured) * 100

def rmse(predicted, measured):
    if math.isnan(predicted) or math.isnan(measured):
        return float("nan")
    return math.sqrt((predicted - measured) ** 2)

def apply_scenario_load(scenario_id, params):
    """
    Applique la charge réseau réelle pour un scénario.
    Méthode : injecter du trafic iperf3 UDP vers vmupf depuis la VM 6g.
    La cible ogstun UPF (10.45.0.1) reçoit des paquets UDP.
    """
    traffic_mbps = params.get("traffic_mbps", 0)
    if traffic_mbps > 0:
        # Lancer iperf3 en mode UDP depuis 6g vers vmupf (ogstun 10.45.0.1)
        # Serveur sur vmupf en arrière-plan 60s
        ssh("172.31.38.166", "pkill iperf3 2>/dev/null; nohup iperf3 -s -p 5900 -D 2>/dev/null")
        time.sleep(1)
        # Client depuis 6g (non bloquant)
        load_cmd = f"nohup iperf3 -c 10.45.0.1 -p 5900 -u -b {min(traffic_mbps,100)}M -t 50 >/dev/null 2>&1 &"
        subprocess.Popen(["bash", "-c", load_cmd])
    return True

def restore_initial_state(scenario_id):
    """Rétablit l'état initial après chaque test."""
    subprocess.run(["bash", "-c", "pkill iperf3 2>/dev/null"], capture_output=True)
    ssh("172.31.38.166", "pkill iperf3 2>/dev/null")
    time.sleep(2)

print(f"\n{'='*72}")
print(f"  AT20 — Validation Physique : Prédit vs Mesuré")
print(f"  Horodatage : {datetime.now(timezone.utc).isoformat()[:19]}")
print(f"{'='*72}\n")

# Phase 0 : Mesure baseline
print("  [BASELINE] Mesure de l'état nominal (30s)...")
baseline_pred = dt.predict(**BASELINE)
baseline_real = measure_real(duration_s=30)
baseline_lat_real = safe_mean([m["latency_ms"] for m in baseline_real])
baseline_cpu_real = safe_mean([m["cpu_vmupf_pct"] for m in baseline_real])
print(f"    Baseline réel : latence={baseline_lat_real:.4f} ms, CPU UPF={baseline_cpu_real:.1f}%")
print(f"    Baseline prédit: latence={baseline_pred['predicted_latency_combined_ms']:.4f} ms\n")

comparison_rows = []
for sid, scenario in SCENARIOS.items():
    params = scenario["params"]
    pred = dt.predict(**params)
    print(f"  [{sid}] {scenario['description'][:60]}")
    print(f"    Prédit   : latence={pred['predicted_latency_combined_ms']:.4f} ms, CPU UPF={pred['predicted_cpu_upf_pct']:.1f}%")

    # Appliquer la charge
    apply_scenario_load(sid, params)
    print(f"    Mesure en cours (30s)...")
    real_measures = measure_real(duration_s=30)
    restore_initial_state(sid)

    real_lat = safe_mean([m["latency_ms"] for m in real_measures])
    real_cpu = safe_mean([m["cpu_vmupf_pct"] for m in real_measures])
    real_loss = safe_mean([m["loss_pct"] for m in real_measures])

    print(f"    Mesuré   : latence={real_lat:.4f} ms, CPU UPF={real_cpu:.1f}%, perte={real_loss:.1f}%")

    # MAPE et RMSE
    mape_lat = mape(pred["predicted_latency_combined_ms"], real_lat)
    rmse_lat = rmse(pred["predicted_latency_combined_ms"], real_lat)
    mape_cpu = mape(pred["predicted_cpu_upf_pct"], real_cpu)

    print(f"    MAPE latence : {mape_lat:.1f}%  |  RMSE latence : {rmse_lat:.4f} ms")
    if pred["sla_violations"]:
        print(f"    ⚠️  Violations SLA prédites : {len(pred['sla_violations'])}")
    print()

    comparison_rows.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario_id": sid,
        "description": scenario["description"],
        "predicted_latency_ms": pred["predicted_latency_combined_ms"],
        "measured_latency_ms": round(real_lat, 4),
        "mape_latency_pct": round(mape_lat, 2),
        "rmse_latency_ms": round(rmse_lat, 4),
        "predicted_cpu_upf_pct": pred["predicted_cpu_upf_pct"],
        "measured_cpu_upf_pct": round(real_cpu, 2),
        "mape_cpu_pct": round(mape_cpu, 2),
        "predicted_loss_pct": pred["predicted_loss_pct"],
        "measured_loss_pct": round(real_loss, 2),
        "sla_violations": " | ".join(pred["sla_violations"]) if pred["sla_violations"] else "NONE",
        "source": "real_measurement",
    })

os.makedirs(os.path.dirname(COMPARISON_CSV), exist_ok=True)
with open(COMPARISON_CSV, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(comparison_rows[0].keys()))
    writer.writeheader()
    writer.writerows(comparison_rows)

# Résumé global
mapes = [r["mape_latency_pct"] for r in comparison_rows if not math.isnan(r["mape_latency_pct"])]
rmses = [r["rmse_latency_ms"] for r in comparison_rows if not math.isnan(r["rmse_latency_ms"])]
print(f"  RÉSUMÉ GLOBAL :")
print(f"    MAPE latence moyen : {safe_mean(mapes):.1f}%")
print(f"    RMSE latence moyen : {safe_mean(rmses):.4f} ms")
print(f"    → {COMPARISON_CSV} écrit ({len(comparison_rows)} scénarios)")
print(f"{'='*72}")
