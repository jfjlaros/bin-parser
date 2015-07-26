"""
Field unpacking functions for the general binary parser.


(C) 2015 Jeroen F.J. Laros <J.F.J.Laros@lumc.nl>
"""


import operator
import yaml


operators = {
    'not': operator.not_,
    'and': operator.and_,
    'or': operator.or_,
    'xor': operator.xor,
    'eq': operator.eq,
    'ne': operator.ne,
    'ge': operator.ge,
    'gt': operator.gt,
    'le': operator.le,
    'lt': operator.lt,
    'mod': operator.mod,
    'contains': operator.contains
}


class BinParseFunctions(object):
    def __init__(self, types_handle):
        """
        """
        self._types = yaml.load(types_handle)

        # Add standard data types.
        self._types['raw'] = {}
        self._types['list'] = {}

        # Set default data type.
        if 'default' not in self._types:
            self._types['default'] = 'text'


    def raw(self, data):
        """
        Return the input data in hexadecimal, grouped by bit.

        :arg str data: Input data.

        :return str: Hexadecimal representation of {data}.
        """
        raw_data = data.encode('hex')
        return ' '.join(
            [raw_data[x:x + 2] for x in range(0, len(raw_data), 2)])


    def bit(self, data):
        return '{:08b}'.format(ord(data))


    def int(self, data):
        """
        Decode a little-endian encoded integer.

        Decoding is done as follows:
        - Reverse the order of the bits.
        - Convert the bits to ordinals.
        - Interpret the list of ordinals as digits in base 256.

        :arg str data: Little-endian encoded integer.

        :return int: Integer representation of {data}
        """
        return reduce(lambda x, y: x * 0x100 + y,
            map(lambda x: ord(x), data[::-1]))


    def colour(self, data):
        return '0x{:06x}'.format(self.int(data))


    def trim(self, data):
        return data.split(
            ''.join(map(chr, self._types['trim']['delimiter'])))[0]


    def text(self, data, delimiter=[]):
        """
        """
        field = data.split(''.join(map(chr,
            self._types['text']['delimiter'])))[0]

        if delimiter:
            return '\n'.join(field.split(''.join(map(chr,
                self._types['text']['data'][delimiter]))))
        return field


    def date(self, data):
        """
        Decode a date.

        The date is encoded as an integer, representing the year followed by
        the (zero padded) day of the year.

        :arg str data: Binary encoded date.

        :return str: Date in format '%Y%j', 'defined' or 'unknown'.
        """
        date_int = self.int(data)

        if date_int in self._types['date']['data']:
            return self._types['date']['data'][date_int]
        return str(date_int)


    def map(self, data, annotation):
        """
        Replace a value with its annotation.

        :arg str data: Encoded data.
        :arg dict annotation: Annotation of {data}.

        :return str: Annotated representation of {data}.
        """
        index = ord(data)

        if index in self._types['map']['data'][annotation]:
            return self._types['map']['data'][annotation][index]
        return '{:02x}'.format(index)


    def flags(self, data, annotation):
        """
        Explode a bitfield into flags.

        :arg int data: Bit field.
        :arg str annotation: Annotation of {data}.

        :return dict: Dictionary of flags and their values.
        """
        bitfield = self.int(data)
        flags = {}

        for flag in map(lambda x: 2 ** x, range(8)):
            value = bool(flag & bitfield)

            if flag not in self._types['flags']['data'][annotation]:
                if value:
                    flags['flags_{}_{:02x}'.format(annotation, flag)] = value
            else:
                flags[self._types['flags']['data'][annotation][flag]] = value

        return flags
