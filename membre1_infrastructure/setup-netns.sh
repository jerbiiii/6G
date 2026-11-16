#!/bin/bash
# Usage: sudo ./setup-netns.sh [N]   (N = nombre d'UEs, 3 par defaut)
N=${1:-3}
for i in $(seq 1 10); do ip netns del ue$i 2>/dev/null; ip link del veth-h$i 2>/dev/null; done
ip link del veth-h 2>/dev/null
ip link del br-ue 2>/dev/null
ip link add br-ue type bridge
ip addr add 10.100.0.1/24 dev br-ue
ip link set br-ue up
for i in $(seq 1 $N); do
  ip netns add ue$i
  ip link add veth-h$i type veth peer name veth-ue$i
  ip link set veth-ue$i netns ue$i
  ip link set veth-h$i master br-ue
  ip link set veth-h$i up
  ip netns exec ue$i ip addr add 10.100.0.$((10+i))/24 dev veth-ue$i
  ip netns exec ue$i ip link set veth-ue$i up
  ip netns exec ue$i ip link set lo up
done
echo "OK: $N namespaces (ue1..ue$N) relies au pont br-ue (10.100.0.1)"
