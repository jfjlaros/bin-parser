"""Field packing and unpacking functions for the general binary parser."""
import codecs
import collections
import operator
import struct

from .deprecated import deprecation_warning


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
    return {v: k for k, v in dictionary.items()}


class BinReadFunctions(object):
    """Functions for decoding data."""
    def struct(self, data, fmt='b', labels=None, annotation=None):
        """Decode basic and simple compound data types.

        Primary decoding is controlled with the `fmt` parameter (see
        https://docs.python.org/2/library/struct.html for more information),
        which yields a list of values. These values are optionally substituted
        using `annotation` as a substitution scheme.
        If the list has only one element, this element is returned, if `labels`
        is defined, a set of key-value pairs is returned, the bare list is
        returned otherwise.

        :arg str data: Input data.
        :arg str fmt: Format characters.
        :arg list labels: Labels for the decoded data units.
        :arg dict annotation: Names for special cases.

        :returns any: Decoded data.
        """
        decoded = list(struct.unpack(fmt, data))

        if annotation:
            for index, value in enumerate(decoded):
                if value in annotation:
                    decoded[index] = annotation[value]

        if len(decoded) > 1:
            if labels:
                return dict(zip(labels, decoded))
            return list(decoded)
        if fmt == 'c':
            return decoded[0].decode('utf-8')
        return decoded[0]

    def raw(self, data):
        """Encode a string in hexadecimal, grouped by byte.

        :arg str data: Input data.

        :returns str: Hexadecimal representation of {data}.
        """
        raw_data = codecs.encode(data, 'hex')

        return b' '.join(
            [raw_data[x:x + 2] for x in range(0, len(raw_data), 2)]).decode(
                'utf-8')

    def bit(self, data):
        return '{:08b}'.format(ord(data))

    def int(self, data):
        """Decode a little-endian encoded integer.

        Decoding is done as follows:
        - Reverse the order of the bits.
        - Convert the bits to ordinals.
        - Interpret the list of ordinals as digits in base 256.

        :arg str data: Little-endian encoded integer.

        :returns int: Integer representation of {data}
        """
        # TODO: Deprecated, remove.
        deprecation_warning('int')
        return sum(ord(x) * 0x100 ** i for i, x in enumerate(data))

    def float(self, data):
        """Decode an IEEE 754 single precision encoded floating-point.

        :arg str data: Big-endian encoded 32bit single precision floating point.

        :returns float: Float representation of {data}.
        """
        # TODO: Deprecated, remove.
        deprecation_warning('float')
        return struct.unpack('>f', data)[0]

    def colour(self, data):
        # TODO: Deprecated, remove.
        deprecation_warning('colour')
        return '0x{:06x}'.format(self.int(data))

    def text(self, data, split=[], encoding='utf-8'):
        """Decode a text string.

        :arg str data: Text string.
        :arg list(byte) split: Internal delimiter for end of line.
        :arg str encoding: Character encoding.

        :returns str: Decoded text.
        """
        decoded_text = data.decode(encoding)

        if split:
            return '\n'.join(decoded_text.split(''.join(chr(x) for x in split)))
        return decoded_text

    def date(self, data, annotation):
        """Decode a date.

        The date is encoded as an integer, representing the year followed by
        the (zero padded) day of the year.

        :arg str data: Binary encoded date.
        :arg dict annotation: Names for special cases.

        :returns str: Date in format '%Y%j', 'defined' or 'unknown'.
        """
        # TODO: Deprecated, remove.
        deprecation_warning('date')
        date_int = self.int(data)

        if date_int in annotation:
            return annotation[date_int]
        return str(date_int)

    def map(self, data, annotation):
        """Replace a value with its annotation.

        :arg str data: Encoded data.
        :arg dict annotation: Annotation of {data}.

        :returns str: Annotated representation of {data}.
        """
        # TODO: Deprecated, remove.
        deprecation_warning('map')
        index = ord(data)

        if index in annotation:
            return annotation[index]
        return '{:02x}'.format(index)

    def flags(self, data, annotation):
        """Explode a bitfield into flags.

        Note that if a flag is not annotated and False, it will not be included
        in the results.

        :arg int data: Bit field.
        :arg str annotation: Annotation of {data}.

        :returns dict: Dictionary of flags and their values.
        """
        bitfield = ord(data)
        flags_dict = {}

        for flag in (2 ** x for x in range(8)):
            value = bool(flag & bitfield)

            if flag not in annotation:
                if value:
                    flags_dict['flag_{:02x}'.format(flag)] = value
            else:
                flags_dict[annotation[flag]] = value

        return flags_dict


class BinWriteFunctions(object):
    """Functions for encoding data.

    Every decoding function in the BinReadFunctions class has a counterpart for
    encoding. Documentation of these functions is omitted.
    """
    def struct(self, data, fmt='b', labels=None, annotation=None):
        if isinstance(data, collections.Mapping):
            data_list = [data[x] for x in labels]
        elif isinstance(data, list):
            data_list = data
        elif fmt == 'c':
            data_list = [data.encode('utf-8')]
        else:
            data_list = [data]

        if annotation:
            inverse_annotation = _inverse_dict(annotation)

            for index, value in enumerate(data_list):
                if value in inverse_annotation:
                    data_list[index] = inverse_annotation[value]

        return struct.pack(fmt, *data_list)

    def raw(self, hex_string):
        return codecs.decode(''.join(hex_string.split()), 'hex')

    def bit(self, bit_string):
        return chr(int('0b{}'.format(bit_string), 2)).encode('utf-8')

    def int(self, integer):
        # TODO: Deprecated, remove.
        deprecation_warning('int')
        data_int = integer
        result = ''

        while data_int:
            result += chr(data_int % 0x100)
            data_int >>= 8

        return result or chr(0x00)

    def float(self, real_number):
        # TODO: Deprecated, remove.
        deprecation_warning('float')
        return struct.pack('>f', real_number)

    def colour(self, colour_string):
        # TODO: Deprecated, remove.
        deprecation_warning('colour')
        return self.int(int(colour_string, 0x10))

    def text(self, text_string, split=[], encoding='utf-8'):
        decoded_text = text_string

        if split:
            decoded_text = ''.join(chr(x) for x in split).join(
                text_string.split('\n'))
        return decoded_text.encode(encoding)

    def date(self, date_int, annotation):
        # TODO: Deprecated, remove.
        deprecation_warning('date')
        inverse_annotation = _inverse_dict(annotation)

        if date_int in inverse_annotation:
            return self.int(inverse_annotation[date_int])
        return self.int(int(date_int))

    def map(self, mapped_string, annotation):
        # TODO: Deprecated, remove.
        deprecation_warning('map')
        inverse_annotation = _inverse_dict(annotation)

        if mapped_string in inverse_annotation:
            return chr(inverse_annotation[mapped_string])
        return chr(int(mapped_string, 0x10))

    def flags(self, flags_dict, annotation):
        inverse_annotation = _inverse_dict(annotation)
        prefix_len = len('flag_')
        values = 0x00

        for key in flags_dict:
            if flags_dict[key]:
                if key in inverse_annotation:
                    values += inverse_annotation[key]
                else:
                    values += int(key[prefix_len:], 0x10)

        return chr(values).encode('utf-8')
