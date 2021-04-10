#!/bin/bash
set -meo pipefail

sudo mkdir -p /opt/zwavejs2mqtt/store/ /etc/docker-compose/zwavejs2mqtt
sudo cp ./zwavejs2mqtt/docker-compose.yml /etc/docker-compose/zwavejs2mqtt

sudo systemctl daemon-reload
sudo systemctl start docker-compose@zwavejs2mqtt
sudo systemctl enable docker-compose@zwavejs2mqtt
