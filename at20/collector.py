#!/usr/bin/env python3
"""
AT20 Digital Twin - Collecteur de métriques réseau 6G
Fréquence: 5s | Sources: ping réel, kubectl top SSH, SSH vmran/vmupf
Nœuds réels: vm-cp (172.31.47.81), vm-ran (172.31.34.222), vm-upf (172.31.38.166)
ogstun UP: 10.45.0.1 (SST1 eMBB)
ogstun2: ABSENT | ogstun3: ABSENT
iperf3 server: UNAVAILABLE (dans pod CNF, non joignable depuis hôte)
"""

import csv
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone

METRICS_PATH = "/home/ubuntu/at20/data/metrics.csv"
SSH_KEY     = "/home/ubuntu/.ssh/6g-team-key.pem"
SSH_OPTS    = "-o StrictHostKeyChecking=no -o ConnectTimeout=5"
VMCP        = "172.31.47.81"
VMRAN       = "172.31.34.222"
VMUPF       = "172.31.38.166"
OGSTUN_IP   = "10.45.0.1"    # SST1 eMBB - confirmé UP
INTERVAL    = 5              # secondes

COLUMNS = [
    "timestamp",
    "latency_ms", "latency_target", "latency_source",
    "loss_pct", "loss_source",
    "throughput_mbps", "throughput_source",
    "cpu_vmcp_pct", "cpu_vmran_pct", "cpu_vmupf_pct",
    "ram_vmcp_mb", "ram_vmran_mb", "ram_vmupf_mb",
    "resources_source",
    "ue_count", "ue_source",
    "handover_count", "mobility_source",
    "slice_embb_latency_ms", "slice_embb_source",
    "slice_urllc_latency_ms", "slice_urllc_source",
    "slice_mmtc_latency_ms", "slice_mmtc_source",
]

running = True

def handle_signal(signum, frame):
    global running
    print(f"\n[collector] Signal {signum} reçu - arrêt propre", flush=True)
    running = False

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

def run_cmd(cmd, timeout=8):
    """Execute une commande locale, retourne (stdout, returncode)."""
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", -1
    except Exception as e:
        return f"ERROR:{e}", -1

def ssh_cmd(host, remote_cmd, timeout=10):
    """Execute une commande sur un hôte distant via SSH, retourne (stdout, returncode)."""
    cmd = f'ssh {SSH_OPTS} -i {SSH_KEY} ubuntu@{host} "{remote_cmd}"'
    return run_cmd(cmd, timeout=timeout)

def collect_latency():
    """Ping vers ogstun 10.45.0.1 (SST1). Fallback: ping vmupf 172.31.38.166."""
    out, rc = run_cmd(f"ping -c 3 -W 1 {OGSTUN_IP}", timeout=10)
    target = OGSTUN_IP
    source = "real"
    latency = "NaN"
    loss = "NaN"

    if rc == 0 and "rtt" in out:
        # rtt min/avg/max/mdev = 0.029/0.040/0.052/0.011 ms
        m = re.search(r"rtt min/avg/max/mdev = [\d.]+/([\d.]+)/", out)
        if m:
            latency = m.group(1)
        # packet loss
        m2 = re.search(r"(\d+(?:\.\d+)?)% packet loss", out)
        if m2:
            loss = m2.group(1)
    else:
        # Fallback vers vmupf IP privée
        out2, rc2 = run_cmd(f"ping -c 3 -W 1 {VMUPF}", timeout=10)
        target = f"{VMUPF} (DIRECT)"
        source = "real_fallback"
        if rc2 == 0 and "rtt" in out2:
            m = re.search(r"rtt min/avg/max/mdev = [\d.]+/([\d.]+)/", out2)
            if m:
                latency = m.group(1)
            m2 = re.search(r"(\d+(?:\.\d+)?)% packet loss", out2)
            if m2:
                loss = m2.group(1)
        else:
            source = "unavailable"
            loss = "NaN"

    return latency, target, source, loss

def collect_throughput():
    """iperf3 non disponible (serveur dans pod CNF non joignable depuis hôte)."""
    return "0", "UNAVAILABLE"

def collect_resources():
    """kubectl top nodes sur vmcp. Format: NAME CPU(cores) CPU% MEMORY(bytes) MEMORY%"""
    out, rc = ssh_cmd(VMCP, "sudo k3s kubectl top nodes --no-headers 2>/dev/null", timeout=15)
    
    nodes = {
        "vm-cp":  {"cpu": "NaN", "ram": "NaN"},
        "vm-ran": {"cpu": "NaN", "ram": "NaN"},
        "vm-upf": {"cpu": "NaN", "ram": "NaN"},
    }
    source = "real"
    
    if rc != 0 or not out or "UNAVAILABLE" in out or "TIMEOUT" in out or "ERROR" in out:
        source = "unavailable"
        return nodes, source

    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        name = parts[0]
        # parts: NAME  CPU(cores)  CPU%  MEMORY(bytes)  MEMORY%
        cpu_str = parts[2].rstrip("%")   # CPU%
        ram_str = parts[3]               # MEMORY e.g. "1827Mi"
        
        try:
            cpu_val = float(cpu_str)
        except:
            cpu_val = None
        
        ram_val = None
        m = re.match(r"(\d+(?:\.\d+)?)([KMGi]*)", ram_str)
        if m:
            v = float(m.group(1))
            unit = m.group(2).upper().replace("I", "")
            if unit in ("G",):
                v *= 1024
            elif unit in ("K",):
                v /= 1024
            ram_val = round(v)
        
        for key in nodes:
            if key in name:
                nodes[key]["cpu"] = str(cpu_val) if cpu_val is not None else "NaN"
                nodes[key]["ram"] = str(ram_val) if ram_val is not None else "NaN"
                break
    
    return nodes, source

