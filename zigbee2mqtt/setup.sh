#!/bin/bash
set -meo pipefail

sudo mkdir -p /opt/zigbee2mqtt/store/ /etc/docker-compose/zigbee2mqtt
sudo cp ./zigbee2mqtt/docker-compose.yml /etc/docker-compose/zigbee2mqtt

sudo systemctl daemon-reload
sudo systemctl start docker-compose@zigbee2mqtt
sudo systemctl enable docker-compose@zigbee2mqtt
