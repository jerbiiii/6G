#!/bin/bash
set -euo pipefail
SSH_KEY="/home/ubuntu/.ssh/6g-team-key.pem"
VMRAN="172.31.34.222"
VMCP="172.31.47.81"

echo "=== Étape 1 : Création du profil rogue UE sur vmran ==="
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" ubuntu@"$VMRAN" "cat << 'ROGUE' > ~/UERANSIM/config/ue_rogue.yaml
supi: 'imsi-999700000000999'
mcc: '999'
mnc: '70'
protectionScheme: 0
key: '00000000000000000000000000000000'
op: '00000000000000000000000000000000'
opType: 'OPC'
amf: '8000'
gnbSearchList:
  - 172.31.34.222
sessions:
  - type: 'IPv4'
    apn: 'internet'
    slice:
      sst: 1
ROGUE"

echo "=== Étape 2 : Lancement gNB sur vmran ==="
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" ubuntu@"$VMRAN" "tmux kill-session -t at27-gnb 2>/dev/null || true; tmux new -d -s at27-gnb 'cd ~/UERANSIM && ./build/nr-gnb -c config/open5gs-gnb.yaml'"
sleep 3

echo "=== Étape 3 : Test Authentification Légitime (IMSI-999700000000001) ==="
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" ubuntu@"$VMRAN" "timeout 8 ./UERANSIM/build/nr-ue -c ./UERANSIM/config/ue1.yaml > /tmp/ue_normal.log 2>&1 || true"
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" ubuntu@"$VMCP" "sudo journalctl -u open5gs-amfd -n 40 --no-pager" > /home/ubuntu/at27/captures/auth_normal.log
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" ubuntu@"$VMRAN" "cat /tmp/ue_normal.log" >> /home/ubuntu/at27/captures/auth_normal.log

echo "=== Étape 4 : Test Authentification Rogue / Invalide (IMSI-999700000000999) ==="
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" ubuntu@"$VMRAN" "timeout 8 ./UERANSIM/build/nr-ue -c ./UERANSIM/config/ue_rogue.yaml > /tmp/ue_rogue.log 2>&1 || true"
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" ubuntu@"$VMCP" "sudo journalctl -u open5gs-amfd -n 40 --no-pager" > /home/ubuntu/at27/captures/auth_invalid.log
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" ubuntu@"$VMRAN" "cat /tmp/ue_rogue.log" >> /home/ubuntu/at27/captures/auth_invalid.log

echo "=== Étape 5 : Nettoyage gNB ==="
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY" ubuntu@"$VMRAN" "tmux kill-session -t at27-gnb 2>/dev/null || true; pkill -f nr-ue 2>/dev/null || true"

echo "=== Synthèse Authentification ==="
grep -E "Registration|Authentication|reject|failed|complete|associated" /home/ubuntu/at27/captures/auth_normal.log | tail -10 || true
echo "--- Rejet Rogue ---"
grep -E "Registration|Authentication|reject|failed|Unknown|404|imsi-999700000000999" /home/ubuntu/at27/captures/auth_invalid.log | tail -10 || true
