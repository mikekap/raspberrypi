#!/bin/bash
set -meo pipefail

sudo mkdir -p /opt/unifi/data /opt/mongodb /etc/docker-compose/unifi/
sudo cp ./unifi/docker-compose.yml /etc/docker-compose/unifi/
sudo systemctl daemon-reload
sudo systemctl start docker-compose@unifi
