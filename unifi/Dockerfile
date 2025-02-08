FROM rpi-base

RUN cd /tmp/ && \
    apt download unifi && \
    dpkg-deb -R unifi*.deb unifi && \
    rm unifi*.deb && \
    sed -i -e '/mongodb/d' -e 's/java8-runtime-headless,//' unifi/DEBIAN/control && \
    dpkg-deb -b unifi unifi-fixed.deb && \
    apt install -y --no-install-recommends ./unifi-fixed.deb libactivation-java && \
    rm -rf unifi*

ENV BASEDIR=/usr/lib/unifi \
    DATADIR=/unifi/data \
    LOGDIR=/unifi/log \
    CERTDIR=/unifi/cert \
    RUNDIR=/unifi/run \
    ORUNDIR=/var/run/unifi \
    ODATADIR=/var/lib/unifi \
    OLOGDIR=/var/log/unifi \
    CERT_IS_CHAIN=false \
    GOSU_VERSION=1.10 \
    BIND_PRIV=true \
    RUNAS_UID0=true \
    UNIFI_GID=999 \
    UNIFI_UID=999

ADD docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["unifi"]
