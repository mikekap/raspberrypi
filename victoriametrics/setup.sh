#!/bin/bash
set -meo pipefail

sudo mkdir -p /data/victoriametrics/ /etc/docker-compose/victoriametrics
sudo cp ./victoriametrics/docker-compose.yml /etc/docker-compose/victoriametrics

sudo systemctl daemon-reload
sudo systemctl start docker-compose@victoriametrics
sudo systemctl enable docker-compose@victoriametrics