def collect_ue_count():
    """Compte les interfaces uesimtun* sur vmran."""
    out, rc = ssh_cmd(VMRAN, "ip -br a | grep -c uesimtun || echo 0", timeout=8)
    source = "real"
    if rc != 0 or not out.strip().isdigit():
        return "0", "unavailable"
    return out.strip(), source

def collect_slice_latency(ip, label):
    """Ping vers une IP de slice ogstun. Retourne latency_ms ou NaN."""
    out, rc = run_cmd(f"ping -c 3 -W 1 {ip}", timeout=10)
    if rc == 0 and "rtt" in out:
        m = re.search(r"rtt min/avg/max/mdev = [\d.]+/([\d.]+)/", out)
        if m:
            return m.group(1), "real"
    return "NaN", "unavailable"

def write_row(writer, row):
    writer.writerow(row)

def main():
    global running
    
    os.makedirs(os.path.dirname(METRICS_PATH), exist_ok=True)
    
    file_exists = os.path.isfile(METRICS_PATH)
    f = open(METRICS_PATH, "a", newline="")
    writer = csv.DictWriter(f, fieldnames=COLUMNS)
    if not file_exists:
        writer.writeheader()
        f.flush()
    
    iteration = 0
    print(f"[collector] Démarrage - écriture dans {METRICS_PATH}", flush=True)
    print(f"[collector] Cible ogstun: {OGSTUN_IP} | Intervalle: {INTERVAL}s", flush=True)
    # ogstun2/ogstun3 absents (vérifiés lors de la découverte)
    OGSTUN2_UP = False
    OGSTUN3_UP = False
    
    while running:
        t0 = time.time()
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        try:
            # 1. Latence & perte
            lat, lat_target, lat_src, loss = collect_latency()
            
            # 2. Débit iperf3
            tput, tput_src = collect_throughput()
            
            # 3. Ressources (kubectl top)
            nodes, res_src = collect_resources()
            
            # 4. UEs actifs
            ue_count, ue_src = collect_ue_count()
            
            # 5. Slices
            # eMBB = ogstun 10.45.0.1 (même mesure que latency)
            embb_lat = lat
            embb_src = lat_src
            
            # URLLC = ogstun2 10.46.0.1 (absent)
            if OGSTUN2_UP:
                urllc_lat, urllc_src = collect_slice_latency("10.46.0.1", "URLLC")
            else:
                urllc_lat, urllc_src = "NaN", "unavailable"
            
            # mMTC = ogstun3 10.47.0.1 (absent)
            if OGSTUN3_UP:
                mmtc_lat, mmtc_src = collect_slice_latency("10.47.0.1", "mMTC")
            else:
                mmtc_lat, mmtc_src = "NaN", "unavailable"
            
            row = {
                "timestamp": ts,
                "latency_ms": lat,
                "latency_target": lat_target,
                "latency_source": lat_src,
                "loss_pct": loss,
                "loss_source": "real",
                "throughput_mbps": tput,
                "throughput_source": tput_src,
                "cpu_vmcp_pct": nodes["vm-cp"]["cpu"],
                "cpu_vmran_pct": nodes["vm-ran"]["cpu"],
                "cpu_vmupf_pct": nodes["vm-upf"]["cpu"],
                "ram_vmcp_mb": nodes["vm-cp"]["ram"],
                "ram_vmran_mb": nodes["vm-ran"]["ram"],
                "ram_vmupf_mb": nodes["vm-upf"]["ram"],
                "resources_source": res_src,
                "ue_count": ue_count,
                "ue_source": ue_src,
                "handover_count": "0",
                "mobility_source": "GENERATED",
                "slice_embb_latency_ms": embb_lat,
                "slice_embb_source": embb_src,
                "slice_urllc_latency_ms": urllc_lat,
                "slice_urllc_source": urllc_src,
                "slice_mmtc_latency_ms": mmtc_lat,
                "slice_mmtc_source": mmtc_src,
            }
            
            write_row(writer, row)
            f.flush()
            iteration += 1
            
            elapsed = time.time() - t0
            print(f"[collector] iter={iteration} ts={ts} lat={lat}ms loss={loss}% cpu_cp={nodes['vm-cp']['cpu']}% ue={ue_count} ({elapsed:.1f}s)", flush=True)
            
        except Exception as e:
            print(f"[collector] ERREUR iter={iteration}: {e}", flush=True)
        
        # Attendre le reste de l'intervalle
        elapsed = time.time() - t0
        wait = max(0, INTERVAL - elapsed)
        deadline = time.time() + wait
        while running and time.time() < deadline:
            time.sleep(0.1)
    
    f.close()
    print(f"[collector] Arrêté proprement après {iteration} itérations.", flush=True)

if __name__ == "__main__":
    main()
