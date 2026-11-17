#!/bin/bash
for i in 2 3; do
  ip tuntap add name ogstun$i mode tun 2>/dev/null
  ip link set ogstun$i up
done
ip addr add 10.46.0.1/16 dev ogstun2 2>/dev/null
ip addr add 10.47.0.1/16 dev ogstun3 2>/dev/null
sysctl -w net.ipv4.ip_forward=1
for n in 10.45.0.0/16 10.46.0.0/16 10.47.0.0/16; do
  iptables -t nat -C POSTROUTING -s $n -o enp39s0 -j MASQUERADE 2>/dev/null || \
  iptables -t nat -A POSTROUTING -s $n -o enp39s0 -j MASQUERADE
done
for d in ogstun ogstun2 ogstun3; do
  iptables -C INPUT -i $d -j ACCEPT 2>/dev/null || iptables -I INPUT -i $d -j ACCEPT
  iptables -C FORWARD -i $d -j ACCEPT 2>/dev/null || iptables -I FORWARD -i $d -j ACCEPT
done
