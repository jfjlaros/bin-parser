# General binary file parser
This library aims at general binary file parsing by interpreting documentation
of the file structure and data types. By default, it supports basic data types
like integers, variable length (delimited) strings, dates, maps and bit fields
(flags) and it can iterate over sub structures. Other data types are easily
added.

The file structure and the types are stored in a nested dictionary. For
practical purposes the structure is separated from the types, this way multiple
file formats using the same types (within one project for example) can be
easily supported without much duplication.

The design of the library is such that all operations can be reversed. This is
fully implemented in the Python version of the library. This means that fully
functional binary editing is possible using this implementation; first use the
reader to convert a binary file to a serialised dictionary representation, this
representation is easily edited using a text editor, and then use the writer to
convert back to binary.

This idea is implemented in two languages; Python and JavaScript. All main
development is done in Python. We chose YAML as our preferred serialised
dictionary format, but other serialisation formats (JSON for example) can be
used too.


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
parsers contain a lot of boiler plate code. We try to minimise this by
providing a framework where all knowledge is recorded in a human readable
format (YAML files) while the obligatory boiler plate code is incorporated in
the library.


## Background
In the following example, we read two bytes from an input stream, convert the
read data to an integer and store it in an output dictionary under the keys
`weight` and `age`.

```python
output['weight'] = s_char_to_int(input_handle.read(1))
output['age'] = s_char_to_int(input_handle.read(1))
```

This approach results in file specific literals (like `weight` and `1`) and
data type conversions (`s_char_to_int()`) directly in source code. This has
several disadvantages:

- It is difficult to see what the file format is. This can be deduced only from
  the source code of the developed parser.
- A separate piece of software needs to be implemented if the conversion needs
  to be reversed.
- The parser is not portable to other programming languages.

Within the framework of this library, we attempt to solve the aforementioned
problems.

By first defining the types, we can reuse them easily:

```yml
---
s_char:
  function:
    name: struct
```

Now we can use the type `s_char` in our structure definition:

```yml
---
- name: weight
  type: s_char
- name: age
  type: s_char
```

By recording the file structure this way, the knowledge of the file format and
the implementation of the parser are strictly separated. This has the following
advantages:

- The file format is documented in a human readable way.
- Reading and writing of the file format is supported.
- The parser is portable.


## When can this library be used?
The main assumption made is that the binary files are *linearly parsable*. File
seeking or multiple passes over an input file are not supported. Also, there is
no support for the chaining of data types, so currently, compressed and
encrypted files are not supported.


## Installation
### Python

    pip install bin-parser

### JavaScript

    npm install bin-parser


## Usage
### Python
To convert a binary file to YAML, use the `read` subcommand:

    bin_parser read input.bin structure.yml types.yml output.yml

To convert a YAML file to binary, use the `write` subcommand:

    bin_parser write input.yml structure.yml types.yml output.bin

### JavaScript
To convert a binary file to YAML, use the `read` subcommand:

    ./node_modules/.bin/bin-parser read input.bin structure.yml types.yml \
      output.yml

To convert a YAML file to binary, use the `write` subcommand:

    ./node_modules/.bin/bin_parser write input.yml structure.yml types.yml \
      output.bin


## Approach
In order to parse a binary file, the library needs two pieces of information:
it needs to know what the structure of the binary file is and it needs to know
which types are used. Both of these information sources are provided to the
library as nested dictionaries.

### Example: Personal information
Suppose we have a file (`person.dat`) that contains the following:

- An age (one byte integer).
- A name (zero delimited string).
- A weight (an other one byte integer).

To make a parser for this type of file, we need to create a file that contains
the type definitions. We name this file `types.yml`.

```yml
---
types:
  s_char:
    function:
      name: struct
  text:
    delimiter:
      - 0x00
```

Then we create a file that contains the definition of the structure. This file
we name `structure.yml`.

```yml
---
- name: age
  type: s_char
- name: name
  type: text
- name: weight
  type: s_char
```

