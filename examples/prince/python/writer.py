#!/usr/bin/env python
import sys

import yaml

from bin_parser import BinWriter
from functions import PrinceWriteFunctions


parser = BinWriter(
    yaml.safe_load(open('../prince.yml')),
    yaml.safe_load(open('../structure.yml')),
    yaml.safe_load(open('../types.yml')),
    functions=PrinceWriteFunctions())
sys.stdout.write(parser.data)
