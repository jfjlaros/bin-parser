#!/usr/bin/env node

'use strict';

var fs = require('fs'),
    path = require('path');
    //BinParser = require('./index');

var Functions = require('./functions');

var main = function(filename) {
  var f = new Functions.BinParseFunctions(
    fs.readFileSync(filename).toString('binary'));

  console.log(f.bit('a'));

  //var BP = new BinParser(fs.readFileSync(filename).toString('binary'));

  //BP.dump();
};

var exitCode = main(
  path.resolve(process.cwd(), process.argv[2])
);

/*
Wait for the stdout buffer to drain.
See https://github.com/eslint/eslint/issues/317
*/
process.on('exit', function() {
  process.reallyExit(exitCode);
});
