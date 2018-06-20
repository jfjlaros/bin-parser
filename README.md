General binary file parser
==========================

[![Build Status](https://travis-ci.org/jfjlaros/bin-parser.svg?branch=master)](https://travis-ci.org/jfjlaros/bin-parser)

This library provides general binary file parsing by interpreting
documentation of a file structure and data types. By default, it
supports basic data types like big-endian and little-endian integers,
floats and doubles, variable length (delimited) strings, maps and bit
fields (flags) and it can iterate over sub structures. Other data types
are easily added.

The file structure and the types are stored in nested dictionaries. The
structure is separated from the types, this way multiple file formats
using the same types (within one project for example) can be easily
supported without much duplication.

The design of the library is such that all operations can be reversed.
This means that fully functional binary editing is possible using this
implementation; first use the reader to convert a binary file to a
serialised dictionary representation, this representation is easily
edited using a text editor, and then use the writer to convert back to
binary.

This idea is implemented in two languages; Python and JavaScript. All
main development is done in Python. We chose YAML as our preferred
serialised dictionary format, but other serialisation formats (JSON for
example) can be used too.

Please see
[ReadTheDocs](http://bin-parser.readthedocs.io/en/latest/index.html) for
the latest documentation.
