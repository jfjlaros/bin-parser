#!/usr/bin/env node

'use strict';

var fs = require('fs'),
    path = require('path'),
    yaml = require('js-yaml');

var BinReader = require('./index');

var main = function(filename, structure, types) {
  var parser = new BinReader.BinReader(
    fs.readFileSync(filename).toString('binary'),
    yaml.load(fs.readFileSync(structure).toString('binary')),
    yaml.load(fs.readFileSync(types).toString('binary')));

  parser.dump();
};

var exitCode = main(
  path.resolve(process.cwd(), process.argv[2]),
  path.resolve(process.cwd(), process.argv[3]),
  path.resolve(process.cwd(), process.argv[4])
);

/*
Wait for the stdout buffer to drain.
See https://github.com/eslint/eslint/issues/317
*/
process.on('exit', function() {
  process.reallyExit(exitCode);
});
