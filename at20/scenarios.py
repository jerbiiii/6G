#!/usr/bin/env python3
"""
AT20 Digital Twin — Scénarios What-If paramétrables
S1: Explosion trafic eMBB (+250 Mbps)
S2: Charge critique URLLC (80 Mbps)
S3: Panne gNB-B, reroutage UE
S4: Réduction CPU UPF (35%)
Sortie: data/predictions.csv
"""
import csv, json, os
from datetime import datetime, timezone
from twin import DigitalTwin

PREDICTIONS_CSV = "/home/ubuntu/at20/data/predictions.csv"
dt = DigitalTwin()

SCENARIOS = {
    "S1_embb_burst": {
        "description": "Explosion trafic eMBB +250 Mbps (burst charge extrême)",
        "params": {"ue_count": 10, "traffic_mbps": 250, "cpu_upf_pct": 70, "cpu_cp_pct": 55, "cpu_ran_pct": 40},
        "user_adjustable": True,
    },
    "S2_urllc_critical": {
        "description": "Charge critique URLLC — 80 Mbps trafic temps-réel",
        "params": {"ue_count": 5, "traffic_mbps": 80, "cpu_upf_pct": 50, "cpu_cp_pct": 35, "cpu_ran_pct": 25},
        "user_adjustable": True,
    },
    "S3_gnb_b_failure": {
        "description": "Panne gNB-B — UE reroutés vers gNB-A et gNB-C (+50% charge)",
        "params": {"ue_count": 15, "traffic_mbps": 120, "cpu_upf_pct": 60, "cpu_cp_pct": 65, "cpu_ran_pct": 75},
        "user_adjustable": True,
    },
    "S4_upf_cpu_reduction": {
        "description": "Réduction CPU UPF à 35% (limitation ressource)",
        "params": {"ue_count": 5, "traffic_mbps": 50, "cpu_upf_pct": 35, "cpu_cp_pct": 30, "cpu_ran_pct": 15},
        "user_adjustable": True,
    },
}

BASELINE = {"ue_count": 0, "traffic_mbps": 0, "cpu_upf_pct": 2, "cpu_cp_pct": 5, "cpu_ran_pct": 1}

def run_all_scenarios():
    ts = datetime.now(timezone.utc)
    results = []
    baseline_pred = dt.predict(**BASELINE)

    print(f"\n{'='*72}")
    print(f"  AT20 Digital Twin — Scénarios What-If")
    print(f"  Horodatage : {ts.isoformat()[:19]}")
    print(f"  Référence baseline : latence {baseline_pred['predicted_latency_combined_ms']:.4f} ms")
    print(f"{'='*72}\n")

    for sid, scenario in SCENARIOS.items():
        pred = dt.predict(**scenario["params"])
        delta_lat = pred["predicted_latency_combined_ms"] - baseline_pred["predicted_latency_combined_ms"]
        delta_pct = (delta_lat / max(baseline_pred["predicted_latency_combined_ms"], 0.001)) * 100

        row = {
            "timestamp": ts.isoformat(),
            "scenario_id": sid,
            "description": scenario["description"],
            **{f"param_{k}": v for k, v in scenario["params"].items()},
            "baseline_latency_ms": baseline_pred["predicted_latency_combined_ms"],
            "predicted_latency_mm1_ms": pred["predicted_latency_mm1_ms"],
            "predicted_latency_ridge_ms": pred["predicted_latency_ridge_ms"],
            "predicted_latency_combined_ms": pred["predicted_latency_combined_ms"],
            "delta_latency_ms": round(delta_lat, 4),
            "delta_latency_pct": round(delta_pct, 1),
            "predicted_loss_pct": pred["predicted_loss_pct"],
            "predicted_cpu_upf_pct": pred["predicted_cpu_upf_pct"],
            "sla_violations_count": len(pred["sla_violations"]),
            "sla_violations": " | ".join(pred["sla_violations"]) if pred["sla_violations"] else "NONE",
            "queue_stable": pred["queue_stable"],
            "ridge_confidence": pred["ridge_confidence"],
            "source": "digital_twin_prediction",
        }
        results.append(row)

        print(f"  {sid}: {scenario['description'][:55]}")
        print(f"    Paramètres : {scenario['params']}")
        print(f"    Latence prédite : {pred['predicted_latency_combined_ms']:.4f} ms  (Δ={delta_lat:+.4f} ms, {delta_pct:+.1f}%)")
        print(f"    Perte: {pred['predicted_loss_pct']:.2f}%  |  CPU UPF: {pred['predicted_cpu_upf_pct']:.1f}%")
        if pred["sla_violations"]:
            for v in pred["sla_violations"]:
                print(f"    ⚠️  {v}")
        else:
            print(f"    ✅ Aucune violation SLA")
        print()

    # Écrire predictions.csv
    os.makedirs(os.path.dirname(PREDICTIONS_CSV), exist_ok=True)
    with open(PREDICTIONS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"  → {PREDICTIONS_CSV} écrit ({len(results)} scénarios)")
    print(f"{'='*72}")
    return results

if __name__ == "__main__":
    run_all_scenarios()
