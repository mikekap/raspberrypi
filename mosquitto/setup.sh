#!/bin/bash
set -meo pipefail

sudo mkdir -p /opt/mosquitto/config /opt/mosquitto/data /etc/docker-compose/mosquitto/
sudo cp ./mosquitto/mosquitto.conf /opt/mosquitto/config/
sudo cp ./mosquitto/docker-compose.yml /etc/docker-compose/mosquitto/
sudo systemctl daemon-reload
sudo systemctl start docker-compose@mosquitto
sudo systemctl enable docker-compose@mosquitto


