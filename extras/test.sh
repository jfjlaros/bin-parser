#!/bin/bash

# Test whether the YAML produced by the JavaScript version equals that of the
# Python version.
test_cli() {
  local seed="${RANDOM}"
  local py="/tmp/${seed}_py.yml"
  local js="/tmp/${seed}_js.yml"

  echo "  ${1}"
  python -m python.cli read "${1}" "${2}" "${3}" "${py}"
  nodejs javascript/cli.js read "${1}" "${2}" "${3}" "${js}"

  compare_yaml "${py}" "${js}"

  rm "${py}" "${js}"
}

# Test whether the generated YAML is invariant under writing to binary and
# back.
test_writer() {
  local seed="${RANDOM}"
  local yml_1="/tmp/${seed}_1.yml"
  local yml_2="/tmp/${seed}_2.yml"
  local bin_1="/tmp/${seed}_1.bin"
  local bin_2="/tmp/${seed}_2.bin"

  python -m python.cli read "${1}" "${2}" "${3}" "${yml_1}"
  python -m python.cli write "${yml_1}" "${2}" "${3}" "${bin_1}"
  nodejs javascript/cli.js write "${yml_1}" "${2}" "${3}" "${bin_2}"
  python -m python.cli read "${bin_1}" "${2}" "${3}" "${yml_2}"

  echo "  ${1}"
  compare_yaml "${yml_1}" "${yml_2}"
  diff "${bin_1}" "${bin_2}"

  rm "${yml_1}" "${yml_2}" "${bin_1}" "${bin_2}"
}

echo 'Python vs. JavaScript tests:'
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
test_cli examples/var_size/var_size.dat examples/var_size/structure.yml \
  examples/var_size/types.yml
test_cli examples/padding/padding.dat examples/padding/structure.yml \
  examples/padding/types.yml
test_cli examples/order/order.dat examples/order/structure.yml \
  examples/order/types.yml
test_cli examples/map/map.dat examples/map/structure.yml \
  examples/map/types.yml
test_cli examples/flags/flags.dat examples/flags/structure.yml \
  examples/flags/types.yml
test_cli examples/colour/colour.dat examples/colour/structure.yml \
  examples/colour/types.yml
test_cli examples/macro/macro.dat examples/macro/structure_plain.yml \
  examples/macro/types.yml
test_cli examples/macro/macro.dat examples/macro/structure_nested.yml \
  examples/macro/types.yml
test_cli examples/macro/macro.dat examples/macro/structure.yml \
  examples/macro/types.yml

echo
echo 'Writer tests:'
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
test_writer examples/var_size/var_size.dat examples/var_size/structure.yml \
  examples/var_size/types.yml
test_writer examples/padding/padding.dat examples/padding/structure.yml \
  examples/padding/types.yml
test_writer examples/order/order.dat examples/order/structure.yml \
  examples/order/types.yml
test_writer examples/map/map.dat examples/map/structure.yml \
  examples/map/types.yml
test_writer examples/flags/flags.dat examples/flags/structure.yml \
  examples/flags/types.yml
test_writer examples/colour/colour.dat examples/colour/structure.yml \
  examples/colour/types.yml
test_writer examples/macro/macro.dat examples/macro/structure_plain.yml \
  examples/macro/types.yml
test_writer examples/macro/macro.dat examples/macro/structure_nested.yml \
  examples/macro/types.yml
test_writer examples/macro/macro.dat examples/macro/structure.yml \
  examples/macro/types.yml

echo
echo 'Interface test:'
cd examples/balance
echo -n '  Balance'
if [ "$(python parser.py)" != "$(nodejs parser.js)" ]; then
  echo ' failed.'
else
  echo '.'
fi
cd - > /dev/null

echo
echo 'Inheritance tests:'
cd examples/prince/python
echo '  Prince reader.'
compare_yaml <(python reader.py) <(nodejs ../javascript/reader.js)
echo -n '  Prince writer'
py_checksum=$(python writer.py | md5sum)
js_checksum=$(nodejs ../javascript/writer.js | md5sum)
if [ "${py_checksum}" != "${js_checksum}" ]; then
  echo ' failed.'
else
  echo '.'
fi
cd - > /dev/null
