'use strict';

/*
General binary file parser.

(C) 2015 Jeroen F.J. Laros <J.F.J.Laros@lumc.nl>
*/

var Buffer = require('buffer-extend-split'),
    yaml = require('js-yaml');

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
function BinParser(structureContent, typesContent, functions) {
  var types_data = typesContent;

  /*
  Resolve the value of a variable.
 
  First look in the cache to see if `name` is defined, then check the set
  of constants. If nothing can be found, the variable is considered to be
  a literal.
 
  :arg any name: The name or value of a variable.
  :returns any: The resolved value.
  */
  this.getValue = function(name) {
    if (this.internal[name] !== undefined) {
      return this.internal[name];
    }
    if (this.constants[name] !== undefined) {
      return this.constants[name];
    }
    return name;
  };

  /*
  Resolve the value of a member variable.

  First see if the variable is defined in `item`, then check the type
  definition and lastly check the defaults.

  :arg object item: Data structure.
  :arg str dtype: Name of the data type.
  :arg str name: The name of the variable.

  :returns any: The resolved value.
  */
  this.getDefault = function(item, dtype, name) {
    if (item[name] !== undefined) {
      return item[name];
    }
    if ((this.types[dtype] !== undefined) &&
        (this.types[dtype][name] !== undefined)) {
      return this.types[dtype][name];
    }
    if (this.defaults[name] !== undefined) {
      return this.defaults[name];
    }
    return undefined;
  };

  /*
  Determine what to read and how to interpret what was read.

  First resolve the `delimiter` and `size`. If none are given, assume we
  read one byte. Then resolve the function that will interpret the data
  (either delimited or fixed size).

  :arg object item: Data structure.
  :arg str dtype: Name of the data type.

  :returns tuple: (`delim`, `size`, `func`, `kwargs`).
  */
  this.getFunction = function(item, dtype) {
    var delim = this.getDefault(item, dtype, 'delimiter'),
        size = this.getDefault(item, dtype, 'size'),
        func = dtype,
        kwargs = {};

    if (!(delim.length || size)) {
      size = 1;
    }

    // Determine the function and its arguments.
    if ('function' in this.types[dtype]) {
      if ('name' in this.types[dtype].function) {
        func = this.types[dtype].function.name;
      }
      if ('args' in this.types[dtype].function) {
        kwargs = this.types[dtype].function.args;
      }
    }
    return [delim, size, func, kwargs];
  };

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
  this.evaluate = function(expression) {
    var operands = [],
        index;

    for (index = 0; index < expression.operands.length; index++) {
      operands.push(this.getValue(expression.operands[index]));
    }

    if ((operands.length === 1) && (expression.operator === undefined)) {
      return operands[0];
    }
    return Functions.operators[expression.operator].apply(this, operands);
  };

  /*
  Initialisation.
  */
  this.internal = {};

  this.functions = functions || new Functions.BinReadFunctions();

  this.constants = {};
  this.defaults = {
    'delimiter': [],
    'name': '',
    'size': 0,
    'type': 'text',
    'unknown_destination': '__raw__',
    'unknown_function': 'raw'
  };
  this.types = {
    'int': {},
    'raw': {}
  };

  if (types_data.constants) {
    update(this.constants, types_data.constants);
  }
  if (types_data.defaults) {
    update(this.defaults, types_data.defaults);
  }
  if (types_data.types) {
    update(this.types, types_data.types);
  }

  this.structure = structureContent;
}

