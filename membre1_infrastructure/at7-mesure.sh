#!/bin/bash
# usage: at7-mesure.sh <nom>   (resultats dans ~/6g-lab/at7/<nom>)
D=~/6g-lab/at7/$1; mkdir -p $D
snap(){ lxc exec $1 -- bash -c 'echo $(grep usage_usec /sys/fs/cgroup/cpu.stat | cut -d" " -f2) $(cat /sys/fs/cgroup/memory.current) $(cat /sys/class/net/eth0/statistics/rx_bytes) $(cat /sys/class/net/eth0/statistics/tx_bytes)'; }
UE=$(lxc exec node-ran -- ip -4 -o addr show uesimtun0 | awk '{print $4}' | cut -d/ -f1)
[ -z "$UE" ] && { echo "UE absent : lancez ~/6g-lab/start-at7.sh"; exit 1; }
echo "UE=$UE" | tee $D/ue.txt
for n in node-cp node-upf node-ran; do snap $n > $D/$n.avant; done
T=20
lxc exec node-ran -- ping -I uesimtun0 -i 0.2 -c $((T*5)) 10.45.0.1 > $D/ping.txt &
lxc exec node-ran -- iperf3 -c 10.45.0.1 -B $UE -t $T > $D/iperf_tcp.txt
wait
for n in node-cp node-upf node-ran; do snap $n > $D/$n.apres; done
echo "== Resultats ($1, ${T}s)"
for n in node-cp node-upf node-ran; do
  read a1 m1 r1 t1 < $D/$n.avant; read a2 m2 r2 t2 < $D/$n.apres
  echo "$n : CPU $(( (a2-a1)/10000/T )) % d'un coeur (moyenne), memoire $((m2/1048576)) Mo, eth0 rx $(( (r2-r1)/1024 )) Ko, tx $(( (t2-t1)/1024 )) Ko"
done
echo "-- ping"; tail -n 2 $D/ping.txt
echo "-- iperf3 TCP"; grep -E "sender|receiver" $D/iperf_tcp.txt
