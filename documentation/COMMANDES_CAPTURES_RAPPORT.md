# 📸 GUIDE DES COMMANDES POUR CAPTURES D'ÉCRAN — RAPPORT PROJET 6G

> Ce document regroupe **toutes les commandes prêtes à l'emploi** pour effectuer les captures d'écran nécessaires à l'évaluation et au rapport des ateliers **AT7-bis**, **AT8**, **AT9** et **AT10**.
> 
> **Important :** Exécutez ces commandes depuis votre terminal PowerShell sur Windows. Les accès SSH vers les VM sous-jacentes sont indiqués étape par étape.

---

## 🔑 Rappel des Adresses IP et Connexion SSH

- **VM Principale (Passerelle / Labo) :** IP publique `13.48.10.213` (IP privée `172.31.41.25`)
- **vm-cp (Control-Plane / Master k3s) :** IP privée `172.31.47.81`
- **vm-upf (User-Plane / Agent k3s) :** IP privée `172.31.38.166`
- **vm-ran (gNB + UE / Agent k3s) :** IP privée `172.31.34.222`

---

## 📡 ATELIER 7-bis — Répartition Multi-VM Réelles EC2

### Capture 1 : État des services Open5GS du Plan de Contrôle (vm-cp)
**Où :** Se connecter à `vm-cp` via la VM principale.
```bash
# Dans votre PowerShell Windows :
ssh -i .\6g-team-key.pem ubuntu@13.48.10.213

# Puis depuis la VM principale :
ssh ubuntu@172.31.47.81

# Commande à capturer :
systemctl is-active open5gs-amfd open5gs-smfd open5gs-nrfd open5gs-ausfd open5gs-udmd open5gs-pcfd
sudo journalctl -u open5gs-amfd -n 8 --no-pager | grep -E "NF|AMF|connected"
```
📸 **Ce que montre la capture :** Tous les microservices du Core Control-Plane sont actifs (`active`) et interconnectés.

---

### Capture 2 : Association N4 (PFCP) et interface GTP-U sur l'UPF (vm-upf)
**Où :** Depuis la VM principale, se connecter à `vm-upf`.
```bash
ssh ubuntu@172.31.38.166

# Commande à capturer :
systemctl is-active open5gs-upfd
sudo journalctl -u open5gs-upfd -n 10 --no-pager | grep -i "PFCP"
ip addr show ogstun
```
📸 **Ce que montre la capture :** Le lien N4 entre SMF (`172.31.47.81`) et UPF (`172.31.38.166`) est associé avec succès, et le tunnel `ogstun` (10.45.0.1) est UP.

---

### Capture 3 : Enregistrement de l'UE et Session PDU (vm-ran)
**Où :** Depuis la VM principale, se connecter à `vm-ran`.
```bash
ssh ubuntu@172.31.34.222

# Commande à capturer :
tmux capture-pane -t gnb -p | tail -12
tmux capture-pane -t ue1 -p | tail -15
ip addr show uesimtun0
```
📸 **Ce que montre la capture :** La gNB a validé le NG Setup avec l'AMF, et l'UE a réussi son enregistrement 5G/6G et créé son interface `uesimtun0` avec l'adresse IP `10.45.0.2`.

---

### Capture 4 : Test de Ping UE → UPF à travers le réseau cellulaire (vm-ran)
**Où :** Toujours sur `vm-ran`.
```bash
# Commande à capturer :
ping -c 5 -I uesimtun0 10.45.0.1
```
📸 **Ce que montre la capture :** 0% de perte de paquets et une latence RTT très faible (~1.4 ms) à travers les VM EC2.

---

### Capture 5 : Débit Réseau Réel 5G/6G iperf3 TCP (835 Mbit/s)
**Où :**
1. Sur `vm-upf` (dans un terminal), s'assurer que le serveur iperf3 est prêt :
```bash
nohup /usr/bin/iperf3 -s -B 10.45.0.1 -p 5201 -D > /tmp/iperf-server.log 2>&1
```
2. Sur `vm-ran` (dans un autre terminal), lancer le test :
```bash
iperf3 -c 10.45.0.1 -B 10.45.0.2 -p 5201 -t 10
```
📸 **Ce que montre la capture :** Débit soutenu de **835 Mbit/s** sur de vraies VM AWS, soit +127% par rapport aux conteneurs LXD.

---

## ☸️ ATELIER 8 — Orchestration Cloud-Native Kubernetes (k3s)

