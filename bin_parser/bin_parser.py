"""
General binary file parser.


(C) 2015 Jeroen F.J. Laros <J.F.J.Laros@lumc.nl>
"""


import argparse
import inspect
import os
import sys

import yaml

from functions import BinParseFunctions


class BinParser(object):
    """
    General binary file parser.
    """
    def __init__(self, input_handle, structure_handle, fields_handle,
            functions=BinParseFunctions, experimental=False, debug=0,
            log=sys.stdout):
        """
        Constructor.

        :arg stream input_handle: Open readable handle to a FAM file.
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

        self._functions = functions(fields_handle)
        self._fields = self._functions._fields     # Move to functions.py

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
            field = self.data[self._offset:].split(
                chr(self._fields['delimiters']['field']))[0]
            extracted = len(field) + 1

        if self._debug > 1:
            self._log.write('0x{:06x}: '.format(self._offset))
            if size:
                self._log.write('{} ({})'.format(_raw(field), size))
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
            destination[key].append(_raw(self._get_field(size)))
        else:
            self._get_field(size)

        self._raw_byte_count += size


    def _parse(self, structure, dest):
        """
        Parse a FAM file.

        :arg dict structure:
        :arg dict dest:
        """
        for item in structure:
            if 'structure' in item:
                if self._debug > 2:
                    self._log.write('-- {}\n'.format(item['name']))
                if item['name'] not in dest:
                    if set(['size', 'delimiter', 'count']) & set(item):
                        dest[item['name']] = []
                    else:
                        dest[item['name']] = {}
                if 'size' in item:
                    for index in range(item['size']):
                        d = {}
                        self._parse(item['structure'], d)
                        dest[item['name']].append(d)
                elif 'count' in item:
                    for index in range(self._internal[item['count']]):
                        d = {}
                        self._parse(item['structure'], d)
                        dest[item['name']].append(d)
                elif 'delimiter' in item:
                    while (self._call('int', self._get_field(1)) !=
                            self._fields['delimiters'][item['delimiter']]):
                        d = {}
                        self._parse(item['structure'], d)
                        dest[item['name']].append(d)
                else:
                    self._parse(item['structure'], dest[item['name']])
            else:
                d = dest
                if 'internal' in item:
                    d = self._internal

                size = 0
                if 'size' in item:
                    size = item['size']

                if 'type' in item:
                    if item['type'] not in ('raw', 'conditional'):
                        if 'size' in self._fields['types'][item['type']]:
                            size = self._fields['types'][item['type']]['size']

                    if item['type'] in ('map', 'text'):
                        if 'arg' in self._fields['types'][item['type']]:
                            d[item['name']] = self._call(item['type'],
                                self._get_field(size), 
                                item[self._fields['types'][item['type']]['arg']])

                    elif item['type'] == 'flags':
                        d.update(self._call('flags', self._get_field(
                            self._fields['types']['flags']['size']),
                            item['flags']))
                    elif item['type'] == 'conditional':
                        if d[item['condition']]:
                            d[item['name']] = self._get_field(size)
                    else:
                        f = item['type']
                        if item['type'] not in ('raw'):
                            if 'function' in self._fields['types'][
                                    item['type']]:
                                f = self._fields['types'][item['type']][
                                    'function']
                        d[item['name']] = self._call(f, self._get_field(size))
                else:
                    if item['name']:
                        d[item['name']] = self._get_field(size)
                    else:
                        self._parse_raw(d, size)
            if self._debug > 2:
                self._log.write(' --> {}\n'.format(item['name']))


    def write(self, output_handle):
        """
        Write the parsed FAM file to a stream.

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
