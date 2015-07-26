"""
General binary file parser.


(C) 2015 Jeroen F.J. Laros <J.F.J.Laros@lumc.nl>
"""


import sys

import yaml

from functions import BinParseFunctions, operators


class BinParser(object):
    """
    General binary file parser.
    """
    def __init__(self, input_handle, structure_handle, types_handle,
            functions=BinParseFunctions, experimental=False, debug=0,
            log=sys.stdout):
        """
        Constructor.

        :arg stream input_handle: Open readable handle to a binary file.
        :arg stream structure_handle: Open readable handle to the structure
            definition.
        :arg stream types_handle: Open readable handle to the types definition.
        :arg object functions: Object containing parsing functions.
        :arg bool experimental: Enable experimental features.
        :arg int debug: Debugging level.
        :arg stream log: Debug stream to write to.
        """
        self.data = input_handle.read()
        self.parsed = {}
        self._internal = {}

        self._debug = debug
        self._experimental = experimental | bool(debug)
        self._log = log

        self._functions = functions(types_handle)
        self._types = self._functions._types

        self._offset = 0
        self._raw_byte_count = 0

        structure = yaml.load(structure_handle)
        self._parse(structure, self.parsed)


    def _call(self, name, data, *args):
        return getattr(self._functions, name)(data, *args)


    def _get_field(self, size=0):
        """
        Extract a field from {self.data} using either a fixed size, or a
        delimiter. After reading, {self._offset} is set to the next field.

        :arg int size: Size of fixed size field.

        :return str: Content of the requested field.
        """
        if size:
            field = self.data[self._offset:self._offset + size]
            extracted = size
        else:
            field = self._call('text', self.data[self._offset:])
            extracted = len(field) + 1

        if self._debug > 1:
            self._log.write('0x{:06x}: '.format(self._offset))
            if size:
                self._log.write('{} ({})'.format(self._call('raw', field),
                    size))
            else:
                self._log.write('{}'.format(field))
            if self._debug < 3:
                self._log.write('\n')

        self._offset += extracted
        return field


    def _parse_raw(self, destination, size, key='raw'):
        """
        Stow unknown data away in a list.

        This function is needed to skip data of which the function is unknown.
        If `self._experimental` is set to `True`,  the data is placed in an
        appropriate place. This is mainly for debugging purposes.

        Ideally, this function will become obsolete (when we have finished the
        reverse engineering completely).

        :arg dict destination: Destination dictionary.
        :arg int size: Bytes to be stowed away (see `_get_field`).
        :arg str key: Name of the list to store the data in.
        """
        if self._experimental:
            if not key in destination:
                destination[key] = []
            destination[key].append(self._call('raw', self._get_field(size)))
        else:
            self._get_field(size)

        self._raw_byte_count += size


    def _set(self, item, field, default):
        """
        Return `field[name]` if it exists, otherwise return `default`.

        :arg dict item: A dictionary.
        :arg str field: A field that may or may not be present in `item`.
        :arg any default: Default value if `field[name]` does not exist.

        :returns any: `field[name]` or `default`.
        """
        if field in item:
            return item[field]
        return default


    def _store(self, dest, name, value):
        """
        Store a value both in the destination dictionary, as well as in the
        internal cache.

        :arg dict dest: Destination dictionary.
        :arg str name: Field name used in the destination dictionary.
        :arg any value: Value to store.
        """
        dest[name] = value
        self._internal[name] = value


    def _get_value(self, name):
        """
        Resolve the value of a variable.

        First look in the cache to see if `name` is defined, then check the set
        of constants. If nothing can be found, the variable is considered to be
        a literal.

        :arg any name: The name or value of a variable.
        :returns: The resolved value.
        """
        if name in self._internal:
            return self._internal[name]
        if 'constants' in self._types and name in self._types['constants']:
            return self._types['constants'][name]
        return name


    def _evaluate(self, expression):
        """
        Evaluate an expression.

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


    def _parse_structure(self, item, dest, name):
        """
        Convenience function for nested structures.

        :arg dict item: A dictionary.
        :arg dict dest: Destination dictionary.
        :arg str name: Field name used in the destination dictionary.
        """
        structure_dict = {}
        self._parse(item['structure'], structure_dict)
        dest[name].append(structure_dict)


    def _parse(self, structure, dest):
        """
        Parse a binary file.

        :arg dict structure: Structure of the binary file.
        :arg dict dest: Destination dictionary.
        """
        for item in structure:
            name = self._set(item, 'name', '')

            dtype = self._set(item, 'type', self._types['default'])
            if 'structure' in item:
                dtype = 'list'

            # Conditional statement.
            if 'if' in item:
                if not self._evaluate(item['if']):
                    continue

            # Primitive data types.
            if dtype != 'list':
                size = self._set(self._types[dtype], 'size',
                    self._set(item, 'size', 0))
                if type(size) != int:
                    size = self._internal[size]

                if dtype == 'flags':
                    flags = self._call('flags', self._get_field(size),
                        item['flags'])
                    for name in flags:
                        self._store(dest, name, flags[name])
                elif name:
                    function = self._set(self._types[dtype], 'function', dtype)
                    args = self._set(item,
                        self._set(self._types[dtype], 'arg', ''), ())
                    if args:
                        args = (args, )
                    self._store(dest, name,
                        self._call(function, self._get_field(size), *args))
                else:
                    self._parse_raw(dest, size)
            # Nested structures.
            else:
                if self._debug > 2:
                    self._log.write('-- {}\n'.format(name))

                if name not in dest:
                    if set(['for', 'do_while', 'while']) & set(item):
                        dest[name] = []
                    else:
                        dest[name] = {}

                if 'for' in item:
                    length = item['for']
                    if type(length) != int:
                        length = self._internal[length]
                    for _ in range(length):
                        self._parse_structure(item, dest, name)
                elif 'do_while' in item:
                    while True:
                        self._parse_structure(item, dest, name)
                        if not self._evaluate(item['do_while']):
                            break
                elif 'while' in item:
                    delimiter = item['structure'][0]
                    dest[name] = [{}]
                    self._parse([delimiter], dest[name][0])
                    while True:
                        if not self._evaluate(item['while']):
                            break
                        self._parse(item['structure'][1:], dest[name][-1])
                        dest[name].append({})
                        self._parse([delimiter], dest[name][-1])
                    dest[item['while']['term']] = dest[name].pop(
                        -1).values()[0]
                else:
                    self._parse(item['structure'], dest[name])

            if self._debug > 2:
                self._log.write(' --> {}\n'.format(name))


    def write(self, output_handle):
        """
        Write the parsed binary file to a stream.

        :arg stream output_handle: Open writable handle.
        """
        if self._debug > 1:
            output_handle.write('\n\n')

        if self._debug:
            output_handle.write('--- YAML DUMP ---\n\n')
        yaml.dump(self.parsed, output_handle, width=76,
            default_flow_style=False)

        if self._debug:
            output_handle.write('\n\n--- INTERNAL VARIABLES ---\n\n')
            yaml.dump(self._internal, output_handle, width=76,
                default_flow_style=False)

            data_length = len(self.data)
            parsed = data_length - self._raw_byte_count

            output_handle.write('\n\n--- DEBUG INFO ---\n\n')
            output_handle.write('Reached byte {} out of {}.\n'.format(
                self._offset, data_length))
            output_handle.write('{} bytes parsed ({:d}%)\n'.format(
                parsed, parsed * 100 // len(self.data)))
