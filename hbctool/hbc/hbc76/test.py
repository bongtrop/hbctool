from hbctool import hbc as hbcl, hasm
from .translator import assemble, disassemble
import unittest
import re
import pathlib
import json

basepath = pathlib.Path(__file__).parent.absolute()
class TestHBC76(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestHBC76, self).__init__(*args, **kwargs)
        self.hbc = hbcl.load(open(f"{basepath}/example/index.android.bundle", "rb"))
        self.objdump = open(f"{basepath}/example/objdump.out", "r").read()
        self.pretty = open(f"{basepath}/example/pretty.out", "r").read()
        self.raw = open(f"{basepath}/example/raw.out", "r").read()

    def test_get_function(self):
        target_offsets = re.findall(r"([0-9a-f]+) \<_[0-9]+\>", self.objdump)
        target_args = re.findall(r"Function<(.*?)>([0-9]+)\(([0-9]+) params, ([0-9]+) registers,\s?([0-9]+) symbols\):", self.pretty)
        functionCount = self.hbc.getFunctionCount()

        self.assertEqual(functionCount, len(target_offsets))
        self.assertEqual(functionCount, len(target_args))

        for i in range(functionCount):
            target_offset = target_offsets[i]
            target_functionName, _, target_paramCount, target_registerCount, target_symbolCount = target_args[i]
            try:
                functionName, paramCount, registerCount, symbolCount, _, funcHeader = self.hbc.getFunction(i)
            except AssertionError:
                self.fail()

            self.assertEqual(functionName, target_functionName)
            self.assertEqual(paramCount, int(target_paramCount))
            self.assertEqual(registerCount, int(target_registerCount))
            self.assertEqual(symbolCount, int(target_symbolCount))
            self.assertEqual(funcHeader["offset"], int(target_offset, 16))
    
    def test_get_string(self):
        target_strings = re.findall(r"[is][0-9]+\[([UTFASCI16-]+), ([0-9]+)..([0-9-]+)\].*?:\s?(.*)", self.pretty)
        stringCount = self.hbc.getStringCount()

        self.assertEqual(stringCount, len(target_strings))

        for i in range(stringCount):
            val, header = self.hbc.getString(i)
            isUTF16, offset, length = header

            t, target_start, target_end, target_val = target_strings[i]

            target_isUTF16 = t == "UTF-16"
            target_offset = int(target_start)
            target_length = int(target_end) - target_offset + 1

            self.assertEqual(isUTF16, target_isUTF16)
            self.assertEqual(offset, target_offset)
            self.assertEqual(length, target_length)

            # TODO : Implement this please
            # self.assertEqual(val, target_val)

    def test_translator(self):
        functionCount = self.hbc.getFunctionCount()

        for i in range(functionCount):
            _, _, _, _, bc, _ = self.hbc.getFunction(i, disasm=False)

            self.assertEqual(assemble(disassemble(bc)), bc)
class TestParser76(unittest.TestCase):
    def test_hbc(self):
        f = open(f"{basepath}/example/index.android.bundle", "rb")
        hbc = hbcl.load(f)
        f.close()
        f = open("/tmp/hbctool_test.android.bundle", "wb")
        hbcl.dump(hbc, f)
        f.close()

        f = open("hbc/hbc76/example/index.android.bundle", "rb")
        a = f.read()
        f.close()
        f = open("/tmp/hbctool_test.android.bundle", "rb")
        b = f.read()
        f.close()

        self.assertEqual(a, b)

    def test_hasm(self):
        f = open(f"{basepath}/example/index.android.bundle", "rb")
        a = hbcl.load(f)
        f.close()
        hasm.dump(a, "/tmp/hbctool_test", force=True)
        b = hasm.load("/tmp/hbctool_test")

        self.assertEqual(json.dumps(a.getObj()), json.dumps(b.getObj()))
