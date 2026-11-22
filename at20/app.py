#!/usr/bin/env python3
"""AT20 Digital Twin Dashboard - Flask app port 8090"""
import sys, os, csv, json, io, datetime
sys.path.insert(0, '/home/ubuntu/at20')
from flask import Flask, jsonify, request, redirect, send_file, make_response
from twin import DigitalTwin

METRICS_CSV   = '/home/ubuntu/at20/data/metrics.csv'
COMPARISON_CSV= '/home/ubuntu/at20/data/comparison.csv'

app = Flask(__name__)

def _load_csv(path, maxrows=None):
    rows = []
    try:
        with open(path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    except Exception:
        pass
    if maxrows:
        rows = rows[-maxrows:]
    return rows

try:
    twin = DigitalTwin(csv_path=METRICS_CSV)
    twin.calibrate()
except Exception as e:
    twin = None
    print(f"[WARN] DigitalTwin init failed: {e}")

@app.route('/')
def index():
    return redirect('/dashboard')

@app.route('/health')
def health():
    return jsonify({"status":"ok","timestamp":datetime.datetime.utcnow().isoformat()+"Z"})

@app.route('/api/metrics')
def api_metrics():
    rows = _load_csv(METRICS_CSV, maxrows=30)
    return jsonify(rows)

@app.route('/api/comparison')
def api_comparison():
    rows = _load_csv(COMPARISON_CSV)
    return jsonify(rows)

@app.route('/api/predict')
def api_predict():
    try:
        ue  = float(request.args.get('ue_count',0))
        mbps= float(request.args.get('traffic_mbps',0))
        cpu = float(request.args.get('cpu_upf_pct',2))
        if twin:
            res = twin.predict(ue_count=ue, traffic_mbps=mbps, cpu_upf_pct=cpu)
        else:
            res = {"error":"twin not available"}
        res["source"] = "PREDICTED"
        res["inputs"] = {"ue_count":ue,"traffic_mbps":mbps,"cpu_upf_pct":cpu}
        return jsonify(res)
    except Exception as e:
        return jsonify({"error":str(e)}), 400

@app.route('/api/export/csv')
def export_csv():
    rows = _load_csv(METRICS_CSV)
    if not rows:
        return "No data", 404
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)
    buf.seek(0)
    return make_response(buf.getvalue(), 200, {
        'Content-Type':'text/csv',
        'Content-Disposition':'attachment; filename=at20_metrics.csv'
    })

@app.route('/api/export/json')
def export_json():
    data = {
        "metrics": _load_csv(METRICS_CSV),
        "comparison": _load_csv(COMPARISON_CSV),
        "exported_at": datetime.datetime.utcnow().isoformat()+"Z"
    }
    buf = json.dumps(data, indent=2)
    return make_response(buf, 200, {
        'Content-Type':'application/json',
        'Content-Disposition':'attachment; filename=at20_export.json'
    })

