#!/bin/bash
set -e

echo "=========================================================="
echo "=== [AT10] COMPARAISON 6G : EDGE vs FOG vs CLOUD       ==="
echo "=========================================================="

echo ""
echo "--- 1. Vérification des Services et Pods AT10 ---"
sudo k3s kubectl get pods -n at10-edge-fog-cloud -o wide
sudo k3s kubectl get svc -n at10-edge-fog-cloud -o wide

EDGE_IP="172.31.34.222"
FOG_IP="172.31.38.166"
CLOUD_IP="172.31.47.81"

echo ""
echo "--- 2. Test Fonctionnel des 3 Niveaux (/health) ---"
echo -n "Edge  (vm-ran:30081)  : "
curl -s http://${EDGE_IP}:30081/health || echo "Erreur Edge"
echo ""
echo -n "Fog   (vm-upf:30082)  : "
curl -s http://${FOG_IP}:30082/health || echo "Erreur Fog"
echo ""
echo -n "Cloud (vm-cp:30083)   : "
curl -s http://${CLOUD_IP}:30083/health || echo "Erreur Cloud"
echo ""

echo ""
echo "--- 3. Temps de Traitement Calcul 6G (/compute) ---"
echo -n "Edge Processing  : "
curl -s http://${EDGE_IP}:30081/compute
echo ""
echo -n "Fog Processing   : "
curl -s http://${FOG_IP}:30082/compute
echo ""
echo -n "Cloud Processing : "
curl -s http://${CLOUD_IP}:30083/compute
echo ""

echo ""
echo "--- 4. Mesure Comparative de Latence Réseau (RTT en ms) ---"
measure_latency() {
    local target=$1
    local sum=0
    for i in {1..5}; do
        t=$(curl -o /dev/null -s -w "%{time_total}\n" "$target")
        t_ms=$(awk "BEGIN {print $t * 1000}")
        sum=$(awk "BEGIN {print $sum + $t_ms}")
    done
    avg=$(awk "BEGIN {printf \"%.2f\", $sum / 5}")
    echo "$avg ms"
}

echo -n "Latence moyenne vers EDGE  (vm-ran): "
measure_latency "http://${EDGE_IP}:30081/health"

echo -n "Latence moyenne vers FOG   (vm-upf): "
measure_latency "http://${FOG_IP}:30082/health"

echo -n "Latence moyenne vers CLOUD (vm-cp) : "
measure_latency "http://${CLOUD_IP}:30083/health"

echo ""
echo "--- 5. Utilisation des Ressources Kubernetes ---"
echo "[Pods AT10]"
sudo k3s kubectl top pods -n at10-edge-fog-cloud
echo ""
echo "[Nodes CPU & RAM]"
sudo k3s kubectl top nodes

echo ""
echo "=== [AT10] ATELIER 10 VALIDÉ AVEC SUCCÈS ==="
