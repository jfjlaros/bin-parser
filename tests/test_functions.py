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
        self.annotation = 'xxxx'
        self.date_annotation = {
            int(self.bpf.date(self.string, {})): self.annotation}
        self.map_annotation = {
            int(self.bpf.map(self.byte, {}), 0x10): self.annotation}

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
        assert (self.bpf.date(self.string, self.date_annotation) ==
            self.annotation)

    def test_date_3(self):
        assert self.string == self.bpf.date_inv(
            self.bpf.date(self.string, self.date_annotation),
            self.date_annotation)

    def test_map_1(self):
        assert self.byte == self.bpf.map_inv(self.bpf.map(self.byte, {}), {})

    def test_map_2(self):
        assert (self.bpf.map(self.byte, self.map_annotation) ==
            self.annotation)

    def test_map_3(self):
        assert self.byte == self.bpf.map_inv(
            self.bpf.map(self.byte, self.map_annotation), self.map_annotation)
