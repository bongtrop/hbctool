from hbctool import hbc as hbcl
from .parser import (
    _pack_bits, _unpack_bits, _SFH_W1, _SFH_W2, _SSTE,
)
import io
import os
import unittest
import pathlib

basepath = pathlib.Path(__file__).parent.absolute()


class TestHBC98Bitfields(unittest.TestCase):
    """The v98 small headers pack three or more sub-fields into one 32-bit word.
    These are serialized by splitting/combining whole integers (see parser.py),
    so verify the pack/unpack helpers are exact inverses."""

    def test_small_func_header_word1(self):
        for vals in ([11728124, 1, 0], [33554431, 31, 3], [0, 0, 0], [1, 1, 1]):
            d = dict(zip([n for n, _ in _SFH_W1], vals))
            word = _pack_bits(d, _SFH_W1)
            self.assertLess(word, 1 << 32)
            self.assertEqual(_unpack_bits(word, _SFH_W1), d)

    def test_small_func_header_word2(self):
        for vals in ([9, 158, 0, 0], [16383, 255, 31, 31], [471, 86, 3, 7]):
            d = dict(zip([n for n, _ in _SFH_W2], vals))
            word = _pack_bits(d, _SFH_W2)
            self.assertLess(word, 1 << 32)
            self.assertEqual(_unpack_bits(word, _SFH_W2), d)

    def test_small_string_table_entry(self):
        for vals in ([1, 123456, 7], [0, 0, 0], [1, (1 << 23) - 1, 255]):
            d = dict(zip([n for n, _ in _SSTE], vals))
            word = _pack_bits(d, _SSTE)
            self.assertLess(word, 1 << 32)
            self.assertEqual(_unpack_bits(word, _SSTE), d)

    def test_overflow_offset_encoding(self):
        # Large header offset is encoded as (functionName << 24) | offset.
        for large in (0, 0xFF, 0x123456, 0xFFFFFF, 0x7FFFFFF, 20449490):
            offset = large & 0xFFFFFF
            functionName = (large >> 24) & 0xFF
            self.assertEqual((functionName << 24) | offset, large)


class TestHBC98RoundTrip(unittest.TestCase):
    """Full byte-for-byte round-trip, only if a v98 sample is present."""

    def test_roundtrip(self):
        sample = f"{basepath}/example/index.android.bundle"
        if not os.path.exists(sample):
            self.skipTest("no v98 example bundle present")
        orig = open(sample, "rb").read()
        h = hbcl.load(io.BytesIO(orig))
        self.assertEqual(h.getVersion(), 98)
        out = io.BytesIO()
        hbcl.dump(h, out)
        self.assertEqual(orig, out.getvalue())


if __name__ == "__main__":
    unittest.main()
