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


def _inverse_dict(dictionary):
    return dict(map(lambda x: x[::-1], dictionary.items()))


class BinParseFunctions(object):
    def __init__(self):
        self.functions = {
            'raw': [self.raw, self.raw_inv],
            'bit': [self.bit, self.bit_inv],
            'int': [self.int, self.int_inv],
            'colour': [self.colour, self.colour_inv],
            'text': [self.text, self.text_inv]
        }

    def raw(self, data):
        """
        Return the input data in hexadecimal, grouped by bit.

        :arg str data: Input data.

        :return str: Hexadecimal representation of {data}.
        """
        raw_data = data.encode('hex')
        return ' '.join(
            [raw_data[x:x + 2] for x in range(0, len(raw_data), 2)])

    def raw_inv(self, data):
        return ''.join(data.split()).decode('hex')

    def bit(self, data):
        return '{:08b}'.format(ord(data))

    def bit_inv(self, data):
        return chr(int('0b{}'.format(data), 2))

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
        return reduce(
            lambda x, y: x * 0x100 + y, map(lambda x: ord(x), data[::-1]))

    def int_inv(self, data):
        """
        """
        data_int = data
        result = ''

        while data_int:
            result += chr(data_int % 0x100)
            data_int >>= 8

        return result

    def colour(self, data):
        return '0x{:06x}'.format(self.int(data))

    def colour_inv(self, data):
        return self.int_inv(int(data, 0x10))

    def text(self, data, split=[], encoding='utf-8'):
        """
        """
        decoded_text = data.decode(encoding)

        if split:
            return '\n'.join(decoded_text.split(''.join(map(chr, split))))
        return decoded_text

    def text_inv(self, data, split=[], encoding='utf-8'):
        decoded_text = data

        if split:
            decoded_text = ''.join(map(chr, split)).join(data.split('\n'))
        return decoded_text.encode(encoding)

    def date(self, data, annotation):
        """
        Decode a date.

        The date is encoded as an integer, representing the year followed by
        the (zero padded) day of the year.

        :arg str data: Binary encoded date.

        :return str: Date in format '%Y%j', 'defined' or 'unknown'.
        """
        date_int = self.int(data)

        if date_int in annotation:
            return annotation[date_int]
        return str(date_int)

    def date_inv(self, data, annotation):
        """
        """
        inverse_annotation = _inverse_dict(annotation)

        if data in inverse_annotation:
            return self.int_inv(inverse_annotation[data])
        return self.int_inv(int(data))

    def map(self, data, annotation):
        """
        Replace a value with its annotation.

        :arg str data: Encoded data.
        :arg dict annotation: Annotation of {data}.

        :return str: Annotated representation of {data}.
        """
        index = ord(data)

        if index in annotation:
            return annotation[index]
        return '{:02x}'.format(index)

    def flags(self, data, default, annotation):
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

            if flag not in annotation:
                if value:
                    flags['flags_{}_{:02x}'.format(default, flag)] = value
            else:
                flags[annotation[flag]] = value

        return flags
