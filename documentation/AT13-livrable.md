# Livrable AT13 : O-RAN, RIC et réseau programmable 6G

## 1. Objectifs de l'atelier
- Étudier l'architecture O-RAN (RU, DU, CU, O-DU, O-CU) et ses interfaces standardisées (E2, A1, O1).
- Simuler un contrôleur Near-RT RIC et une xApp de contrôle radio dans un environnement Kubernetes.
- Mesurer les temps de boucle de contrôle et vérifier la conformité aux cibles O-RAN 3GPP.

## 2. Architecture O-RAN simulée (K8s namespace at13-oran-ric)

| Composant | Pod K8s | Nœud | Port | Rôle |
|---|---|---|---|---|
| E2 Node simulé | e2-node | vm-ran | 8080 | Expose les métriques radio (lat, throughput, loss) via /metrics JSON |
| Near-RT RIC | near-rt-ric | vm-cp | 8081 | Lit les métriques E2, décide THROTTLE/BOOST/HOLD, expose /status et /command |
| xApp RAN Optimizer | xapp-ran (Job) | vm-upf | — | Boucle 3× : read E2 → décision RIC → commande QoS → vérification |

## 3. Résultats des 3 boucles de contrôle xApp

| Boucle | Latence UE (ms) | Perte (%) | Décision RIC | QoS appliqué | Temps total | Conformité |
|---|---|---|---|---|---|---|
| 1 | 3.987 | 0.197 | THROTTLE | 20 Mbps | 109.5 ms | ✅ < 1s |
| 2 | 1.696 | 0.016 | THROTTLE | 20 Mbps | 7.9 ms | ✅ < 1s |
| 3 | 1.696 | 0.016 | HOLD | 20 Mbps | 6.7 ms | ✅ < 1s |

**Statistiques :** moy=41.3 ms, min=6.7 ms, max=109.5 ms

## 4. Near-RT RIC : 171 boucles E2 internes
- Intervalle de boucle : 500 ms
- Temps de boucle mesuré : **1.792 ms** (très en deçà du plafond 1000 ms Near-RT)
- Toutes les cibles O-RAN 3GPP respectées.

## 5. Conformité aux cibles O-RAN
| Cible | Valeur mesurée | Statut |
|---|---|---|
| Near-RT RIC loop < 1s | 1.792 ms | ✅ ATTEINTE |
| xApp boucle complète < 1s | 6.7 ms à 109.5 ms (moy 41.3 ms) | ✅ ATTEINTE |
| 3 boucles xApp validées | 3/3 | ✅ |

## 6. Limites et incidents
- Interface E2 et A1 simulées via HTTP REST (pas de stack O-RAN open-source complète déployée).
- Métriques radio aléatoires (pas de vrai gNB UERANSIM connecté au RIC, pas de protocole E2AP SCTP).
- Stack O-RAN complète (OpenRAN, FlexRIC, SD-RAN) nécessite du matériel/hyperviseur non disponible sur AWS.
