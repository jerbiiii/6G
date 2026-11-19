#!/usr/bin/env python3
"""
AT20 - Digital Twin Hybride Réseau 6G (M/M/1 + ML Scikit-Learn)
Calibré sur data/metrics.csv
Simule et prédit latence, débit, perte, CPU et violations SLA pour :
- S1 : Explosion trafic eMBB (+250 Mbps)
- S2 : Charge critique URLLC (80 Mbps)
- S3 : Panne gNB-B et ré-aiguillage UE
- S4 : Réduction CPU UPF
Sortie : data/predictions.csv
"""

import os
import sys
import time
import datetime
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

DATA_DIR = "/home/ubuntu/at20/data"
METRICS_CSV = os.path.join(DATA_DIR, "metrics.csv")
PREDICTIONS_CSV = os.path.join(DATA_DIR, "predictions.csv")

# Seuils SLA 6G
SLA_LIMITS = {
    "embb": {"max_latency_ms": 15.0, "max_loss_pct": 1.0, "min_throughput_mbps": 100.0},
    "urllc": {"max_latency_ms": 2.0, "max_loss_pct": 0.05, "min_throughput_mbps": 10.0},
    "mmtc": {"max_latency_ms": 50.0, "max_loss_pct": 2.0, "min_throughput_mbps": 1.0}
}