HTML = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AT20 — Digital Twin 6G Dashboard</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d1117;color:#c9d1d9;font-family:'Courier New',monospace;min-height:100vh}
header{background:#161b22;padding:12px 20px;border-bottom:1px solid #30363d;display:flex;justify-content:space-between;align-items:center}
header h1{font-size:1.1rem;color:#58a6ff;letter-spacing:2px}
.sync-badge{background:#1f6feb22;border:1px solid #1f6feb;padding:4px 10px;border-radius:12px;font-size:.75rem;color:#58a6ff}
.sync-badge.ok{border-color:#3fb950;color:#3fb950;background:#3fb95022}
main{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:auto auto auto;gap:12px;padding:14px;max-width:1600px;margin:0 auto}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:14px}
.card h2{font-size:.85rem;color:#8b949e;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;border-bottom:1px solid #21262d;padding-bottom:6px}
.full-width{grid-column:1/-1}
canvas{display:block;width:100%}
/* badges */
.badge{display:inline-block;padding:1px 6px;border-radius:4px;font-size:.65rem;font-weight:bold;vertical-align:middle;margin-left:4px}
.badge-real{background:#3fb95033;color:#3fb950;border:1px solid #3fb950}
.badge-pred{background:#1f6feb33;color:#58a6ff;border:1px solid #58a6ff}
.badge-gen{background:#d2992233;color:#d29922;border:1px solid #d29922}
/* gauges */
.gauges{display:flex;gap:16px;justify-content:space-around;flex-wrap:wrap}
.gauge-wrap{text-align:center}
.gauge-label{font-size:.75rem;color:#8b949e;margin-top:4px}
.gauge-val{font-size:1.1rem;font-weight:bold;color:#58a6ff}
/* what-if */
.wi-controls{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:12px}
.wi-ctrl{flex:1;min-width:140px}
.wi-ctrl label{font-size:.75rem;color:#8b949e;display:block;margin-bottom:4px}
.wi-ctrl input[type=range]{width:100%;accent-color:#58a6ff}
.wi-ctrl span{font-size:.8rem;color:#c9d1d9}
.wi-buttons{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}
.wi-btn{background:#21262d;border:1px solid #30363d;color:#c9d1d9;padding:5px 12px;border-radius:6px;cursor:pointer;font-size:.8rem;transition:background .2s}
.wi-btn:hover{background:#1f6feb33;border-color:#58a6ff;color:#58a6ff}
.wi-result{background:#0d1117;border:1px solid #21262d;border-radius:6px;padding:10px;min-height:60px;font-size:.85rem}
.wi-arrow{font-size:1.4rem;margin:0 8px;vertical-align:middle}
.arrow-up{color:#f85149}
.arrow-down{color:#3fb950}
/* comparison table */
table{width:100%;border-collapse:collapse;font-size:.78rem}
th{background:#21262d;color:#8b949e;text-align:left;padding:6px 8px;font-weight:normal}
td{padding:5px 8px;border-bottom:1px solid #21262d}
tr:hover td{background:#21262d55}
.mape-ok{color:#3fb950}.mape-warn{color:#d29922}.mape-bad{color:#f85149}
/* topology */
#topo-canvas{background:#0d1117;border-radius:6px}
/* timeline */
#metric-canvas{background:#0d1117;border-radius:6px}
/* export */
.export-btns{display:flex;gap:8px;margin-top:8px}
.export-btn{background:#21262d;border:1px solid #30363d;color:#c9d1d9;padding:4px 12px;border-radius:6px;cursor:pointer;font-size:.78rem;text-decoration:none;display:inline-block}
.export-btn:hover{background:#3fb95022;border-color:#3fb950;color:#3fb950}
</style>
</head>
<body>
<header>
  <h1>⬡ AT20 — Digital Twin 6G</h1>
  <div style="display:flex;align-items:center;gap:12px">
    <div class="export-btns">
      <a class="export-btn" href="/api/export/csv">⬇ CSV</a>
      <a class="export-btn" href="/api/export/json">⬇ JSON</a>
    </div>
    <div class="sync-badge" id="sync-badge">⟳ SYNCHRONIZING...</div>
  </div>
</header>
<main>
  <!-- Topologie + Métriques temps réel -->
  <div class="card">
    <h2>Topologie Réseau Physique <span class="badge badge-real">Réel</span></h2>
    <canvas id="topo-canvas" width="560" height="280"></canvas>
  </div>
  <div class="card">
    <h2>Métriques Temps Réel <span class="badge badge-real">Réel</span></h2>
    <canvas id="metric-canvas" width="560" height="280"></canvas>
  </div>
  <!-- Jauges CPU -->
  <div class="card">
    <h2>Charge CPU par VM <span class="badge badge-real">Réel</span></h2>
    <div class="gauges">
      <div class="gauge-wrap"><canvas id="g-vmcp" width="120" height="80"></canvas><div class="gauge-label">vm-cp (AMF/SMF)</div><div class="gauge-val" id="v-vmcp">--%</div></div>
      <div class="gauge-wrap"><canvas id="g-vmran" width="120" height="80"></canvas><div class="gauge-label">vm-ran (gNB/UE)</div><div class="gauge-val" id="v-vmran">--%</div></div>
      <div class="gauge-wrap"><canvas id="g-vmupf" width="120" height="80"></canvas><div class="gauge-label">vm-upf (UPF)</div><div class="gauge-val" id="v-vmupf">--%</div></div>
    </div>
    <div style="margin-top:10px;font-size:.75rem;color:#8b949e">
      Latence eMBB&nbsp;<span class="badge badge-real">Réel</span>&nbsp;<span id="lat-embb">--</span> ms &nbsp;|&nbsp;
      Perte paquets&nbsp;<span class="badge badge-real">Réel</span>&nbsp;<span id="loss-val">--</span>%
    </div>
  </div>
  <!-- What-If -->
  <div class="card">
    <h2>Panneau What-If <span class="badge badge-pred">Prédit</span></h2>
    <div class="wi-controls">
      <div class="wi-ctrl"><label>Trafic (Mbps) <span id="lbl-mbps">100</span></label><input type="range" id="sl-mbps" min="0" max="500" value="100"><span>0–500 Mbps</span></div>
      <div class="wi-ctrl"><label>UE Count <span id="lbl-ue">5</span></label><input type="range" id="sl-ue" min="0" max="50" value="5"><span>0–50 UEs</span></div>
      <div class="wi-ctrl"><label>CPU UPF (%) <span id="lbl-cpu">40</span></label><input type="range" id="sl-cpu" min="0" max="100" value="40"><span>0–100%</span></div>
    </div>
    <div class="wi-buttons">
      <button class="wi-btn" onclick="loadScenario(1)">S1 eMBB Burst</button>
      <button class="wi-btn" onclick="loadScenario(2)">S2 URLLC 80M</button>
      <button class="wi-btn" onclick="loadScenario(3)">S3 Panne gNB-B</button>
      <button class="wi-btn" onclick="loadScenario(4)">S4 CPU UPF 35%</button>
      <button class="wi-btn" onclick="runPredict()" style="background:#1f6feb33;border-color:#58a6ff;color:#58a6ff">▶ Prédire</button>
    </div>
    <div class="wi-result" id="wi-result">Ajustez les curseurs ou choisissez un scénario, puis cliquez ▶ Prédire.</div>
  </div>
  <!-- Tableau comparison -->
  <div class="card full-width">
    <h2>Validation : Prédit vs Mesuré <span class="badge badge-pred">Prédit</span> <span class="badge badge-real">Réel</span></h2>
    <table id="cmp-table">
      <thead><tr><th>Scénario</th><th>Description</th><th>Latence Prédite</th><th>Latence Mesurée</th><th>MAPE Latence</th><th>RMSE</th><th>Violations SLA</th></tr></thead>
      <tbody id="cmp-body"><tr><td colspan="7" style="color:#8b949e;text-align:center">Chargement...</td></tr></tbody>
    </table>
  </div>
</main>

<script>
// ===== State =====
let metricsData = [], compData = [];
let baselineLatency = null;

// ===== Fetch data =====
async function fetchAll() {
  try {
    const [mr, cr] = await Promise.all([
      fetch('/api/metrics').then(r=>r.json()),
      fetch('/api/comparison').then(r=>r.json())
    ]);
    metricsData = mr; compData = cr;
    updateSync();
    renderMetricChart();
    renderGauges();
    renderComparison();
    renderTopology();
  } catch(e){ console.error(e); }
}

function updateSync() {
  const el = document.getElementById('sync-badge');
  if(metricsData.length) {
    const last = metricsData[metricsData.length-1];
    const ts = last.timestamp ? last.timestamp.substring(0,19).replace('T',' ') : '?';
    el.textContent = '✔ SYNCHRONIZED · ' + ts + ' UTC';
    el.className = 'sync-badge ok';
  }
}

// ===== Gauge (SVG arc via Canvas) =====
function drawGauge(canvasId, pct, color) {
  const c = document.getElementById(canvasId);
  if(!c) return;
  const ctx = c.getContext('2d');
  const W=c.width, H=c.height, cx=W/2, cy=H*0.85, R=Math.min(W,H)*0.65;
  ctx.clearRect(0,0,W,H);
  // bg arc
  ctx.beginPath(); ctx.arc(cx,cy,R, Math.PI, 2*Math.PI);
  ctx.lineWidth=14; ctx.strokeStyle='#21262d'; ctx.stroke();
  // value arc
  const angle = Math.PI + (Math.PI * Math.min(pct,100)/100);
  ctx.beginPath(); ctx.arc(cx,cy,R, Math.PI, angle);
  ctx.lineWidth=14; ctx.strokeStyle=color; ctx.lineCap='round'; ctx.stroke();
}

function cpuColor(v) {
  if(v<50) return '#3fb950';
  if(v<80) return '#d29922';
  return '#f85149';
}

function renderGauges() {
  if(!metricsData.length) return;
  const last = metricsData[metricsData.length-1];
  const cp  = parseFloat(last.cpu_vmcp_pct)||0;
  const ran = parseFloat(last.cpu_vmran_pct)||0;
  const upf = parseFloat(last.cpu_vmupf_pct)||0;
  drawGauge('g-vmcp',  cp,  cpuColor(cp));
  drawGauge('g-vmran', ran, cpuColor(ran));
  drawGauge('g-vmupf', upf, cpuColor(upf));
  document.getElementById('v-vmcp').textContent  = cp.toFixed(1)+'%';
  document.getElementById('v-vmran').textContent = ran.toFixed(1)+'%';
  document.getElementById('v-vmupf').textContent = upf.toFixed(1)+'%';
  const lat = parseFloat(last.slice_embb_latency_ms);
  document.getElementById('lat-embb').textContent = isNaN(lat)?'N/A':lat.toFixed(4);
  const loss = parseFloat(last.loss_pct);
  document.getElementById('loss-val').textContent = isNaN(loss)?'N/A':loss.toFixed(2);
}

// ===== Metric timeline chart =====
function renderMetricChart() {
  const c = document.getElementById('metric-canvas');
  if(!c||!metricsData.length) return;
  const ctx = c.getContext('2d');
  const W=c.width, H=c.height;
  ctx.clearRect(0,0,W,H);
  const data = metricsData.slice(-30);
  const lats = data.map(r=>parseFloat(r.latency_ms)||0);
  const cpus = data.map(r=>parseFloat(r.cpu_vmupf_pct)||0);
  const maxLat = Math.max(...lats,0.001);
  const pad = {l:50,r:20,t:20,b:30};
  const W2=W-pad.l-pad.r, H2=H-pad.t-pad.b;
  // grid
  ctx.strokeStyle='#21262d'; ctx.lineWidth=1;
  for(let i=0;i<=4;i++){const y=pad.t+H2*i/4;ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(W-pad.r,y);ctx.stroke();}
  // axis labels
  ctx.fillStyle='#8b949e'; ctx.font='10px monospace'; ctx.textAlign='right';
  for(let i=0;i<=4;i++){const v=(maxLat*(1-i/4)).toExponential(2);ctx.fillText(v,pad.l-4,pad.t+H2*i/4+4);}
  ctx.fillStyle='#8b949e'; ctx.font='10px monospace'; ctx.textAlign='left';
  ctx.fillText('ms latence',pad.l,pad.t-6);
  // latency line
  ctx.strokeStyle='#58a6ff'; ctx.lineWidth=2; ctx.lineJoin='round';
  ctx.beginPath();
  data.forEach((r,i)=>{
    const x=pad.l+W2*i/(data.length-1||1);
    const y=pad.t+H2*(1-lats[i]/maxLat);
    i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
  });
  ctx.stroke();
  // cpu line (scaled 0-100 to same H2)
  ctx.strokeStyle='#d29922'; ctx.lineWidth=1.5; ctx.setLineDash([4,3]);
  ctx.beginPath();
  data.forEach((r,i)=>{
    const x=pad.l+W2*i/(data.length-1||1);
    const y=pad.t+H2*(1-cpus[i]/100);
    i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
  });
  ctx.stroke(); ctx.setLineDash([]);
  // legend
  ctx.fillStyle='#58a6ff'; ctx.fillRect(pad.l,H-20,16,3);
  ctx.fillStyle='#c9d1d9'; ctx.font='10px monospace'; ctx.textAlign='left';
  ctx.fillText('Latence',pad.l+20,H-15);
  ctx.fillStyle='#d29922'; ctx.fillRect(pad.l+100,H-20,16,3);
  ctx.fillStyle='#c9d1d9'; ctx.fillText('CPU UPF',pad.l+120,H-15);
  // store baseline
  if(lats.length) baselineLatency = lats[lats.length-1];
}

// ===== Topology =====
const NODES = {
  vmcp:  {label:'vm-cp\n(AMF/SMF/NRF)',x:0.5,y:0.15,color:'#58a6ff'},
  vmran: {label:'vm-ran\n(gNB+UE)',    x:0.15,y:0.75,color:'#3fb950'},
  vmupf: {label:'vm-upf\n(UPF)',       x:0.85,y:0.75,color:'#d29922'},
  gnb:   {label:'gNB',                 x:0.15,y:0.45,color:'#3fb95099'},
  ue:    {label:'UE-sim',              x:0.05,y:0.9, color:'#8b949e'},
};
const LINKS = [['vmcp','vmran'],['vmcp','vmupf'],['vmran','gnb'],['gnb','ue'],['gnb','vmupf']];
let topoAnim = 0;

function renderTopology() {
  const c = document.getElementById('topo-canvas');
  if(!c) return;
  const ctx = c.getContext('2d');
  const W=c.width, H=c.height;
  ctx.clearRect(0,0,W,H);
  // last cpu for color
  let cpuUpf=0, cpuCp=0;
  if(metricsData.length){
    const last=metricsData[metricsData.length-1];
    cpuUpf=parseFloat(last.cpu_vmupf_pct)||0;
    cpuCp=parseFloat(last.cpu_vmcp_pct)||0;
  }
  // draw links with animated particles
  LINKS.forEach(([a,b])=>{
    const A=NODES[a], B=NODES[b];
    const ax=A.x*W, ay=A.y*H, bx=B.x*W, by=B.y*H;
    ctx.strokeStyle='#30363d'; ctx.lineWidth=2;
    ctx.beginPath(); ctx.moveTo(ax,ay); ctx.lineTo(bx,by); ctx.stroke();
    // particle along link
    const t=((topoAnim/60)%1);
    const px=ax+(bx-ax)*t, py=ay+(by-ay)*t;
    ctx.beginPath(); ctx.arc(px,py,4,0,2*Math.PI);
    ctx.fillStyle='#58a6ff88'; ctx.fill();
  });
  // draw nodes
  Object.entries(NODES).forEach(([k,n])=>{
    const x=n.x*W, y=n.y*H;
    let col = n.color;
    if(k==='vmupf') col=cpuColor(cpuUpf);
    if(k==='vmcp')  col=cpuColor(cpuCp);
    ctx.beginPath(); ctx.arc(x,y,20,0,2*Math.PI);
    ctx.fillStyle=col+'22'; ctx.fill();
    ctx.strokeStyle=col; ctx.lineWidth=2; ctx.stroke();
    ctx.fillStyle=col; ctx.font='bold 10px monospace'; ctx.textAlign='center';
    n.label.split('\n').forEach((l,i)=>ctx.fillText(l,x,y+30+i*13));
  });
  topoAnim++;
}

// ===== Comparison table =====
function mapeClass(v){return v<20?'mape-ok':v<50?'mape-warn':'mape-bad';}
function renderComparison(){
  const tb=document.getElementById('cmp-body');
  if(!compData.length){tb.innerHTML='<tr><td colspan="7" style="color:#8b949e;text-align:center">Aucune donnée</td></tr>';return;}
  tb.innerHTML=compData.map(r=>{
    const mape=parseFloat(r.mape_latency_pct)||0;
    const cls=mapeClass(mape);
    const sla=r.sla_violations||'—';
    return `<tr>
      <td><strong>${r.scenario_id||'—'}</strong></td>
      <td style="font-size:.72rem;color:#8b949e">${r.description||'—'}</td>
      <td>${parseFloat(r.predicted_latency_ms||0).toFixed(4)} ms <span class="badge badge-pred">Prédit</span></td>
      <td>${parseFloat(r.measured_latency_ms||0).toFixed(4)} ms <span class="badge badge-real">Réel</span></td>
      <td class="${cls}">${mape.toFixed(1)}%</td>
      <td>${parseFloat(r.rmse_latency_ms||0).toFixed(4)} ms</td>
      <td style="font-size:.7rem;color:#f85149">${sla}</td>
    </tr>`;
  }).join('');
}

// ===== What-If =====
const sliders=[['sl-mbps','lbl-mbps'],['sl-ue','lbl-ue'],['sl-cpu','lbl-cpu']];
sliders.forEach(([id,lbl])=>{
  document.getElementById(id).addEventListener('input',e=>{
    document.getElementById(lbl).textContent=e.target.value;
  });
});

const SCENARIOS={
  1:{mbps:350,ue:30,cpu:84,label:'S1 eMBB Burst (+250 Mbps)'},
  2:{mbps:80, ue:5, cpu:20,label:'S2 URLLC 80 Mbps'},
  3:{mbps:200,ue:10,cpu:50,label:'S3 Panne gNB-B (handover simulé)'},
  4:{mbps:100,ue:5, cpu:35,label:'S4 CPU UPF 35%'},
};
function loadScenario(n){
  const s=SCENARIOS[n];
  document.getElementById('sl-mbps').value=s.mbps; document.getElementById('lbl-mbps').textContent=s.mbps;
  document.getElementById('sl-ue').value=s.ue;   document.getElementById('lbl-ue').textContent=s.ue;
  document.getElementById('sl-cpu').value=s.cpu;  document.getElementById('lbl-cpu').textContent=s.cpu;
  runPredict(s.label);
}

async function runPredict(label){
  const mbps=document.getElementById('sl-mbps').value;
  const ue=document.getElementById('sl-ue').value;
  const cpu=document.getElementById('sl-cpu').value;
  const lbl=label||`UE=${ue}, Trafic=${mbps} Mbps, CPU=${cpu}%`;
  const r=document.getElementById('wi-result');
  r.innerHTML='⟳ Calcul en cours...';
  try{
    const res=await fetch(`/api/predict?ue_count=${ue}&traffic_mbps=${mbps}&cpu_upf_pct=${cpu}`);
    const d=await res.json();
    if(d.error){r.innerHTML=`<span style="color:#f85149">Erreur: ${d.error}</span>`;return;}
    const pred=parseFloat(d.latency_ms||d.predicted_latency_ms||0);
    const base=baselineLatency||0.048;
    const delta=pred-base;
    const pct=base>0?((delta/base)*100).toFixed(1):0;
    const arrow=delta>0
      ? `<span class="wi-arrow arrow-up">▲</span><span style="color:#f85149">+${pct}%</span>`
      : `<span class="wi-arrow arrow-down">▼</span><span style="color:#3fb950">${pct}%</span>`;
    r.innerHTML=`
      <div style="margin-bottom:6px;color:#8b949e;font-size:.75rem">${lbl}</div>
      <div style="font-size:1rem">
        Baseline : <strong>${base.toFixed(4)} ms</strong> <span class="badge badge-real">Réel</span>
        ${arrow}
        Prédit : <strong>${pred.toFixed(4)} ms</strong> <span class="badge badge-pred">Prédit</span>
      </div>
      <div style="margin-top:6px;font-size:.75rem;color:#8b949e">
        CPU UPF prédit : ${parseFloat(d.cpu_upf_pct||cpu).toFixed(1)}% &nbsp;|&nbsp;
        Source : <span class="badge badge-pred">PREDICTED</span>
      </div>`;
  }catch(e){r.innerHTML=`<span style="color:#f85149">Erreur réseau: ${e}</span>`;}
}

// ===== Animation loop =====
let lastFetch=0;
function loop(ts){
  if(ts-lastFetch>5000){lastFetch=ts;fetchAll();}
  renderTopology();
  requestAnimationFrame(loop);
}
fetchAll().then(()=>requestAnimationFrame(loop));
</script>
</body>
</html>"""

@app.route('/dashboard')
def dashboard():
    return HTML

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090, debug=False)
