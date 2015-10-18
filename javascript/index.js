'use strict';

/*
General binary file parser.

(C) 2015 Jeroen F.J. Laros <J.F.J.Laros@lumc.nl>
*/

var yaml = require('js-yaml');

var Functions = require('./functions');

/*
Get the first value in an object.

:arg object object: An object.

:returns object: The first value encountered in an object.
*/
function getOneValue(object) {
  return object[Object.keys(object)[0]];
}

/*
Update an object with the properties of an other object.

:arg object target: Target object.
:arg object source: Source object.
*/
function update(target, source) {
  var item;

  for (item in source) {
    target[item] = source[item];
  }
}

/*
Pop an item from an object.

:arg object object: An object.
:arg str key: Name of an item.

:returns object: The desired item.
*/
function pop(object, key) {
  var result = object[key];

  delete object[key];
  return result;
}

function numerical(a, b) {
  return a - b;
}

/*
General binary file reader.
*/
function BinReader(
    fileContent, structureContent, typesContent, functions, prune) {
  var 
      internal = {},
      functions = functions || new Functions.BinReadFunctions(),
      prune = prune || false,
      constants = {},
      defaults = {
        'delimiter': [],
        'name': '',
        'size': 0,
        'type': 'text',
        'unknown_destination': 'raw',
        'unknown_function': 'raw'
      },
      types = {
        'raw': {},
        'int': {}
      },
      types_data = typesContent,
      structure = structureContent,
      data,
      offset,
      parsed;

  /*
  Resolve the value of a variable.
 
  First look in the cache to see if `name` is defined, then check the set
  of constants. If nothing can be found, the variable is considered to be
  a literal.
 
  :arg any name: The name or value of a variable.
  :returns any: The resolved value.
  */
  function getValue(name) {
    if (internal[name] !== undefined) {
      return internal[name];
    }
    if (constants[name] !== undefined) {
      return constants[name];
    }
    return name;
  }

  /*
  Resolve the value of a member variable.

  First see if the variable is defined in `item`, then check the type
  definition and lastly check the defaults.

  :arg object item: Data structure.
  :arg str dtype: Name of the data type.
  :arg str name: The name of the variable.

  :returns any: The resolved value.
  */
  function getDefault(item, dtype, name) {
    if (item[name] !== undefined) {
      return item[name];
    }
    if ((types[dtype] !== undefined) && (types[dtype][name] !== undefined)) {
      return types[dtype][name];
    }
    if (defaults[name] !== undefined) {
      return defaults[name];
    }
    return undefined;
  }

  /*
  Determine what to read and how to interpret what was read.

  First resolve the `delimiter` and `size`. If none are given, assume we
  read one byte. Then resolve the function that will interpret the data
  (either delimited or fixed size).

  :arg object item: Data structure.
  :arg str dtype: Name of the data type.

  :returns tuple: (`delim`, `size`, `func`, `kwargs`).
  */
  function getFunction(item, dtype) {
    var delim = getDefault(item, dtype, 'delimiter'),
        size = getDefault(item, dtype, 'size'),
        func = dtype,
        kwargs = {};

    if (!(delim.length || size)) {
      size = 1;
    }

    // Determine the function and its arguments.
    if ('function' in types[dtype]) {
      if ('name' in types[dtype].function) {
        func = types[dtype].function.name;
      }
      if ('args' in types[dtype].function) {
        kwargs = types[dtype].function.args;
      }
    }
    return [delim, size, func, kwargs];
  }

  /*
  Evaluate an expression.

  An expression is represented by an object with the following
  structure:

      expression = {
          'operator': '',
          'operands': []
      }

  :arg object expression: An expression.
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
  Reader specific functions.
  */

  /*
  Extract a field from {data} using either a fixed size, or a delimiter. After
  reading, {offset} is set to the next field.

  :arg int size: Size of fixed size field.
  :return str: Content of the requested field.
  */
  function getField(size, delimiter) {
    var field,
        extracted,
        separator;

    if (offset >= data.length) {
      throw('StopIteration');
    }

    separator = String.fromCharCode.apply(this, delimiter)
    if (size) {
      // Fixed sized field.
      field = data.slice(offset, offset + size);
      extracted = size;
      if (delimiter.length) {
        // A variable sized field in a fixed sized field.
        field = field.split(separator)[0];
      }
    }
    else {
      // Variable sized field.
      field = data.slice(offset, -1).split(separator)[0];
      extracted = field.length + 1;
    }

    offset += extracted;
    return field;
  }

  /*
  Parse a primitive data type.
  
  :arg object item: Data structure.
  :arg str dtype: Data type.
  :arg object dest: Destination object.
  :arg str name: Field name used in the destination dictionary.
  */
  function parsePrimitive(item, dtype, dest, name) {
    var temp = getFunction(item, dtype),
        delim = temp[0],
        size = temp[1],
        func = temp[2],
        kwargs = temp[3],
        data,
        member,
        result,
        unknownDest;

    if (name) {
      // Read and process the data.
      result = functions[func](getField(size, delim), kwargs);
      if (result.constructor === Object) {
        // Unpack dictionaries in order to use the items in evaluations.
        for (member in result) {
          internal[member] = result[member];
        }
      }
      else {
        internal[name] = result;
      }
      dest[name] = result;
    }
    else {
      // Stow unknown data away in a list.
      data = getField(size, []);
      if (!prune) {
        unknownDest = getDefault(item, dtype, 'unknown_destination');
        if (!(unknownDest in dest)) {
          dest[unknownDest] = [];
        }
        dest[unknownDest].push(
          functions[getDefault(item, dtype, 'unknown_function')](data));
      }
    }
  }

  /*
  Parse a for loop.
  
  :arg object item: Data structure.
  :arg object dest: Destination object.
  :arg str name: Field name used in the destination dictionary.
  */
  function parseFor(item, dest, name) {
    var length = item.for,
        structureDict,
        _;

    if (length.constructor !== Number) {
      length = internal[length];
    }

    for (_ = 0; _ < length; _++) {
      structureDict = {};
      parse(item['structure'], structureDict);
      dest[name].push(structureDict);
    }
  }

  /*
  Parse a do-while loop.
  
  :arg object item: Data structure.
  :arg object dest: Destination object.
  :arg str name: Field name used in the destination dictionary.
  */
  function parseDoWhile(item, dest, name) {
    var structureDict;

    while (true) {
      structureDict = {};
      parse(item['structure'], structureDict);
      dest[name].push(structureDict);
      if (!evaluate(item.do_while)) {
        break;
      }
    }
  }

  /*
  Parse a while loop.
  
  :arg object item: Data structure.
  :arg object dest: Destination object.
  :arg str name: Field name used in the destination dictionary.
  */
  function parseWhile(item, dest, name) {
    var delim = item.structure[0];

    dest[name] = [{}];
    parse([delim], dest[name][0]);
    while (true) {
      if (!evaluate(item.while)) {
        break;
      }
      parse(item.structure.slice(1), dest[name].slice(-1)[0]);
      dest[name].push({});
      parse([delim], dest[name].slice(-1)[0]);
    }
    dest[item.while.term] = getOneValue(dest[name].pop(-1));
  }

  /*
  Parse a binary file.

  :arg object structure: Structure of the binary file.
  :arg object dest: Destination object.
  */
  function parse(structure, dest) {
    var item,
        name,
        dtype,
        index;

    for (index = 0; index < structure.length; index++) {
      item = structure[index];

      if (item.if) {
        // Conditional statement.
        if (!evaluate(item.if)) {
          continue;
        }
      }

      dtype = getDefault(item, '', 'type');
      name = getDefault(item, dtype, 'name');

      if (!item.structure) {
        // Primitive data types.
        parsePrimitive(item, dtype, dest, name);
      }
      else {
        // Nested structures.
        if (!dest[name]) {
          if (item.for || item.do_while || item.while) {
            dest[name] = [];
          }
          else {
            dest[name] = {};
          }
        }

        if (item.for) {
          parseFor(item, dest, name);
        }
        else if (item.do_while) {
          parseDoWhile(item, dest, name);
        }
        else if (item.while) {
          parseWhile(item, dest, name);
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
    console.log('---');
    console.log(yaml.dump(this.parsed));
  };

  /*
  Initialisation.
  */
  if (types_data.constants) {
    update(constants, types_data.constants);
  }
  if (types_data.defaults) {
    update(defaults, types_data.defaults);
  }
  if (types_data.types) {
    update(types, types_data.types);
  }

  this.types = types;
  this.constants = constants;
  this.defaults = defaults;

  /*
  Reader specific initialisation.
  */

  data = fileContent;
  parsed = {};
  offset = 0;

  try {
    parse(structure, parsed);
  }
  catch(err) {
    if (err !== 'StopIteration') {
      throw(err);
    }
  }

  this.data = data;
  this.parsed = parsed;
}

module.exports.BinReader = BinReader;
module.exports.update = update;
module.exports.pop = pop;
module.exports.numerical = numerical;
module.exports.getOneValue = getOneValue;
