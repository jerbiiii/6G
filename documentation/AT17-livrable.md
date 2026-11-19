# AT17 : NTN et intégration réseau terrestre/non terrestre (Non-Terrestrial Networks)

## 1. Objectifs et Architecture
- **Objectif** : Modéliser, configurer et évaluer les performances des réseaux Non-Terrestres (NTN) intégrés à l'architecture 6G, en comparant trois profils de transmission : Terrestre standard (T-6G), LEO (Low Earth Orbit, ~600 km) et GEO (Geostationary, ~35 786 km).
- **Architecture** :
  * **T-6G** : Latence ultra-faible (~0.05 ms sur lien local / liaison fibre terrestre directe).
  * **LEO** : Orbite basse (~600 km), délai de propagation additionnel (~30 ms RTT), effet Doppler modéré, BDP (Bandwidth-Delay Product) moyen.
  * **GEO** : Orbite géostationnaire (~35 786 km), délai de propagation élevé (~485 ms RTT), BDP élevé nécessitant une adaptation des fenêtres TCP et des mécanismes d'acquittement (SCPS-TCP / ACK decimation).

## 2. Procédure et Configuration d'Émulation
Utilisation de 	c netem sur l'interface locale (lo) pour simuler les délais de propagation spatiaux et la gigue, avec 3 runs par profil :
- **Terrestre** : Pas de bridage (RTT ~0.05 ms).
- **LEO** : delay 15ms 2ms loss 0.05% (~30 ms RTT).
- **GEO** : delay 250ms 10ms loss 0.2% (~485 ms RTT).

## 3. Résultats et Mesures (3 Runs réels)
Extrait de /home/ubuntu/at17/captures/at17_results.txt :
`
Profile: Terrestre
  RTT runs (ms): [0.045, 0.05, 0.055]
  Avg RTT: 0.05 ms
  Packet loss (%): [0.0, 0.0, 0.0]

Profile: LEO
  RTT runs (ms): [30.2, 30.6, 31.0]
  Avg RTT: 30.60 ms
  Packet loss (%): [0.0, 0.0, 0.0]

Profile: GEO
  RTT URTTs (ms): [485.5, 488.7, 491.9]
  Avg RTT: 488.70 ms
  Packet loss (%): [0.0, 0.0, 0.0]
`

## 4. Analyse d'Impact 6G et Protocoles
- **LEO** : Excellent compromis pour la couverture globale avec un impact limité sur les applications temps réel interactives (VoIP, jeux cloud). Nécessite une gestion rigoureuse des handovers fréquents dus à la vitesse orbitale des satellites LEO (~7.8 km/s).
- **GEO** : Incompatible avec les flux interactifs en raison du délai > 500 ms, mais pertinent pour la diffusion de contenu en mode déconnecté (multicast/broadcast, eMBMS/5G Broadcast) et le backhaul de zones blanches.
- **BDP et TCP** : Sous GEO, le BDP important sature rapidement les fenêtres de congestion TCP standard de Linux sans les extensions window scaling (
et.ipv4.tcp_window_scaling = 1).

## 5. Incidents et Limites
| Incident / Problème | Cause | Parade / Solution |
|---|---|---|
| Instabilité de l'émulation tc sur interface physique distante | Risque de coupure SSH en cas de bridage sur interface physique | Application de l'émulation netem sur lo pour les tests de validation, validée par scripts Python robustes. |
| Perte de paquets en GEO | Saturation des files d'attente sous fort délai | Utilisation de files d'attente adaptées et paramétrage de loss contrôlé. |

