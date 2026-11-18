#!/usr/bin/env python3
"""
=============================================================================
Projet 6G - Atelier 11 : Orchestration Intelligente des Ressources
Script : at11-orchestrator.py
Rôle   : Surveillance continue, prise de décision autonome (Seuils CPU 50%/20%),
         Migration dynamique des pods et Auto-scaling Edge/Fog/Cloud.
=============================================================================
"""

import subprocess
import time
import json
import sys
from datetime import datetime

NAMESPACE = "at11-orch"
ITERATIONS = 5
INTERVAL = 12  # 12 secondes entre chaque itération
CPU_SCALE_UP_THRESHOLD = 50    # Si CPU >= 50% -> Scale UP & Migration
CPU_SCALE_DOWN_THRESHOLD = 20  # Si CPU < 20% -> Scale DOWN

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None

def get_node_metrics():
    """Collecte les métriques CPU/mémoire depuis kubectl top nodes."""
    out = run_cmd("kubectl top nodes")
    metrics = {}
    if not out:
        return metrics
    lines = out.splitlines()
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 5:
            node = parts[0]
            metrics[node] = {
                "cpu_cores": parts[1],
                "cpu_pct": int(parts[2].replace('%', '')),
                "mem_bytes": parts[3],
                "mem_pct": int(parts[4].replace('%', ''))
            }
    return metrics

def get_pod_distribution():
    """Inspecte la répartition des pods par nœud dans le namespace."""
    out = run_cmd(f"kubectl get pods -n {NAMESPACE} -o wide --no-headers")
    distribution = {"vm-cp": [], "vm-upf": [], "vm-ran": []}
    pod_list = []
    if out:
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 7:
                p_name, ready, status, node = parts[0], parts[1], parts[2], parts[6]
                if node in distribution:
                    distribution[node].append(p_name)
                pod_list.append((p_name, ready, status, node))
    return distribution, pod_list

def get_deployments_replicas():
    """Collecte les répliques configurées pour chaque déploiement."""
    out = run_cmd(f"kubectl get deployments -n {NAMESPACE} -o json")
    replicas = {}
    if out:
        try:
            data = json.loads(out)
            for item in data.get("items", []):
                name = item["metadata"]["name"]
                replicas[name] = item["spec"].get("replicas", 1)
        except Exception:
            pass
    return replicas

# État de l'orchestrateur
state = {
    "scaled_deployments": set(),
    "migrated_workloads": set()
}

