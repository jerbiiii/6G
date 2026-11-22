#!/usr/bin/env python3
"""
AT27 - Tests de Robustesse Réseau 6G (Scan de ports & Burst UDP contrôlé)
"""
import socket
import time
import subprocess
import json

TARGET_CP = "172.31.47.81"
TARGET_UPF = "172.31.38.166"

results = {
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "tests": []
}

print("[1/3] Test Scan de Ports vers Control-Plane (vmcp)...")
ports_to_test = [22, 80, 443, 6443, 7777, 8805, 10250, 38412]
open_ports = []
scan_start = time.time()
for p in ports_to_test:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)
    try:
        res = s.connect_ex((TARGET_CP, p))
        if res == 0:
            open_ports.append(p)
    except Exception:
        pass
    finally:
        s.close()
scan_duration = round(time.time() - scan_start, 3)
results["tests"].append({
    "name": "Port Scan Control-Plane",
    "target": TARGET_CP,
    "tested_ports": ports_to_test,
    "open_ports": open_ports,
    "duration_s": scan_duration,
    "status": "COMPLETED"
})
print(f"  -> Scan terminé en {scan_duration}s. Ports ouverts détectés: {open_ports}")

print("[2/3] Test Flood UDP contrôlé vers UPF N3 (port 2152)...")
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
payload = b"X" * 512
nb_packets = 1000
burst_start = time.time()
for _ in range(nb_packets):
    udp_sock.sendto(payload, (TARGET_UPF, 2152))
burst_duration = round(time.time() - burst_start, 4)
udp_sock.close()
throughput_pps = round(nb_packets / burst_duration, 1) if burst_duration > 0 else 0
results["tests"].append({
    "name": "Controlled UDP Burst N3",
    "target": f"{TARGET_UPF}:2152",
    "packets_sent": nb_packets,
    "packet_size_bytes": 512,
    "duration_s": burst_duration,
    "rate_pps": throughput_pps,
    "status": "COMPLETED"
})
print(f"  -> {nb_packets} paquets émis en {burst_duration}s ({throughput_pps} pps)")

print("[3/3] Vérification de l'intégrité et stabilité du cœur réseau après les tests...")
SSH_KEY = "/home/ubuntu/.ssh/6g-team-key.pem"
cmd_cp = f"ssh -o StrictHostKeyChecking=no -i {SSH_KEY} ubuntu@{TARGET_CP} 'systemctl is-active open5gs-amfd open5gs-smfd'"
status_cp = subprocess.check_output(cmd_cp, shell=True, text=True).strip().splitlines()
cmd_upf = f"ssh -o StrictHostKeyChecking=no -i {SSH_KEY} ubuntu@{TARGET_UPF} 'systemctl is-active open5gs-upfd'"
status_upf = subprocess.check_output(cmd_upf, shell=True, text=True).strip()

core_stable = all(s == "active" for s in status_cp) and (status_upf == "active")
results["core_health"] = {
    "amfd": status_cp[0] if len(status_cp) > 0 else "unknown",
    "smfd": status_cp[1] if len(status_cp) > 1 else "unknown",
    "upfd": status_upf,
    "stable_and_intact": core_stable
}

output_path = "/home/ubuntu/at27/captures/robustness_results.txt"
with open(output_path, "w") as f:
    f.write(json.dumps(results, indent=2))

print(f"  -> AMF: {status_cp[0]}, SMF: {status_cp[1]}, UPF: {status_upf}")
print(f"  -> Stabilité du cœur: {'PARFAITE (100% actif)' if core_stable else 'DÉGRADÉ'}")
print(f"Résultats enregistrés dans {output_path}")
