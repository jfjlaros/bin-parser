#!/usr/bin/env python
import sys

import yaml

from bin_parser import BinWriter


parser = BinWriter(
    yaml.safe_load(open('../float.yml')),
    yaml.safe_load(open('../structure.yml')),
    yaml.safe_load(open('../types.yml')))
sys.stdout.write(parser.data)
