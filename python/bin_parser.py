"""General binary file parser.


(C) 2015 Jeroen F.J. Laros <J.F.J.Laros@lumc.nl>
"""
import sys

from .functions import BinReadFunctions, BinWriteFunctions, operators


def deep_update(target, source):
    """Recursively update dictionary `target` with values from `source`.

    :arg dict target: Target dictionary.
    :arg dict source: Source dictionary.
    """
    for key in source:
        if key in target and type(target[key]) == type(source[key]) == dict:
            deep_update(target[key], source[key])
        else:
            target[key] = source[key]


class BinParser(object):
    """General binary file parser.
    """
    def __init__(self, structure, types, functions, debug=0, log=sys.stderr):
        """Constructor.

        :arg dict structure: The structure definition.
        :arg dict types: The types definition.
        :arg object functions: Object containing parsing or encoding functions.
        :arg int debug: Debugging level.
        :arg stream log: Debug stream to write to.
        """
        self._internal = {}

        self._debug = debug
        self._log = log

        self._functions = functions

        self.constants = {}
        self.defaults = {
            'delimiter': [],
            'name': '',
            'size': 0,
            'trim': None,
            'order': 1,
            'type': 'text',
            'unknown_destination': '__raw__',
            'unknown_function': 'raw'
        }
        self.types = {
            'int': {},
            'raw': {},
            'text': {}
        }

        types_data = types or {}
        if 'constants' in types_data:
            deep_update(self.constants, types_data['constants'])
        if 'defaults' in types_data:
            deep_update(self.defaults, types_data['defaults'])
        if 'types' in types_data:
            deep_update(self.types, types_data['types'])

        self._structure = structure

        if self._debug & 0x02:
            self._log.write('--- PARSING DETAILS ---\n\n')

    def _call(self, name, data, *args, **kwargs):
        return getattr(self._functions, name)(data, *args, **kwargs)

    def _get_value(self, name):
        """Resolve the value of a variable.

        First look in the cache to see if `name` is defined, then check the set
        of constants. If nothing can be found, the variable is considered to be
        a literal.

        :arg any name: The name or value of a variable.
        :returns any: The resolved value.
        """
        if name in self._internal:
            return self._internal[name]
        if name in self.constants:
            return self.constants[name]
        return name

    def _get_default(self, item, dtype, name):
        """Resolve the value of a member variable.

        First see if the variable is defined in `item`, then check the type
        definition and lastly check the defaults.

        :arg dict item: Data structure.
        :arg str dtype: Name of the data type.
        :arg str name: The name of the variable.

        :returns any: The resolved value.
        """
        if name in item:
            return item[name]
        if dtype in self.types and name in self.types[dtype]:
            return self.types[dtype][name]
        if name in self.defaults:
            return self.defaults[name]
        return None

    def _get_function(self, item, dtype):
        """Determine what to read and how to interpret what was read.

        First resolve the `delimiter` and `size`. If none are given, assume we
        read one byte. Then resolve the function that will interpret the data
        (either delimited or fixed size).

        :arg dict item: Data structure.
        :arg str dtype: Name of the data type.

        :returns tuple: (`delim`, `size`, `trim`, `order`, `func`, `kwargs`).
        """
        delim = self._get_default(item, dtype, 'delimiter')
        size = self._get_value(self._get_default(item, dtype, 'size'))
        trim = self._get_default(item, dtype, 'trim')
        order = self._get_default(item, dtype, 'order')
        if not (delim or size):
            size = 1

        # Determine the function and its arguments.
        func = dtype
        kwargs = {}
        if 'function' in self.types[dtype]:
            if 'name' in self.types[dtype]['function']:
                func = self.types[dtype]['function']['name']
            if 'args' in self.types[dtype]['function']:
                kwargs = self.types[dtype]['function']['args']

        return delim, size, trim, order, func, kwargs

    def _evaluate(self, expression):
        """Evaluate an expression.

        An expression is represented by a dictionary with the following
        structure:

            expression = {
                'operator': '',
                'operands': []
            }

        :arg dict expression: An expression.
        :returns any: Result of the evaluation.
        """
        operands = map(lambda x: self._get_value(x), expression['operands'])

        if len(operands) == 1 and 'operator' not in expression:
            return operands[0]
        return operators[expression['operator']](*operands)

    def _log_debug_info(self):
        """Write additional debugging information to the log.
        """
        if self._debug & 0x01:
            if self._debug & 0x02:
                self._log.write('\n\n')
            self._log.write('--- INTERNAL VARIABLES ---\n\n')
            for item in self._internal:
                self._log.write('{}: {}\n'.format(item, self._internal[item]))

        self._log.write('\n\n--- DEBUG INFO ---\n\n')


