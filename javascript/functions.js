"use strict";

/* Field packing and unpacking functions for the general binary parser. */

var Buffer = require("buffer-extend-split"),
    iconv = require("iconv-lite"),
    struct = require("python-struct");

var deprecated = require("./deprecated");

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
  /**
   * Decode basic and simple compound data types.
   *
   * Primary decoding is controlled with the `fmt` parameter (see
   * https://docs.python.org/2/library/struct.html for more information),
   * which yields a list of values. These values are optionally substituted
   * using `annotation` as a substitution scheme.
   * If the list has only one element, this element is returned, if `labels`
   * is defined, a set of key-value pairs is returned, the bare list is
   * returned otherwise.
   *
   * @arg {string} data - Input data.
   * @arg {string} fmt - Format characters.
   * @arg {Array} labels - Labels for the decoded data units.
   * @arg {Object} annotation - Names for special cases.
   *
   * @returns {} - Decoded data.
   */
  this.struct = function(data, kwargs) {
    var fmt = kwargs.fmt || "b",
        labels = kwargs.labels,
        annotation = kwargs.annotation,
        decoded = struct.unpack(fmt, data),
        kvSet = {},
        index, value;

    if (annotation !== undefined) {
      for (index = 0; index < decoded.length; index++) {
        value = decoded[index];

        if (value in annotation) {
          decoded[index] = annotation[value];
        }
      }
    }

    if (decoded.length > 1) {
      if (labels !== undefined) {
        for (index = 0; index < labels.length; index++) {
          kvSet[labels[index]] = decoded[index];
        }
        return kvSet;
      }
      return decoded;
    }
    return decoded[0];
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
  // TODO: Deprecated, remove.
  this.int = function(data) {
    var result = 0,
        index;

    deprecated.deprecationWarning("int");
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
  // TODO: Deprecated, remove.
  this.float = function(data) {
    deprecated.deprecationWarning("float");
    return data.readFloatBE();
  };

  // TODO: Deprecated, remove.
  this.colour = function(data) {
    deprecated.deprecationWarning("colour");
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
  // TODO: Deprecated, remove.
  this.date = function(data, kwargs) {
    var annotation = kwargs.annotation,
        dateInt = this.int(data);

    deprecated.deprecationWarning("date");
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
  // TODO: Deprecated, remove.
  this.map = function(data, kwargs) {
    var annotation = kwargs.annotation,
        index = ord(data);

    deprecated.deprecationWarning("map");
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
        flagsDict = {},
        flag,
        value;

    for (flag = 0x01; flag < 0x100; flag <<= 1) {
      value = Boolean(flag & bitfield);

      if (!annotation[flag]) {
        if (value) {
          flagsDict["flag_" + pad(hex(flag), 2)] = value;
        }
      }
      else {
        flagsDict[annotation[flag]] = value;
      }
    }
    return flagsDict;
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
    var fmt = kwargs.fmt || "b",
        labels = kwargs.labels,
        annotation = kwargs.annotation,
        dataList = [],
        inverseAnnotation,
        index, value;

    if (typeof(data) === "object") {
      if (!Array.isArray(data)) {
        for (index = 0; index < labels.length; index++) {
          dataList.push(data[labels[index]]);
        }
      }
      else {
        dataList = data;
      }
    }
    else {
      dataList.push(data);
    }

    if (annotation !== undefined) {
      inverseAnnotation = inverseDict(annotation);

      for (index = 0; index < dataList.length; index++) {
        value = dataList[index];

        if (value in inverseAnnotation) {
          dataList[index] = inverseAnnotation[value];
        }
      }
    }

    return struct.pack(fmt, dataList);
  };

  this.raw = function(hexString) {
    return new Buffer(hexString.split(" ").map(unHex));
  };

  this.bit = function(bitString) {
    return new Buffer([parseInt(bitString, 2)]);
  };

  // TODO: Deprecated, remove.
  this.int = function(integer) {
    var dataInt = integer,
        result = [];

    deprecated.deprecationWarning("int");
    while (dataInt) {
      result.push(dataInt % 0x100);
      dataInt >>= 8;
    }

    if (result.length) {
      return new Buffer(result);
    }
    return new Buffer([0x00]);
  };

  // TODO: Deprecated, remove.
  this.float = function(realNumber) {
    var data = new Buffer(4);

    deprecated.deprecationWarning("float");
    data.writeFloatBE(realNumber);
    return data;
  };

  // TODO: Deprecated, remove.
  this.colour = function(colourString) {
    deprecated.deprecationWarning("colour");
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

  // TODO: Deprecated, remove.
  this.date = function(dateInt, kwargs) {
    var inverseAnnotation = inverseDict(kwargs.annotation),
        dateString = dateInt;

    deprecated.deprecationWarning("date");
    if (dateInt in inverseAnnotation) {
      dateString = parseInt(inverseAnnotation[dateInt]);
    }
    return this.int(parseInt(dateString));
  };

  // TODO: Deprecated, remove.
  this.map = function(mappedString, kwargs) {
    deprecated.deprecationWarning("map");
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
      if (flagsDict[key]) {
        if (key in inverseAnnotation) {
            values += parseInt(inverseAnnotation[key]);
        }
        else {
          values += parseInt(key.slice(5), 0x10);
        }
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
