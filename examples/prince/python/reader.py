#!/usr/bin/env python

import sys

from bin_parser import BinReader
from functions import PrinceReadFunctions


parser = BinReader(
    open('../prince.hof'), open('../structure.yml'), open('../types.yml'),
    functions=PrinceReadFunctions)
parser.write(sys.stdout)
