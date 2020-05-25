FROM rpi-base

RUN echo 'deb https://www.ui.com/downloads/unifi/debian stable ubiquiti' >> /etc/apt/sources.list && \
    wget -O /etc/apt/trusted.gpg.d/unifi-repo.gpg https://dl.ui.com/unifi/unifi-repo.gpg && \
    apt update && \
    cd /tmp/ && \
    apt download unifi && \
    dpkg-deb -R unifi*.deb unifi && \
    rm unifi*.deb && \
    sed -i -e '/mongodb/d' -e 's/java8-runtime-headless,//' unifi/DEBIAN/control && \
    dpkg-deb -b unifi unifi-fixed.deb && \
    apt install -y --no-install-recommends ./unifi-fixed.deb libactivation-java && \
    rm -rf unifi* && \
    rm -rf /var/lib/apt/lists/*

ADD docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["unifi"]
