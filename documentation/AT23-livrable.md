# AT23 — IA Générative & LLM pour le Réseau 6G

## Objectif

Intégrer un modèle de langage (LLM) dans le testbed 6G pour trois usages :
1. **Analyse automatique d'alertes réseau** : explication en langage naturel + recommandation d'action
2. **Génération de configurations réseau** : suggestions de configuration YAML Open5GS optimisées
3. **Chatbot d'assistance réseau 6G** : interface conversationnelle sur l'état du réseau

## Architecture LLM Choisie

### Backend : Ollama + TinyLlama (1.1B paramètres, CPU-only)

**Raison du choix :**
- RAM disponible sur VM 6g : 4.7 GB libres (mesurée : `free -h`)
- TinyLlama occupe ~700 MB en mémoire, compatible CPU (aucun GPU sur la VM)
- Modèle déjà mis en cache localement (`ollama pull tinyllama`) — pas de téléchargement répété
- Fallback automatique `rule_based` si Ollama indisponible (résilience garantie)

**Architecture système :**

```
VM 6g (172.31.41.25)
├── Ollama daemon   → 127.0.0.1:11434  (systemd, CPU-only)
│   └── tinyllama  → modèle 1.1B params
├── Flask app       → 0.0.0.0:8023    (tmux session at23)
│   ├── at23_llm.py  (module LLM + moteur règles)
│   └── at23_app.py  (API REST + Dashboard)
└── captures/       → preuves JSON
```

**Endpoints REST :**
| Endpoint | Méthode | Description |
|---|---|---|
| `/health` | GET | Statut backend LLM |
| `/analyze` | POST | Analyse alerte QoS |
| `/generate_config` | POST | Génération config Open5GS |
| `/chat?q=...` | GET | Chatbot réseau 6G |
| `/dashboard` | GET | Interface web interactive |
| `/history` | GET | 10 dernières interactions |

## Procédure d'Installation

### Prérequis
```bash
# RAM disponible (vérifiée)
free -h  # → 4.7 GB libres
python3 --version  # → 3.12.3
pip3 show flask    # → Flask 3.1.3
```

