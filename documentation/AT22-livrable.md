# AT22 — Quantum Machine Learning et Optimisation 6G

**Statut :** Terminé (preuve : at22/captures/at22_proof.txt)
**Date :** 2026-11-22

---

## 1. Objectif

Étudier l'apport du Quantum Machine Learning (QAOA — Quantum Approximate Optimization Algorithm) pour résoudre un problème d'allocation de ressources réseau 6G formulé comme un problème QUBO (Quadratic Unconstrained Binary Optimization).

---

## 2. Problème QUBO

**Allocation de bande passante** entre 3 slices (eMBB, URLLC, mMTC) :
- Variables binaires : x[i][k] = 1 si slice i reçoit le niveau k
- Niveaux : [20, 30, 50] Mbps par slice | Budget total : 100 Mbps
- 9 variables → matrice QUBO 9×9 → espace de Hilbert 2⁹ = 512 états
- Contraintes SLA : eMBB≥30, URLLC≥20, mMTC≥20 Mbps

| Slice | Niveaux | SLA Min | Utilité |
|---|---|---|---|
| eMBB  | 20/30/50 Mbps | 30 Mbps | 0.3/0.6/1.0 |
| URLLC | 20/30/50 Mbps | 20 Mbps | 0.8/1.0/1.0 |
| mMTC  | 20/30/50 Mbps | 20 Mbps | 1.0/1.0/1.0 |

---

## 3. Architecture

```
VM 6g /home/ubuntu/at22/
├── problem.py          → Formulation QUBO + évaluation solutions
├── classical_solver.py → Glouton + Brute Force exhaustif
├── qaoa_simulator.py   → Simulateur QAOA NumPy pur (p=1, 9 qubits)
├── compare.py          → 3 runs comparatifs classique vs quantique
├── app.py              → Dashboard Flask :8022 + API
├── data/comparison.csv → 3 runs de résultats
├── VERIFICATION.md     → Audit anti-hallucination
└── captures/at22_proof.txt
```

---

## 4. Résultats sur 3 runs réels

| Solveur | Utilité moy. | BW utilisée | Temps moyen | Type |
|---|---|---|---|---|
| Glouton classique | **2.80 / 3.0** | 90 Mbps | 0.015 ms | Heuristique |
| Brute Force optimal | **3.00 / 3.0** | 100 Mbps | 0.124 ms | Exhaustif |
| **QAOA simulé** | **3.00 / 3.0** | 100 Mbps | **530 ms** | Quantique simulé |

**Solution optimale trouvée :** eMBB=50Mbps (u=1.0), URLLC=30Mbps (u=1.0), mMTC=20Mbps (u=1.0)

**QAOA = optimal : 3/3 runs ✅**
**Gap Glouton/Optimal : 6.67%** (glouton suboptimal : alloue URLLC=20 au lieu de 30)

---

## 5. Paramètres QAOA optimisés

| Paramètre | Valeur |
|---|---|
| γ_opt (phase separator) | 2.464 rad |
| β_opt (mixer) | 1.941 rad |
| Énergie QUBO minimisée | -21.1014 |
| Nombre de qubits | 9 |
| Couches p | 1 |
| Méthode d'optimisation | COBYLA (scipy) |
| Échantillons mesurés | 2000 |
| Redémarrages | 5 |

---

## 6. Analyse

### QAOA vs Classique
- QAOA trouve la **solution optimale** exacte (utilité 3.0/3.0, 0% de gap)
- Le glouton classique est **sous-optimal** (utilité 2.8/3.0, gap 6.67%)
- Le Brute Force classique est également optimal mais n'est pas scalable (27 itérations ici)

### Complexité de l'espace de Hilbert
- 9 qubits → 512 amplitudes complexes simulées par NumPy
- Sur un vrai ordinateur quantique, l'état serait stocké physiquement dans les qubits

### Honnêteté sur l'avantage quantique
- **QAOA simulé ≠ ordinateur quantique réel** — simulation sur CPU classique
- Temps QAOA (~530ms) >> Brute Force classique (0.1ms) pour ce problème
- L'avantage quantique n'existe **qu'à très grande échelle** (100+ variables QUBO)
- Pédagogiquement : démonstration de la méthode QAOA et son application réseau

---

## 7. Incidents

| Incident | Cause | Solution |
|---|---|---|
| Qiskit absent | Non installé sur la VM | Simulateur NumPy pur (legal, rapide, sans dépendance) |
| Sous-agents 429 | Quota LLM épuisé | Exécution directe SSH depuis coordinateur |

---

## 8. Accès Dashboard

```bash
ssh -L 8022:localhost:8022 -i 6g-team-key.pem ubuntu@51.20.191.212
```
Puis : http://localhost:8022/dashboard
