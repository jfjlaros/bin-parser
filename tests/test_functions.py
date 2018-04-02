"""Tests for the bin_parser.functions module."""


from bin_parser import functions


class TestParser(object):
    """Test the bin_parser.functions module."""
    def setup(self):
        self.brf = functions.BinReadFunctions()
        self.bwf = functions.BinWriteFunctions()
        self.string = '012'
        self.byte = '0'
        self.annotation = 'xxxx'
        self.float = '\x42\xf6\xcc\xcd'
        self.date_annotation = {3289392: self.annotation}
        self.map_annotation = {48: self.annotation}
        self.flags_annotation = {0x10: self.annotation, 0x01: 'unused'}

    def test_raw(self):
        assert self.string == self.bwf.raw(self.brf.raw(self.string))

    def test_bit(self):
        assert self.byte == self.bwf.bit(self.brf.bit(self.byte))

    def test_int_1(self):
        assert self.string == self.bwf.int(self.brf.int(self.string))

    def test_int_2(self):
        assert self.bwf.int(0) == chr(0x00)

    def test_float(self):
        assert self.float == self.bwf.float(self.brf.float(self.float))

    def test_colour(self):
        assert self.string == self.bwf.colour(self.brf.colour(self.string))

    def test_date_1(self):
        assert self.string == self.bwf.date(
            self.brf.date(self.string, {}), {})

    def test_date_2(self):
        assert self.brf.date(
            self.string, self.date_annotation) == self.annotation

    def test_date_3(self):
        assert self.string == self.bwf.date(
            self.brf.date(self.string, self.date_annotation),
            self.date_annotation)

    def test_map_1(self):
        assert self.byte == self.bwf.map(self.brf.map(self.byte, {}), {})

    def test_map_2(self):
        assert self.brf.map(
            self.byte, self.map_annotation) == self.annotation

    def test_map_3(self):
        assert self.byte == self.bwf.map(
            self.brf.map(self.byte, self.map_annotation), self.map_annotation)

    def test_flags_1(self):
        assert self.byte == self.bwf.flags(self.brf.flags(self.byte, {}), {})

    def test_flags_2(self):
        assert (self.brf.flags(
            self.byte, self.flags_annotation) ==
            {'flag_20': True, 'unused': False, 'xxxx': True})

    def test_flags_3(self):
        assert self.bwf.flags(self.brf.flags(
            self.byte, self.flags_annotation),
            self.flags_annotation) == self.byte
