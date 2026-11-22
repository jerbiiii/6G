#!/usr/bin/env python3
"""
AT20 Digital Twin — Modele hybride M/M1 + Ridge
Sources de données : metrics.csv réel collecté sur le testbed 6G AWS
"""
import csv, os, math, json
from datetime import datetime, timezone

# ─── SLA 6G (3GPP TS 22.261) ─────────────────────────────────────────────────
SLA = {
    "embb_latency_max_ms":  10.0,
    "urllc_latency_max_ms":  1.0,
    "mmtc_latency_max_ms":  50.0,
    "loss_max_pct":          1.0,
    "cpu_upf_max_pct":      80.0,
}

METRICS_CSV = "/home/ubuntu/at20/data/metrics.csv"
MODEL_VERSION = "1.0"

# ─── Utilitaires ──────────────────────────────────────────────────────────────
def _mean(values):
    v = [x for x in values if x is not None and not math.isnan(x)]
    return sum(v) / len(v) if v else float("nan")

def _std(values):
    v = [x for x in values if x is not None and not math.isnan(x)]
    if len(v) < 2:
        return 1.0
    m = _mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / len(v)) or 1.0

def _safe_float(x, default=float("nan")):
    try:
        f = float(x)
        return f if not math.isnan(f) else default
    except Exception:
        return default

# ─── Lecture du CSV réel ──────────────────────────────────────────────────────
def load_metrics(csv_path=METRICS_CSV):
    rows = []
    if not os.path.exists(csv_path):
        return rows
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

# ─── Modèle M/M1 (file d'attente simple) ─────────────────────────────────────
class MM1Model:
    """
    Modélise la latence d'une file M/M1 selon la charge.
    mu  = taux de service (paquets/s ou Mbps équivalent) — calibré sur les données réelles
    lambda = taux d'arrivée (proportionnel au trafic et au nombre d'UE)
    W = 1 / (mu - lambda)   (en unités normalisées, puis converti en ms)
    """
    def __init__(self):
        self.mu_base = 1000.0   # Capacité de base (Mbps)
        self.latency_base_ms = 0.05  # Latence mesurée à charge nulle (ms) — calibrée
        self.calibrated = False

    def calibrate(self, rows):
        """Calibre mu_base sur la latence mesurée à faible charge."""
        low_load = [r for r in rows
                    if _safe_float(r.get("cpu_vmupf_pct", "nan"), float("nan")) < 10
                    and _safe_float(r.get("slice_embb_latency_ms", "nan"), float("nan")) > 0]
        if low_load:
            lats = [_safe_float(r["slice_embb_latency_ms"]) for r in low_load]
            self.latency_base_ms = _mean(lats)
        self.calibrated = True

    def predict(self, ue_count: float, traffic_mbps: float, cpu_upf_pct: float) -> dict:
        """Prédit la latence via le modèle M/M1."""
        # Taux d'arrivée normalisé (0 à ~1 × mu_base)
        cpu_load = min(cpu_upf_pct / 100.0, 0.99)
        traffic_load = min(traffic_mbps / self.mu_base, 0.99)
        # Charge combinée : pondération CPU 70% / trafic 30%
        rho = min(0.7 * cpu_load + 0.3 * traffic_load, 0.99)
        if rho > 0:
            # Formule M/M1 : W = rho / (mu * (1 - rho)) + W0
            queuing_ms = (rho / (1.0 - rho)) * self.latency_base_ms
        else:
            queuing_ms = 0.0
        predicted = self.latency_base_ms + queuing_ms
        return {
            "predicted_latency_mm1_ms": round(predicted, 4),
            "rho": round(rho, 4),
            "queue_stable": rho < 1.0,
        }

