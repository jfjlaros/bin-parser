#!/usr/bin/env python
import sys

import yaml

from bin_parser import BinReader


parser = BinReader(
    open('../float.dat').read(),
    yaml.safe_load(open('../structure.yml')),
    yaml.safe_load(open('../types.yml')))
yaml.safe_dump(parser.parsed, sys.stdout, width=76, default_flow_style=False)
