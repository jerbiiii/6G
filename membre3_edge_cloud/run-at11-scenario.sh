#!/bin/bash
set -e

LOG_FILE="$HOME/at11-scenario.log"
exec > >(tee "$LOG_FILE") 2>&1

echo "=========================================================="
echo "=== [AT11] DÉPLOIEMENT & VALIDATION ORCHESTRATION 6G   ==="
echo "=========================================================="

echo ""
echo "--- Étape 1 : Déploiement des workloads et services AT11 ---"
kubectl apply -f ~/at11-deploy.yaml

echo ""
echo "--- Attente du Rollout des Pods ---"
kubectl rollout status deployment/app-edge -n at11-orch --timeout=60s
kubectl rollout status deployment/app-fog -n at11-orch --timeout=60s
kubectl rollout status deployment/app-cloud -n at11-orch --timeout=60s
kubectl rollout status deployment/workload-app -n at11-orch --timeout=60s

echo ""
echo "--- Vérification initiale des Pods et Services ---"
kubectl get pods -n at11-orch -o wide
kubectl get svc -n at11-orch -o wide

EDGE_IP="172.31.34.222"
FOG_IP="172.31.38.166"
CLOUD_IP="172.31.47.81"

echo ""
echo "--- Test de connectivité initiale HTTP (/health) ---"
echo -n "Workload App (vm-ran:30090) : "
curl -s http://${EDGE_IP}:30090/health | grep -E "status|service|node|tier" || echo "Erreur"
echo -n "App Edge     (vm-ran:30091) : "
curl -s http://${EDGE_IP}:30091/health | grep -E "status|service|node|tier" || echo "Erreur"
echo -n "App Fog      (vm-upf:30092) : "
curl -s http://${FOG_IP}:30092/health | grep -E "status|service|node|tier" || echo "Erreur"
echo -n "App Cloud    (vm-cp:30093)  : "
curl -s http://${CLOUD_IP}:30093/health | grep -E "status|service|node|tier" || echo "Erreur"

echo ""
echo "--- Mesure de latence RTT initiale (baseline) ---"
measure_rtt() {
    local url=$1
    local total=0
    for i in {1..3}; do
        rtt=$(curl -o /dev/null -s -w "%{time_total}\n" "$url")
        rtt_ms=$(awk "BEGIN {print $rtt * 1000}")
        total=$(awk "BEGIN {print $total + $rtt_ms}")
    done
    avg=$(awk "BEGIN {printf \"%.2f\", $total / 3}")
    echo "$avg ms"
}

echo -n "RTT vers Edge (vm-ran:30091)       : "; measure_rtt "http://${EDGE_IP}:30091/health"
echo -n "RTT vers Fog  (vm-upf:30092)       : "; measure_rtt "http://${FOG_IP}:30092/health"
echo -n "RTT vers Cloud (vm-cp:30093)       : "; measure_rtt "http://${CLOUD_IP}:30093/health"
echo -n "RTT vers Workload (NodePort 30090) : "; measure_rtt "http://${EDGE_IP}:30090/health"

echo ""
echo "--- Étape 2 & 3 : Exécution de l'Orchestrateur Intelligent Python ---"
python3 ~/at11-orchestrator.py

echo ""
echo "--- Étape 4 : Vérification post-orchestration ---"
echo "[État des Pods at11-orch]"
kubectl get pods -n at11-orch -o wide

echo ""
echo "[Métriques CPU & Mémoire actuelles]"
kubectl top nodes

echo ""
echo "--- Mesure de latence après rééquilibrage ---"
echo -n "RTT vers Workload (NodePort 30090)  : "; measure_rtt "http://${EDGE_IP}:30090/health"
echo -n "RTT vers Fog Service (vm-upf:30092) : "; measure_rtt "http://${FOG_IP}:30092/health"

echo ""
echo "=== [AT11] SCÉNARIO D'ORCHESTRATION TERMINÉ AVEC SUCCÈS ==="
