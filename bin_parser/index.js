'use strict';

/*
General binary file parser.

(C) 2015 Jeroen F.J. Laros <J.F.J.Laros@lumc.nl>
*/
// NOTE: All integers are probably 2 bytes.
// NOTE: Colours may be 4 bytes.

var yaml = require('js-yaml'),
    requireFile = require('require-file');

/*
General binary file parser.
*/
function FamParser(fileContent) {
  var data = fileContent,
      parsed = {},
      internal = {},
      functions = Functions(types_handle),
      types = functions.types
      offset = 0,
      structure = yaml.load(structure_handle);

  /*
  Extract a field from {data} using either a fixed size, or a delimiter. After
  reading, {offset} is set to the next field.

  :arg int size: Size of fixed size field.
  :return str: Content of the requested field.
  */
  function getField(size) {
    var field,
        extracted;

    if (size) {
      field = data.slice(offset, offset + size);
      extracted = size;
    }
    else {
      field = data.slice(offset, -1).split(
        String.fromCharCode(fields.delimiters.field))[0];
      extracted = field.length + 1;
    }

    offset += extracted;
    return field;
  }

  /*
  Return `field[name]` if it exists, otherwise return `default`.

  :arg dict item: A dictionary.
  :arg str field: A field that may or may not be present in `item`.
  :arg any default: Default value if `field[name]` does not exist.

  :returns any: `field[name]` or `default`.
  */
  function set(item, field, deft) {
    if (field in item) {
      return item[field];
    }
    return deft;
  }


  /*
  Store a value both in the destination dictionary, as well as in the
  internal cache.

  :arg dict dest: Destination dictionary.
  :arg str name: Field name used in the destination dictionary.
  :arg any value: Value to store.
  */
  function store(dest, name, value) {
    dest[name] = value;
    internal[name] = value;
  }

  /*
  Resolve the value of a variable.
 
  First look in the cache to see if `name` is defined, then check the set
  of constants. If nothing can be found, the variable is considered to be
  a literal.
 
  :arg any name: The name or value of a variable.
  :returns: The resolved value.
  */
  function getValue(name) {
    if (name in internal) {
      return internal[name];
    }
    if ('constants' in types && name in types['constants']) {
      return types['constants'][name];
    }
    return name;
  }

  /*
  Evaluate an expression.

  An expression is represented by a dictionary with the following
  structure:

      expression = {
          'operator': '',
          'operands': []
      }

  :arg dict expression: An expression.
  :returns any: Result of the evaluation.
  */
  function evaluate(expression) {
    var operands = map(lambda x: get_value(x), expression['operands']);

    if (len(operands) == 1 and 'operator' not in expression) {
      return operands[0];
    }
    return operators[expression['operator']](*operands);
  }

  /*
  Convenience function for nested structures.

  :arg dict item: A dictionary.
  :arg dict dest: Destination dictionary.
  :arg str name: Field name used in the destination dictionary.
  */
  function parseStructure(item, dest, name) {
    var structure_dict = {};

    parse(item['structure'], structure_dict);
    dest[name].append(structure_dict);
  }


  /*
  Parse a binary file.

  :arg dict structure: Structure of the binary file.
  :arg dict dest: Destination dictionary.
  */
  function parse(structure, dest) {
    for (item in structure) {
      name = set(item, 'name', '');

      dtype = set(item, 'type', types['default']);
      if ('structure' in item) {
        dtype = 'list';
      }

      // Conditional statement.
      if ('if' in item) {
        if (not evaluate(item['if'])) {
          continue;
        }
      }

      // Primitive data types.
      if (dtype != 'list') {
        size = set(types[dtype], 'size', set(item, 'size', 0));
        if (type(size) != int) {
          size = internal[size];
        }

        if (dtype == 'flags') {
          flags = call('flags', get_field(size), item['flags']);
          for name in flags {
            store(dest, name, flags[name]);
        }
        else if (name) {
          function = set(types[dtype], 'function', dtype);
          args = set(item, set(types[dtype], 'arg', ''), ());
          if (args) {
            args = (args, );
          }
          store(dest, name, call(function, get_field(size), *args));
        }
        else {
          parse_raw(dest, size);
        }
      }
      // Nested structures.
      else {
        if (name not in dest) {
          if (set(['for', 'do_while', 'while']) & set(item)) {
            dest[name] = [];
          }
          else {
            dest[name] = {};
          }
        }

        if ('for' in item) {
          length = item['for'];
          if (type(length) != int) {
            length = internal[length];
          }
          for (_ in range(length)) {
            parse_structure(item, dest, name);
          }
        }
        else if ('do_while' in item) {
          while (True) {
            parse_structure(item, dest, name);
            if not evaluate(item['do_while']) {
              break;
            }
          }
        }
        else if ('while' in item) {
          delimiter = item['structure'][0];
          dest[name] = [{}];
          parse([delimiter], dest[name][0]);
          while True {
            if not evaluate(item['while']) {
              break;
            }
            parse(item['structure'][1:], dest[name][-1]);
            dest[name].append({});
            parse([delimiter], dest[name][-1]);
          }
          dest[item['while']['term']] = dest[name].pop(-1).values()[0];
        else {
          parse(item['structure'], dest[name]);
        }
      }
    }
  }

  /*
  Write the parsed FAM file to the console.
  */
  this.dump = function() {
    console.log('--- YAML DUMP ---');
    console.log(yaml.dump(parsed));
    console.log('\n--- DEBUG INFO ---\n');
    console.log(yaml.dump(internal));
  };

  /*
  Get parsed object.
  */
  this.getParsed = function() {
    return parsed;
  };

  parse(yaml.load(requireFile('../structure.yml')), parsed);
}

module.exports = FamParser;