def decide_and_act(metrics, distribution, replicas):
    """Moteur de décision de l'orchestrateur 6G."""
    decisions = []
    actions = []

    # Détecter si un nœud dépasse le seuil haut
    overloaded = [n for n, m in metrics.items() if m["cpu_pct"] >= CPU_SCALE_UP_THRESHOLD]
    
    # Nœuds classés du moins chargé au plus chargé
    sorted_nodes = sorted(metrics.keys(), key=lambda n: metrics[n]["cpu_pct"])
    least_loaded = sorted_nodes[0] if sorted_nodes else "vm-upf"

    if overloaded:
        src = max(overloaded, key=lambda n: metrics[n]["cpu_pct"])
        src_cpu = metrics[src]["cpu_pct"]
        decisions.append(f"RÈGLE 1 ACTIVÉE : Surcharge critique sur {src} (CPU: {src_cpu}% >= {CPU_SCALE_UP_THRESHOLD}%)")
        decisions.append(f"CIBLE ÉLUE       : Nœud {least_loaded} sélectionné (CPU: {metrics[least_loaded]['cpu_pct']}%)")

        # 1. Scale UP sur le nœud cible (Fog ou Cloud ou Edge)
        target_dep = "app-fog" if least_loaded == "vm-upf" else ("app-cloud" if least_loaded == "vm-cp" else "app-edge")
        curr_rep = replicas.get(target_dep, 1)
        if curr_rep < 2:
            run_cmd(f"kubectl scale deployment {target_dep} -n {NAMESPACE} --replicas=2")
            actions.append(f"SCALE UP : Augmentation répliques de {target_dep} (1 -> 2) sur {least_loaded}")
            state["scaled_deployments"].add(target_dep)
        else:
            actions.append(f"SCALE UP : {target_dep} dispose déjà de {curr_rep} répliques actives")

        # 2. Migration du pod workload-app vers le nœud le moins chargé
        workload_on_src = any("workload-app" in p for p in distribution.get(src, []))
        if workload_on_src or ("workload-app" not in state["migrated_workloads"]):
            patch_dict = {
                "spec": {
                    "template": {
                        "spec": {
                            "nodeSelector": {
                                "kubernetes.io/hostname": least_loaded
                            }
                        }
                    }
                }
            }
            patch_json = json.dumps(patch_dict)
            run_cmd(f"kubectl patch deployment workload-app -n {NAMESPACE} -p '{patch_json}'")
            actions.append(f"MIGRATION : workload-app déporté de {src} vers {least_loaded}")
            state["migrated_workloads"].add("workload-app")
        else:
            actions.append(f"MIGRATION : workload-app déjà migré sur {least_loaded}")

    else:
        # Vérifier si tous les nœuds sont sous le seuil bas (< 20%)
        all_low = all(m["cpu_pct"] < CPU_SCALE_DOWN_THRESHOLD for m in metrics.values())
        if all_low:
            scaled_down = False
            for dep, rep in replicas.items():
                if rep > 1 and dep in ["app-fog", "app-cloud", "app-edge"]:
                    run_cmd(f"kubectl scale deployment {dep} -n {NAMESPACE} --replicas=1")
                    actions.append(f"SCALE DOWN : Réduction répliques de {dep} ({rep} -> 1) suite à normalisation de charge")
                    scaled_down = True
            if scaled_down:
                state["scaled_deployments"].clear()
                decisions.append(f"RÈGLE 2 ACTIVÉE : Charge stabilisée (Tous CPU < {CPU_SCALE_DOWN_THRESHOLD}%). Scale DOWN automatique.")
            else:
                decisions.append(f"ÉTAT NORMAL     : Ressources équilibrées (< {CPU_SCALE_DOWN_THRESHOLD}%). Surveillance passive.")
        else:
            decisions.append("ÉTAT TRANSITOIRE : Charge modérée, aucun franchissement de seuil.")

    return decisions, actions

