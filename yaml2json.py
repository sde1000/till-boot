#!/usr/bin/env python3

import yaml
import json
import sys

json.dump(yaml.safe_load(sys.stdin), sys.stdout, indent=2)
