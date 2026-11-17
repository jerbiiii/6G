#!/bin/bash
# usage: at6-charge.sh <dossier>   (résultats dans ~/6g-lab/at6/<dossier>)
D=~/6g-lab/at6/$1
mkdir -p "$D"; rm -f "$D/phases.txt"
ipof(){ sudo ip netns exec "$1" ip -4 -o addr show uesimtun0 | awk '{print $4}' | cut -d/ -f1; }
IP1=$(ipof ue1); IP2=$(ipof ue2); IP3=$(ipof ue3)
echo "IP : ue1=$IP1 ue2=$IP2 ue3=$IP3" | tee "$D/ips.txt"
cd ~/6g-lab
./at6-policy.sh static > "$D/policy_depart.txt" 2>&1
sar -u 1 96 > "$D/cpu.txt" 2>&1 &
START=${START:-300} python3 controleur_slices.py 96 "at6/$1" > "$D/controleur.log" 2>&1 &
sudo ip netns exec ue2 iperf3 -c 10.47.0.1 -p 5202 -B "$IP2" -u -b 100k -l 100 -t 94 > "$D/iot.txt" 2>&1 &
sudo ip netns exec ue3 iperf3 -c 10.46.0.1 -p 5203 -B "$IP3" -u -b 2M -l 200 -t 94 > "$D/urllc.txt" 2>&1 &
for ph in 1:2 2:6 3:2; do
  n=${ph%%:*}; p=${ph##*:}
  echo "phase $n : $p flux video ($(date +%T))" | tee -a "$D/phases.txt"
  sudo ip netns exec ue1 iperf3 -c 10.45.0.1 -p 5201 -B "$IP1" -P "$p" -t 30 > "$D/video_phase$n.txt" 2>&1
  sleep 1
done
wait
echo fin
