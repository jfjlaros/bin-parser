'use strict';

/*
Field unpacking functions for the general binary parser.

(C) 2015 Jeroen F.J. Laros <J.F.J.Laros@lumc.nl>
*/

var yaml = require('js-yaml');

module.exports.operators = {
  'not': function(a) { return !a; },
  'and': function(a, b) { return a && b; },
  'or': function(a, b) { return a || b; },
  'xor': function(a, b) { return a ^ b; },
  'eq': function(a, b) { return a === b; },
  'ne': function(a, b) { return a !== b; },
  'ge': function(a, b) { return a >= b; },
  'gt': function(a, b) { return a > b; },
  'le': function(a, b) { return a <= b; },
  'lt': function(a, b) { return a < b; },
  'mod': function(a, b) { return a % b; },
  'contains': function(a, b) { return a in b; }
};

/*
Miscellaneous functions.
*/

function ord(character) {
  return character.charCodeAt(0);
}

function hex(value) {
  return value.toString(16);
}

/*
Pad a string with leading zeroes.

:arg any input: String to be padded.
:arg int length: Length of the resulting string.

:return str: Padded string.
*/
function pad(input, length) {
  var string = input.toString(),
      padding = '',
      index;

  for (index = 0; index < length - string.length; index++) {
    padding += '0';
  }
  return padding + string;
}

/*
Encode a string in hexadecimal.

:arg str data: Input string.

:return str: Hexadecimal representation of {data}.
*/
function convertToHex(data) {
  var result = '',
      index;

  for (index = 0; index < data.length; index++) {
    result += pad(hex(data.charCodeAt(index)), 2);
  }
  return result;
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

function BinParseFunctions(typesHandle) {
  var types = yaml.load(typesHandle);

  this.raw = function(data) {
    return convertToHex(data);
  };

  this.bit = function(data) {
    var bitField = data.charCodeAt(0),
        result = '',
        mask;

    for (mask = 0x80; mask; mask >>= 1) {
      result += (+Boolean(bitField & mask)).toString();
    }
    return result;
  };

  /*
  Decode a little-endian encoded integer.

  Decoding is done as follows:
  - Reverse the order of the bits.
  - Convert the bits to ordinals.
  - Interpret the list of ordinals as digits in base 256.

  :arg str data: Little-endian encoded integer.

  :return int: Integer representation of {data}
  */
  this.int = function(data) {
    var result = 0,
        index;

    for (index = data.length - 1; index >= 0; index--) {
      result = result * 0x100 + data.charCodeAt(index);
    }
    return result;
  };

  this.colour = function(data) {
    return '0x' + pad(hex(this.int(data)), 6);
  };

  this.trim = function(data) {
    var delimiter = String.fromCharCode(types.trim.delimiter);

    return data.split(delimiter)[0];
  };

  this.text = function(data, delimiter) {
    var field = data.split(String.fromCharCode(types.text.delimiter))[0];

    if (delimiter) {
      return field.split(String.fromCharCode(
        types.text.data[delimiter])).join('\n');
    }
    return field;
  };

  /*
  Decode a date.

  The date is encoded as an integer, representing the year followed by the
  (zero padded) day of the year.

  :arg str data: Binary encoded date.

  :return str: Date in format '%Y%j', 'defined' or 'unknown'.
  */
  this.date = function(data) {
    var dateInt = this.int(data);

    if (dateInt in types.date.data) {
      return types.date.data[dateInt];
    }
    return dateInt.toString();
  };

  /*
  Replace a value with its annotation.

  :arg str data: Encoded data.
  :arg dict annotation: Annotation of {data}.

  :return str: Annotated representation of {data}.
  */
  this.map = function(data, annotation) {
    var index = ord(data);

    if (index in types.map.data[annotation]) {
      return types.map.data[annotation][index];
    }
    return convertToHex(data);
  };

  /*
  Explode a bitfield into flags.

  :arg int data: Bit field.
  :arg str annotation: Annotation of {data}.
  */
  this.flags = function(data, annotation) {
    var bitfield = this.int(data),
        destination = {},
        flag,
        value;

    for (flag = 0x01; flag < 0x100; flag <<= 1) {
      value = Boolean(flag & bitfield);

      if (!types.flags.data[annotation][flag]) {
        if (value) {
          destination['flags_' + annotation + '_' + pad(hex(flag), 2)] = value;
        }
      }
      else {
        destination[types.flags.data[annotation][flag]] = value;
      }
    }
    return destination;
  };

  this.getTypes = function() {
    return types;
  };

  // Add standard data types.
  update(types, {
    'raw': {},
    'list': {}
  });

  // Set default data type.
  if (!types.default) {
    types.default = 'text';
  }
}

module.exports.BinParseFunctions = BinParseFunctions;
