"""AT22 - Solveur classique : glouton + brute force"""
import time, json, itertools, sys
sys.path.insert(0, '/home/ubuntu/at22')
from problem import SLICES, LEVELS, B_TOTAL, SLA_MIN, UTILITY, N_L, evaluate_solution

def greedy_solve():
    t0 = time.perf_counter()
    alloc = {}
    # Minimum SLA pour chaque slice
    for s in SLICES:
        k = next((k for k,v in enumerate(LEVELS) if v >= SLA_MIN[s]), N_L-1)
        alloc[s] = k
    # Allouer surplus par utilite marginale maximale
    remaining = B_TOTAL - sum(LEVELS[alloc[s]] for s in SLICES)
    improved = True
    while improved and remaining >= min(LEVELS):
        improved = False
        best_gain, best_s, best_k = 0, None, None
        for s in SLICES:
            curr_k = alloc[s]
            for k in range(curr_k+1, N_L):
                extra = LEVELS[k] - LEVELS[curr_k]
                if extra <= remaining:
                    gain = UTILITY[s][k] - UTILITY[s][curr_k]
                    if gain > best_gain:
                        best_gain, best_s, best_k = gain, s, k
        if best_s:
            remaining -= LEVELS[best_k] - LEVELS[alloc[best_s]]
            alloc[best_s] = best_k
            improved = True
    t1 = time.perf_counter()
    x_bin = [0]*(len(SLICES)*N_L)
    for i,s in enumerate(SLICES):
        x_bin[i*N_L + alloc[s]] = 1
    res = evaluate_solution(x_bin)
    res['solver'] = 'greedy_classical'
    res['time_ms'] = round((t1-t0)*1000, 4)
    return res

def brute_force_solve():
    t0 = time.perf_counter()
    best, best_u = None, -1
    n_explored = 0
    for combo in itertools.product(range(N_L), repeat=len(SLICES)):
        x_bin = [0]*(len(SLICES)*N_L)
        for i,k in enumerate(combo):
            x_bin[i*N_L+k] = 1
        res = evaluate_solution(x_bin)
        n_explored += 1
        if res['feasible'] and res['utility_total'] > best_u:
            best_u = res['utility_total']
            best = res
    t1 = time.perf_counter()
    best['solver'] = 'brute_force_optimal'
    best['time_ms'] = round((t1-t0)*1000, 4)
    best['n_explored'] = n_explored
    return best

if __name__ == '__main__':
    print("=== Solveur Glouton ===")
    g = greedy_solve()
    print(json.dumps(g, indent=2))
    print("\n=== Brute Force Optimal ===")
    b = brute_force_solve()
    print(json.dumps(b, indent=2))
    print(f"\nGlouton utility   : {g['utility_total']}")
    print(f"Optimal utility   : {b['utility_total']}")
    gap = round((b['utility_total']-g['utility_total'])/b['utility_total']*100, 2)
    print(f"Gap glouton/opt   : {gap}%")
