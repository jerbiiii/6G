#!/bin/bash
# usage: at6-resume.sh <dossier>   (lit ~/6g-lab/at6/<dossier>)
D=~/6g-lab/at6/$1
echo "== IP / phases"; cat $D/ips.txt $D/phases.txt
echo "== Actions (toutes fenetres)"; tail -n +2 $D/controle.csv | cut -d, -f6 | sort | uniq -c
echo "== Par phase (bornes approx. 0-31 / 31-62 / 62-93 s ; fenetres apres 93 s exclues)"
awk -F, 'NR>1 { sub(/\r$/,"",$6); t=$1; if (t>93) next; p=(t<=31)?1:(t<=62)?2:3; n[p]++; s[p]+=$2; if ($6=="baisse") b[p]++; if ($6=="hausse") h[p]++; lim[p]=$5; if (!(p in mn) || $5<mn[p]) mn[p]=$5; if ($5>mx[p]) mx[p]=$5 } END { for (p=1;p<=3;p++) printf "phase %d : %d fenetres, latence moy %.2f ms, %d baisses, %d hausses, limite min/max %d/%d, fin de phase %d\n", p, n[p], s[p]/n[p], b[p], h[p], mn[p], mx[p], lim[p] }' $D/controle.csv
echo "== Video (SUM)"; grep -h SUM $D/video_phase*.txt | grep -E "sender|receiver"
echo "== IoT"; grep -E "sender|receiver" $D/iot.txt
echo "== URLLC"; grep -E "sender|receiver" $D/urllc.txt
echo "== CPU"; grep -E "Moyenne|Average" $D/cpu.txt
echo "== tc"; for u in ue1 ue2 ue3; do echo "$u: $(sudo ip netns exec $u tc qdisc show dev uesimtun0)"; done
