#!/usr/bin/env node

'use strict';

var fs = require('fs'),
    yaml = require('js-yaml');

var BinParser = require('../../../javascript/index');

var PrinceReadFunctions = require('./functions');

function main() {
  var parser = new BinParser.BinReader(
    fs.readFileSync('../prince.hof'),
    yaml.load(fs.readFileSync('../structure.yml')),
    yaml.load(fs.readFileSync('../types.yml')),
    {'functions': new PrinceReadFunctions.PrinceReadFunctions()});

  process.stdout.write(yaml.dump(parser.parsed));
}

/*
 * Wait for the stdout buffer to drain, see
 * https://github.com/eslint/eslint/issues/317
 */
process.on('exit', function() {
  process.reallyExit(main());
});
