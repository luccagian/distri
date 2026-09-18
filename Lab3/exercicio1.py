import sys
import random
import time
import threading
from mpi4py import MPI

def mult_matriz_seq(A, B, N):
    C = [[0] * N for _ in range(N)]
    inicio = time.time()
    for i in range(N):
        for j in range(N):
            for k in range(N):
                C[i][j] += A[i][k] * B[k][j]
    fim = time.time()
    return (fim - inicio) * 1000

def mult_matriz_threads(A, B, N, num_threads=4):
    C = [[0] * N for _ in range(N)]
    
    def worker(inicio, fim):
        for i in range(inicio, fim):
            for j in range(N):
                for k in range(N):
                    C[i][j] += A[i][k] * B[k][j]

    threads = []
    linhas_por_thread = N // num_threads
    inicio = time.time()
    for t in range(num_threads):
        ini = t * linhas_por_thread
        fim_t = N if t == num_threads - 1 else (t + 1) * linhas_por_thread
        th = threading.Thread(target=worker, args=(ini, fim_t))
        threads.append(th)
        th.start()

    for th in threads:
        th.join()
    fim = time.time()
    return (fim - inicio) * 1000

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Aceita parâmetro do terminal ou usa a lista completa por padrão
    if len(sys.argv) > 1:
        DUMMY_N = [int(sys.argv[1])]
    else:
        DUMMY_N = [300, 600, 1000]

    for N in DUMMY_N:
        if rank == 0:
            A = [[random.random() for _ in range(N)] for _ in range(N)]
            B = [[random.random() for _ in range(N)] for _ in range(N)]
        else:
            A = None
            B = None

        # Difusão das matrizes para todos os nós
        t_start = time.time()
        A = comm.bcast(A, root=0)
        B = comm.bcast(B, root=0)

        # Divisão das linhas entre os processos
        linhas_por_rank = N // size
        ini_idx = rank * linhas_por_rank
        fim_idx = N if rank == size - 1 else (rank + 1) * linhas_por_rank

        sub_C = []
        for i in range(ini_idx, fim_idx):
            linha = [0] * N
            for j in range(N):
                for k in range(N):
                    linha[j] += A[i][k] * B[k][j]
            sub_C.append(linha)

        # Agregação no processo root
        coletado = comm.gather(sub_C, root=0)
        t_end = time.time()
        t_mpi = (t_end - t_start) * 1000

        if rank == 0:
            C_final = []
            for bloco in coletado:
                C_final.extend(bloco)
            
            t_seq = mult_matriz_seq(A, B, N)
            t_th = mult_matriz_threads(A, B, N, num_threads=4)

            print(f"=== Dimensão N = {N} ===")
            print(f"Tempo Sequencial: {t_seq:.2f} ms")
            print(f"Tempo Multithreaded: {t_th:.2f} ms")
            print(f"Tempo Distribuído MPI: {t_mpi:.2f} ms\n")

if __name__ == "__main__":
    main()