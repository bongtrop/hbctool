from util import *
import json
import os
import shutil

def dump(hbc, path):
    if os.path.exists(path):
        c = input(f"'{path}' exists. Do you want to remove it ? (y/n): ").strip()
        if c == "y":
            shutil.rmtree(path)
        else:
            exit(1337)

    os.makedirs(path)
    # Write all obj to metadata.json
    f = open(f"{path}/metadata.json", "w")
    json.dump(hbc.getObj(), f)
    f.close()
    
    stringCount = hbc.getStringCount()
    functionCount = hbc.getFunctionCount()

    ss = []
    for i in range(stringCount):
        val, header = hbc.getString(i)
        ss.append({
            "id": i,
            "value": val
        })
    
    f = open(f"{path}/string.json", "w")
    json.dump(ss, f, indent=4)
    f.close()

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
                    f.write(f"\t; Oper[{ii}]: String({val}) {repr(s)}\n")

                f.write("\n")

        f.write("EndFunction\n\n")
    f.close()