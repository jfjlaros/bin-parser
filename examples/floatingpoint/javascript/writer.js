#!/usr/bin/env node

'use strict';

var fs = require('fs'),
    yaml = require('js-yaml');

var BinParser = require('../../../javascript/index');

function main() {
  var parser = new BinParser.BinWriter(
    yaml.load(fs.readFileSync('../float.yml')),
    yaml.load(fs.readFileSync('../structure.yml')),
    yaml.load(fs.readFileSync('../types.yml')),
    {});

    process.stdout.write(parser.data);
}

// Wait for the stdout buffer to drain, see
// https://github.com/eslint/eslint/issues/317
process.on('exit', function() {
  process.reallyExit(main());
});
