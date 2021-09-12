
from hbctool.util import *
from hbctool.hbc.hbc76 import HBC76
from hbctool.hbc.hbc74 import HBC74
from hbctool.hbc.hbc59 import HBC59
import json

MAGIC = 2240826417119764422
INIT_HEADER = {
    "magic": ["uint", 64, 1],
    "version": ["uint", 32, 1]
}
BYTECODE_ALIGNMENT = 4

HBC = {
    76: HBC76,
    74: HBC74,
    59: HBC59
}

def load(f):
    f = BitReader(f)
    magic = read(f, INIT_HEADER["magic"])
    version = read(f, INIT_HEADER["version"])
    f.seek(0)
    assert magic == MAGIC, f"The magic ({hex(magic)}) is invalid. (must be {hex(MAGIC)})"
    assert version in HBC, f"The HBC version ({version}) is not supported."

    return HBC[version](f)

def loado(obj):
    magic = obj["header"]["magic"]
    version = obj["header"]["version"]

    assert magic == MAGIC, f"The magic ({hex(magic)}) is invalid. (must be {hex(MAGIC)})"
    assert version in HBC, f"The HBC version ({version}) is not supported."

    hbc = HBC[version]()
    hbc.setObj(obj)
    return hbc

def dump(hbc, f):
    f = BitWriter(f)
    hbc.export(f)

def dumpo(hbc):
    return hbc.getObj()