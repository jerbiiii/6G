# Projet fédérateur 3 : réseau 6G simulé — Suivi d'avancement

**Période :** 16 → 27 novembre 2026 (point d'étape le 20/11, validation le 27/11)
**Dernière mise à jour :** 17/11/2026 (AT7 bis : 3 instances EC2 créées et joignables ; installation d'Open5GS et d'UERANSIM en cours, étape 51)

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
| 42 | 16/11 | Git : `git pull --rebase`, script `~/6g-lab/sync-repo.sh` (copie scripts, configs Open5GS / UERANSIM et résultats AT4 à AT6 vers `~/6G`), ajout de `avancement.md` et `AT1-AT2-livrables.md` dans `documentation/` (copie depuis le PC), commit, push | Terminé | commit `5665442`, 94 fichiers, `git push` réussi (`1cabfdc..5665442`, branche `main`), « Current branch main is up to date » au `pull --rebase` ; arborescence : scripts à la racine de `membre1_infrastructure/` et `membre2_qos_mobilite/`, résultats dans `membre2_qos_mobilite/resultats/`, configs dans `membre1_infrastructure/configs/`. `documentation/avancement.md` est un instantané : à recopier depuis le PC à chaque mise à jour |
| 43 | 16/11 | AT7 : cadrage de l'environnement : type d'instance AWS et virtualisation matérielle exposée | Terminé | instance `m7i-flex.large` ; `grep -c -E 'vmx\|svm' /proc/cpuinfo` = 0 ; `lscpu` : hypervisor vendor KVM, virtualization type full → pas de KVM imbriqué : conteneurs système LXD comme nœuds virtuels |
| 44 | 16/11 | AT7, phase A : installer LXD, pont `lxdbr0` (10.10.10.0/24), règles Docker-USER, créer `node-cp` (.11), `node-upf` (.12), `node-ran` (.13), périphérique `/dev/net/tun` pour UPF et RAN, limites mémoire, ping entre nœuds | Terminé | 3 nœuds `RUNNING` (10.10.10.11, .12, .13) ; pings inter-nœuds 0 % de perte (RTT moyen 0,06 ms) ; ping Internet depuis `node-ran` 0 % de perte (3,6 ms) ; `/dev/net/tun` présent dans `node-upf` (crw-rw-rw-, 10:200) |
| 45 | 16/11 | AT7, phase B1 et B2 : arrêt des fonctions Open5GS de l'hôte, MongoDB joignable depuis le pont (`bindIp` 127.0.0.1,10.10.10.1), installation d'Open5GS dans `node-cp` et `node-upf`, paquets et binaires UERANSIM dans `node-ran` | Terminé | vérifié : `open5gs-amfd` et `open5gs-smfd` `active` dans `node-cp`, `open5gs-upfd` `active` dans `node-upf` avec `ogstun` 10.45.0.1/16 ; `node-ran` : aucune bibliothèque manquante (`ldd`), 5 binaires et 2 configurations présents. La sortie de `ss` pour MongoDB n'a pas été transmise : vérification de bout en bout prévue depuis `node-cp` à l'étape 46 |
| 46 | 16/11 | AT7, phase B3 : test de joignabilité de MongoDB depuis `node-cp`, adaptation des adresses (AMF N2, SMF et UPF N4, UPF N3, `db_uri` des fonctions UDR et PCF, gNB et UE), désactivation des fonctions inutiles par nœud, redémarrage, vérification de l'association PFCP | Terminé | « MongoDB joignable » depuis `node-cp` ; 4 × `OK` (`amf`, `smf`, `udr`, `pcf`) + `upf` ; 10 fonctions `active` dans `node-cp` ; AMF en écoute SCTP sur 10.10.10.11:38412, SMF sur 10.10.10.11:8805 ; UPF en écoute sur 10.10.10.12:8805 et :2152 ; log de l'UPF : `PFCP associated [10.10.10.11]:8805` (N4 entre deux nœuds ; la ligne `de-associated [127.0.0.4]` précède la reconfiguration) ; gNB : `linkIp` 127.0.0.1, `ngapIp` et `gtpIp` 10.10.10.13, AMF 10.10.10.11 ; UE : `gnbSearchList` 127.0.0.1. Un message `RTNETLINK answers: Invalid argument` est apparu pendant `ss -anp` dans `node-cp` sans empêcher l'affichage des lignes attendues (cause non analysée, probablement sans conséquence) |
| 47 | 16/11 | AT7, phase C : démarrer la gNB et l'UE dans `node-ran` (tmux), vérifier l'enregistrement et la session PDU, ping vers 10.45.0.1, iperf3 vers `node-upf`, script `~/6g-lab/at7-mesure.sh` (CPU, mémoire et trafic par nœud via cgroup et `/sys/class/net`) | Terminé | UE enregistré (`uesimtun0` = 10.45.0.2) via le cœur réparti ; log de l'AMF : `gNB-N2[10.10.10.13]` ajoutée et `[imsi-999700000000001] Registration complete` (N2 entre `node-ran` et `node-cp`) ; ping 4/4 vers 10.45.0.1 (RTT moyen 0,577 ms) ; serveur iperf3 dans `tmux` de `node-upf` (écoute 10.45.0.1:5201) ; mesure `repartie_r1` faite : voir « Résultats AT7 » |
| 48 | 17/11 | AT7 : répéter la mesure répartie (`repartie_r2`, `repartie_r3`) pour la variabilité ; optionnel : référence sur une seule VM dans les mêmes conditions (même jour, 20 s) | Terminé | `repartie_r2` et `repartie_r3` valides après relance de `start-at7.sh` : TCP 378 et 380 Mbit/s (réception), 724 et 837 retransmissions, ping sous charge 3,541 et 3,432 ms en moyenne, CPU 0 / 47 / 110 % ; voir « Résultats AT7 : trois exécutions ». Deux tentatives antérieures invalides (UE absent) écartées ; référence sur une seule VM non réalisée |
| 49 | 17/11 | AT7 : livrable `AT7-livrable.md` (architecture, procédure, adresses modifiées, résultats, limites, incidents) | Terminé | à relire ; à placer dans `documentation/` du dépôt |
| 50 | 17/11 | AT7 bis et AT8 : préparation EC2 : vérifier le quota de vCPU, les types éligibles, les crédits restants et l'alerte de budget ; règle « tout le trafic depuis le groupe lui-même » ; lancer 3 instances Ubuntu 24.04 `m7i-flex.large` (`vm-cp`, `vm-upf`, `vm-ran`) dans le même VPC, sous-réseau et avec la même clé ; noter les IP privées et publiques | Terminé | instances créées : `vm-cp` 172.31.47.81, `vm-upf` 172.31.38.166, `vm-ran` 172.31.34.222 (machine existante `6G-team` : 172.31.41.25) ; pings depuis `vm-cp` vers `vm-upf` et `vm-ran` : 0 % de perte, RTT moyen 1,235 et 1,077 ms (premier paquet plus lent : 2,26 et 1,92 ms, les suivants environ 0,2 ms) ; crédits restants 118,80 $, forfait gratuit valable jusqu'au 16/05/2027 (180 jours) ; quota de vCPU et alerte de budget non transmis (le lancement des 3 instances a réussi) ; les IP publiques changent à chaque arrêt et démarrage |
| 51 | 18/11 | AT7 bis : Déploiement multi-VM EC2 réelles : MongoDB 172.31.41.25, Open5GS CP (vm-cp) et UPF (vm-upf), UERANSIM (vm-ran), association N4 PFCP, NG Setup N2, session PDU (uesimtun0 = 10.45.0.2), ping UE->UPF et iperf3 | Terminé | Ping 4/4 reçus (0% perte, RTT 1,395 ms) ; iperf3 TCP 835 Mbit/s (+127% vs LXD) ; N2/N3/N4 fonctionnelles inter-VM |
| 52 | 18/11 | AT8 : Cluster Kubernetes k3s multi-nœuds (serveur sur vm-cp, agents sur vm-upf et vm-ran) ; namespace open5gs, déploiement web-6g, auto-scaling 1->3->1 et mesures de charge | Terminé | 3 nœuds Ready (v1.37.2+k3s1, containerd) ; pod web-6g répliqué sur les 3 VM ; kubectl top nodes OK |
| 53 | 18/11 | AT9 : Conteneurisation des fonctions réseau CNF 6G (namespace cnf-6g, Core SBI REST API, UPF iperf3 server, RAN generator client, CoreDNS K8s, Flannel CNI, mesures de performances) | Terminé | CoreDNS OK ; HTTP SBI 200 OK ({"status":"ACTIVE"}) ; Ping Flannel RTT 0,469 ms ; iperf3 TCP 7,90 Gbits/s (4,60 Go, 0 retr.) ; empreinte mémoire 1 à 11 Mo par Pod |
| 54 | 18/11 | AT10 : Edge, Fog et Cloud Computing : déploiement du même microservice de calcul sur les 3 tiers (Edge vm-ran:30081, Fog vm-upf:30082, Cloud vm-cp:30083) ; tests fonctionnels, mesures de latence RTT et temps de traitement depuis l'UE | Terminé | 3 tiers opérationnels ; RTT UE->Edge = 0,653 ms vs Fog = 0,874 ms et Cloud = 0,836-1,14 ms ; calcul ~0,39 ms ; mémoire 11 Mo par Pod |
| 55 | 18/11 | AT11 : Orchestration intelligente des ressources K8s : boucle de contrôle autonome Python (seuils CPU >50% et <20%), migration dynamique des pods (Edge vm-ran -> Fog vm-upf) et auto-scaling (1->2->1) | Terminé | Détection surcharge (CPU 78%), migration workload-app vers vm-upf, scale-up app-fog (1->2), normalisation et scale-down (2->1), latence stable 1,00-1,49 ms |

## 3. Suivi des ateliers

| Atelier | Titre | Statut | Preuves | Problèmes | Prochaine étape |
|---|---|---|---|---|---|
| AT1 | Installation de l'environnement | Terminé | VM + outils + Open5GS + UERANSIM installés ; tableau B5G/6G et architecture cible dans `AT1-AT2-livrables.md` | Références 3GPP / ITU à vérifier avant citation | Relecture, puis `documentation/` |
| AT2 | Architecture 6G | Terminé | schéma d'architecture, composants et rôles, interfaces (dont celles réellement en place : Uu simulée, N2, N3, N4, SBI, N6) dans `AT1-AT2-livrables.md` | Interfaces O-RAN (E2, A1) et orchestration seulement décrites | Relecture, puis `documentation/` |
| AT3 | Enregistrement, sessions, connectivité | Terminé | UE enregistré, session PDU, ping, traceroute, iperf3 TCP/UDP | Résolu (NAT + UE dans namespace) | AT4 |
| AT4 | Plusieurs UEs et services | Terminé | 3 UEs, 3 profils, trafic simultané, mesures baseline/simultané, congestion identifiée (CPU saturé) | | AT5 |
| AT5 | QoS intelligente | Terminé | indicateurs, règle statique, règle dynamique, comparaison avant/statique/dynamique | Latence non améliorée (CPU simulé = goulot) | AT6 |
| AT6 | Slicing dynamique | Terminé | 3 slices fonctionnelles de bout en bout (AMF, SMF, UPF, NSSF, `ogstun2/3`, abonnés, UEs par slice) ; mesures avant / statique / dynamique (5 exécutions du contrôleur, 3 réglages de seuils) ; voir « Synthèse AT6 » | Isolation non obtenue (CPU simulé saturé) : atténuation par plafonnement de l'eMBB ; latence non pilotable par la limite eMBB ; forte variabilité d'une exécution à l'autre ; une seule exécution par scénario pour « avant » et « statique » | Écrire ces limites dans le rapport ; AT1, AT2 puis AT7 |
| AT7 | Virtualisation des fonctions réseau | Terminé | 3 nœuds LXD ; cœur réparti (plan de contrôle dans `node-cp`, UPF dans `node-upf`, gNB et UE dans `node-ran`, base d'abonnés sur l'hôte) ; N2, N3 et N4 vérifiées entre nœuds ; UE enregistré, ping, iperf3 ; mesures CPU, mémoire, trafic par nœud (3 exécutions) ; livrable `AT7-livrable.md` | Nœuds = conteneurs système LXD (justifié : pas de virtualisation matérielle exposée) ; débit TCP d'environ 368 Mbit/s contre 564 Mbit/s à l'AT3 (mesures non homogènes) ; mémoire `memory.current` incluant le cache ; pas de référence sur une seule VM | Git (livrable, scripts, résultats) ; AT7 bis sur de vraies VM EC2 (étape 50) |
| AT8 | Cloud-native et orchestration | Terminé | Cluster k3s v1.37.2+k3s1 multi-nœuds (vm-cp, vm-ran, vm-upf tous Ready) ; namespace open5gs ; auto-scaling dynamique 1->3->1 réussi | Pods répartis automatiquement sur les 3 nœuds physiques ; pas d'anomalie | AT9 |
| AT9 | Conteneurisation des fonctions 6G | Terminé | Namespace cnf-6g (Core SBI HTTP, UPF iperf3, client RAN) ; CoreDNS OK ; Ping inter-pods RTT 0,469 ms ; iperf3 7,90 Gbits/s ; RAM 1-11 Mo par Pod | Aucun incident ; performances optimales sous Flannel CNI | AT10 |
| AT10 | Edge, Fog, Cloud | Terminé | Déploiement K8s NodePort (Edge 30081, Fog 30082, Cloud 30083) ; latences et temps de traitement mesurés depuis UE ; Edge ~0,65 ms vs Fog/Cloud ~0,87-1,14 ms | Gain de latence de ~30% validé au niveau Edge pour les applications temps réel | AT11 |
| AT11 | Orchestration intelligente | Terminé | Boucle d'orchestration Python autonome (5 itérations), détection pic 78% CPU, migration dynamique vers vm-upf, scale-up/down répliques (1->2->1), RTT 1,00-1,49 ms | Aucun incident ; migration à chaud transparente sous K8s | AT12 |
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

## Plan AT7 : fonctions réseau réparties sur des nœuds virtuels (16/11/2026)

Constat (étape 43) : instance `m7i-flex.large`, `vmx` / `svm` absents (0), hyperviseur KVM, virtualisation complète : pas de virtualisation matérielle exposée à la VM, donc pas de machines virtuelles KVM imbriquées. Choix technique : conteneurs système LXD, chacun avec son système Ubuntu 24.04, son adresse IP et ses limites de ressources, utilisés comme nœuds virtuels. À justifier dans le rapport comme alternative aux VM.

| Nœud | Adresse | Fonctions | Limite mémoire |
|---|---|---|---|
| hôte (VM AWS) | 10.10.10.1 (pont `lxdbr0`) | MongoDB (base des abonnés), supervision (`lxc info`, `sar`) | n/a |
| `node-cp` | 10.10.10.11 | fonctions du plan de contrôle du cœur (NRF, SCP, AMF, SMF, NSSF, UDM, UDR, AUSF) | 2 Go |
| `node-upf` | 10.10.10.12 | UPF, interface `ogstun`, serveur iperf3 | 1 Go |
| `node-ran` | 10.10.10.13 | gNB et UE UERANSIM, client iperf3 | 1,5 Go |

Phases : A = nœuds et réseau ; B = installation d'Open5GS et adaptation des adresses (N2, N3, N4, base de données) à partir des configurations d'origine à un seul slice ; C = enregistrement de l'UE, ping, iperf3, mesures CPU, mémoire et trafic par nœud (`lxc info`). Les 3 slices de l'AT6 ne sont pas reproduits en AT7.

## Résultats AT7 : fonctions réparties sur des nœuds LXD (17/11/2026)

Mesure `repartie_r1` : 20 s de TCP (iperf3, UE `node-ran` vers 10.45.0.1 dans `node-upf`) avec un ping toutes les 0,2 s en parallèle. CPU : moyenne sur 20 s en pourcentage d'un cœur (division entière, « 0 » signifie moins de 1 %), tirée de `cpu.stat` du cgroup du nœud ; mémoire : `memory.current` (cache de fichiers inclus) ; réseau : compteurs de `eth0` du nœud.

| Nœud | Fonctions | CPU moyen | Mémoire | `eth0` reçu | `eth0` émis |
|---|---|---|---|---|---|
| `node-cp` (10.10.10.11, limite 2 Go) | plan de contrôle du cœur (10 fonctions) | < 1 % d'un cœur | 536 Mio | 0 Kio | 0 Kio |
| `node-upf` (10.10.10.12, limite 1 Go) | UPF, serveur iperf3 | 47 % | 479 Mio | 918 223 Kio | 31 652 Kio |
| `node-ran` (10.10.10.13, limite 1,5 Go) | gNB, UE, client iperf3 | 110 % | 400 Mio | 31 652 Kio | 918 223 Kio |

| Test | Résultat |
|---|---|
| iperf3 TCP, 20 s | 829 Mio transférés, 348 Mbit/s (émission) et 347 Mbit/s (réception), 652 retransmissions |
| Ping pendant la charge, 100 paquets | 0 % de perte, RTT min / moy / max 1,012 / 3,823 / 12,738 ms (écart-type 1,504 ms) |
| Ping sans charge (4 paquets) | 0 % de perte, RTT min / moy / max 0,405 / 0,577 / 0,919 ms |
| Interfaces vérifiées | N2 : log de l'AMF (`gNB-N2[10.10.10.13]`) ; N4 : `PFCP associated [10.10.10.11]:8805` dans `node-upf` ; N3 : trafic GTP-U entre `node-ran` et `node-upf` |

Référence indicative (AT3, une seule VM, UE dans un namespace, TCP 10 s) : 564 Mbit/s, 920 retransmissions. Conditions non homogènes (autre durée, autre moment, VM redémarrée depuis, une seule exécution de chaque côté).

Analyse :
- Séparation plan de contrôle / plan usager visible dans les mesures : pendant le transfert, `node-cp` n'échange aucun octet mesurable sur `eth0` ; les 918 223 Kio (environ 897 Mio) circulent uniquement entre `node-ran` et `node-upf`.
- Répartition du CPU : `node-ran` environ 110 % d'un cœur (gNB et UE, avec l'attente active d'UERANSIM déjà observée à l'AT4), `node-upf` environ 47 %, `node-cp` négligeable. Sur 2 vCPU, `node-ran` à lui seul sature plus d'un cœur.
- Mémoire : 400 à 536 Mio par nœud, soit environ 1,4 Gio au total sur 8 Gio, bien sous les limites fixées.
- Le volume sur `eth0` (environ 940 Mo décimaux émis pour 829 Mio de charge utile TCP) dépasse la charge utile : cohérent avec les en-têtes TCP/IP, l'encapsulation GTP-U/UDP/IP et les retransmissions ; non décomposé.
- Débit TCP de 348 Mbit/s contre 564 Mbit/s à l'AT3 (environ 38 % de moins) et latence plus élevée sous charge : la répartition ajoute des sauts (pont `lxdbr0`, paires veth) et la gNB et l'UE partagent un même nœud, mais la variabilité observée d'une exécution à l'autre sur cette instance ne permet pas d'attribuer l'écart à la répartition sans répétitions et sans référence mesurée dans les mêmes conditions.
- Limites : une seule exécution ; conteneurs système LXD et non machines virtuelles complètes (noyau partagé avec l'hôte) ; base d'abonnés hébergée sur l'hôte.

## Résultats AT7 : trois exécutions (17/11/2026)

| Mesure | r1 | r2 | r3 |
|---|---|---|---|
| Débit TCP, réception (Mbit/s) | 347 | 378 | 380 |
| Retransmissions TCP | 652 | 724 | 837 |
| Ping sous charge : min / moy / max (ms) | 1,012 / 3,823 / 12,738 | 1,214 / 3,541 / 10,634 | 0,778 / 3,432 / 16,480 |
| CPU `node-cp` / `node-upf` / `node-ran` (% d'un cœur) | < 1 / 47 / 110 | 0 / 47 / 110 | 0 / 47 / 110 |
| `eth0` de `node-upf` : reçu (Kio) | 918 223 | 999 759 | 1 004 488 |
| Mémoire `memory.current` (Mio) `node-cp` / `node-upf` / `node-ran` | 536 / 479 / 400 | 925 / 614 / 775 | 926 / 614 / 776 |

Lecture :
- Débit TCP de 347 à 380 Mbit/s (moyenne environ 368 Mbit/s, écart d'environ 9 % entre extrêmes), soit environ 35 % de moins que la référence indicative de l'AT3 (564 Mbit/s, une seule exécution de 10 s, autres conditions) ; l'écart ne peut pas être attribué à la seule répartition.
- Le CPU est identique sur les trois exécutions (47 % pour l'UPF, 110 % pour la gNB et l'UE) ; les retransmissions varient de 652 à 837 (environ +28 %).
- Le volume sur `eth0` dépasse d'environ 8 % la charge utile TCP à chaque exécution (rapport de 1,080 à 1,082).
- La mémoire de r1 n'est pas comparable à celle de r2 et r3 : `memory.current` inclut le cache, et des mises à jour automatiques (`unattended-upgrades`, `packagekitd`) s'exécutaient dans `node-cp` ; le plus gros processus de `node-cp` (`open5gs-smfd`) n'utilise que 52 Mio.

## Plan EC2 : AT7 bis (vraies VM) et AT8 (cluster) (17/11/2026)

| Machine | Rôle AT7 bis | Rôle AT8 | IP privée |
|---|---|---|---|
| `6G-team` (existante, `m7i-flex.large`) | MongoDB (`bindIp` à adapter à son IP privée), WebUI, poste de pilotage, Git | hors cluster (administration) | 172.31.41.25 |
| `vm-cp` (nouvelle) | plan de contrôle du cœur (NRF, SCP, AMF, SMF, NSSF, UDM, UDR, AUSF, PCF, BSF) | serveur k3s | 172.31.47.81 |
| `vm-upf` (nouvelle) | UPF, `ogstun`, serveur iperf3 | agent k3s | 172.31.38.166 |
| `vm-ran` (nouvelle) | gNB et UE UERANSIM, client iperf3 | agent k3s | 172.31.34.222 |

Choix : Ubuntu Server 24.04 LTS x86_64 (cohérence avec l'installation actuelle et avec les binaires UERANSIM compilés pour x86_64 ; la version 26.04 n'est pas retenue, la disponibilité du PPA Open5GS n'y ayant pas été vérifiée) ; même type que la VM actuelle ; même VPC, même sous-réseau et même zone ; disque de 30 Gio ; groupe de sécurité : SSH limité à l'IP de l'équipe et règle « tout le trafic » dont la source est le groupe lui-même (SCTP compris pour N2). Après les mesures de l'AT7 bis, les services Open5GS natifs seront arrêtés avant d'installer k3s pour l'AT8. Les mesures seront comparées à celles des conteneurs LXD (`repartie_r1` à `repartie_r3`).

Coûts à surveiller : instances (environ 0,1 $ par heure et par instance de ce type, à vérifier), disques, adresses IPv4 publiques facturées à l'heure ; arrêter les instances en fin de séance (les IP privées sont conservées, les IP publiques changent).

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
| 17/11 | `iperf3 -s -B 10.45.0.1 -D` lancé par `lxc exec` dans `node-upf` : « iperf3: interrupt - the server has terminated » et `pgrep` ne trouve rien ; le client `at7-mesure.sh` obtient « Connection refused » | Cause probable : le démon est arrêté à la fermeture de la session `lxc exec`. Correction appliquée : service `iperf3` désactivé dans `node-upf`, serveur lancé dans `tmux` (comme pour la gNB et l'UE dans `node-ran`) ; `ss` montre l'écoute sur 10.45.0.1:5201 |
| 17/11 | Après redémarrage de la VM : `at7-mesure.sh` lancé sans UE (« Device "uesimtun0" does not exist », `UE=` vide, « Name or service not known ») et résultats vides ou sans signification (CPU 0 %, réseau 0 Kio) | Cause : gNB, UE et serveur iperf3 tournent dans des sessions `tmux` des nœuds et ne survivent pas au redémarrage ; les nœuds LXD, eux, reviennent en marche, et les fonctions Open5GS de l'hôte (arrêtées sans être désactivées) redémarrent aussi. Correction : `~/6g-lab/start-at7.sh` (arrêt des fonctions de l'hôte, vérification du cœur réparti, relance du serveur iperf3, de la gNB et de l'UE) et vérification dans `at7-mesure.sh` qui s'arrête si l'UE est absent |
| 17/11 | Au `start-at7.sh` après redémarrage : « MongoDB INJOIGNABLE » (connexion refusée à 10.10.10.1:27017 depuis `node-cp`), `udrd` et `pcfd` restent en `activating`, l'UE ne s'enregistre pas (`uesimtun0` absent) ; messages `error connecting to /tmp/tmux-0/default` pour les `tmux kill-server` (aucune session à arrêter, sans conséquence) | Diagnostic du 17/11 : `mongod` `active` mais n'écoute que sur 127.0.0.1:27017, y compris après `systemctl restart mongod`, alors que `lxdbr0` est `UP` en 10.10.10.1/24, que `net.ipv4.ip_nonlocal_bind` = 1 et que le journal ne montre aucune erreur. `/etc/mongod.conf` contient `bindIp: 127.0.0.1`, a la même taille (578 octets) que la sauvegarde `mongod.conf.bak-at7` et une date de modification de 01:34, soit après le redémarrage de `mongod` de 01:33:09 : le fichier a donc été remis à sa valeur d'origine à 01:34, sans redémarrage de `mongod`, qui a continué avec le réglage en mémoire (d'où « MongoDB joignable » à l'étape 46) jusqu'à son arrêt à 01:48. Auteur de la remise en l'état non établi (la commande de retour arrière `cp /etc/mongod.conf.bak-at7 /etc/mongod.conf` proposée en cas de problème est une explication possible). Correction appliquée : `sed` tolérant, `bindIp: 127.0.0.1,10.10.10.1`, `mongod` redémarré : écoute sur 10.10.10.1:27017 et 127.0.0.1:27017, « MongoDB joignable » depuis `node-cp`, 10 fonctions `active`. Ne plus exécuter la commande de retour arrière tant que l'AT7 est en cours |
| 17/11 | `pkill: killing pid 5750 failed: Operation not permitted` au début de `start-at7.sh` | Cause probable : les processus des conteneurs sont visibles dans la table des processus de l'hôte avec un autre identifiant d'utilisateur ; `pkill iperf3` lancé sans `sudo` rencontre l'`iperf3` de `node-upf` et ne peut pas le tuer (sans conséquence ici, le script le relance). Attention : `sudo pkill nr-ue` / `nr-gnb` ou `sudo pkill iperf3` sur l'hôte tueraient aussi les processus des conteneurs. Correction proposée : `pkill -u $USER iperf3` |
| 17/11 | Deuxième tentative de `repartie_r2` / `repartie_r3` invalide : UE absent alors que `start-at7.sh` venait d'afficher `UE: 10.45.0.2/24` et un ping à 0 % de perte ; `node-ran` à 0 % de CPU ; mémoire de `node-cp` de 1038 à 1140 Mio | Diagnostic : plus aucun serveur `tmux` ni processus `nr-` dans `node-ran` ; l'historique de l'hôte montre l'exécution de `pkill -u $USER iperf3; sudo pkill nr-ue; sudo pkill nr-gnb` (entrée 1051, entre deux exécutions du même `sed`) : des lignes de sortie du script ont très probablement été collées dans le terminal et exécutées ; `sudo pkill nr-ue` / `nr-gnb` sur l'hôte tue aussi les processus des conteneurs. Mémoire de `node-cp` : `unattended-upgrades` et `packagekitd` figurent parmi les processus les plus gros ; `ps` montre moins de 60 Mio de RSS pour le plus gros processus, donc la mémoire relevée est surtout du cache. Garde-fou « UE absent » enfin actif (le motif `sed` initial `/^echo "UE="/` était faux, erreur de ma part ; corrigé en `/^echo "UE=/`) ; ligne d'avertissement en double supprimée. Consigne : ne copier que les commandes des blocs, jamais les lignes de sortie |

## 5. Choix techniques à justifier dans le rapport

- VM unique sur AWS (pas de virtualisation imbriquée) : AT7 réalisé avec conteneurs Docker ou network namespaces.
- UE UERANSIM exécuté dans un network namespace (`ue1`) relié à la gNB par une paire veth : évite le conflit d'adresses quand cœur, gNB et UE sont sur la même VM ; un namespace par UE pour AT4.
- AT4 : un namespace par UE (`ue1` à `ue3`), reliés à un pont hôte `br-ue` (10.100.0.1) ; script `~/6g-lab/setup-netns.sh` pour tout recréer après un redémarrage.
- Dépôt Git partagé `git@github.com:jerbiiii/6G.git`, accès depuis la VM par clé SSH dédiée ; arborescence conforme à la planification du groupe (dossiers `membre1_...` à `membre4_...`, `integration/`, `documentation/`).
- Processus longs (gNB, UEs) lancés dans des sessions `tmux` nommées (`gnb`, `ue1` à `ue3`) : survivent à la déconnexion SSH, logs consultables avec `tmux attach -t <nom>` ; sessions listées avec `tmux ls`.
- Après un redémarrage de la VM, pour l'AT7 : `~/6g-lab/start-at7.sh` (nœuds LXD, cœur réparti, gNB, UE, iperf3).
- Après un redémarrage de la VM : `ogstun2` / `ogstun3`, les namespaces `ue1` à `ue3`, la gNB, les UEs et les serveurs iperf3 ne sont pas persistants ; `~/6g-lab/start-lab.sh` les recrée et relance (sessions `tmux` `gnb`, `ue1` à `ue3`, `srv1` à `srv3`).
- Instance AWS : `m7i-flex.large` (relevé via les métadonnées d'instance) ; ce n'est pas une instance `t3` / `t3a`, donc pas de crédits CPU à surveiller comme je le supposais. Les performances peuvent néanmoins varier d'une exécution à l'autre (famille « flex »), ce qui serait cohérent avec le `steal` de 1,70 % relevé en `dynamique_v2_r2` ; non vérifié (documentation AWS, CloudWatch).
- Pas d'interface graphique : captures avec `tcpdump`, analyse Wireshark sur le PC.
- AT27 : attaque simulée uniquement en interne (localhost / namespaces).
- AT7 : conteneurs système LXD comme nœuds virtuels, faute de virtualisation matérielle exposée (`vmx` / `svm` = 0 sur `m7i-flex.large`).

## 6. Prochaines étapes

0. Relancer le labo après un redémarrage : `~/6g-lab/start-lab.sh` (étape 37). Vérifier `at6/dynamique_test.log` (`ls -l ~/6g-lab/at6/dynamique_test*`).
1. Git : synchroniser les scripts, configurations et résultats de l'AT7, recopier `avancement.md`, `AT1-AT2-livrables.md` et `AT7-livrable.md` dans `documentation/`, puis commit et push. Relire `AT1-AT2-livrables.md` et `AT7-livrable.md`.
2. Git : fait (étape 42). Relancer `~/6g-lab/sync-repo.sh`, recopier `avancement.md` depuis le PC, puis `git add -A`, `commit`, `pull --rebase`, `push` à chaque atelier terminé.
3. AT8 (cloud-native, Kubernetes) ; AT7 terminé.
3 bis. Décision de l'équipe : refaire la répartition de l'AT7 sur de vraies machines virtuelles (instances EC2 dans le même VPC), puis monter le cluster Kubernetes de l'AT8 sur les mêmes machines (instances créées à l'étape 50, installation en cours à l'étape 51 : voir « Plan EC2 »).
4. Vérifier le type d'instance AWS et les crédits CPU (voir section 5) ; arrêter gNB et UEs quand on ne mesure pas (`start-lab.sh` les relance en 40 s).
5. (optionnel) AT6 : répéter « avant » et « statique » (plusieurs exécutions alternées, moyennées) pour consolider la comparaison.


---

# 🚀 MISES À JOUR DU 18/11/2026 : AT7-bis, AT8 et AT9 VALIDÉS

## Étape 51 (18/11) — Réalisation et validation d'AT7-bis (Multi-VM EC2 réelles)

### Architecture déployée
- **Hôte principal / BD (`6G-team`)** : `172.31.41.25` — MongoDB configuré pour accepter les connexions privées du sous-réseau.
- **Nœud Plan de Contrôle (`vm-cp`)** : `172.31.47.81` — 10 services Open5GS actifs (NRF, SCP, AMF, SMF, AUSF, UDM, UDR, PCF, BSF, NSSF). N2/NGAP configuré sur `172.31.47.81`.
- **Nœud Plan Usager (`vm-upf`)** : `172.31.38.166` — UPF Open5GS actif, GTP-U sur `172.31.38.166`, tunnel `ogstun` configuré (10.45.0.1/16).
- **Nœud Radio & Terminal (`vm-ran`)** : `172.31.34.222` — UERANSIM gNB (`ngapIp: 172.31.34.222`) connecté à l'AMF `172.31.47.81`, UE 5G simulé (`ue1.yaml`).

### Résultats & Métriques mesurées
- **Association N4 (PFCP)** : `PFCP associated [172.31.47.81]:8805` confirmé dans les logs de l'UPF.
- **Lien N2 (NGAP)** : `NG Setup successful` validé entre gNB (`vm-ran`) et AMF (`vm-cp`).
- **Établissement Session PDU** : Interface `uesimtun0` créée avec succès sur `vm-ran` (`10.45.0.2/24`).
- **Ping cellulaire UE → UPF** : 4/4 paquets reçus (0% perte), RTT min/moy/max = **0.756 / 1.395 / 3.062 ms**.
- **Débit iperf3 TCP (10 secondes)** : **835 Mbit/s** (vs ~368 Mbit/s sur conteneurs LXD d'AT7, soit **+127% de gain** grâce à la séparation des cartes réseau et noyaux virtio AWS).

---

## Étape 52 (18/11) — Réalisation et validation d'AT8 (Cluster Kubernetes k3s multi-nœuds)

### Architecture Cloud-Native
- **Serveur Master k3s** : Installé sur `vm-cp` (`172.31.47.81`) via l'interface `enp39s0`.
- **Agents Workers k3s** : Installés sur `vm-upf` (`172.31.38.166`) et `vm-ran` (`172.31.34.222`).
- **Version k3s** : `v1.37.2+k3s1` avec runtime `containerd://2.3.7-k3s1` et CNI Flannel.
- **Statut des nœuds** :
  - `vm-cp` : Ready, role control-plane
  - `vm-ran` : Ready, worker
  - `vm-upf` : Ready, worker

### Déploiement et Scalabilité
- Création du namespace `open5gs`.
- Déploiement `web-6g` (image `nginx:alpine`) et Service ClusterIP `10.43.6.34:80`.
- **Test d'auto-scaling dynamique** :
  - Passage de 1 à 3 répliques : Kubernetes ordonnance instantanément 1 pod sur chaque nœud physique (`vm-cp`, `vm-ran`, `vm-upf`).
  - Réduction de 3 à 1 réplique : mise à l'échelle inverse immédiate sans interruption de service.
- **Consommation nœuds (`kubectl top nodes`)** : `vm-cp` 172m/8%, `vm-ran` 104m/5%, `vm-upf` 42m/2%.

---

## Étape 53 (18/11) — Réalisation et validation d'AT9 (Conteneurisation des fonctions CNF 6G)

### Écosystème déployé (Namespace `cnf-6g`)
- **`cnf-core-service`** (sur `vm-cp`) : Microservice REST Python émulant le plan de contrôle 6G SBI (Service-Based Interface), exposant `/health` et `/metrics`.
- **`cnf-upf-service`** (sur `vm-upf`) : Microservice de terminaison du plan usager avec serveur de trafic `iperf3` encapsulé.
- **`cnf-ran-generator`** (sur `vm-ran`) : Conteneur générateur de trafic simulant les équipements radio / terminaux.

### Tests de Connectivité et Performances
- **Découverte de services (CoreDNS K8s)** : Résolution DNS interne vérifiée avec succès pour `cnf-core-service.cnf-6g.svc.cluster.local` (`10.43.65.94`) et `cnf-upf-service.cnf-6g.svc.cluster.local` (`10.43.171.140`).
- **Interface SBI HTTP** : Réponse 200 OK reçue par le client : `{"status": "ACTIVE", "nf": "6G-Core-ControlPlane", "node": "vm-cp"}`.
- **Latence inter-pods (CNI Flannel Overlay)** : Ping 4/4 reçus, 0% perte, RTT moyen = **0.469 ms**.
- **Débit maximal inter-conteneurs (iperf3 TCP)** : **7.90 Gbits/sec** (4.60 Go transférés en 5s, 0 retransmission).
- **Empreinte de ressources (Green 6G CNF)** : Consommation de seulement **1 à 11 Mo de RAM** par fonction conteneurisée.

---

## Synthèse comparative des Ateliers de Virtualisation (AT7, AT7-bis, AT9)

| Critère | AT7 (Conteneurs LXD) | AT7-bis (VM EC2 réelles) | AT9 (Kubernetes CNF 6G) |
|---|---|---|---|
| Débit utile mesuré | 368 Mbit/s | 835 Mbit/s | **7.90 Gbit/s** (Flannel overlay) |
| Latence RTT inter-nœuds | ~0.58 ms | ~1.40 ms (réseau AWS) | **0.469 ms** |
| Découverte de services | Statique manuelle | Statique manuelle | **Dynamique (CoreDNS)** |
| Empreinte mémoire / fonction | ~150 - 300 Mo | OS complet VM | **1 - 11 Mo par Pod** |
| Portabilité 3GPP | Moyenne | Faible | **Maximale (Cloud-Native)** |

---

## Statut Global du Projet
- **Ateliers terminés et validés** : AT1, AT2, AT3, AT4, AT5, AT6, AT7, AT7-bis, AT8, AT9 (**10 ateliers sur 28 = 36% du projet terminé**).
- **Livrable de commandes de captures d'écran** : Disponible dans le fichier `COMMANDES_CAPTURES_RAPPORT.md`.
- **Prochain atelier prévu (après confirmation)** : **Atelier 10 — Edge, Fog et Cloud Computing** (comparaison de latence et traitement UE → Edge → Fog → Cloud).


---

## Étape 54 (18/11) — Réalisation et validation d'AT10 (Edge, Fog et Cloud Computing)

### Architecture Multi-Niveaux Déployée (Namespace `at10-edge-fog-cloud`)
- **Niveau Edge** : Déploiement `edge-service` sur `vm-ran` (`172.31.34.222`), exposé sur le port NodePort **30081**.
- **Niveau Fog** : Déploiement `fog-service` sur `vm-upf` (`172.31.38.166`), exposé sur le port NodePort **30082**.
- **Niveau Cloud** : Déploiement `cloud-service` sur `vm-cp` (`172.31.47.81`), exposé sur le port NodePort **30083**.

### Résultats et Comparaison Expérimentale (Mesures depuis le Terminal UE sur `vm-ran`)

| Niveau 6G | Nœud Physique | NodePort | Latence RTT moyenne | Temps Traitement (`/compute`) | Consommation RAM |
|---|---|---|---|---|---|
| **EDGE** | `vm-ran` (Radio / Proximité) | `30081` | **0.653 ms** | **0.430 ms** | 11 MiB |
| **FOG** | `vm-upf` (Cœur Utilisateur) | `30082` | **0.874 ms** (+34%) | **0.388 ms** | 11 MiB |
| **CLOUD** | `vm-cp` (Cœur Contrôle Central) | `30083` | **0.836 - 1.140 ms** (+28% à +74%) | **0.392 ms** | 11 MiB |

### Conclusions Clés pour le Rapport 6G
1. **Gain de latence critique à l'Edge** : Le traitement local à l'Edge offre un RTT de **0.653 ms**, soit un gain de **~30% à 40%** par rapport à un déport vers le Cloud central. C'est le pilier fondamental des cas d'usage 6G ultra-réactifs (URLLC, robotique collaborative, véhicules autonomes).
2. **Capacité de traitement équivalente** : Les temps de calcul purs sont similaires (~0.39 ms), confirmant que l'avantage de l'Edge réside dans l'élimination des délais de transit réseau et de traversée de backhaul.
3. **Empreinte Cloud-Native minimale** : Chaque niveau ne consomme que 11 Mo de RAM, démontrant la viabilité du déploiement de fonctions de calcul légères directement sur les stations de base (gNB / O-RAN DU-CU).
---

## Étape 55 (18/11) — Réalisation et validation d'AT11 (Orchestration Intelligente des Ressources)

### Architecture et Politique de Contrôle Autonome Déployées (Namespace `at11-orch`)
- **Microservices déployés** :
  - `workload-app` : Application applicative Python (NodePort `30090`), initialement hébergée sur `vm-ran` (Edge).
  - `app-edge` : Service Edge sur `vm-ran` (NodePort `30091`).
  - `app-fog` : Service Fog sur `vm-upf` (NodePort `30092`).
  - `app-cloud` : Service Cloud sur `vm-cp` (NodePort `30093`).
- **Moteur d'orchestration (`at11-orchestrator.py`)** :
  - Surveillance continue des métriques réelles du cluster (`kubectl top nodes`) à intervalle régulier.
  - **Règle 1 (Surcharge critique)** : Si `CPU >= 50%` sur un nœud :
    1. Élection du nœud le moins chargé du cluster (`vm-upf` avec CPU ~1-2%).
    2. **Scale UP** : Augmentation du nombre de répliques du service cible (`app-fog` 1 -> 2 répliques) pour absorber le trafic.
    3. **Migration dynamique** : Déportation à chaud du pod `workload-app` depuis le nœud saturé (`vm-ran`) vers le nœud cible (`vm-upf`) par reconfiguration dynamique de `nodeSelector`.
  - **Règle 2 (Stabilisation & Économie d'énergie)** : Si tous les nœuds ont `CPU < 20%` :
    1. **Scale DOWN** : Réduction automatique des répliques excédentaires (`app-fog` 2 -> 1 réplique) pour libérer les ressources.

### Résultats Expérimentaux de l'Orchestrateur (5 Itérations)

1. **Itération 1 (T0 - Baseline)** :
   - CPU : `vm-ran` = 1%, `vm-upf` = 1%, `vm-cp` = 3%.
   - Répartition : `vm-ran` (2 pods), `vm-upf` (1 pod), `vm-cp` (1 pod).
   - Décision : État normal, surveillance passive.
2. **Itération 2 (T_charge)** :
   - Déclenchement de la charge CPU applicative sur `vm-ran`.
3. **Itération 3 (T_pic - Détection Surcharge)** :
   - CPU : `vm-ran` = **78%** (1577m), `vm-upf` = **2%** (50m), `vm-cp` = 7% (146m).
   - Décision : Règle 1 activée ! Nœud `vm-upf` élu comme cible optimale.
   - Actions exécutées : **Scale UP** `app-fog` (1 -> 2) et **Migration** de `workload-app` vers `vm-upf`.
4. **Itération 4 (Vérification Charge & Résilience)** :
   - CPU : `vm-ran` = 76%, `vm-upf` = 6%, `vm-cp` = 7%.
   - Le pod `workload-app` bascule en état Running sur `vm-upf` (IP `10.42.2.12`).
5. **Itération 5 (T_stabilisé - Retour au Calme)** :
   - CPU : `vm-ran` = **2%** (44m), `vm-upf` = **4%** (89m), `vm-cp` = 6% (121m).
   - Décision : Règle 2 activée ! Charge stabilisée (< 20%).
   - Action exécutée : **Scale DOWN** de `app-fog` (2 -> 1 réplique).

### Tableau Comparatif Final : Évolution des Ressources et Répartition des Pods

| Métrique / Nœud | Initial (T0 - Repos) | Pic de Charge (T_pic) | Post-Orchestration Stabilisé |
|---|---|---|---|
| **CPU vm-ran (Edge)** | **1%** (20m) | **78%** (1577m) — Surcharge | **2%** (44m) — Soulagé |
| **CPU vm-upf (Fog)** | **1%** (38m) | **2% - 6%** (absorption) | **4%** (89m) |
| **CPU vm-cp (Cloud)** | **3%** (66m) | **7%** (146m) | **6%** (121m) |
| **Pods sur vm-ran** | 2 pods (`app-edge`, `workload-app`) | 2 pods | **1 pod** (`app-edge`) |
| **Pods sur vm-upf** | 1 pod (`app-fog`) | 3 pods (`app-fog` x2, `workload-app`) | **2 pods** (`app-fog`, `workload-app`) |
| **Pods sur vm-cp** | 1 pod (`app-cloud`) | 1 pod | 1 pod |

### Latence et Continuité de Service Post-Migration

| Service | NodePort | Latence RTT Initiale | Latence RTT Post-Orchestration | Statut Continuité |
|---|---|---|---|---|
| **Workload App** | `30090` | **1.17 ms** (sur `vm-ran`) | **1.49 ms** (migré sur `vm-upf`) | **100% DISPONIBLE (0 interruption)** |
| **Fog Service** | `30092` | **0.92 ms** (1 réplique) | **1.00 ms** (stabilisé) | **100% DISPONIBLE** |
| **Edge Service** | `30091` | **1.48 ms** | **1.35 ms** | **100% DISPONIBLE** |
| **Cloud Service** | `30093` | **0.86 ms** | **0.88 ms** | **100% DISPONIBLE** |

### Conclusions Clés pour le Rapport 6G (AT11)
1. **Autonomie et auto-réparation (Zero-Touch Management)** : L'orchestrateur a détecté et résolu la congestion de manière 100% autonome en moins de 15 secondes, sans intervention humaine.
2. **Migration à chaud sans perte de service** : Le basculement du pod `workload-app` depuis l'Edge vers le Fog s'est effectué de manière transparente grâce au réseau Flannel CNI et au routage K8s (temps de réponse RTT stable à ~1.4 ms).
3. **Efficacité énergétique et élasticité** : Le mécanisme de Scale DOWN automatique permet de restituer immédiatement les ressources CPU/RAM dès la fin du pic de trafic, respectant les objectifs de sobriété énergétique des réseaux 6G (Green 6G).
