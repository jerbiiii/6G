#!/usr/bin/env python3
# Controleur QoS dynamique : adapte la limite de debit de la video (ue1)
# selon la latence de la navigation (ue3). Usage: python3 controleur_qos.py [duree_s]
import subprocess, re, time, sys, csv, os

DUREE = int(sys.argv[1]) if len(sys.argv) > 1 else 30
OUT = os.path.expanduser("~/6g-lab/at5_dynamique/controle.csv")
RATE_MAX, RATE_MIN = 300, 20
HIGH, LOW = 2.0, 1.4

def mesurer():
    r = subprocess.run(["sudo", "ip", "netns", "exec", "ue3", "ping", "-I", "uesimtun0",
                        "-i", "0.2", "-c", "10", "10.45.0.1"], capture_output=True, text=True)
    m = re.search(r"= [\d.]+/([\d.]+)/", r.stdout)
    l = re.search(r"([\d.]+)% packet loss", r.stdout)
    return (float(m.group(1)) if m else None), (float(l.group(1)) if l else 100.0)

def set_rate(rate):
    subprocess.run(["sudo", "ip", "netns", "exec", "ue1", "tc", "qdisc", "replace", "dev", "uesimtun0",
                    "root", "tbf", "rate", f"{rate}mbit", "burst", "256kb", "latency", "50ms"], check=True)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
rate, ok, rows = RATE_MAX, 0, []
set_rate(rate)
debut = time.time()
while time.time() - debut < DUREE:
    t = round(time.time() - debut, 1)
    avg, loss = mesurer()
    avant = rate
    if avg is None or loss > 0 or avg > HIGH:
        rate = max(RATE_MIN, int(rate * 0.75)); ok = 0
    elif avg < LOW:
        ok += 1
        if ok >= 2:
            rate = min(RATE_MAX, rate + 20); ok = 0
    else:
        ok = 0
    if rate != avant:
        set_rate(rate)
    rows.append([t, avg, loss, avant, rate])
    print(f"t={t:5.1f}s latence={avg} ms perte={loss}% limite {avant} -> {rate} Mbit/s")

with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["temps_s", "latence_moy_ms", "perte_pct", "limite_avant_mbit", "limite_apres_mbit"])
    w.writerows(rows)
print("CSV:", OUT)
