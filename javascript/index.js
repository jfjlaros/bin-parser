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
General binary file parser.
*/
function BinParser(fileContent, structureContent, typesContent, functions) {
  var data = fileContent,
      internal = {},
      functions = functions || new Functions.BinParseFunctions(),
      tdata = typesContent,
      types = tdata.types || {},
      constants = tdata.constants || {},
      defaults = tdata.defaults || {},
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
        extracted;

    if (offset >= data.length) {
      throw('StopIteration');
    }

    if (size) {
      field = data.slice(offset, offset + size);
      extracted = size;
    }
    else {
      field = data.slice(offset, -1).split(String.fromCharCode.apply(
        this, delimiter))[0];
      extracted = field.length + 1;
    }

    offset += extracted;
    return field;
  }

  /*
  Store a value both in the destination object, as well as in the
  internal cache.

  :arg object dest: Destination object.
  :arg str name: Field name used in the destination object.
  :arg any value: Value to store.
  */
  function store(dest, name, value) {
    //console.log(name + ': ' + value + '\n');
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

  /*
  Convenience function for nested structures.

  :arg object item: An object.
  :arg object dest: Destination object.
  :arg str name: Field name used in the destination object.
  */
  function parseStructure(item, dest, name) {
    var structureDict = {};

    parse(item['structure'], structureDict);
    dest[name].push(structureDict);
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
        size,
        func,
        length,
        delim,
        kwargs,
        result,
        index,
        member,
        _;

    for (index = 0; index < structure.length; index++) {
      item = structure[index];

      // Conditional statement.
      if (item.if) {
        if (!evaluate(item.if)) {
          continue;
        }
      }

      name = item.name || '';
      dtype = item.type || types.default;
      if ('structure' in item) {
        dtype = 'list';
      }

      // Primitive data types.
      if (dtype !== 'list') {
        // Determine whether to read a fixed or variable amount.
        delim = [];
        size = defaults.read || 1;
        if (item.read) {
          size = item.read;
        }
        else if (types[dtype].read) {
          if (types[dtype].read.constructor === Array) {
            size = 0;
            delim = types[dtype].read;
          }
          else {
            size = types[dtype].read;
          }
        }

        if (name) {
          // Determine the function and its arguments.
          func = dtype;
          kwargs = {};
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
          delim = item.structure[0];
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

module.exports.BinParser = BinParser;
module.exports.update = update;
module.exports.pop = pop;
module.exports.numerical = numerical;
module.exports.getOneValue = getOneValue;
