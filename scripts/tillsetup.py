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
import os

_true_strings = (
    'y', 'Y', 'yes', 'Yes', 'YES', 'true', 'True', 'TRUE', 'on', 'On', 'ON')
_false_strings = (
    'n', 'N', 'no', 'No', 'NO', 'false', 'False', 'FALSE', 'off', 'Off', 'OFF')

def get_boolean(d, k, default=None):
    # There is some confusion in yaml regarding whether unquoted
    # 'yes', 'no', etc. get turned into strings or booleans. The
    # specification changed between yaml 1.1 and 1.2. Depending on how
    # whoever wrote the configuration file quoted their options, we
    # may end up with a real boolean, or one of the _true_strings or
    # _false_strings above (which are taken from the yaml 1.1
    # spec). Or possibly something else!

    # We return the default if the key is not present. If one of the
    # _true_strings or _false_strings is present we return True or
    # False. Otherwise we return the contents of the key unchanged.
    if k not in d:
        return default
    i = d[k]
    if i in _true_strings:
        return True
    if i in _false_strings:
        return False
    return i

def bail(problem):
    print(problem)
    sys.exit(1)

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
    cmdline_config = {}

    for i in words:
        xs = i.split('=')
        if len(xs) < 2:
            continue
        cmdline_config[xs[0]] = i[len(xs[0]) + 1:]

    boot_version = cmdline_config.get("till-boot-version")
    if not boot_version:
        bail("till-boot-version kernel command line parameter not set")
    boot_config = cmdline_config.get("till-boot-config")
    if not boot_config:
        bail("till-boot-config kernel command line parameter not set")
    try:
        r = requests.get(boot_config)
    except Exception as e:
        print(e)
        bail(f"exception fetching config from {boot_config}")
    if r.status_code != 200:
        bail(f"response code {r.status_code} fetching config from {r.url}")

    try:
        config = yaml.safe_load(r.text)
    except Exception as e:
        print(e)
        bail(f"problem reading configuration from {r.url}")

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

    mode = config.get("mode", "till")

    mm = "maintenance-message"
    if config.get(mm):
        mode = "maintenance"
        with open(mm, "w") as f:
            f.write(config[mm])
            f.write("\n")

    with open("mode", "w") as f:
        f.write(f"{mode}\n")

    with open("display-url", "w") as f:
        f.write(f"{config.get('display-url', 'https://quicktill.assorted.org.uk')}\n")

    # Add apt respositories
    with open("apt-sources.list", "w") as f:
        for r in config.get("repos", []):
            f.write(f"{r}\n")

    with open("install", "w") as f:
        install = config.get("install", []) + config.get("extra-install", [])
        f.write(f"{' '.join(install)}\n")

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

    pointer = get_boolean(config, "pointer", default=False)

    with open("pointer", "w") as f:
        f.write(f"{'yes' if pointer else 'no'}\n")

    printserver = config.get("printserver", None)

    if printserver:
        with open("printserver", "w") as f:
            f.write(f"{printserver}\n")

    with open("runtill-command", "w") as f:
        f.write("runtill \\\n")
        if "configurl" in config:
            f.write(f'  -u "{config["configurl"]}" \\\n')
        f.write(f'  -c "{configname}" \\\n')
        f.write(f'  -d "{database}" \\\n')
        f.write('  start \\\n')
        f.write('  --gtk --fullscreen \\\n')
        # yaml awkwardness: 'keyboard' may be a boolean or a string
        keyboard = get_boolean(config, "keyboard", default=True)
        if keyboard:
            f.write('  --keyboard \\\n')
            if keyboard == "onscreen-only":
                f.write('  --no-hardware-keyboard \\\n')
        f.write(f'  --font="sans {fontsize}" \\\n')
        f.write(f'  --monospace-font="monospace {fontsize}" \\\n')
        f.write('  -e 0 "Restart till software" \\\n')
        f.write('  -e 20 "Power off till" \\\n')
        f.write('  -e 30 "Reboot till" \\\n')
        f.write('  -i 40\n')

if __name__ == '__main__':
    run()
