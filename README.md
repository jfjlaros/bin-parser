# General binary file parser
This library aims at general binary file parsing by interpreting documentation
of the file structure and the types used. It supports basic data types like
integers, variable length (delimited) strings, dates, maps and bit fields
(flags) and it can iterate over sub structures.

## Why use this library?
The challenge of parsing binary files is not a new one, it requires reverse
engineering skills, knowledge of encodings, but above all, patience and
intuition. Once all knowledge is gathered, the person doing the reverse
engineering usually writes a parser for the binary file and, if we are lucky,
leaves some documentation. We try to facilitate this process by providing the
tools to do this in a uniform way. In essence, we document the knowledge we
gain from the reverse engineering process and use this documentation directly
in a parser.

Since the bulk of the types stored in binary files are standard, dedicated
parsers contain a lot of boiler plate code. {{MORE}}

# Approach
In order to parse a binary file, the library needs two pieces of information:
it needs to know what the structure of the binary file is and it needs to know
which types are used. Both of these information sources are provided to the
library in YAML format.

## Example: Account balance
Suppose we have a file (`balance.dat`) that contains the following:

- A year of birth (two byte integer).
- A name (zero delimited string).
- Account balance (an other two byte integer).

To make a parser for this type of file, we need to create a file that contains
the type definitions. We name this file `types.yml`.

    ---
    int:
      size: 2
    text:
      delimiter:
        - 0x00

Then we create a file that contains the definition of the structure. This file
we name `structure.yml`.

    ---
    - name: year_of_birth
      type: int
    - name: name
      type: text
    - name: balance
      type: int

We can now call the command line interface as follows:

    bin-parser balance.dat structure.yml fields.yml balance.yml

This will result in a new file, named `balance.yml`, which contains the content
of the input file (`balance.dat`) in a human (and machine) readable format:

    balance: 3210
    name: John Doe
    year_of_birth: 1999

## Using the library
To use the library from our own code, we need to use the following:

    from bin_parser import BinParser

    parser = BinParser(open('balance.dat'), open('types.yml'),
        open('structure.yml')
    print parser.fields['name']

The `BinParser` object contains the original data in `data` and the parsed data
in `parsed`. Furthermore it contains the function `write` to write the content
of `parsed` in YAML format to a file handle.

# `types.yml`
This file contains the types used in `structure.yml`. A type contains a subset
of the following fields:

- name
- size
- function
- delimiter
- data
- arg

# `structure.yml`

# Defaults

# Defining new types
