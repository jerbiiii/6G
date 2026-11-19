# Atelier 19 (AT19) : Optimisation des ressources pour la mobilité 6G

## 1. Objectifs pédagogiques
- Concevoir et implémenter un contrôleur d'adaptation proactive des ressources dans le réseau 6G.
- Exploiter les prédictions de mobilité issues de l'AT18 (T_lead environ 2.46 s) pour anticiper les congestions de cellules cibles lors d'un afflux massif d'utilisateurs.
- Comparer rigoureusement l'approche **Réactive** (adaptation post-congestion) et l'approche **Prédictive** (AI-Native Mobility Optimization) sur 3 runs expérimentaux.
- Mesurer les gains en termes de latence moyenne/pic, de taux de perte de paquets et de violations de SLA.

## 2. Architecture & Modèle d'optimisation prédictive
- **Modèle d'anticipation** : Récupération du vecteur de trajectoire et de la vitesse estimée par le modèle de mobilité d'AT18.
- **Horizon de prédiction** : T_lead = 2.46 s avant l'arrivée effective du convoi d'UEs dans la cellule cible (Cellule B/C).
- **Contrôleur proactif** : Déclenchement d'une augmentation préventive du quota de bande passante (	c) et réallocation de la tranche URLLC/eMBB avant que la file d'attente ne sature.

## 3. Procédure & Scénarios d'expérimentation
1. **Scénario d'afflux d'utilisateurs** : Simulation de l'arrivée soudaine de 50 flux UEs mobiles convergeant vers une même cellule.
2. **Mode Réactif** : Ressources figées à leur valeur nominale ; réaction déclenchée uniquement après franchissement du seuil d'alerte (générant des files d'attente saturées et des pertes de paquets).
3. **Mode Prédictif** : Application du profil préventif T_lead secondes avant l'impact.

## 4. Résultats mesurés comparatifs (Moyenne sur 3 runs réels)

| Métrique | Approche Réactive | Approche Prédictive | Gain / Amélioration |
|---|---|---|---|
| **Latence Moyenne** | 84.95 ms | 17.92 ms | **+78.9%** (Division par ~4.7) |
| **Latence Pic (max)** | 171.26 ms | 21.49 ms | **+87.5%** (Suppression des pics) |
| **Taux de Perte de Paquets** | 3.92 % | 0.07 % | **Élimination quasi-totale** |
| **Taux de Violation SLA** | 18.79 % | 0.49 % | **Conformité stricte (< 1%)** |

*Preuve brute enregistrée sur la VM : /home/ubuntu/at19/captures/at19_results.txt*

## 5. Analyse QoS et SLA
L'approche réactive souffre d'un délai inhérent au cycle de supervision (détection de charge, transmission de l'alarme, reconfiguration), provoquant un dépassement massif du SLA (18.79% de violations). En revanche, l'anticipation par l'IA de mobilité (AT18) permet au réseau 6G d'absorber l'afflux sans rupture de service, maintenant la latence pic sous les 22 ms et un taux de violation inférieur à 0.5%.

## 6. Limites & Incidents
- **Limites** : Précision dépendante de la qualité du modèle de prédiction de trajectoire (erreurs de GPS ou masquage urbain pouvant réduire T_lead).
- **Incidents** : Aucun incident critique lors des 3 runs sur la VM principale.
