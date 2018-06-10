Types
======

Types, constants, defaults and macros are defined in a nested dictionary which
is usually serialised to YAML. This file, usually named ``types.yml``, consists
of three (optional) sections; ``types``, ``constants``, ``defaults`` and
``macros``. In general the types file will look something like this:

.. code:: yaml

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


Types
-----

A type consists of two subunits controlling two stages; the acquirement stage
and the processing stage.

The acquirement stage is controlled by the ``size`` and ``delimiter``
parameters, the size is given in number of bytes, the delimiter is a list of
bytes. Usually specifying one of these parameters is sufficient for the
acquisition of the data, but in some cases, where for example we have to read a
fixed sized block in which a string of variable size is stored, both parameters
can be used simultaneously. Once the data is acquired, it is passed to the
processing stage.

The processing stage is controlled by the ``function`` parameter, it denotes
the function that is responsible for processing the acquired data. Additional
parameters for this function can be supplied by the ``args`` parameter.

Basic types
~~~~~~~~~~~

In version 0.0.14 the ``struct`` type was introduced to replace basic types
like ``int``, ``float``, etc. and simple compound data types. The formatting
parameter ``fmt`` is used to control how a value is packed or unpacked. For
example, a 4-byte little-endian integer uses the formatting string ``<i`` and a
big-endian unsigned long uses the formatting string ``>L``.

For a complete overview of the supported basic types, see the Python struct_
documentation or our extensive list of examples_.

Examples
~~~~~~~~

The following type is stored in two bytes and is processed by the
``text`` function:

.. code:: yaml

    id:
      size: 2
      function:
        name: text

This type is stored in a variable size array delimited by ``0x00`` and is
processed by the ``text`` function:

.. code:: yaml

    comment:
      delimiter:
        - 0x00
      function:
        name: text

We can pass additional parameters to the ``text`` function, in this case split
on the character ``0x09``, like so:

.. code:: yaml

    comment:
      delimiter:
        - 0x00
      function:
        name: text
        args:
          split:
            - 0x09

A 2-byte little-endian integer is defined as follows:

.. code:: yaml

    int:
      size: 2
      function:
        name: struct
        args:
          fmt: '<h'

And a 4-byte big-endian float is defined as follows:

.. code:: yaml

    float:
      size: 4
      function:
        name: struct
        args:
          fmt: '>f'

Compound types
~~~~~~~~~~~~~~

Simple compound types can also be created using the ``struct`` function. By
default this will return a list of basic types, which can optionally be mapped
using an annotation list. Additionally, a simple dictionary can be created by
labeling the basic types.

In the following example, we read three unsigned bytes, by providing a list of
labels, the first byte is labelled ``r``, the second one ``g``, and the last
one ``b``. If the values are 0, 255 and 128 respectively, the resulting
dictionary will be: ``{'r': 0, 'g': 255, 'b': 128}``.

.. code:: yaml

      colour:
        size: 3
        function:
          name: struct
          args:
            fmt: BBB
            labels: ['r', 'g', 'b']

Values can also be mapped using an annotation list to improve readability. This
procedure replaces specific values by their annotation and leaves other values
unaltered. Note that mapping multiple values to the same annotation will break
reversibility of the parser.

In the following example, we read one 4-byte little-endian unsigned integer and
provide annotation for the maximum and minimum value. If the value is 0, the
result will be ``unknown``, if the value is 10, the result will be 10 as well.

.. code:: yaml

      date:
        size: 4
        function:
          name: struct
          args:
            fmt: <I
            annotation:
              0xffffffff: defined
              0x00000000: unknown

Labels and annotation lists can be combined.


Constants
---------

A constant can be used as an alias in ``structure.yml``. Using constants can
make conditional statements and loops more readable.


Defaults
--------

To save some space and time writing types definitions, the following default
values are used:

- ``size`` defaults to ``1``.
- ``function`` defaults to the name of the type.
- If no name is given, the type defaults to ``raw`` and the destination is a
  list named ``__raw__``.

So, for example, since a byte is of size 1, we can omit the ``size`` parameter
in the type definition:

.. code:: yaml

    byte:
      function:
        name: struct

In the next example the function ``text`` will be used.

.. code:: yaml

    text:
      size: 2

And if we need an integer of size one which we want to name ``struct``, we do
not need to define anything.

If the following construction is used in the structure, the type will default
to ``raw``:

.. code:: yaml

    - name:
      size: 20


Overrides
~~~~~~~~~

The following defaults can be overridden by adding an entry in the ``defaults``
section:

- ``delimiter`` (defaults to ``[]``).
- ``name`` (defaults to ``''``).
- ``size`` (defaults to 1).
- ``type`` (defaults to ``text``).
- ``unknown_destination`` (defaults to ``__raw__``).
- ``unknown_type`` (defaults to ``raw``).


Macros
------

Macros were introduced in version 0.0.15 to define complex compound types. A
macro is equivalent to a sub structure, which are also used in the structure
definition either as is, or as the body of a loop or conditional statement.

In the following example, we have a substructure that occurs more than once in
our binary file. We have two persons, of which the name, age, weight and height
are stored. Using a flat file structure will result in something similar to
this:

.. include:: ../examples/macro/structure_plain.yml
   :code: yaml

Note that we have to choose new variable names for every instance of a person.
This makes downstream processing quite tedious. Furthermore, code duplication
makes maintenance tedious.

The ``structure`` directive can be used to group variables in a substructure.
This solves the variable naming issue, but it does not solve the maintenance
issue.

.. include:: ../examples/macro/structure_nested.yml
   :code: yaml

We can define a macro in the ``types.yml`` file by adding a section named
``macros`` where we describe the structure of the group of variables.

.. include:: ../examples/macro/types.yml
   :code: yaml

This macro can then be used in the ``structure.yml`` file in almost the same we
we use a basic type.

.. include:: ../examples/macro/structure.yml
   :code: yaml


.. _struct: https://docs.python.org/2/library/struct.html#format-characters
.. _examples: https://github.com/jfjlaros/bin-parser/blob/master/examples/types/types.yml
