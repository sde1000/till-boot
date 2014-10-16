#!/usr/bin/env python

"""
This script is run at boot time on the network-booted system.  It does
some general setup (eg. keymap), then arranges to invoke the till
software with configuration URL, configname and database connection
details from the kernel command line.

"""

import sys,string
from subprocess import call
from urllib import urlretrieve

print "Checking till configuration..."

with file("/proc/cmdline") as f:
    cmdline=f.readline()

words=cmdline.split()

configwords=["configurl","configname","dbname","dbhost","dbuser","dbpassword",
             "printserver","xres","yres","install","tillcmd"]
config={}

for i in words:
    xs=i.split('=')
    if len(xs)<2: continue
    if xs[0] in configwords:
        config[xs[0]]=i[len(xs[0])+1:]

print "Configuration found:"
print config

# The only required option is 'configurl'.
if 'configurl' not in config:
    sys.stderr.write("No configurl found; system will "
                     "not be customised.\n")
    sys.exit(0)

configurl=config['configurl']
configname=config.get('configname')
dbname=config.get('dbname')
dbhost=config.get('dbhost')
dbuser=config.get('dbuser')
dbpassword=config.get('dbpassword')
printserver=config.get('printserver')
xres=config.get('xres')
yres=config.get('yres')
install=config.get('install')
tillcmd=config.get('tillcmd')

dbstring=[]
if dbname is not None: dbstring.append("dbname=%s"%dbname)
if dbhost is not None: dbstring.append("host=%s"%dbhost)
if dbuser is not None: dbstring.append("user=%s"%dbuser)
if dbpassword is not None: dbstring.append("password=%s"%dbpassword)

# Update packages from the pubco private repository if possible
call(['/usr/bin/apt-get','update'])
call(['/usr/bin/apt-get','-y','dist-upgrade'])
if install:
    call(['/usr/bin/apt-get','-y','install']+
         install.split(','))

# Allow 'till' user to access printers directly
call(['/usr/sbin/adduser','till','lp'])
# Create till config directory
call(['/bin/mkdir','-p','/etc/quicktill'])
with file("/etc/quicktill/configurl",'w') as f:
    f.write("{}\n".format(configurl))

# Some framebuffers don't come up in the correct resolution by default.
# Fix them if necessary.
if xres:
    call(['/bin/fbset','-a','-match','-xres',xres])
if yres:
    call(['/bin/fbset','-a','-match','-yres',yres])

# Append startup script to till user's .profile
runtillargs=[]
if configname is not None:
    runtillargs=runtillargs+["-c",configname]
if len(dbstring)>0:
    runtillargs=runtillargs+["-d","\"{}\"".format(string.join(dbstring))]
if tillcmd:
    runtillargs.append(tillcmd)

with file("/home/till/.profile","a") as f:
    f.write("""
sudo setterm -blank 10 -powerdown 1 -powersave powerdown -msg off
setfont /usr/share/consolefonts/Uni2-TerminusBold22x11.psf.gz
if [ "$(tty)" = "/dev/tty1" ]; then
    sudo apt-get update
    sudo apt-get -y dist-upgrade
    runtill {}
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
""".format(' '.join(runtillargs)))

# If a print server is specified, create an appropriate /etc/cups/client.conf
if printserver:
    call(['/bin/mkdir','-p','/etc/cups'])
    with file("/etc/cups/client.conf",'w') as f:
        f.write("ServerName {}\n".format(printserver))

# That should be it!  Casper will already have arranged for auto-login
