#!/usr/bin/env python


import sys

from bin_parser import BinParser, BinParseFunctions


class Prince(BinParseFunctions):
    def min(self, data):
        return super(Prince, self).int(data) - 1


    def sec(self, data):
        return super(Prince, self).int(data) // 12


parser = BinParser(open('prince.hof'), open('structure.yml'),
    open('types.yml'), functions=Prince)
parser.write(sys.stdout)
