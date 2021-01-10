from util import *
import json
import os

def dump(hbc, path):
    assert not os.path.exists(path), f"'{path}' exists."
    os.makedirs(path)
    # Write all obj to metadata.json
    json.dump(hbc.getObj(), open(f"{path}/metadata.json", "w"))
    
    stringCount = hbc.getStringCount()
    functionCount = hbc.getFunctionCount()

    f = open(f"{path}/instruction.hasm", "w")
    for i in range(functionCount):
        functionName, paramCount, registerCount, symbolCount, insts, _ = hbc.getFunction(i)
        # Function<>1270(2 params, 1 registers, 0 symbols):
        f.write(f"Function<{functionName}>{i}({paramCount} params, {registerCount} registers, {symbolCount} symbols):\n")
        for opcode, operands in insts:
            f.write(f"\t{opcode.ljust(20,' ')}\t")
            o = []
            ss = []
            for ii, v in enumerate(operands):
                t, is_str, val = v
                o.append(f"{t}:{val}")

                if is_str:
                    s, _ = hbc.getString(val)
                    ss.append((ii, val, s))
                    
            
            f.write(f"{', '.join(o)}\n")
            if len(ss) > 0:
                for ii, val, s in ss:
                    f.write(f"\t; Oper[{ii}]: String({val}) {s}\n")

                f.write("\n")

        f.write("EndFunction\n\n")
    f.close()