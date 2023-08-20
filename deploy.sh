#!/bin/bash
set -e

cd "$(dirname "$0")"

docker build -t scelfo/hubitat-prometheus .

docker push scelfo/hubitat-prometheus
