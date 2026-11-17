#!/usr/bin/env python3
# Usage : sudo-less ; python3 controleur_slices.py <duree_s> <dossier_sortie>
# Env : START (Mbit/s, defaut 300), LAT_HIGH (2.0 ms), LAT_LOW (1.2 ms)
import subprocess, sys, time, re, os, csv
DUREE = int(sys.argv[1]) if len(sys.argv) > 1 else 60
OUT = sys.argv[2] if len(sys.argv) > 2 else "at6/dynamique"
START = int(os.environ.get("START", "300"))
LAT_HIGH = float(os.environ.get("LAT_HIGH", "2.0"))
LAT_LOW = float(os.environ.get("LAT_LOW", "1.2"))
RMIN, RMAX, STEP, NLOW = 20, 300, 20, 3
os.makedirs(OUT, exist_ok=True)

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout

def set_rate(r):
    sh(f"sudo ip netns exec ue1 tc qdisc replace dev uesimtun0 root tbf rate {r}mbit burst 256kb latency 50ms")

def mesure():
    out = sh("sudo ip netns exec ue3 ping -n -I uesimtun0 -c 20 -i 0.1 -W 1 10.46.0.1")
    l = re.search(r"([\d.]+)% packet loss", out)
    r = re.search(r"= ([\d.]+)/([\d.]+)/([\d.]+)/", out)
    loss = float(l.group(1)) if l else 100.0
    avg = float(r.group(2)) if r else float("nan")
    mx = float(r.group(3)) if r else float("nan")
    return avg, mx, loss

rate = START
set_rate(rate)
low = 0
t0 = time.time()
with open(f"{OUT}/controle.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["t_s", "lat_moy_ms", "lat_max_ms", "perte_pct", "limite_mbit", "action"])
    while time.time() - t0 < DUREE:
        avg, mx, loss = mesure()
        action = "aucune"
        if loss > 0 or avg != avg or avg > LAT_HIGH:
            new = max(RMIN, int(rate * 0.75)); low = 0
            if new != rate: action = "baisse"
            rate = new
        elif avg < LAT_LOW:
            low += 1
            if low >= NLOW:
                new = min(RMAX, rate + STEP); low = 0
                if new != rate: action = "hausse"
                rate = new
        else:
            low = 0
        if action != "aucune":
            set_rate(rate)
        w.writerow([round(time.time() - t0, 1), avg, mx, loss, rate, action]); f.flush()
        print(f"t={time.time()-t0:5.1f}s lat={avg} max={mx} perte={loss}% limite={rate} {action}", flush=True)
