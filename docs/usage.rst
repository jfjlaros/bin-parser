Command line usage
==================

A command line interface is available for both implementations. Apart from some
implementation details concerning standard streams, their behaviour is
identical.


Python
------

To convert a binary file to YAML, use the ``read`` subcommand:

::

    bin_parser read input.bin structure.yml types.yml output.yml

To convert a YAML file to binary, use the ``write`` subcommand:

::

    bin_parser write input.yml structure.yml types.yml output.bin


JavaScript
----------

To convert a binary file to YAML, use the ``read`` subcommand:

::

    ./node_modules/.bin/bin_parser read input.bin structure.yml types.yml \
      output.yml

To convert a YAML file to binary, use the ``write`` subcommand:

::

    ./node_modules/.bin/bin_parser write input.yml structure.yml types.yml \
      output.bin

Please note that when installing from source, the ``bin_parser`` executable is
not installed. Instead run the script ``cli.js`` as follows:

::

    nodejs javascript/cli.js
