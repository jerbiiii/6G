html_path = "/home/ubuntu/at20/dashboard.html"
with open(html_path, "r") as f:
    html = f.read()

s_start = html.find("<script>")
s_end = html.find("</script>")

if s_start == -1 or s_end == -1:
    print("Erreur balises script introuvables")
    exit(1)

new_script = """<script>
// --- ÉTAT RÉACTIF GLOBAL DU DIGITAL TWIN ---
let currentMode = "REAL"; // "REAL" ou "SIMULATION"
let realTelemetry = null;
let activeData = {
  throughput_mbps: 560.0,
  latency_ms: 1.35,
  jitter_ms: 0.12,
  loss_pct: 0.0,
  vmcp_cpu_pct: 3,
  vmran_cpu_pct: 1,
  vmupf_cpu_pct: 1,
  embb_latency_ms: 1.35,
  urllc_latency_ms: 0.58,
  mmtc_latency_ms: 3.6,
  gnbBDown: false
};

// Historique glissant pour le graphe live
let rollingChart = [];
const MAX_CHART_PTS = 30;

// Nœuds physiques réels
const topoNodes = {
  cp:  { name: "vm-cp",  ip: "172.31.47.81",  role: "Control Plane", x: 200, y: 70,  color: "#00e5ff" },
  ran: { name: "vm-ran", ip: "172.31.34.222", role: "gNodeB-A",      x: 200, y: 240, color: "#3b82f6" },
  upf: { name: "vm-upf", ip: "172.31.38.166", role: "User Plane",    x: 520, y: 155, color: "#a855f7" },
  gnbB:{ name: "gNB-B",  ip: "Cell-2",        role: "gNodeB-B",      x: 350, y: 260, color: "#38bdf8" },
  ue1: { name: "UE-01",  ip: "10.45.0.3",     role: "eMBB UE",       x: 55,  y: 240, color: "#34d399" },
  ue2: { name: "UE-02",  ip: "10.45.0.4",     role: "URLLC UE",      x: 55,  y: 150, color: "#fbbf24" }
};

// Pool de particules bidirectionnelles
let particles = [];
function initParticles() {
  particles = [];
  // eMBB UL & DL
  for (let i = 0; i < 10; i++) {
    particles.push({ stream: "embb_ul1", from: "ue1", to: "ran", progress: Math.random(), speed: 0.009 + Math.random()*0.005, color: "#34d399", size: 3 });
    particles.push({ stream: "embb_ul2", from: "ran", to: "upf", progress: Math.random(), speed: 0.008 + Math.random()*0.005, color: "#34d399", size: 3.2 });
    particles.push({ stream: "embb_dl1", from: "upf", to: "ran", progress: Math.random(), speed: 0.009 + Math.random()*0.005, color: "#00e5ff", size: 3 });
    particles.push({ stream: "embb_dl2", from: "ran", to: "ue1", progress: Math.random(), speed: 0.008 + Math.random()*0.005, color: "#00e5ff", size: 3 });
  }
  // URLLC UL & DL
  for (let i = 0; i < 8; i++) {
    particles.push({ stream: "urllc_ul1", from: "ue2", to: "gnbB", progress: Math.random(), speed: 0.014 + Math.random()*0.005, color: "#fbbf24", size: 2.8 });
    particles.push({ stream: "urllc_ul2", from: "gnbB", to: "upf", progress: Math.random(), speed: 0.014 + Math.random()*0.005, color: "#fbbf24", size: 2.8 });
    particles.push({ stream: "urllc_dl1", from: "upf", to: "gnbB", progress: Math.random(), speed: 0.014 + Math.random()*0.005, color: "#f59e0b", size: 2.8 });
    particles.push({ stream: "urllc_dl2", from: "gnbB", to: "ue2", progress: Math.random(), speed: 0.014 + Math.random()*0.005, color: "#f59e0b", size: 2.8 });
  }
  // Control Plane N2 & N4
  for (let i = 0; i < 4; i++) {
    particles.push({ stream: "n2_down", from: "cp", to: "ran", progress: Math.random(), speed: 0.004 + Math.random()*0.002, color: "#60a5fa", size: 2.2 });
    particles.push({ stream: "n2_up",   from: "ran", to: "cp", progress: Math.random(), speed: 0.004 + Math.random()*0.002, color: "#60a5fa", size: 2.2 });
    particles.push({ stream: "n4_down", from: "cp", to: "upf", progress: Math.random(), speed: 0.004 + Math.random()*0.002, color: "#c084fc", size: 2.2 });
    particles.push({ stream: "n4_up",   from: "upf", to: "cp", progress: Math.random(), speed: 0.004 + Math.random()*0.002, color: "#c084fc", size: 2.2 });
  }
}
initParticles();

// --- SYNCHRONISATION INSTANTANÉE DE TOUS LES PANNEAUX ---
function updateAllPanels(d) {
  activeData = d;

  // 1. Jauges CPU
  const cpVal = Math.round(d.vmcp_cpu_pct);
  const ranVal = Math.round(d.vmran_cpu_pct);
  const upfVal = Math.round(d.vmupf_cpu_pct);

  document.getElementById("cpuCP").innerText = cpVal + "%";
  document.getElementById("barCP").style.width = Math.min(cpVal, 100) + "%";

  document.getElementById("cpuRAN").innerText = ranVal + "%";
  document.getElementById("barRAN").style.width = Math.min(ranVal, 100) + "%";

  document.getElementById("cpuUPF").innerText = upfVal + "%";
  document.getElementById("barUPF").style.width = Math.min(upfVal, 100) + "%";
  document.getElementById("barUPF").style.background = (upfVal > 80) ? "var(--accent-red)" : "#a855f7";

  // 2. KPIs
  document.getElementById("kpiTh").innerText = parseFloat(d.throughput_mbps).toFixed(1) + " Mbps";
  document.getElementById("kpiLat").innerText = parseFloat(d.latency_ms).toFixed(2) + " ms";
  document.getElementById("kpiJitter").innerText = parseFloat(d.jitter_ms).toFixed(3) + " ms";
  document.getElementById("kpiLoss").innerText = parseFloat(d.loss_pct).toFixed(1) + " %";

  document.getElementById("kpiLat").style.color = (d.latency_ms > 15) ? "var(--accent-red)" : ((d.latency_ms > 5) ? "var(--accent-amber)" : "#f3f4f6");
  document.getElementById("kpiLoss").style.color = (d.loss_pct > 1) ? "var(--accent-red)" : "#f3f4f6";

  // 3. Alimentation et mise à jour de la courbe temps réel
  pushChartPoint(d.embb_latency_ms, d.urllc_latency_ms, d.mmtc_latency_ms);
}

function pushChartPoint(embb, urllc, mmtc) {
  rollingChart.push({
    embb: parseFloat(embb) || 1.2,
    urllc: parseFloat(urllc) || 0.5,
    mmtc: parseFloat(mmtc) || 3.0
  });
  if (rollingChart.length > MAX_CHART_PTS) {
    rollingChart.shift();
  }
  drawChart();
}

function drawChart() {
  const canvas = document.getElementById("chartCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (rollingChart.length < 2) return;

  const w = canvas.width;
  const h = canvas.height;
  const padding = 32;

  ctx.strokeStyle = "#1e293b";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding, h - padding);
  ctx.lineTo(w - 10, h - padding);
  ctx.stroke();

  let maxLat = 10.0;
  rollingChart.forEach(p => {
    if (p.embb > maxLat) maxLat = p.embb * 1.2;
    if (p.mmtc > maxLat) maxLat = p.mmtc * 1.2;
  });

  const stepX = (w - padding - 20) / Math.max(rollingChart.length - 1, 1);

  function drawSeries(key, color) {
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.2;
    rollingChart.forEach((pt, idx) => {
      const val = pt[key];
      const x = padding + idx * stepX;
      const y = (h - padding) - (Math.min(val, maxLat) / maxLat) * (h - 2 * padding);
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }

  drawSeries("embb", "#00e5ff");
  drawSeries("urllc", "#00e676");
  drawSeries("mmtc", "#a855f7");

  ctx.fillStyle = "#64748b";
  ctx.font = "9px monospace";
  ctx.textAlign = "right";
  ctx.fillText(maxLat.toFixed(1) + " ms", padding - 4, padding + 10);
  ctx.fillText("0 ms", padding - 4, h - padding);
}

// Animation Topologie Canvas
function initTopo() {
  const canvas = document.getElementById("topoCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const isDown = activeData.gnbBDown;

    const links = [
      { from: topoNodes.ran, to: topoNodes.upf, label: "N3 GTP-U (UDP 2152)", color: "#334155", width: 3 },
      { from: topoNodes.cp,  to: topoNodes.ran, label: "N2 NGAP (SCTP 38412)", color: "#1e3a8a", width: 2, dashed: true },
      { from: topoNodes.cp,  to: topoNodes.upf, label: "N4 PFCP (UDP 8805)",   color: "#581c87", width: 2, dashed: true },
      { from: topoNodes.ue1, to: topoNodes.ran, label: "NR-Uu (eMBB)",          color: "#065f46", width: 2.5 },
    ];

    if (!isDown) {
      links.push({ from: topoNodes.ue2, to: topoNodes.gnbB, label: "NR-Uu (URLLC)", color: "#78350f", width: 2.5 });
      links.push({ from: topoNodes.gnbB, to: topoNodes.upf, label: "N3 gNB-B",      color: "#334155", width: 2.5 });
    } else {
      links.push({ from: topoNodes.ue2, to: topoNodes.gnbB, label: "LIEN ROMPU", color: "#7f1d1d", width: 2, dashed: true });
      links.push({ from: topoNodes.ue2, to: topoNodes.ran,  label: "⚡ REROUTAGE URLLC -> gNB-A", color: "#f97316", width: 3 });
    }

    links.forEach(l => {
      ctx.beginPath();
      ctx.strokeStyle = l.color;
      ctx.lineWidth = l.width;
      if (l.dashed) ctx.setLineDash([4, 4]); else ctx.setLineDash([]);
      ctx.moveTo(l.from.x, l.from.y);
      ctx.lineTo(l.to.x, l.to.y);
      ctx.stroke();
      ctx.setLineDash([]);

      const mx = (l.from.x + l.to.x) / 2;
      const my = (l.from.y + l.to.y) / 2 - 5;
      ctx.fillStyle = (l.color === "#f97316") ? "#f97316" : ((l.color === "#7f1d1d") ? "#ef4444" : "#64748b");
      ctx.font = "bold 9px " + getComputedStyle(document.body).getPropertyValue('--font-mono');
      ctx.textAlign = "center";
      ctx.fillText(l.label, mx, my);
    });

    const th = activeData.throughput_mbps;
    let speedMult = 1.0;
    if (th > 700) speedMult = 2.4;
    else if (th > 400) speedMult = 1.5;

    particles.forEach(p => {
      p.progress += p.speed * speedMult;
      if (p.progress > 1) p.progress = 0;

      let fromKey = p.from;
      let toKey = p.to;

      if (isDown) {
        if (fromKey === "gnbB") fromKey = "ran";
        if (toKey === "gnbB") toKey = "ran";
        if (p.from === "ue2" && p.to === "gnbB") { fromKey = "ue2"; toKey = "ran"; }
      }

      const fNode = topoNodes[fromKey];
      const tNode = topoNodes[toKey];
      if (!fNode || !tNode) return;

      const px = fNode.x + (tNode.x - fNode.x) * p.progress;
      const py = fNode.y + (tNode.y - fNode.y) * p.progress;

      let curColor = p.color;
      if (p.stream.startsWith("embb") && th > 700) curColor = "#ff1744";
      else if (p.stream.startsWith("urllc") && isDown) curColor = "#f97316";

      ctx.beginPath();
      ctx.fillStyle = curColor;
      ctx.shadowColor = curColor;
      ctx.shadowBlur = 6;
      ctx.arc(px, py, p.size, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;
    });

    Object.keys(topoNodes).forEach(k => {
      const n = topoNodes[k];
      const isFailed = (k === "gnbB" && isDown);

      let halo = "rgba(0,229,255,0.12)";
      if (k === "upf" && activeData.vmupf_cpu_pct > 80) halo = "rgba(255,23,68,0.3)";
      if (isFailed) halo = "rgba(239,68,68,0.25)";

      ctx.beginPath();
      ctx.arc(n.x, n.y, 22, 0, Math.PI * 2);
      ctx.fillStyle = halo;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(n.x, n.y, 16, 0, Math.PI * 2);
      ctx.fillStyle = isFailed ? "#7f1d1d" : "#0f172a";
      ctx.fill();
      ctx.lineWidth = 2.5;
      ctx.strokeStyle = isFailed ? "#ef4444" : n.color;
      ctx.stroke();

      ctx.fillStyle = isFailed ? "#ef4444" : "#f1f5f9";
      ctx.font = "bold 10px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(isFailed ? n.name + " [PANNE]" : n.name, n.x, n.y + 28);

      ctx.fillStyle = isFailed ? "#f87171" : "#94a3b8";
      ctx.font = "8.5px " + getComputedStyle(document.body).getPropertyValue('--font-mono');
      ctx.fillText(n.ip, n.x, n.y + 40);
    });

    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
}

// Polling temps réel du flux EC2
async function fetchRealTelemetry() {
  try {
    const res = await fetch("/api/metrics");
    const data = await res.json();
    if (data.latest) {
      realTelemetry = data.latest;

      if (currentMode === "REAL") {
        updateAllPanels({
          throughput_mbps: parseFloat(data.latest.throughput_mbps),
          latency_ms: parseFloat(data.latest.latency_ms),
          jitter_ms: parseFloat(data.latest.jitter_ms),
          loss_pct: parseFloat(data.latest.loss_pct),
          vmcp_cpu_pct: parseFloat(data.latest.vmcp_cpu_pct),
          vmran_cpu_pct: parseFloat(data.latest.vmran_cpu_pct),
          vmupf_cpu_pct: parseFloat(data.latest.vmupf_cpu_pct),
          embb_latency_ms: parseFloat(data.latest.embb_latency_ms),
          urllc_latency_ms: parseFloat(data.latest.urllc_latency_ms),
          mmtc_latency_ms: parseFloat(data.latest.mmtc_latency_ms),
          gnbBDown: false
        });

        const syncTxt = document.getElementById("syncText");
        if (syncTxt) syncTxt.innerText = "MODE DIRECT : TÉLÉMÉTRIE LIVE (" + (data.iso_time ? data.iso_time.split("T")[1].slice(0,8) : "LIVE") + ")";
      }
    }
  } catch (e) {
    console.error("Erreur télémétrie:", e);
  }
}

// Déclenchement de la simulation : TOUS les panneaux réagissent en direct !
async function triggerSimulation() {
  currentMode = "SIMULATION";

  const badge = document.getElementById("modeBadge");
  if (badge) {
    badge.style.background = "rgba(192,132,252,0.18)";
    badge.style.borderColor = "#c084fc";
    badge.style.color = "#c084fc";
  }
  const dot = document.getElementById("modeDot");
  if (dot) {
    dot.style.background = "#c084fc";
    dot.style.boxShadow = "0 0 8px #c084fc";
  }
  const syncTxt = document.getElementById("syncText");
  if (syncTxt) syncTxt.innerText = "⚡ MODE SIMULATION WHAT-IF (DIGITAL TWIN ACTIF)";

  const traffic = parseFloat(document.getElementById("rngTraffic").value);
  const ue = parseInt(document.getElementById("rngUE").value);
  const cpu = parseFloat(document.getElementById("rngCPU").value);
  const gnb = activeData.gnbBDown ? "GNB_B_DOWN" : "ALL_OK";

  document.getElementById("lblTraffic").innerText = traffic + " Mbps";
  document.getElementById("lblUE").innerText = ue + " UE" + (ue > 1 ? "s" : "");
  document.getElementById("lblCPU").innerText = cpu + " %";

  try {
    const res = await fetch(`/api/predict?traffic=${traffic}&ue=${ue}&cpu=${cpu}&gnb=${gnb}`);
    const pred = await res.json();

    document.getElementById("predLat").innerText = pred.pred_latency_ms + " ms";
    document.getElementById("predTh").innerText = pred.pred_throughput_mbps + " Mbps";
    document.getElementById("predLoss").innerText = pred.pred_loss_pct + " %";
    document.getElementById("predCPU").innerText = pred.pred_cpu_upf_pct + " %";

    const slaB = document.getElementById("slaBadge");
    if (pred.sla_violated) {
      slaB.className = "sla-fail";
      slaB.innerText = "ALERTE: " + pred.sla_details;
    } else {
      slaB.className = "sla-ok";
      slaB.innerText = "SLA RESPECTÉ";
    }

    if (realTelemetry) {
      const dLat = (pred.pred_latency_ms - parseFloat(realTelemetry.latency_ms)).toFixed(2);
      document.getElementById("deltaLat").innerText = (dLat >= 0 ? "+" : "") + dLat + " ms";
      document.getElementById("deltaLat").style.color = (dLat > 3) ? "var(--accent-red)" : "var(--accent-green)";
    }

    // TOUS LES PANNEAUX SONT MIS À JOUR EN TEMPS RÉEL !
    updateAllPanels({
      throughput_mbps: pred.pred_throughput_mbps,
      latency_ms: pred.pred_latency_ms,
      jitter_ms: Math.min(2.5, pred.pred_latency_ms * 0.12),
      loss_pct: pred.pred_loss_pct,
      vmcp_cpu_pct: Math.min(95, 3 + ue * 2.5),
      vmran_cpu_pct: Math.min(95, 1 + (traffic / 1000) * 45),
      vmupf_cpu_pct: pred.pred_cpu_upf_pct,
      embb_latency_ms: pred.slices.embb.latency_ms,
      urllc_latency_ms: pred.slices.urllc.latency_ms,
      mmtc_latency_ms: pred.slices.mmtc.latency_ms,
      gnbBDown: (gnb === "GNB_B_DOWN")
    });

  } catch (e) {
    console.error("Erreur simulation:", e);
  }
}

function applyPreset(p) {
  document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));

  if (p === 's1') {
    document.getElementById("btnS1").classList.add('active');
    document.getElementById("rngTraffic").value = 750;
    document.getElementById("rngUE").value = 5;
    document.getElementById("rngCPU").value = 100;
    activeData.gnbBDown = false;
  } else if (p === 's2') {
    document.getElementById("btnS2").classList.add('active');
    document.getElementById("rngTraffic").value = 490;
    document.getElementById("rngUE").value = 10;
    document.getElementById("rngCPU").value = 100;
    activeData.gnbBDown = false;
  } else if (p === 's4') {
    document.getElementById("btnS4").classList.add('active');
    document.getElementById("rngTraffic").value = 350;
    document.getElementById("rngUE").value = 4;
    document.getElementById("rngCPU").value = 35;
    activeData.gnbBDown = false;
  }
  triggerSimulation();
}

function toggleGnBFailure() {
  activeData.gnbBDown = !activeData.gnbBDown;
  const btn = document.getElementById("btnS3");
  if (activeData.gnbBDown) {
    btn.classList.add('active');
    btn.innerText = "S3: Panne ACTIVE";
  } else {
    btn.classList.remove('active');
    btn.innerText = "S3: Panne gNB-B";
  }
  triggerSimulation();
}

function resetToRealMode() {
  currentMode = "REAL";
  activeData.gnbBDown = false;
  document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
  document.getElementById("btnS3").innerText = "S3: Panne gNB-B";

  const badge = document.getElementById("modeBadge");
  if (badge) {
    badge.style.background = "rgba(0,230,118,0.12)";
    badge.style.borderColor = "#00e676";
    badge.style.color = "#00e676";
  }
  const dot = document.getElementById("modeDot");
  if (dot) {
    dot.style.background = "#00e676";
    dot.style.boxShadow = "0 0 8px #00e676";
  }
  const syncTxt = document.getElementById("syncText");
  if (syncTxt) syncTxt.innerText = "MODE DIRECT : TÉLÉMÉTRIE LIVE";

  if (realTelemetry) {
    document.getElementById("rngTraffic").value = Math.round(parseFloat(realTelemetry.throughput_mbps));
    document.getElementById("rngUE").value = 1;
    document.getElementById("rngCPU").value = 100;
    document.getElementById("lblTraffic").innerText = Math.round(parseFloat(realTelemetry.throughput_mbps)) + " Mbps";
    document.getElementById("lblUE").innerText = "1 UE";
    document.getElementById("lblCPU").innerText = "100 %";
  }

  fetchRealTelemetry();
}

// Tableau Prédit vs Mesuré
async function fetchComparison() {
  try {
    const res = await fetch("/api/comparison");
    const data = await res.json();
    if (data.scenarios && data.scenarios.length > 0) {
      const tbody = document.getElementById("compTableBody");
      tbody.innerHTML = "";

      data.scenarios.forEach(s => {
        const tr = document.createElement("tr");

        const mapeLat = parseFloat(s.mape_latency_pct);
        const mapeTh = parseFloat(s.mape_throughput_pct);

        const badgeLatClass = mapeLat < 15 ? "diff-good" : (mapeLat < 50 ? "diff-warn" : "diff-bad");
        const badgeThClass = mapeTh < 15 ? "diff-good" : (mapeTh < 30 ? "diff-warn" : "diff-bad");
        const slaClass = s.sla_violated_pred ? "sla-fail" : "sla-ok";
        const slaText = s.sla_violated_pred ? "VIOLATION" : "CONFORME";

        tr.innerHTML = `
          <td><strong>${s.scenario_id}</strong></td>
          <td style="color:#94a3b8;">${s.scenario_desc}</td>
          <td>${s.pred_latency_ms} ms / <span style="color:#38bdf8;">${s.meas_latency_ms} ms</span></td>
          <td><span class="badge-diff ${badgeLatClass}">${mapeLat}%</span></td>
          <td>${s.pred_throughput_mbps} M / <span style="color:#38bdf8;">${s.meas_throughput_mbps} M</span></td>
          <td><span class="badge-diff ${badgeThClass}">${mapeTh}%</span></td>
          <td>${s.pred_cpu_pct}% / ${s.meas_cpu_pct}%</td>
          <td>${s.pred_loss_pct}% / ${s.meas_loss_pct}%</td>
          <td><span class="${slaClass}">${slaText}</span></td>
        `;
        tbody.appendChild(tr);
      });

      if (data.global_mape) {
        document.getElementById("globalMapeBadge").innerText = 
          `MAPE Global : Latence ${data.global_mape.latency_pct}% | Débit ${data.global_mape.throughput_pct}%`;
      }
    }
  } catch (e) {
    console.error("Erreur comparaison:", e);
  }
}

// Initialisation globale
window.onload = () => {
  initTopo();
  fetchRealTelemetry();
  fetchComparison();
  setInterval(fetchRealTelemetry, 1500);
};
</script>"""

new_html = html[:s_start] + new_script + html[s_end+9:]
with open(html_path, "w") as f:
    f.write(new_html)

print("Mise à jour réactive terminée avec succès !")
