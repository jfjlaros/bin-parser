#!/usr/bin/env python


import sys

from bin_parser import BinParser, BinParseFunctions


class Prince(BinParseFunctions):
    def minute(self, data):
        return super(Prince, self).int(data) - 1


parser = BinParser(open('examples/prince/prince.hof'),
    open('examples/prince/structure.yml'), open('examples/prince/fields.yml'),
    functions=Prince)
parser.write(sys.stdout)
