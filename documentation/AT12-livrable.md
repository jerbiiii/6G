# Livrable AT12 : Edge Intelligence (IA à l'Edge)

## 1. Objectifs de l'atelier
- Déployer un modèle d'intelligence artificielle (machine learning) à l'Edge (nœud `vm-ran`) et au Cloud (nœud `vm-cp`) sous Kubernetes k3s.
- Réaliser l'inférence locale en temps réel pour classifier les profils de qualité de service (QoS 6G : eMBB, URLLC, mMTC) selon les métriques réseau (latence, débit, pertes de paquets).
- Comparer quantitativement les performances d'inférence et le temps de réponse total (RTT) entre l'exécution Edge (au plus près de l'UE/RAN) et l'exécution Cloud distante.

## 2. Architecture de déploiement
- **Namespace Kubernetes :** `at12-edge-ia`
- **Modèle IA :** Classifieur k-Nearest Neighbors (k=7, 600 points d'entraînement synthétiques normalisés, 3 classes cibles : eMBB=0, URLLC=1, mMTC=2). Implémentation native Python sans dépendance externe pour empreinte minimale (conteneur `python:3.11-alpine`).
- **Nœud Edge :** `vm-ran` (IP privée 172.31.34.222), Pod `ia-edge`, Service NodePort `30120`.
- **Nœud Cloud :** `vm-cp` (IP privée 172.31.47.81), Pod `ia-cloud`, Service NodePort `30121`.
- **Point de mesure UE :** Requêtes générées depuis `vm-ran` simulant un équipement utilisateur accédant à l'Edge en local vs Cloud distant.

## 3. Procédure et commandes de validation
1. Déploiement du ConfigMap K8s contenant le serveur HTTP d'inférence Python (`/predict`, `/health`).
2. Déploiement des pods `ia-edge` et `ia-cloud` avec `nodeSelector` respectif (`kubernetes.io/hostname`).
3. Vérification de l'état des pods (`kubectl get pods -n at12-edge-ia -o wide`).
4. Exécution du benchmark automatisé (20 requêtes POST par palier avec charges variables).
5. Mesure du temps d'inférence algorithmique interne et du RTT global vu du client.

## 4. Résultats des mesures (2 séries de 20 requêtes depuis vm-ran)

| Métrique | Série 1 (Edge) | Série 1 (Cloud) | Série 2 (Edge) | Série 2 (Cloud) |
|---|---|---|---|---|
| **RTT total moyen** | **6.15 ms** | 6.65 ms | **5.85 ms** | 6.20 ms |
| **RTT min / max** | 6.00 / 8.00 ms | 6.00 / 7.00 ms | 5.00 / 6.00 ms | 6.00 / 7.00 ms |
| **Temps inférence moyen** | 0.66 ms | 0.68 ms | 0.62 ms | 0.70 ms |
| **Gain latence Edge vs Cloud** | **+7.5 %** | référence | **+5.6 %** | référence |

## 5. Analyse et enseignements
- **Réduction de latence :** L'inférence à l'Edge apporte un gain systématique de 5.6 % à 7.5 % sur le temps de cycle requête/décision par rapport au Cloud, même au sein d'un même VPC AWS à latence inter-VM faible (~1 ms). En conditions réelles (avec backhaul WAN / satellite / fibre), ce gain serait démultiplié.
- **Rapidité d'inférence :** L'inférence kNN native s'exécute en moins de 0.7 ms par décision sur 1 vCPU, ce qui est parfaitement compatible avec les contraintes d'ordonnancement quasi temps réel (Near-RT RIC / O-RAN).
- **Précision de classification :** Les requêtes à faible latence et faible perte sont classifiées à 100% en URLLC ; les requêtes à fort débit en eMBB.

## 6. Limites constatées et incidents résolus
- **Incident environnement :** Le conteneur Alpine de base n'embarquait pas `scikit-learn` / `gfortran`. Solution : implémentation native vectorisée kNN en Python pur dans le ConfigMap K8s, garantissant un démarrage instantané (< 5 s) et une consommation mémoire ultra-faible (< 25 Mo).
- **Emplacement des mesures :** Les mesures exécutées depuis la VM de management (`6G-team`) donnaient un RTT identique (~7 ms) car équidistante des deux nœuds. Les mesures ont été reconduites directement depuis `vm-ran` pour refléter la topologie réelle UE → Edge.