class BinReader(BinParser):
    """General binary file reader.
    """
    def __init__(
            self, data, structure, types, functions=BinReadFunctions(),
            prune=False, debug=0, log=sys.stderr):
        """Constructor.

        :arg stream data: Content of a binary file.
        :arg dict structure: The structure definition.
        :arg dict types: The types definition.
        :arg object functions: Object containing parsing functions.
        :arg bool prune: Remove all unknown data fields from the output.
        :arg int debug: Debugging level.
        :arg stream log: Debug stream to write to.
        """
        super(BinReader, self).__init__(
            structure, types, functions, debug, log)

        self._prune = prune

        self.data = data
        self.parsed = {}
        self._offset = 0
        self._raw_byte_count = 0

        try:
            self._parse(self._structure, self.parsed)
        except StopIteration:
            pass

    def _get_field(self, size=0, delimiter=[], trim=None, order=1):
        """Extract a field from {self.data} using either a fixed size, or a
        delimiter. After reading, {self._offset} is set to the next field.

        :arg int size: Size of fixed size field.
        :arg list(char) delimiter: Delimiter for variable sized fields.
        :arg byte trim: Padding character.
        :arg int order: Byte order.

        :return str: Content of the requested field.
        """
        if self._offset >= len(self.data):
            raise StopIteration

        separator = ''.join(map(chr, delimiter))

        if size:
            # Fixed sized field.
            field = self.data[self._offset:self._offset + size]
            extracted = size
            if delimiter:
                # A variable sized field in a fixed sized field.
                field = field.split(separator)[0]
        else:
            # Variable sized field.
            field = self.data[self._offset:].split(separator)[0]
            extracted = len(field) + 1 # FIXME: len(separator)

        # Endianness.
        field = field[::order]

        if trim:
            # Strip trailing characters.
            field = field.rstrip(chr(trim))

        if self._debug & 0x02:
            self._log.write('0x{:06x}: '.format(self._offset))
            if size:
                self._log.write('{} ({})'.format(self._call(
                    'raw', field), size))
            else:
                self._log.write('{}'.format(field))

        self._offset += extracted
        return field

    def _parse_primitive(self, item, dtype, dest, name):
        """Parse a primitive data type.

        :arg dict item: Data structure.
        :arg str dtype: Data type.
        :arg dict dest: Destination dictionary.
        :arg str name: Field name used in the destination dictionary.
        """
        # Read and process the data.
        if not name:
            dtype = self._get_default(item, '', 'unknown_function')
        delim, size, trim, order, func, kwargs = self._get_function(
            item, dtype)
        result = self._call(
            func, self._get_field(size, delim, trim, order), **kwargs)

        if name:
            # Store the data.
            if type(result) == dict:
                # Unpack dictionaries in order to use the items in evaluations.
                for member in result:
                    self._internal[member] = result[member]
            else:
                self._internal[name] = result
            dest[name] = result
        else:
            # Stow unknown data away in a list.
            if not self._prune:
                unknown_dest = self._get_default(
                    item, dtype, 'unknown_destination')
                if unknown_dest not in dest:
                    dest[unknown_dest] = []
                dest[unknown_dest].append(result)
            self._raw_byte_count += size

    def _parse_for(self, item, dest, name):
        """Parse a for loop.

        :arg dict item: Data structure.
        :arg dict dest: Destination dictionary.
        :arg str name: Field name used in the destination dictionary.
        """
        length = item['for']
        if type(length) != int:
            length = self._internal[length]

        for _ in range(length):
            structure_dict = {}
            self._parse(item['structure'], structure_dict)
            dest[name].append(structure_dict)

    def _parse_do_while(self, item, dest, name):
        """Parse a do-while loop.

        :arg dict item: Data structure.
        :arg dict dest: Destination dictionary.
        :arg str name: Field name used in the destination dictionary.
        """
        while True:
            structure_dict = {}
            self._parse(item['structure'], structure_dict)
            dest[name].append(structure_dict)
            if not self._evaluate(item['do_while']):
                break

    def _parse_while(self, item, dest, name):
        """Parse a while loop.

        :arg dict item: Data structure.
        :arg dict dest: Destination dictionary.
        :arg str name: Field name used in the destination dictionary.
        """
        delim = item['structure'][0]

        dest[name] = [{}]
        self._parse([delim], dest[name][0])
        while True:
            if not self._evaluate(item['while']):
                break
            self._parse(item['structure'][1:], dest[name][-1])
            dest[name].append({})
            self._parse([delim], dest[name][-1])

        dest[item['while']['term']] = dest[name].pop(-1).values()[0]

    def _parse(self, structure, dest):
        """Parse a binary file.

        :arg dict structure: Structure of the binary file.
        :arg dict dest: Destination dictionary.
        """
        for item in structure:
            if 'if' in item:
                # Conditional statement.
                if not self._evaluate(item['if']):
                    continue

            dtype = self._get_default(item, '', 'type')
            name = self._get_default(item, dtype, 'name')

            if 'structure' not in item:
                # Primitive data types.
                self._parse_primitive(item, dtype, dest, name)
            else:
                # Nested structures.
                if self._debug & 0x02:
                    self._log.write('-- {}\n'.format(name))

                if name not in dest:
                    if set(['for', 'do_while', 'while']) & set(item):
                        dest[name] = []
                    else:
                        dest[name] = {}

                if 'for' in item:
                    self._parse_for(item, dest, name)
                elif 'do_while' in item:
                    self._parse_do_while(item, dest, name)
                elif 'while' in item:
                    self._parse_while(item, dest, name)
                else:
                    self._parse(item['structure'], dest[name])

            if self._debug & 0x02:
                self._log.write(' --> {}\n'.format(name))

    def log_debug_info(self):
        """Write additional debugging information to the log.
        """
        self._log_debug_info()

        data_length = len(self.data)
        parsed = data_length - self._raw_byte_count

        self._log.write('Reached byte {} out of {}.\n'.format(
            self._offset, data_length))
        self._log.write('{} bytes parsed ({:d}%).\n'.format(
            parsed, parsed * 100 // data_length))


class BinWriter(BinParser):
    """General binary file writer.
    """
    def __init__(
            self, parsed, structure, types, functions=BinWriteFunctions(),
            debug=0, log=sys.stderr):
        """Constructor.

        :arg dict parsed: Parsed representation of a binary file.
        :arg dict structure: The structure definition.
        :arg dict types: The types definition.
        :arg object functions: Object containing parsing functions.
        :arg int debug: Debugging level.
        :arg stream log: Debug stream to write to.
        """
        super(BinWriter, self).__init__(
            structure, types, functions, debug, log)

        self.data = ''
        self.parsed = parsed

        self._encode(self._structure, self.parsed)

    def _set_field(self, data, size=0, delimiter=[], trim=None, order=1):
        """Append a field to {self.data} using either a fixed size, or a
        delimiter.

        :arg int data: The content of the field.
        :arg int size: Size of fixed size field.
        :arg list(char) delimiter: Delimiter for variable sized fields.
        :arg byte trim: Padding character.
        :arg int order: Byte order.
        """
        field = data

        # Pad the field if necessary.
        field += chr(trim or 0x00) * (size - len(field))

        # Endianness.
        field = field[::order]

        if delimiter:
            # Add the delimiter for variable length fields.
            field += ''.join(map(chr, delimiter))
        if size:
            # Clip the field if it is too large.
            # NOTE: This can result in a non-delimited trimmed field.
            field = field[:size]

        self.data += field

    def _encode_primitive(self, item, dtype, value, name):
        """Encode a primitive data type.

        :arg dict item: Data structure.
        :arg str dtype: Data type.
        :arg unknown value: Value to be stored.
        :arg str name: Field name used in the destination dictionary.
        """
        delim, size, trim, order, func, kwargs = self._get_function(
            item, dtype)

        if type(value) == dict:
            # Unpack dictionaries in order to use the items in evaluations.
            for member in value:
                self._internal[member] = value[member]
        else:
            self._internal[name] = value

        self._set_field(
            self._call(func, value, **kwargs), size, delim, trim, order)

    def _get_item(self, item):
        """Resolve the `term` field in the `while` structure.

        :arg dict item: Data structure.

        :returns dict: Item that `term` points to.
        """
        for operand in item['while']['operands']:
            for field in item['structure']:
                if operand == field['name']:
                    return field

        return None

    def _encode(self, structure, source):
        """Encode to a binary file.

        :arg dict structure: Structure of the binary file.
        :arg dict source: Source dictionary.
        """
        raw_counter = 0

        for item in structure:
            if 'if' in item:
                # Conditional statement.
                if not self._evaluate(item['if']):
                    continue

            dtype = self._get_default(item, '', 'type')
            name = self._get_default(item, dtype, 'name')

            if not name:
                # NOTE: Not sure if this is correct.
                dtype = self._get_default(item, dtype, 'unknown_function')
                value = source[self._get_default(
                    item, dtype, 'unknown_destination')][raw_counter]
                raw_counter += 1
            else:
                value = source[name]

            if 'structure' not in item:
                # Primitive data types.
                if self._debug & 0x02:
                    self._log.write('0x{:06x}: {} --> {}\n'.format(
                        len(self.data), name, value))

                self._encode_primitive(item, dtype, value, name)
            else:
                # Nested structures.
                if self._debug & 0x02:
                    self._log.write('-- {}\n'.format(name))

                if set(['for', 'do_while', 'while']) & set(item):
                    for subitem in value:
                        self._encode(item['structure'], subitem)
                    if 'while' in item:
                        term = self._get_item(item)
                        self._encode(
                            [term],
                            {term['name']: source[item['while']['term']]})
                else:
                    self._encode(item['structure'], value)

                if self._debug & 0x02:
                    self._log.write(' --> {}\n'.format(name))

    def log_debug_info(self):
        """Write additional debugging information to the log.
        """
        self._log_debug_info()

        self._log.write('{} bytes written.\n'.format(len(self.data)))
