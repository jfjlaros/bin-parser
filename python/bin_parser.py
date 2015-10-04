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
    def __init__(
            self, input_handle, structure_handle, types_handle,
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

        self._functions = functions()

        tdata = yaml.load(types_handle)
        self.types = tdata['types'] if 'types' in tdata else {}
        self.constants = tdata['constants'] if 'constants' in tdata else {}
        self.defaults = tdata['defaults'] if 'defaults' in tdata else {}

        # Add standard data types.
        self.types['raw'] = {}
        self.types['list'] = {}

        # Set default data type.
        if 'type' not in self.defaults:
            self.defaults['type'] = 'text'

        self._offset = 0
        self._raw_byte_count = 0

        structure = yaml.load(structure_handle)
        try:
            self._parse(structure, self.parsed)
        except StopIteration:
            pass

    def _call(self, name, data, *args, **kwargs):
        return getattr(self._functions, name)(data, *args, **kwargs)

    def _get_field(self, size=0, delimiter=[]):
        """
        Extract a field from {self.data} using either a fixed size, or a
        delimiter. After reading, {self._offset} is set to the next field.

        :arg int size: Size of fixed size field.
        :arg list(char) delimiter: Delimiter for variable sized fields.

        :return str: Content of the requested field.
        """
        if self._offset >= len(self.data):
            raise StopIteration

        if size:
            field = self.data[self._offset:self._offset + size]
            extracted = size
        else:
            field = self.data[self._offset:].split(
                ''.join(map(chr, delimiter)))[0]
            extracted = len(field) + 1

        if self._debug > 1:
            self._log.write('0x{:06x}: '.format(self._offset))
            if size:
                self._log.write('{} ({})'.format(self._call(
                    'raw', field), size))
            else:
                self._log.write('{}'.format(field))
            if self._debug < 3:
                self._log.write('\n')

        self._offset += extracted
        return field

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
        if name in self.constants:
            return self.constants[name]
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
            if key not in destination:
                destination[key] = []
            destination[key].append(self._call('raw', self._get_field(size)))
        else:
            self._get_field(size)

        self._raw_byte_count += size

    def _parse_primitive(self, item, dtype, dest, name):
        """
        Parse a primitive data type.

        :arg dict item: A dictionary.
        :arg str dtype: Data type.
        :arg dict dest: Destination dictionary.
        :arg str name: Field name used in the destination dictionary.
        """
        # Determine whether to read a fixed or variable amount.
        delim = []
        size = (self.defaults['read'] if 'read' in self.defaults else 1)
        if 'read' in item:
            size = item['read']
        elif 'read' in self.types[dtype]:
            if type(self.types[dtype]['read']) == list:
                size = 0
                delim = self.types[dtype]['read']
            else:
                size = self.types[dtype]['read']

        if name:
            # Determine the function and its arguments.
            func = dtype
            kwargs = {}
            if 'function' in self.types[dtype]:
                if 'name' in self.types[dtype]['function']:
                    func = self.types[dtype]['function']['name']
                if 'args' in self.types[dtype]['function']:
                    kwargs = self.types[dtype]['function']['args']

            # Read and process the data.
            result = self._call(func, self._get_field(size, delim), **kwargs)
            if type(result) == dict:
                for member in result:
                    dest[member] = result[member]
                    self._internal[member] = result[member]
            else:
                dest[name] = result
                self._internal[name] = result
        else:
            self._parse_raw(dest, size)

    def _parse_for(self, item, dest, name):
        """
        Parse a for loop.

        :arg dict item: A dictionary.
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
        """
        Parse a do-while loop.

        :arg dict item: A dictionary.
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
        """
        Parse a while loop.

        :arg dict item: A dictionary.
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
        """
        Parse a binary file.

        :arg dict structure: Structure of the binary file.
        :arg dict dest: Destination dictionary.
        """
        for item in structure:
            if 'if' in item:
                # Conditional statement.
                if not self._evaluate(item['if']):
                    continue

            name = item['name'] if 'name' in item else ''
            dtype = item['type'] if 'type' in item else self.defaults['type']

            if 'structure' not in item:
                # Primitive data types.
                self._parse_primitive(item, dtype, dest, name)
            else:
                # Nested structures.
                if self._debug > 2:
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
        output_handle.write('---\n')
        yaml.dump(
            self.parsed, output_handle, width=76, default_flow_style=False)

        if self._debug:
            output_handle.write('\n\n--- INTERNAL VARIABLES ---\n\n')
            yaml.dump(
                self._internal, output_handle, width=76,
                default_flow_style=False, encoding=None)

            data_length = len(self.data)
            parsed = data_length - self._raw_byte_count

            output_handle.write('\n\n--- DEBUG INFO ---\n\n')
            output_handle.write('Reached byte {} out of {}.\n'.format(
                self._offset, data_length))
            output_handle.write('{} bytes parsed ({:d}%)\n'.format(
                parsed, parsed * 100 // len(self.data)))
