import time
import multiprocessing
import sys

def burn(duration):
    t_end = time.time() + duration
    while time.time() < t_end:
        _ = sum(i * i for i in range(10000))

if __name__ == "__main__":
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    print(f"[STRESS] Lancement de la charge CPU sur vm-ran pendant {duration} secondes...")
    procs = []
    for _ in range(2):
        p = multiprocessing.Process(target=burn, args=(duration,))
        p.start()
        procs.append(p)
    for p in procs:
        p.join()
    print("[STRESS] Fin de la charge CPU sur vm-ran.")
