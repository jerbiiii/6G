#!/bin/bash
# Usage: ./at6-run.sh <dossier> <flux_video>
OUT=~/6g-lab/at6/$1; P=${2:-2}; D=30; mkdir -p $OUT
for i in 1 2 3; do eval UE$i=$(sudo ip netns exec ue$i ip -4 -o addr show uesimtun0 | awk '{print $4}' | cut -d/ -f1); done
sar -u 1 $D > $OUT/cpu.txt &
sudo ip netns exec ue1 iperf3 -c 10.45.0.1 -p 5201 -B $UE1 -P $P -t $D > $OUT/embb_video.txt &
sudo ip netns exec ue2 iperf3 -c 10.47.0.1 -p 5202 -B $UE2 -u -b 100k -l 100 -t $D > $OUT/mmtc_iot.txt &
sudo ip netns exec ue3 iperf3 -c 10.46.0.1 -p 5203 -B $UE3 -u -b 2M -l 200 -t $D > $OUT/urllc_udp.txt &
sudo ip netns exec ue3 ping -I uesimtun0 -i 0.2 -c $((D*5)) 10.46.0.1 > $OUT/urllc_ping.txt &
wait
echo "Termine : $OUT"