### Capture 6 : État du Cluster K3s multi-nœuds (vm-cp)
**Où :** Sur `vm-cp`.
```bash
ssh ubuntu@172.31.47.81

# Commande à capturer :
sudo k3s kubectl get nodes -o wide
```
📸 **Ce que montre la capture :** Les 3 nœuds (`vm-cp`, `vm-ran`, `vm-upf`) sont en statut `Ready` avec la version v1.37.2 et le runtime containerd.

---

### Capture 7 : Déploiement et Service dans le namespace `open5gs` (vm-cp)
**Où :** Sur `vm-cp`.
```bash
# Commande à capturer :
sudo k3s kubectl get pods -n open5gs -o wide
sudo k3s kubectl get svc -n open5gs -o wide
```
📸 **Ce que montre la capture :** Le microservice `web-6g` déployé avec son adresse ClusterIP interne (10.43.6.34) et son pod actif sur l'un des nœuds agents.

---

### Capture 8 : Scalabilité dynamique (Auto-Scaling 1 → 3 répliques) (vm-cp)
**Où :** Sur `vm-cp`.
```bash
# Lancer le scaling à 3 répliques :
sudo k3s kubectl scale deployment web-6g --replicas=3 -n open5gs

# Commande à capturer :
sudo k3s kubectl get pods -n open5gs -o wide
```
📸 **Ce que montre la capture :** Kubernetes répartit automatiquement un pod sur chaque nœud physique (`vm-cp`, `vm-ran`, `vm-upf`), démontrant la résilience et la distribution géographique.

---

### Capture 9 : Surveillance des Ressources Nœuds (`kubectl top nodes`) (vm-cp)
**Où :** Sur `vm-cp`.
```bash
# Commande à capturer :
sudo k3s kubectl top nodes
```
📸 **Ce que montre la capture :** Utilisation CPU et mémoire équilibrée sur l'ensemble du cluster k3s.

---

## 📦 ATELIER 9 — Conteneurisation des Fonctions Réseau (CNF 6G)

### Capture 10 : Écosystème CNF 6G complet (`cnf-6g`) (vm-cp)
**Où :** Sur `vm-cp`.
```bash
# Commande à capturer :
sudo k3s kubectl get pods -n cnf-6g -o wide
sudo k3s kubectl get svc -n cnf-6g -o wide
```
📸 **Ce que montre la capture :** Les 3 fonctions conteneurisées (`cnf-core-service` sur `vm-cp`, `cnf-ran-generator` sur `vm-ran`, et `cnf-upf-service` sur `vm-upf`) actives avec leurs adresses IP de pods et de services.

---

### Capture 11 : Validation Globale Automatisée d'AT9 (Script de Référence)
**Où :** Sur `vm-cp`.
```bash
# Commande à capturer :
bash ~/run-at9-full-eval.sh
```
📸 **Ce que montre cette capture majeure :**
1. Résolution CoreDNS interne réussie pour `cnf-core-service` et `cnf-upf-service`.
2. Appel API HTTP SBI du plan de contrôle (`/health` renvoyant `{"status": "ACTIVE", "nf": "6G-Core-ControlPlane", "node": "vm-cp"}`).
3. Ping inter-pods via Flannel Overlay avec **0.469 ms** de latence et 0% de perte.
4. Test de bande passante iperf3 TCP atteignant **7.90 Gbits/sec** inter-VM avec 0 retransmission.
5. Empreinte de ressources ultra-faible (Green CNF : 1 à 11 MiB par Pod).

---

### Capture 12 : Métriques Détaillées CPU / Mémoire par Pod CNF
**Où :** Sur `vm-cp`.
```bash
# Commande à capturer :
sudo k3s kubectl top pods -n cnf-6g
```
📸 **Ce que montre la capture :** L'efficacité énergétique et la légèreté des microservices 6G conteneurisés par rapport à des VM traditionnelles.


---

## 🌐 ATELIER 10 — Edge, Fog et Cloud Computing

### Capture 13 : Déploiement multi-niveaux K8s (NodePort Edge / Fog / Cloud) (vm-cp)
**Où :** Se connecter à `vm-cp` via la VM principale.
```bash
# Dans votre PowerShell Windows :
ssh -i .\6g-team-key.pem ubuntu@13.48.10.213

# Depuis la VM principale :
ssh ubuntu@172.31.47.81

# Commande à capturer :
sudo k3s kubectl get pods -n at10-edge-fog-cloud -o wide
sudo k3s kubectl get svc -n at10-edge-fog-cloud -o wide
```
📸 **Ce que montre la capture :** Les 3 services déployés avec leurs `NodePort` respectifs (30081 Edge sur `vm-ran`, 30082 Fog sur `vm-upf`, 30083 Cloud sur `vm-cp`).

