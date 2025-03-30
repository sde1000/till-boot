#!/usr/bin/env python3
"""This script is run when user "till" automatically logs in on the
network-booted system.
"""

import sys
import time
import requests
import subprocess
import json


def bail(problem):
    print(problem)
    sys.exit(1)


def fetch_config(cmdline_config):
    boot_config_json = cmdline_config.get("till-boot-config-json")
    if not boot_config_json:
        bail("till-boot-config-json kernel command line parameter not set")

    try:
        r = requests.get(boot_config_json)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(e)
        bail(f"exception fetching config from {boot_config_json}")


def run():
    try:
        with open("tillsetup-cmdline") as f:
            cmdline = f.readline()
    except FileNotFoundError:
        with open("/proc/cmdline") as f:
            cmdline = f.readline()

    words = cmdline.split()
    cmdline_config = {}

    for i in words:
        xs = i.split('=')
        if len(xs) < 2:
            continue
        cmdline_config[xs[0]] = i[len(xs[0]) + 1:]

    boot_version = cmdline_config.get("till-boot-version")
    if not boot_version:
        bail("till-boot-version kernel command line parameter not set")

    config = fetch_config(cmdline_config)

    if "version" not in config:
        bail("no 'version' key present in configuration")

    # At this point we have both the boot-time config from the kernel
    # command line and the run-time config read over http.  We can see
    # whether we need to reboot to pick up an updated boot image.
    if boot_version != config["version"]:
        print(f"Current boot image version: {boot_version}")
        print(f"Available boot image version: {config['version']}")
        print("")
        print("An updated boot image is available for this till.")
        print("Rebooting to load it.")
        time.sleep(5)
        subprocess.run(["/usr/bin/sudo", "reboot"])
        time.sleep(60)
        bail("did not reboot in time!")

    # Dump the config to the home directory
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    # Fetch files, overwriting existing files if required
    fetch = config.get("fetch", {})
    for filename, url in fetch.items():
        try:
            r = requests.get(url)
            r.raise_for_status()
            with open(filename, 'wb') as f:
                f.write(r.content)
        except Exception:
            print(f"failed to fetch {url} as {filename}")


if __name__ == '__main__':
    run()
