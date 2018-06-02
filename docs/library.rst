Library
=======


Basic usage
-----------

Python
~~~~~~

To use the library from our own code, we need to use the following:

.. code:: python

    import yaml

    import bin_parser

    parser = bin_parser.BinReader(
        open('balance.dat').read(),
        yaml.safe_load(open('structure.yml')),
        yaml.safe_load(open('types.yml')))

    print parser.parsed['name']

The ``BinReader`` object stores the original data in the ``data`` member
variable and the parsed data in the ``parsed`` member variable.

JavaScript
~~~~~~~~~~

Similarly, in JavaScript, we use the following:

.. code:: javascript

    var fs = require('fs'),
        yaml = require('js-yaml');

    var BinParser = require('../../javascript/index');

    var parser = new BinParser.BinReader(
      fs.readFileSync('balance.dat'),
      yaml.load(fs.readFileSync('structure.yml')),
      yaml.load(fs.readFileSync('types.yml')),
      {})

    console.log(parser.parsed.name);


Defining new types
------------------

See `Prince <examples/prince/>`__ for a working example of a reader and
a writer in both Python and JavaScript.

Python
~~~~~~

Types can be added by subclassing the ``BinReadFunctions`` class.
Suppose we need a function that inverts all bits in a byte. We first
have to make a subclass that implements this function:

.. code:: python

    from bin_parser import BinReadFunctions

    class Invert(BinReadFunctions):
        def inv(self, data):
            return data ^ 0xff

By default, the new type will read one byte and process it with the
``inv`` function. In this case there is no need to define the type in
``types.yml``.

Now we can initialise the parser using an instance of the new class:

.. code:: python

    parser = bin_parser.BinReader(
        open('something.dat').read(),
        yaml.safe_load(open('structure.yml')),
        yaml.safe_load(open('types.yml')),
        functions=Invert())

JavaScript
~~~~~~~~~~

Similarly, in JavaScript, we make a prototype of the
``BinReadFunctions`` function.

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
