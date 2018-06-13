#!/usr/bin/env python
import os
import sys

import yaml

from bin_parser import BinWriter
from functions import PrinceWriteFunctions


parser = BinWriter(
    yaml.safe_load(open('../prince.yml')),
    yaml.safe_load(open('../structure.yml')),
    yaml.safe_load(open('../types.yml')),
    functions=PrinceWriteFunctions())

fp = os.fdopen(sys.stdout.fileno(), 'wb')
fp.write(parser.data)
