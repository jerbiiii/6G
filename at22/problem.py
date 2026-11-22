"""AT22 - Probleme QUBO allocation ressources 6G
Slices : eMBB, URLLC, mMTC
Niveaux : [20, 30, 50] Mbps (3 niveaux => 9 qubits => 2^9=512 etats, QAOA rapide)
"""
import numpy as np

SLICES = ['eMBB', 'URLLC', 'mMTC']
LEVELS = [20, 30, 50]   # Mbps - 3 niveaux pour garder QAOA rapide
B_TOTAL = 100           # Budget total Mbps

# Utilite QoS de chaque slice a chaque niveau (0-1)
UTILITY = {
    'eMBB':  [0.3, 0.6, 1.0],   # veut beaucoup de BP
    'URLLC': [0.8, 1.0, 1.0],   # sature a 30 Mbps
    'mMTC':  [1.0, 1.0, 1.0],   # sature a 20 Mbps
}
SLA_MIN = {'eMBB': 30, 'URLLC': 20, 'mMTC': 20}

N_S = len(SLICES)
N_L = len(LEVELS)

def idx(i, k):
    return i * N_L + k

def qubo_matrix(penalty=10.0):
    """Matrice QUBO Q : minimiser x^T Q x"""
    n = N_S * N_L
    Q = np.zeros((n, n))
    # Objectif : minimiser -utility (termes diagonaux)
    for i, s in enumerate(SLICES):
        for k in range(N_L):
            Q[idx(i,k), idx(i,k)] -= UTILITY[s][k]
    # Contrainte : exactement 1 niveau par slice
    # penalty*(sum_k x_ik - 1)^2 => diag: penalty*(1-2)=-penalty, off-diag: 2*penalty
    for i in range(N_S):
        for k in range(N_L):
            Q[idx(i,k), idx(i,k)] += penalty * (1 - 2)
            for l in range(k+1, N_L):
                Q[idx(i,k), idx(i,l)] += 2 * penalty
    return Q

def evaluate_solution(x_bin):
    allocation = {}
    utility_total = 0.0
    bandwidth_used = 0.0
    sla_violations = []
    for i, s in enumerate(SLICES):
        chosen_k = next((k for k in range(N_L) if x_bin[i*N_L+k] == 1), -1)
        bw = LEVELS[chosen_k] if chosen_k >= 0 else 0
        u  = UTILITY[s][chosen_k] if chosen_k >= 0 else 0.0
        allocation[s] = {'bw_mbps': bw, 'utility': round(u,3)}
        utility_total += u
        bandwidth_used += bw
        if bw < SLA_MIN[s]:
            sla_violations.append(f"{s}: {bw}Mbps < SLA {SLA_MIN[s]}Mbps")
    return {
        'utility_total': round(utility_total, 4),
        'bandwidth_used': int(bandwidth_used),
        'sla_violations': sla_violations,
        'allocation': allocation,
        'feasible': len(sla_violations) == 0 and bandwidth_used <= B_TOTAL
    }

if __name__ == '__main__':
    import json
    print(f"Slices : {SLICES}")
    print(f"Niveaux : {LEVELS} Mbps | Budget : {B_TOTAL} Mbps")
    print(f"Variables QUBO : {N_S*N_L} | Espace Hilbert : 2^{N_S*N_L} = {2**(N_S*N_L)} etats")
    Q = qubo_matrix()
    print(f"Matrice QUBO : {Q.shape}")
    test = [0,1,0, 0,0,1, 1,0,0]  # eMBB=30, URLLC=50, mMTC=20
    res = evaluate_solution(test)
    print("Exemple evaluation :", json.dumps(res, indent=2))