---

### Capture 14 : Test de traitement calcul 6G et latence globale (vm-cp)
**Où :** Sur `vm-cp`.
```bash
# Commande à capturer :
bash ~/test-at10.sh
```
📸 **Ce que montre la capture :**
1. Requêtes fonctionnelles `/health` pour Edge, Fog et Cloud avec identification du nœud d'exécution.
2. Temps de calcul `/compute` mesuré sur chaque tier (~0.4 ms).
3. Comparaison de latence RTT progressive (Edge < Fog < Cloud).
4. Utilisation CPU et mémoire des pods et des nœuds du cluster.

---

### Capture 15 : Mesures comparatives directes depuis le Terminal UE (vm-ran)
**Où :** Depuis la VM principale, se connecter à `vm-ran`.
```bash
ssh ubuntu@172.31.34.222

# Commande à capturer :
bash ~/test-from-ue.sh
```
📸 **Ce que montre la capture :** Le point de vue du terminal / utilisateur 6G :
- **Latence vers EDGE** : **0.653 ms** (gain de réactivité maximal)
- **Latence vers FOG** : **0.874 ms**
- **Latence vers CLOUD** : **0.836 ms**


---

## ⚡ ATELIER 11 — Orchestration Intelligente des Ressources

### Capture 16 : Déploiement initial des microservices 6G et services NodePort (vm-cp)
**Où :** Se connecter à `vm-cp` via la VM principale.
```bash
# Dans votre PowerShell Windows :
ssh -i .\6g-team-key.pem ubuntu@13.48.10.213

# Depuis la VM principale :
ssh ubuntu@172.31.47.81

# Commande à capturer :
sudo k3s kubectl get pods,svc -n at11-orch -o wide
```
📸 **Ce que montre la capture :** Les 4 déploiements opérationnels (`workload-app` sur `vm-ran`, `app-edge` sur `vm-ran`, `app-fog` sur `vm-upf`, `app-cloud` sur `vm-cp`) et leurs NodePorts respectifs (30090 à 30093).

---

### Capture 17 : Exécution complète de la boucle d'orchestration intelligente (vm-cp)
**Où :** Sur `vm-cp`.
```bash
# Commande à capturer :
cat ~/at11-scenario.log | grep -A 45 "ORCHESTRATEUR INTELLIGENT DE RESSOURCES 6G"
```
📸 **Ce que montre la capture :** L'analyse en temps réel des métriques (`kubectl top nodes`), la détection de la surcharge sur `vm-ran` (78% CPU), la décision autonome d'élection de `vm-upf` (2% CPU), le Scale UP de `app-fog` et la migration à chaud de `workload-app`.

---

### Capture 18 : Tableau comparatif final et bilan des ressources (vm-cp)
**Où :** Sur `vm-cp`.
```bash
# Commande à capturer :
cat ~/at11-scenario.log | grep -A 35 "RAPPORT FINAL ET TABLEAU COMPARATIF"
```
📸 **Ce que montre la capture :** Le tableau comparatif officiel de l'orchestrateur montrant l'évolution du CPU par nœud (1% -> 78% -> 2%) et la redistribution automatique des pods entre T0, pic de charge et stabilisation.

---

### Capture 19 : Preuve de la migration dynamique et continuité de service (vm-cp)
**Où :** Sur `vm-cp`.
```bash
# Commande à capturer :
sudo k3s kubectl get pods -n at11-orch -o wide
curl -s http://172.31.38.166:30090/health
```
📸 **Ce que montre la capture :** Le pod `workload-app` tourne désormais sur `vm-upf` (Node: `vm-upf`) et répond en JSON confirmant son nouvel emplacement d'exécution sans interruption de service (RTT ~1.4 ms).


---

## 🤖 ATELIER 11 — Orchestration Intelligente des Ressources 6G

### Capture 16 : Déploiement initial des microservices 6G et services NodePort (vm-cp)
**Où :** Sur `vm-cp` (via VM principale).
```bash
ssh -i .\6g-team-key.pem ubuntu@13.48.10.213
ssh ubuntu@172.31.47.81

# Commande à capturer :
sudo k3s kubectl get pods,svc -n at11-orch -o wide
```
📸 **Ce que montre la capture :** Les 4 pods déployés sur leurs nœuds respectifs (Edge/Fog/Cloud) et les services NodePort 30090 à 30093.

---

