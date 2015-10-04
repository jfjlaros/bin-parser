"""
General binary file parser


Copyright (c) 2015 Jeroen F.J. Laros <J.F.J.Laros@lumc.nl>

Licensed under the MIT license, see the LICENSE file.
"""
from .bin_parser import BinParser
from .functions import BinParseFunctions


__version_info__ = ('0', '0', '8')
__date__ = '4 Oct 2015'

__version__ = '.'.join(__version_info__)
__author__ = 'Jeroen F.J. Laros'
__contact__ = 'J.F.J.Laros@lumc.nl'
__homepage__ = 'https://git.lumc.nl/j.f.j.laros/bin-parser'


usage = __doc__.split('\n\n\n')


def version(name):
    return '{} version {}\n\nAuthor   : {} <{}>\nHomepage : {}'.format(
        name, __version__, __author__, __contact__, __homepage__)
