"""Tests for the bin_parser.bin_parser module."""
import yaml

from bin_parser import BinReader, BinWriter


def _bin_reader(path, input_file, structure_file, types_file):
    return BinReader(
        open('examples/{}/{}'.format(path, input_file), 'rb').read(),
        yaml.safe_load(
            open('examples/{}/{}'.format(path, structure_file), 'rb')),
        yaml.safe_load(
            open('examples/{}/{}'.format(path, types_file), 'rb'))).parsed


def _idempotence(path, input_file, structure_file, types_file):
    data = open('examples/{}/{}'.format(path, input_file), 'rb').read()

    parsed = BinReader(
        data,
        yaml.safe_load(
            open('examples/{}/{}'.format(path, structure_file), 'rb')),
        yaml.safe_load(
            open('examples/{}/{}'.format(path, types_file), 'rb'))).parsed

    assert data == BinWriter(
        parsed,
        yaml.safe_load(
            open('examples/{}/{}'.format(path, structure_file), 'rb')),
        yaml.safe_load(
            open('examples/{}/{}'.format(path, types_file), 'rb'))).data


class TestReader(object):
    """Test the python.bin_parser module."""
    def setup(self):
        self._data = {
            'balance': [
                'balance', 'balance.dat', 'structure.yml', 'types.yml'],
            'for': ['lists', 'for.dat', 'structure_for.yml', 'types.yml'],
            'do_while': [
                'lists', 'do_while.dat', 'structure_do_while.yml',
                'types.yml'],
            'while': [
                'lists', 'while.dat', 'structure_while.yml', 'types.yml'],
            'if_a': ['conditional', 'a.dat', 'structure.yml', 'types.yml'],
            'if_b': ['conditional', 'b.dat', 'structure.yml', 'types.yml'],
            'var_size': [
                'var_size', 'var_size.dat', 'structure.yml', 'types.yml'],
            'padding': [
                'padding', 'padding.dat', 'structure.yml', 'types.yml'],
            'order': ['order', 'order.dat', 'structure.yml', 'types.yml'],
            'colour': ['colour', 'colour.dat', 'structure.yml', 'types.yml'],
            'complex_eval': [
                'complex_eval', 'complex_eval.dat', 'structure.yml',
                'types.yml'],
            'csv': ['csv', 'test.csv', 'structure.yml', 'types.yml'],
            'flags': ['flags', 'flags.dat', 'structure.yml', 'types.yml'],
            'map': ['map', 'map.dat', 'structure.yml', 'types.yml'],
            'size_string': [
                'size_string', 'size_string.dat', 'structure.yml',
                'types.yml'],
            'var_type': [
                'var_type', 'var_type.dat', 'structure.yml', 'types.yml']}

    def test_idempotence(self):
        for example in self._data:
            _idempotence(*self._data[example])

    def test_balance_1(self):
        assert _bin_reader(*self._data['balance'])['name'] == 'John Doe'

    def test_balance_2(self):
        assert _bin_reader(*self._data['balance'])['year_of_birth'] == 1999

    def test_balance_3(self):
        assert _bin_reader(*self._data['balance'])['balance'] == 3210

    def test_for_1(self):
        assert _bin_reader(*self._data['for'])['size_of_list'] == 5

    def test_for_2(self):
        assert len(_bin_reader(*self._data['for'])['lines']) == 5

    def test_for_3(self):
        assert _bin_reader(*self._data['for'])[
            'lines'][0]['content'] == 'line1'

    def test_for_4(self):
        assert _bin_reader(*self._data['for'])[
            'lines'][4]['content'] == 'last'

    def test_do_while_1(self):
        assert len(_bin_reader(*self._data['do_while'])['lines']) == 5

    def test_do_while_2(self):
        assert _bin_reader(*self._data['do_while'])['lines'][0]['id'] == 0x01

    def test_do_while_3(self):
        assert _bin_reader(*self._data['do_while'])['lines'][4]['id'] == 0x02

    def test_while_1(self):
        assert len(_bin_reader(*self._data['while'])['lines']) == 5

    def test_while_2(self):
        assert _bin_reader(*self._data['while'])['lines'][4]['id'] == 0x01

    def test_while_3(self):
        assert _bin_reader(*self._data['while'])['lines_term'] == 0x02

    def test_if_1(self):
        assert 'related_to_b' not in _bin_reader(*self._data['if_a'])

    def test_if_2(self):
        assert (
            _bin_reader(*self._data['if_a'])['related_to_a'] == 'not skipped')

    def test_if_3(self):
        assert 'related_to_a' not in _bin_reader(*self._data['if_b'])

    def test_if_4(self):
        assert (
            _bin_reader(*self._data['if_b'])['related_to_b'] == 'not skipped')

    def test_var_size(self):
        assert _bin_reader(*self._data['var_size'])['field_2_size'] == 4

    def test_padding_1(self):
        assert _bin_reader(*self._data['padding'])['string_1'] == '123'

    def test_padding_2(self):
        assert _bin_reader(*self._data['padding'])['string_2'] == '456789'

    def test_padding_3(self):
        assert _bin_reader(*self._data['padding'])['string_3'] == ''

    def test_order_1(self):
        assert _bin_reader(*self._data['order'])['val_1'] == 0x010200

    def test_order_2(self):
        assert _bin_reader(*self._data['order'])['val_2'] == 0x010200

    def test_colour_1(self):
        assert _bin_reader(*self._data['colour'])['background']['g'] == 128

    def test_colour_2(self):
        assert _bin_reader(*self._data['colour'])['background']['b'] == 'full'

    def test_complex_eval_1(self):
        assert 'item_1' not in _bin_reader(*self._data['complex_eval'])

    def test_complex_eval_2(self):
        assert _bin_reader(*self._data['complex_eval'])['item_2'] == 'A'

    def test_flags_1(self):
        assert not _bin_reader(*self._data['flags'])['flags']['bit_one']

    def test_flags_2(self):
        assert _bin_reader(*self._data['flags'])['flags']['bit_two']

    def test_flags_3(self):
        assert _bin_reader(*self._data['flags'])['flags']['flag_04']

    def test_map_1(self):
        assert _bin_reader(
            *self._data['map'])['number'] == 'two hunderd and fifty-eight'

    def test_map_2(self):
        assert _bin_reader(*self._data['map'])['choice'] == 1

    def test_size_string_1(self):
        assert _bin_reader(
            *self._data['size_string'])['string_1']['size_of_string'] == 28

    def test_size_string_2(self):
        assert len(_bin_reader(
            *self._data['size_string'])['string_1']['string']) == 28

    def test_size_string_3(self):
        assert _bin_reader(
            *self._data['size_string'])['string_2']['size_of_string'] == 23

    def test_size_string_4(self):
        assert len(_bin_reader(
            *self._data['size_string'])['string_2']['string']) == 23

    def test_var_type_1(self):
        assert _bin_reader(
            *self._data['var_type'])['value_1']['content'] == 'A'

    def test_var_type_2(self):
        assert _bin_reader(
            *self._data['var_type'])['value_1']['type_name'] == 'char'

    def test_var_type_3(self):
        assert _bin_reader(
            *self._data['var_type'])['value_2']['content'] == 123

    def test_var_type_2(self):
        assert _bin_reader(
            *self._data['var_type'])['value_2']['type_name'] == 'le_s_short'
