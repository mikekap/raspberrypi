#!/bin/bash
set -meo pipefail

sudo mkdir -p /etc/docker-compose/light-control/ /opt/light-training/photos
sudo cp ./light-control/docker-compose.yml /etc/docker-compose/light-control/
sudo systemctl daemon-reload
sudo systemctl start docker-compose@light-control
sudo systemctl enable docker-compose@light-control

