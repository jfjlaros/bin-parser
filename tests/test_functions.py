"""
Tests for the bin_parser.functions module.
"""


from bin_parser import functions


class TestParser(object):
    """
    Test the python.fam_parser module.
    """
    def setup(self):
        self.bpf = functions.BinReadFunctions()
        self.bpfi = functions.BinWriteFunctions()
        self.string = '012'
        self.byte = '0'
        self.annotation = 'xxxx'
        self.date_annotation = {3289392: self.annotation}
        self.map_annotation = {48: self.annotation}
        self.flags_annotation = {0x10: self.annotation, 0x01: 'unused'}
        self.flags_name = 'yy'

    def test_raw(self):
        assert self.string == self.bpfi.raw(self.bpf.raw(self.string))

    def test_bit(self):
        assert self.byte == self.bpfi.bit(self.bpf.bit(self.byte))

    def test_int_1(self):
        assert self.string == self.bpfi.int(self.bpf.int(self.string))

    def test_int_2(self):
        assert self.bpfi.int(0) == chr(0x00)

    def test_colour(self):
        assert self.string == self.bpfi.colour(self.bpf.colour(self.string))

    def test_date_1(self):
        assert self.string == self.bpfi.date(
            self.bpf.date(self.string, {}), {})

    def test_date_2(self):
        assert self.bpf.date(
            self.string, self.date_annotation) == self.annotation

    def test_date_3(self):
        assert self.string == self.bpfi.date(
            self.bpf.date(self.string, self.date_annotation),
            self.date_annotation)

    def test_map_1(self):
        assert self.byte == self.bpfi.map(self.bpf.map(self.byte, {}), {})

    def test_map_2(self):
        assert self.bpf.map(
            self.byte, self.map_annotation) == self.annotation

    def test_map_3(self):
        assert self.byte == self.bpfi.map(
            self.bpf.map(self.byte, self.map_annotation), self.map_annotation)

    def test_flags_1(self):
        assert self.byte == self.bpfi.flags(
            self.bpf.flags(self.byte, self.flags_name, {}),
            self.flags_name, {})

    def test_flags_2(self):
        assert (self.bpf.flags(
            self.byte, self.flags_name, self.flags_annotation) ==
            {'flags_yy_20': True, 'unused': False, 'xxxx': True})

    def test_flags_3(self):
        assert self.bpfi.flags(self.bpf.flags(
            self.byte, self.flags_name, self.flags_annotation),
            self.flags_name, self.flags_annotation) == self.byte
