FROM rpi-base

RUN echo 'deb https://adoptopenjdk.jfrog.io/adoptopenjdk/deb/ focal main' >> /etc/apt/sources.list && \
    wget -qO - https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public | apt-key add - && \
    apt update && apt install adoptopenjdk-14-hotspot && rm -rf /var/lib/apt/lists/*

