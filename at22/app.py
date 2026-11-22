#!/usr/bin/env python3
"""AT22 Quantum ML Dashboard - Flask port 8022"""
import sys, os, csv, json, datetime
sys.path.insert(0, '/home/ubuntu/at22')
from flask import Flask, jsonify, redirect, make_response, request
from problem import SLICES, LEVELS, B_TOTAL, UTILITY, SLA_MIN, evaluate_solution
from classical_solver import greedy_solve, brute_force_solve
from qaoa_simulator import qaoa_solve

COMPARISON_CSV = '/home/ubuntu/at22/data/comparison.csv'
app = Flask(__name__)

def _load_csv(path):
    try:
        with open(path, newline='') as f:
            return list(csv.DictReader(f))
    except: return []

@app.route('/')
def index(): return redirect('/dashboard')

@app.route('/health')
def health(): return jsonify({"status":"ok","timestamp":datetime.datetime.utcnow().isoformat()+"Z"})

@app.route('/api/comparison')
def api_comparison(): return jsonify(_load_csv(COMPARISON_CSV))

@app.route('/api/run_all')
def api_run_all():
    g = greedy_solve()
    b = brute_force_solve()
    q = qaoa_solve(n_restarts=3)
    return jsonify({"greedy":g,"brute_force":b,"qaoa":q,
                    "timestamp":datetime.datetime.utcnow().isoformat()+"Z"})

@app.route('/api/problem_info')
def api_problem_info():
    return jsonify({"slices":SLICES,"levels":LEVELS,"budget":B_TOTAL,
                    "sla_min":SLA_MIN,"utility":UTILITY,
                    "n_qubits":len(SLICES)*len(LEVELS),
                    "hilbert_dim":2**(len(SLICES)*len(LEVELS))})

