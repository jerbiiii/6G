# AT25 — Détection intelligente des anomalies réseau 6G

**Date** : 19/11/2026  
**Atelier** : AT25  
**Statut** : Terminé (preuve : `/home/ubuntu/at25/captures/at25_results.txt`, `/home/ubuntu/at25/anomalies_detectees.csv`)

---

## 1. Objectif

Implémenter et comparer trois méthodes de détection d'anomalies réseau sur le dataset 6G télécom (597 échantillons, 14 colonnes), sans bibliothèque ML externe (Python stdlib uniquement). Évaluer chaque méthode via Precision, Recall et F1-score en comparant avec la colonne ground truth `is_congested`.

---

## 2. Architecture et données

- **Dataset** : `/home/ubuntu/at14/dataset_6g_telecom.csv` — 597 échantillons
- **Colonnes** : `sample_id`, `source`, `time_s`, `slice_type`, `slice_id`, `throughput_mbps`, `latency_ms`, `loss_pct`, `jitter_ms`, `cpu_usage_pct`, `qos_limit_mbps`, `ric_action`, `ric_action_id`, `is_congested`
- **Ground truth** : `is_congested` — 192 cas positifs (congestion réelle), 405 négatifs
- **Script** : `/home/ubuntu/at25/anomaly_detection.py` (Python 3.12, stdlib uniquement)
- **VM** : VM principale 6G-team (172.31.41.25)

---

## 3. Méthodes implémentées

### Méthode 1 — Z-Score (détection statistique univariée)

**Principe** : Pour chaque feature numérique (`latency_ms`, `throughput_mbps`, `cpu_usage_pct`), calculer mean et std. Un point est anomalie si |z| > 2.5 sur au moins une feature.

| Métrique | Valeur |
|---|---|
| Anomalies détectées | 52 / 597 |
| Precision | 0.0769 |
| Recall | 0.0208 |
| F1-score | 0.0328 |
| TP / FP / FN / TN | 4 / 48 / 188 / 357 |

**Analyse** : Le Z-Score détecte principalement des outliers statistiques extrêmes (valeurs > 2.5σ). La faible performance s'explique par le fait que la congestion réseau ne se manifeste pas forcément par des valeurs statistiquement aberrantes, mais par des combinaisons de valeurs modérément élevées.

---

### Méthode 2 — Distance Mahalanobis simplifiée (détection multivariée)

**Principe** : Distance normalisée euclidienne à la moyenne sur 3 features (`latency_ms`, `cpu_usage_pct`, `loss_pct`). Seuil = percentile 95 de la distribution des distances (seuil observé : 3.4681).

| Métrique | Valeur |
|---|---|
| Seuil (p95) | 3.4681 |
| Anomalies détectées | 20 / 597 (top 5%) |
| Precision | 0.0000 |
| Recall | 0.0000 |
| F1-score | 0.0000 |
| TP / FP / FN / TN | 0 / 20 / 192 / 385 |

**Analyse** : Les 20 points les plus éloignés de la moyenne (forte latence, débit élevé à 120 Mbps) ne correspondent pas à des congestions selon le label `is_congested`. Ce résultat contre-intuitif révèle que les anomalies statistiques sur ces features ne capturent pas le phénomène de congestion tel que défini dans le dataset — la congestion peut survenir dans les plages de valeurs "normales" mais selon d'autres critères (seuils QoS, contexte de slice).

---

### Méthode 3 — Règles expertes (baseline métier)

**Principe** : Anomalie si `latency_ms > 3.5` OU `cpu_usage_pct > 90` OU `loss_pct > 0.1`.

| Métrique | Valeur |
|---|---|
| Anomalies détectées | 89 / 597 |
| Precision | 0.4494 |
| Recall | 0.2083 |
| F1-score | 0.2847 |
| TP / FP / FN / TN | 40 / 49 / 152 / 356 |

**Analyse** : Les règles expertes obtiennent les meilleures performances (F1 = 0.285). La latence élevée (> 3.5 ms) ou le CPU > 90% sont des indicateurs pertinents de congestion. Cependant, le Recall reste faible (0.208), indiquant que 152 cas de congestion réelle ne déclenchent aucune de ces règles — la congestion a donc d'autres manifestations non capturées par ces 3 seuils.

---

## 4. Tableau comparatif des résultats

