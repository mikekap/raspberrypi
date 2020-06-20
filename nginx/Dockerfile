FROM rpi-base

RUN apt install -y nginx certbot ssl-cert
ADD nginx.conf /etc/nginx/nginx.conf
ADD docker-entrypoint.sh /

CMD ["/docker-entrypoint.sh"]
