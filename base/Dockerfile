FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get upgrade -y && \
    export VERSION_CODENAME=$(env -i bash -c '. /etc/os-release; echo $VERSION_CODENAME') && \
    apt install -y --no-install-recommends wget gnupg ca-certificates && \
    echo "deb https://packages.adoptium.net/artifactory/deb $VERSION_CODENAME main" >> /etc/apt/sources.list && \
    (wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public | apt-key add -) && \
    echo 'deb [arch=arm64] https://www.ui.com/downloads/unifi/debian stable ubiquiti' >> /etc/apt/sources.list && \
    wget -O /etc/apt/trusted.gpg.d/unifi-repo.gpg https://dl.ui.com/unifi/unifi-repo.gpg && \
    apt update

RUN apt install -y --no-install-recommends temurin-11-jdk python3 python3-dev python3-pip build-essential
RUN python3 -m pip install pip setuptools -U
