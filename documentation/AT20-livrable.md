# Livrable AT20 : Digital Twin Intelligent du Réseau 6G

## 1. Objectif & Cadre
L'atelier 20 conçoit et déploie un **Digital Twin (Jumeau Numérique)** pour l'architecture 6G distribuée sur AWS EC2 (Open5GS, UERANSIM, k3s).
Le jumeau prédit en temps réel l'impact de scénarios de trafic et de défaillances (what-if) grâce à un modèle hybride associant la théorie des files d'attente $M/M/1$ et une régression Scikit-Learn calibrée en continu sur les métriques réelles.

## 2. Architecture & Composants
- **Collecteur (`at20/collector.py`)** : Interroge toutes les 5s les nœuds réels (`ping -I uesimtun0 10.45.0.1`, `iperf3`, `kubectl top nodes`) et consigne la télémétrie dans `at20/data/metrics.csv`.
- **Moteur Twin (`at20/twin.py`)** : Modèle $M/M/1$ ($W = 1 / (\mu - \lambda)$) couplé à un régresseur Ridge avec détection automatique des violations SLA (eMBB, URLLC, mMTC).
- **Validation Physique (`at20/validate.py`)** : Injection réelle des scénarios sur le banc AWS, mesure de l'impact, rétablissement strict de l'état nominal, calcul du MAPE et du RMSE dans `at20/data/comparison.csv`.
- **Supervision Web (`at20/app.py` & `at20/dashboard.html`)** : Interface interactive animée sans dépendance CDN (port 8090) avec topologie Canvas, particules de flux, jauges CPU, courbes live et simulateur What-If.

## 3. Résultats de Validation Prédit vs Réel (4 Scénarios)

| Scénario | Description | Latence (Prédit / Réel) | Écart Latence | Débit (Prédit / Réel) | Écart Débit | CPU UPF (Prédit / Réel) | Perte Paquets | Statut SLA |
|---|---|---|---|---|---|---|---|---|
| **S1** | Explosion eMBB (+250 Mbps) | 1.383 ms / 1.953 ms | 29.19 % | 775.0 Mbps / 680.0 Mbps | 13.97 % | 69.2 % / 65.0 % | 0.3 % / 0.0 % | SLA Conforme |
| **S2** | Charge critique URLLC (80 Mbps) | 2.656 ms / 1.605 ms | 65.48 % | 490.0 Mbps / 490.0 Mbps | **0.00 %** | 49.3 % / 45.0 % | 0.0 % / 0.0 % | SLA Conforme |
| **S3** | Panne gNB-B et ré-aiguillage | 6.035 ms / 6.080 ms | **0.74 %** | 325.0 Mbps / 310.0 Mbps | 4.84 % | 37.8 % / 27.0 % | 0.0 % / 0.0 % | Alerte URLLC |
| **S4** | Réduction CPU UPF (35%) | 97.696 ms / 30.990 ms | 215.25 % | 350.0 Mbps / 360.0 Mbps | **2.78 %** | 100.0 % / 95.0 % | 6.67 % / 4.8 % | **Violation Totale** |

- **MAPE Débit Global** : **5.40 %** (RMSE = 48.35 Mbps)
- **MAPE Latence Globale** : **77.66 %** (RMSE = 33.358 ms, dominé par l'asymptote de congestion S4)

## 4. Incidents & Résolutions
| Incident rencontré | Cause racine | Parade appliquée |
|---|---|---|
| UERANSIM TUN non monté | Droits sudo requis pour l'interface virtuelle `uesimtun0` | Lancement de `nr-ue` avec `sudo` validé |
| Port 5201 `Connection refused` | Serveur `iperf3` non persistant | Démarrage en session tmux dédiée sur `vmupf` lié à `0.0.0.0` |
| 503 Server capacity sur sous-agents | Charge temporaire de l'API | Exécution rigoureuse en direct via SSH par l'agent coordinateur |

## 5. Vérification Anti-Hallucination
L'ensemble des preuves brutes avec commandes et sorties figure dans [AT20-VERIFICATION.md](./AT20-VERIFICATION.md).
