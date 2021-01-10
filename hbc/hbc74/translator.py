import pathlib
import json
from util import *

basepath = pathlib.Path(__file__).parent.absolute()

operand_type = {
    "Reg8": (1, to_uint8, from_uint8),
    "Reg32": (4, to_uint32, from_uint32),
    "UInt8": (1, to_uint8, from_uint8),
    "UInt16": (2, to_uint16, from_uint16),
    "UInt32": (4, to_uint32, from_uint16),
    "Addr8": (1, to_int8, from_int8),
    "Addr32": (4, to_int32, from_int32),
    "Reg32": (4, to_uint32, from_uint32),
    "Imm32": (4, to_uint32, from_uint32),
    "Double": (8, to_double, from_double)
}

def disassemble(inst):
    f = open(f"{basepath}/data/opcode.json", "r")
    opcode_operand = json.load(f)
    f.close()
    opcode_mapper = list(opcode_operand.keys())
    i = 0
    rs = []
    while i < len(inst):
        opcode = opcode_mapper[inst[i]]
        i+=1
        r = (opcode, [])
        operand_ts = opcode_operand[opcode]
        for oper_t in operand_ts:
            is_str = oper_t.endswith(":S")
            if is_str:
                oper_t = oper_t[:-2]
                
            size, conv_to, _ = operand_type[oper_t]
            val = conv_to(inst[i:i+size])
            r[1].append((oper_t, is_str, val))
            i+=size
        
        rs.append(r)
        
    return rs

def assemble(inst):
    pass