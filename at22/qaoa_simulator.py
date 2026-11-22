"""
AT22 - Simulateur QAOA (Quantum Approximate Optimization Algorithm)
Implementation NumPy pure — 9 qubits, espace Hilbert 512 etats.
p=1 couche, optimisation angles gamma/beta via scipy.minimize (COBYLA).
"""
import numpy as np
from scipy.optimize import minimize
import time, json, sys
sys.path.insert(0, '/home/ubuntu/at22')
from problem import SLICES, LEVELS, N_S, N_L, qubo_matrix, evaluate_solution

N_QUBITS = N_S * N_L   # 9
DIM      = 2**N_QUBITS  # 512

def bits_of(state_idx):
    return np.array([(state_idx >> b) & 1 for b in range(N_QUBITS)], dtype=float)

# Precalcul des energies QUBO pour chaque etat de base
def precompute_energies(Q):
    energies = np.zeros(DIM)
    for i in range(DIM):
        x = bits_of(i)
        energies[i] = x @ Q @ x
    return energies

def apply_phase_separator(state, energies, gamma):
    """U_C(gamma) : dephasage par l'energie QUBO."""
    return state * np.exp(-1j * gamma * energies)

def apply_mixer(state, beta):
    """U_B(beta) : rotation X sur chaque qubit."""
    cos_b = np.cos(beta)
    sin_b = np.sin(beta)
    for q in range(N_QUBITS):
        mask = 1 << q
        new_state = np.zeros(DIM, dtype=complex)
        for i in range(DIM):
            flipped = i ^ mask
            new_state[i] += cos_b * state[i] + 1j * sin_b * state[flipped]
        state = new_state
    return state

def qaoa_circuit(gamma, beta, energies):
    """Circuit QAOA p=1 : |+>^n -> U_C -> U_B -> mesure."""
    state = np.ones(DIM, dtype=complex) / np.sqrt(DIM)
    state = apply_phase_separator(state, energies, gamma)
    state = apply_mixer(state, beta)
    return state

def expectation_value(params, energies):
    gamma, beta = params
    state = qaoa_circuit(gamma, beta, energies)
    probs = np.abs(state)**2
    return float(np.dot(probs, energies))

def qaoa_solve(n_restarts=5):
    t0 = time.perf_counter()
    Q = qubo_matrix(penalty=10.0)
    energies = precompute_energies(Q)

    # Optimisation des angles
    best_energy = np.inf
    best_params = None
    rng = np.random.default_rng(42)
    for _ in range(n_restarts):
        g0 = rng.uniform(0, np.pi)
        b0 = rng.uniform(0, np.pi/2)
        res = minimize(expectation_value, x0=[g0, b0], args=(energies,),
                       method='COBYLA', options={'maxiter':300, 'rhobeg':0.5})
        if res.fun < best_energy:
            best_energy = res.fun
            best_params = res.x

    gamma_opt, beta_opt = best_params
    state_opt = qaoa_circuit(gamma_opt, beta_opt, energies)
    probs = np.abs(state_opt)**2
    probs /= probs.sum()

    # Echantillonnage 2000 fois
    rng2 = np.random.default_rng(123)
    samples = rng2.choice(DIM, size=2000, p=probs)

    # Meilleure solution faisable parmi les echantillons
    best_sol = None; best_u = -1
    seen = set()
    for s_idx in samples:
        if s_idx in seen: continue
        seen.add(s_idx)
        bits = [(s_idx >> b) & 1 for b in range(N_QUBITS)]
        res = evaluate_solution(bits)
        if res['feasible'] and res['utility_total'] > best_u:
            best_u = res['utility_total']
            best_sol = dict(res)

    # Fallback : top-50 probabilites si aucune faisable
    if best_sol is None:
        top_idx = np.argsort(probs)[::-1][:50]
        for s_idx in top_idx:
            bits = [(s_idx >> b) & 1 for b in range(N_QUBITS)]
            res = evaluate_solution(bits)
            if res['utility_total'] > best_u:
                best_u = res['utility_total']; best_sol = dict(res)

    t1 = time.perf_counter()
    best_sol['solver']       = 'QAOA_numpy_simulated'
    best_sol['n_qubits']     = N_QUBITS
    best_sol['hilbert_dim']  = DIM
    best_sol['p_layers']     = 1
    best_sol['n_restarts']   = n_restarts
    best_sol['gamma_opt']    = round(float(gamma_opt), 4)
    best_sol['beta_opt']     = round(float(beta_opt), 4)
    best_sol['qaoa_energy']  = round(float(best_energy), 4)
    best_sol['time_ms']      = round((t1-t0)*1000, 1)
    return best_sol

if __name__ == '__main__':
    print(f"QAOA simulateur : {N_QUBITS} qubits, dim Hilbert = {DIM}")
    result = qaoa_solve(n_restarts=5)
    print(json.dumps(result, indent=2))
