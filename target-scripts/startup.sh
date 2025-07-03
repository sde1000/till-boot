#!/bin/bash

# Start up using options from the configuration file

mode=$(jq -r '.mode // "till"' config.json)

if [ "${mode}" = "maintenance" ]; then
    echo
    echo
    echo "System is in maintenance mode; startup will not continue"
    echo
    echo -n "Last checked: "
    date
    echo
    jq -r '."maintenance-message" // "Waiting 30s before checking again."' config.json
    echo
    sleep 30
    exit
fi

if [ "$(jq -r '."restore-apt-sources" // false' config.json)" = "true" ]; then
    echo "***DEBUG MODE: restoring /etc/apt/sources.list from image creation"
    sudo cp /root/sources.list /etc/apt/sources.list
fi

# Update list of respositories
jq -r '.repos // [] | join("\n")' config.json >apt-sources.list

sudo apt-get update
sudo apt-get -y dist-upgrade

if jq -e 'has("printserver")' config.json >/dev/null ; then
    sudo ./set-printserver.sh
fi

if jq -e 'has("install")' config.json >/dev/null ; then
  sudo apt-get -y install $(jq -r '.install | join(" ")' config.json)
fi

if jq -e 'has("extra-install")' config.json >/dev/null ; then
  sudo apt-get -y install $(jq -r '."extra-install" | join(" ")' config.json)
fi

if jq -e 'has("quicktill-config")' config.json >/dev/null ; then
    mkdir -p ~/.config
    jq '."quicktill-config"' config.json >~/.config/quicktill.json
fi

if [ -x ./mode-${mode} ]; then
    exec ./mode-${mode}
fi

echo "Script for ${mode} mode is not executable — will retry in 30s"

sleep 30