### Capture 17 : Exécution complète de la boucle d'orchestration intelligente (vm-cp)
**Où :** Sur `vm-cp`.
```bash
# Commande à capturer :
cat ~/at11-scenario.log | grep -A 45 "ORCHESTRATEUR INTELLIGENT DE RESSOURCES 6G"
```
📸 **Ce que montre la capture :** Les 5 itérations de l'orchestrateur Python autonome avec :
- Détection du pic CPU à **78%** sur `vm-ran` (seuil 50% dépassé)
- Élection automatique de `vm-upf` comme nœud cible (CPU : 2%)
- Scale UP `app-fog` (1 → 2 répliques)
- Migration à chaud de `workload-app` vers `vm-upf`

---

### Capture 18 : Tableau comparatif final CPU et distribution des pods (vm-cp)
**Où :** Sur `vm-cp`.
```bash
# Commande à capturer :
cat ~/at11-scenario.log | grep -A 35 "RAPPORT FINAL ET TABLEAU COMPARATIF"
```
📸 **Ce que montre la capture :** Synthèse comparative CPU par nœud (T0 Repos → T_pic Surcharge → T_fin Stabilisé) et évolution de la distribution des pods.

---

### Capture 19 : Preuve de migration dynamique et continuité de service (vm-cp)
**Où :** Sur `vm-cp`.
```bash
# Commande à capturer :
sudo k3s kubectl get pods -n at11-orch -o wide
curl -s http://172.31.38.166:30090/health
```
📸 **Ce que montre la capture :**
- `workload-app` s'exécute désormais sur `vm-upf` (Fog), confirmant la migration réussie.
- Réponse JSON `{"status":"UP","node":"vm-upf"}` prouvant la continuité de service sans interruption.


---

### Capture 20 : État des pods AT12 Edge Intelligence (vm-cp)
**Où :** Sur `vm-cp`.
```bash
# Commande à capturer :
sudo k3s kubectl get pods,svc -n at12-edge-ia -o wide
```
📸 **Ce que montre la capture :** Les 2 pods déployés (ia-edge sur vm-ran, ia-cloud sur vm-cp) et les services NodePort (30120 et 30121).

---

### Capture 21 : Health check et prédiction IA depuis UE (vm-ran)
**Où :** Sur `vm-ran`.
```bash
# Commande à capturer :
curl -s http://127.0.0.1:30120/health
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"latence_ms":2.5,"debit_mbps":80,"pertes_pct":0.05}' \
  http://127.0.0.1:30120/predict
```
📸 **Ce que montre la capture :**
- Health `{"status":"UP","node":"vm-ran-edge"}` confirmant l'IA opérationnelle à l'Edge
- Prédiction de classe de service QoS avec temps d'inférence en ms

---

### Capture 22 : Benchmark comparatif Edge vs Cloud depuis UE (vm-ran)
**Où :** Sur `vm-ran`.
```bash
# Commande à capturer (exécuter at12-benchmark-ue.sh et afficher stats) :
bash /tmp/at12-benchmark-ue.sh 2>&1 | grep -E "(STATS|RTT|Inf|Gain|Edge|Cloud)"
```
📸 **Ce que montre la capture :**
- Edge RTT moyen : 5.85-6.15 ms (inference locale sur vm-ran)
- Cloud RTT moyen : 6.20-6.65 ms (inference distante sur vm-cp)
- **Gain latence Edge vs Cloud : 5.6% à 7.5%**
- Temps d'inférence kNN : ~0.63-0.68 ms (Edge) vs ~0.65-0.70 ms (Cloud)


---

### Capture 23 : Statistiques descriptives du Dataset 6G Telecom (6G-team)
**Où :** Sur `6G-team`.
```bash
# Commande à capturer :
cat /home/ubuntu/at14/captures/dataset_summary.txt
```
📸 **Ce que montre la capture :**
- Volume total : **597 échantillons** consolidés à partir des mesures AT5, AT6, AT12 et AT13.
- Répartition par tranche : **eMBB** (30.7%), **URLLC** (33.8%), **mMTC** (35.5%).
- Équilibre des classes de congestion : 67.8% nominal vs 32.2% congestionné.
- Statistiques descriptives des variables (débit, latence, gigue, perte, CPU).

---

