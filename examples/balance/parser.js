#!/usr/bin/env node

'use strict';

var fs = require('fs'),
    yaml = require('js-yaml');

var BinParser = require('../../javascript/index');

var parser = new BinParser.BinReader(
  fs.readFileSync('balance.dat'),
  yaml.load(fs.readFileSync('structure.yml')),
  yaml.load(fs.readFileSync('types.yml')),
  {})

console.log(parser.parsed.name);
