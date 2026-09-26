FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-numpy \
    openmpi-bin \
    libopenmpi-dev \
    openssh-server \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/sshd
RUN useradd -m -s /bin/bash mpiuser && echo "mpiuser:mpiuser" | chpasswd

WORKDIR /home/mpiuser
USER mpiuser
RUN ssh-keygen -t rsa -N "" -f /home/mpiuser/.ssh/id_rsa && \
    cp /home/mpiuser/.ssh/id_rsa.pub /home/mpiuser/.ssh/authorized_keys

USER root
EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]