### Capture 24 : Aperçu du Dataset 6G brut et normalisé (6G-team)
**Où :** Sur `6G-team`.
```bash
# Commande à capturer :
head -n 6 /home/ubuntu/at14/dataset_6g_telecom.csv
head -n 6 /home/ubuntu/at14/dataset_6g_normalized.csv
```
📸 **Ce que montre la capture :**
- Les 14 colonnes tabulaires (`sample_id`, `source`, `slice_type`, `throughput_mbps`, `latency_ms`, `loss_pct`, `jitter_ms`, `cpu_usage_pct`, `qos_limit_mbps`, `ric_action`, `is_congested`).
- La version normalisée Min-Max [0, 1] prête pour l'ingestion par les modèles de machine learning des ateliers AT24 (prédiction) et AT25 (détection d'anomalies).

---

### Capture 25 : Exécution de la boucle fermée AI-native et synthèse comparative Statique vs AI (6G-team)
**Où :** Sur `6G-team`.
```bash
# Commande à capturer :
cat /home/ubuntu/at26/captures/at26_results.txt
```
📸 **Ce que montre la capture :**
- Comparaison quantitative des 15 cycles : Baseline Statique (50 Mbps figé) vs Boucle Dynamique Fermée AI-Native (MAPE-K / OODA).
- Réduction spectaculaire de la latence moyenne de 25.868 ms à 1.646 ms (+93.64% d'amélioration) et du pic de 45.0 ms à 2.13 ms (+95.27%).
- Taux de congestion évitée/résolue de 100% (0/15 en mode AI vs 13/15 en statique) et élimination totale des pertes de paquets (0.0%).
- Temps de cycle de la boucle autonome : 5.527 ms moyen (< 100 ms cible Near-RT O-RAN, soit ~18× plus rapide que la contrainte critique).
- Actuation concrète au niveau du noyau Linux via Traffic Control (`tc` qdisc TBF) sur les tranches URLLC, eMBB et mMTC.

---

### Capture 28 : Résultats réels Mobilité et Handover 6G (Dual-gNB) (6G-team)
**Où :** Sur `6G-team`.
```bash
# Commande à capturer :
cat /home/ubuntu/6G/membre2_qos_mobilite/captures/at15_results.txt
```
📸 **Ce que montre la capture :**
- Architecture double point d'accès Dual-gNB (gNB1 `0x00001` source et gNB2 `0x00002` cible) connectés à l'AMF Open5GS (`172.31.47.81:38412`).
- Détail des 3 runs réels de basculement inter-cellulaire (Handover).
- Handover Interruption Time (HIT) moyen mesuré à **26.33 ms**, respectant le seuil critique 6G/URLLC (< 30 ms).
- Taux de perte transitoire moyen de 10.0% durant la commutation radio, avec rétablissement immédiat de session.
- Stabilité post-handover : RTT moyen de 13.00 ms et gigue réduite à 1.62 ms.

---

### Capture 29 : Mesures quantitatives de communication V2X 6G (V2I / V2V) (6G-team)
**Où :** Sur `6G-team`.
```bash
# Commande à capturer :
cat /home/ubuntu/6G/captures/at16_results.txt
```
📸 **Ce que montre la capture :**
- Résultats réels sur 3 runs des flux V2I (Urbain 50 km/h) et V2V (Autoroute 130 km/h).
- Taux de livraison de paquets (PDR) parfait en V2I urbain (**100.00%**) et ultra-élevé en V2V autoroutier (**99.00%**).
- Latence moyenne sub-milliseconde (**0.047 ms en V2I** et **0.067 ms en V2V**), démontrant la faisabilité d'échanges véhiculaires critiques sous couverture 6G Edge/RSU.
- Gigue maîtrisée (**0.05 ms** urbain / **0.07 ms** autoroutier).

---

### Capture 30 : Benchmark comparatif NTN Réseaux Non-Terrestres (Terrestre vs LEO vs GEO) (6G-team)
**Où :** Sur `6G-team`.
```bash
# Commande à capturer :
cat /home/ubuntu/at17/captures/at17_results.txt
```
📸 **Ce que montre la capture :**
- Résultats mesurés sur 3 runs réels pour chaque profil d'orbite :
  * **Terrestre (T-6G)** : RTT sub-milliseconde moyen de **0.05 ms** (fibre/local).
  * **LEO (Low Earth Orbit ~600 km)** : RTT moyen de **30.60 ms** (délai de vol aller-retour spatial réaliste, adapté aux flux interactifs et à la couverture 3D globale).
  * **GEO (Geostationary ~35 786 km)** : RTT moyen de **488.70 ms** (propagation longue distance, adapté à la diffusion broadcast/multicast et au backhaul).
- Taux de perte de paquets de 0.0% pour tous les profils sous dimensionnement adéquat.




