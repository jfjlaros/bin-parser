"""
Tests for the bin_parser.bin_parser module.
"""
import yaml

from bin_parser import BinReader


class TestReader(object):
    """
    Test the python.fam_parser module.
    """
    def setup(self):
        self.balance = BinReader(open('examples/balance/balance.dat').read(),
            yaml.safe_load(open('examples/balance/structure.yml')),
            yaml.safe_load(open('examples/balance/types.yml'))).parsed
        self.for_ = BinReader(open('examples/lists/for.dat').read(),
            yaml.safe_load(open('examples/lists/structure_for.yml')),
            yaml.safe_load(open('examples/lists/types.yml'))).parsed
        self.do_while = BinReader(open('examples/lists/do_while.dat').read(),
            yaml.safe_load(open('examples/lists/structure_do_while.yml')),
            yaml.safe_load(open('examples/lists/types.yml'))).parsed
        self.while_ = BinReader(open('examples/lists/while.dat').read(),
            yaml.safe_load(open('examples/lists/structure_while.yml')),
            yaml.safe_load(open('examples/lists/types.yml'))).parsed
        self.if_a = BinReader(open('examples/conditional/a.dat').read(),
            yaml.safe_load(open('examples/conditional/structure.yml')),
            yaml.safe_load(open('examples/conditional/types.yml'))).parsed
        self.if_b = BinReader(open('examples/conditional/b.dat').read(),
            yaml.safe_load(open('examples/conditional/structure.yml')),
            yaml.safe_load(open('examples/conditional/types.yml'))).parsed
        self.var_size = BinReader(
            open('examples/var_size/var_size.dat').read(),
            yaml.safe_load(open('examples/var_size/structure.yml')),
            yaml.safe_load(open('examples/var_size/types.yml'))).parsed
        self.padding = BinReader(
            open('examples/padding/padding.dat').read(),
            yaml.safe_load(open('examples/padding/structure.yml')),
            yaml.safe_load(open('examples/padding/types.yml'))).parsed

    def test_balance_1(self):
        assert self.balance['name'] == 'John Doe'

    def test_balance_2(self):
        assert self.balance['year_of_birth'] == 1999

    def test_balance_3(self):
        assert self.balance['balance'] == 3210

    def test_for_1(self):
        assert self.for_['size_of_list'] == 5

    def test_for_2(self):
        assert len(self.for_['lines']) == 5

    def test_for_3(self):
        assert self.for_['lines'][0]['content'] == 'line1'

    def test_for_4(self):
        assert self.for_['lines'][4]['content'] == 'last'

    def test_do_while_1(self):
        assert len(self.do_while['lines']) == 5

    def test_do_while_2(self):
        assert self.do_while['lines'][0]['id'] == 0x01

    def test_do_while_3(self):
        assert self.do_while['lines'][4]['id'] == 0x02

    def test_while_1(self):
        assert len(self.while_['lines']) == 5

    def test_while_2(self):
        assert self.while_['lines'][4]['id'] == 0x01

    def test_while_3(self):
        assert self.while_['lines_term'] == 0x02

    def test_if_1(self):
        assert 'related_to_b' not in self.if_a

    def test_if_2(self):
        assert self.if_a['related_to_a'] == 'not skipped'

    def test_if_3(self):
        assert 'related_to_a' not in self.if_b

    def test_if_4(self):
        assert self.if_b['related_to_b'] == 'not skipped'

    def test_var_size(self):
        assert self.var_size['field_2_size'] == 4

    def test_padding_1(self):
        assert self.padding['string_1'] == '123'

    def test_padding_2(self):
        assert self.padding['string_2'] == '456789'

    def test_padding_3(self):
        assert self.padding['string_3'] == ''