/*
General binary file reader.
*/
function BinReader(
    fileContent, structureContent, typesContent, functions, prune) {
  var prune = prune || false,
      offset = 0;

  /*
  Extract a field from {data} using either a fixed size, or a delimiter. After
  reading, {offset} is set to the next field.

  :arg int size: Size of fixed size field.
  :return str: Content of the requested field.
  */
  this.getField = function(size, delimiter) {
    var field,
        extracted,
        separator;

    if (offset >= this.data.length) {
      throw('StopIteration');
    }

    separator = String.fromCharCode.apply(this, delimiter)
    if (size) {
      // Fixed sized field.
      field = this.data.slice(offset, offset + size);
      extracted = size;
      if (delimiter.length) {
        // A variable sized field in a fixed sized field.
        field = field.split(separator)[0];
      }
    }
    else {
      // Variable sized field.
      field = this.data.slice(offset, -1).split(separator)[0];
      extracted = field.length + 1;
    }

    offset += extracted;
    return field;
  };

  /*
  Parse a primitive data type.
  
  :arg object item: Data structure.
  :arg str dtype: Data type.
  :arg object dest: Destination object.
  :arg str name: Field name used in the destination dictionary.
  */
  this.parsePrimitive = function(item, dtype, dest, name) {
    var delim,
        func,
        kwargs,
        member,
        result,
        size,
        temp,
        unknownDest;

    // Read and process the data.
    if (!name) {
      dtype = this.getDefault(item, '', 'unknown_function');
    }
    temp = this.getFunction(item, dtype);
    delim = temp[0];
    size = temp[1];
    func = temp[2];
    kwargs = temp[3];
    result = this.functions[func](this.getField(size, delim), kwargs);

    if (name) {
      // Store the data.
      if (result.constructor === Object) {
        // Unpack dictionaries in order to use the items in evaluations.
        for (member in result) {
          this.internal[member] = result[member];
        }
      }
      else {
        this.internal[name] = result;
      }
      dest[name] = result;
    }
    else {
      // Stow unknown data away in a list.
      if (!prune) {
        unknownDest = this.getDefault(item, dtype, 'unknown_destination');
        if (!(unknownDest in dest)) {
          dest[unknownDest] = [];
        }
        dest[unknownDest].push(result);
      }
    }
  };

  /*
  Parse a for loop.
  
  :arg object item: Data structure.
  :arg object dest: Destination object.
  :arg str name: Field name used in the destination dictionary.
  */
  this.parseFor = function(item, dest, name) {
    var length = item.for,
        structureDict,
        _;

    if (length.constructor !== Number) {
      length = this.internal[length];
    }

    for (_ = 0; _ < length; _++) {
      structureDict = {};
      this.parse(item['structure'], structureDict);
      dest[name].push(structureDict);
    }
  };

  /*
  Parse a do-while loop.
  
  :arg object item: Data structure.
  :arg object dest: Destination object.
  :arg str name: Field name used in the destination dictionary.
  */
  this.parseDoWhile = function(item, dest, name) {
    var structureDict;

    while (true) {
      structureDict = {};
      this.parse(item['structure'], structureDict);
      dest[name].push(structureDict);
      if (!this.evaluate(item.do_while)) {
        break;
      }
    }
  };

  /*
  Parse a while loop.
  
  :arg object item: Data structure.
  :arg object dest: Destination object.
  :arg str name: Field name used in the destination dictionary.
  */
  this.parseWhile = function(item, dest, name) {
    var delim = item.structure[0];

    dest[name] = [{}];
    this.parse([delim], dest[name][0]);
    while (true) {
      if (!this.evaluate(item.while)) {
        break;
      }
      this.parse(item.structure.slice(1), dest[name].slice(-1)[0]);
      dest[name].push({});
      this.parse([delim], dest[name].slice(-1)[0]);
    }
    dest[item.while.term] = getOneValue(dest[name].pop(-1));
  };

  /*
  Parse a binary file.

  :arg object structure: Structure of the binary file.
  :arg object dest: Destination object.
  */
  this.parse = function(structure, dest) {
    var item,
        name,
        dtype,
        index;

    for (index = 0; index < structure.length; index++) {
      item = structure[index];
      //console.log(item);

      if (item.if) {
        // Conditional statement.
        if (!this.evaluate(item.if)) {
          continue;
        }
      }

      dtype = this.getDefault(item, '', 'type');
      name = this.getDefault(item, dtype, 'name');

      if (!item.structure) {
        // Primitive data types.
        this.parsePrimitive(item, dtype, dest, name);
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
          this.parseFor(item, dest, name);
        }
        else if (item.do_while) {
          this.parseDoWhile(item, dest, name);
        }
        else if (item.while) {
          this.parseWhile(item, dest, name);
        }
        else {
          this.parse(item.structure, dest[name]);
        }
      }
    }
  };

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
  BinParser.call(this, structureContent, typesContent, functions);

  this.data = fileContent;
  this.parsed = {};

  try {
    this.parse(this.structure, this.parsed);
  }
  catch(err) {
    if (err !== 'StopIteration') {
      throw(err);
    }
  }
}

module.exports.BinReader = BinReader;
module.exports.update = update;
module.exports.pop = pop;
module.exports.numerical = numerical;
module.exports.getOneValue = getOneValue;
