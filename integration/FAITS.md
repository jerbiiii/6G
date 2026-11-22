
## AT21 — Blockchain Sécurité 6G (2026-11-22)

| Fait | Valeur | Commande source | Date |
|------|--------|-----------------|------|
| IP publique 6g (renouvelée) | 51.20.191.212 | ip.txt (mis à jour) | 2026-11-22 |
| IP privée 6g | 172.31.41.25 | ip -br a | 2026-11-22 |
| Interface principale 6g | enp39s0 | ip -br a | 2026-11-22 |
| RAM libre 6g | 4.8 Gi | free -h | 2026-11-22 |
| Python version | 3.12.3 | python3 --version | 2026-11-22 |
| Flask version | 3.1.3 | pip3 install flask | 2026-11-22 |
| Port AT21 API | 8021 | ss -tlnp | 2026-11-22 |
| Chemin blockchain | /home/ubuntu/at21/data/blockchain.json | ls | 2026-11-22 |
| CPU vm-cp | 147m (7%) | kubectl top nodes | 2026-11-22 |
| CPU vm-ran | 119m (5%) | kubectl top nodes | 2026-11-22 |
| CPU vm-upf | 47m (2%) | kubectl top nodes | 2026-11-22 |
| RAM vm-cp | 1719Mi (22%) | kubectl top nodes | 2026-11-22 |

## AT23 - 2026-11-22
- RAM libre VM 6g : 4.7 GB (commande: free -h)
- Ollama installe : /usr/local/bin/ollama (commande: which ollama)
- Ollama port : 127.0.0.1:11434 (commande: curl /api/tags)
- Modele : tinyllama (commande: ollama pull tinyllama)
- Flask AT23 : 0.0.0.0:8023 (tmux session at23)
- Flask version : 3.1.3 (commande: python3 -c "import flask; print(flask.__version__)")
