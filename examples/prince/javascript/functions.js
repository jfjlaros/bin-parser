var Functions = require('../../../javascript/functions');

function PrinceReadFunctions() {
  this.min = function(data) {
    return this.struct(data, '<h') - 1;
  };

  this.sec = function(data) {
    return Math.floor(this.struct(data, '<h') / 12);
  };

  Functions.BinReadFunctions.call(this);
}

function PrinceWriteFunctions() {
  this.min = function(minutes) {
    return this.struct(minutes + 1, '<h');
  };

  this.sec = function(seconds) {
    return this.struct(seconds * 12, '<h');
  };

  Functions.BinWriteFunctions.call(this);
}

module.exports = {
  'PrinceReadFunctions': PrinceReadFunctions,
  'PrinceWriteFunctions': PrinceWriteFunctions
};
