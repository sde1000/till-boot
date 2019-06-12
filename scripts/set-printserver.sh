#!/bin/bash

set -e

cd /home/till

mkdir -p /etc/cups
printserver=$(cat printserver)

echo "ServerName ${printserver}" >/etc/cups/client.conf
