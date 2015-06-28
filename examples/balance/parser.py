#!/usr/bin/env python


import sys

import bin_parser


parser = bin_parser.BinParser(open('balance.dat'), open('structure.yml'),
    open('types.yml'))
parser.write(sys.stdout)
