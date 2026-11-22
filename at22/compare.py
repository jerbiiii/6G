"""AT22 - Comparaison classique vs quantique simule"""
import json, csv, time, sys
sys.path.insert(0, '/home/ubuntu/at22')
from problem import SLICES, LEVELS, B_TOTAL
from classical_solver import greedy_solve, brute_force_solve
from qaoa_simulator import qaoa_solve

def run_comparison(n_runs=3):
    results = []
    for run in range(1, n_runs+1):
        print(f"\n--- Run {run}/{n_runs} ---")
        g = greedy_solve()
        b = brute_force_solve()
        q = qaoa_solve(n_restarts=3)
        gap_greedy = round((b['utility_total']-g['utility_total'])/b['utility_total']*100, 2)
        gap_qaoa   = round((b['utility_total']-q['utility_total'])/b['utility_total']*100, 2)
        row = {
            'run': run,
            'greedy_utility':     g['utility_total'],
            'greedy_bw':          g['bandwidth_used'],
            'greedy_time_ms':     g['time_ms'],
            'brute_utility':      b['utility_total'],
            'brute_bw':           b['bandwidth_used'],
            'brute_time_ms':      b['time_ms'],
            'qaoa_utility':       q['utility_total'],
            'qaoa_bw':            q['bandwidth_used'],
            'qaoa_time_ms':       q['time_ms'],
            'qaoa_gamma':         q['gamma_opt'],
            'qaoa_beta':          q['beta_opt'],
            'gap_greedy_pct':     gap_greedy,
            'gap_qaoa_pct':       gap_qaoa,
            'qaoa_matches_optimal': q['utility_total'] >= b['utility_total'],
        }
        results.append(row)
        print(f"  Glouton  : utility={g['utility_total']}, bw={g['bandwidth_used']}Mbps, t={g['time_ms']}ms")
        print(f"  Optimal  : utility={b['utility_total']}, bw={b['bandwidth_used']}Mbps, t={b['time_ms']}ms")
        print(f"  QAOA     : utility={q['utility_total']}, bw={q['bandwidth_used']}Mbps, t={q['time_ms']}ms")
        print(f"  Gap Greedy/Opt: {gap_greedy}% | Gap QAOA/Opt: {gap_qaoa}%")

    # Sauvegarder CSV
    with open('/home/ubuntu/at22/data/comparison.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=results[0].keys())
        w.writeheader(); w.writerows(results)
    print(f"\nCSV sauvegarde: /home/ubuntu/at22/data/comparison.csv")
    return results

if __name__ == '__main__':
    results = run_comparison(n_runs=3)
    # Resume
    import statistics
    q_utils = [r['qaoa_utility'] for r in results]
    g_utils = [r['greedy_utility'] for r in results]
    b_utils = [r['brute_utility'] for r in results]
    q_times = [r['qaoa_time_ms'] for r in results]
    n_opt   = sum(1 for r in results if r['qaoa_matches_optimal'])
    print(f"\n=== RESUME {len(results)} runs ===")
    print(f"Glouton  utility moy : {round(statistics.mean(g_utils),4)}")
    print(f"Optimal  utility moy : {round(statistics.mean(b_utils),4)}")
    print(f"QAOA     utility moy : {round(statistics.mean(q_utils),4)}")
    print(f"QAOA temps moy (ms)  : {round(statistics.mean(q_times),1)}")
    print(f"QAOA = optimal       : {n_opt}/{len(results)} runs")
