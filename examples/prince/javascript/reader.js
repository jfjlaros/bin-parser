#!/usr/bin/env node

'use strict';

var fs = require('fs'),
    path = require('path'),
    yaml = require('js-yaml');

var BinParser = require('../../../javascript/index');

var PrinceReadFunctions = require('./functions');

var main = function(filename) {
  var parser = new BinParser.BinReader(
    fs.readFileSync('../prince.hof'),
    yaml.load(fs.readFileSync('../structure.yml')),
    yaml.load(fs.readFileSync('../types.yml')),
    new PrinceReadFunctions.PrinceReadFunctions());

  parser.dump();
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
