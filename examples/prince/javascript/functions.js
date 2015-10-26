var BinReadFunctions = require('../../../javascript/functions');

BinReadFunctions.BinReadFunctions.prototype.min = function(data) {
  return this.int(data) - 1;
}

BinReadFunctions.BinReadFunctions.prototype.sec = function(data) {
  return Math.floor(this.int(data) / 12);
}
