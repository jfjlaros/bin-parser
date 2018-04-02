#!/usr/bin/env node

'use strict';

var fs = require('fs'),
    yaml = require('js-yaml');

var BinParser = require('../../javascript/index');
console.log("== starting read test ==");
var parser = new BinParser.BinReader(
  fs.readFileSync('float_input.dat'),
  yaml.load(fs.readFileSync('structure_float.yml')),
  yaml.load(fs.readFileSync('types.yml')),
  {})

console.log(parser.parsed.voltage);
console.log(parser.parsed.frequency);
console.log(parser.parsed.current);

 console.log("== starting write test ==")
 function main() {
   var parser = new BinParser.BinWriter(
     yaml.load(fs.readFileSync('./input.yml')),
     yaml.load(fs.readFileSync('./structure_float.yml')),
     yaml.load(fs.readFileSync('./types.yml')),
     {});
     console.log("binary output",(parser.data));
     process.stdout.write((parser.data));
 }

 // Wait for the stdout buffer to drain, see
 // https://github.com/eslint/eslint/issues/317
 process.on('exit', function() {
   process.reallyExit(main());
 });
