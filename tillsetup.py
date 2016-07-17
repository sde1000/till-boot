#!/usr/bin/env python

"""This script is run at boot time on the network-booted system.  It
does some general setup, then arranges to invoke the till software
with configuration URL, configname and database connection details
from the kernel command line.

"""

from __future__ import print_function
from __future__ import unicode_literals
import sys
import string
from subprocess import call

with file("/proc/cmdline") as f:
    cmdline = f.readline()

words = cmdline.split()
config = {}

for i in words:
    xs = i.split('=')
    if len(xs) < 2:
        continue
    config[xs[0]] = i[len(xs[0])+1:]

print("Configuration found: {}".format(repr(config)))

# Update packages from the pubco private repository if possible
call(['/usr/bin/apt-get', 'update'])
call(['/usr/bin/apt-get', '-y', 'dist-upgrade'])

if "configurl" in config:
    call(['/bin/mkdir', '-p', '/etc/quicktill'])
    with file("/etc/quicktill/configurl", 'w') as f:
        f.write("{}\n".format(config['configurl']))

if "install" in config:
    call(['/usr/bin/apt-get', '-y', 'install']+
         config["install"].split(','))

dbstring=[]
if "dbname" in config:
    dbstring.append("dbname="+config["dbname"])
if "dbhost" in config:
    dbstring.append("host="+config["dbhost"])
if "dbuser" in config:
    dbstring.append("user="+config["dbuser"])
if "dbpassword" in config:
    dbstring.append("password="+config["dbpassword"])

# If a print server is specified, create an appropriate /etc/cups/client.conf
if "printserver" in config:
    call(['/bin/mkdir', '-p', '/etc/cups'])
    with file("/etc/cups/client.conf", 'w') as f:
        f.write("ServerName {}\n".format(config["printserver"]))

# Some framebuffers don't come up in the correct resolution by default.
# Fix them if necessary.
if "xres" in config:
    call(['/bin/fbset', '-a', '-match', '-xres', config["xres"]])
if "yres" in config:
    call(['/bin/fbset', '-a', '-match', '-yres', config["yres"]])

# Allow 'till' user to access printers directly
call(['/usr/sbin/adduser', 'till', 'lp'])

runtillargs = []
if "configname" in config:
    runtillargs = runtillargs + ["-c", config["configname"]]
if len(dbstring)>0:
    runtillargs = runtillargs + ["-d","\"{}\"".format(string.join(dbstring))]
if "tillcmd" in config:
    runtillargs.append(config["tillcmd"])

font=config.get("tillfont","Uni2-TerminusBold22x11.psf.gz")

# Options are "off", "on", "vsync", "powerdown", "hsync"
powerdown = config.get("powerdown", "1")
powersavemode = config.get("powersavemode", "powerdown")
# If there's a kernel consoleblank parameter, we want to avoid overriding it
consoleblank = config.get("consoleblank", None)

with file("/home/till/.profile", "a") as f:
    if consoleblank is None:
        f.write("""
sudo setterm -blank 10 -powerdown {powerdown} -powersave {powersavemode} -msg off
""".format(powerdown = powerdown, powersavemode = powersavemode))
    f.write("""
setfont /usr/share/consolefonts/{font}
if [ "$(tty)" = "/dev/tty1" ]; then
    sudo apt-get update
    sudo apt-get -y dist-upgrade
    runtill {runtillargs}
    tillexit=$?
    sleep 2
    case "$tillexit" in
    0) exit ;;
    2) sudo poweroff ;;
    3) sudo reboot ;;
    esac
    sleep 1
    exit
    fi
""".format(font = font,
           runtillargs = ' '.join(runtillargs)))

# That should be it!  Casper will already have arranged for auto-login
