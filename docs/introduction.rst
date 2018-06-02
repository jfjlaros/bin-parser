Introduction
============

Why this library?
-----------------

Writing a parser for binary files requires reverse engineering skills,
knowledge of encodings, and above all, patience and intuition. Once all
knowledge is gathered, the person doing the reverse engineering usually writes
a parser and, if we are lucky, leaves some documentation. We try to facilitate
this process by providing the tools to do this in a uniform way. In essence, we
document the knowledge we gain from the reverse engineering process and use
this documentation directly in a parser.

Since the bulk of the types stored in binary files are standard, dedicated
parsers contain a lot of boiler plate code. We try to minimise this by
providing a framework where all knowledge is recorded in a human readable
format (YAML files) while the obligatory boiler plate code is incorporated in
the library.


Background
----------

In the following example, we read two bytes from an input stream, convert the
read data to an integer and store it in an output dictionary under the keys
``weight`` and ``age``.

.. code:: python

    output['weight'] = s_char_to_int(input_handle.read(1))
    output['age'] = s_char_to_int(input_handle.read(1))

This approach results in file specific literals (like ``weight`` and ``1``) and
data type conversions (``s_char_to_int()``) directly in source code. This has
several disadvantages:

- It is difficult to see what the file format is. This can be deduced only from
  the source code of the developed parser.
- A separate piece of software needs to be implemented if the conversion needs
  to be reversed.
- The parser is not portable to other programming languages.

Within the framework of this library, we attempt to solve the aforementioned
problems.

By first defining the types, we can reuse them easily:

.. code:: yaml

    ---
    s_char:
      function:
        name: struct

Now we can use the type ``s_char`` in our structure definition:

.. code:: yaml

    ---
    - name: weight
      type: s_char
    - name: age
      type: s_char

By recording the file structure this way, the knowledge of the file format and
the implementation of the parser are strictly separated. This has the following
advantages:

- The file format is documented in a human readable way.
- Reading and writing of the file format is supported.
- The parser is portable.


Approach
--------

In order to parse a binary file, the library needs two pieces of
information: it needs to know what the structure of the binary file is
and it needs to know which types are used. Both of these information
sources are provided to the library as nested dictionaries.

Example: Personal information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose we have a file (``person.dat``) that contains the following:

- An age (one byte integer).
- A name (zero delimited string).
- A weight (an other one byte integer).

To make a parser for this type of file, we need to create a file that
contains the type definitions. We name this file ``types.yml``.

.. code:: yaml

    ---
    types:
      s_char:
        function:
          name: struct
      text:
        delimiter:
          - 0x00

Then we create a file that contains the definition of the structure.
This file we name ``structure.yml``.

.. code:: yaml

    ---
    - name: age
      type: s_char
    - name: name
      type: text
    - name: weight
      type: s_char

We can now call the command line interface as follows:

::

    bin_parser read person.dat structure.yml types.yml person.yml

This will result in a new file, named ``person.yml``, which contains the
content of the input file (``person.dat``) in a human (and machine)
readable format:

.. code:: yaml

    ---
    age: 36
    name: John Doe
    weight: 81


Limitations
-----------

The main assumption made is that the binary files are *linearly parsable*. File
seeking or multiple passes over an input file are not supported. Also, there is
no support for the chaining of data types, so currently, compressed and
encrypted files are not supported.