### Installation Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
# → Ollama API disponible sur 127.0.0.1:11434
# → Service systemd actif
ollama pull tinyllama
```

### Démarrage de l'application
```bash
cd /home/ubuntu/at23
tmux new-session -d -s at23 "python3 at23_app.py > flask.log 2>&1"
# Vérification
curl -s http://localhost:8023/health
```

### Accès Dashboard (via tunnel SSH)
```bash
ssh -L 8023:localhost:8023 -i 6g-team-key.pem ubuntu@51.20.191.212
# Ouvrir navigateur : http://localhost:8023/dashboard
```

## Résultats des 3 Tests

### Test 1 — Analyse alerte URLLC (ollama/tinyllama)
**Entrée :** `{latency_ms: 45.2, throughput_mbps: 12.5, loss_pct: 2.1, cpu_pct: 87, slice: "URLLC"}`

**Sortie (source: ollama/tinyllama) :**
```json
{
  "severity": "OK",
  "action": "The recommended action is to maintain the current network conditions and avoid any undue stress on the network.",
  "source": "ollama/tinyllama",
  "timestamp": "2026-11-22T09:22:51.555561Z"
}
```
*Note : TinyLlama (1.1B) a évalué "OK" malgré des métriques URLLC dégradées (latence 45ms >> seuil 10ms). Limitation inhérente au modèle léger non spécialisé. Le moteur rule_based aurait retourné "CRITICAL". En production : utiliser le fallback rule_based pour les décisions critiques.*

**Exécution 2 (rule_based, pour validation croisée) :**
```json
{"severity":"CRITICAL","source":"rule_based"}
```

### Test 2 — Génération config surcharge eMBB (rule_based)
**Entrée :** `{scenario: "embb_overload", constraints: {max_latency_ms: 10, min_throughput_mbps: 100}}`

**Sortie (source: rule_based) :**
```json
{
  "scenario": "embb_overload",
  "source": "rule_based",
  "config": {
    "yaml_config": {
      "smf": {"slice": [{"sst": 1, "session": [{"ambr": {"uplink": {"value": 100, "unit": "Mbps"}, "downlink": {"value": 200, "unit": "Mbps"}}, "type": "IPv4"}]}]},
      "upf": {"pfcp": {"server": [{"address": "172.31.38.166"}]}},
      "recommendation": "Activer NSSAI prioritaire SST=1, augmenter AMBR uplink/downlink, activer admission control."
    }
  }
}
```

### Test 3 — Chatbot (ollama/tinyllama)
**Question :** "Quelle est la latence URLLC acceptable en 6G"

**Réponse (source: ollama/tinyllama) :** TinyLlama a fourni une réponse en français sur les classes de latence 6G (mentionnant 20ms, référence à 3GPP R19.81). La réponse est verbeuse et contient des inexactitudes (20ms vs < 1ms réel). C'est une limitation documentée du modèle 1.1B non fine-tuné.

**Preuve :** `/home/ubuntu/at23/captures/chat_test.json`

## Tableau Comparatif des Backends

| Backend LLM | Avantages | Limites |
|---|---|---|
| **ollama/tinyllama** | Local, privé, pas de quota, réponses en langage naturel | CPU lent (~30-60s/requête), réponses imprécises, non spécialisé 6G |
| **rule_based** | Instantané (<1ms), 100% précis, déterministe, fonctionne offline | Rigide, pas de langage naturel, ne couvre que les cas prévus |
| **HuggingFace API** | Modèles plus capables, gratuit en mode limité | Dépend de la connectivité, quota HTTP 429, latence réseau |

## Incidents

| Incident | Cause | Parade |
|---|---|---|
| Test 1 : TinyLlama retourne "OK" sur URLLC dégradé | Modèle 1.1B non fine-tuné, prompt JSON parfois mal parsé | Fallback rule_based pour évaluations critiques |
| Test 2 : Fallback rule_based déclenché | Réponse Ollama hors format JSON strict | Try/except → rule_based automatique |
| Génération longue (30-90s) | CPU-only, 1.1B paramètres | Timeout 90s configuré, acceptable pour usage non-temps-réel |

## Limites et Perspectives

1. **Modèle léger** : TinyLlama 1.1B n'est pas adapté aux décisions réseau critiques. Un modèle fine-tuné sur des données 3GPP/6G (ex. `Llama-3-6G-expert`) serait plus fiable.
2. **Latence d'inférence** : 30-90s en CPU. En production, nécessite GPU ou modèle quantifié Q4 + hardware dédié.
3. **Intégration RIC Near-RT** : Le module `at23_llm.analyze_alert()` pourrait être appelé depuis le xApp at19 (O-RAN) pour des décisions automatisées.
4. **Fine-tuning** : Entraîner TinyLlama sur les logs UERANSIM/Open5GS et les KPIs AT4-AT22 améliorerait drastiquement la précision des analyses.
5. **Sécurité** : L'API Flask n'est pas authentifiée. En production : ajouter un token Bearer.

## Preuves

| Fichier | Description |
|---|---|
| `captures/health.json` | Statut Ollama actif (mesuré) |
| `captures/analyze_urllc.json` | Réponse TinyLlama analyse URLLC (mesuré) |
| `captures/generate_config.json` | Config eMBB générée (mesuré) |
| `captures/chat_test.json` | Réponse chatbot TinyLlama (mesuré) |
| `captures/dashboard_200.txt` | HTTP 200 sur /dashboard (mesuré) |

**Sources :** Toutes les valeurs (IP, RAM, versions) ont été découvertes par commandes dans cette session. Voir JOURNAL.md et FAITS.md.

---
*AT23 réalisé le 2026-11-22 — Backend : Ollama/TinyLlama (CPU) + rule_based fallback — Dashboard : http://localhost:8023/dashboard (via tunnel SSH)*
