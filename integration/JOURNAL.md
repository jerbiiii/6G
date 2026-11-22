
## [2026-11-22 09:00] AT21 - Blockchain Sécurité 6G

- Constat : VM 6g accessible sur 51.20.191.212 (IP AWS renouvelée), RAM 4.8Gi libre, Python 3.12.3, Flask non installé, port 8021 libre, dossier at21 inexistant.
- Action : `pip3 install flask --break-system-packages` → Flask 3.1.3
- Action : Création /home/ubuntu/at21/{blockchain.py, at21_app.py, at21_collector.py, data/, captures/}
- Action : Lancement API Flask sur port 8021 (tmux at21-api)
- Action : 5 registrations UE, 2 décisions AMF/RIC, 2 métriques QoS → 10 blocs chainés, valides
- Action : Tamper test bloc #3 → fraude détectée : "Bloc 3: hash altéré (tamper détecté)"
- Action : Lancement collecteur 30s (tmux at21-collector) → 15 blocs au total
- Résultat : OK — blockchain opérationnelle, intégrité vérifiée, dashboard sur :8021/dashboard
- Fichier de preuve : /home/ubuntu/at21/captures/validate_output.txt
