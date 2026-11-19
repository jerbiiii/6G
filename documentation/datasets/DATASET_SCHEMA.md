# Schéma et Dictionnaire des Données — Dataset 6G Telecom

Ce dataset a été construit dans le cadre de l'**Atelier 14 (Préparation des datasets 6G)**.
Il agrège les mesures télémétriques réelles des fonctions réseau 5G/6G (Open5GS, UERANSIM, k3s, Near-RT RIC O-RAN).

## 1. Dictionnaire des variables

| Colonne | Type | Unité | Description | Exemple |
|---|---|---|---|---|
| `sample_id` | Entier | - | Identifiant unique de l'échantillon | 1, 2, ... |
| `source` | Chaîne | - | Atelier / module réseau source (AT5, AT6, AT12, AT13) | `AT6-dynamique_charge` |
| `time_s` | Float | secondes | Timestamp relatif de la mesure | 12.4 |
| `slice_type` | Catégoriel | - | Tranche réseau 6G (eMBB, URLLC, mMTC) | `URLLC` |
| `slice_id` | Entier | - | Encodage numérique de la tranche (0: eMBB, 1: URLLC, 2: mMTC) | 1 |
| `throughput_mbps` | Float | Mbit/s | Débit utile mesuré sur l'interface PDU / GTP-U | 85.50 |
| `latency_ms` | Float | millisecondes | Latence aller-retour RTT (ping / requête SBI / E2) | 1.45 |
| `loss_pct` | Float | % | Taux de perte de paquets UDP mesuré | 0.012 |
| `jitter_ms` | Float | millisecondes | Gigue ou temps de traitement d'inférence/contrôle | 0.150 |
| `cpu_usage_pct` | Float | % | Utilisation processeur de l'infrastructure d'accueil | 78.5 |
| `qos_limit_mbps` | Float | Mbit/s | Plafond de QoS alloué par le contrôleur tc / RIC | 100.0 |
| `ric_action` | Catégoriel | - | Décision O-RAN / RIC prise (`HOLD`, `THROTTLE`, `BOOST`) | `THROTTLE` |
| `ric_action_id` | Entier | - | Encodage numérique de l'action (0: HOLD, 1: THROTTLE, 2: BOOST) | 1 |
| `is_congested` | Binaire | {0, 1} | Cible de classification d'anomalie / congestion | 1 |

## 2. Utilisation pour les ateliers suivants
- **AT24 (IA Prédictive)** : Prédire `throughput_mbps` ou `latency_ms` à t+1 en fonction de l'état actuel.
- **AT25 (Détection d'anomalies)** : Modèle non-supervisé (Isolation Forest) sur `is_congested`.
- **AT26 (Boucle AI-native)** : Prédire `ric_action_id` pour ajuster automatiquement le slicing réseau.
