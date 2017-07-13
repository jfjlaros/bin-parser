"""General binary file parser.


Copyright (c) 2015 Jeroen F.J. Laros <J.F.J.Laros@lumc.nl>

Licensed under the MIT license, see the LICENSE file.
"""
from .bin_parser import BinReader, BinWriter
from .functions import BinReadFunctions, BinWriteFunctions


__version_info__ = ('0', '0', '13')

__version__ = '.'.join(__version_info__)
__author__ = 'Jeroen F.J. Laros'
__contact__ = 'J.F.J.Laros@lumc.nl'
__homepage__ = 'https://git.lumc.nl/j.f.j.laros/bin-parser'


usage = __doc__.split('\n\n\n')


def doc_split(func):
    return func.__doc__.split('\n\n')[0]


def version(name):
    return '{} version {}\n\nAuthor   : {} <{}>\nHomepage : {}'.format(
        name, __version__, __author__, __contact__, __homepage__)
