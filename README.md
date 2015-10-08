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

# Installation

For Python:

    pip install bin-parser

For JavaScipt

    npm install bin-parser

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

```yml
 ---
 types:
   int:
     read: 2
   text:
     read:
       - 0x00
```

Then we create a file that contains the definition of the structure. This file
we name `structure.yml`.

```yml
---
- name: year_of_birth
  type: int
- name: name
  type: text
- name: balance
  type: int
```

We can now call the command line interface as follows:

    bin_parser balance.dat structure.yml types.yml balance.yml

This will result in a new file, named `balance.yml`, which contains the content
of the input file (`balance.dat`) in a human (and machine) readable format:

```yml
balance: 3210
name: John Doe
year_of_birth: 1999
```

## Using the library
To use the library from our own code, we need to use the following:

```python
import bin_parser

parser = bin_parser.BinReader(
    open('balance.dat'), open('structure.yml'), open('types.yml'))
print parser.parsed['name']
```

The `BinReader` object contains the original data in `data` and the parsed data
in `parsed`. Furthermore it contains the function `write` to write the content
of `parsed` in YAML format to a file handle.


# `structure.yml`: The structure of the binary file
The file `structure.yml` contains the general structure of the binary file.

## Loops and conditionals
Both loops and conditionals (except the `for` loop) are controlled by an
evaluation of a logic statement. The statement is formulated by specifying one
or two *operands* and one *operator*. The operands are either constants,
variables or literals. The operator is one of the following:

   operator  | binary | explanation
   ---------:|:------:|:-----------
       `not` |    no  | Not.
       `and` |   yes  | And.
        `or` |   yes  | Or.
       `xor` |   yes  | Exclusive or.
        `eq` |   yes  | Equal.
        `ne` |   yes  | Not equal.
        `ge` |   yes  | Greater then or equal.
        `gt` |   yes  | Greater then.
        `le` |   yes  | Less then or equal.
        `lt` |   yes  | Less then.
       `mod` |   yes  | Modulo.
  `contains` |   yes  | Is a sub string of.

A simple test for truth or non-zero can be done by supplying one operand and no
operator.

### `for` loops
A simple `for` loop can be made as follows.

```yml
- name: fixed_size_list
  for: 2
  structure:
    - name: item
    - name: value
      type: int
```

The size can also be given by a variable.

```yml
- name: size_of_list
  type: int
- name: variable_size_list
  for: size_of_list
  structure:
    - name: item
    - name: value
      type: int
```

### `while` loops
The `do-while` loop reads the structure as long as the specified condition is
met. Evaluation is done at the end of each cycle, the resulting list is
therefore at least of size 1.

```yml
- name: variable_size_list
  do_while:
    operands:
      - value
      - 2
    operator: ne
  structure:
    - name: item
    - name: value
      type: int
```

The `while` loop first reads the first element of the structure and if the
specified condition is met, the rest of the structure is read. Evaluation is
done at the start of the cycle, the resulting list can therefore be of size 0.
The element used in the last evaluation (the one that terminates the loop),
does not have an associated structure, so its value is stored in the variable
specified by the `term` keyword.

```yml
- name: variable_size_list
  while:
    operands:
      - value
      - 2
    operator: ne
    term: list_term
  structure:
    - name: value
      type: int
    - name: item
```

### Conditionals
A variable or structure can be read conditionally using the `if` statement.

```yml
- name: something
  type: int
- name: item
  if:
    operands:
      - something
      - 2
    operator: eq
```

# `types.yml`: Constants, defaults and types
The file `types.yml` consists of three (optional) sections; `types`,
`constants` and `defaults`. In general the types file will look something like
this:

```yml
---
constants:
  const: 10
defaults:
  read: 2
types:
  int:
    read: 3
```

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

```yml
short:
  read: 2
  function:
    name: int
```

This type is stored in a variable size array delimited by `0x00` and is
processed by the `text` function:

```yml
comment:
  read:
    - 0x00
  function:
    name: text
```

And if we need to pass additional parameters to the `text` function, in this
case split on the character `0x09`:

```yml
comment:
  read:
    - 0x00
  function:
    name: text
    args:
      split:
        - 0x09
```

### Defining new types
Types can be added by subclassing the BinReadFunctions class. Suppose we need
a function that inverts all bits in a byte. We first have to make a subclass
that implements this function:

```python
class Invert(BinReadFunctions):
    def inv(self, data):
        return data ^ 0xff
```

By default, the new type will read one byte and process it with the `inv`
function. In this case there is no need to define the type in `types.yml`.

Now we can initiate the parser with this new class:

```python
parser = bin_parser.BinReader(
    open('something.dat'), open('structure.yml'),
    open('types.yml'), functions=Invert)
```

See `examples/prince/` for a working example.

## Defaults
To save some space and time writing our types definitions, the following
default values are used:

- `read` defaults to `1`.
- `function` defaults to the name of the type.
- The type itself defaults to `function`.
- If no name is given, the type defaults to `raw`.

So, for example, since a byte is of size 1, we can omit the `read` parameter:

```yml
byte:
  function:
    name: int
```

In the next example the function `int` will be used.

```yml
int:
  read: 2
```

And if we need an integer of size one which we want to name `int`, we do not
need to define anything.

### Overrides
The following defaults can be overridden by adding an entry in the `defaults`
section:

- `read`
- `type`
