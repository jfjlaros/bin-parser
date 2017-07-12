"""
Tests for the bin_parser.bin_parser module.
"""
import yaml

from bin_parser import BinReader, BinWriter


def _bin_reader(path, input_file, structure_file, types_file):
    return BinReader(
        open('examples/{}/{}'.format(path, input_file)).read(),
        yaml.safe_load(open('examples/{}/{}'.format(path, structure_file))),
        yaml.safe_load(open('examples/{}/{}'.format(path, types_file)))).parsed


def _idempotence(path, input_file, structure_file, types_file):
    data = open('examples/{}/{}'.format(path, input_file)).read()

    parsed = BinReader(
        data,
        yaml.safe_load(open('examples/{}/{}'.format(path, structure_file))),
        yaml.safe_load(open('examples/{}/{}'.format(path, types_file)))).parsed

    assert data == BinWriter(
        parsed,
        yaml.safe_load(open('examples/{}/{}'.format(path, structure_file))),
        yaml.safe_load(open('examples/{}/{}'.format(path, types_file)))).data


class TestReader(object):
    """
    Test the python.fam_parser module.
    """
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
            'order': ['order', 'order.dat', 'structure.yml', 'types.yml']}

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
