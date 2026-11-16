#!/bin/bash
# Usage: ./at4-run.sh <baseline|simultane> [duree_s]
MODE=${1:-simultane}; D=${2:-30}
OUT=~/6g-lab/${3:-at4}/$MODE; mkdir -p $OUT; rm -f $OUT/*
for i in 1 2 3; do eval UE$i=$(sudo ip netns exec ue$i ip -4 -o addr show uesimtun0 | awk '{print $4}' | cut -d/ -f1); done
echo "Mode=$MODE duree=${D}s UE1=$UE1 UE2=$UE2 UE3=$UE3"
sar -u 1 $D > $OUT/cpu.txt &
sar -n DEV 1 $D | grep -E "IFACE|ogstun" > $OUT/net.txt &
if [ "$MODE" = "simultane" ]; then
  sudo ip netns exec ue1 iperf3 -c 10.45.0.1 -p 5201 -B $UE1 -P 2 -t $D > $OUT/video.txt &
  sudo ip netns exec ue2 iperf3 -c 10.45.0.1 -p 5202 -B $UE2 -u -b 100k -l 100 -t $D > $OUT/iot.txt &
fi
sudo ip netns exec ue3 iperf3 -c 10.45.0.1 -p 5203 -B $UE3 -u -b 2M -l 200 -t $D > $OUT/nav_udp.txt &
sudo ip netns exec ue3 ping -I uesimtun0 -i 0.2 -c $((D*5)) 10.45.0.1 > $OUT/nav_ping.txt &
wait
echo "===== RESUME ($MODE) ====="
echo "--- Navigation : ping"; tail -n 2 $OUT/nav_ping.txt
echo "--- Navigation : UDP (gigue, pertes)"; grep receiver $OUT/nav_udp.txt
[ -f $OUT/iot.txt ] && { echo "--- IoT : UDP (gigue, pertes)"; grep receiver $OUT/iot.txt; }
[ -f $OUT/video.txt ] && { echo "--- Video : TCP (debit total)"; grep -E "SUM.*(sender|receiver)" $OUT/video.txt; }
echo "--- CPU moyen"; grep Average $OUT/cpu.txt
echo "--- Debit ogstun"; grep Average $OUT/net.txt
