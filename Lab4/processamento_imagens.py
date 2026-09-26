import sys
import time
import random
import numpy as np
from mpi4py import MPI

# Etapa 1: Inicialização do Ambiente MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Declarando o tempo inicial
t_inicio = time.time()

# Etapa 2 & 3: Processo 0 gera a imagem sintética
if rank == 0:
    LINHAS = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    COLUNAS = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    
    if LINHAS % size != 0:
        LINHAS = ((LINHAS // size) + 1) * size

    # Geração da radiografia base com intensidades entre 30 e 90
    imagem_completa = np.random.randint(30, 90, size=(LINHAS, COLUNAS), dtype=np.uint8)
    
    # Injeção de foco de opacidade suspeita no pulmão direito (colunas à direita)
    imagem_completa[int(LINHAS*0.3):int(LINHAS*0.5), int(COLUNAS*0.6):int(COLUNAS*0.8)] = \
        np.random.randint(180, 245, size=(int(LINHAS*0.2), int(COLUNAS*0.2)), dtype=np.uint8)

    parametros = {
        'linhas': LINHAS, 'colunas': COLUNAS,
        'limiar_suspeito': 200, 'limiar_alto': 230, 'pct_critico': 5.0
    }
else:
    imagem_completa = None
    parametros = None

# Etapa 3: Difusão dos parâmetros via Broadcast
parametros = comm.bcast(parametros, root=0)

# Etapa 4: Sincronização Inicial
comm.Barrier()

# Etapa 5: Divisão e distribuição da imagem via Scatter
linhas_por_proc = parametros['linhas'] // size
bloco_local = np.empty((linhas_por_proc, parametros['colunas']), dtype=np.uint8)

if rank == 0:
    blocos_divididos = np.split(imagem_completa, size, axis=0)
else:
    blocos_divididos = None

comm.scatter(blocos_divididos, root=0)

# Etapa 6 & 7: Processamento e classificação local
total_local = bloco_local.size
soma_local = int(np.sum(bloco_local))
max_local = int(np.max(bloco_local))
col_meio = parametros['colunas'] // 2

esq_mask = bloco_local[:, :col_meio] > parametros['limiar_suspeito']
dir_mask = bloco_local[:, col_meio:] > parametros['limiar_suspeito']

suspeitos_esq = int(np.sum(esq_mask))
suspeitos_dir = int(np.sum(dir_mask))
suspeitos_local = suspeitos_esq + suspeitos_dir
altamente_suspeitos_local = int(np.sum(bloco_local > parametros['limiar_alto']))

pct_suspeito = (suspeitos_local / total_local) * 100.0
if pct_suspeito >= parametros['pct_critico']:
    classificacao_local = "CRÍTICA"
elif pct_suspeito >= 1.0:
    classificacao_local = "ATENÇÃO"
else:
    classificacao_local = "NORMAL"

# Etapa 8: Simulação de heterogeneidade de nós
if rank % 2 != 0:
    time.sleep(0.05 * rank)

# Etapa 9: Sincronização pré-consolidação
comm.Barrier()

# Etapa 10: Consolidação numérica com MPI_Reduce
total_pixels_global = comm.reduce(total_local, op=MPI.SUM, root=0)
soma_global = comm.reduce(soma_local, op=MPI.SUM, root=0)
max_global = comm.reduce(max_local, op=MPI.MAX, root=0)
suspeitos_global = comm.reduce(suspeitos_local, op=MPI.SUM, root=0)
altos_global = comm.reduce(altamente_suspeitos_local, op=MPI.SUM, root=0)
esq_global = comm.reduce(suspeitos_esq, op=MPI.SUM, root=0)
dir_global = comm.reduce(suspeitos_dir, op=MPI.SUM, root=0)

# Etapa 11: Coleta de relatórios via MPI_Gather
relatorio_local = {
    'rank': rank, 'linhas_inicio': rank * linhas_por_proc,
    'linhas_fim': (rank + 1) * linhas_por_proc, 'pixels': total_local,
    'suspeitos': suspeitos_local, 'classificacao': classificacao_local,
    'max_local': max_local
}
todos_relatorios = comm.gather(relatorio_local, root=0)

# Etapa 12: Relatório final emitido pelo processo 0
if rank == 0:
    t_total = (time.time() - t_inicio) * 1000.0
    media_intensidade = soma_global / total_pixels_global
    taxa_comprometida = (suspeitos_global / total_pixels_global) * 100.0
    
    print("\n" + "="*60, flush=True)
    print("      RELATÓRIO CONSOLIDADO DE TRIAGEM DISTRIBUÍDA", flush=True)
    print("="*60, flush=True)
    print(f"Dimensões do Exame      : {parametros['linhas']} x {parametros['colunas']} pixels", flush=True)
    print(f"Processos MPI Utilizados: {size}", flush=True)
    print(f"Tempo Total de Execução : {t_total:.2f} ms", flush=True)
    print(f"Intensidade Média Global: {media_intensidade:.2f} (Máxima: {max_global})", flush=True)
    print(f"Total de Pixels Suspeitos: {suspeitos_global} ({taxa_comprometida:.2f}%)", flush=True)
    print(f"  - Pulmão Esquerdo     : {esq_global} suspeitos", flush=True)
    print(f"  - Pulmão Direito      : {dir_global} suspeitos", flush=True)
    
    lado_critico = "Direito" if dir_global > esq_global else "Esquerdo" if esq_global > dir_global else "Equilibrado"
    print(f"Maior Concentração      : Pulmão {lado_critico}", flush=True)
    print("\n--- Auditoria por Processo (Faixas) ---", flush=True)
    for rel in todos_relatorios:
        print(f"Processo {rel['rank']:02d} | Linhas [{rel['linhas_inicio']:04d} - {rel['linhas_fim']:04d}] | "
              f"Suspeitos: {rel['suspeitos']:05d} | Máx: {rel['max_local']:03d} | Faixa: {rel['classificacao']}", flush=True)
    print("="*60 + "\n", flush=True)