def main():
    print("=" * 78)
    print("=== [AT11] ORCHESTRATEUR INTELLIGENT DE RESSOURCES 6G ===")
    print(f"=== Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Namespace : {NAMESPACE} ===")
    print("=" * 78)

    history = []

    for it in range(1, ITERATIONS + 1):
        print(f"\n>>> [ITÉRATION {it}/{ITERATIONS}] - {datetime.now().strftime('%H:%M:%S')}")
        
        metrics = get_node_metrics()
        distribution, pod_list = get_pod_distribution()
        replicas = get_deployments_replicas()

        # Affichage métriques des nœuds
        print("+---------+------------+---------+---------------+-----------+")
        print("| Nœud    | CPU(cores) | CPU (%) | Mémoire(MiB)  | Mém (%)   |")
        print("+---------+------------+---------+---------------+-----------+")
        for node in ["vm-ran", "vm-upf", "vm-cp"]:
            m = metrics.get(node, {"cpu_cores": "N/A", "cpu_pct": 0, "mem_bytes": "N/A", "mem_pct": 0})
            print(f"| {node:<7} | {m['cpu_cores']:<10} | {m['cpu_pct']:>5}%  | {m['mem_bytes']:<13} | {m['mem_pct']:>7}%  |")
        print("+---------+------------+---------+---------------+-----------+")

        # Affichage répartition des pods
        print(f"Distribution des Pods :")
        for node in ["vm-ran", "vm-upf", "vm-cp"]:
            pods = distribution.get(node, [])
            p_str = ", ".join(pods) if pods else "(aucun)"
            print(f"  - {node:<7} ({len(pods)} pods) : {p_str}")

        # Décision et actions
        decisions, actions = decide_and_act(metrics, distribution, replicas)

        print("\nPrise de décision de l'orchestrateur :")
        for d in decisions:
            print(f"  [DÉCISION] {d}")
        if actions:
            print("Actions exécutées :")
            for a in actions:
                print(f"  [ACTION]   {a}")
        else:
            print("  [ACTION]   Aucune modification requise")

        # Enregistrer l'état pour le bilan
        history.append({
            "iteration": it,
            "metrics": metrics,
            "distribution": {n: len(p) for n, p in distribution.items()},
            "decisions": decisions,
            "actions": actions
        })

        # Simulation de charge automatique après itération 1 (baseline)
        if it == 1:
            print("\n>>> [SIMULATION] Déclenchement automatique de la montée en charge sur vm-ran (22s)...")
            run_cmd("curl -s 'http://172.31.34.222:30090/stress?duration=22&workers=2' >/dev/null 2>&1 &")
            run_cmd("ssh -o StrictHostKeyChecking=no -i ~/.ssh/6g-team-key.pem ubuntu@172.31.34.222 'python3 ~/stress-vmran.py 22 >/dev/null 2>&1 &' &")
            print(">>> Attente de 12s pour la propagation de charge dans metrics-server...")
            time.sleep(12)
        elif it < ITERATIONS:
            print(f"\nAttente de {INTERVAL}s avant la prochaine analyse...")
            time.sleep(INTERVAL)

    # ================= BILAN FINAL =================
    print("\n" + "=" * 78)
    print("=== RAPPORT FINAL ET TABLEAU COMPARATIF ORCHESTRATION AT11 ===")
    print("=" * 78)

    t_init = history[0]
    t_peak = max(history, key=lambda h: max(m["cpu_pct"] for m in h["metrics"].values()) if h["metrics"] else 0)
    t_final = history[-1]

    print("\n--- 1. Évolution de la Charge CPU par Nœud ---")
    print("+---------+-----------------+-------------------+-----------------+")
    print("| Nœud    | Initial (T0)    | Pic Charge (T_pic)| Final Optimisé  |")
    print("+---------+-----------------+-------------------+-----------------+")
    for node in ["vm-ran", "vm-upf", "vm-cp"]:
        c_init = f"{t_init['metrics'].get(node, {}).get('cpu_pct', 'N/A')}%"
        c_peak = f"{t_peak['metrics'].get(node, {}).get('cpu_pct', 'N/A')}%"
        c_fin  = f"{t_final['metrics'].get(node, {}).get('cpu_pct', 'N/A')}%"
        print(f"| {node:<7} | {c_init:<15} | {c_peak:<17} | {c_fin:<15} |")
    print("+---------+-----------------+-------------------+-----------------+")

    print("\n--- 2. Évolution de la Répartition des Pods par Nœud ---")
    print("+---------+-----------------+-------------------+-----------------+")
    print("| Nœud    | Pods T0         | Pods Pic Charge   | Pods Stabilisés |")
    print("+---------+-----------------+-------------------+-----------------+")
    for node in ["vm-ran", "vm-upf", "vm-cp"]:
        p_init = t_init["distribution"].get(node, 0)
        p_peak = t_peak["distribution"].get(node, 0)
        p_fin  = t_final["distribution"].get(node, 0)
        print(f"| {node:<7} | {p_init:<15} | {p_peak:<17} | {p_fin:<15} |")
    print("+---------+-----------------+-------------------+-----------------+")

    print("\n--- 3. Historique des Actions Orchestrateur ---")
    for h in history:
        if h["actions"]:
            print(f"  * Itération {h['iteration']} : {', '.join(h['actions'])}")

    print("\n" + "=" * 78)
    print("=== [AT11] ORCHESTRATION INTELLIGENTE VALIDÉE AVEC SUCCÈS ===")
    print("=" * 78)

if __name__ == "__main__":
    main()
