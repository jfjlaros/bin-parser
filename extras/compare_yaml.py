import argparse

import yaml

from . import usage, version


def dict_compare(d1, d2):
    if type(d1) == dict:
        for key in set(d1.keys() + d2.keys()):
            if key in d1 and key in d2:
                dict_compare(d1[key], d2[key])
            else:
                print 'missing key: {}'.format(key)
    elif type(d1) == list:
        if len(d1) != len(d2):
            print 'lists of different length'
        else:
            for index in range(len(d1)):
                dict_compare(d1[index], d2[index])
    else:
        if d1 != d2:
            print '{} != {}'.format(d1, d2)


def yaml_compare(input_handle_1, input_handle_2):
    dict_compare(yaml.load(input_handle_1), yaml.load(input_handle_2))


def main():
    parser = argparse.ArgumentParser(description=usage[0], epilog=usage[1],
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('input_handle', metavar='INPUT',
        type=argparse.FileType('r'), nargs=2, help='input file in YAML format')
    parser.add_argument('-v', action='version', version=version(parser.prog))

    try:
        arguments = parser.parse_args()
    except IOError as error:
        parser.error(error)

    yaml_compare(*arguments.input_handle)


if __name__ == '__main__':
    main()
