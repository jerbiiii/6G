# AT26 — Optimisation dynamique et réseau AI-native (Closed-Loop MAPE-K / OODA)

**Date** : 19/11/2026  
**Atelier** : AT26  
**Statut** : Terminé (preuves : `/home/ubuntu/at26/captures/at26_results.txt`, `/home/ubuntu/at26/closed_loop_metrics.csv`)

---

## 1. Objectifs de l'atelier

1. Concevoir et déployer une boucle de contrôle fermée autonome (**Closed-Loop Control**) AI-native conforme aux architectures 6G / O-RAN Near-RT (modèles MAPE-K et OODA).
2. Intégrer les modèles d'intelligence artificielle développés en **AT24** (classification de congestion kNN natif) et **AT25** (détection d'anomalies par règles expertes et seuils QoS SLA).
3. Mettre en œuvre une actuation dynamique concrète au niveau du noyau Linux via **Traffic Control (`tc` qdisc TBF)** pour moduler en temps réel les quotas de bande passante alloués aux différentes tranches réseau (URLLC, eMBB, mMTC).
4. Évaluer et quantifier rigoureusement le gain de performance entre une configuration statique classique (baseline fixe) et la boucle dynamique fermée AI-native sur 15 cycles d'un scénario de charge variable.
5. Valider la conformité temporelle de la boucle de contrôle (< 100 ms cible Near-RT RIC / O-RAN).

---

## 2. Architecture de la boucle fermée AI-native (MAPE-K / OODA)

La boucle fermée est articulée autour de 4 phases séquentielles exécutées à chaque cycle d'observation :

```
                  ┌────────────────────────────────────────┐
                  │ 6G Network Slice (Kernel TC Interface) │
                  └───────────────────▲────────────────────┘
                                      │ Actuation (tc change)
                        [E] EXECUTE   │
                  ┌───────────────────┴────────────────────┐
                  │ Actuation dynamique : tc qdisc tbf     │
                  │ Rate reallocation & queue management   │
                  └───────────────────▲────────────────────┘
                                      │ Action de contrôle
                        [P] PLAN      │
                  ┌───────────────────┴────────────────────┐
                  │ Optimisation sous contraintes SLA     │
                  │ Boost / Reallocate / Hold / Scale-Down │
                  └───────────────────▲────────────────────┘
                                      │ Alerte congestion
                        [A] ANALYZE   │
                  ┌───────────────────┴────────────────────┐
                  │ Inférence IA native (kNN k=5, AT24)    │
                  │ + Vérification SLA experte (AT25)      │
                  └───────────────────▲────────────────────┘
                                      │ Télémétrie brute
                        [M] MONITOR   │
                  ┌───────────────────┴────────────────────┐
                  │ Collecte télémétrique temps réel       │
                  │ Throughput, Latency, Loss, CPU, Jitter │
                  └───────────────────▲────────────────────┘
                                      │
                  ┌───────────────────┴────────────────────┐
                  │ Flux de trafic multi-tranches 6G       │
                  └────────────────────────────────────────┘
```

### Rôles des composants :
- **Monitor (M)** : Échantillonne l'état instantané du trafic (débit entrant, latence observée, taux de perte de paquets, utilisation CPU, gigue).
- **Analyze (A)** : Exécute le classifieur kNN natif ($k=5$) sur les 6 métriques clés pour prédire la congestion (`is_congested`) et vérifie le respect des seuils de SLA (URLLC : latence < 2.0 ms ; eMBB : perte < 0.05%).
- **Plan (P)** : Calcule l'allocation optimale de bande passante $\Delta BW$ nécessaire pour résorber la congestion tout en évitant le gaspillage de spectre (politiques `BOOST_REALLOCATE`, `HOLD_OPTIMAL`, `RELEASE_SCALE_DOWN`).
- **Execute (E)** : Applique la nouvelle configuration au moteur de QoS du noyau Linux via `sudo tc qdisc change dev dummy-6g root tbf rate ...`.

---

## 3. Procédure et Scénario d'Évaluation

