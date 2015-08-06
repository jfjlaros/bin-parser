#!/bin/bash

test_cli() {
  seed=${RANDOM}
  py="/tmp/${seed}_py.yml"
  js="/tmp/${seed}_js.yml"

  python -m python.cli $1 $2 $3 $py
  nodejs javascript/cli.js $1 $2 $3 > $js

  echo $1
  python extras/compare_yaml.py $py $js

  rm $py $js
}

test_cli examples/balance/balance.dat examples/balance/structure.yml \
  examples/balance/types.yml
test_cli examples/conditional/a.dat examples/conditional/structure.yml \
  examples/conditional/types.yml
test_cli examples/conditional/b.dat examples/conditional/structure.yml \
  examples/conditional/types.yml
test_cli examples/csv/test.csv examples/csv/structure.yml \
  examples/csv/types.yml
test_cli examples/lists/do_while.dat examples/lists/structure_do_while.yml \
  examples/lists/types.yml
test_cli examples/lists/for.dat examples/lists/structure_for.yml \
  examples/lists/types.yml
test_cli examples/lists/while.dat examples/lists/structure_while.yml \
  examples/lists/types.yml

