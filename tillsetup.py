#!/usr/bin/env python3

"""This script is run at boot time on the network-booted system.  It
does some general setup, then arranges to invoke the till software
with configuration URL, configname and database connection details
from the kernel command line.
"""

import sys
import string
from subprocess import call

try:
    with open("/tillsetup-cmdline") as f:
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

print("Configuration found: {}".format(repr(config)))

# Update packages from the pubco private repository if possible
call(['/usr/bin/apt-get', 'update'])
call(['/usr/bin/apt-get', '-y', 'dist-upgrade'])

if "configurl" in config:
    call(['/bin/mkdir', '-p', '/etc/quicktill'])
    with open("/etc/quicktill/configurl", 'w') as f:
        f.write("{}\n".format(config['configurl']))

if "install" in config:
    call(['/usr/bin/apt-get', '-y', 'install']+
         config["install"].split(','))

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
    with open("/home/till/database", "w") as f:
        f.write(" ".join(dbstring) + "\n")

# If a print server is specified, create an appropriate /etc/cups/client.conf
if "printserver" in config:
    call(['/bin/mkdir', '-p', '/etc/cups'])
    with open("/etc/cups/client.conf", 'w') as f:
        f.write("ServerName {}\n".format(config["printserver"]))

# Some framebuffers don't come up in the correct resolution by default.
# Fix them if necessary.
if "xres" in config:
    call(['/bin/fbset', '-a', '-match', '-xres', config["xres"]])
if "yres" in config:
    call(['/bin/fbset', '-a', '-match', '-yres', config["yres"]])

if "configname" in config:
    with open("/home/till/configname", "w") as f:
        f.write(config["configname"] + "\n")

font = config.get("tillfont", "Uni2-TerminusBold22x11.psf.gz")

call(['/bin/setfont', '/usr/share/consolefonts/{}'.format(font)])

# Options are "off", "on", "vsync", "powerdown", "hsync"
screenblank = config.get("screenblank", "10")
powerdown = config.get("powerdown", "1")
powersavemode = config.get("powersavemode", "powerdown")

# If there's a kernel consoleblank parameter, we want to avoid overriding it
if consoleblank not in config:
    call(['/usr/bin/setterm',
          '-blank', screenblank,
          '-powerdown', powerdown,
          '-powersave', powersavemode,
          '-msg', 'off',
    ])

# That should be it!
