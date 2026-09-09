# Relatório

## 1. Resumo da Solução
Desenvolvimento de uma aplicação paralela com `mpi4py` para analisar 100.000 logs HTTP. O processo principal (Rank 0) gera os dados e usa `comm.scatter` para dividir o trabalho igualmente entre 4 processos. Cada processo analisa 25.000 linhas, e o total é somado ao final via `comm.reduce`.

## 2. Principal Desafio e Solução
Durante a execução no **Codespaces**, o OpenMPI bloqueou a criação de 4 processos porque a máquina virtual do ambiente possui menos de 4 núcleos físicos de CPU disponíveis.

* **Erro:** Limite de slots do sistema excedidos (`not enough slots available`).
* **Solução:** Foi necessário utilizar a flag `--oversubscribe` no comando `mpirun`. Essa flag força o OpenMPI a alocar múltiplos processos virtuais no mesmo núcleo físico, permitindo a execução paralela dos 4 processos e a correta distribuição dos dados.

## 3. Conclusão
A implementação dividiu o processamento com sucesso (25.000 logs/processo), demonstrando a eficiência da comunicação coletiva no MPI mesmo em ambientes virtualizados com limitação de hardware.