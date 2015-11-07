#!/usr/bin/env node

'use strict';

/*
Command line interface for the general binary parser.
*/
var argparse = require('argparse'),
    fs = require('fs'),
    path = require('path'),
    yaml = require('js-yaml');

var BinReader = require('./index'),
    distMeta = require('../package.json');

/*
Convert a binary file to YAML.

:arg str input_handle: Open readable handle to a binary file.
:arg str structure_handle: Open readable handle to the structure file.
:arg str types_handle: Open readable handle to the types file.
:arg str output_handle: Open writable handle.
:arg bool prune: Remove all unknown data fields from the output.
:arg int debug: Debugging level.
*/
function binReader(inputFile, structureFile, typesFile, outputFile, kwargs) {
  var parser = new BinReader.BinReader(
        fs.readFileSync(inputFile),
        yaml.load(fs.readFileSync(structureFile)),
        yaml.load(fs.readFileSync(typesFile)),
        kwargs);

  if (outputFile === '-') {
    process.stdout.write('---\n');
    process.stdout.write(yaml.dump(parser.parsed));
  }
  else {
    fs.writeFileSync(outputFile, '---\n');
    fs.appendFileSync(outputFile, yaml.dump(parser.parsed));
  }
  if (kwargs.debug) {
    parser.logDebugInfo();
  }
}

/*
Convert a YAML file to binary.

:arg str input_handle: Open readable handle to a YAML file.
:arg str structure_handle: Open readable handle to the structure file.
:arg str types_handle: Open readable handle to the types file.
:arg str output_handle: Open writable handle.
:arg int debug: Debugging level.
*/
function binWriter(inputFile, structureFile, typesFile, outputFile, kwargs) {
  var parser = new BinReader.BinWriter(
        yaml.load(fs.readFileSync(inputFile)),
        yaml.load(fs.readFileSync(structureFile)),
        yaml.load(fs.readFileSync(typesFile)),
        kwargs);

  if (outputFile === '-') {
    process.stdout.write(parser.data);
  }
  else {
    fs.writeFileSync(outputFile, parser.data);
  }
  if (kwargs.debug) {
    parser.logDebugInfo();
  }
}

/*
Command line argument parsing.
*/
function main() {
  var optParser = new argparse.ArgumentParser({addHelp: false}),
      parser = new argparse.ArgumentParser({
        version: distMeta.version,
        addHelp: true,
        description: distMeta.description,
        epilog: 'Copyright (c) ' + distMeta.year + ' ' + distMeta.author +
          '\n\nLicensed under the ' + distMeta.license +
          ' license, see the LICENSE file.',
        formatterClass: argparse.RawDescriptionHelpFormatter
      }),
      subparsers = parser.addSubparsers({
        title:'subcommands',
        dest:"subcommand_name"
      }),
      readParser,
      writeParser,
      args;

  optParser.addArgument(['inputFile'], {help: 'Input file'});
  optParser.addArgument(
    ['structureFile'], {help: 'Structure definition file'});
  optParser.addArgument(['typesFile'], {help: 'Type definition file'});
  optParser.addArgument(['outputFile'], {help: 'Output file'});
  optParser.addArgument(
    ['-d'], {
      dest: 'debug',
      type: 'int', defaultValue: 0,
      help: 'Debugging level (%(type)s default=%(defaultValue)s)'
    });

  readParser = subparsers.addParser(
    'read', {
      parents: [optParser], description: 'Convert a binary file to YAML.'});
  readParser.addArgument(
    ['-p'],
    {dest: 'prune', action: 'storeTrue', help: 'Remove unknown data fields'});

  writeParser = subparsers.addParser(
    'write', {
      parents: [optParser], description: 'Convert a YAML file to binary.'});

  args = parser.parseArgs();

  if (args.subcommand_name == 'read') {
    binReader(
      args.inputFile, args.structureFile, args.typesFile, args.outputFile,
      {'prune': args.prune, 'debug': args.debug});
  }
  if (args.subcommand_name == 'write') {
    binWriter(
      args.inputFile, args.structureFile, args.typesFile, args.outputFile,
      {'debug': args.debug});
  }
}

// Wait for the stdout buffer to drain, see
// https://github.com/eslint/eslint/issues/317
process.on('exit', function() {
  process.reallyExit(main());
});
