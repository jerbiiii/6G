#!/bin/bash
# test-at10-v2.sh — Mesures Edge/Fog/Cloud depuis l'UE (uesimtun0)
# Version 2: CLOUD routing fixé, iperf3 amélioré

EDGE_IP="172.31.34.222"
FOG_IP="172.31.38.166"
CLOUD_IP="172.31.47.81"

EDGE_PORT="30081"
FOG_PORT="30082"
CLOUD_PORT="30083"

UE_IFACE="uesimtun0"
UE_IP="10.45.0.2"

echo "============================================================"
echo " AT10 — MESURES EDGE / FOG / CLOUD depuis UE (uesimtun0)"
echo " Date : $(date)"
echo " Interface UE : $UE_IFACE ($UE_IP)"
echo "============================================================"
echo ""

# ── Fonction: mesure latence HTTP ─────────────────────────────
measure_latency() {
  local TIER=$1
  local URL=$2
  local TOTAL=0
  local COUNT=0

  echo "--- Latence HTTP $TIER ($URL) ---"
  for i in 1 2 3 4 5; do
    T=$(curl --interface "$UE_IFACE" -o /dev/null -s \
      -w "%{time_total}" \
      --max-time 5 \
      "$URL/health" 2>/dev/null)
    if echo "$T" | grep -qE '^[0-9]+\.[0-9]+$'; then
      echo "  Essai $i : ${T}s"
      TOTAL=$(echo "$TOTAL + $T" | bc -l 2>/dev/null || awk "BEGIN{print $TOTAL + $T}")
      COUNT=$((COUNT + 1))
    else
      echo "  Essai $i : FAIL (timeout)"
    fi
  done

  if [ "$COUNT" -gt 0 ]; then
    AVG=$(awk "BEGIN{printf \"%.4f\", $TOTAL / $COUNT}")
    echo "  Moyenne : ${AVG}s  (${COUNT}/5 succès)"
  else
    echo "  Moyenne : N/A"
  fi
  echo ""
}

# ── Fonction: réponse JSON ─────────────────────────────────────
check_service() {
  local TIER=$1
  local URL=$2
  echo "--- Vérification service $TIER ---"
  RESP=$(curl --interface "$UE_IFACE" -s --max-time 5 "$URL/" 2>/dev/null)
  if [ -n "$RESP" ]; then
    echo "$RESP" | python3 -m json.tool 2>/dev/null || echo "  Réponse: $RESP"
  else
    echo "  [ERREUR] Service $TIER non joignable"
  fi
  echo ""
}

# ── 1. Vérification des services ─────────────────────────────
echo "============================================================"
echo " SECTION 1 — VÉRIFICATION DES SERVICES"
echo "============================================================"
check_service "EDGE"  "http://${EDGE_IP}:${EDGE_PORT}"
check_service "FOG"   "http://${FOG_IP}:${FOG_PORT}"
check_service "CLOUD" "http://${CLOUD_IP}:${CLOUD_PORT}"

# ── 2. Latence RTT HTTP ───────────────────────────────────────
echo "============================================================"
echo " SECTION 2 — LATENCE RTT HTTP (5 essais par tier)"
echo "============================================================"
measure_latency "EDGE"  "http://${EDGE_IP}:${EDGE_PORT}"
measure_latency "FOG"   "http://${FOG_IP}:${FOG_PORT}"
measure_latency "CLOUD" "http://${CLOUD_IP}:${CLOUD_PORT}"

# ── 3. Endpoint /time ─────────────────────────────────────────
echo "============================================================"
echo " SECTION 3 — TIMESTAMP /time PAR TIER"
echo "============================================================"
for TIER_INFO in "EDGE:${EDGE_IP}:${EDGE_PORT}" "FOG:${FOG_IP}:${FOG_PORT}" "CLOUD:${CLOUD_IP}:${CLOUD_PORT}"; do
  TIER=$(echo "$TIER_INFO" | cut -d: -f1)
  IP=$(echo "$TIER_INFO" | cut -d: -f2)
  PORT=$(echo "$TIER_INFO" | cut -d: -f3)
  echo "--- $TIER /time ---"
  RESP=$(curl --interface "$UE_IFACE" -s --max-time 5 "http://${IP}:${PORT}/time" 2>/dev/null)
  if [ -n "$RESP" ]; then
    echo "$RESP" | python3 -m json.tool 2>/dev/null || echo "$RESP"
  else
    echo "  [ERREUR]"
  fi
  echo ""
done

# ── 4. Débit iperf3 TCP ───────────────────────────────────────
echo "============================================================"
echo " SECTION 4 — DÉBIT iperf3 TCP (5s par tier)"
echo "============================================================"