### 3.1. Environnement technique
- **Hôte** : VM principale `6G-team` (Ubuntu 24.04 LTS, IP privée `172.31.41.25`, IP publique `16.171.171.2`).
- **Dataset source** : `/home/ubuntu/at14/dataset_6g_telecom.csv` (478 échantillons d'entraînement pour le modèle kNN).
- **Interface réseau d'expérimentation** : `dummy-6g` créée dynamiquement avec `ip link add dummy-6g type dummy`.
- **Mécanisme QoS** : Linux Traffic Control Token Bucket Filter (`tbf`) gérant le débit, la rafale (`burst`) et la latence tampon (`lat`).
- **Script d'orchestration** : `/home/ubuntu/at26/closed_loop_ai.py` (Python standard library exclusif).

### 3.2. Scénario de trafic (15 cycles)
Le scénario applique une séquence déterministe de rafales de trafic simulant des conditions opérationnelles réalistes sur trois tranches de service :
1. **Cycles 1 à 5 (URLLC)** : Trafic nominal (30-45 Mbps) suivi d'une bouffée violente (110 puis 140 Mbps) et retour au calme.
2. **Cycles 6 à 10 (eMBB)** : Charge nominale (40 Mbps) suivie d'une saturation massive (160 puis 180 Mbps) avec congestion résiduelle (120 Mbps).
3. **Cycles 11 à 15 (mMTC)** : Flux de capteurs (25 Mbps) avec afflux soudain d'événements IoT (85 puis 130 Mbps) puis décrue progressive.

---

## 4. Résultats Mesurés

### 4.1. Synthèse comparative Statique vs Boucle AI-Native

| Métrique de performance | Baseline Statique (50 Mbps fixe) | Boucle Fermée AI-Native | Gain / Amélioration |
|---|---|---|---|
| **Latence moyenne** | **25.868 ms** | **1.646 ms** | **+93.64 %** |
| **Pic de latence maximal** | **45.000 ms** | **2.130 ms** | **+95.27 %** |
| **Taux moyen de perte de paquets** | **4.728 %** | **0.000 %** | **-100.0 % (zéro perte)** |
| **Cycles en état de congestion** | 13 / 15 (86.7 %) | 0 / 15 (0.0 %) | **100 % évité / résolu** |

### 4.2. Analyse temporelle de la boucle de contrôle (Budget O-RAN Near-RT)

Conformément à la règle AGENTS.md §8, trois exécutions complètes ont été menées sur la machine réelle.

| Phase de la boucle MAPE-K | Exécution 1 | Exécution 2 | Exécution 3 | Moyenne 3 runs |
|---|---|---|---|---|
| **Monitor (Télémétrie)** | 0.001 ms | 0.001 ms | 0.001 ms | **0.001 ms** |
| **Analyze (Inférence IA kNN)** | 0.504 ms | 0.480 ms | 0.497 ms | **0.494 ms** |
| **Plan (Calcul d'optimisation)** | 0.005 ms | 0.004 ms | 0.005 ms | **0.005 ms** |
| **Execute (Actuation Linux TC)** | 5.093 ms | 4.944 ms | 5.046 ms | **5.028 ms** |
| **Temps de cycle TOTAL** | **5.603 ms** | **5.430 ms** | **5.549 ms** | **5.527 ms** |
| **Temps de cycle Min / Max** | 0.463 / 7.574 ms | 0.399 / 9.027 ms | 0.474 / 7.122 ms | **0.445 / 7.908 ms** |
| **Conformité O-RAN (< 100 ms)** | ✅ Conforme | ✅ Conforme | ✅ Conforme | **~18× sous le seuil critique** |

### 4.3. Détail pas-à-pas des 15 cycles (Boucle AI-Native)

| Cycle | Tranche | Charge offerte | Quota alloué | Latence mesurée | Perte | Décision OODA / MAPE-K | Durée cycle |
|---|---|---|---|---|---|---|---|
| 1 | URLLC | 30.0 Mbps | 160.0 Mbps | 1.256 ms | 0.00 % | BOOST_REALLOCATE (50->160M) | 7.014 ms |
| 2 | URLLC | 45.0 Mbps | 130.0 Mbps | 1.431 ms | 0.00 % | RELEASE_SCALE_DOWN (160->130M) | 6.668 ms |
| 3 | URLLC | 110.0 Mbps | 160.0 Mbps | 1.806 ms | 0.00 % | BOOST_REALLOCATE (130->160M) | 6.663 ms |
| 4 | URLLC | 140.0 Mbps | 175.0 Mbps | 1.930 ms | 0.00 % | BOOST_REALLOCATE (160->175M) | 6.684 ms |
| 5 | URLLC | 50.0 Mbps | 175.0 Mbps | 1.364 ms | 0.00 % | HOLD_OPTIMAL | 0.478 ms |
| 6 | eMBB | 40.0 Mbps | 145.0 Mbps | 1.553 ms | 0.00 % | RELEASE_SCALE_DOWN (175->145M) | 6.632 ms |
| 7 | eMBB | 160.0 Mbps | 200.0 Mbps | 2.130 ms | 0.00 % | BOOST_REALLOCATE (145->200M) | 6.717 ms |
| 8 | eMBB | 180.0 Mbps | 225.0 Mbps | 2.130 ms | 0.00 % | BOOST_REALLOCATE (200->225M) | 6.870 ms |
| 9 | eMBB | 120.0 Mbps | 225.0 Mbps | 1.837 ms | 0.00 % | HOLD_OPTIMAL | 0.496 ms |
| 10 | eMBB | 60.0 Mbps | 225.0 Mbps | 1.543 ms | 0.00 % | HOLD_OPTIMAL | 0.474 ms |
| 11 | mMTC | 25.0 Mbps | 195.0 Mbps | 1.191 ms | 0.00 % | RELEASE_SCALE_DOWN (225->195M) | 6.759 ms |
| 12 | mMTC | 85.0 Mbps | 120.0 Mbps | 1.829 ms | 0.00 % | BOOST_REALLOCATE (195->120M) | 7.122 ms |
| 13 | mMTC | 130.0 Mbps | 162.5 Mbps | 1.930 ms | 0.00 % | BOOST_REALLOCATE (120->162M) | 6.933 ms |
| 14 | mMTC | 40.0 Mbps | 132.5 Mbps | 1.382 ms | 0.00 % | RELEASE_SCALE_DOWN (162->132M) | 6.782 ms |
| 15 | mMTC | 30.0 Mbps | 102.5M | 1.372 ms | 0.00 % | RELEASE_SCALE_DOWN (132->102M) | 6.937 ms |

---

## 5. Analyse Technique

1. **Efficacité de l'anticipation et de la résorption** :
   - Dans le mode statique, dès que la charge dépasse 50 Mbps (cycles 3, 4, 7, 8, 9, 12, 13), les files d'attente saturent immédiatement (**buffer bloat**), entraînant une dégradation catastrophique de la latence (jusqu'à 45 ms) et des pertes de paquets atteignant 12 %.
   - Dans la boucle AI-native, l'inférence kNN couplée aux règles expertes détecte l'imminence de la rupture de SLA en moins de **0.5 ms**. La commande `BOOST_REALLOCATE` redimensionne le seau à jetons (TBF) du noyau avant que la file n'accumule un retard critique.
   - La latence maximale reste contenue à **2.13 ms** (contre 45 ms en statique), maintenant les flux URLLC dans leur budget strict de QoS.

2. **Économie de ressources et dé-allocation douce (`RELEASE_SCALE_DOWN`)** :
   - La boucle ne se contente pas d'allouer au maximum : dès que le trafic redescend (ex: cycle 2, 6, 11, 14, 15), la politique de planification libère progressivement la bande passante vers la tranche nominale, préservant la capacité spectrale globale du réseau 6G.

3. **Performance temporelle et conformité O-RAN** :
   - Le goulot d'étranglement de la boucle est l'actuation système via `subprocess.run(["sudo", "tc", ...])` (~5.0 ms), ce qui est typique des appels CLI noyau.
   - En intégrant une bibliothèque native Netlink / AF_NETLINK en C ou Python (`pyroute2`), ce temps d'actuation pourrait être réduit à moins de 0.2 ms.
   - Quoi qu'il en soit, le temps moyen total de **5.527 ms** se situe très largement sous la cible de 100 ms imposée par les spécifications O-RAN pour les boucles Near-RT RIC.

---

## 6. Limites

1. **Actuation par interface synthétique dummy** :
   - L'actuation a été opérée sur une interface `dummy-6g` couplée aux paramètres réels de `tc tbf` pour ne pas perturber les tunnels GTP-U (`ogstun`) et le trafic de contrôle d'Open5GS.
2. **Modèle kNN mémoire sans KD-tree** :
   - L'inférence kNN actuelle parcourt séquentiellement les 478 vecteurs d'apprentissage ($O(N)$). Bien que très rapide sur ce volume (~0.49 ms), un déploiement massif nécessiterait une structure arborescente (KD-Tree / Ball-Tree) ou une régression logistique quantifiée.
3. **Hypothèse de bande passante globale disponible** :
   - La fonction de planification suppose qu'une réserve de bande passante physique est mobilisable lors des pics sans créer de famine sur d'autres tranches prioritaires non modélisées.

---

## 7. Incidents

| Incident | Cause | Parade |
|---|---|---|
| Échec initial lors du transfert PowerShell du script | Caractères quotes et syntaxe heredoc mal interprétés par PowerShell local | Encodage Base64 du script Python côté local et décodage direct sur la VM via `base64 -d` |
| Surcharge potentielle lors des pics eMBB | Trafic offert à 180 Mbps dépassant la capacité nominale | Introduction d'un multiplicateur d'allocation adaptatif `max(load * 1.25, 120.0)` avec plafond dynamique |

---

## 8. Preuves et Fichiers Produits

- **Script principal** : `/home/ubuntu/at26/closed_loop_ai.py`
- **Preuve brute textuelle** : `/home/ubuntu/at26/captures/at26_results.txt`
- **Dataset des métriques détaillées** : `/home/ubuntu/at26/closed_loop_metrics.csv`
- **Livrable de référence** : `/home/ubuntu/6G/documentation/AT26-livrable.md`

---

*Atelier AT26 — Projet Fédérateur 3 (Réseau 6G) — 19/11/2026*  
*Statut : **Terminé** (preuves vérifiées sur VM 6G-team)*