# ─── Modèle de Régression Ridge (natif, sans scikit-learn requis) ─────────────
class RidgeModel:
    """
    Régression Ridge implémentée en Python pur (numpy-free).
    Prédit slice_embb_latency_ms à partir de cpu_vmcp_pct, cpu_vmran_pct,
    cpu_vmupf_pct, ue_count, handover_count.
    """
    FEATURES = ["cpu_vmcp_pct", "cpu_vmran_pct", "cpu_vmupf_pct", "ue_count", "handover_count"]
    ALPHA = 1.0

    def __init__(self):
        self.weights = None
        self.bias = 0.0
        self.feature_means = {}
        self.feature_stds = {}
        self.target_mean = 0.0
        self.n_samples = 0
        self.calibrated = False

    def _extract_row(self, row):
        x = [_safe_float(row.get(f, "nan"), 0.0) for f in self.FEATURES]
        y = _safe_float(row.get("slice_embb_latency_ms", "nan"), float("nan"))
        return x, y

    def calibrate(self, rows):
        """Ajustement de Ridge par gradient descendant simple."""
        valid = []
        for row in rows:
            x, y = self._extract_row(row)
            if not math.isnan(y) and all(not math.isnan(v) for v in x):
                valid.append((x, y))
        self.n_samples = len(valid)
        if self.n_samples < 3:
            # Pas assez de données → modèle trivial (moyenne)
            ys = [v[1] for v in valid] if valid else [0.05]
            self.target_mean = _mean(ys)
            self.weights = [0.0] * len(self.FEATURES)
            self.bias = self.target_mean
            self.calibrated = True
            return

        # Normalisation des features
        n_feat = len(self.FEATURES)
        for i, f in enumerate(self.FEATURES):
            vals = [row[0][i] for row in valid]
            self.feature_means[f] = _mean(vals)
            self.feature_stds[f] = _std(vals)
        self.target_mean = _mean([row[1] for row in valid])

        # Normaliser
        X = []
        Y = []
        for x, y in valid:
            xn = [(x[i] - self.feature_means[self.FEATURES[i]]) / self.feature_stds[self.FEATURES[i]]
                  for i in range(n_feat)]
            X.append(xn)
            Y.append(y - self.target_mean)

        # Gradient descendant Ridge
        w = [0.0] * n_feat
        lr = 0.01
        for _ in range(2000):
            # Gradient MSE + Ridge
            grad = [0.0] * n_feat
            for xi, yi in zip(X, Y):
                pred = sum(w[j] * xi[j] for j in range(n_feat))
                err = pred - yi
                for j in range(n_feat):
                    grad[j] += err * xi[j] / len(X)
            for j in range(n_feat):
                grad[j] += self.ALPHA * w[j] / len(X)
                w[j] -= lr * grad[j]
        self.weights = w
        self.bias = self.target_mean
        self.calibrated = True

    def predict(self, cpu_vmcp: float, cpu_vmran: float, cpu_vmupf: float,
                ue_count: float, handover_count: float) -> dict:
        if not self.calibrated or self.weights is None:
            return {"predicted_latency_ridge_ms": self.target_mean,
                    "ridge_confidence": "low"}
        x_raw = [cpu_vmcp, cpu_vmran, cpu_vmupf, ue_count, handover_count]
        x_norm = [(x_raw[i] - self.feature_means.get(self.FEATURES[i], 0.0)) /
                   max(self.feature_stds.get(self.FEATURES[i], 1.0), 1e-9)
                   for i in range(len(self.FEATURES))]
        pred = sum(self.weights[j] * x_norm[j] for j in range(len(self.FEATURES))) + self.bias
        pred = max(pred, 0.001)
        confidence = "high" if self.n_samples >= 10 else ("medium" if self.n_samples >= 5 else "low")
        return {"predicted_latency_ridge_ms": round(pred, 4),
                "ridge_confidence": confidence,
                "n_training_samples": self.n_samples}

