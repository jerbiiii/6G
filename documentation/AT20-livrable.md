# Atelier 20 (AT20) : Digital Twin intelligent du réseau 6G

## 1. Objectifs pédagogiques
- Concevoir et déployer un Jumeau Numérique (Digital Twin) répliquant en temps réel l'infrastructure physique du réseau 6G multi-domaines (Control Plane Open5GS, User Plane UPF, RAN distribué multi-gNB, tranches réseau et UEs).
- Mettre en œuvre une API REST de supervision et d'expérimentation en circuit fermé (*closed-loop experimentation*).
- Simuler des scénarios prédictifs complexes (*What-If*) sans impacter le réseau physique en production : surcharge de trafic par tranche, panne inopinée d'une cellule radio, mobilité massive.
- Comparer quantitativement la fidélité des prédictions du Digital Twin aux mesures physiques réelles (erreur relative < 4.5%).

## 2. Architecture du Digital Twin 6G
Le Digital Twin repose sur une architecture en trois couches :
1. **Couche d'ingestion et de synchronisation** : Réplication continue des états des nœuds physiques (`vm-cp`, `vm-ran`, `vm-upf`), de la charge CPU, des UEs enregistrés et des sessions PDU actives.
2. **Couche de modélisation numérique (Digital State Engine)** : Maintien en mémoire de la topologie cellulaire (cellules gNB-A, B, C, D) et des tranches réseau (eMBB 100 Mbps, URLLC 50 Mbps, mMTC 20 Mbps).
3. **Couche d'expérimentation What-If & API REST (port 8090)** :
   - `GET /api/v1/twin/state` : État global synchronisé du jumeau.
   - `POST /api/v1/twin/simulate` : Injection de scénarios et prédiction d'impact.
   - `GET /api/v1/twin/compare` : Benchmark de fidélité numérique vs réseau physique.

## 3. Scénarios What-If simulés
1. **Scénario 1 — Surcharge de trafic eMBB (+250 Mbps sur tranche allouée à 100 Mbps)** :
   - *Prédiction du Jumeau* : Saturation du buffer à 100%, explosion de la latence de 4.12 ms à 21.44 ms, perte de paquets de 12.75%, violation critique du SLA.
   - *Action prescriptive générée* : Déclenchement d'un Scale-UP dynamique de bande passante (+150 Mbps) ou migration Fog vers `vm-upf`.
2. **Scénario 2 — Panne inopinée de la cellule radio gNB-B (18 UEs connectés)** :
   - *Prédiction du Jumeau* : Répartition automatique de 9 UEs vers gNB-A et 9 UEs vers gNB-C, délai de basculement estimé à 26.33 ms (conforme AT15), capacité résiduelle suffisante sans interruption.

## 4. Évaluation quantitative de fidélité (Digital Twin vs Réseau Physique)

| Tranche / Métrique | Mesure Réseau Physique | Prédiction Digital Twin | Écart relatif (%) | Statut de fidélité |
|---|---|---|---|---|
| **eMBB Latence (ms)** | 4.25 ms | 4.12 ms | **3.06 %** | Haute fidélité |
| **URLLC Latence (ms)** | 0.653 ms | 0.650 ms | **0.46 %** | Fidélité quasi-parfaite |
| **mMTC Latence (ms)** | 12.80 ms | 12.40 ms | **3.13 %** | Haute fidélité |
| **Moyenne globale (MAPE)** | — | — | **2.21 %** | **Excellence (< 4.5%)** |

*Preuve brute enregistrée sur la VM : `/home/ubuntu/at20/captures/at20_results.txt`*

## 5. Commandes d'accès et de test en direct
Le Digital Twin est actif en arrière-plan sur la VM principale (`16.171.171.2:8090`).
```bash
# 1. Consulter l'état en direct du Digital Twin
curl -s http://127.0.0.1:8090/api/v1/twin/state

# 2. Lancer une simulation prédictive What-If (surcharge de trafic)
curl -s -X POST http://127.0.0.1:8090/api/v1/twin/simulate \
     -H "Content-Type: application/json" \
     -d '{"scenario":"traffic_surge","slice":"embb","load_mbps":250}'

# 3. Lancer une simulation prédictive What-If (panne de cellule)
curl -s -X POST http://127.0.0.1:8090/api/v1/twin/simulate \
     -H "Content-Type: application/json" \
     -d '{"scenario":"cell_failure","cell":"gnb-B"}'

# 4. Vérifier la fidélité Jumeau vs Réseau Physique
curl -s http://127.0.0.1:8090/api/v1/twin/compare
```

## 6. Limites & Incidents
- **Limites** : Modélisation des files d'attente basée sur des lois de puissance calibrées sur les données réelles (AT5, AT6, AT26) ; précision dépendante de la fréquence de rafraîchissement des télémétries.
- **Incidents** : Aucun incident ; le serveur Python stdlib assure une latence de réponse < 2 ms sur toutes les requêtes REST.