run_iperf() {
  local TIER=$1
  local IP=$2
  echo "--- iperf3 TCP vers $TIER ($IP:5201) ---"
  if command -v iperf3 &>/dev/null; then
    # Lancer le serveur iperf3 en arrière-plan sur la cible si possible
    # Ici on tente une connexion vers le port 5201 standard
    RESULT=$(iperf3 -c "$IP" -t 5 -B "$UE_IP" 2>&1)
    if echo "$RESULT" | grep -q "Mbits/sec"; then
      echo "$RESULT" | grep -E "sender|receiver" | tail -2
    else
      echo "  [iperf3 non joignable sur $IP:5201 — pas de serveur actif]"
      echo "  Alternative: mesure débit via curl..."
      # Mesure débit HTTP approximatif via curl
      T=$(curl --interface "$UE_IFACE" -s --max-time 10 -o /dev/null \
        -w "%{speed_download}:%{time_total}" \
        "http://${IP}:$([ "$TIER" = "EDGE" ] && echo $EDGE_PORT || [ "$TIER" = "FOG" ] && echo $FOG_PORT || echo $CLOUD_PORT)/health" 2>/dev/null)
      SPEED=$(echo "$T" | cut -d: -f1)
      TIME=$(echo "$T" | cut -d: -f2)
      MBPS=$(awk "BEGIN{printf \"%.3f\", $SPEED / 1048576}" 2>/dev/null || echo "N/A")
      echo "  Débit HTTP (curl): ${MBPS} MB/s en ${TIME}s"
    fi
  else
    echo "  [iperf3 non installé sur vm-ran]"
  fi
  echo ""
}

run_iperf "EDGE"  "$EDGE_IP"
run_iperf "FOG"   "$FOG_IP"
run_iperf "CLOUD" "$CLOUD_IP"

# ── 5. Tableau comparatif final ───────────────────────────────
echo "============================================================"
echo " SECTION 5 — TABLEAU COMPARATIF LATENCES (3 mesures)"
echo "============================================================"
printf "%-8s  %-20s  %-8s  %-15s  %-10s\n" "TIER" "ENDPOINT" "PORT" "LATENCE AVG" "STATUT"
printf "%-8s  %-20s  %-8s  %-15s  %-10s\n" "--------" "--------------------" "--------" "---------------" "----------"

for TIER_INFO in "EDGE:${EDGE_IP}:${EDGE_PORT}" "FOG:${FOG_IP}:${FOG_PORT}" "CLOUD:${CLOUD_IP}:${CLOUD_PORT}"; do
  TIER=$(echo "$TIER_INFO" | cut -d: -f1)
  IP=$(echo "$TIER_INFO" | cut -d: -f2)
  PORT=$(echo "$TIER_INFO" | cut -d: -f3)

  TOTAL=0
  COUNT=0
  for i in 1 2 3; do
    T=$(curl --interface "$UE_IFACE" -o /dev/null -s \
      -w "%{time_total}" --max-time 5 \
      "http://${IP}:${PORT}/health" 2>/dev/null)
    if echo "$T" | grep -qE '^[0-9]+\.[0-9]+$'; then
      TOTAL=$(awk "BEGIN{print $TOTAL + $T}")
      COUNT=$((COUNT + 1))
    fi
  done

  if [ "$COUNT" -gt 0 ]; then
    AVG=$(awk "BEGIN{printf \"%.4fs\", $TOTAL / $COUNT}")
    STATUS="OK ($COUNT/3)"
  else
    AVG="N/A"
    STATUS="FAIL"
  fi
  printf "%-8s  %-20s  %-8s  %-15s  %-10s\n" "$TIER" "$IP" "$PORT" "$AVG" "$STATUS"
done

echo ""
echo "============================================================"
echo " SECTION 6 — RESSOURCES KUBERNETES (kubectl top)"
echo "============================================================"
if command -v kubectl &>/dev/null; then
  echo "--- kubectl top nodes ---"
  kubectl top nodes 2>/dev/null || echo "  [metrics-server non disponible]"
  echo ""
  echo "--- kubectl top pods AT10 ---"
  kubectl top pods -n at10-edge-fog-cloud 2>/dev/null || echo "  [metrics-server non disponible]"
  echo ""
  echo "--- Pods AT10 (état) ---"
  kubectl get pods -n at10-edge-fog-cloud -o wide 2>/dev/null
else
  echo "  [kubectl non disponible sur vm-ran — vérification via vm-cp]"
fi

echo ""
echo "============================================================"
echo " AT10 — TESTS TERMINÉS : $(date)"
echo "============================================================"
