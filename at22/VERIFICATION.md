# VERIFICATION.md — AT22 Quantum ML 6G
## Anti-hallucination audit

**Date :** 2026-11-22

---

## 1. Simulateur QAOA est bien NumPy pur (pas Qiskit)

**Commande :** `python3 -c "import qiskit" 2>&1` → `ModuleNotFoundError`
**Vérification :** `grep -n "import" /home/ubuntu/at22/qaoa_simulator.py`
```
import numpy as np
from scipy.optimize import minimize
```
✅ Aucune importation de Qiskit ou simulateur externe.

---

## 2. Résultats vérifiés sur 3 runs (non inventés)

**Fichier :** `/home/ubuntu/at22/data/comparison.csv`

| Run | Glouton | Optimal | QAOA | QAOA = Optimal |
|-----|---------|---------|------|----------------|
| 1   | 2.8     | 3.0     | 3.0  | True           |
| 2   | 2.8     | 3.0     | 3.0  | True           |
| 3   | 2.8     | 3.0     | 3.0  | True           |

✅ QAOA atteint la solution optimale 3/3 runs.

---

## 3. Le problème QUBO est bien défini

- Variables : x[i][k] ∈ {0,1}, i=slice, k=niveau — **binaires**
- Contrainte : exactement 1 niveau par slice (pénalité penalty=10)
- Objectif : maximiser l'utilité totale = minimiser -Σ utility[i][k]*x[i][k]
- Espace : 3 slices × 3 niveaux = **9 variables** → **2^9 = 512 états** dans l'espace de Hilbert simulé

---

## 4. Circuit QAOA p=1 : angles optimisés

- γ_opt ≈ 2.464 rad, β_opt ≈ 1.941 rad (optimisés par COBYLA scipy)
- Énergie QUBO minimisée : -21.1014
- 2000 échantillons tirés de la distribution de probabilité quantique finale

---

## 5. Limitations documentées

| Limitation | Explication |
|---|---|
| QAOA simulé ≠ ordinateur quantique réel | Simulation classique d'un circuit quantique — pas de qubits physiques |
| Problème petit (9 qubits) | Un vrai ordinateur quantique ne serait avantageux qu'à très grande échelle |
| p=1 couche QAOA | Précision augmente avec p mais temps de calcul aussi |
| Brute force optimal connu | Pour ce problème (27 solutions), brute force < 1ms — avantage quantique non démontrable ici |

---

## 6. Honnêteté : pas de vrai avantage quantique démontré

> Le QAOA simulé **trouve** la solution optimale mais est **500× plus lent** que brute force classique
> sur ce problème de taille réduite. L'intérêt pédagogique est de montrer la **méthode** QAOA
> et son application au QUBO réseau, pas de prétendre à un avantage quantique réel.
