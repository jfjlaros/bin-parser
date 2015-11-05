#!/usr/bin/env node

'use strict';

/*
Command line interface for the general binary parser.
*/
var fs = require('fs'),
    path = require('path'),
    yaml = require('js-yaml');

var BinReader = require('./index');

function main(inputFile, structure, types, outputFile) {
  var parser = new BinReader.BinReader(
    fs.readFileSync(inputFile),
    yaml.load(fs.readFileSync(structure)),
    yaml.load(fs.readFileSync(types)));

  fs.writeFileSync(outputFile, '---\n');
  fs.appendFileSync(outputFile, yaml.dump(parser.parsed));
}

var exitCode = main(
  path.resolve(process.cwd(), process.argv[2]),
  path.resolve(process.cwd(), process.argv[3]),
  path.resolve(process.cwd(), process.argv[4]),
  path.resolve(process.cwd(), process.argv[5])
);

/*
Wait for the stdout buffer to drain.
See https://github.com/eslint/eslint/issues/317
*/
process.on('exit', function() {
  process.reallyExit(exitCode);
});
