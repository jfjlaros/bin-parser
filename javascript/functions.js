'use strict';

var iconv = require('iconv-lite');

/*
Field packing and unpacking functions for the general binary parser.

(C) 2015 Jeroen F.J. Laros <J.F.J.Laros@lumc.nl>
*/

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
  return character[0];
}

function hex(value) {
  return value.toString(16);
}

function unHex(string) {
  return parseInt(string, 16);
}

function inverseDict(dictionary) {
  var result = {},
      item;

  for (item in dictionary) {
    result[dictionary[item]] = item;
  }
  return result;
}

/*
Pad a string with leading zeroes.

:arg any input: String to be padded.
:arg int length: Length of the resulting string.

:returns str: Padded string.
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
Encode a string in hexadecimal, grouped by byte.

:arg str data: Input string.

:returns str: Hexadecimal representation of {data}.
*/
function convertToHex(data) {
  var result = '',
      index;

  for (index = 0; index < data.length; index++) {
    result += pad(hex(data[index]), 2);
  }
  return result;
}

/*
Functions for decoding data.
*/
function BinReadFunctions() {
  /*
  Encode a string in hexadecimal, grouped by byte.

  :arg str data: Input data.

  :returns str: Hexadecimal representation of {data}.
  */
  this.raw = function(data) {
    return convertToHex(data).match(/.{1,2}/g).join(' ');
  };

  this.bit = function(data) {
    var bitField = data[0],
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

  :returns int: Integer representation of {data}
  */
  this.int = function(data) {
    var result = 0,
        index;

    for (index = data.length - 1; index >= 0; index--) {
      result = result * 0x100 + data[index];
    }
    return result;
  };

  this.colour = function(data) {
    return '0x' + pad(hex(this.int(data)), 6);
  };

  /*
  Decode a text string.

  :arg str data: Text string.
  :arg list(byte) kwargs.split: Internal delimiter for end of line.
  :arg str kwargs.encoding: Character encoding.

  :returns str: Decoded text.
  */
  this.text = function(data, kwargs) {
    var split = kwargs.split,
        encoding = kwargs.encoding || 'utf-8',
        decodedText = iconv.decode(data, encoding);

    if (split) {
      return decodedText.split(
        String.fromCharCode.apply(this, split)).join('\n');
    }
    return decodedText;
  };

  /*
  Decode a date.

  The date is encoded as an integer, representing the year followed by the
  (zero padded) day of the year.

  :arg str data: Binary encoded date.
  :arg dict kwargs.annotation: Names for special cases.


  :returns str: Date in format '%Y%j', 'defined' or 'unknown'.
  */
  this.date = function(data, kwargs) {
    var annotation = kwargs.annotation,
        dateInt = this.int(data);

    if (dateInt in annotation) {
      return annotation[dateInt];
    }
    return dateInt.toString();
  };

  /*
  Replace a value with its annotation.

  :arg str data: Encoded data.
  :arg dict kwargs.annotation: Annotation of {data}.

  :returns str: Annotated representation of {data}.
  */
  this.map = function(data, kwargs) {
    var annotation = kwargs.annotation,
        index = ord(data);

    if (index in annotation) {
      return annotation[index];
    }
    return convertToHex(data);
  };

  /*
  Explode a bitfield into flags.

  :arg int data: Bit field.
  :arg str kwargs.annotation: Annotation of {data}.

  :returns dict: Dictionary of flags and their values.
  */
  this.flags = function(data, kwargs) {
    var annotation = kwargs.annotation,
        bitfield = this.int(data),
        flags_dict = {},
        flag,
        value;

    for (flag = 0x01; flag < 0x100; flag <<= 1) {
      value = Boolean(flag & bitfield);

      if (!annotation[flag]) {
        if (value) {
          flags_dict['flag_' + pad(hex(flag), 2)] = value;
        }
      }
      else {
        flags_dict[annotation[flag]] = value;
      }
    }
    return flags_dict;
  };
}

/*
Functions for encoding data.

Every decoding function in the BinReadFunctions class has a counterpart for
encoding. Documentation of these functions is omitted.
*/
function BinWriteFunctions() {
  this.raw = function(hexString) {
    return hexString.split(' ').map(unHex);
  }

  this.bit = function(bitString) {
    return Buffer([parseInt(bitString, 2)]);
  };

  this.int = function(integer) {
    var dataInt = integer,
        result = [];

    while (dataInt) {
      result.push(dataInt % 0x100);
      dataInt >>= 8;
    }

    if (result.length) {
      return Buffer(result);
    }
    return Buffer([0x00]);
  };

  this.colour = function(colourString) {
    return this.int(parseInt(colourString, 0x10));
  };

  this.text = function(textString, kwargs) {
    var split = kwargs.split,
        encoding = kwargs.encoding || 'utf-8',
        decodedText = textString;

    if (split) {
      decodedText = decodedText.split('\n').join(
        String.fromCharCode.apply(this, split));
    }
    return iconv.encode(decodedText, encoding);
  };

  this.date = function(dateInt, kwargs) {
    var inverseAnnotation = inverseDict(kwargs.annotation),
        dateString = dateInt;

    if (dateInt in inverseAnnotation) {
      dateString = parseInt(inverseAnnotation[dateInt]);
    }
    return this.int(parseInt(dateString));
  };

  this.map = function(mappedString, kwargs) {
    var inverseAnnotation = inverseDict(kwargs.annotation);

    if (mappedString in inverseAnnotation) {
      return Buffer([inverseAnnotation[mappedString]]);
    }
    return Buffer([parseInt(mappedString, 0x10)]);
  };

  this.flags = function(flagsDict, kwargs) {
    var inverseAnnotation = inverseDict(kwargs.annotation),
        prefixLen = 'flag_'.length,
        values = 0x00,
        key;

    for (key in flagsDict) {
      if (key in inverseAnnotation) {
        if (flagsDict[key]) {
          values += parseInt(inverseAnnotation[key]);
        }
      }
      else {
        values += parseInt(key.slice(5), 0x10);
      }
    }
    return Buffer([values]);
  };
}

module.exports.BinReadFunctions = BinReadFunctions;
module.exports.BinWriteFunctions = BinWriteFunctions;
