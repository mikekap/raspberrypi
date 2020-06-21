#!/bin/bash
set -meo pipefail

sudo mkdir -p /opt/nginx/sites-enabled /etc/docker-compose/nginx /opt/nginx/certbot
sudo cp ./nginx/docker-compose.yml /etc/docker-compose/nginx

sudo cp -f ./nginx/index.html /var/www/html/
sudo cp -f ./nginx/default /opt/nginx/sites-enabled/

sudo systemctl daemon-reload
sudo systemctl start docker-compose@nginx
sudo systemctl enable docker-compose@nginx
