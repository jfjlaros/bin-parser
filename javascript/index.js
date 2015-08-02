'use strict';

/*
General binary file parser.

(C) 2015 Jeroen F.J. Laros <J.F.J.Laros@lumc.nl>
*/

var yaml = require('js-yaml');

var Functions = require('./functions');

function getOneValue(dictionary) {
  var item;

  for (item in dictionary) {
    return dictionary[item];
  }
}

/*
Update a dictionary with the properties of another dictionary.

:arg dict target: Target dictionary.
:arg dict source: Source dictionary.
*/
function update(target, source) {
  var item;

  for (item in source) {
    target[item] = source[item];
  }
}

/*
General binary file parser.
*/
function BinParser(fileContent, structureHandle, typesHandle, functions) {
  var data = fileContent,
      parsed = {},
      internal = {},
      functions = new Functions.BinParseFunctions(),
      types = yaml.load(typesHandle),
      offset = 0,
      structure = yaml.load(structureHandle);

  /*
  Extract a field from {data} using either a fixed size, or a delimiter. After
  reading, {offset} is set to the next field.

  :arg int size: Size of fixed size field.
  :return str: Content of the requested field.
  */
  function getField(size, delimiter) {
    var field,
        extracted;

    if (offset >= data.length) {
      throw('StopIteration');
    }

    if (size) {
      field = data.slice(offset, offset + size);
      extracted = size;
    }
    else {
      field = functions.text(data.slice(offset, -1), {'delimiter': delimiter});
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
    //console.log(name + ': ' + value);
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
    if (internal[name] !== undefined) {
      return internal[name];
    }
    if (types.constants && types.constants[name]) {
      return types.constants[name];
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
    var operands = expression.operands.map(getValue);

    if (operands.length === 1 && !expression.operator) {
      return operands[0];
    }
    return Functions.operators[expression.operator].apply(this, operands);
  }

  /*
  Convenience function for nested structures.

  :arg dict item: A dictionary.
  :arg dict dest: Destination dictionary.
  :arg str name: Field name used in the destination dictionary.
  */
  function parseStructure(item, dest, name) {
    var structureDict = {};

    parse(item['structure'], structureDict);
    dest[name].push(structureDict);
  }


  /*
  Parse a binary file.

  :arg dict structure: Structure of the binary file.
  :arg dict dest: Destination dictionary.
  */
  function parse(structure, dest) {
    var item,
        name,
        dtype,
        size,
        func,
        length,
        delimiter,
        kwargs,
        result,
        index,
        member,
        _;

    for (index = 0; index < structure.length; index++) {
      item = structure[index];
      name = set(item, 'name', '');

      dtype = set(item, 'type', types.default);
      if ('structure' in item) {
        dtype = 'list';
      }

      // Conditional statement.
      if (item.if) {
        if (!evaluate(item.if)) {
          continue;
        }
      }

      // Primitive data types.
      if (dtype !== 'list') {
        size = set(types[dtype], 'size', set(item, 'size', 0));
        if (size.constructor !== Number) {
          size = internal[size];
        }

        if (name) {
          func = set(types[dtype], 'function', dtype);
          
          kwargs = set(types[dtype], 'args', {});
          delimiter = set(kwargs, 'delimiter', []);
          
          result = functions[func](getField(size, delimiter), kwargs);
          if (result.constructor === Object) {
            for (member in result) {
              store(dest, member, result[member]);
            }
          }
          else {
            store(dest, name, result);
          }
        }
        else {
          getField(size);
        }
      }
      // Nested structures.
      else {
        if (!dest[name]) {
          if (item.for || item.do_while || item.while) {
            dest[name] = [];
          }
          else {
            dest[name] = {};
          }
        }

        if (item.for) {
          length = item.for;
          if (length.constructor !== Number) {
            length = internal[length];
          }
          for (_ = 0; _ < length; _++) {
            parseStructure(item, dest, name);
          }
        }
        else if (item.do_while) {
          while (true) {
            parseStructure(item, dest, name);
            if (!evaluate(item.do_while)) {
              break;
            }
          }
        }
        else if (item.while) {
          delimiter = item.structure[0];
          dest[name] = [{}];
          parse([delimiter], dest[name][0]);
          while (true) {
            if (!evaluate(item.while)) {
              break;
            }
            parse(item.structure.slice(1, -1), dest[name].slice(-1)[0]);
            dest[name].push({});
            parse([delimiter], dest[name].slice(-1)[0]);
          }
          dest[item.while.term] = getOneValue(dest[name].pop(-1));
        }
        else {
          parse(item.structure, dest[name]);
        }
      }
    }
  }

  /*
  Write the parsed binary file to the console.
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

  /*
  Initialisation.
  */
  // Add standard data types.
  update(types, {
    'raw': {},
    'list': {}
  });

  // Set default data type.
  if (!types.default) {
    types.default = 'text';
  }

  try {
    parse(structure, parsed);
  }
  catch(err) {
    if (err !== 'StopIteration') {
      throw(err);
    }
  }
}

module.exports = BinParser;
