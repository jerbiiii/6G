#!/bin/bash
# Relance du labo AT7 (coeur reparti sur 3 noeuds LXD) apres un redemarrage de la VM
grep -q "bindIp: 127.0.0.1,10.10.10.1" /etc/mongod.conf || echo "ATTENTION : /etc/mongod.conf sans bindIp 10.10.10.1 (voir avancement.md)"
echo "== Hote : arret des fonctions Open5GS locales (WebUI et MongoDB conserves)"
sudo systemctl stop 'open5gs-*d'
pkill -u $USER iperf3; sudo pkill nr-ue; sudo pkill nr-gnb
for s in gnb ue1 ue2 ue3 srv1 srv2 srv3; do tmux kill-session -t $s 2>/dev/null; done
echo "== Noeuds LXD"
lxc start node-cp node-upf node-ran 2>/dev/null
sleep 8
lxc list -c ns4
lxc exec node-cp -- bash -c 'timeout 3 bash -c "</dev/tcp/10.10.10.1/27017" && echo "MongoDB joignable" || echo "MongoDB INJOIGNABLE"'
echo "== Coeur : services et association N4"
lxc exec node-cp -- bash -c 'for s in nrfd scpd udrd udmd ausfd pcfd nssfd bsfd amfd smfd; do echo -n "$s:$(systemctl is-active open5gs-$s) "; done; echo'
lxc exec node-upf -- bash -c 'echo "upfd: $(systemctl is-active open5gs-upfd)"; ip -br addr show ogstun | cut -c1-60; grep -i associated /var/log/open5gs/upf.log | tail -n 1'
echo "== gNB, UE et serveur iperf3 (noeuds)"
lxc exec node-ran -- tmux kill-server 2>/dev/null
lxc exec node-upf -- tmux kill-server 2>/dev/null
lxc exec node-upf -- tmux new -d -s srv "iperf3 -s -B 10.45.0.1"
lxc exec node-ran -- tmux new -d -s gnb "cd /root/UERANSIM && ./build/nr-gnb -c config/open5gs-gnb.yaml"
sleep 4
lxc exec node-ran -- tmux new -d -s ue1 "cd /root/UERANSIM && ./build/nr-ue -c config/ue1.yaml"
sleep 7
echo "== Verification"
lxc exec node-ran -- ip -4 -o addr show uesimtun0 | awk '{print "UE: " $4}'
lxc exec node-ran -- ping -I uesimtun0 -c 2 10.45.0.1 | tail -n 2
lxc exec node-upf -- ss -ltn | grep 5201
