#!/bin/bash

set -e

cd /home/till

mkdir -p /etc/cups
printserver=$(jq -r .printserver config.json)

echo "ServerName ${printserver}" >/etc/cups/client.conf
