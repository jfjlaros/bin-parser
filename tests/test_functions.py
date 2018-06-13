"""Tests for the bin_parser.functions module."""
from bin_parser import functions


class TestParser(object):
    """Test the bin_parser.functions module."""
    def setup(self):
        self._brf = functions.BinReadFunctions()
        self._bwf = functions.BinWriteFunctions()

    def _idem(self, func, data, **kwargs):
        """General idempotency test.

        This test decodes `data`, encodes the result and checks whether this
        equals `data`.

        :arg function func: Function to be tested.
        :arg any data: Data for `func`.
        :arg dict **kwargs: Arguments for `func`.
        """
        assert getattr(self._bwf, func)(
            getattr(self._brf, func)(data, **kwargs), **kwargs) == data

    def test_raw_single(self):
        assert self._brf.raw(b'\x03') == '03'

    def test_raw_multi(self):
        assert self._brf.raw(b'\x00\x01\x02') == '00 01 02'

    def test_raw_idem(self):
        self._idem('raw', b'\x00\x01\x02')

    def test_bit(self):
        assert self._brf.bit(b'\x03') == '00000011'

    def test_bit_idem(self):
        self._idem('bit', b'\x03')

    def test_le_s_short(self):
        assert self._brf.struct(b'\x01\x00', fmt='<h') == 1

    def test_be_s_short(self):
        assert self._brf.struct(b'\x00\x01', fmt='>h') == 1

    def test_le_s_short_idem(self):
        self._idem('struct', b'\x01\x02', fmt='<h')

    def test_be_s_float_idem(self):
        self._idem('struct', b'\x01\x02\x03\x04', fmt='>f')

    def test_labels(self):
        assert self._brf.struct(
            b'\x01\x02', fmt='BB', labels=['a', 'b']) == {'a': 1, 'b': 2}

    def test_labels_idem(self):
        self._idem('struct', b'\x01\x02', fmt='BB', labels=['a', 'b'])

    def test_annotation(self):
        assert self._brf.struct(
            b'\x01\x02', fmt='BB', annotation={1: 'x'}) == ['x', 2]

    def test_annotation_idem(self):
        self._idem('struct', b'\x01\x02', fmt='BB', annotation={1: 'a'})

    def test_labels_annotation(self):
        assert self._brf.struct(
            b'\x01\x02', fmt='BB', labels=['a', 'b'],
            annotation={1: 'x'}) == {'a': 'x', 'b': 2}

    def test_labels_annotation_idem(self):
        self._idem(
            'struct', b'\x01\x02', fmt='BB', labels=['a', 'b'],
            annotation={1: 'x'})

    def test_flags(self):
        assert self._brf.flags(b'\x03', {}) == {
            'flag_01': True, 'flag_02': True}

    def test_flags_false(self):
        assert self._bwf.flags(
            {'flag_01': True, 'flag_02': False}, {}) == b'\x01'

    def test_flags_idem(self):
        self._idem('flags', b'\x03', annotation={})

    def test_flags_annotation(self):
        assert self._brf.flags(b'\x03', {2: 'a'}) == {
            'flag_01': True, 'a': True}

    def test_flags_annotation_false(self):
        assert self._brf.flags(b'\x01', {2: 'a'}) == {
            'flag_01': True, 'a': False}

    def test_flags_annotation_idem(self):
        self._idem('flags', b'\x03', annotation={2: 'a'})
