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
function BinReader(fileContent, structureContent, typesContent, functions) {
  var data = fileContent,
      internal = {},
      functions = functions || new Functions.BinReadFunctions(),
      constants = {},
      defaults = {
        'size': 0,
        'delimiter': [],
        'type': 'text'
      },
      types = {
        'raw': {},
        'int': {}
      },
      types_data = typesContent,
      offset = 0,
      structure = structureContent;

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
    if (constants[name] !== undefined) {
      return constants[name];
    }
    return name;
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

  function getDefault(item, dtype, name) {
    if (name in item) {
      return item[name];
    }
    if (name in types[dtype]) {
      return types[dtype][name];
    }
    if (name in defaults) {
      return defaults[name];
    }
    return undefined;
  }

  /*
  Parse a primitive data type.
  
  :arg dict item: A dictionary.
  :arg str dtype: Data type.
  :arg dict dest: Destination dictionary.
  :arg str name: Field name used in the destination dictionary.
  */
  function parsePrimitive(item, dtype, dest, name) {
    var delim = getDefault(item, dtype, 'delimiter'),
        size = getDefault(item, dtype, 'size'),
        func = dtype,
        kwargs = {},
        member,
        result;

    if (!(delim.length || size)) {
      size = 1;
    }

    if (name) {
      // Determine the function and its arguments.
      if (types[dtype].function) {
        if (types[dtype].function.name) {
          func = types[dtype].function.name;
        }
        if (types[dtype].function.args) {
          kwargs = types[dtype].function.args;
        }
      }

      // Read and process the data.
      result = functions[func](getField(size, delim), kwargs);
      if (result.constructor === Object) {
        for (member in result) {
          dest[member] = result[member];
          internal[member] = result[member];
        }
      }
      else {
        dest[name] = result;
        internal[name] = result;
      }
    }
    else {
      getField(size, []);
    }
  }

  /*
  Parse a for loop.
  
  :arg dict item: A dictionary.
  :arg dict dest: Destination dictionary.
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
  
  :arg dict item: A dictionary.
  :arg dict dest: Destination dictionary.
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
  
  :arg dict item: A dictionary.
  :arg dict dest: Destination dictionary.
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

      name = item.name || '';
      dtype = item.type || defaults.type;

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
  Get parsed object.
  this.getParsed = function() {
    return parsed;
  };
  */
  this.parsed = {};

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

  try {
    parse(structure, this.parsed);
  }
  catch(err) {
    if (err !== 'StopIteration') {
      throw(err);
    }
  }

  this.types = types;
  this.constants = constants;
  this.defaults = defaults;
}

module.exports.BinReader = BinReader;
module.exports.update = update;
module.exports.pop = pop;
module.exports.numerical = numerical;
module.exports.getOneValue = getOneValue;
