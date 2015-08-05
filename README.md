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
    types:
      int:
        read: 2
      text:
        read:
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

    bin_parser balance.dat structure.yml types.yml balance.yml

This will result in a new file, named `balance.yml`, which contains the content
of the input file (`balance.dat`) in a human (and machine) readable format:

    balance: 3210
    name: John Doe
    year_of_birth: 1999

## Using the library
To use the library from our own code, we need to use the following:

    import bin_parser

    parser = bin_parser.BinParser(open('balance.dat'), open('structure.yml'),
        open('types.yml'))
    print parser.parsed['name']

The `BinParser` object contains the original data in `data` and the parsed data
in `parsed`. Furthermore it contains the function `write` to write the content
of `parsed` in YAML format to a file handle.


# `structure.yml`: The structure of the binary file
The file `structure.yml` contains the general structure of the binary file. 

## Loops and conditionals
    - name: fixed_size_list
      for: 10
      structure:
        - name: bla
          value: something

    - name: size_of_x
      type: int
    - name: x
      for: size_of_x
      structure:
        - name: bla
          value: something

    - name: something_to_match
      type: int
    - name: x
      while:
        operands:
          - something_to_match
          - something_else_to_match
        operator: eq

      structure:
        - name: bla
          value: something
        - name: something_else_to_match
          type: int

    - name: something_to_match
      type: int
    - name: x
      do_while:
        operands:
          - something_to_match
          - something_else_to_match
        operator: eq
      structure:
        - name: bla
          value: something
        - name: something_else_to_match
          type: int

    - name: something_to_match
      type: int
    - name: something_else_to_match
      type: int
    - name: x
      if:
        operands:
          - something_to_match
          - something_else_to_match
        operator: eq
      structure:
        - name: bla
          value: something


# `types.yml`: Constants, defaults and types
The file `types.yml` consists of three (optional) sections; `types`,
`constants` and `defaults`. In general the types file will look something like
this:

    ---
    constants:
      const: 10
    defaults:
      read: 2
    types:
      int:
        read: 3

## Constants
A constant can be used as an alias in `structure.yml`. Using constants can make
conditional statements and loops more readable.

## Types
A type consists of two subunits controlling two stages; the acquirement stage
and the processing stage.

The acquirement stage is controlled by the `read` parameter, which is either
an integer or a list of characters. If an integer is passed, the parser will
read this amount of bytes, if a list is passed, the parser will read until the
supplied characters are encountered. Once the data is acquired, it is passed to
the processing stage.

The processing stage is controlled by the `function` parameter, it denotes the
function that is responsible for the processing of the acquired data.
Additional parameters for this function can be supplied by the `args`
parameter.

### Examples
The following type is stored in two bytes and is processed by the `int`
function:

    short:
      read: 2
      function:
        name: int

This type is stored in a variable size array delimited by `0x00` and is
processed by the `text` function:

    comment:
      read:
        - 0x00
      function:
        name: text

And if we need to pass additional parameters to the `text` function, in this
case split on the character `0x09`:

    comment:
      read:
        - 0x00
      function:
        name: text
        args:
          split:
            - 0x09

### Defining new types
Types can be added by subclassing the BinParseFunctions class. Suppose we need
a function that inverts all bits in a byte. We first have to make a subclass
that implements this function:

    class Invert(BinParseFunctions):
        def inv(self, data):
            return data ^ 0xff

By default, the new type will read one byte and process it with the `inv`
function. In this case there is no need to define the type in `types.yml`.

Now we can initiate the parser with this new class:

    parser = bin_parser.BinParser(open('something.dat'), open('structure.yml'),
        open('types.yml'), functions=Invert)

See `examples/prince/` for a working example.

## Defaults
To save some space and time writing our types definitions, the following
default values are used:

- `read` defaults to `1`.
- `function` defaults to the name of the type.
- The type itself defaults to `function`.
- If no name is given, the type defaults to `raw`.

So, for example, since a byte is of size 1, we can omit the `read` parameter:

    byte:
      function:
        name: int

In the next example the function `int` will be used.

    int:
      read: 2

And if we need an integer of size one which we want to name `int`, we do not
need to define anything.

### Overrides
The following defaults can be overridden by adding an entry in the `defaults`
section:

- `read`
- `type`
