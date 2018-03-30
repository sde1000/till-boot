#!/usr/bin/env python3
"""This script is run when user "till" automatically logs in on the
network-booted system.
"""

import sys
import string
from subprocess import call

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

if "configurl" in config:
    with open("configurl", 'w') as f:
        f.write("{}\n".format(config['configurl']))

if "install" in config:
    with open("install", 'w') as f:
        f.write("{}\n".format(" ".join(config["install"].split(","))))

dbstring = []
if "dbname" in config:
    dbstring.append("dbname=" + config["dbname"])
if "dbhost" in config:
    dbstring.append("host=" + config["dbhost"])
if "dbuser" in config:
    dbstring.append("user=" + config["dbuser"])
if "dbpassword" in config:
    dbstring.append("password=" + config["dbpassword"])
if len(dbstring) > 0:
    with open("database", "w") as f:
        f.write(" ".join(dbstring) + "\n")

# Some framebuffers don't come up in the correct resolution by default.
# Fix them if necessary.
if "xres" in config:
    call(['/bin/fbset', '-a', '-match', '-xres', config["xres"]])
if "yres" in config:
    call(['/bin/fbset', '-a', '-match', '-yres', config["yres"]])

configname = config.get("configname", "default")
with open("configname", "w") as f:
    f.write(configname + "\n")

fontsize = config.get("fontsize", "20")
with open("fontsize", "w") as f:
    f.write(fontsize + "\n")

# That should be it!
