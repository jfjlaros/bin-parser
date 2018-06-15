#!/usr/bin/env python
import yaml

from bin_parser import BinReader


parser = BinReader(
    open('balance.dat', 'rb').read(),
    yaml.safe_load(open('structure.yml')),
    yaml.safe_load(open('types.yml')))

print('{}\n'.format(parser.parsed['name']))
print('{}\n'.format(parser.parsed['year_of_birth']))
print('{}\n'.format(parser.parsed['balance']))