# ─── Digital Twin combiné ─────────────────────────────────────────────────────
class DigitalTwin:
    def __init__(self, csv_path=METRICS_CSV):
        self.csv_path = csv_path
        self.mm1 = MM1Model()
        self.ridge = RidgeModel()
        self._calibration_mtime = 0.0
        self._calibrated_at = None
        self.calibrate()

    def calibrate(self):
        rows = load_metrics(self.csv_path)
        self.mm1.calibrate(rows)
        self.ridge.calibrate(rows)
        self._calibrated_at = datetime.now(timezone.utc).isoformat()
        self._calibration_mtime = os.path.getmtime(self.csv_path) if os.path.exists(self.csv_path) else 0.0
        return len(rows)

    def _auto_recalibrate(self):
        if os.path.exists(self.csv_path):
            mtime = os.path.getmtime(self.csv_path)
            if mtime > self._calibration_mtime:
                self.calibrate()

    def predict(self, ue_count=0, traffic_mbps=0.0, cpu_upf_pct=2.0,
                cpu_cp_pct=5.0, cpu_ran_pct=1.0, handover_count=0) -> dict:
        self._auto_recalibrate()
        mm1_out = self.mm1.predict(ue_count, traffic_mbps, cpu_upf_pct)
        ridge_out = self.ridge.predict(cpu_cp_pct, cpu_ran_pct, cpu_upf_pct, ue_count, handover_count)
        mm1_lat = mm1_out["predicted_latency_mm1_ms"]
        ridge_lat = ridge_out["predicted_latency_ridge_ms"]
        # Combinaison pondérée : Ridge si bien calibré, sinon M/M1
        if ridge_out.get("ridge_confidence") == "high":
            w_ridge, w_mm1 = 0.7, 0.3
        elif ridge_out.get("ridge_confidence") == "medium":
            w_ridge, w_mm1 = 0.5, 0.5
        else:
            w_ridge, w_mm1 = 0.2, 0.8
        combined = w_ridge * ridge_lat + w_mm1 * mm1_lat
        # Prédictions SLA secondaires
        pred_loss_pct = max(0.0, (cpu_upf_pct / 100.0) * 2.0)
        pred_cpu_upf_pct = cpu_upf_pct * (1 + ue_count * 0.02)
        result = {
            "predicted_latency_mm1_ms": mm1_lat,
            "predicted_latency_ridge_ms": ridge_lat,
            "predicted_latency_combined_ms": round(combined, 4),
            "predicted_loss_pct": round(pred_loss_pct, 4),
            "predicted_cpu_upf_pct": round(pred_cpu_upf_pct, 2),
            "queue_stable": mm1_out["queue_stable"],
            "rho": mm1_out["rho"],
            "ridge_confidence": ridge_out.get("ridge_confidence", "low"),
            "n_training_samples": ridge_out.get("n_training_samples", 0),
            "sla_violations": self.check_sla(combined, pred_loss_pct, pred_cpu_upf_pct),
            "data_sources": {
                "mm1": "analytical_model",
                "ridge": f"calibrated_on_{self.ridge.n_samples}_real_samples",
                "latency_base_ms": self.mm1.latency_base_ms,
            },
            "model_version": MODEL_VERSION,
            "calibrated_at": self._calibrated_at,
        }
        return result

    def check_sla(self, latency_ms: float, loss_pct: float, cpu_upf_pct: float) -> list:
        violations = []
        if latency_ms > SLA["embb_latency_max_ms"]:
            violations.append(f"SLA_VIOLATION: eMBB latency {latency_ms:.2f}ms > {SLA['embb_latency_max_ms']}ms")
        if latency_ms > SLA["urllc_latency_max_ms"]:
            violations.append(f"SLA_VIOLATION: URLLC latency {latency_ms:.2f}ms > {SLA['urllc_latency_max_ms']}ms")
        if loss_pct > SLA["loss_max_pct"]:
            violations.append(f"SLA_VIOLATION: Loss {loss_pct:.2f}% > {SLA['loss_max_pct']}%")
        if cpu_upf_pct > SLA["cpu_upf_max_pct"]:
            violations.append(f"SLA_VIOLATION: CPU UPF {cpu_upf_pct:.1f}% > {SLA['cpu_upf_max_pct']}%")
        return violations

# ─── Main : Test avec 3 scénarios de référence ───────────────────────────────
if __name__ == "__main__":
    dt = DigitalTwin()
    n = dt.ridge.n_samples
    print(f"\n{'='*70}")
    print(f"  AT20 Digital Twin — Modèle Hybride M/M1 + Ridge")
    print(f"  Calibré sur {n} échantillons réels | {dt._calibrated_at[:19]}")
    print(f"  Latence de base mesurée : {dt.mm1.latency_base_ms:.4f} ms")
    print(f"{'='*70}\n")
    scenarios = [
        {"name": "Baseline (aucun UE)",      "ue_count": 0,  "traffic_mbps": 0,   "cpu_upf_pct": 2,  "cpu_cp_pct": 5,  "cpu_ran_pct": 1},
        {"name": "eMBB chargé (5 UE)",       "ue_count": 5,  "traffic_mbps": 50,  "cpu_upf_pct": 40, "cpu_cp_pct": 30, "cpu_ran_pct": 20},
        {"name": "Critique (20 UE, 85% CPU)","ue_count": 20, "traffic_mbps": 200, "cpu_upf_pct": 85, "cpu_cp_pct": 70, "cpu_ran_pct": 50},
    ]
    for s in scenarios:
        name = s.pop("name")
        res = dt.predict(**s)
        print(f"  Scénario : {name}")
        print(f"    M/M1   : {res['predicted_latency_mm1_ms']:.4f} ms  (rho={res['rho']:.3f}, stable={res['queue_stable']})")
        print(f"    Ridge  : {res['predicted_latency_ridge_ms']:.4f} ms  (confiance={res['ridge_confidence']}, N={res['n_training_samples']})")
        print(f"    Combiné: {res['predicted_latency_combined_ms']:.4f} ms")
        print(f"    Perte prédite : {res['predicted_loss_pct']:.2f}%  |  CPU UPF prédit : {res['predicted_cpu_upf_pct']:.1f}%")
        viols = res["sla_violations"]
        if viols:
            for v in viols:
                print(f"    ⚠️  {v}")
        else:
            print(f"    ✅ Aucune violation SLA")
        print()
    print(f"  Sources M/M1 : {res['data_sources']['mm1']}")
    print(f"  Sources Ridge: {res['data_sources']['ridge']}")
    print(f"{'='*70}")
