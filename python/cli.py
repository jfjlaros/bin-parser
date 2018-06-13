"""Command line interface for the general binary parser."""
import argparse

import yaml

from . import usage, version, doc_split
from .bin_parser import BinReader, BinWriter


def bin_reader(
        input_handle, structure_handle, types_handle, output_handle,
        prune=False, debug=0):
    """Convert a binary file to YAML.

    :arg stream input_handle: Open readable handle to a binary file.
    :arg stream structure_handle: Open readable handle to the structure file.
    :arg stream types_handle: Open readable handle to the types file.
    :arg stream output_handle: Open writable handle.
    :arg bool prune: Remove all unknown data fields from the output.
    :arg int debug: Debugging level.
    """
    parser = BinReader(
        input_handle.read(),
        yaml.safe_load(structure_handle),
        yaml.safe_load(types_handle),
        prune=prune, debug=debug)
    output_handle.write('---\n')
    yaml.safe_dump(
        parser.parsed, output_handle, width=76, default_flow_style=False)
    if debug:
        parser.log_debug_info()


def bin_writer(
        input_handle, structure_handle, types_handle, output_handle, debug=0):
    """Convert a YAML file to binary.

    :arg stream input_handle: Open readable handle to a YAML file.
    :arg stream structure_handle: Open readable handle to the structure file.
    :arg stream types_handle: Open readable handle to the types file.
    :arg stream output_handle: Open writable handle.
    :arg int debug: Debugging level.
    """
    parser = BinWriter(
        yaml.safe_load(input_handle),
        yaml.safe_load(structure_handle),
        yaml.safe_load(types_handle),
        debug=debug)
    output_handle.write(parser.data)
    if debug:
        parser.log_debug_info()


def main():
    """Command line argument parsing."""
    bin_input_parser = argparse.ArgumentParser(add_help=False)
    bin_input_parser.add_argument(
        'input_handle', metavar='INPUT', type=argparse.FileType('rb'),
        help='input file')

    input_parser = argparse.ArgumentParser(add_help=False)
    input_parser.add_argument(
        'input_handle', metavar='INPUT', type=argparse.FileType('r'),
        help='input file')

    bin_output_parser = argparse.ArgumentParser(add_help=False)
    bin_output_parser.add_argument(
        'output_handle', metavar='OUTPUT', type=argparse.FileType('wb'),
        help='output file')
    output_parser = argparse.ArgumentParser(add_help=False)
    output_parser.add_argument(
        'output_handle', metavar='OUTPUT', type=argparse.FileType('w'),
        help='output file')

    opt_parser = argparse.ArgumentParser(add_help=False)
    opt_parser.add_argument(
        'structure_handle', metavar='STRUCTURE', type=argparse.FileType('r'),
        help='structure definition file')
    opt_parser.add_argument(
        'types_handle', metavar='TYPES', type=argparse.FileType('r'),
        help='type definition file')
    opt_parser.add_argument(
        '-d', dest='debug', type=int, default=0,
        help='debugging level (%(type)s default=%(default)s)')

    parser = argparse.ArgumentParser(
        description=usage[0], epilog=usage[1],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '-v', action='version', version=version(parser.prog))
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True

    read_parser = subparsers.add_parser(
        'read', parents=[bin_input_parser, opt_parser, output_parser],
        description=doc_split(bin_reader))
    read_parser.add_argument(
        '-p', dest='prune', default=False, action='store_true',
        help='remove unknown data fields')
    read_parser.set_defaults(func=bin_reader)

    write_parser = subparsers.add_parser(
        'write', parents=[input_parser, opt_parser, bin_output_parser],
        description=doc_split(bin_writer))
    write_parser.set_defaults(func=bin_writer)

    try:
        arguments = parser.parse_args()
    except IOError as error:
        parser.error(error)

    try:
        arguments.func(**{
            k: v for k, v in vars(arguments).items()
            if k not in ('func', 'subcommand')})
    except ValueError as error:
        parser.error(error)


if __name__ == '__main__':
    main()
