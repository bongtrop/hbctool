
from util import *
from hbc.hbc74 import HBC74
import json

MAGIC = 2240826417119764422
INIT_HEADER = {
    "magic": ["uint", 64, 1],
    "version": ["uint", 32, 1]
}
BYTECODE_ALIGNMENT = 4

HBC = {
    74: HBC74
}

def parseFromFile(f):
    f = BitReader(f)
    magic = read(f, INIT_HEADER["magic"])
    version = read(f, INIT_HEADER["version"])
    f.seek(0)
    assert magic == MAGIC, f"The magic ({hex(magic)}) is invalid. (must be {hex(MAGIC)})"
    assert version in HBC, f"The HBC version ({version}) is not supported."

    return HBC[version](f)

