# Livrable AT27 — Cybersécurité et Détection d'Intrusion Réseau 6G

**Auteur :** Équipe Projet 6G (Membre Cybersécurité & Infrastructure)  
**Date :** 22 novembre 2026  
**Environnement :** Testbed multi-instances AWS EC2 (VM principale `6g`, `vm-cp`, `vm-ran`, `vm-upf`), Open5GS v2.8.0, UERANSIM, k3s v1.37.2.

---

## 1. Objectif de l'Atelier
L'atelier AT27 vise à auditer, tester et sécuriser l'architecture distribuée 6G simulée à travers 4 axes fondamentaux :
1. **Cartographie exhaustive des surfaces d'attaque** et interfaces 3GPP (N2, N3, N4, SBI, K8s).
2. **Audit de chiffrement et de confidentialité** des liaisons inter-nœuds (conformité 3GPP TS 33.501).
3. **Évaluation de l'authentification 5G-AKA** : vérification des mécanismes de protection contre l'usurpation d'identité et les UEs illégitimes (Rogue UEs).
4. **Détection d'intrusion (IDS)** et tests de robustesse (déni de service / rafales UDP) avec preuve de stabilité du cœur réseau.

---

## 2. Cartographie Réelle des Interfaces et Ports Exposés

| Nœud | Interface | Protocole & Port | Rôle 3GPP | Statut d'Exposition |
|---|---|---|---|---|
| `vm-cp` (172.31.47.81) | N2 (NGAP) | SCTP `38412` | Signalisation Radio gNB <-> AMF | Écoute réseau privé |
| `vm-cp` (172.31.47.81) | N4 (PFCP) | UDP `8805` | Contrôle de Session SMF <-> UPF | Écoute réseau privé |
| `vm-cp` (172.31.47.81) | SBI (Service Based) | TCP `127.0.0.x:7777` | Bus de communication AMF/SMF/UDM/AUSF | Localhost (non exposé) |
| `vm-cp` (172.31.47.81) | Kubernetes API | TCP `6443` | API Server k3s | Écoute réseau privé |
| `vm-upf` (172.31.38.166) | N3 (GTP-U) | UDP `2152` | Encapsulation trafic usager (User Plane) | Écoute réseau privé |
| `vm-upf` (172.31.38.166) | N4 (PFCP) | UDP `8805` | Association de règles de transfert (PDR/FAR) | Écoute réseau privé |
| `vm-upf` (172.31.38.166) | Passerelle eMBB | IP `10.45.0.1` (`ogstun`) | Sortie IP tranche nominale | Actif (UP) |

---

## 3. Audit de Chiffrement des Liaisons 3GPP

L'audit des configurations réelles d'Open5GS (`/etc/open5gs/*.yaml`) révèle que **toutes les directives TLS sont commentées** en environnement de testbed de base :

| Interface | Transport | Chiffrement Observé | Risque 3GPP | Recommandation TS 33.501 |
|---|---|---|---|---|
| **N2 (NGAP)** | SCTP | **AUCUN (Clair)** | Interception de signalisation, injection d'ordres de coupure radio | IPsec ESP obligatoire ou DTLS |
| **N3 (GTP-U)** | UDP | **AUCUN (Clair)** | Écoute passive des paquets IP utilisateurs | Chiffrement IPsec en mode tunnel ou E2E applicatif |
| **N4 (PFCP)** | UDP | **AUCUN (Clair)** | Usurpation de règles de routage de sessions | IPsec ESP avec IKEv2 entre SMF et UPF |
| **SBI** | HTTP/2 | **HTTP clair (127.0.0.x)** | Faible sur l'hôte, critique en multi-conteneurs distribués | Activation de mTLS (authentification mutuelle x509) |

**Score Global de Sécurité Cryptographique : D** (Vulnérabilité aux attaques Man-in-the-Middle sur le réseau de transport).

---

## 4. Tests d'Authentification 5G-AKA

Les tests d'attachement radio ont été menés sur `vm-ran` avec capture des logs de l'AMF et de l'UDM :

### Test A : UE Légitime (`imsi-999700000000001`)
- Clés dérivées : $K_i$ et $OP_c$ provisionnées dans MongoDB.
- Échange : Initial Registration -> Authentication Request (SUCI dé-anonymisé via AUSF/UDM) -> Security Mode Command -> Registration Complete.
- Résultat : **Session PDU PSI[1] établie avec succès**.

### Test B : UE Illégitime / Rogue (`imsi-999700000000999`)
- Clés arbitraires, abonné absent de la base d'abonnés de l'opérateur.
- Échange : Attachement rejeté au niveau de l'UDM.
- Résultat : **Accès refusé, aucune clé de session générée, cœur 6G protégé contre les accès non autorisés**.

---

## 5. Tests de Robustesse & Détection d'Intrusion (IDS)

1. **Scan de ports TCP** : 8 ports testés vers le Control-Plane en 1 ms. Le cœur n'a subi aucun ralentissement.
2. **Rafale UDP N3** : 1000 paquets émis vers `172.31.38.166:2152` à un débit de 476 190 paquets/s. L'UPF a encaissé le pic sans défaillance de service.
3. **Vérification post-test** :
   - AMF Daemon : `active`
   - SMF Daemon : `active`
   - UPF Daemon : `active`
   - **Taux de disponibilité : 100%**.
4. **Moteur IDS** (`at27_ids.py`) : 5 alertes de sécurité horodatées et corrélées générées dans `data/alerts.json`.

---

## 6. Dashboard Web de Sécurité (Port 8027)

Un dashboard de supervision SOC en temps réel a été développé et déployé sur le port `8027` :
- **Indicateurs clés** : État du cœur, nombre d'alertes IDS, score crypto, conformité 5G-AKA.
- **Tableau des alertes IDS en direct** avec sévérités dynamiques (`CRITICAL`, `WARNING`, `INFO`).
- **Matrice des risques et recommandations 3GPP**.
- **Accès** : `http://localhost:8027/dashboard` (via tunnel SSH).
- **Preuve HTTP 200** : `/home/ubuntu/at27/captures/dashboard_200.txt`.

---

## 7. Fichiers et Preuves de l'Atelier
- Code IDS : `/home/ubuntu/at27/ids/at27_ids.py`
- Code API/Dashboard : `/home/ubuntu/at27/at27_app.py`
- Script robustesse : `/home/ubuntu/at27/at27_robustness.py`
- Script de test d'authentification : `/home/ubuntu/at27/at27_auth_test.sh`
- Captures brutes : `/home/ubuntu/at27/captures/`
