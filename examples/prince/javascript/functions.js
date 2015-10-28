var BinReadFunctions = require('../../../javascript/functions');

function PrinceReadFunctions() {
  this.min = function(data) {
    return this.int(data) - 1;
  };

  this.sec = function(data) {
    return Math.floor(this.int(data) / 12);
  };

  BinReadFunctions.BinReadFunctions.call(this);
}

module.exports.PrinceReadFunctions = PrinceReadFunctions;