We can now call the command line interface as follows:

    bin_parser read person.dat structure.yml types.yml person.yml

This will result in a new file, named `person.yml`, which contains the content
of the input file (`person.dat`) in a human (and machine) readable format:

```yml
---
age: 36
name: John Doe
weight: 81
```


## Constants, defaults and types
The file `types.yml` consists of three (optional) sections; `types`,
`constants` and `defaults`. In general the types file will look something like
this:

```yml
---
constants:
  multiplier: 10
defaults:
  size: 2
types:
  s_char:
    size: 1
    function:
      name: struct
  text:
    delimiter:
      - 0x00
```

### Constants
A constant can be used as an alias in `structure.yml`. Using constants can make
conditional statements and loops more readable.

### Types
A type consists of two subunits controlling two stages; the acquirement stage
and the processing stage.

The acquirement stage is controlled by the `size` and `delimiter` parameters,
the size is given in number of bytes, the delimiter is a list of bytes. Usually
specifying one of these parameters is sufficient for the acquisition of the
data, but in some cases, where for example we have to read a fixed sized block
in which a string of variable size is stored, both parameters can be used
simultaneously. Once the data is acquired, it is passed to the processing
stage.

The processing stage is controlled by the `function` parameter, it denotes the
function that is responsible for processing the acquired data. Additional
parameters for this function can be supplied by the `args` parameter.

#### Basic types
In version 0.0.14 the `struct` type was introduced to replace basic types like
`int`, `float`, etc. The formatting parameter `fmt` is used to control how a
value is packed or unpacked. For example, a 4-byte little-endian integer uses
the formatting string `<i` and a big-endian unsigned long uses the formatting
string `>L`.

