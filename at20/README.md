# Digital Twin Intelligent du Réseau 6G (AT20)

## Présentation
Ce projet implémente un Jumeau Numérique (Digital Twin) hybride pour un réseau cellulaire 5G/6G basé sur Open5GS, UERANSIM et k3s déployé sur AWS EC2.
Le jumeau combine :
1. Une modélisation analytique de théorie des files d'attente $M/M/1$ ($W = 1 / (\mu - \lambda)$).
2. Un modèle de régression Ridge (Scikit-Learn) ré-étalonné en continu sur les métriques réelles.
3. Un simulateur de scénarios What-If (S1 eMBB burst, S2 URLLC load, S3 gNB failover, S4 UPF CPU limit).
4. Un banc de validation physique mesurant les écarts MAPE/RMSE.
5. Une interface Web de supervision et simulation visuelle en temps réel.

## Architecture des Fichiers
- `collector.py` : Collecteur périodique (5s) des métriques réelles (`metrics.csv` et `mobility.csv`).
- `twin.py` : Moteur Digital Twin hybride (calibration, inférence, scénarios what-if).
- `validate.py` : Injection physique des scénarios sur le réseau réel, calcul MAPE/RMSE (`comparison.csv`).
- `app.py` : Serveur HTTP autonome exposant l'API REST et le dashboard web.
- `dashboard.html` : Interface visuelle animée (topologie Canvas, particules de flux, jauges CPU, courbes temps réel, panneau What-If).
- `VERIFICATION.md` : Preuves formelles anti-hallucination.

## Lancement & Accès
### 1. Démarrer le serveur Web (Port 8090)
```bash
python3 /home/ubuntu/at20/app.py
```
Le serveur écoute sur `0.0.0.0:8090`.

### 2. Accéder à l'interface depuis votre PC hôte
Ouvrez un tunnel SSH vers la VM principale :
```powershell
ssh -i "6g-team-key.pem" -L 8090:127.0.0.1:8090 ubuntu@16.171.171.2
```
Puis accédez dans votre navigateur Web à :
**`http://localhost:8090`** (ou directement sur l'IP publique `http://16.171.171.2:8090` si le port est ouvert sur le Security Group AWS).

## Limites Connues
1. Les trajectoires spatiales de mobilité (`mobility.csv`) sont générées de manière synthétique et étiquetées comme telles, car les UEs UERANSIM s'exécutent sur une instance fixe sans déplacement physique GPS réel.
2. Le calcul MAPE de la latence lors du stress CPU UPF (S4) présente un écart important (215%) car le modèle prédit un effondrement sévère de la file d'attente ($W \approx 97$ ms) alors que la mesure réelle a plafonné à $30.9$ ms grâce à la régulation TCP de congestion.
