var Functions = require('../../../javascript/functions');

function PrinceReadFunctions() {
  this.min = function(data) {
    return this.int(data) - 1;
  };

  this.sec = function(data) {
    return Math.floor(this.int(data) / 12);
  };

  Functions.BinReadFunctions.call(this);
}

function PrinceWriteFunctions() {
  this.min = function(minutes) {
    return this.int(minutes + 1);
  };

  this.sec = function(seconds) {
    return this.int(seconds * 12);
  };

  Functions.BinWriteFunctions.call(this);
}

module.exports.PrinceReadFunctions = PrinceReadFunctions;
module.exports.PrinceWriteFunctions = PrinceWriteFunctions;
