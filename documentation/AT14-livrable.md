# Livrable AT14 : Préparation des datasets 6G

## 1. Objectifs de l'atelier
- Construire un dataset unifié et représentatif des communications 6G (multi-slices, multi-tiers, boucle O-RAN).
- Collecter, filtrer, nettoyer et formater les métriques produites lors des ateliers de simulation et de mesure réelles (AT5, AT6, AT12, AT13).
- Produire un schéma de données normalisé prêt pour les ateliers d'apprentissage automatique (AT24 IA prédictive, AT25 détection d'anomalies, AT26 boucle AI-native).

## 2. Origine et fusion des sources de données

| Atelier Source | Nature des données | Nombre d'échantillons | Variables extraites |
|---|---|---|---|
| **AT5 (QoS dynamique)** | Mesures de latence et throttling `tc` sous charge vidéo | 16 | Latence, seuil QoS, pertes, débit eMBB |
| **AT6 (Slicing dynamique)** | 3 tranches indépendantes (eMBB, URLLC, mMTC) sous 3 scénarios | 441 (3 runs x 147) | Débit, RTT, pertes UDP, charge CPU, allocation de bande passante |
| **AT12 (Edge Intelligence)** | Benchmark inférence IA locale (Edge) vs distante (Cloud) | 40 | RTT aller-retour UE, temps de calcul d'inférence (gigue) |
| **AT13 (O-RAN / RIC)** | Boucle de contrôle Near-RT RIC et métriques E2 Node | 100 | Décisions THROTTLE/HOLD/BOOST, latence E2, régulation |
| **TOTAL** | **Dataset 6G Telecom complet** | **597 échantillons** | **14 colonnes tabulaires** |

## 3. Structure et caractéristiques du dataset (`dataset_6g_telecom.csv`)

- **Répartition équilibrée par tranche de service :**
  - **eMBB (Haut débit) :** 183 échantillons (30.7%)
  - **URLLC (Ultra-fiabilité & faible latence) :** 202 échantillons (33.8%)
  - **mMTC (IoT massif) :** 212 échantillons (35.5%)

- **Classes d'état et d'anomalie :**
  - **Nominal (`is_congested = 0`) :** 405 échantillons (67.8%)
  - **Congestionné / Anomalie (`is_congested = 1`) :** 192 échantillons (32.2%)

- **Statistiques descriptives clés :**
  - **Débit utile :** de 0.10 Mbit/s (IoT) à 207.00 Mbit/s (eMBB max), moyenne = 36.59 Mbit/s.
  - **Latence :** de 0.21 ms à 7.00 ms, moyenne = 2.17 ms (écart-type = 1.32 ms).
  - **Charge CPU :** de 32.10% à 98.50%, moyenne = 77.04%.

## 4. Fichiers produits et disponibles
1. `documentation/datasets/dataset_6g_telecom.csv` : Dataset en unités réelles (ms, Mbit/s, %).
2. `documentation/datasets/dataset_6g_normalized.csv` : Dataset normalisé Min-Max (0 à 1) prêt pour l'entraînement d'algorithmes ML/DL.
3. `documentation/datasets/DATASET_SCHEMA.md` : Dictionnaire complet des attributs.
4. `captures/at14/dataset_summary.txt` : Synthèse statistique descriptive.

## 5. Exploitation future dans le projet
Ce jeu de données constitue la base d'apprentissage pour :
- **AT24** : Prédiction de séries temporelles de trafic (régression).
- **AT25** : Détection non supervisée de congestion réseau (Isolation Forest / Autoencoders).
- **AT26** : Automatisation de la boucle fermée d'orchestration AI-native.
