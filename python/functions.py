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
    """
    Functions for decoding and encoding data.

    Every decoding function has a counterpart for encoding. These functions end
    with `_inv`. Documentation of these functions is omited.
    """
    def raw(self, data):
        """
        Encode a string in hexadecimal, grouped by byte.

        :arg str data: Input data.

        :returns str: Hexadecimal representation of {data}.
        """
        raw_data = data.encode('hex')

        return ' '.join(
            [raw_data[x:x + 2] for x in range(0, len(raw_data), 2)])

    def raw_inv(self, hex_string):
        return ''.join(hex_string.split()).decode('hex')

    def bit(self, data):
        return '{:08b}'.format(ord(data))

    def bit_inv(self, bit_string):
        return chr(int('0b{}'.format(bit_string), 2))

    def int(self, data):
        """
        Decode a little-endian encoded integer.

        Decoding is done as follows:
        - Reverse the order of the bits.
        - Convert the bits to ordinals.
        - Interpret the list of ordinals as digits in base 256.

        :arg str data: Little-endian encoded integer.

        :returns int: Integer representation of {data}
        """
        return reduce(
            lambda x, y: x * 0x100 + y, map(lambda x: ord(x), data[::-1]))

    def int_inv(self, integer):
        data_int = integer
        result = ''

        while data_int:
            result += chr(data_int % 0x100)
            data_int >>= 8

        return result

    def colour(self, data):
        return '0x{:06x}'.format(self.int(data))

    def colour_inv(self, colour_string):
        return self.int_inv(int(colour_string, 0x10))

    def text(self, data, split=[], encoding='utf-8'):
        """
        Decode a text string.

        :arg str data: Text string.
        :arg list(byte) split: Internal delimiter for end of line.
        :arg str encoding: Character encoding.

        :returns str: Decoded text.
        """
        decoded_text = data.decode(encoding)

        if split:
            return '\n'.join(decoded_text.split(''.join(map(chr, split))))
        return decoded_text

    def text_inv(self, text_string, split=[], encoding='utf-8'):
        decoded_text = text_string

        if split:
            decoded_text = ''.join(map(chr, split)).join(
                text_string.split('\n'))
        return decoded_text.encode(encoding)

    def date(self, data, annotation):
        """
        Decode a date.

        The date is encoded as an integer, representing the year followed by
        the (zero padded) day of the year.

        :arg str data: Binary encoded date.
        :arg dict annotation: Names for special cases.

        :returns str: Date in format '%Y%j', 'defined' or 'unknown'.
        """
        date_int = self.int(data)

        if date_int in annotation:
            return annotation[date_int]
        return str(date_int)

    def date_inv(self, date_int, annotation):
        inverse_annotation = _inverse_dict(annotation)

        if date_int in inverse_annotation:
            return self.int_inv(inverse_annotation[date_int])
        return self.int_inv(int(date_int))

    def map(self, data, annotation):
        """
        Replace a value with its annotation.

        :arg str data: Encoded data.
        :arg dict annotation: Annotation of {data}.

        :returns str: Annotated representation of {data}.
        """
        index = ord(data)

        if index in annotation:
            return annotation[index]
        return '{:02x}'.format(index)

    def map_inv(self, mapped_string, annotation):
        inverse_annotation = _inverse_dict(annotation)

        if mapped_string in inverse_annotation:
            return chr(inverse_annotation[mapped_string])
        return chr(int(mapped_string, 0x10))

    def flags(self, data, default, annotation):
        """
        Explode a bitfield into flags.

        Note that if a flag is not annotated and false, it will not be included
        in the results.

        :arg int data: Bit field.
        :arg str default: Flag name for unannotated bits.
        :arg str annotation: Annotation of {data}.

        :returns dict: Dictionary of flags and their values.
        """
        bitfield = self.int(data)
        flags_dict = {}

        for flag in map(lambda x: 2 ** x, range(8)):
            value = bool(flag & bitfield)

            if flag not in annotation:
                if value:
                    flags_dict['flags_{}_{:02x}'.format(default, flag)] = value
            else:
                flags_dict[annotation[flag]] = value

        return flags_dict

    def flags_inv(self, flags_dict, default, annotation):
        inverse_annotation = _inverse_dict(annotation)
        prefix_len = len('flags_{}_'.format(default))
        values = 0x00

        for key in flags_dict:
            if key in inverse_annotation:
                if flags_dict[key]:
                    values += inverse_annotation[key]
            else:
                values += int(key[prefix_len:], 0x10)
        return chr(values)
