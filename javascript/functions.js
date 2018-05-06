"use strict";

/* Field packing and unpacking functions for the general binary parser. */

var Buffer = require("buffer-extend-split"),
    iconv = require("iconv-lite"),
    struct = require("python-struct");

var depricated = require("./depricated");

var operators = {
  "not": function(a) { return !a; },
  "and": function(a, b) { return a && b; },
  "or": function(a, b) { return a || b; },
  "xor": function(a, b) { return a ^ b; },
  "eq": function(a, b) { return a === b; },
  "ne": function(a, b) { return a !== b; },
  "ge": function(a, b) { return a >= b; },
  "gt": function(a, b) { return a > b; },
  "le": function(a, b) { return a <= b; },
  "lt": function(a, b) { return a < b; },
  "mod": function(a, b) { return a % b; },
  "contains": function(a, b) { return a in b; }
};

/* Miscellaneous functions. */

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

/**
 * Pad a string with leading zeroes.
 *
 * @arg {} input - String to be padded.
 * @arg {number} length - Length of the resulting string.
 *
 * @return {string} - Padded string.
 */
function pad(input, length) {
  var string = input.toString(),
      padding = "",
      index;

  for (index = 0; index < length - string.length; index++) {
    padding += "0";
  }
  return padding + string;
}

/**
 * Encode a string in hexadecimal, grouped by byte.
 *
 * @arg {string} data - Input string.
 *
 * @return {string} - Hexadecimal representation of {data}.
 */
function convertToHex(data) {
  var result = "",
      index;

  for (index = 0; index < data.length; index++) {
    result += pad(hex(data[index]), 2);
  }
  return result;
}

/* Functions for decoding data. */
function BinReadFunctions() {
  this.struct = function(data, kwargs) {
    var fmt = kwargs.fmt || "b";

    return struct.unpack(fmt, data)[0]
  };

  /**
   * Encode a string in hexadecimal, grouped by byte.
   *
   * @arg {string} data - Input data.
   *
   * @returns {string} - Hexadecimal representation of {data}.
   */
  this.raw = function(data) {
    return convertToHex(data).match(/.{1,2}/g).join(" ");
  };

  this.bit = function(data) {
    var bitField = data[0],
        result = "",
        mask;

    for (mask = 0x80; mask; mask >>= 1) {
      result += (+Boolean(bitField & mask)).toString();
    }
    return result;
  };

  /**
   * Decode a little-endian encoded integer.
   *
   * Decoding is done as follows:
   * - Reverse the order of the bits.
   * - Convert the bits to ordinals.
   * - Interpret the list of ordinals as digits in base 256.
   *
   * @arg {string} data - Little-endian encoded integer.
   *
   * @return {number} - Integer representation of {data}.
   */
  this.int = function(data) {
    var result = 0,
        index;

    depricated.deprication_warning("int");
    for (index = data.length - 1; index >= 0; index--) {
      result = result * 0x100 + data[index];
    }
    return result;
  };

  /**
   * Decode an IEEE 754 single precision encoded floating-point.
   *
   * @arg {string} data - Big-endian encoded 32bit single precision floating
   *   point.
   *
   * @return {number} - Float representation of {data}.
   */
  this.float = function(data) {
    depricated.deprication_warning("float");
    return data.readFloatBE();
  };

  this.colour = function(data) {
    return "0x" + pad(hex(this.int(data)), 6);
  };

  /**
   * Decode a text string.
   *
   * @arg {string} data - Text string.
   * @arg {Array} kwargs.split - Internal delimiter for end of line.
   * @arg {string} kwargs.encoding - Character encoding.
   *
   * @return {string} - Decoded text.
   */
  this.text = function(data, kwargs) {
    var split = kwargs.split,
        encoding = kwargs.encoding || "utf-8",
        decodedText = iconv.decode(data, encoding);

    if (split) {
      return decodedText.split(
        String.fromCharCode.apply(this, split)).join("\n");
    }
    return decodedText;
  };

  /**
   * Decode a date.
   *
   *  The date is encoded as an integer, representing the year followed by the
   *  (zero padded) day of the year.
   *
   *  @arg {string} data - Binary encoded date.
   *  @arg {Object} kwargs.annotation - Names for special cases.
   *
   *
   *  @return {string} - Date in format "%Y%j", "defined" or "unknown".
   */
  this.date = function(data, kwargs) {
    var annotation = kwargs.annotation,
        dateInt = this.int(data);

    if (dateInt in annotation) {
      return annotation[dateInt];
    }
    return dateInt.toString();
  };

  /**
   * Replace a value with its annotation.
   *
   * @arg {string} data - Encoded data.
   * @arg {Object} kwargs.annotation - Annotation of {data}.
   *
   * @return str - Annotated representation of {data}.
   */
  this.map = function(data, kwargs) {
    var annotation = kwargs.annotation,
        index = ord(data);

    if (index in annotation) {
      return annotation[index];
    }
    return convertToHex(data);
  };

  /**
   * Explode a bitfield into flags.
   *
   * @arg {number} data - Bit field.
   * @arg {string} kwargs.annotation - Annotation of {data}.
   *
   * @return {Object} - Dictionary of flags and their values.
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
          flags_dict["flag_" + pad(hex(flag), 2)] = value;
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
 * Functions for encoding data.
 *
 * Every decoding function in the BinReadFunctions class has a counterpart for
 * encoding. Documentation of these functions is omitted.
 */
function BinWriteFunctions() {
  this.struct = function(data, kwargs) {
    var fmt = kwargs.fmt || "b";

    return struct.pack(fmt, data)
  };

  this.raw = function(hexString) {
    return new Buffer(hexString.split(" ").map(unHex));
  };

  this.bit = function(bitString) {
    return new Buffer([parseInt(bitString, 2)]);
  };

  this.int = function(integer) {
    var dataInt = integer,
        result = [];

    depricated.deprication_warning("int");
    while (dataInt) {
      result.push(dataInt % 0x100);
      dataInt >>= 8;
    }

    if (result.length) {
      return new Buffer(result);
    }
    return new Buffer([0x00]);
  };

  this.float = function(realNumber) {
    var data = new Buffer(4);

    depricated.deprication_warning("float");
    data.writeFloatBE(realNumber);
    return data;
  };

  this.colour = function(colourString) {
    return this.int(parseInt(colourString, 0x10));
  };

  this.text = function(textString, kwargs) {
    var split = kwargs.split,
        encoding = kwargs.encoding || "utf-8",
        decodedText = textString;

    if (split) {
      decodedText = decodedText.split("\n").join(
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
      return new Buffer([inverseAnnotation[mappedString]]);
    }
    return new Buffer([parseInt(mappedString, 0x10)]);
  };

  this.flags = function(flagsDict, kwargs) {
    var inverseAnnotation = inverseDict(kwargs.annotation),
        prefixLen = "flag_".length,
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
    return new Buffer([values]);
  };
}

module.exports = {
  "BinReadFunctions": BinReadFunctions,
  "BinWriteFunctions": BinWriteFunctions,
  "hex": hex,
  "pad": pad,
  "operators": operators
};
