#!/bin/bash
set -meo pipefail

sudo mkdir -p /opt/home-assistant /etc/docker-compose/home-assistant
sudo cp ./home-assistant/docker-compose.yml /etc/docker-compose/home-assistant
sudo systemctl daemon-reload
sudo systemctl start docker-compose@home-assistant
sudo systemctl enable docker-compose@home-assistant


