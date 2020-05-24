FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get upgrade -y && \
    apt install -y --no-install-recommends wget gnupg ca-certificates && \
    echo 'deb https://adoptopenjdk.jfrog.io/adoptopenjdk/deb/ focal main' >> /etc/apt/sources.list && \
    (wget -qO - https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public | apt-key add -) && \
    apt update && \
    apt install -y --no-install-recommends adoptopenjdk-14-hotspot && \
    rm -rf /var/lib/apt/lists/*
