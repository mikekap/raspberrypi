FROM rpi-base

RUN cd /tmp/ && \
    apt download unifi && \
    dpkg-deb -R unifi*.deb unifi && \
    rm unifi*.deb && \
    sed -i -e '/mongodb/d' -e 's/java8-runtime-headless,//' unifi/DEBIAN/control && \
    dpkg-deb -b unifi unifi-fixed.deb && \
    apt install -y --no-install-recommends ./unifi-fixed.deb libactivation-java && \
    rm -rf unifi*

ADD docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["unifi"]
