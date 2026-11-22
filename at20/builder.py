import re

html_path = "/home/ubuntu/at20/dashboard.html"
with open(html_path, "r") as f:
    html = f.read()

# 1. Update header actions to include mode badge and direct return button
old_header = """  <div class="header-actions">
    <div class="sync-badge">
      <div class="sync-dot"></div>
      <span id="syncText">SYNCHRONIZED (Connexion...)</span>
    </div>
    <a href="/api/export/csv" class="btn" download>📥 Export metrics.csv</a>
    <a href="/api/export/json" class="btn" download>📥 Export JSON</a>
  </div>"""

new_header = """  <div class="header-actions">
    <div id="modeBadge" class="sync-badge" style="background:rgba(0,230,118,0.12); border:1px solid #00e676; color:#00e676;">
      <div id="modeDot" class="sync-dot" style="background:#00e676; box-shadow:0 0 8px #00e676;"></div>
      <span id="syncText">MODE DIRECT : TÉLÉMÉTRIE LIVE</span>
    </div>
    <button class="btn" style="border-color:#00e676; color:#00e676;" onclick="resetToRealMode()">🔄 Revenir au Direct</button>
    <a href="/api/export/csv" class="btn" download>📥 Export metrics.csv</a>
    <a href="/api/export/json" class="btn" download>📥 Export JSON</a>
  </div>"""

if old_header in html:
    html = html.replace(old_header, new_header)
    print("Header replaced successfully")
else:
    print("Warning: old_header not found, skipping header replace")

# 2. Update presets buttons to include Reset button
old_presets = """    <div class="preset-btns">
      <button class="preset-btn" onclick="applyPreset('s1')">S1: eMBB +250M</button>
      <button class="preset-btn" onclick="applyPreset('s2')">S2: URLLC 80M</button>
      <button class="preset-btn" onclick="toggleGnBFailure()">S3: Panne gNB-B</button>
      <button class="preset-btn" onclick="applyPreset('s4')">S4: CPU UPF 35%</button>
    </div>"""

new_presets = """    <div class="preset-btns" style="grid-template-columns: repeat(5, 1fr);">
      <button id="btnS1" class="preset-btn" onclick="applyPreset('s1')">S1: eMBB +250M</button>
      <button id="btnS2" class="preset-btn" onclick="applyPreset('s2')">S2: URLLC 80M</button>
      <button id="btnS3" class="preset-btn" onclick="toggleGnBFailure()">S3: Panne gNB-B</button>
      <button id="btnS4" class="preset-btn" onclick="applyPreset('s4')">S4: CPU UPF 35%</button>
      <button class="preset-btn" style="border-color:#00e676; color:#00e676;" onclick="resetToRealMode()">🔄 Direct</button>
    </div>"""

if old_presets in html:
    html = html.replace(old_presets, new_presets)
    print("Presets replaced successfully")
else:
    print("Warning: old_presets not found")

with open(html_path, "w") as f:
    f.write(html)
print("Phase 1 done")