HTML = r"""<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AT22 — Quantum ML 6G</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d1117;color:#c9d1d9;font-family:'Courier New',monospace}
header{background:#161b22;padding:12px 20px;border-bottom:1px solid #30363d;display:flex;justify-content:space-between;align-items:center}
header h1{font-size:1.1rem;color:#a371f7;letter-spacing:2px}
main{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:14px;max-width:1400px;margin:0 auto}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:14px}
.card h2{font-size:.85rem;color:#8b949e;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;border-bottom:1px solid #21262d;padding-bottom:6px}
.full{grid-column:1/-1}
.badge{display:inline-block;padding:1px 7px;border-radius:4px;font-size:.65rem;font-weight:bold;vertical-align:middle}
.bq{background:#a371f733;color:#a371f7;border:1px solid #a371f7}
.bc{background:#3fb95033;color:#3fb950;border:1px solid #3fb950}
.bg{background:#d2992233;color:#d29922;border:1px solid #d29922}
.br{background:#f8514933;color:#f85149;border:1px solid #f85149}
table{width:100%;border-collapse:collapse;font-size:.8rem}
th{background:#21262d;color:#8b949e;text-align:left;padding:7px 10px;font-weight:normal}
td{padding:6px 10px;border-bottom:1px solid #21262d}
tr:hover td{background:#21262d55}
.bar-wrap{background:#21262d;border-radius:4px;height:18px;position:relative;overflow:hidden}
.bar{height:100%;border-radius:4px;transition:width .6s ease;display:flex;align-items:center;justify-content:flex-end;padding-right:4px;font-size:.7rem;color:#fff;font-weight:bold}
.btn{background:#21262d;border:1px solid #30363d;color:#c9d1d9;padding:7px 16px;border-radius:6px;cursor:pointer;font-size:.82rem;transition:all .2s}
.btn:hover{background:#a371f733;border-color:#a371f7;color:#a371f7}
.btn:disabled{opacity:.4;cursor:not-allowed}
#result-panel{background:#0d1117;border:1px solid #21262d;border-radius:6px;padding:12px;min-height:80px;font-size:.82rem;white-space:pre-wrap}
.metric-box{background:#0d1117;border:1px solid #21262d;border-radius:6px;padding:10px;text-align:center;flex:1}
.metric-val{font-size:1.6rem;font-weight:bold;color:#a371f7}
.metric-lbl{font-size:.7rem;color:#8b949e;margin-top:3px}
.metrics-row{display:flex;gap:10px;margin-bottom:12px;flex-wrap:wrap}
.qubit-grid{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}
.qubit{width:28px;height:28px;border-radius:50%;border:2px solid #30363d;display:flex;align-items:center;justify-content:center;font-size:.65rem;transition:all .4s}
.qubit.zero{background:#21262d;color:#8b949e;border-color:#30363d}
.qubit.one{background:#a371f733;color:#a371f7;border-color:#a371f7;box-shadow:0 0 8px #a371f755}
.qubit.super{background:#1f6feb33;border-color:#58a6ff;animation:pulse 1s infinite}
@keyframes pulse{0%,100%{box-shadow:0 0 4px #58a6ff55}50%{box-shadow:0 0 14px #58a6ffaa}}
</style></head>
<body>
<header>
  <h1>⚛ AT22 — Quantum Machine Learning 6G</h1>
  <div style="font-size:.75rem;color:#8b949e">9 qubits · dim Hilbert 512 · QAOA p=1 · NumPy pur</div>
</header>
<main>
  <!-- Info problème -->
  <div class="card">
    <h2>Problème QUBO <span class="badge bq">Quantique</span></h2>
    <p style="font-size:.8rem;color:#8b949e;margin-bottom:10px">
      Allocation de bande passante entre 3 slices 6G sous contraintes SLA.<br>
      Variables binaires x[slice][niveau] → matrice QUBO 9×9.
    </p>
    <table>
      <thead><tr><th>Slice</th><th>Niveaux</th><th>SLA Min</th><th>Utilité</th></tr></thead>
      <tbody>
        <tr><td>eMBB</td><td>20/30/50 Mbps</td><td>30 Mbps</td><td>0.3 / 0.6 / 1.0</td></tr>
        <tr><td>URLLC</td><td>20/30/50 Mbps</td><td>20 Mbps</td><td>0.8 / 1.0 / 1.0</td></tr>
        <tr><td>mMTC</td><td>20/30/50 Mbps</td><td>20 Mbps</td><td>1.0 / 1.0 / 1.0</td></tr>
      </tbody>
    </table>
    <div style="margin-top:10px;font-size:.75rem;color:#8b949e">Budget total : <strong style="color:#c9d1d9">100 Mbps</strong> · Solutions faisables : 27 · Espace Hilbert : 2⁹ = 512 états</div>
  </div>

  <!-- Qubits visualisation -->
  <div class="card">
    <h2>Registre Quantique <span class="badge bq">9 qubits</span></h2>
    <p style="font-size:.75rem;color:#8b949e;margin-bottom:6px">
      eMBB [q0 q1 q2] · URLLC [q3 q4 q5] · mMTC [q6 q7 q8]
    </p>
    <div class="qubit-grid" id="qubit-grid">
      <!-- rempli par JS -->
    </div>
    <div style="margin-top:10px;font-size:.72rem;color:#8b949e">
      <span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:#21262d;border:2px solid #30363d;vertical-align:middle;margin-right:4px"></span>|0⟩ &nbsp;
      <span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:#a371f733;border:2px solid #a371f7;vertical-align:middle;margin-right:4px"></span>|1⟩ &nbsp;
      <span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:#1f6feb33;border:2px solid #58a6ff;vertical-align:middle;margin-right:4px"></span>Superposition
    </div>
    <div style="margin-top:8px;font-size:.75rem;color:#8b949e" id="qubit-state-label">En attente d'une expérience...</div>
  </div>

  <!-- Lancer une expérience -->
  <div class="card full">
    <h2>Expérience : Optimisation Quantique vs Classique</h2>
    <div style="display:flex;gap:10px;margin-bottom:12px;flex-wrap:wrap">
      <button class="btn" id="btn-run" onclick="runExperiment()">▶ Lancer l'optimisation (3 solveurs)</button>
      <span style="font-size:.75rem;color:#8b949e;align-self:center">Exécution sur VM réelle · ~500ms pour QAOA</span>
    </div>
    <div id="result-panel">Cliquez sur ▶ pour lancer l'optimisation quantique simulée.</div>
  </div>

  <!-- Résultats comparatifs -->
  <div class="card">
    <h2>Utilité QoS <span class="badge bc">Résultats</span></h2>
    <div class="metrics-row" id="util-row">
      <div class="metric-box"><div class="metric-val" id="v-greedy">—</div><div class="metric-lbl">Glouton <span class="badge bg">Classique</span></div></div>
      <div class="metric-box"><div class="metric-val" id="v-brute">—</div><div class="metric-lbl">Brute Force Optimal <span class="badge bc">Classique</span></div></div>
      <div class="metric-box"><div class="metric-val" id="v-qaoa">—</div><div class="metric-lbl">QAOA Simulé <span class="badge bq">Quantique</span></div></div>
    </div>
    <div>
      <div style="font-size:.75rem;color:#8b949e;margin-bottom:4px">Utilité relative (max = 3.0)</div>
      <div style="margin-bottom:6px"><span style="font-size:.72rem;color:#d29922">Glouton</span>
        <div class="bar-wrap"><div class="bar" id="bar-greedy" style="width:0%;background:#d29922"></div></div></div>
      <div style="margin-bottom:6px"><span style="font-size:.72rem;color:#3fb950">Brute Force</span>
        <div class="bar-wrap"><div class="bar" id="bar-brute" style="width:0%;background:#3fb950"></div></div></div>
      <div><span style="font-size:.72rem;color:#a371f7">QAOA</span>
        <div class="bar-wrap"><div class="bar" id="bar-qaoa" style="width:0%;background:#a371f7"></div></div></div>
    </div>
  </div>

  <!-- Allocation -->
  <div class="card">
    <h2>Allocation Optimale QAOA <span class="badge bq">Quantique</span></h2>
    <table id="alloc-table">
      <thead><tr><th>Slice</th><th>Bande passante</th><th>Utilité</th><th>SLA</th></tr></thead>
      <tbody id="alloc-body"><tr><td colspan="4" style="color:#8b949e;text-align:center">En attente...</td></tr></tbody>
    </table>
    <div style="margin-top:10px;font-size:.75rem;color:#8b949e" id="qaoa-params">—</div>
  </div>

  <!-- Tableau historique -->
  <div class="card full">
    <h2>Historique des expériences <span class="badge bc">3 runs précédents</span></h2>
    <table>
      <thead><tr><th>Run</th><th>Glouton Util.</th><th>Optimal Util.</th><th>QAOA Util.</th><th>QAOA = Opt ?</th><th>Gap Glouton/Opt</th><th>Temps QAOA (ms)</th></tr></thead>
      <tbody id="hist-body"><tr><td colspan="7" style="color:#8b949e;text-align:center">Chargement...</td></tr></tbody>
    </table>
  </div>
</main>

<script>
let lastResult = null;

function initQubits(state) {
  const grid = document.getElementById('qubit-grid');
  grid.innerHTML = '';
  const labels = ['q0','q1','q2','q3','q4','q5','q6','q7','q8'];
  const sliceColors = ['#a371f7','#a371f7','#a371f7','#3fb950','#3fb950','#3fb950','#58a6ff','#58a6ff','#58a6ff'];
  for(let i=0;i<9;i++){
    const q = document.createElement('div');
    q.className = 'qubit';
    q.id = 'q'+i;
    q.textContent = labels[i];
    if(state === 'super') {
      q.classList.add('super');
      q.style.borderColor = sliceColors[i];
    } else if(state && state[i] === 1) {
      q.classList.add('one');
      q.style.background = sliceColors[i]+'33';
      q.style.borderColor = sliceColors[i];
      q.style.boxShadow = `0 0 8px ${sliceColors[i]}55`;
    } else {
      q.classList.add('zero');
    }
    grid.appendChild(q);
  }
}

async function runExperiment() {
  const btn = document.getElementById('btn-run');
  const panel = document.getElementById('result-panel');
  btn.disabled = true;
  btn.textContent = '⟳ Optimisation en cours...';
  panel.textContent = '⟳ Initialisation du circuit quantique (9 qubits, 512 états)...\n';
  initQubits('super');
  document.getElementById('qubit-state-label').textContent = 'Superposition uniforme |+⟩⁹ — QAOA p=1 en cours...';
  
  try {
    const r = await fetch('/api/run_all');
    const d = await r.json();
    lastResult = d;
    
    // Afficher qubits solution QAOA
    const alloc = d.qaoa.allocation;
    const sliceNames = ['eMBB','URLLC','mMTC'];
    const levels = [20,30,50];
    const bits = new Array(9).fill(0);
    sliceNames.forEach((s,i)=>{
      const bw = alloc[s].bw_mbps;
      const k = levels.indexOf(bw);
      if(k>=0) bits[i*3+k] = 1;
    });
    initQubits(bits);
    document.getElementById('qubit-state-label').textContent =
      `Solution mesurée : γ=${d.qaoa.gamma_opt} β=${d.qaoa.beta_opt} · énergie=${d.qaoa.qaoa_energy}`;

    // Métriques utilité
    const maxU = 3.0;
    document.getElementById('v-greedy').textContent = d.greedy.utility_total.toFixed(2);
    document.getElementById('v-brute').textContent  = d.brute_force.utility_total.toFixed(2);
    document.getElementById('v-qaoa').textContent   = d.qaoa.utility_total.toFixed(2);
    document.getElementById('bar-greedy').style.width = (d.greedy.utility_total/maxU*100)+'%';
    document.getElementById('bar-greedy').textContent = d.greedy.utility_total.toFixed(2);
    document.getElementById('bar-brute').style.width  = (d.brute_force.utility_total/maxU*100)+'%';
    document.getElementById('bar-brute').textContent  = d.brute_force.utility_total.toFixed(2);
    document.getElementById('bar-qaoa').style.width   = (d.qaoa.utility_total/maxU*100)+'%';
    document.getElementById('bar-qaoa').textContent   = d.qaoa.utility_total.toFixed(2);

    // Allocation QAOA
    const ab = document.getElementById('alloc-body');
    ab.innerHTML = sliceNames.map(s=>{
      const a = d.qaoa.allocation[s];
      const sla = {eMBB:30,URLLC:20,mMTC:20};
      const ok = a.bw_mbps >= sla[s];
      return `<tr>
        <td><strong>${s}</strong></td>
        <td>${a.bw_mbps} Mbps</td>
        <td>${a.utility.toFixed(3)}</td>
        <td>${ok?'<span class="badge bc">✓ OK</span>':'<span class="badge br">✗ VIOLATION</span>'}</td>
      </tr>`;
    }).join('');
    document.getElementById('qaoa-params').textContent =
      `γ_opt=${d.qaoa.gamma_opt} · β_opt=${d.qaoa.beta_opt} · énergie QUBO=${d.qaoa.qaoa_energy} · temps=${d.qaoa.time_ms}ms`;

    // Panel résultat
    const isOpt = d.qaoa.utility_total >= d.brute_force.utility_total;
    panel.textContent = `✅ Optimisation terminée — ${new Date().toLocaleTimeString()}\n\n`+
      `QAOA (quantique simulé) :\n`+
      `  Utilité = ${d.qaoa.utility_total} / 3.0 ${isOpt?'✅ OPTIMAL':'⚠'}\n`+
      `  BW utilisée = ${d.qaoa.bandwidth_used} Mbps / 100 Mbps\n`+
      `  Violations SLA = ${d.qaoa.sla_violations.length}\n`+
      `  Temps = ${d.qaoa.time_ms} ms\n\n`+
      `Brute Force (classique optimal) :\n`+
      `  Utilité = ${d.brute_force.utility_total} · BW = ${d.brute_force.bandwidth_used} Mbps · t=${d.brute_force.time_ms}ms\n\n`+
      `Glouton (classique heuristique) :\n`+
      `  Utilité = ${d.greedy.utility_total} · BW = ${d.greedy.bandwidth_used} Mbps · t=${d.greedy.time_ms}ms\n\n`+
      `Gap Glouton/Optimal = ${((d.brute_force.utility_total-d.greedy.utility_total)/d.brute_force.utility_total*100).toFixed(2)}%\n`+
      `Gap QAOA/Optimal    = ${((d.brute_force.utility_total-d.qaoa.utility_total)/d.brute_force.utility_total*100).toFixed(2)}%`;

    loadHistory();
  } catch(e) {
    panel.textContent = '❌ Erreur : ' + e;
  }
  btn.disabled = false;
  btn.textContent = '▶ Lancer l\'optimisation (3 solveurs)';
}

async function loadHistory() {
  try {
    const r = await fetch('/api/comparison');
    const rows = await r.json();
    const tb = document.getElementById('hist-body');
    if(!rows.length){tb.innerHTML='<tr><td colspan="7" style="color:#8b949e;text-align:center">Aucune donnée</td></tr>';return;}
    tb.innerHTML = rows.map(r=>
      `<tr>
        <td>${r.run}</td>
        <td>${r.greedy_utility}</td>
        <td>${r.brute_utility}</td>
        <td style="color:#a371f7"><strong>${r.qaoa_utility}</strong></td>
        <td>${r.qaoa_matches_optimal==='True'?'<span class="badge bq">✓ OUI</span>':'<span class="badge br">✗ NON</span>'}</td>
        <td class="${parseFloat(r.gap_greedy_pct)>5?'':''}"">${r.gap_greedy_pct}%</td>
        <td>${r.qaoa_time_ms} ms</td>
      </tr>`).join('');
  } catch(e) {}
}

// Init
initQubits(null);
loadHistory();
</script>
</body></html>"""

@app.route('/dashboard')
def dashboard(): return HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8022, debug=False)
