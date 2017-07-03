#!/usr/bin/env python
"""
Use an example file and a delimiter to extract a rudimentary structure and a
types definition.
"""
import argparse
import yaml


class HexInt(int):
    pass


def representer(dumper, data):
    return yaml.ScalarNode('tag:yaml.org,2002:int', '0x{:02x}'.format(data))


def hex_int(string):
    return int(string, 16)


def make_structure(data, delimiter):
    """
    Split the input data and extract a rudimentary structure.

    :arg str data: The input data.
    :arg list(int) delimiter: The delimiter to split {data}.
    """
    structure = []

    for index in range(len(data.split(''.join(map(chr, delimiter))))):
        structure.append({
            'name': 'field_{:06d}'.format(index),
            'type': 'raw'
        })

    return structure


def make_types(delimiter):
    return {
        'types': {
            'raw': {
                'delimiter': map(HexInt, delimiter),
                'function': {
                    'name': 'raw'
                }
            },
            'text': {
                'delimiter': map(HexInt, delimiter)
            }
        }
    }


def make_skeleton(input_handle, structure_handle, types_handle, delimiter):
    """
    Use an example file and a delimiter to extract a rudimentary structure and
    a types definition.

    :arg stream input_handle:
    :arg stream structure_handle:
    :arg stream types_handle:
    :arg list(int) delimiter: The delimiter.
    """
    yaml.add_representer(HexInt, representer)

    structure_handle.write('---\n')
    structure_handle.write(
        yaml.safe_dump(
            make_structure(input_handle.read(), delimiter),
        width=76, default_flow_style=False))
    types_handle.write('---\n')
    types_handle.write(
        yaml.dump(make_types(delimiter), width=76,
        default_flow_style=False))


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(
        description=__doc__.split('\n\n')[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        'input_handle', metavar='INPUT', type=argparse.FileType('r'),
        help='input file')
    parser.add_argument(
        'structure_handle', metavar='STRUCTURE', type=argparse.FileType('w'),
        help='structure definition file')
    parser.add_argument(
        'types_handle', metavar='TYPES', type=argparse.FileType('w'),
        help='types definition file')
    parser.add_argument(
        '-d', dest='delimiter', type=hex_int, action='append', default=[],
        help='delimiter (use multiple times for multi byte delimiters)')

    args = parser.parse_args()

    make_skeleton(
        args.input_handle, args.structure_handle, args.types_handle,
        args.delimiter)


if __name__ == '__main__':
    main()
