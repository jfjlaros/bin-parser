"""
Tests for the bin_parser.functions module.
"""


from bin_parser import functions


class TestParser(object):
    """
    Test the python.fam_parser module.
    """
    def setup(self):
        self.bpf = functions.BinParseFunctions()
        self.string = '012'
        self.byte = '0'
        self.annotation = {int(self.bpf.date(self.string, {})): 'hello'}

    def test_raw(self):
        assert self.string == self.bpf.raw_inv(self.bpf.raw(self.string))

    def test_bit(self):
        assert self.byte == self.bpf.bit_inv(self.bpf.bit(self.byte))

    def test_int(self):
        assert self.string == self.bpf.int_inv(self.bpf.int(self.string))

    def test_colour(self):
        assert self.string == self.bpf.colour_inv(self.bpf.colour(self.string))

    def test_date_1(self):
        assert self.string == self.bpf.date_inv(
            self.bpf.date(self.string, {}), {})

    def test_date_2(self):
        assert self.bpf.date(self.string, self.annotation) == 'hello'

    def test_date_3(self):
        assert self.string == self.bpf.date_inv(
            self.bpf.date(self.string, self.annotation), self.annotation)
