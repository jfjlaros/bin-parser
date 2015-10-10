#!/bin/bash

# Test whether the YAML produced by the JavaScript version equals that of the
# Python version.
test_cli() {
  seed=${RANDOM}
  py="/tmp/${seed}_py.yml"
  js="/tmp/${seed}_js.yml"

  python -m python.cli read $1 $2 $3 $py
  nodejs javascript/cli.js $1 $2 $3 > $js

  echo "  $1"
  python -m extras.compare_yaml $py $js

  rm $py $js
}

# Test whether the generated YAML is invariant under writing to binary and
# back.
test_writer() {
  seed=${RANDOM}
  yml_1="/tmp/${seed}_1.yml"
  yml_2="/tmp/${seed}_2.yml"
  bin="/tmp/${seed}.bin"

  python -m python.cli read $1 $2 $3 $yml_1
  python -m python.cli write $yml_1 $2 $3 $bin
  python -m python.cli read $bin $2 $3 $yml_2

  echo "  $1"
  python -m extras.compare_yaml $yml_1 $yml_2

  rm $yml_1 $yml_2 $bin
}

echo Python vs. JavaScript tests:
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

echo
echo Writer tests:
test_writer examples/balance/balance.dat examples/balance/structure.yml \
  examples/balance/types.yml
test_writer examples/conditional/a.dat examples/conditional/structure.yml \
  examples/conditional/types.yml
test_writer examples/conditional/b.dat examples/conditional/structure.yml \
  examples/conditional/types.yml
test_writer examples/csv/test.csv examples/csv/structure.yml \
  examples/csv/types.yml
test_writer examples/lists/do_while.dat examples/lists/structure_do_while.yml \
  examples/lists/types.yml
test_writer examples/lists/for.dat examples/lists/structure_for.yml \
  examples/lists/types.yml
test_writer examples/lists/while.dat examples/lists/structure_while.yml \
  examples/lists/types.yml
