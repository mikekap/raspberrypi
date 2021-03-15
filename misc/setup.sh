#!/bin/bash
set -meo pipefail

sudo mkdir -p /opt/misc/
sudo cp sync-keys disk-space-alert /opt/misc/
sudo chmod +x /opt/misc/*

sudo ln -sf /opt/misc/sync-keys /etc/cron.hourly/
sudo ln -sf /opt/misc/disk-space-alert /etc/cron.hourly/
