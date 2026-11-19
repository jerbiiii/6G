#!/usr/bin/env python3
"""
AT20 - Dashboard Web du Digital Twin Intelligent 6G
Serveur HTTP autonome haute performance (aucun CDN requis, compatible 100% hors-ligne)
Expose :
- GET /              : Dashboard visuel et interactif
- GET /api/metrics   : Dernières métriques réelles + historique 30 points
- GET /api/comparison: Résultats Prédit vs Réel (S1-S4) avec MAPE & RMSE
- GET /api/predict   : Moteur d'inférence What-If interactif en direct
- GET /api/export/csv: Export du fichier data/metrics.csv
- GET /api/export/json: Export JSON complet
"""

import os
import sys
import json
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import pandas as pd

sys.path.append("/home/ubuntu/at20")
from twin import NetworkDigitalTwin

PORT = 8090
DATA_DIR = "/home/ubuntu/at20/data"
METRICS_CSV = os.path.join(DATA_DIR, "metrics.csv")
COMPARISON_CSV = os.path.join(DATA_DIR, "comparison.csv")
HTML_FILE = "/home/ubuntu/at20/dashboard.html"

# Initialisation du moteur Twin
twin_engine = NetworkDigitalTwin()
twin_engine.calibrate()

class DigitalTwinHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence standard HTTP logs for performance
        return

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self.serve_html()
        elif path == "/api/metrics":
            self.serve_metrics()
        elif path == "/api/comparison":
            self.serve_comparison()
        elif path == "/api/predict":
            self.serve_predict(query)
        elif path == "/api/export/csv":
            self.serve_export_csv()
        elif path == "/api/export/json":
            self.serve_export_json()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def serve_html(self):
        if not os.path.exists(HTML_FILE):
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Dashboard HTML missing")
            return
        with open(HTML_FILE, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def serve_metrics(self):
        if not os.path.exists(METRICS_CSV):
            self.send_json({"error": "metrics.csv missing"}, status=503)
            return
        try:
            df = pd.read_csv(METRICS_CSV).dropna()
            if len(df) == 0:
                self.send_json({"error": "metrics.csv empty"}, status=503)
                return
            latest = df.iloc[-1].to_dict()
            history = df.tail(30).to_dict(orient="records")
            self.send_json({
                "status": "SYNCHRONIZED",
                "timestamp": latest.get("timestamp", time.time()),
                "iso_time": latest.get("iso_time", ""),
                "latest": latest,
                "history": history
            })
        except Exception as e:
            self.send_json({"error": str(e)}, status=500)

    def serve_comparison(self):
        if not os.path.exists(COMPARISON_CSV):
            self.send_json({"scenarios": [], "error": "comparison.csv missing"})
            return
        try:
            df = pd.read_csv(COMPARISON_CSV)
            scenarios = df.to_dict(orient="records")
            mape_lat = df["mape_latency_pct"].mean() if "mape_latency_pct" in df else 0.0
            mape_th = df["mape_throughput_pct"].mean() if "mape_throughput_pct" in df else 0.0
            self.send_json({
                "scenarios": scenarios,
                "global_mape": {
                    "latency_pct": round(mape_lat, 2),
                    "throughput_pct": round(mape_th, 2)
                }
            })
        except Exception as e:
            self.send_json({"error": str(e)}, status=500)

    def serve_predict(self, query):
        try:
            traffic = float(query.get("traffic", [500.0])[0])
            ue = int(query.get("ue", [1])[0])
            cpu = float(query.get("cpu", [100.0])[0])
            gnb = query.get("gnb", ["ALL_OK"])[0]

            # Répartition du trafic par défaut : 80% eMBB, 15% URLLC, 5% mMTC
            embb = traffic * 0.80
            urllc = traffic * 0.15
            mmtc = traffic * 0.05

            pred = twin_engine.predict(
                ue_count=ue,
                embb_mbps=embb,
                urllc_mbps=urllc,
                mmtc_mbps=mmtc,
                upf_cpu_cap_pct=cpu,
                gnb_state=gnb
            )
            self.send_json(pred)
        except Exception as e:
            self.send_json({"error": str(e)}, status=400)

    def serve_export_csv(self):
        if not os.path.exists(METRICS_CSV):
            self.send_response(404)
            self.end_headers()
            return
        with open(METRICS_CSV, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/csv")
        self.send_header("Content-Disposition", 'attachment; filename="metrics.csv"')
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def serve_export_json(self):
        export_data = {
            "exported_at": time.time(),
            "metrics": [],
            "comparison": []
        }
        if os.path.exists(METRICS_CSV):
            export_data["metrics"] = pd.read_csv(METRICS_CSV).tail(50).to_dict(orient="records")
        if os.path.exists(COMPARISON_CSV):
            export_data["comparison"] = pd.read_csv(COMPARISON_CSV).to_dict(orient="records")
        self.send_json(export_data)

    def send_json(self, data, status=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def run():
    server = HTTPServer(("0.0.0.0", PORT), DigitalTwinHTTPHandler)
    print(f"[*] Dashboard Digital Twin 6G actif sur http://0.0.0.0:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[!] Arrêt du serveur.")
        server.server_close()

if __name__ == "__main__":
    run()
