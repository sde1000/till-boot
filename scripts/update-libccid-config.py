#!/usr/bin/env python3

# Edit /etc/libccid_Info.plist to set ifdDriverOptions to 0x0001

import argparse
import plistlib

parser = argparse.ArgumentParser(description="Update libccid config file")
parser.add_argument("infile", help="File to read")
parser.add_argument("outfile", help="File to write")
args = parser.parse_args()

with open(args.infile, "rb") as f:
    c = plistlib.load(f)

c['ifdDriverOptions'] = "0x0001"

with open(args.outfile, "wb") as f:
    plistlib.dump(c, f, fmt=plistlib.FMT_XML, sort_keys=False)
