Structure
=========

After having defined the basic types, the structure of the binary file can be
recorded in a separate nested dictionary which is usually serialised to YAML.
This file, usually named ``structure.yml`` contains the general structure of
the binary file.


Flat structure
--------------

A simple flat structure is recorded as a list in which, for every variable, we
supply a name and a type. In the following example we see the definition of a
simple flat structure containing two short integers and one text field.

.. include:: ../examples/balance/structure.yml
   :code: yaml


Loops and conditionals
----------------------

Both loops and conditionals (except the ``for`` loop) are controlled by an
evaluation of a logic statement. The statement is formulated by specifying one
or two *operands* and one *operator*. The operands are either constants,
variables or literals. The operator is one of the following:

+----------------+----------+--------------------------+
| operator       | binary   | explanation              |
+================+==========+==========================+
| ``not``        | no       | Not.                     |
+----------------+----------+--------------------------+
| ``and``        | yes      | And.                     |
+----------------+----------+--------------------------+
| ``or``         | yes      | Or.                      |
+----------------+----------+--------------------------+
| ``xor``        | yes      | Exclusive or.            |
+----------------+----------+--------------------------+
| ``eq``         | yes      | Equal.                   |
+----------------+----------+--------------------------+
| ``ne``         | yes      | Not equal.               |
+----------------+----------+--------------------------+
| ``ge``         | yes      | Greater then or equal.   |
+----------------+----------+--------------------------+
| ``gt``         | yes      | Greater then.            |
+----------------+----------+--------------------------+
| ``le``         | yes      | Less then or equal.      |
+----------------+----------+--------------------------+
| ``lt``         | yes      | Less then.               |
+----------------+----------+--------------------------+
| ``mod``        | yes      | Modulo.                  |
+----------------+----------+--------------------------+
| ``contains``   | yes      | Is a sub string of.      |
+----------------+----------+--------------------------+

A simple test for truth or non-zero can be done by supplying one operand and no
operator.


``for`` loops
-------------

A simple ``for`` loop can be made as follows.

.. code:: yaml

    - name: fixed_size_list
      for: 2
      structure:
        - name: item
        - name: value
          type: s_char

The size can also be given by a variable.

.. code:: yaml

    - name: size_of_list
      type: s_char
    - name: variable_size_list
      for: size_of_list
      structure:
        - name: item
        - name: value
          type: s_char


``while`` loops
---------------

The ``do-while`` loop reads the structure as long as the specified condition is
met. Evaluation is done at the end of each cycle, the resulting list is
therefore at least of size 1.

.. code:: yaml

    - name: variable_size_list
      do_while:
        operands:
          - value
          - 2
        operator: ne
      structure:
        - name: item
        - name: value
          type: s_char

The ``while`` loop first reads the first element of the structure and if the
specified condition is met, the rest of the structure is read. Evaluation is
done at the start of the cycle, the resulting list can therefore be of size 0.
The element used in the last evaluation (the one that terminates the loop),
does not have an associated structure, so its value is stored in the variable
specified by the ``term`` keyword.

.. code:: yaml

    - name: variable_size_list
      while:
        operands:
          - value
          - 2
        operator: ne
        term: list_term
      structure:
        - name: value
          type: s_char
        - name: item

When using this structure on the input ``\x01hello\x00\x03world\x00\x02``, the
result will be as follows.

.. code:: yaml

    list_term: 2
    variable_size_list:
    - item: hello
      value: 1
    - item: world
      value: 3


Conditionals
------------

A variable or structure can be read conditionally using the ``if`` statement.

.. code:: yaml

    - name: something
      type: s_char
    - name: item
      if:
        operands:
          - something
          - 2
        operator: eq


Notes on evaluation
-------------------

Since we use a general way of evaluating expressions, there are usually
multiple ways of writing such an expression. For example, the following
statements are equal:

Implicit truth test.

.. code:: yaml

    - name: item
      if:
        operands:
          - something

Explicit truth test.

.. code:: yaml

    - name: item
      if:
        operands:
          - something
          - true
        operator: eq

Explicit non-false test.

.. code:: yaml

    - name: item
      if:
        operands:
          - something
          - false
        operator: ne
