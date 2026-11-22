
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

## [2026-11-22 09:24] AT23 - IA Generative LLM reseau 6G
- Constat : RAM 4.7GB libre, HuggingFace accessible, Ollama non installe, port 8023 libre
- Action : Installation Ollama + pull tinyllama + Flask 8023 (tmux at23)
- Resultat : OK - Ollama/TinyLlama actif sur 127.0.0.1:11434, Flask 0.0.0.0:8023
- Tests : analyze_urllc.json (ollama OK), generate_config.json (rule_based), chat_test.json (ollama OK)
- Fichier de preuve : /home/ubuntu/at23/captures/
## [2026-11-22 09:36] AT27 - Cybersécurité et Détection d'Intrusion 6G
- Constat : Cartographie 3GPP (N2 38412, N3 2152, N4 8805), TLS absent (commenté dans /etc/open5gs/), 5G-AKA actif
- Action : Audit crypto, tests auth rogue vs légitime, burst UDP 476k pps vers UPF N3, IDS léger, dashboard :8027
- Résultat : OK - Stabilité cœur 100%, rogue UE bloqué, HTTP 200 sur dashboard
- Fichier de preuve : /home/ubuntu/at27/captures/


## [2026-11-22 11:30] AT20 - Etape 5 : Dashboard Flask
- Constat : Flask 3.1.3 disponible, port 8090 libre, twin.py csv_path OK
- Action : Creation app.py (474 lignes) avec topologie animee, jauges CPU, courbes, what-if, tableau MAPE
- Resultat : OK - HTTP 200 sur /health, /dashboard, /api/metrics, /api/predict
- Fichier de preuve : at20/captures/dashboard_step5_200.txt

## [2026-11-22 11:30] AT20 - Etape 6 : VERIFICATION.md
- Constat : Toutes preuves collectees (ip -br a, grep hardcoded, timestamps CSV, source=real)
- Action : Creation VERIFICATION.md (168 lignes) audit anti-hallucination complet
- Resultat : OK - 10 sections documentees avec preuves

## [2026-11-22 11:30] AT20 - TERMINE
- Commit : 3bba068 - 26 fichiers, 2525 insertions
- Dashboard accessible : ssh -L 8090:localhost:8090 -i 6g-team-key.pem ubuntu@51.20.191.212
- MAPE moyen (hors S3) : 31.2% - S3 non valide (1 seul gNB)