For a complete overview of the supported basic types, see the Python
[struct](https://docs.python.org/2/library/struct.html#format-characters)
documentation.

#### Examples
The following type is stored in two bytes and is processed by the `text`
function:

```yml
id:
  size: 2
  function:
    name: text
```

This type is stored in a variable size array delimited by `0x00` and is
processed by the `text` function:

```yml
comment:
  delimiter:
    - 0x00
  function:
    name: text
```

We can pass additional parameters to the `text` function, in this case split on
the character `0x09`, like so:

```yml
comment:
  delimiter:
    - 0x00
  function:
    name: text
    args:
      split:
        - 0x09
```

A 2-byte little-endian integer is defined as follows:

```yml
int:
  size: 2
  function:
    name: struct
    args:
      fmt: '<h'
```

And a 4-byte big-endian float is defined as follows:

```yml
float:
  size: 4
  function:
    name: struct
    args:
      fmt: '>f'
```

### Defaults
To save some space and time writing types definitions, the following default
values are used:

- `size` defaults to `1`.
- `function` defaults to the name of the type.
- If no name is given, the type defaults to `raw` and the destination is a list
  named `__raw__`.

So, for example, since a byte is of size 1, we can omit the `size` parameter in
the type definition:

```yml
byte:
  function:
    name: struct
```

In the next example the function `text` will be used.

```yml
text:
  size: 2
```

And if we need an integer of size one which we want to name `struct`, we do not
need to define anything.

If the following construction is used in the structure, the type will default
to `raw`:

```yml
- name:
  size: 20
```

#### Overrides
The following defaults can be overridden by adding an entry in the `defaults`
section:

- `delimiter` (defaults to `[]`).
- `name` (defaults to `''`).
- `size` (defaults to 1).
- `type` (defaults to `text`).
- `unknown_destination` (defaults to `__raw__`).
- `unknown_type` (defaults to `raw`).


## Structure of the binary file
The file `structure.yml` contains the general structure of the binary file.

### Loops and conditionals
Both loops and conditionals (except the `for` loop) are controlled by an
evaluation of a logic statement. The statement is formulated by specifying one
or two *operands* and one *operator*. The operands are either constants,
variables or literals. The operator is one of the following:

|   operator | binary | explanation
|         --:|:------:|:--
|      `not` |    no  | Not.
|      `and` |   yes  | And.
|       `or` |   yes  | Or.
|      `xor` |   yes  | Exclusive or.
|       `eq` |   yes  | Equal.
|       `ne` |   yes  | Not equal.
|       `ge` |   yes  | Greater then or equal.
|       `gt` |   yes  | Greater then.
|       `le` |   yes  | Less then or equal.
|       `lt` |   yes  | Less then.
|      `mod` |   yes  | Modulo.
| `contains` |   yes  | Is a sub string of.

A simple test for truth or non-zero can be done by supplying one operand and no
operator.

#### `for` loops
A simple `for` loop can be made as follows.

```yml
- name: fixed_size_list
  for: 2
  structure:
    - name: item
    - name: value
      type: short
```

The size can also be given by a variable.

```yml
- name: size_of_list
  type: short
- name: variable_size_list
  for: size_of_list
  structure:
    - name: item
    - name: value
      type: short
```

#### `while` loops
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
      type: short
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
      type: short
    - name: item
```

#### Conditionals
A variable or structure can be read conditionally using the `if` statement.

```yml
- name: something
  type: short
- name: item
  if:
    operands:
      - something
      - 2
    operator: eq
```

#### Evaluation
The following statements are equal:

```yml
- name: item
  if:
    operands:
      - something
```

```yml
- name: item
  if:
    operands:
      - something
      - true
    operator: eq
```

```yml
- name: item
  if:
    operands:
      - something
      - false
    operator: ne
```


## Using the library
### Python
To use the library from our own code, we need to use the following:

```python
import yaml

import bin_parser

parser = bin_parser.BinReader(
    open('balance.dat').read(),
    yaml.safe_load(open('structure.yml')),
    yaml.safe_load(open('types.yml')))

print parser.parsed['name']
```

The `BinReader` object stores the original data in the `data` member variable
and the parsed data in the `parsed` member variable.

### JavaScript
Similarly, in JavaScript, we use the following:

```javascript
var fs = require('fs'),
    yaml = require('js-yaml');

var BinParser = require('../../javascript/index');

var parser = new BinParser.BinReader(
  fs.readFileSync('balance.dat'),
  yaml.load(fs.readFileSync('structure.yml')),
  yaml.load(fs.readFileSync('types.yml')),
  {})

console.log(parser.parsed.name);
```


## Defining new types
See `examples/prince/` for a working example of a reader and a writer in both
Python and JavaScript.

### Python
Types can be added by subclassing the `BinReadFunctions` class. Suppose we need
a function that inverts all bits in a byte. We first have to make a subclass
that implements this function:

```python
from bin_parser import BinReadFunctions

class Invert(BinReadFunctions):
    def inv(self, data):
        return data ^ 0xff
```

By default, the new type will read one byte and process it with the `inv`
function. In this case there is no need to define the type in `types.yml`.

Now we can initialise the parser using an instance of the new class:

```python
parser = bin_parser.BinReader(
    open('something.dat').read(),
    yaml.safe_load(open('structure.yml')),
    yaml.safe_load(open('types.yml')),
    functions=Invert())
```

### JavaScript
Similarly, in JavaScript, we make a prototype of the `BinReadFunctions`
function.

```javascript
var Functions = require('../../../javascript/functions');

function Invert() {
  this.inv = function(data) {
    return data ^ 0xff;
  };

  Functions.BinReadFunctions.call(this);
}
```

Now we can initialise the parser with the prototyped function:

```javascript
var parser = new BinParser.BinReader(
  fs.readFileSync('something.dat'),
  yaml.load(fs.readFileSync('structure.yml')),
  yaml.load(fs.readFileSync('types.yml')),
  {'functions': new Invert()});
```


## Extras

    make_skeleton -d 0x0d input.bin structure.yml types.yml
    bin_parser read -d 2 input.bin structure.yml types.yml output.yml 2>&1 | \
      less

and in an other terminal:

    less output.yml
