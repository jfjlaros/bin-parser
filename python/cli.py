import argparse

from . import usage, version
from .bin_parser import BinParser


def bin_parser(
        input_handle, structure_handle, types_handle, output_handle,
        experimental=False, debug=0):
    """
    Main entry point.

    :arg stream input_handle: Open readable handle to a binary file.
    :arg stream structure_handle: Open readable handle to the structure file.
    :arg stream types_handle: Open readable handle to the types file.
    :arg stream output_handle: Open writable handle.
    :arg bool experimental: Enable experimental features.
    :arg int debug: Debugging level.
    """
    parser = BinParser(
        input_handle, structure_handle, types_handle,
        experimental=experimental, debug=debug)
    parser.write(output_handle)


def main():
    """
    Command line argument parsing.
    """
    parser = argparse.ArgumentParser(
        description=usage[0], epilog=usage[1],
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        'input_handle', metavar='INPUT', type=argparse.FileType('r'),
        help='input file')
    parser.add_argument(
        'structure_handle', metavar='STRUCTURE', type=argparse.FileType('r'),
        help='structure definition file')
    parser.add_argument(
        'types_handle', metavar='TYPES', type=argparse.FileType('r'),
        help='type definition file')
    parser.add_argument(
        'output_handle', metavar='OUTPUT', type=argparse.FileType('w'),
        help='output file')
    parser.add_argument('-d', dest='debug', type=int, help='debugging level')
    parser.add_argument(
        '-e', dest='experimental', action='store_true',
        help='enable experimental features')
    parser.add_argument('-v', action='version', version=version(parser.prog))

    try:
        arguments = parser.parse_args()
    except IOError as error:
        parser.error(error)

    try:
        bin_parser(**dict(
            (k, v) for k, v in vars(arguments).items()
            if k not in ('func', 'subcommand')))
    except ValueError as error:
        parser.error(error)


if __name__ == '__main__':
    main()
