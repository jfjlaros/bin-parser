Extras
======

``make_skeleton``
-----------------

To facilitate the development of support for a new file type, the
``make_skeleton`` command can be used to generate a definition stub. It takes
an example file and a delimiter as input and outputs a structure and types
files definition. The input file is scanned for occurrences of the delimiter
and creates a field of type ``raw`` for the preceding bytes. All fields are
treated as delimited variable length strings that are processed by the ``raw``
function, as a result, all fixed sized fields are appended to the start of
these strings.

Example
~~~~~~~

Suppose we know that the string delimiter in our balance_ example is ``0x00``.
We can create a stub for the structure and types definitions as follows:

::

    make_skeleton -d 0x00 balance.dat structure.yml types.yml

The ``-d`` parameter can be used multiple times for multi-byte delimiters.

This will generate the following types definition:

.. code:: yaml

    ---
    types:
      raw:
        delimiter:
        - 0x00
        function:
          name: raw
      text:
        delimiter:
        - 0x00

with the following structure definition:

.. code:: yaml

    ---
    - name: field_000000
      type: raw
    - name: field_000001
      type: raw

The performance of these generated definitions can be assessed by using the
parser in debug mode:

::

    bin_parser read -d 2 \
      balance.dat structure.yml types.yml balance.yml 2>&1 | less

which gives the following output:

::

    0x000000: <CF>^GJohn Doe --> field_000000
    0x00000b: <8A>^L --> field_000001

We see that the first field has two extra bytes preceding the text field. This
is an indication that one or more fields need to be added to the start of the
structure definition. If we also know that in this file format only strings and
16-bit integers are used, we can change the definitions as follows.

We remove the ``raw`` type and add a type for parsing 16-bit integers:

.. code:: yaml

    ---
    types:
      short:
        size: 2
        function:
          name: struct
          args:
            fmt: '<h'
      text:
        delimiter:
          - 0x00

and we change the structure to enable parsing of the newly found integers:

.. code:: yaml

    ---
    - name: number_1
      type: short
    - name: name
      type: text
    - name: number_2
      type: short

By iterating this process, reverse engineering of these types of file formats
is greatly simplified.

``compare_yaml``
----------------

Since YAML files are serialised dictionaries or JavaScript objects, the order
of the keys is not fixed. Also, differences in indentation, line wrapping and
other formatting differences can lead to false positive detection of
differences when using rudimentary tools like ``diff``.

``compare_yaml`` takes two YAML files as input and outputs differences in the
content of these files:

::

    compare_yaml input_1.yaml input_2.yaml

The program recursively compares the contents of dictionaries (keys), lists and
values. The following differences are reported:

- Missing keys at any level.
- Lists of unequal size.
- Differences in values.

When a difference is detected, no further recursive comparison attempted, so
the list reported differences is not guaranteed to be complete. Conversely, if
no differences are reported, then the YAML files are guaranteed to have the
same content.

``test.sh``
-----------

To keep the Python- and JavaScript implementations in sync, we use a shell
script that compares the output of both the parser and the writer for various
examples.

::

    bash extras/test.sh

This will perform a parser test and an invariance test for all examples.

Parser test
~~~~~~~~~~~

This test uses the Python- and JavaScript implementation to convert from binary
to YAML. ``compare_yaml`` is used to check for any differences.

Invariance test
~~~~~~~~~~~~~~~

This test performs the following steps:

1. Use the Python implementation to convert from binary to YAML.
2. Use the Python implementation to convert the output of step 1 back to
   binary.
3. Use the JavaScript implementation to convert the output of step 1 back to
   binary.
4. Use the Python implementation to convert the output of step 2 to YAML.

The output of step 1 and 4 is compared using ``compare_yaml`` to assure that
the generated YAML is invariant under conversion to binary and back in the
Python implementation. The two generated binary files in step 2 and 3 are
compared with ``diff`` to confirm that the Python- and JavaScript
implementations behave identically.

Note that the original binary may not be invariant under conversion to YAML and
back. This is the case when variable length strings within fixed sized fields
are used.


.. _balance: examples/balance
