Library
=======

While the command line interface can be used to parse a binary file when the
correct types and structure files are provided, it may be useful to have a
dedicated interface for specific file types. It could also be that the current
library does not provide all functions required for a specific file type. In
these cases, direct interfacing to the library is needed.


Basic usage
-----------

For both implementations we provide a ``BinReader`` and a ``BinWriter`` object
that are initialised with the input file and the types and structure
definitions.

Python
~~~~~~

To use the library from our own code, we need to use the following:

.. include:: ../examples/balance/parser.py

The ``BinReader`` object stores the original data in the ``data`` member
variable and the parsed data in the ``parsed`` member variable.

JavaScript
~~~~~~~~~~

Similarly, in JavaScript, we use the following:

.. include:: ../examples/balance/parser.js


Defining new types
------------------

See prince_ for a working example of a reader and a writer in both Python and
JavaScript.

Python
~~~~~~

Types can be added by subclassing the ``BinReadFunctions`` class. Suppose we
need a function that inverts all bits in a byte. We first have to make a
subclass that implements this function:

.. code:: python

    from bin_parser import BinReadFunctions

    class Invert(BinReadFunctions):
        def inv(self, data):
            return data ^ 0xff

By default, the new type will read one byte and process it with the ``inv``
function. In this case there is no need to define the type in ``types.yml``.

Now we can initialise the parser using an instance of the new class:

.. code:: python

    parser = bin_parser.BinReader(
        open('something.dat').read(),
        yaml.safe_load(open('structure.yml')),
        yaml.safe_load(open('types.yml')),
        functions=Invert())

JavaScript
~~~~~~~~~~

Similarly, in JavaScript, we make a prototype of the ``BinReadFunctions``
function.

.. code:: javascript

    var Functions = require('../../../javascript/functions');

    function Invert() {
      this.inv = function(data) {
        return data ^ 0xff;
      };

      Functions.BinReadFunctions.call(this);
    }

Now we can initialise the parser with the prototyped function:

.. code:: javascript

    var parser = new BinParser.BinReader(
      fs.readFileSync('something.dat'),
      yaml.load(fs.readFileSync('structure.yml')),
      yaml.load(fs.readFileSync('types.yml')),
      {'functions': new Invert()});


.. _prince: https://github.com/jfjlaros/bin-parser/blob/master/examples/prince

