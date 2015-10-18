#!/usr/bin/env python

import sys

from bin_parser import BinWriter
from functions import PrinceWriteFunctions


parser = BinWriter(
    open('prince.yml'), open('structure.yml'), open('types.yml'),
    functions=PrinceWriteFunctions)
parser.write(sys.stdout)
