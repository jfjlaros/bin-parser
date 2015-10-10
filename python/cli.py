import argparse

from . import usage, version, doc_split
from .bin_parser import BinReader, BinWriter


def bin_reader(
        input_handle, structure_handle, types_handle, output_handle, debug=0):
    """
    Convert a binary file to YAML.

    :arg stream input_handle: Open readable handle to a binary file.
    :arg stream structure_handle: Open readable handle to the structure file.
    :arg stream types_handle: Open readable handle to the types file.
    :arg stream output_handle: Open writable handle.
    :arg int debug: Debugging level.
    """
    parser = BinReader(
        input_handle, structure_handle, types_handle, debug=debug)
    parser.write(output_handle)


def bin_writer(
        input_handle, structure_handle, types_handle, output_handle, debug=0):
    """
    Convert a YAML file to binary.

    :arg stream input_handle: Open readable handle to a YAML file.
    :arg stream structure_handle: Open readable handle to the structure file.
    :arg stream types_handle: Open readable handle to the types file.
    :arg stream output_handle: Open writable handle.
    :arg int debug: Debugging level.
    """
    parser = BinWriter(
        input_handle, structure_handle, types_handle, debug=debug)
    parser.write(output_handle)


def main():
    """
    Command line argument parsing.
    """
    opt_parser = argparse.ArgumentParser(add_help=False)
    opt_parser.add_argument(
        'input_handle', metavar='INPUT', type=argparse.FileType('r'),
        help='input file')
    opt_parser.add_argument(
        'structure_handle', metavar='STRUCTURE', type=argparse.FileType('r'),
        help='structure definition file')
    opt_parser.add_argument(
        'types_handle', metavar='TYPES', type=argparse.FileType('r'),
        help='type definition file')
    opt_parser.add_argument(
        'output_handle', metavar='OUTPUT', type=argparse.FileType('w'),
        help='output file')
    opt_parser.add_argument(
        '-d', dest='debug', type=int, help='debugging level')

    parser = argparse.ArgumentParser(
        description=usage[0], epilog=usage[1],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '-v', action='version', version=version(parser.prog))
    subparsers = parser.add_subparsers()

    read_parser = subparsers.add_parser(
        'read', parents=[opt_parser], description=doc_split(bin_reader))
    read_parser.set_defaults(func=bin_reader)

    write_parser = subparsers.add_parser(
        'write', parents=[opt_parser], description=doc_split(bin_writer))
    write_parser.set_defaults(func=bin_writer)

    try:
        arguments = parser.parse_args()
    except IOError as error:
        parser.error(error)

    try:
        arguments.func(**dict(
            (k, v) for k, v in vars(arguments).items()
            if k not in ('func', 'subcommand')))
    except ValueError as error:
        parser.error(error)


if __name__ == '__main__':
    main()