| Méthode | Anomalies | Precision | Recall | F1-score | TP | FP | FN | TN |
|---|---|---|---|---|---|---|---|---|
| Z-Score (seuil \|z\|>2.5) | 52 | 0.0769 | 0.0208 | 0.0328 | 4 | 48 | 188 | 357 |
| Mahalanobis simplifié (p95) | 20 | 0.0000 | 0.0000 | 0.0000 | 0 | 20 | 192 | 385 |
| Règles expertes | **89** | **0.4494** | **0.2083** | **0.2847** | **40** | **49** | **152** | **356** |

> [!NOTE]
> Les règles expertes dominent nettement sur ce dataset. L'absence de sklearn/pandas contraint à des implémentations statistiques simplifiées qui n'atteignent pas les performances d'algorithmes ML entraînés (Random Forest, Isolation Forest complet).

---

## 5. Top 10 anomalies détectées (score Mahalanobis décroissant)

| Rang | sample_id | latency_ms | cpu_usage_pct | loss_pct | throughput_Mbps | Score | Congestion réelle |
|---|---|---|---|---|---|---|---|
| 1 | 485 | 7.00 | 35.0 | 0.0000 | 120.00 | 4.310 | Non |
| 2 | 487 | 7.00 | 35.0 | 0.0000 | 120.00 | 4.310 | Non |
| 3 | 489 | 7.00 | 35.0 | 0.0000 | 120.00 | 4.310 | Non |
| 4 | 492 | 7.00 | 35.0 | 0.0000 | 120.00 | 4.310 | Non |
| 5 | 478 | 6.00 | 35.0 | 0.0000 | 120.00 | 3.690 | Non |
| 6 | 479 | 6.00 | 35.0 | 0.0000 | 120.00 | 3.690 | Non |
| 7 | 480 | 6.00 | 35.0 | 0.0000 | 120.00 | 3.690 | Non |
| 8 | 481 | 6.00 | 35.0 | 0.0000 | 120.00 | 3.690 | Non |
| 9 | 482 | 6.00 | 35.0 | 0.0000 | 120.00 | 3.690 | Non |
| 10 | 483 | 6.00 | 35.0 | 0.0000 | 120.00 | 3.690 | Non |

**Observation** : Les points détectés comme "plus anormaux" statistiquement (latence 6-7 ms, débit 120 Mbps) ne correspondent pas à de la congestion selon le label du dataset. Ces points forment une plage de valeurs extrêmes qui caractérisent un comportement réseau différent (haut débit, latence légèrement élevée) mais pas congestionné au sens 5G/QoS.

---

## 6. Procédure de reproduction

```bash
# Prérequis : dataset présent
ls -lh ~/at14/dataset_6g_telecom.csv

# Créer dossier et exécuter
mkdir -p ~/at25/captures/
python3 /home/ubuntu/at25/anomaly_detection.py

# Vérifier résultats
cat ~/at25/captures/at25_results.txt
cat ~/at25/anomalies_detectees.csv
```

---

## 7. Limites et analyse critique

| Limite | Impact |
|---|---|
| Pas de bibliothèques ML (pandas/sklearn non installées) | Isolation Forest réel non implémentable ; Mahalanobis sans matrice de covariance complète |
| Mahalanobis simplifié = distance euclidienne normalisée | Ignore les corrélations inter-features ; sous-optimal |
| Seuil Z-Score fixe (2.5) | Non calibré sur données d'apprentissage ; à optimiser par cross-validation |
| `is_congested` : définition non documentée | Peut dépendre de critères non observés dans les 3 features (contexte slice, QoS limit) |
| Dataset déséquilibré | 192/597 = 32% de positifs — métriques F1 pénalisées par FN élevés |
| Pas de séparation train/test | Évaluation sur l'intégralité du dataset, sans holdout |

---

## 8. Incidents

| Incident | Cause | Parade |
|---|---|---|
| Mahalanobis F1=0.000 | Anomalies statistiques ≠ congestion réseau ; seuil p95 trop conservateur | Réduire seuil (p80) ou utiliser d'autres features (jitter, ric_action) |
| Z-Score faible recall | Congestion n'implique pas de valeurs extrêmes univariées | Combiner Z-Scores en règle composée |

---

## 9. Fichiers produits

| Fichier | Contenu |
|---|---|
| `/home/ubuntu/at25/anomaly_detection.py` | Script Python stdlib — 3 méthodes de détection |
| `/home/ubuntu/at25/captures/at25_results.txt` | Résultats complets : métriques + top 10 |
| `/home/ubuntu/at25/anomalies_detectees.csv` | Top 10 anomalies CSV avec scores |
| `/home/ubuntu/6G/documentation/AT25-livrable.md` | Ce livrable |
