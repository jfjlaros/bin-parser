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
      functions = functions || new Functions.BinParseFunctions(),
      tdata = yaml.load(typesHandle),
      types = tdata.types || {},
      constants = tdata.constants || {},
      defaults = tdata.defaults || {},
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
      field = data.slice(offset, -1).split(String.fromCharCode.apply(
        this, delimiter))[0];
      extracted = field.length + 1;
    }

    offset += extracted;
    return field;
  }

  /*
  Store a value both in the destination dictionary, as well as in the
  internal cache.

  :arg dict dest: Destination dictionary.
  :arg str name: Field name used in the destination dictionary.
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
        args,
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
    console.log(yaml.dump(parsed));
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
