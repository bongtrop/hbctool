import unittest
from hbctool.util import *
from hbctool.hbc.hbc76.test import *
from hbctool.hbc.hbc74.test import *
from hbctool.hbc.hbc62.test import *
from hbctool.hbc.hbc59.test import *
from hbctool import hbc as hbcl, hasm
import pathlib
import json

basepath = pathlib.Path(__file__).parent.absolute()

class ByteIO:
    def __init__(self, v=b""):
        self.buf = v

    def write(self, b):
        self.buf += b

    def read(self, n=-1):
        if n==-1:
            o = self.buf
            self.buf = b""
            return o

        o = self.buf[:n]
        self.buf = self.buf[n:]
        return o

class TestFileUtilization(unittest.TestCase):
    def test_bit_writer(self):
        io = ByteIO()
        fw = BitWriter(io)

        offset = 182856
        paramCount = 1
        bytecodeSizeInBytes = 12342
        functionName = 3086

        write(fw, offset, ["bit", 25, 1])
        write(fw, paramCount, ["bit", 7, 1])
        write(fw, bytecodeSizeInBytes, ["bit", 15, 1])
        write(fw, functionName, ["bit", 17, 1])

        bs = io.read()
        self.assertEqual("48ca020236300706", bs.hex())

        isUTF16 = 0
        offset = 465
        length = 3

        write(fw, isUTF16, ["bit", 1, 1])
        write(fw, offset, ["bit", 23, 1])
        write(fw, length, ["bit", 8, 1])

        bs = io.read()
        self.assertEqual("a2030003", bs.hex())

    def test_bit_reader(self):
        io = ByteIO()
        fr = BitReader(io)

        io.write(bytes.fromhex("48ca020236300706"))

        offset = read(fr, ["bit", 25, 1])
        paramCount = read(fr, ["bit", 7, 1])
        bytecodeSizeInBytes = read(fr, ["bit", 15, 1])
        functionName = read(fr, ["bit", 17, 1])

        self.assertEqual(offset, 182856)
        self.assertEqual(paramCount, 1)
        self.assertEqual(bytecodeSizeInBytes, 12342)
        self.assertEqual(functionName, 3086)

        io.write(bytes.fromhex("a2030003"))

        isUTF16 = read(fr, ["bit", 1, 1])
        offset = read(fr, ["bit", 23, 1])
        length = read(fr, ["bit", 8, 1])

        self.assertEqual(isUTF16, 0)
        self.assertEqual(offset, 465)
        self.assertEqual(length, 3)

    def test_conversion(self):

        io = ByteIO()
        fr = BitReader(io)
        fw = BitWriter(io)

        isUTF16 = 1
        offset = 465
        length = 3

        write(fw, isUTF16, ["bit", 1, 1])
        write(fw, offset, ["bit", 23, 1])
        write(fw, length, ["bit", 8, 1])

        isUTF16 = read(fr, ["bit", 1, 1])
        offset = read(fr, ["bit", 23, 1])
        length = read(fr, ["bit", 8, 1])

        self.assertEqual(isUTF16, 1)
        self.assertEqual(offset, 465)
        self.assertEqual(length, 3)

def main():
    unittest.main()

if __name__ == "__main__":
    main()
