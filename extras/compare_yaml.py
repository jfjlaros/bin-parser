"""Compare two YAML files.


(C) 2015 Jeroen F.J. Laros <J.F.J.Laros@lumc.nl>

Licensed under the MIT license, see the LICENSE file.
"""
import argparse

import yaml


def dict_compare(d1, d2):
    """Compare two nested dictionaries.

    :arg dict d1: A nested dictionary.
    :arg dict d2: An other nested dictionary.
    """
    if type(d1) == dict:
        for key in set(list(d1.keys()) + list(d2.keys())):
            if key in d1 and key in d2:
                dict_compare(d1[key], d2[key])
            else:
                print('missing key: {}\n'.format(key))
    elif type(d1) == list:
        if len(d1) != len(d2):
            print('lists of different length\n')
        else:
            for index in range(len(d1)):
                dict_compare(d1[index], d2[index])
    else:
        if d1 != d2:
            print('{} != {}\n'.format(d1, d2))


def yaml_compare(input_handle_1, input_handle_2):
    """Compare two YAML files.

    :arg stream input_handle_1: Open readable handle to a YAML file.
    :arg stream input_handle_2: Open readable handle to an other YAML file.
    """
    dict_compare(yaml.load(input_handle_1), yaml.load(input_handle_2))


def main():
    """Main entry point."""
    usage = __doc__.split('\n\n\n')
    parser = argparse.ArgumentParser(description=usage[0], epilog=usage[1],
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('input_handle', metavar='INPUT',
        type=argparse.FileType('r'), nargs=2, help='input file in YAML format')

    try:
        arguments = parser.parse_args()
    except IOError as error:
        parser.error(error)

    yaml_compare(*arguments.input_handle)


if __name__ == '__main__':
    main()
