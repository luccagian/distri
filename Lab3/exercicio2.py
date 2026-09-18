import random
import time
from mpi4py import MPI

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    N_TOTAL = 10_000_000
    N_LOCAL = N_TOTAL // size

    comm.Barrier()
    inicio = time.time()

    dentro_local = 0
    for _ in range(N_LOCAL):
        x = random.random()
        y = random.random()
        if x*x + y*y <= 1.0:
            dentro_local += 1

    dentro_total = comm.reduce(dentro_local, op=MPI.SUM, root=0)
    fim = time.time()

    if rank == 0:
        pi_estimado = 4.0 * dentro_total / N_TOTAL
        tempo_total = (fim - inicio) * 1000
        print("=== Estimativa de Pi (Monte Carlo) ===")
        print(f"Total de Pontos: {N_TOTAL}")
        print(f"Pontos no Círculo: {dentro_total}")
        print(f"Pi Estimado: {pi_estimado:.6f}")
        print(f"Tempo Distribuído MPI: {tempo_total:.2f} ms")

if __name__ == "__main__":
    main()