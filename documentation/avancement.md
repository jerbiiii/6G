# Projet fédérateur 3 : réseau 6G simulé — Suivi d'avancement

**Période :** 16 → 27 novembre 2026 (point d'étape le 20/11, validation le 27/11)
**Dernière mise à jour :** 16/11/2026 (AT1 et AT2 rédigés ; Git : synchronisation du dépôt en cours, étape 42)

Statuts : À commencer · En cours · Bloqué · Terminé · Validé

---

## 1. Environnement

| Élément | Valeur |
|---|---|
| Hébergement | AWS EC2 (free trial) |
| OS | Ubuntu 24.04.5 LTS (noble) |
| Ressources | 2 vCPU, 8 Go RAM (+ 4 Go swap), 80 Go disque |
| Accès | SSH (port 22), WebUI Open5GS par tunnel SSH |
| Docker | 29.9.3 |

## 2. Journal des étapes

| # | Date | Étape | Statut | Preuve / remarque |
|---|---|---|---|---|
| 1 | 16/11 | Création de la VM AWS Ubuntu 24.04 (2 vCPU, 8 Go, 80 Go) | Terminé | `lsb_release -a` OK |
| 2 | 16/11 | Mise à jour système + outils de base (git, iperf3, tcpdump, tshark, tmux, python3-venv…) | Terminé | |
| 3 | 16/11 | Swap 4 Go | Terminé | `free -h` : Swap 4.0Gi |
| 4 | 16/11 | Installation de Docker | Terminé | `docker --version` : 29.9.3 |
| 5 | 16/11 | Installation de MongoDB 8.0 | Terminé | |
| 6 | 16/11 | Installation d'Open5GS (PPA) | Terminé | services actifs |
| 7 | 16/11 | Installation de la WebUI Open5GS (Node.js 20) | Terminé | port 9999 en local |
| 8 | 16/11 | Installation d'UERANSIM (compilation) | Terminé | `nr-gnb`, `nr-ue`, `nr-cli` |
| 9 | 16/11 | Ajout de l'abonné (WebUI) + lancement gNB/UE | Terminé | |
| 10 | 16/11 | Enregistrement UE + session PDU (`uesimtun0`) | Terminé | |
| 11 | 16/11 | Test `ping -I uesimtun0 8.8.8.8` | Terminé | échec initial (NAT + conflit d'adresses), résolu aux étapes 12 à 15 |
| 12 | 16/11 | Correction du NAT (bonne interface `enp39s0`) | Terminé | règle MASQUERADE + FORWARD en place |
| 13 | 16/11 | Diagnostic du ping qui échoue (chemin GTP-U) | Terminé | `tcpdump` : les paquets arrivent sur `ogstun` mais aucune réponse ; cause = UE et cœur dans le même espace réseau |
| 14 | 16/11 | Déplacer l'UE dans un network namespace (`ue1`) + relancer gNB/UE | Terminé | veth OK (ping 10.100.0.1) ; UE enregistré dans `ue1`, `uesimtun0` = 10.45.0.5 |
| 15 | 16/11 | Nettoyer l'ancien `nr-ue`, relancer l'UE dans `ue1`, tester les pings | Terminé | ping 10.45.0.1 et 8.8.8.8 via `uesimtun0` : OK |
| 16 | 16/11 | AT3 : traceroute et iperf3 (TCP + UDP) | Terminé | résultats dans la section « Résultats AT3 » |
| 17 | 16/11 | AT3 : règles sauvegardées, captures `tcpdump` (`at3_registration.pcap`, `at3_data.pcap`) et logs Open5GS | Terminé | confirmé |
| 18 | 16/11 | AT4 : script `setup-netns.sh` (pont `br-ue` + 3 namespaces), 3 abonnés, 3 UEs (vidéo, IoT, navigation) | Terminé | ue1 = 10.45.0.9, ue2 = 10.45.0.10, ue3 = 10.45.0.11 ; pings vers 10.45.0.1 OK (RTT environ 0,45 ms) |
| 19 | 16/11 | AT4 : profils de trafic (script `at4-run.sh`) : scénario baseline puis simultané, mesures CPU/débit, repérage de la congestion | Terminé | baseline et simultané faits (voir « Résultats AT4 ») |
| 20 | 16/11 | AT5 : indicateurs QoS définis ; règle statique `tc` (limite de la vidéo à 100 Mbit/s) puis mesure « après » | Terminé | voir « Résultats AT5 » |
| 21 | 16/11 | AT5 : boucle d'adaptation dynamique (`controleur_qos.py`) et comparaison avant / statique / dynamique | Terminé | voir « Résultats AT5 : comparaison finale » ; CSV `~/6g-lab/at5_dynamique/controle.csv` |
| 22 | 16/11 | Dépôt Git commun `git@github.com:jerbiiii/6G.git` : clé SSH sur la VM, clone, arborescence, premier push (AT3 à AT5) | Terminé | confirmé |
| 23 | 16/11 | AT6 : plan des 3 slices, sauvegarde des configs Open5GS (`/etc/open5gs/backup-at3`), lecture des configs actuelles | Terminé | configs en 2.8.0 : `session` avec `subnet` + `gateway` |
| 24 | 16/11 | AT6 : vérification de l'état réel des configs avant modification (`amf`, `smf`, `upf`, `nssf`, gNB, ue3, interfaces) | Terminé | voir « État des configs AT6 (avant modification) » : tout est encore à l'état initial (SST 1 seul, `ogstun` seule) |
| 25 | 16/11 | AT6 : modification de `amf.yaml`, `smf.yaml`, `upf.yaml`, `nssf.yaml`, création de `ogstun2` / `ogstun3` (`setup-slices-tun.sh`), redémarrage d'Open5GS | Terminé | redémarrage OK : amfd, smfd, upfd, nssfd = `active` ; UPF écoute 127.0.0.7:2152 (GTP-U) et 8805 (PFCP). Sorties des vérifications des yaml / `ogstun2` / `ogstun3` / configs gNB et UEs non encore relevées |
| 26 | 16/11 | AT6 : abonnés dans MongoDB (3 slices) | Terminé | mise à jour par `mongosh` : 999700000000001 → SST 1 / `internet` (ue1), 999700000000002 → SST 3 / `mmtc` (ue2), 999700000000003 → SST 2 / `urllc` (ue3) ; vérifié par `db.subscribers.find` |
| 27 | 16/11 | AT6 : contrôle des yaml du cœur, des interfaces `ogstun2/3` et des configs gNB / UEs | Terminé | tout conforme (voir « Vérification des configs après modification ») ; reste `sd: 1` dans le default-nssai de ue1 |
| 28 | 16/11 | AT6 : correction de `sd: 1` dans `ue1.yaml` + relevé des commandes de lancement (gNB `linkIp` 10.100.0.1, `ngapIp`/`gtpIp` 127.0.0.1, AMF 127.0.0.5:38412 ; UEs avec `gnbSearchList` 10.100.0.1) | Terminé | gNB : `./build/nr-gnb -c config/open5gs-gnb.yaml` (dans `~/UERANSIM`) ; UEs : `sudo ip netns exec ue$i nohup ./build/nr-ue -c config/ue$i.yaml > ~/6g-lab/ue$i.log` |
| 29 | 16/11 | AT6 : relance gNB + 3 UEs par slice dans des sessions `tmux` (`gnb`, `ue1`, `ue2`, `ue3`), vérification des 3 sessions PDU (10.45 / 10.46 / 10.47) | Terminé | 3 enregistrements + 3 sessions PDU réussis ; ue1 = 10.45.0.2, ue3 = 10.46.0.2, ue2 = 10.47.0.2 ; pings vers la passerelle de chaque slice : 0 % de perte, RTT moyen environ 0,44 ms (voir « Résultats AT6 : mise en place des slices ») |
| 30 | 16/11 | AT6 : script `at6-run.sh` (un flux par slice vers sa passerelle, serveurs iperf3 dans `tmux` `srv1` à `srv3`), mesure « avant adaptation » avec charge nominale (2 flux vidéo) puis surcharge eMBB (6 flux vidéo) | Terminé | résultats dans `~/6g-lab/at6/avant_nominal` et `avant_surcharge` ; voir « Résultats AT6 : avant adaptation » |
| 31 | 16/11 | AT6 : politique d'adaptation par slice (`tc`), mesures après adaptation, comparaison avant / après | En cours | découpée en étapes 32 et suivantes |
| 32 | 16/11 | AT6 : politique statique par slice : script `at6-policy.sh` (`clear` / `static` / `show`), application et relevé de l'état `tc` | Terminé | état vérifié : ue1 = tbf 100 Mbit/s, ue2 = tbf 5 Mbit/s, ue3 = fq_codel sans limite (`at6/politique_avant_application.txt`, `at6/politique_statique_tc.txt`). Application seulement : mesures non faites |
| 33 | 16/11 | AT6 : mesures avec politique statique (nominal puis surcharge eMBB) | Terminé | `at6/statique_nominal` et `at6/statique_surcharge` ; résultats dans « Résultats AT6 : politique statique » : pertes et retransmissions à zéro, latence URLLC plus basse (une seule exécution par scénario, à confirmer) |
| 34 | 16/11 | AT6 : contrôleur dynamique par slice (`controleur_slices.py` : limite eMBB pilotée par la latence et les pertes de l'URLLC), test fonctionnel puis mesures sous charge variable | Terminé | script écrit, test fonctionnel sans charge fait (la branche « hausse » fonctionne : 100 → 160 Mbit/s, CSV et `tc` conformes) ; branche « baisse » validée à l'étape 35 (10 baisses) ; mesures sous charge variable : voir étape 35. Sortie de la dernière exécution (20 s, 11 fenêtres) relue à 16:26 : conforme au CSV ; vérifier `at6/dynamique_test.log` (commande saisie de façon mélangée) |
| 35 | 16/11 | AT6 : mesures du contrôleur dynamique sous charge variable (nominal → surcharge → nominal) | Terminé | script `~/6g-lab/at6-charge.sh <dossier>` exécuté (voir « Protocole de l'étape 35 »), départ à 300 Mbit/s, 3 phases de 30 s, résultats dans `at6/dynamique_charge/` ; 49 fenêtres : 10 baisses, 6 hausses, 33 sans changement ; limite finale 127 Mbit/s (107 Mbit/s sous charge : la dernière hausse, à t = 97,2 s, est très probablement après la fin du trafic ; voir « Relecture de l'étape 35 »). Voir « Résultats AT6 : contrôleur dynamique sous charge variable » (une seule exécution) |
| 36 | 16/11 | AT6 : répéter le contrôleur dynamique avec un départ à 100 Mbit/s (2 exécutions : `dynamique_charge_r2`, `dynamique_charge_r3`) pour isoler l'effet de la surcharge et mesurer la variabilité | Terminé | `at6-charge.sh` paramétrable (`START=${START:-300}`), résumés par `at6-resume.sh` ; voir « Résultats AT6 : répétitions du contrôleur » : limite eMBB tombée au plancher (20 Mbit/s) dès la phase 1 dans les deux exécutions, URLLC et IoT sans perte, latence URLLC de 1,4 à 1,8 ms ; l'effet de la surcharge n'est toujours pas isolé |
| 37 | 16/11 | Redémarrage de la VM : cœur (`ogstun2/3`), namespaces, gNB, UEs et serveurs iperf3 ne repartent pas seuls ; script `~/6g-lab/start-lab.sh` pour tout relancer | Terminé | `start-lab.sh` exécuté : mongod + 4 services Open5GS `active`, `ogstun` / `ogstun2` / `ogstun3` UP, NG Setup réussi, ue1 = 10.45.0.2, ue2 = 10.47.0.2, ue3 = 10.46.0.2, 3 pings vers les passerelles à 0 % de perte (RTT moyen 0,43 ms). Deux anomalies : `pkill: killing pid 591 failed: Operation not permitted` (`pkill iperf3`) et session `srv1` absente de `tmux ls` (voir « Problèmes rencontrés ») |
| 38 | 16/11 | Désactiver le service systemd `iperf3` (PID 591, port 5201 sur `*`) puis lancer `srv1` (`iperf3 -s -B 10.45.0.1 -p 5201`) dans `tmux` | Terminé | `ss` : trois serveurs liés à 10.45.0.1:5201, 10.47.0.1:5202 et 10.46.0.1:5203 ; `tmux ls` : `srv1` à `srv3` présents ; test vidéo de 5 s depuis ue1 : 20,3 Mbit/s, 0 retransmission (limite `tbf` de 20 Mbit/s laissée par r3, pas une anomalie) |
| 39 | 16/11 | AT6 : dernière tentative du contrôleur avec seuils recalibrés (`LAT_HIGH=3.0`, `LAT_LOW=1.6`, départ 100 Mbit/s), 2 exécutions : `dynamique_v2_r1`, `dynamique_v2_r2` | Terminé | critère de succès non atteint dans les deux exécutions (voir « Résultats AT6 : dernière tentative »). Conclusion prévue au protocole : le compromis eMBB / URLLC n'est pas résolu par un réglage des seuils sur la latence ; AT6 clôturé avec cette limite |
| 40 | 16/11 | AT1 : composants réutilisables, nouvelles fonctionnalités, tableau des différences B5G/6G, architecture cible | Terminé | `AT1-AT2-livrables.md` (à relire ; vérifier les références 3GPP / ITU avant de les citer) |
| 41 | 16/11 | AT2 : schéma d'architecture 6G (diagramme dans le chat + version Mermaid dans `AT1-AT2-livrables.md`), composants et rôles, interfaces | Terminé | à relire ; à placer dans `documentation/` du dépôt |
| 42 | 16/11 | Git : `git pull --rebase`, script `~/6g-lab/sync-repo.sh` (copie scripts, configs Open5GS / UERANSIM et résultats AT4 à AT6 vers `~/6G`), ajout de `avancement.md` et `AT1-AT2-livrables.md` dans `documentation/` (copie depuis le PC), commit, push | En cours | arborescence conservée : scripts à la racine de `membre1_infrastructure/` et `membre2_qos_mobilite/`, résultats dans `membre2_qos_mobilite/resultats/`, configs dans `membre1_infrastructure/configs/` |

## 3. Suivi des ateliers

| Atelier | Titre | Statut | Preuves | Problèmes | Prochaine étape |
|---|---|---|---|---|---|
| AT1 | Installation de l'environnement | Terminé | VM + outils + Open5GS + UERANSIM installés ; tableau B5G/6G et architecture cible dans `AT1-AT2-livrables.md` | Références 3GPP / ITU à vérifier avant citation | Relecture, puis `documentation/` |
| AT2 | Architecture 6G | Terminé | schéma d'architecture, composants et rôles, interfaces (dont celles réellement en place : Uu simulée, N2, N3, N4, SBI, N6) dans `AT1-AT2-livrables.md` | Interfaces O-RAN (E2, A1) et orchestration seulement décrites | Relecture, puis `documentation/` |
| AT3 | Enregistrement, sessions, connectivité | Terminé | UE enregistré, session PDU, ping, traceroute, iperf3 TCP/UDP | Résolu (NAT + UE dans namespace) | AT4 |
| AT4 | Plusieurs UEs et services | Terminé | 3 UEs, 3 profils, trafic simultané, mesures baseline/simultané, congestion identifiée (CPU saturé) | | AT5 |
| AT5 | QoS intelligente | Terminé | indicateurs, règle statique, règle dynamique, comparaison avant/statique/dynamique | Latence non améliorée (CPU simulé = goulot) | AT6 |
| AT6 | Slicing dynamique | Terminé | 3 slices fonctionnelles de bout en bout (AMF, SMF, UPF, NSSF, `ogstun2/3`, abonnés, UEs par slice) ; mesures avant / statique / dynamique (5 exécutions du contrôleur, 3 réglages de seuils) ; voir « Synthèse AT6 » | Isolation non obtenue (CPU simulé saturé) : atténuation par plafonnement de l'eMBB ; latence non pilotable par la limite eMBB ; forte variabilité d'une exécution à l'autre ; une seule exécution par scénario pour « avant » et « statique » | Écrire ces limites dans le rapport ; AT1, AT2 puis AT7 |
| AT7 | Virtualisation des fonctions réseau | À commencer | | | |
| AT8 | Cloud-native et orchestration | À commencer | | | |
| AT9 | Conteneurisation | À commencer | | | |
| AT10 | Edge, Fog, Cloud | À commencer | | | |
| AT11 | Orchestration intelligente | À commencer | | | |
| AT12 | Edge Intelligence | À commencer | | | |
| AT13 | O-RAN, RIC | À commencer | | | |
| AT14 | Dataset 6G | À commencer | | | |
| AT15 | Mobilité et handover | À commencer | | | |
| AT16 | V2X | À commencer | | | |
| AT17 | NTN | À commencer | | | |
| AT18 | Gestion intelligente de la mobilité | À commencer | | | |
| AT19 | Optimisation pour la mobilité | À commencer | | | |
| AT20 | Digital Twin | À commencer | | | |
| AT21 | Blockchain | À commencer | | | |
| AT22 | Quantum ML | À commencer | | | |
| AT23 | IA générative / LLM | À commencer | | | |
| AT24 | IA prédictive | À commencer | | | |
| AT25 | Détection d'anomalies | À commencer | | | |
| AT26 | Boucle AI-native | À commencer | | | |
| AT27 | Cybersécurité | À commencer | | | |
| AT28 | Projet intégrateur | À commencer | | | |

## Résultats AT3 (16/11/2026)

| Test | Commande (depuis `ue1`) | Résultat |
|---|---|---|
| Ping passerelle | `ping -I uesimtun0 10.45.0.1` | OK |
| Ping Internet | `ping -I uesimtun0 8.8.8.8` | OK |
| Traceroute | `traceroute -n -I -i uesimtun0 8.8.8.8` | 7 sauts, 1er saut = 10.45.0.1 (UPF/`ogstun`), 8.8.8.8 atteint en environ 4 ms |
| iperf3 TCP (10 s) | `iperf3 -c 10.45.0.1 -B <IP UE>` | environ 564 Mbit/s, 920 retransmissions |
| iperf3 UDP (50 Mbit/s, 10 s) | `iperf3 -c 10.45.0.1 -B <IP UE> -u -b 50M` | 0 % de perte (0/46361), gigue 0,170 ms |

Remarques : le débit mesuré est limité par le CPU de la VM (liaison radio simulée en local), pas par un vrai canal radio ; l'IP de l'UE change à chaque relance (10.45.0.x).

## Résultats AT4 (16/11/2026)

Deux scénarios de 30 s. **Baseline** : seul ue3 (navigation) génère du trafic. **Simultané** : ue1 = vidéo (TCP, 2 flux), ue2 = IoT (UDP 100 kbit/s, paquets de 100 octets), ue3 = navigation (UDP 2 Mbit/s + ping toutes les 0,2 s).

| Mesure | Baseline | Simultané |
|---|---|---|
| Vidéo : débit TCP total | n/a | 300 Mbit/s (3165 retransmissions) |
| IoT : pertes / gigue | n/a | 0,21 % (8/3750) / 0,661 ms |
| Navigation UDP : pertes / gigue | 0 % (0/37500) / 0,649 ms | 0,16 % (61/37498) / 0,574 ms |
| Navigation ping : min / moy / max | 0,143 / 1,068 / 4,833 ms | 0,186 / 1,513 / 5,810 ms |
| Navigation ping : pertes | 0 % | 0 % |
| CPU : user + system / idle | 78,1 % / 21,9 % | 100 % / 0 % |
| Débit `ogstun` (UE → réseau) | environ 2,3 Mbit/s | environ 310 Mbit/s |

Analyse :
- La congestion est visible : le CPU de la VM passe de 22 % d'idle à 0 %. Les 2 vCPU (gNB, UPF et UEs simulés) sont le goulot d'étranglement, pas la bande passante.
- Impact sur la navigation : latence moyenne +42 % (1,07 → 1,51 ms), maximum +20 %, pertes UDP de 0 % à 0,16 %. La gigue ne varie pas de façon significative (0,65 → 0,57 ms).
- Le CPU est déjà à 78 % en baseline pour seulement 2 Mbit/s : UERANSIM consomme du CPU même avec peu de trafic (boucles d'attente actives de la gNB et des UEs). À préciser dans le rapport.
- Aucune priorité n'est appliquée : la vidéo prend la plus grande part des ressources, d'où l'intérêt de la QoS (AT5) et du slicing (AT6).

## Indicateurs QoS (AT5)

| Indicateur | Outil | Cible proposée (navigation) |
|---|---|---|
| Débit | iperf3 | vidéo : le plus haut possible sans dégrader les autres flux |
| Latence | ping (0,2 s) | moyenne ≤ 1,2 ms |
| Gigue | iperf3 UDP | ≤ 1 ms |
| Pertes | iperf3 UDP | ≤ 0,05 % |
| Charge CPU | sar -u | idle > 10 % |

Référence « avant » : scénario simultané d'AT4 (sans règle). Règle testée : limite de débit sur le flux vidéo (`tc` tbf sur `uesimtun0` de ue1).

## Résultats AT5 : règle statique (16/11/2026)

Règle : `tc` tbf à 100 Mbit/s sur `uesimtun0` de ue1 (vidéo). Même scénario simultané de 30 s qu'en AT4.

| Mesure | Avant (AT4 simultané) | Après (limite statique) |
|---|---|---|
| Vidéo : débit TCP / retransmissions | 300 Mbit/s / 3165 | 96,7 Mbit/s / 0 |
| IoT : pertes / gigue | 0,21 % / 0,661 ms | 0 % / 0,506 ms |
| Navigation UDP : pertes / gigue | 0,16 % / 0,574 ms | 0 % / 0,522 ms |
| Navigation ping : min / moy / max | 0,186 / 1,513 / 5,810 ms | 0,184 / 1,661 / 6,715 ms |
| CPU : user + system / idle | 100 % / 0 % | 100 % (81,1 user + 18,9 system) / 0,02 % |
| Débit `ogstun` (UE → réseau) | environ 310 Mbit/s | environ 102 Mbit/s |

Analyse :
- Les pertes des flux sensibles disparaissent (navigation 0,16 % → 0 %, IoT 0,21 % → 0 %) et les retransmissions TCP de la vidéo passent de 3165 à 0. La gigue baisse légèrement.
- La latence de navigation ne s'améliore pas : 1,51 → 1,66 ms en moyenne, avec un écart-type d'environ 1,2 ms. La différence est dans le bruit de mesure (une seule exécution de 30 s par scénario).
- Le CPU reste saturé : limiter le débit de la vidéo ne libère pas de CPU, car la gNB et les UEs UERANSIM consomment du CPU même avec peu de trafic (78 % en baseline). L'indicateur « CPU idle > 10 % » n'est donc pas discriminant dans cet environnement.
- Conclusion : la règle statique protège contre les pertes mais pas contre la latence ; la latence est dominée par l'ordonnancement CPU de la VM, pas par une file d'attente réseau.

## Résultats AT5 : comparaison finale (16/11/2026)

| Mesure | Avant (AT4) | Statique (100 Mbit/s) | Dynamique |
|---|---|---|---|
| Vidéo : débit TCP / retransmissions | 300 Mbit/s / 3165 | 96,7 Mbit/s / 0 | 125 Mbit/s / 210 |
| Navigation UDP : pertes / gigue | 0,16 % / 0,574 ms | 0 % / 0,522 ms | 0,008 % (3/37499) / 0,687 ms |
| IoT : pertes / gigue | 0,21 % / 0,661 ms | 0 % / 0,506 ms | 0,027 % (1/3750) / 0,160 ms |
| Navigation ping : min / moy / max | 0,186 / 1,513 / 5,810 ms | 0,184 / 1,661 / 6,715 ms | 0,198 / 1,941 / 7,228 ms |
| CPU idle | 0 % | 0,02 % | 0,03 % |
| Débit `ogstun` (UE → réseau) | environ 310 Mbit/s | environ 102 Mbit/s | environ 131 Mbit/s |

Comportement du contrôleur : la limite de la vidéo a varié de 300 à 50 Mbit/s en 15 décisions (une seule remontée, à 90 Mbit/s). La latence mesurée par fenêtre de 10 pings a fluctué entre 1,0 et 3,1 ms sans relation nette avec la limite appliquée.

Analyse :
- La boucle mesurer → décider → agir fonctionne : la limite s'adapte automatiquement.
- Compromis : la règle dynamique laisse plus de débit à la vidéo que la règle statique (125 contre 97 Mbit/s) tout en gardant les pertes des flux sensibles proches de zéro (0,008 % et 0,027 %, contre 0,16 % et 0,21 % sans règle).
- La latence n'est pas améliorée (cible ≤ 1,2 ms non atteinte dans les trois cas). La moyenne la plus haute est celle du dynamique (1,94 ms), mais les écarts restent dans le bruit de mesure (écart-type d'environ 1,3 ms, une seule exécution de 30 s par scénario).
- Limites : le contrôleur envoie ses propres pings dans ue3 (légère perturbation), la fenêtre de 10 pings est bruitée, et la latence dépend surtout de l'ordonnancement CPU de la VM. Pistes : fenêtres plus longues, plusieurs exécutions moyennées, signal basé sur les pertes.

## Règle dynamique (AT5)

Script `~/6g-lab/controleur_qos.py` : toutes les 2 s environ, mesure la latence de la navigation (10 pings, ue3) puis ajuste la limite de débit de la vidéo (ue1, `tc` tbf).

| Condition (fenêtre de 10 pings) | Action |
|---|---|
| latence moyenne > 2,0 ms ou perte > 0 % | limite × 0,75 (minimum 20 Mbit/s) |
| latence moyenne < 1,4 ms pendant 2 fenêtres de suite | limite + 20 Mbit/s (maximum 300 Mbit/s) |
| sinon | pas de changement |

Départ à 300 Mbit/s. Chaque décision est enregistrée dans `~/6g-lab/at5_dynamique/controle.csv` (temps, latence, perte, limite).

## Plan des slices (AT6)

| Slice | S-NSSAI | DNN | Sous-réseau / interface UPF | UE |
|---|---|---|---|---|
| eMBB | SST 1 | internet | 10.45.0.0/16 / `ogstun` | ue1 (vidéo) |
| URLLC | SST 2 | urllc | 10.46.0.0/16 / `ogstun2` | ue3 (navigation) |
| mMTC | SST 3 | mmtc | 10.47.0.0/16 / `ogstun3` | ue2 (IoT) |

Principe : une slice = un S-NSSAI + un DNN + une interface UPF dédiée, ce qui permet d'appliquer et de mesurer une politique de ressources par slice avec `tc`. Fichiers à modifier : `amf.yaml`, `smf.yaml`, `upf.yaml`, `nssf.yaml`, abonnés (WebUI), configs UERANSIM (gNB et UEs).

## État des configs AT6 (avant modification, 16/11/2026)

| Fichier | État actuel | À faire |
|---|---|---|
| `amf.yaml` | `plmn_support` : un seul S-NSSAI `sst: 1` (PLMN 999/70, TAC 1) | ajouter `sst: 2` et `sst: 3` |
| `smf.yaml` | `session` : 10.45.0.0/16 et 2001:db8:cafe::/48, sans `dnn` | une entrée par slice avec `dnn` : internet / urllc / mmtc (10.45, 10.46, 10.47) |
| `upf.yaml` | `session` : mêmes sous-réseaux, sans `dnn` | mêmes entrées avec `dnn` et `dev` (`ogstun`, `ogstun2`, `ogstun3`) |
| `nssf.yaml` | `nsi` : un seul S-NSSAI `sst: 1` | ajouter `sst: 2` et `sst: 3` |
| Interfaces | seule `ogstun` (10.45.0.1/16) existe | créer `ogstun2` (10.46.0.1/16) et `ogstun3` (10.47.0.1/16) |
| `open5gs-gnb.yaml` | `slices` : `sst: 1` | ajouter `sst: 2` et `sst: 3` |
| `ue3.yaml` | session `apn: internet`, `sst: 1` ; `default-nssai` avec `sd: 1` | `apn: urllc`, `sst: 2` ; retirer `sd` du default-nssai |

Remarque : les configs sont celles par défaut d'Open5GS 2.8.0 ; la sauvegarde `/etc/open5gs/backup-at3` permet de revenir en arrière.

### Vérification des configs après modification (16/11/2026, 15:58)

| Élément | Résultat |
|---|---|
| Interfaces | `ogstun` 10.45.0.1/16, `ogstun2` 10.46.0.1/16, `ogstun3` 10.47.0.1/16 : toutes UP |
| `amf.yaml` | S-NSSAI SST 1, 2, 3 |
| `smf.yaml` | 3 sessions : internet (10.45), urllc (10.46), mmtc (10.47) |
| `upf.yaml` | mêmes sessions avec `dev` : `ogstun`, `ogstun2`, `ogstun3` |
| `nssf.yaml` | 3 entrées `nsi` (SST 1, 2, 3) |
| gNB | `slices` : SST 1, 2, 3 |
| ue2 | `apn: mmtc`, SST 3 (configured et default NSSAI) |
| ue3 | `apn: urllc`, SST 2 (configured et default NSSAI) |
| ue1 | `apn: internet`, SST 1 ; `sd: 1` retiré du `default-nssai` à 16:00 (corrigé, `default-nssai` = SST 1) |
| Processus | aucun `nr-gnb` / `nr-ue` en cours : à relancer |
| Scripts présents | `at4-run.sh`, `setup-netns.sh`, `setup-slices-tun.sh`, `controleur_qos.py`, logs `ue1.log` à `ue3.log` |

### Après redémarrage du cœur (16/11/2026, 15:55)

- Services `open5gs-amfd`, `smfd`, `upfd`, `nssfd` : tous `active`.
- Base MongoDB : 3 abonnés (IMSI 999700000000001, 002, 003), tous encore en `sst: 1`, session `internet`, `default_indicator: true`, AMBR 1 Gbps, QoS index 9. Les abonnés n'ont donc pas encore de slice 2 / 3 : à corriger avant de lancer les UEs.
- Rappel : le service `open5gs-sgwud` (127.0.0.6) tourne aussi, sans impact sur la 5G SA.

## Résultats AT6 : mise en place des slices (16/11/2026)

| UE | Slice | SST / DNN | IP obtenue | Interface UPF | Enregistrement / session PDU | Ping vers la passerelle (3 paquets) |
|---|---|---|---|---|---|---|
| ue1 | eMBB | 1 / internet | 10.45.0.2 | `ogstun` | réussis | 0 % de perte, 0,396 / 0,441 / 0,499 ms |
| ue3 | URLLC | 2 / urllc | 10.46.0.2 | `ogstun2` | réussis | 0 % de perte, 0,401 / 0,438 / 0,459 ms |
| ue2 | mMTC | 3 / mmtc | 10.47.0.2 | `ogstun3` | réussis | 0 % de perte, 0,391 / 0,453 / 0,485 ms |

Analyse :
- Chaque UE obtient une adresse dans le sous-réseau de sa slice : le routage par S-NSSAI + DNN fonctionne de bout en bout (AMF, NSSF, SMF, UPF).
- Les RTT sont équivalents (environ 0,44 ms) sur les trois slices : sans charge, aucune slice n'est avantagée. La différenciation devra venir des politiques `tc` par interface UPF, mesurées sous charge.
- L'adresse est affichée en /24 sur `uesimtun0` alors que le sous-réseau du SMF est un /16 : comportement d'UERANSIM, sans impact sur les tests.
- Les horodatages des logs UERANSIM (15:00) sont en UTC ; l'heure locale de la VM est UTC+1.

## Résultats AT6 : avant adaptation (16/11/2026)

Script `~/6g-lab/at6-run.sh <dossier> <flux_video>`, 30 s par scénario, sans aucune politique `tc`. Flux : eMBB = vidéo TCP (ue1 → 10.45.0.1, port 5201), mMTC = IoT UDP 100 kbit/s paquets de 100 octets (ue2 → 10.47.0.1, port 5202), URLLC = UDP 2 Mbit/s paquets de 200 octets + ping toutes les 0,2 s (ue3 → 10.46.0.1, port 5203).

| Mesure | Nominal (2 flux vidéo) | Surcharge eMBB (6 flux vidéo) |
|---|---|---|
| eMBB vidéo : débit TCP / retransmissions | 264 Mbit/s / 2388 | 299 Mbit/s / 16897 |
| mMTC IoT : pertes / gigue | 0,4 % (15/3750) / 2,164 ms | 0,69 % (26/3750) / 1,261 ms |
| URLLC UDP : pertes / gigue | 1,1 % (411/37500) / 0,387 ms | 1,1 % (425/37497) / 0,654 ms |
| URLLC ping : pertes | 1,33 % (148/150 reçus) | 0 % |
| URLLC ping : min / moy / max | 0,541 / 2,796 / 8,569 ms | 0,413 / 3,065 / 6,921 ms |
| CPU : user / system / idle | 76,29 % / 23,66 % / 0,05 % | 59,45 % / 40,51 % / 0,03 % |

Analyse :
- Les 3 slices fonctionnent simultanément, mais sans aucune isolation : la slice URLLC subit les mêmes dégradations que les autres (latence moyenne 2,8 à 3,1 ms contre 0,44 ms sans charge, pertes UDP 1,1 %).
- Le CPU est saturé dans les deux cas (idle 0,05 % et 0,03 %). En surcharge, la part système passe de 23,7 % à 40,5 % : le traitement des paquets GTP-U et de la pile réseau augmente avec le nombre de flux TCP. Le goulot est le CPU simulé, pas la bande passante.
- Passer de 2 à 6 flux vidéo n'augmente le débit que de 264 à 299 Mbit/s mais fait passer les retransmissions de 2388 à 16897 : congestion visible.
- Les pertes et latences URLLC sont plus fortes qu'en AT4 (0,16 % et 1,51 ms) : avec 3 interfaces UPF actives et 3 UEs en parallèle, la charge CPU de base est plus élevée. Les mesures AT6 ne sont comparables qu'entre elles.
- Les pertes de ping (1,33 % puis 0 %) et la différence de latence moyenne entre les deux scénarios sont dans le bruit de mesure (une seule exécution de 30 s, écart-type d'environ 1,5 ms).
- Conclusion : cette mesure sert de référence « avant adaptation ». Un effet de la politique par slice devra se lire surtout sur les pertes et les retransmissions, comme en AT5.

## Politique d'adaptation AT6 : statique (appliquée le 16/11/2026)

Script `~/6g-lab/at6-policy.sh clear|static|show` (limites modifiables : `EMBB_RATE`, `MMTC_RATE`).

| Slice | UE | Règle (`tc` tbf sur `uesimtun0`, dans le namespace) | Justification |
|---|---|---|---|
| eMBB | ue1 | 100 Mbit/s (burst 256 Kb, latency 50 ms) | même plafond qu'en AT5, comparaison directe |
| mMTC | ue2 | 5 Mbit/s (burst 32 Kb, latency 50 ms) | protège contre un IoT emballé (nominal : 0,1 Mbit/s) |
| URLLC | ue3 | aucune (fq_codel par défaut) | slice prioritaire : on cherche à la protéger |

État relevé par `at6-policy.sh show` :

| UE | Avant application | Après `static` |
|---|---|---|
| ue1 | fq_codel | tbf 100 Mbit/s |
| ue2 | fq_codel | tbf 5 Mbit/s |
| ue3 | fq_codel | fq_codel (inchangé) |

Remarque d'implémentation : les flux de test vont UE → passerelle (sens montant). Un `tc` en egress sur `ogstun*` agirait sur le sens descendant et ne limiterait pas ces flux ; la règle est donc posée côté UE (`uesimtun0`), comme en AT5. La correspondance « une slice = une interface UPF » reste valable pour les mesures.

Limites connues : une exécution de 30 s par scénario, écart-type de latence d'environ 1,5 ms, CPU saturé. Un effet éventuel se lira sur les pertes et les retransmissions, pas sur la latence moyenne. Les résultats de cette politique sont dans la section « Résultats AT6 : politique statique ».

## Résultats AT6 : politique statique (16/11/2026)

Même script `at6-run.sh`, mêmes flux et 30 s par scénario qu'« avant adaptation » ; politique : eMBB plafonnée à 100 Mbit/s, mMTC à 5 Mbit/s, URLLC sans limite. Dossiers `at6/statique_nominal` et `at6/statique_surcharge`.

| Mesure | Avant nominal | Statique nominal | Avant surcharge | Statique surcharge |
|---|---|---|---|---|
| eMBB vidéo : débit TCP / retransmissions | 264 Mbit/s / 2388 | 96,9 Mbit/s / 0 | 299 Mbit/s / 16897 | 97,1 Mbit/s / 0 |
| mMTC IoT : pertes / gigue | 0,4 % (15/3750) / 2,164 ms | 0 % (0/3750) / 0,306 ms | 0,69 % (26/3750) / 1,261 ms | 0 % (0/3750) / 0,494 ms |
| URLLC UDP : pertes / gigue | 1,1 % (411/37500) / 0,387 ms | 0 % (0/37499) / 0,635 ms | 1,1 % (425/37497) / 0,654 ms | 0 % (0/37500) / 0,490 ms |
| URLLC ping : pertes | 1,33 % | 0 % (0/150) | 0 % | 0 % (0/150) |
| URLLC ping : min / moy / max | 0,541 / 2,796 / 8,569 ms | 0,132 / 1,523 / 4,919 ms | 0,413 / 3,065 / 6,921 ms | 0,127 / 1,164 / 5,032 ms |
| CPU : user / system / idle | 76,29 / 23,66 / 0,05 % | 80,39 / 19,58 / 0,03 % | 59,45 / 40,51 / 0,03 % | 86,48 / 13,48 / 0,03 % |

Analyse :
- Les pertes disparaissent sur les trois slices (URLLC UDP 1,1 % → 0 %, mMTC 0,4 et 0,69 % → 0 %) et les retransmissions TCP de la vidéo passent de 2388 et 16897 à 0. Le résultat est identique en nominal et en surcharge : la limite absorbe la différence de charge.
- Coût pour l'eMBB : débit ramené à environ 97 Mbit/s (environ -63 % en nominal, -68 % en surcharge). Le plafond est sans gain pour l'eMBB lui-même : la politique sacrifie l'eMBB au profit des autres slices.
- Latence URLLC : moyenne 2,80 → 1,52 ms (nominal) et 3,07 → 1,16 ms (surcharge), écart-type d'environ 1,0 ms (mdev 1,052 et 0,964) ; avec 150 pings par scénario l'erreur sur la moyenne est d'environ 0,1 ms, mais une seule exécution par scénario et les mesures « avant » faites à un autre moment : une dérive de l'état de la VM n'est pas exclue. Contrairement à AT5 (aucune amélioration de latence), on observe ici une baisse : à confirmer par plusieurs exécutions alternées avant / statique. Hypothèse non vérifiée : la part système du CPU baisse (23,7 → 19,6 % et 40,5 → 13,5 %), donc moins de traitement GTP-U et pile réseau.
- La règle mMTC (5 Mbit/s) n'a jamais été atteinte (IoT nominal : 0,1 Mbit/s) : elle n'a pas agi ; l'effet vient du plafond eMBB.
- Limite par rapport au résultat attendu « isolation des services » : il s'agit d'une atténuation par plafonnement de l'eMBB, pas d'une isolation. Le CPU est toujours saturé (idle 0,03 %), partagé entre toutes les slices. Un plafond fixe dégrade l'eMBB même quand la charge est faible, d'où l'intérêt d'une règle dynamique.

## Contrôleur dynamique par slice (AT6)

Script `~/6g-lab/controleur_slices.py <durée_s> <dossier_sortie>` (variables : `START`, `LAT_HIGH`, `LAT_LOW`). Toutes les 2 s environ : 20 pings (intervalle 0,1 s) dans ue3 vers 10.46.0.1 (slice URLLC), puis ajustement de la limite eMBB (`tc` tbf sur `uesimtun0` de ue1). La règle mMTC (5 Mbit/s) reste statique. Journal : `controle.csv` (temps, latence moyenne et max, perte, limite, action).

| Condition (fenêtre de 20 pings) | Action |
|---|---|
| latence moyenne > 2,0 ms, perte > 0 % ou mesure invalide | limite × 0,75 (minimum 20 Mbit/s) |
| latence moyenne < 1,2 ms pendant 3 fenêtres de suite | limite + 20 Mbit/s (maximum 300) |
| sinon | pas de changement |

Test fonctionnel (20 s, sans charge, départ à 100 Mbit/s, `at6/dynamique_test/`) :

| Mesure | Résultat |
|---|---|
| Fenêtres | 11 (environ 2 s chacune) |
| Latence moyenne par fenêtre | 0,46 à 0,53 ms, pertes 0 % |
| Limite eMBB | 100 → 120 (t = 6 s) → 140 (t = 12 s) → 160 (t = 17,9 s) |
| État `tc` relevé à la fin | ue1 : tbf 160 Mbit/s ; ue2 : tbf 5 Mbit/s ; ue3 : fq_codel |

Analyse : la boucle mesurer → décider → agir fonctionne pour la branche « hausse » (une hausse de 20 Mbit/s toutes les 3 fenêtres, comme prévu) et la modification de `tc` est effective. Sans charge, la latence URLLC est d'environ 0,49 ms (cohérent avec 0,44 ms des pings de mise en place). La branche « baisse » n'a pas été exercée (aucune charge) : elle sera testée avec les mesures sous charge. Le test s'arrête à 21,9 s car la dernière fenêtre commence avant la fin de la durée.

### Protocole de l'étape 35 (défini le 16/11/2026, 16:30)

Objectif : exercer la branche « baisse » et observer la remontée au retour au nominal.

| Élément | Choix |
|---|---|
| Préparation | `tmux ls` : sessions `gnb`, `ue1` à `ue3`, `srv1` à `srv3` présentes (relancer `srv1` si absente) ; `at6-policy.sh clear` puis règle mMTC statique conservée par le contrôleur |
| Contrôleur | `START=300 python3 controleur_slices.py 90 at6/dynamique_charge` (départ à 300 Mbit/s pour permettre la baisse) |
| Charge en parallèle | phase 1 : 30 s, 2 flux vidéo (nominal) ; phase 2 : 30 s, 6 flux vidéo (surcharge) ; phase 3 : 30 s, 2 flux vidéo (nominal) ; mêmes flux IoT et URLLC qu'en `at6-run.sh` |
| À relever | colonne `action` de `controle.csv` par phase (`baisse` attendu en phase 2, `hausse` en phase 3), limite eMBB finale, état `tc`, débit vidéo, pertes UDP des 3 slices |
| Lecture attendue | pertes (`perte > 0`) comme signal principal ; la latence ne suit pas la limite quand le CPU est saturé (constat AT5 et AT6 statique) |

Script `~/6g-lab/at6-charge.sh <dossier>` : relève les IP des UEs, applique la politique statique, lance `sar -u`, le contrôleur (`START=300`, 96 s), l'IoT (ue2, UDP 100 kbit/s, paquets de 100 octets, port 5202) et l'URLLC (ue3, UDP 2 Mbit/s, paquets de 200 octets, port 5203) pendant 94 s, puis les trois phases vidéo (ue1, port 5201, `-P 2`, `-P 6`, `-P 2`, 30 s chacune). Fichiers produits dans `at6/<dossier>/` : `ips.txt`, `phases.txt`, `video_phase1.txt` à `video_phase3.txt`, `iot.txt`, `urllc.txt`, `cpu.txt`, `controle.csv`, `controleur.log`. Les pings de la boucle de contrôle servent de mesure de latence URLLC (pas de ping séparé, pour ne pas perturber ue3).

## Résultats AT6 : contrôleur dynamique sous charge variable (16/11/2026)

Script `at6-charge.sh dynamique_charge`, une exécution de 96 s, départ à 300 Mbit/s. Phases vidéo lancées à 15:29:40, 15:30:11 et 15:30:42 (heures UTC des logs). Les bornes de phase en secondes du contrôleur (0–31, 31–62, 62–93) sont approximatives (environ ±2 s) : le contrôleur démarre un peu avant la vidéo. IP : ue1 = 10.45.0.2, ue2 = 10.47.0.2, ue3 = 10.46.0.2.

| Phase | Flux vidéo | Débit vidéo (émis / reçu) | Retransmissions | Latence URLLC (moyenne des fenêtres) | Actions du contrôleur | Limite eMBB |
|---|---|---|---|---|---|---|
| 1 (nominal) | 2 | 105 / 104 Mbit/s | 618 | 2,02 ms (15 fenêtres) | 8 baisses, 0 hausse | 300 → 225 → 168 → 126 → 94 → 70 → 52 → 39 → 29 |
| 2 (surcharge) | 6 | 39,0 / 38,5 Mbit/s | 148 | 1,15 ms (16 fenêtres) | 2 baisses, 3 hausses | 27 à 67 |
| 3 (nominal) | 2 | 84,2 / 83,6 Mbit/s | 103 | 1,20 ms (16 fenêtres sous charge ; 1,13 ms avec les 2 dernières fenêtres, hors charge) | 0 baisse, 2 hausses sous charge (+1 hors charge à t = 97,2 s) | 67 → 107 (127 après la fin du trafic) |

Sur 94 s : IoT 1/11750 perdu (0,0085 %), gigue 0,062 ms ; URLLC UDP 14/117499 perdus (0,012 %), gigue 0,008 ms. Latence URLLC moyenne sur les 49 fenêtres : 1,41 ms (environ 1,44 ms sur les 47 fenêtres sous charge) ; 10 fenêtres au-dessus de 2,0 ms (= les 10 baisses) ; perte de ping : 0 % dans toutes les fenêtres. CPU (`sar`, 96 s) : user 86,09 % / system 11,85 % / idle 2,05 %. État `tc` final : ue1 tbf 127 Mbit/s (conforme au CSV), ue2 tbf 5 Mbit/s, ue3 fq_codel.

Comparaison indicative (méthodes de mesure différentes : fenêtres de 20 pings toutes les 0,1 s ici, ping toutes les 0,2 s ailleurs ; durées de 94 s contre 30 s) :

| Mesure | Avant (nominal / surcharge) | Statique (nominal / surcharge) | Dynamique (3 phases) |
|---|---|---|---|
| eMBB vidéo : débit / retransmissions | 264 / 299 Mbit/s ; 2388 / 16897 | 96,9 / 97,1 Mbit/s ; 0 / 0 | 105 / 39 / 84 Mbit/s ; 618 / 148 / 103 |
| URLLC UDP : pertes | 1,1 % / 1,1 % | 0 % / 0 % | 0,012 % (14/117499) |
| URLLC latence moyenne | 2,80 / 3,07 ms | 1,52 / 1,16 ms | 1,41 ms (environ 1,44 ms sous charge ; phases : 2,02 / 1,15 / 1,20) |

Analyse :
- La boucle complète mesurer → décider → agir fonctionne dans les deux sens : 10 baisses (×0,75 à chaque fois, plancher de 20 Mbit/s non atteint, minimum 27) et 6 hausses (+20 Mbit/s après 3 fenêtres sous 1,2 ms ; la dernière, à t = 97,2 s, est très probablement hors charge : 5 hausses sous charge). La branche « baisse » est validée.
- Le protocole prévu n'isole pas l'effet de la surcharge : avec un départ à 300 Mbit/s, la descente (8 baisses sur 10) a eu lieu pendant la phase 1. La phase 2 a démarré avec une limite déjà à 29 Mbit/s, donc les 6 flux vidéo ont été absorbés par le plafond. À refaire avec un départ à 100 Mbit/s (étape 36).
- La latence URLLC baisse quand la limite descend (fenêtres à 2,3 à 3,4 ms au début, environ 1 ms après la limite à 70 Mbit/s ; moyennes par phase 2,02 → 1,15 → 1,20 ms). Contrairement à AT5, la latence suit ici la limite, comme dans les mesures statiques AT6. Réserves : une seule exécution, et la latence est à la fois le signal de décision et la mesure du résultat.
- Le signal « pertes » n'a jamais déclenché (0 % dans les 49 fenêtres) : toutes les baisses viennent de la latence moyenne > 2,0 ms.
- Oscillations en phase 2 (limite entre 27 et 67 Mbit/s) : une hausse de 20 Mbit/s fait remonter la latence, ce qui provoque une baisse. Les seuils 1,2 / 2,0 ms sont proches du bruit (écart-type d'environ 1 ms). Pistes : hystérésis, pas de hausse plus petit, fenêtre plus longue.
- Coût pour l'eMBB : débit moyen d'environ 76 Mbit/s sur les 3 phases (moyenne simple), 39 Mbit/s en phase 2, contre 97 Mbit/s avec le plafond statique ; retransmissions non nulles (103 à 618) contre 0 en statique. Sur ces mesures, le dynamique ne fait pas mieux que le statique ; son intérêt (remonter la limite quand la charge baisse) n'apparaît qu'en phase 3 (limite 67 → 107 sous charge), où le débit (84 Mbit/s) reste sous le statique.
- Pertes URLLC et IoT proches de zéro mais non nulles (14 et 1 paquets) contre 0 en statique. Hypothèse non vérifiée : elles surviennent pendant la descente initiale (limite haute au début).
- CPU toujours quasi saturé (user + system = 97,9 %).
- Conclusion provisoire : le contrôleur suit la charge et protège l'URLLC à un niveau proche du statique, mais il ne le surpasse pas ; à confirmer par plusieurs exécutions.

Point d'attention : la commande de test du 16:26 mélangeait plusieurs commandes (`at6-policy.sh static`, `controle.csv`, `controleur_slices.py 20 at6/dynamique_test`, `tee`). L'exécution a bien eu lieu (sortie et CSV conformes) ; à lancer ensuite chaque commande séparément.

### Relecture de l'étape 35 : fenêtres hors charge (16/11/2026)

- Le trafic IoT et URLLC dure 94 s et la dernière phase vidéo se termine vers 93 à 94 s de l'horloge du contrôleur (bornes à ±2 s). Le contrôleur, lui, tourne 96 s et sa dernière fenêtre se termine à 97,2 s.
- Les deux dernières fenêtres (t = 95,2 s : 0,709 ms ; t = 97,2 s : 0,493 ms) ont une latence proche de celle mesurée sans charge (0,46 à 0,53 ms au test fonctionnel) : elles sont très probablement après la fin du trafic.
- Conséquences : la hausse à t = 97,2 s (107 → 127 Mbit/s) ne correspond pas à un retour au nominal sous charge. Sous charge : 5 hausses (et non 6), limite finale 107 Mbit/s (et non 127), latence moyenne de la phase 3 de 1,20 ms (16 fenêtres) au lieu de 1,13 ms, latence moyenne globale d'environ 1,44 ms (47 fenêtres) au lieu de 1,41 ms. Les 10 baisses ne changent pas.
- Les durées du contrôleur et du trafic devront être alignées pour les prochaines exécutions ; `at6-resume.sh` exclut les fenêtres au-delà de 93 s.
- Le CPU relevé par `sar` (96 s) inclut aussi ces secondes sans trafic : l'idle de 2,05 % est légèrement surévalué.

## Résultats AT6 : répétitions du contrôleur, départ à 100 Mbit/s (16/11/2026)

Deux exécutions de 96 s (`START=100 ./at6-charge.sh dynamique_charge_r2` à 20:06, `..._r3` à 20:11), après redémarrage de la VM (`start-lab.sh`). Même protocole que l'étape 35 (phases de 30 s : 2, 6 puis 2 flux vidéo). Fenêtres au-delà de 93 s exclues des moyennes par phase (bornes de phase approximatives, ±2 s).

| Mesure | r1 (départ 300, étape 35) | r2 (départ 100) | r3 (départ 100) |
|---|---|---|---|
| Actions (aucune / baisse / hausse) | 33 / 10 / 6 (5 hausses sous charge) | 39 / 9 / 1 | 43 / 6 / 0 |
| Limite eMBB en fin de phase 1 / limite finale | n/d / 107 (sous charge) | 42 / 20 | 20 / 20 |
| Vidéo, phases 1 / 2 / 3 (Mbit/s) | 105 / 39 / 84 | 69,9 / 30,2 / 23,4 | 56,5 / 19,7 / 19,6 |
| Retransmissions vidéo, phases 1 / 2 / 3 | 618 / 148 / 103 | 184 / 111 / 132 | 241 / 0 / 0 |
| Latence URLLC moyenne, phases 1 / 2 / 3 (ms) | 2,02 / 1,15 / 1,20 | 1,79 / 1,72 / 1,60 | 1,78 / 1,40 / 1,40 |
| URLLC UDP : pertes / gigue | 0,012 % (14/117499) / 0,008 ms | 0 % (0/117499) / 0,154 ms | 0 % (0/117499) / 0,276 ms |
| IoT UDP : pertes / gigue | 0,0085 % (1/11750) / 0,062 ms | 0 % (0/11750) / 0,927 ms | 0 % (0/11750) / 0,362 ms |
| CPU : user / system / idle | 86,09 / 11,85 / 2,05 % | 73,42 / 24,53 / 2,05 % | 88,68 / 9,27 / 2,05 % |
| `tc` final : ue1 / ue2 / ue3 | 127 Mbit/s / 5 Mbit/s / fq_codel | 20 Mbit/s / 5 Mbit/s / fq_codel | 20 Mbit/s / 5 Mbit/s / fq_codel |

Références statiques (étape 33, une exécution) : vidéo environ 97 Mbit/s et 0 retransmission, latence URLLC 1,52 ms (nominal) et 1,16 ms (surcharge), 0 perte.

Analyse :
- Départ à 100 Mbit/s : la limite eMBB descend au plancher de 20 Mbit/s dès la phase 1 (r2, d'après `at6-resume.sh` corrigé : baisses 3 / 3 / 3 et hausses 0 / 0 / 1 par phase, soit 9 baisses et 1 hausse, avec 100 → 75 → 56 → 42 en phase 1 ; r3 : les 6 baisses ont eu lieu en phase 1, déduit des colonnes min / max et fin de phase). Les phases 2 et 3 démarrent donc avec une limite déjà basse (20 à 42 Mbit/s) : comme à l'étape 35, la surcharge (6 flux) est absorbée par le plafond et son effet propre n'est pas isolé.
- Le contrôleur sur-limite l'eMBB : la latence moyenne des fenêtres dépasse souvent 2,0 ms dans la phase nominale (bruit de mesure, écart-type d'environ 1 ms), ce qui déclenche des baisses ; la remontée exige 3 fenêtres consécutives sous 1,2 ms, rarement atteint (moyennes de 1,4 à 1,8 ms). Résultat : 1 seule hausse sur 2 exécutions et un débit vidéo moyen d'environ 41 Mbit/s (r2) et 32 Mbit/s (r3) contre 97 Mbit/s en statique et environ 76 Mbit/s en r1.
- Aucun bénéfice de latence : à 20 Mbit/s (r3, phases 2 et 3) la latence URLLC est de 1,40 ms, du même ordre que le statique à 100 Mbit/s (1,16 à 1,52 ms). Quand le CPU est saturé, la limite eMBB ne commande pas la latence : le contrôleur n'a pas de prise sur son signal de décision.
- Pertes : 0 perte URLLC et IoT dans r2 et r3, contre 14 et 1 paquets en r1. Cohérent avec l'hypothèse « les pertes surviennent pendant la descente depuis une limite haute (300 Mbit/s) », mais 3 exécutions ne suffisent pas à l'établir.
- Variabilité : à configuration identique, r2 et r3 diffèrent nettement (système 24,5 % contre 9,3 % ; latence phase 2 : 1,72 contre 1,40 ms ; gigue IoT 0,927 contre 0,362 ms). L'hypothèse de l'étape 33 (baisse de la part système liée à la politique statique) n'est donc pas fiable : la part système varie beaucoup d'une exécution à l'autre sans changement de politique. Les écarts de latence entre scénarios restent à interpréter avec prudence.
- La gigue de r2 et r3 (URLLC 0,154 et 0,276 ms, IoT 0,927 et 0,362 ms) est plus élevée qu'en r1 (0,008 et 0,062 ms) ; r2 et r3 ont été faites après le redémarrage de la VM, r1 avant : cause non établie.
- CPU : l'idle de 2,05 % identique dans les trois exécutions s'explique par les secondes sans trafic en fin de mesure (`sar` 96 s, trafic 94 s).
- Conclusion : avec ces seuils (2,0 / 1,2 ms), le contrôleur dynamique protège l'URLLC et l'IoT (0 perte) mais au prix d'un eMBB fortement réduit, sans gain de latence par rapport à la règle statique à 100 Mbit/s. Pour la latence, l'intérêt du dynamique n'est pas démontré dans cet environnement. Pistes si le temps le permet : seuils recalibrés sur les mesures (par exemple HIGH proche de 2,5 à 3 ms), hystérésis, pas de baisse moins agressif, signal basé sur les pertes plutôt que la latence.

### Dernière tentative : seuils recalibrés (protocole défini le 16/11/2026)

Constat de r1 à r3 : la latence des fenêtres de 20 pings varie d'environ ±1 ms ; sous charge, les moyennes vont de 1,1 à 2,0 ms. Le seuil haut de 2,0 ms est donc dans le bruit (baisses inutiles, limite au plancher de 20 Mbit/s) et le seuil bas de 1,2 ms est rarement atteint (peu de hausses).

| Élément | Choix |
|---|---|
| Variante | sans modifier le code : variables d'environnement `LAT_HIGH=3.0` et `LAT_LOW=1.6`, `START=100`, mêmes phases (2 / 6 / 2 flux vidéo) |
| Commande | `LAT_HIGH=3.0 LAT_LOW=1.6 START=100 ./at6-charge.sh dynamique_v2_r1` puis `dynamique_v2_r2` |
| Hypothèse | la limite eMBB monte au-dessus de 100 Mbit/s (maximum 300) ; le débit vidéo moyen dépasse celui du statique |
| Risque | les pertes URLLC / IoT réapparaissent quand la limite est haute (constat de r1 : 14 et 1 paquets perdus) |
| Critère de succès (fixé avant la mesure) | débit vidéo moyen des 3 phases > 100 Mbit/s (statique : environ 97 Mbit/s) avec 0 perte URLLC et IoT et latence URLLC moyenne ≤ 1,6 ms |
| Si le critère n'est pas atteint | conclusion : le compromis eMBB / URLLC n'est pas résolu par un simple réglage des seuils sur la latence ; clôture de l'AT6 avec cette limite documentée |

## Résultats AT6 : dernière tentative, seuils recalibrés (16/11/2026)

`LAT_HIGH=3.0 LAT_LOW=1.6 START=100 ./at6-charge.sh dynamique_v2_r1` (20:21) puis `..._v2_r2` (20:23). Même protocole que les étapes 35 et 36 (phases de 30 s : 2, 6, 2 flux vidéo). Critère de succès fixé avant la mesure : débit vidéo moyen > 100 Mbit/s avec 0 perte URLLC et IoT et latence URLLC moyenne ≤ 1,6 ms.

| Mesure | v2_r1 | v2_r2 |
|---|---|---|
| Actions (aucune / baisse / hausse) | 39 / 2 / 8 | 46 / 1 / 2 |
| Par phase : baisses / hausses | 0 / 1, 0 / 5, 2 / 1 | 1 / 0, 0 / 1, 0 / 1 |
| Limite eMBB en fin de phase 1 / 2 / 3 | 120 / 220 / 143 (`tc` final 163, après la fin du trafic) | 75 / 95 / 115 (`tc` final 115) |
| Vidéo, phases 1 / 2 / 3 (Mbit/s) | 110 / 155 / 153 (moyenne 139) | 74,4 / 89,3 / 105 (moyenne 90) |
| Retransmissions vidéo, phases 1 / 2 / 3 | 53 / 382 / 423 | 0 / 115 / 294 |
| Latence URLLC moyenne, phases 1 / 2 / 3 (ms) | 1,47 / 1,24 / 1,96 (moyenne des fenêtres ≈ 1,56) | 1,93 / 1,64 / 1,60 (≈ 1,72) |
| URLLC UDP : pertes / gigue | 0,037 % (43/117499) / 0,162 ms | 0,084 % (99/117499) / 0,276 ms |
| IoT UDP : pertes / gigue | 0,0085 % (1/11750) / 1,442 ms | 0 % (0/11750) / 0,504 ms |
| CPU : user / system / steal / idle | 88,82 / 9,14 / 0 / 2,04 % | 86,33 / 9,92 / 1,70 / 2,06 % |

Verdict : critère non atteint dans les deux exécutions.
- v2_r1 : débit vidéo 139 Mbit/s (> 100) et latence ≈ 1,56 ms (≤ 1,6), mais 43 paquets URLLC et 1 paquet IoT perdus.
- v2_r2 : débit vidéo 90 Mbit/s (< 100), latence ≈ 1,72 ms (> 1,6) et 99 paquets URLLC perdus.

Analyse :
- Les seuils recalibrés évitent la sur-limitation des exécutions précédentes : la limite eMBB monte (jusqu'à 220 Mbit/s en v2_r1) et le débit vidéo dépasse celui du statique en v2_r1 (139 contre 97 Mbit/s).
- En contrepartie, les pertes URLLC réapparaissent (0,037 % et 0,084 %) alors qu'elles étaient nulles avec le statique et avec les exécutions à limite basse. En v2_r1, la latence URLLC remonte à 1,96 ms en phase 3 après une limite montée à 220 Mbit/s, ce qui déclenche 2 baisses : la latence réagit ici à une limite haute, contrairement aux limites basses.
- Les pertes ne suivent pourtant pas la limite de façon simple : 99 paquets perdus en v2_r2 avec des limites de 75 à 115 Mbit/s, contre 43 en v2_r1 avec des limites de 120 à 220 Mbit/s. Les instants des pertes n'ont pas été relevés ; une cause extérieure à la limite est possible (voir ci-dessous).
- Variabilité entre les deux exécutions à configuration identique : 8 contre 2 hausses, débit vidéo moyen 139 contre 90 Mbit/s, limite en fin de phase 3 de 143 contre 115 Mbit/s. Une exécution ne suffit pas à conclure et deux montrent déjà un écart important.
- Première apparition d'un `steal` non nul dans `sar` (1,70 % en v2_r2) : le CPU de la VM a été disputé par l'hyperviseur. Hypothèse non vérifiée : cela pourrait contribuer aux pertes et à la variabilité de v2_r2.
- Conclusion (prévue au protocole) : le compromis eMBB / URLLC n'est pas résolu par un réglage des seuils sur la latence. Les seuils recalibrés augmentent le débit eMBB mais ramènent des pertes URLLC ; les seuils d'origine protègent l'URLLC mais écrasent l'eMBB.

## Synthèse AT6 (16/11/2026)

| Configuration | Exécutions | Vidéo eMBB (Mbit/s) | URLLC : pertes | URLLC : latence moyenne |
|---|---|---|---|---|
| Sans règle (« avant »), nominal / surcharge | 1 / 1 | 264 / 299 | 1,1 % / 1,1 % | 2,80 / 3,07 ms |
| Statique (eMBB 100, mMTC 5 Mbit/s), nominal / surcharge | 1 / 1 | 96,9 / 97,1 | 0 % / 0 % | 1,52 / 1,16 ms |
| Dynamique, seuils 2,0 / 1,2 ms, départ 300 | 1 (r1) | moyenne 76 (105 / 39 / 84) | 0,012 % | ≈ 1,44 ms |
| Dynamique, seuils 2,0 / 1,2 ms, départ 100 | 2 (r2, r3) | moyenne 41 et 32 | 0 % et 0 % | ≈ 1,70 et 1,52 ms |
| Dynamique, seuils 3,0 / 1,6 ms, départ 100 | 2 (v2_r1, v2_r2) | moyenne 139 et 90 | 0,037 % et 0,084 % | ≈ 1,56 et 1,72 ms |

Les latences du dynamique sont des moyennes de fenêtres de 20 pings sous charge ; celles de « avant » et « statique » viennent d'un ping toutes les 0,2 s sur 30 s : comparaison indicative seulement.

Messages pour le rapport :
- Les 3 slices (S-NSSAI + DNN + interface UPF) fonctionnent de bout en bout.
- Pas d'isolation réelle : le CPU simulé est partagé et saturé ; la politique est une atténuation par plafonnement de l'eMBB.
- La règle statique est la plus simple et la plus stable (0 perte, 0 retransmission) mais sacrifie l'eMBB (environ 97 Mbit/s contre 264 à 299 sans règle).
- Le contrôleur dynamique illustre la boucle mesurer → décider → agir (baisses et hausses effectives), mais sur la latence il suit le bruit de mesure et, à limite haute, les pertes URLLC réapparaissent ; il ne surpasse pas le statique dans cet environnement.
- Forte variabilité d'une exécution à l'autre ; une seule exécution pour « avant » et « statique ».

## 4. Problèmes rencontrés et solutions

| Date | Problème | Solution |
|---|---|---|
| 16/11 | Ping via `uesimtun0` échoue alors que la session PDU est établie | Cause trouvée : la règle MASQUERADE pointait vers une interface inexistante (`ens39s0`) au lieu de `enp39s0`. Correction appliquée (règle recréée avec `enp39s0`, règles FORWARD ACCEPT présentes), mais le ping échoue toujours |
| 16/11 | Le trafic arrive sur `ogstun` (`tcpdump`) mais aucune réponse, même vers 10.45.0.1 | Cause : l'UE (`uesimtun0`, 10.45.0.2) est sur la même machine que l'UPF, donc le noyau voit une source locale et rejette le paquet (martian source). Solution appliquée : UE dans un network namespace séparé (`ue1`) → ping OK |
| 16/11 | Après `at6-run.sh at6/statique_...`, dossier introuvable (`ls` : No such file) | Le script préfixe déjà `~/6g-lab/at6/` : résultats dans `at6/at6/statique_nominal` et `statique_surcharge`. Il faut passer seulement `statique_nominal` (les dossiers « avant » étaient `avant_nominal` et `avant_surcharge`). À déplacer vers `at6/` |
| 16/11 | `srv1` absent de `tmux ls` avant les mesures statiques (seuls `srv2` et `srv3` présents) | Vérifié par `ss -ltnp` : un serveur écoute bien sur `*:5201` (PID non affiché sans `sudo`) et la vidéo se connecte à 10.45.0.1:5201 : mesures vidéo valides. Cause de l'absence de la session `srv1` élucidée plus bas (service systemd `iperf3` déjà à l'écoute sur `*:5201`) ; à relancer proprement dans `tmux` `srv1` avant les prochaines mesures |
| 16/11 | Commande de test du contrôleur saisie en plusieurs morceaux imbriqués (`at6-policy.sh static/controle.csv.py 20 …`, `tee … .logn}", flush=True)`) | Le contrôleur a quand même tourné et produit sa sortie et son CSV ; le fichier `at6/dynamique_test.log` est à vérifier (`ls -l ~/6g-lab/at6/dynamique_test*`). Cause probable : collage multi-lignes dans le terminal. Solution : lancer une commande à la fois ou utiliser un script |
| 16/11 | Au `start-lab.sh` : `pkill: killing pid 591 failed: Operation not permitted` et `srv1` absent de `tmux ls` (seuls `srv2` et `srv3` présents) | Hypothèse à vérifier : un service systemd `iperf3` (PID 591, lancé au démarrage, autre utilisateur) écoute déjà sur `*:5201` ; `iperf3 -s -B 10.45.0.1 -p 5201` ne peut pas se lier au même port et la session `srv1` se ferme aussitôt. Cela expliquerait aussi l'absence inexpliquée de `srv1` notée plus haut ; la vidéo fonctionne car elle se connecte à ce serveur générique. **Confirmé** le 16/11 : `ss` montre `*:5201` tenu par le PID 591 (utilisateur `iperf3`, `/usr/bin/iperf3 --server --interval 0`), service systemd `iperf3` `enabled` et `active` ; `srv2` (10.47.0.1:5202) et `srv3` (10.46.0.1:5203) sont bien les serveurs de `tmux`. Toutes les mesures AT6 (dont r1 à r3) ont utilisé ce serveur générique sur le port 5201. Correction appliquée (étape 38) : `systemctl disable --now iperf3`, `srv1` lancé dans `tmux` ; `ss` montre les trois serveurs liés à 10.45.0.1:5201, 10.47.0.1:5202 et 10.46.0.1:5203 |
| 16/11 | `at6-resume.sh` affiche « 0 baisses, 0 hausses » pour chaque phase alors que les totaux sont corrects (r2 : 9 baisses, 1 hausse) | Cause probable : `controle.csv` écrit avec le module `csv` de Python (fins de ligne CRLF) ; le `\r` reste collé à la colonne `action` et `$6=="baisse"` échoue dans awk (les autres colonnes et `cut | uniq -c` ne sont pas touchés). Correction appliquée (`sub(/\r$/,"",$6)` dans `at6-resume.sh`) : décomptes par phase de r2 conformes (baisses 3 / 3 / 3, hausses 0 / 0 / 1, soit 9 et 1 comme les totaux). Le correctif a suffi ; la présence de CRLF n'a pas été vérifiée directement |
| 16/11 | `phases.txt` de `dynamique_charge_r2` contient 6 lignes : 3 lignes à 20:02:37 / :38 / :39 (une tentative antérieure, trois phases d'une seconde d'écart, flux vidéo en échec immédiat, UEs non démarrés après le redémarrage) puis les 3 lignes valides (20:06:15, 20:06:46, 20:07:17) | `at6-charge.sh` ajoute à `phases.txt` (`tee -a`) sans le vider. Les autres fichiers sont réécrits : les mesures de r2 viennent bien de l'exécution de 20:06. Correction appliquée : `rm -f "$D/phases.txt"` ajouté ligne 4 de `at6-charge.sh` (vérifié par `grep`) |

## 5. Choix techniques à justifier dans le rapport

- VM unique sur AWS (pas de virtualisation imbriquée) : AT7 réalisé avec conteneurs Docker ou network namespaces.
- UE UERANSIM exécuté dans un network namespace (`ue1`) relié à la gNB par une paire veth : évite le conflit d'adresses quand cœur, gNB et UE sont sur la même VM ; un namespace par UE pour AT4.
- AT4 : un namespace par UE (`ue1` à `ue3`), reliés à un pont hôte `br-ue` (10.100.0.1) ; script `~/6g-lab/setup-netns.sh` pour tout recréer après un redémarrage.
- Dépôt Git partagé `git@github.com:jerbiiii/6G.git`, accès depuis la VM par clé SSH dédiée ; arborescence conforme à la planification du groupe (dossiers `membre1_...` à `membre4_...`, `integration/`, `documentation/`).
- Processus longs (gNB, UEs) lancés dans des sessions `tmux` nommées (`gnb`, `ue1` à `ue3`) : survivent à la déconnexion SSH, logs consultables avec `tmux attach -t <nom>` ; sessions listées avec `tmux ls`.
- Après un redémarrage de la VM : `ogstun2` / `ogstun3`, les namespaces `ue1` à `ue3`, la gNB, les UEs et les serveurs iperf3 ne sont pas persistants ; `~/6g-lab/start-lab.sh` les recrée et relance (sessions `tmux` `gnb`, `ue1` à `ue3`, `srv1` à `srv3`).
- Instance AWS : si le type d'instance est burstable (t3 / t3a), l'usage CPU soutenu (UERANSIM consomme environ 78 % du CPU même au repos) peut consommer des crédits CPU et être facturé en supplément ; `steal` à 1,70 % relevé en `dynamique_v2_r2`. Non vérifié : type d'instance et `CPUCreditBalance` (console AWS / CloudWatch).
- Pas d'interface graphique : captures avec `tcpdump`, analyse Wireshark sur le PC.
- AT27 : attaque simulée uniquement en interne (localhost / namespaces).

## 6. Prochaines étapes

0. Relancer le labo après un redémarrage : `~/6g-lab/start-lab.sh` (étape 37). Vérifier `at6/dynamique_test.log` (`ls -l ~/6g-lab/at6/dynamique_test*`).
1. AT1 et AT2 rédigés (étapes 40 et 41) : relire `AT1-AT2-livrables.md`.
2. Git (étape 42 en cours) : copier `AT1-AT2-livrables.md` et `avancement.md` dans `documentation/`, puis figer `at6/` (dont `statique_*`, `dynamique_*`, `dynamique_v2_*`), `at6-run.sh`, `at6-policy.sh`, `at6-charge.sh`, `at6-resume.sh`, `controleur_slices.py`, `setup-slices-tun.sh`, `start-lab.sh` et les configs Open5GS modifiées (`git add`, `commit`, `push`).
3. AT7 (virtualisation des fonctions réseau) puis AT8 (cloud-native, Kubernetes).
4. Vérifier le type d'instance AWS et les crédits CPU (voir section 5) ; arrêter gNB et UEs quand on ne mesure pas (`start-lab.sh` les relance en 40 s).
5. (optionnel) AT6 : répéter « avant » et « statique » (plusieurs exécutions alternées, moyennées) pour consolider la comparaison.