class NetworkDigitalTwin:
    def __init__(self, metrics_file=METRICS_CSV):
        self.metrics_file = metrics_file
        self.scaler = StandardScaler()
        self.model_lat = Ridge(alpha=1.0)
        self.model_cpu = Ridge(alpha=1.0)
        self.is_calibrated = False
        self.base_capacity_mbps = 1000.0  # Capacité nominale UPF / lien 1 Gbps
        self.packet_size_bits = 1500 * 8  # Paquet standard MTU 1500 octets
        self.base_prop_delay_ms = 0.85     # RTT physique mesuré à vide

    def calibrate(self):
        """Recalibrage automatique sur data/metrics.csv"""
        if not os.path.exists(self.metrics_file):
            return False
        df = pd.read_csv(self.metrics_file)
        if len(df) < 3:
            return False

        # Nettoyage et extraction features
        df = df.dropna()
        X = df[["ue_count", "throughput_mbps", "vmupf_cpu_pct"]].values
        y_lat = df["latency_ms"].values
        y_cpu = df["vmupf_cpu_pct"].values

        # Calibration baseline moyenne
        if len(df) >= 3:
            self.base_prop_delay_ms = float(df["latency_ms"].quantile(0.1))
            self.model_lat.fit(X, y_lat)
            self.model_cpu.fit(X, y_cpu)
            self.is_calibrated = True
            return True
        return False

    def mm1_latency(self, load_mbps, capacity_mbps):
        """File d'attente M/M/1 : W = 1 / (mu - lambda) + W_prop"""
        if capacity_mbps <= 0:
            return 999.0
        rho = min(load_mbps / capacity_mbps, 0.99)
        mu = (capacity_mbps * 1e6) / self.packet_size_bits # paquets/sec
        lam = (load_mbps * 1e6) / self.packet_size_bits    # paquets/sec
        
        # Délai moyen de file d'attente en ms
        if mu > lam:
            w_q_ms = (1.0 / (mu - lam)) * 1000.0
        else:
            w_q_ms = 100.0
        
        # Si charge très élevée, surcoût non linéaire
        if rho > 0.8:
            w_q_ms += (rho - 0.8) * 50.0

        return max(self.base_prop_delay_ms, self.base_prop_delay_ms + w_q_ms)

    def predict(self, ue_count=1, embb_mbps=500.0, urllc_mbps=20.0, mmtc_mbps=5.0, upf_cpu_cap_pct=100.0, gnb_state="ALL_OK"):
        """
        Prédiction hybride :
        - Entrées : nombre d'UE, trafic par tranche (Mbps), CPU alloué à l'UPF, état des gNB.
        - Sorties : latence, débit, perte, CPU prévus par tranche, alerte SLA violé.
        """
        total_traffic = embb_mbps + urllc_mbps + mmtc_mbps
        effective_capacity = self.base_capacity_mbps * (upf_cpu_cap_pct / 100.0)

        # Impact panne gNB (ex. gNB-B down -> reroutage + goulot)
        reroute_penalty_ms = 0.0
        if gnb_state == "GNB_B_DOWN":
            reroute_penalty_ms = 3.5 # Latence de reroutage et contention cellule voisine
            effective_capacity *= 0.85

        # 1. Calcul analytique M/M/1
        lat_mm1 = self.mm1_latency(total_traffic, effective_capacity) + reroute_penalty_ms

        # 2. Calcul ML (si calibré)
        lat_ml = lat_mm1
        if self.is_calibrated:
            try:
                x_in = np.array([[ue_count, total_traffic, 100.0 - upf_cpu_cap_pct]])
                lat_ml = float(self.model_lat.predict(x_in)[0])
            except Exception:
                lat_ml = lat_mm1

        # Fusion Hybride (40% Théorique M/M/1, 60% Régression ML empirique)
        pred_lat_embb = round(max(0.85, 0.4 * lat_mm1 + 0.6 * max(lat_ml, lat_mm1 * 0.8)), 3)
        
        # Perte de paquets théorique si trafic > capacité
        if total_traffic > effective_capacity:
            pred_loss_pct = round(min(50.0, ((total_traffic - effective_capacity) / total_traffic) * 100.0), 2)
            actual_throughput = effective_capacity
        else:
            # Perte résiduelle minime liée à la congestion
            pred_loss_pct = round(0.0 if total_traffic < 0.7 * effective_capacity else (total_traffic / effective_capacity - 0.7) * 4.0, 2)
            actual_throughput = total_traffic

        # Prédiction CPU UPF
        base_cpu = 15.0 + (total_traffic / self.base_capacity_mbps) * 70.0
        pred_cpu_upf = round(min(100.0, base_cpu * (100.0 / max(upf_cpu_cap_pct, 10.0))), 1)

        # Déclinaison par tranche QoS
        pred_lat_urllc = round(max(0.45, pred_lat_embb * 0.42), 3) # Priorité scheduling 5G
        pred_lat_mmtc = round(pred_lat_embb * 2.5, 3)

        pred_th_embb = round(min(embb_mbps, actual_throughput * (embb_mbps / max(total_traffic, 1))), 2)
        pred_th_urllc = round(min(urllc_mbps, actual_throughput * (urllc_mbps / max(total_traffic, 1))), 2)
        pred_th_mmtc = round(min(mmtc_mbps, actual_throughput * (mmtc_mbps / max(total_traffic, 1))), 2)

        # Vérification des violations SLA
        sla_violations = []
        if pred_lat_embb > SLA_LIMITS["embb"]["max_latency_ms"] or pred_loss_pct > SLA_LIMITS["embb"]["max_loss_pct"]:
            sla_violations.append("eMBB_SLA_VIOLATED")
        if pred_lat_urllc > SLA_LIMITS["urllc"]["max_latency_ms"]:
            sla_violations.append("URLLC_SLA_VIOLATED")
        if pred_lat_mmtc > SLA_LIMITS["mmtc"]["max_latency_ms"]:
            sla_violations.append("mMTC_SLA_VIOLATED")

        return {
            "timestamp": time.time(),
            "ue_count": ue_count,
            "total_traffic_mbps": round(total_traffic, 2),
            "effective_capacity_mbps": round(effective_capacity, 2),
            "pred_latency_ms": pred_lat_embb,
            "pred_throughput_mbps": round(actual_throughput, 2),
            "pred_loss_pct": pred_loss_pct,
            "pred_cpu_upf_pct": pred_cpu_upf,
            "slices": {
                "embb": {"latency_ms": pred_lat_embb, "throughput_mbps": pred_th_embb},
                "urllc": {"latency_ms": pred_lat_urllc, "throughput_mbps": pred_th_urllc},
                "mmtc": {"latency_ms": pred_lat_mmtc, "throughput_mbps": pred_th_mmtc}
            },
            "sla_violated": len(sla_violations) > 0,
            "sla_details": ";".join(sla_violations) if sla_violations else "NONE",
            "data_origin": "PREDICTED"
        }

    def run_scenarios(self):
        """Exécute les 4 scénarios what-if et enregistre dans predictions.csv"""
        scenarios = {
            "S1_eMBB_Burst": {"ue_count": 5, "embb_mbps": 750.0, "urllc_mbps": 20.0, "mmtc_mbps": 5.0, "upf_cpu": 100.0, "gnb": "ALL_OK", "desc": "Explosion de trafic eMBB (+250 Mbps)"},
            "S2_URLLC_Critical": {"ue_count": 10, "embb_mbps": 400.0, "urllc_mbps": 80.0, "mmtc_mbps": 10.0, "upf_cpu": 100.0, "gnb": "ALL_OK", "desc": "Charge critique URLLC (80 Mbps)"},
            "S3_gNB_Failure": {"ue_count": 8, "embb_mbps": 300.0, "urllc_mbps": 20.0, "mmtc_mbps": 5.0, "upf_cpu": 100.0, "gnb": "GNB_B_DOWN", "desc": "Panne du gNB-B et ré-aiguillage des UE"},
            "S4_UPF_CPU_Limit": {"ue_count": 4, "embb_mbps": 350.0, "urllc_mbps": 20.0, "mmtc_mbps": 5.0, "upf_cpu": 35.0, "gnb": "ALL_OK", "desc": "Réduction du CPU alloué à l'UPF (35%)"}
        }

        results = []
        for s_id, s_cfg in scenarios.items():
            pred = self.predict(
                ue_count=s_cfg["ue_count"],
                embb_mbps=s_cfg["embb_mbps"],
                urllc_mbps=s_cfg["urllc_mbps"],
                mmtc_mbps=s_cfg["mmtc_mbps"],
                upf_cpu_cap_pct=s_cfg["upf_cpu"],
                gnb_state=s_cfg["gnb"]
            )
            pred["scenario_id"] = s_id
            pred["scenario_desc"] = s_cfg["desc"]
            results.append(pred)

        # Sauvegarde CSV
        rows = []
        for r in results:
            rows.append({
                "scenario_id": r["scenario_id"],
                "scenario_desc": r["scenario_desc"],
                "total_traffic_mbps": r["total_traffic_mbps"],
                "pred_latency_ms": r["pred_latency_ms"],
                "pred_throughput_mbps": r["pred_throughput_mbps"],
                "pred_loss_pct": r["pred_loss_pct"],
                "pred_cpu_upf_pct": r["pred_cpu_upf_pct"],
                "embb_lat_ms": r["slices"]["embb"]["latency_ms"],
                "urllc_lat_ms": r["slices"]["urllc"]["latency_ms"],
                "mmtc_lat_ms": r["slices"]["mmtc"]["latency_ms"],
                "sla_violated": r["sla_violated"],
                "sla_details": r["sla_details"],
                "data_origin": r["data_origin"]
            })

        df_out = pd.DataFrame(rows)
        df_out.to_csv(PREDICTIONS_CSV, index=False)
        print(f"[OK] Prédictions enregistrées dans {PREDICTIONS_CSV}")
        return results

if __name__ == "__main__":
    twin = NetworkDigitalTwin()
    calibrated = twin.calibrate()
    print(f"Calibration sur {METRICS_CSV}: {'Succès' if calibrated else 'Baseline initiale'}")
    res = twin.run_scenarios()
    for r in res:
        print(f"[{r['scenario_id']}] {r['scenario_desc']} -> Lat: {r['pred_latency_ms']}ms, Th: {r['pred_throughput_mbps']}Mbps, Loss: {r['pred_loss_pct']}%, CPU UPF: {r['pred_cpu_upf_pct']}%, SLA: {r['sla_details']}")
