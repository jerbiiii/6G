#!/usr/bin/env python3
"""
AT21 - API REST Flask pour la blockchain 6G
Port 8021
"""
import sys
import json
import copy
from datetime import datetime, timezone
from flask import Flask, request, jsonify, Response

sys.path.insert(0, '/home/ubuntu/at21')
from blockchain import Blockchain

app = Flask(__name__)
bc = Blockchain()

# ─── Dashboard HTML ────────────────────────────────────────────────────────────
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="5">
<title>AT21 - Blockchain 6G Dashboard</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Courier New',monospace;background:#0a0e1a;color:#00ff88;min-height:100vh;padding:20px}
h1{font-size:1.6rem;text-align:center;color:#00ffcc;text-shadow:0 0 10px #00ffcc;margin-bottom:8px}
.subtitle{text-align:center;color:#4488aa;font-size:.9rem;margin-bottom:20px}
.stats{display:flex;gap:16px;justify-content:center;margin-bottom:24px;flex-wrap:wrap}
.stat-card{background:#0d1a2a;border:1px solid #00ff88;border-radius:8px;padding:16px 24px;text-align:center;min-width:140px}
.stat-card .val{font-size:2rem;color:#00ffcc;font-weight:bold}
.stat-card .lbl{font-size:.75rem;color:#4488aa;margin-top:4px}
.valid-badge{display:inline-block;padding:4px 14px;border-radius:12px;font-weight:bold;font-size:.85rem}
.valid-badge.ok{background:#00ff8822;border:1px solid #00ff88;color:#00ff88}
.valid-badge.ko{background:#ff003322;border:1px solid #ff4444;color:#ff4444}
table{width:100%;border-collapse:collapse;margin-bottom:24px;font-size:.8rem}
th{background:#0d1a2a;color:#00ffcc;padding:8px;border:1px solid #1a3a5a;text-align:left}
td{padding:7px 8px;border:1px solid #1a2a3a;vertical-align:top;word-break:break-all}
tr:nth-child(even){background:#0a141e}
.type-badge{padding:2px 8px;border-radius:10px;font-size:.75rem;font-weight:bold}
.type-UE_AUTH{background:#003355;color:#00aaff;border:1px solid #0055aa}
.type-AMF_DECISION{background:#220033;color:#cc88ff;border:1px solid #550088}
.type-QOS_METRIC{background:#002200;color:#00cc44;border:1px solid #005500}
.type-GENESIS{background:#1a1a00;color:#aaaa00;border:1px solid #555500}
.type-COLLECTOR{background:#1a0000;color:#ff8844;border:1px solid #662200}
.hash{font-size:.7rem;color:#336688;font-family:monospace}
.section-title{color:#00ffcc;font-size:1.1rem;border-bottom:1px solid #1a3a5a;padding-bottom:6px;margin:20px 0 12px}
.chain-vis{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px;align-items:center}
.chain-block{background:#0d1a2a;border:1px solid #00ff88;border-radius:6px;padding:10px;min-width:130px;max-width:160px;font-size:.7rem}
.chain-block .bidx{color:#00ffcc;font-size:.85rem;font-weight:bold}
.chain-arrow{color:#00ff88;font-size:1.4rem;align-self:center}
footer{text-align:center;color:#335566;font-size:.75rem;margin-top:30px;padding-top:10px;border-top:1px solid #1a3a5a}
</style>
</head>
<body>
<h1>🔗 AT21 — Blockchain Sécurité Réseau 6G</h1>
<div class="subtitle">Auto-refresh 5s | __TS__</div>

<div class="stats">
  <div class="stat-card"><div class="val">__NB_BLOCKS__</div><div class="lbl">Blocs dans la chain</div></div>
  <div class="stat-card"><div class="val">__NB_UE__</div><div class="lbl">Auth UE enregistrées</div></div>
  <div class="stat-card"><div class="val">__NB_DEC__</div><div class="lbl">Décisions AMF/RIC</div></div>
  <div class="stat-card"><div class="val">__NB_QOS__</div><div class="lbl">Métriques QoS</div></div>
  <div class="stat-card"><div class="val valid-badge __VALID_CLS__">__VALID_TXT__</div><div class="lbl">Intégrité chain</div></div>
</div>

<div class="section-title">🧱 Visualisation de la Blockchain</div>
<div class="chain-vis">__CHAIN_VIS__</div>

<div class="section-title">📋 Derniers événements (20 derniers blocs)</div>
<table>
<tr><th>#</th><th>Type</th><th>Timestamp</th><th>Données</th><th>Hash</th></tr>
__ROWS__
</table>

<footer>AT21 Blockchain 6G — SHA-256 + HMAC-SHA256 — Python __PYVER__</footer>
</body>
</html>"""

def _render_dashboard():
    import sys as _sys
    chain = bc.get_chain()
    validation = bc.validate_chain()

    nb_ue = sum(1 for b in chain if b["data"].get("type") == "UE_AUTH")
    nb_dec = sum(1 for b in chain if b["data"].get("type") == "AMF_DECISION")
    nb_qos = sum(1 for b in chain if b["data"].get("type") == "QOS_METRIC")

    valid_cls = "ok" if validation["valid"] else "ko"
    valid_txt = "✓ VALIDE" if validation["valid"] else "✗ CORROMPU"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Chain visualization (last 10)
    vis_blocks = chain[-10:]
    vis_parts = []
    for i, b in enumerate(vis_blocks):
        btype = b["data"].get("type", "?")
        vis_parts.append(
            f'<div class="chain-block">'
            f'<div class="bidx">#{b["index"]}</div>'
            f'<div class="type-badge type-{btype}">{btype}</div>'
            f'<div class="hash" style="margin-top:4px">{b["hash"][:16]}…</div>'
            f'</div>'
        )
        if i < len(vis_blocks) - 1:
            vis_parts.append('<div class="chain-arrow">→</div>')
    chain_vis = "".join(vis_parts)

    # Table rows (last 20)
    rows_html = ""
    for b in reversed(chain[-20:]):
        btype = b["data"].get("type", "?")
        data_disp = {k: v for k, v in b["data"].items() if k != "type"}
        rows_html += (
            f'<tr>'
            f'<td>{b["index"]}</td>'
            f'<td><span class="type-badge type-{btype}">{btype}</span></td>'
            f'<td>{b["timestamp"][:19].replace("T"," ")}</td>'
            f'<td style="font-size:.7rem">{json.dumps(data_disp, ensure_ascii=False)[:200]}</td>'
            f'<td class="hash">{b["hash"][:24]}…</td>'
            f'</tr>'
        )

    html = DASHBOARD_HTML
    subs = {
        "__TS__": ts,
        "__NB_BLOCKS__": str(len(chain)),
        "__NB_UE__": str(nb_ue),
        "__NB_DEC__": str(nb_dec),
        "__NB_QOS__": str(nb_qos),
        "__VALID_CLS__": valid_cls,
        "__VALID_TXT__": valid_txt,
        "__CHAIN_VIS__": chain_vis,
        "__ROWS__": rows_html,
        "__PYVER__": _sys.version.split()[0]
    }
    for k, v in subs.items():
        html = html.replace(k, v)
    return html

# ─── Endpoints ─────────────────────────────────────────────────────────────────
@app.route("/register_ue", methods=["POST"])
def register_ue():
    req = request.get_json(force=True, silent=True) or {}
    block = bc.add_block({
        "type": "UE_AUTH",
        "imsi": req.get("imsi", "unknown"),
        "event": req.get("event", "registration_request"),
        "source_ip": request.remote_addr,
        "extra": req.get("extra", {})
    })
    return jsonify({"status": "ok", "block_index": block.index, "hash": block.hash}), 201

@app.route("/log_decision", methods=["POST"])
def log_decision():
    req = request.get_json(force=True, silent=True) or {}
    block = bc.add_block({
        "type": "AMF_DECISION",
        "component": req.get("component", "AMF"),
        "decision": req.get("decision", "unknown"),
        "target": req.get("target", ""),
        "reason": req.get("reason", "")
    })
    return jsonify({"status": "ok", "block_index": block.index, "hash": block.hash}), 201

@app.route("/log_metric", methods=["POST"])
def log_metric():
    req = request.get_json(force=True, silent=True) or {}
    block = bc.add_block({
        "type": "QOS_METRIC",
        "metric_name": req.get("metric_name", "unknown"),
        "value": req.get("value"),
        "unit": req.get("unit", ""),
        "source": req.get("source", "collector"),
        "node": req.get("node", "")
    })
    return jsonify({"status": "ok", "block_index": block.index, "hash": block.hash}), 201

@app.route("/chain", methods=["GET"])
def get_chain():
    return jsonify(bc.get_chain())

@app.route("/validate", methods=["GET"])
def validate():
    return jsonify(bc.validate_chain())

@app.route("/dashboard", methods=["GET"])
def dashboard():
    return Response(_render_dashboard(), mimetype="text/html")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "blocks": len(bc.chain)})

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "AT21 6G Blockchain API",
        "endpoints": ["/register_ue", "/log_decision", "/log_metric", "/chain", "/validate", "/dashboard"]
    })

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    print("[AT21] Blockchain API démarrée sur port 8021")
    app.run(host="0.0.0.0", port=8021, debug=False)
