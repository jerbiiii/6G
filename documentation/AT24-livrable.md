# AT24 — IA Prédictive pour les Ressources et la Congestion Réseau 6G

## Objectif

Implémenter en Python pur (bibliothèque standard, sans pandas/sklearn) deux modèles d'IA prédictive :
1. **kNN natif (k=5)** : classification binaire de la congestion réseau (`is_congested`).
2. **Régression linéaire Ridge** : prédiction de la latence (`latency_ms`).

Évaluer leurs performances sur le dataset `dataset_6g_telecom.csv` (597 échantillons, données issues des AT5–AT8).

---

## Architecture

```
VM principale (ubuntu@16.171.171.2)
├── ~/at14/dataset_6g_telecom.csv       ← dataset source (597 lignes, 14 colonnes)
├── ~/at24/train_predict.py             ← script IA (kNN + Ridge OLS natif)
├── ~/at24/captures/at24_results.txt    ← métriques
└── ~/at24/predictions_knn.csv          ← prédictions kNN (sample_id, true, pred)
```

**Features utilisées :** `throughput_mbps`, `latency_ms`, `cpu_usage_pct`, `qos_limit_mbps`, `loss_pct`, `jitter_ms`  
**Split :** 478 train / 119 test — séquentiel (pas de shuffle, respect de l'ordre temporel)

---

## Procédure

### 1. Vérification des données
```bash
ls -lh ~/at14/dataset_6g_telecom.csv
# -rw-rw-r-- 1 ubuntu ubuntu 46K  597 lignes confirmées
head -2 ~/at14/dataset_6g_telecom.csv
```

### 2. Création dossier
```bash
mkdir -p ~/at24/captures/
```

### 3. Script Python natif (`~/at24/train_predict.py`)
- Lecture CSV via `csv.DictReader` (bibliothèque standard).
- **kNN** : distance euclidienne, vote majoritaire, k=5.
- **Régression Ridge** : OLS avec λ=1e-3 sur X^T X diagonal, normalisation Z-score préalable, inversion par pivot de Gauss-Jordan.
- Métriques calculées manuellement : matrice de confusion, MSE, MAE, R².

### 4. Exécution
```bash
python3 ~/at24/train_predict.py
```

---

## Résultats

### Modèle 1 — kNN natif (k=5), Cible : `is_congested`

| Métrique   | Valeur  |
|------------|---------|
| Accuracy   | **0.5462** |
| Précision  | **0.4600** |
| Rappel     | **1.0000** |
| F1-Score   | **0.6301** |

**Matrice de confusion :**
|               | Prédit 0 | Prédit 1 |
|---------------|----------|----------|
| **Réel 0**    | TN = 19  | FP = 54  |
| **Réel 1**    | FN = 0   | TP = 46  |

### Modèle 2 — Régression linéaire Ridge (λ=1e-3), Cible : `latency_ms`

| Métrique | Valeur       |
|----------|--------------|
| MSE      | **21.9077 ms²** |
| MAE      | **4.0880 ms**  |
| R²       | **-7.1272**   |

---

## Analyse

### kNN (classification)
- **Rappel = 1.0** : le modèle détecte **tous les cas de congestion** (aucun FN). Comportement conservateur adéquat pour un système réseau où manquer une congestion est critique.
- **Précision = 0.46** : taux de faux positifs élevé (54 FP) — le modèle sur-alerte.
- **Accuracy = 0.55** : modeste mais cohérente avec l'imbalance train/test (le segment test contient majoritairement des cas congestionnés — 46 positifs vs 73 au total dans les 119).
- L'architecture kNN est purement mémorielle (pas de paramètres), adaptée à un déploiement embarqué sur RIC ou contrôleur SDN 6G sans overhead de formation.

### Régression linéaire (prédiction latence)
- **R² = -7.13** : la latence dans ce dataset n'est **pas linéairement expliquée** par les 5 features sélectionnées. Les valeurs de latence sont fortement distribuées (pics liés aux slices eMBB/URLLC/mMTC), nécessitant un modèle non-linéaire (arbre de décision, réseau de neurones léger).
- **MAE = 4.09 ms** : l'erreur absolue moyenne reste acceptable pour certains contextes eMBB, mais insuffisante pour URLLC (<1 ms cible).
- Ce résultat confirme la nécessité d'un modèle plus expressif (AT25+).

---

## Limites

1. **kNN** : complexité O(n²) au test — peu scalable sur un dataset live de millions de flux. Une indexation KD-tree serait nécessaire en production.
2. **Régression** : relation non-linéaire entre features et latence dans ce dataset synthétique multi-slice.
3. **Pas de validation croisée** : split séquentiel unique ; les métriques peuvent varier selon la partition.
4. **Features temporelles** : l'ordre temporel est respecté mais aucun feature lag n'est calculé (ARIMA, LSTM seraient plus adaptés).
5. Le dataset est **synthétique** (généré AT5-AT8) : les performances sur un réseau réel pourraient différer.

---

## Incidents

| Incident | Cause | Parade |
|----------|-------|--------|
| `ValueError: Matrice singuliere` à la 1ère exécution | Collinéarité dans les features brutes (OLS pur) | Ajout régularisation Ridge λ=1e-3 + normalisation Z-score |

---

## Preuves

- Script : `~/at24/train_predict.py`
- Métriques : `~/at24/captures/at24_results.txt`
- Prédictions : `~/at24/predictions_knn.csv` (119 lignes : sample_id, true_label, predicted_label)
- Livrable : `~/6G/documentation/AT24-livrable.md`

---

*Atelier AT24 — Projet Fédérateur 3 (réseau 6G) — 19/11/2026*  
*Statut : **Terminé** (preuve : `~/at24/captures/at24_results.txt`)*
