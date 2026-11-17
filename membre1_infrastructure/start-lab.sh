#!/bin/bash
# Relance complete du labo apres un redemarrage de la VM (a lancer SANS sudo)
echo "== Nettoyage"
for s in gnb ue1 ue2 ue3 srv1 srv2 srv3; do tmux kill-session -t $s 2>/dev/null; done
sudo pkill nr-ue; sudo pkill nr-gnb; pkill iperf3
echo "== Coeur Open5GS"
sudo bash ~/6g-lab/setup-slices-tun.sh
sudo systemctl restart 'open5gs-*'
sleep 6
for s in mongod open5gs-amfd open5gs-smfd open5gs-upfd open5gs-nssfd; do echo "$s: $(systemctl is-active $s)"; done
ip -br addr show | grep ogstun
echo "== Namespaces"
sudo bash ~/6g-lab/setup-netns.sh 3
echo "== gNB"
tmux new -d -s gnb "cd ~/UERANSIM && ./build/nr-gnb -c config/open5gs-gnb.yaml"
sleep 5
echo "NG Setup reussi : $(tmux capture-pane -pt gnb | grep -c 'NG Setup procedure is successful')"
echo "== UEs"
for i in 1 2 3; do
  tmux new -d -s ue$i "cd ~/UERANSIM && sudo ip netns exec ue$i ./build/nr-ue -c config/ue$i.yaml"
  sleep 5
done
echo "== Serveurs iperf3"
tmux new -d -s srv1 "iperf3 -s -B 10.45.0.1 -p 5201"
tmux new -d -s srv2 "iperf3 -s -B 10.47.0.1 -p 5202"
tmux new -d -s srv3 "iperf3 -s -B 10.46.0.1 -p 5203"
sleep 2
echo "== Verification"
for i in 1 2 3; do echo "ue$i: $(sudo ip netns exec ue$i ip -4 -o addr show uesimtun0 | awk '{print $4}')"; done
sudo ip netns exec ue1 ping -I uesimtun0 -c 2 10.45.0.1 | tail -n 2
sudo ip netns exec ue3 ping -I uesimtun0 -c 2 10.46.0.1 | tail -n 2
sudo ip netns exec ue2 ping -I uesimtun0 -c 2 10.47.0.1 | tail -n 2
tmux ls
