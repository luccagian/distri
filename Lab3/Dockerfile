FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    openmpi-bin \
    libopenmpi-dev \
    openssh-server \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Criação do diretório necessário para o daemon do SSH funcionar corretamente
RUN mkdir /var/run/sshd

RUN useradd -m -s /bin/bash mpiuser && \
    echo "mpiuser:mpiuser" | chpasswd

WORKDIR /home/mpiuser

USER mpiuser
RUN ssh-keygen -t rsa -N "" -f /home/mpiuser/.ssh/id_rsa && \
    cp /home/mpiuser/.ssh/id_rsa.pub /home/mpiuser/.ssh/authorized_keys

USER root
EXPOSE 22

# Mantém o SSH a rodar no primeiro plano sem encerrar
CMD ["/usr/sbin/sshd", "-D"]