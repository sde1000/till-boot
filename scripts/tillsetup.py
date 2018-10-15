#!/usr/bin/env python3
"""This script is run when user "till" automatically logs in on the
network-booted system.
"""

import sys
import time
import string
import requests
import subprocess
import yaml

def run():
    try:
        with open("tillsetup-cmdline") as f:
            cmdline = f.readline()
            testing = True
    except FileNotFoundError:
        with open("/proc/cmdline") as f:
            cmdline = f.readline()
            testing = False

    words = cmdline.split()
    config = {}

    for i in words:
        xs = i.split('=')
        if len(xs) < 2:
            continue
        config[xs[0]] = i[len(xs[0]) + 1:]

    if "till-boot-version" in config:
        current(config)
    else:
        legacy(config)

def bail(problem):
    print(problem)
    sys.exit(1)

def current(cmdline_config):
    boot_version = cmdline_config["till-boot-version"]
    boot_config = cmdline_config.get("till-boot-config", None)
    if not boot_config:
        bail("till-boot-config kernel command line parameter not set")
    try:
        r = requests.get(boot_config)
    except Exception as e:
        print(e)
        bail("exception fetching config from {}".format(boot_config))
    if r.status_code != 200:
        bail("response code {} fetching config from {}".format(
            r.status_code, r.url))

    try:
        config = yaml.safe_load(r.text)
    except Exception as e:
        print(e)
        bail("problem reading configuration from {}".format(r.url))

    if "version" not in config:
        bail("no 'version' key present in configuration")

    # At this point we have both the boot-time config from the kernel
    # command line and the run-time config read over http.  We can see
    # whether we need to reboot to pick up an updated boot image.
    if boot_version != config["version"]:
        print("An updated boot image is available for this till.")
        print("Rebooting to load it.")
        time.sleep(5)
        subprocess.run(["/usr/bin/sudo", "reboot"])
        time.sleep(60)
        bail("did not reboot in time!")

    # Add apt respositories
    with open("apt-sources.list", "w") as f:
        for r in config.get("repos", []):
            f.write("{}\n".format(r))

    with open("install", "w") as f:
        install = config.get("install", []) + config.get("extra-install", [])
        f.write("{}\n".format(" ".join(install)))

    # Continue with till config
    tillconfig(config)

def legacy(config):
    if "install" in config:
        with open("install", 'w') as f:
            f.write("{}\n".format(" ".join(config["install"].split(","))))

    # Continue with till config
    tillconfig(config)

def tillconfig(config):
    dbstring = []
    if "dbname" in config:
        dbstring.append("dbname=" + config["dbname"])
    if "dbhost" in config:
        dbstring.append("host=" + config["dbhost"])
    if "dbuser" in config:
        dbstring.append("user=" + config["dbuser"])
    if "dbpassword" in config:
        dbstring.append("password=" + config["dbpassword"])
    database = " ".join(dbstring)

    configname = config.get("configname", "default")

    fontsize = config.get("fontsize", "20")

    with open("runtill-command", "w") as f:
        f.write("runtill \\\n")
        if "configurl" in config:
            f.write('  -u "{}" \\\n'.format(config["configurl"]))
        f.write('  -c "{}" \\\n'.format(configname))
        f.write('  -d "{}" \\\n'.format(database))
        f.write('  start \\\n')
        f.write('  --gtk --fullscreen \\\n')
        if "keyboard" in config:
            f.write('  --keyboard \\\n')
        f.write('  --font="sans {}" \\\n'.format(fontsize))
        f.write('  --monospace-font="monospace {}" \\\n'.format(fontsize))
        f.write('  -e 0 "Restart till software" \\\n')
        f.write('  -e 20 "Power off till" \\\n')
        f.write('  -e 30 "Reboot till" \\\n')
        f.write('  -i 40\n')

if __name__ == '__main__':
    run()
