#!/usr/bin/env python
import sys

import yaml

from bin_parser import BinReader


parser = BinReader(
    open('balance.dat').read(),
    yaml.safe_load(open('structure.yml')),
    yaml.safe_load(open('types.yml')))

print parser.parsed['name']
print parser.parsed['year_of_birth']
print parser.parsed['balance']
