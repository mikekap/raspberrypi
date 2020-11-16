#!/bin/bash
set -exo pipefail

mkdir training || true
scp -r pi@raspberrypi:/opt/light-training/photos/* ./training/
