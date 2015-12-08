#!/usr/bin/env node

'use strict';

var fs = require('fs'),
    yaml = require('js-yaml');

var BinParser = require('../../../javascript/index');

var PrinceWriteFunctions = require('./functions');

function main() {
  var parser = new BinParser.BinWriter(
    yaml.load(fs.readFileSync('../prince.yml')),
    yaml.load(fs.readFileSync('../structure.yml')),
    yaml.load(fs.readFileSync('../types.yml')),
    {'functions': new PrinceWriteFunctions.PrinceWriteFunctions()});

  process.stdout.write(parser.data);
}

// Wait for the stdout buffer to drain, see
// https://github.com/eslint/eslint/issues/317
process.on('exit', function() {
  process.reallyExit(main());
});
