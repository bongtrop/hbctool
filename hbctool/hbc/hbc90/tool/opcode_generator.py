"""
Generate data/opcode.json from raw/BytecodeList.def (upstream Hermes).

Run from this directory:
  python3 opcode_generator.py
"""
import pathlib
import re
import json

basepath = pathlib.Path(__file__).parent.absolute()

bytecodeListFile = open(f"{basepath}/../raw/BytecodeList.def", "r", encoding="utf-8", errors="replace")
lines = bytecodeListFile.readlines()
bytecodeListFile.close()

jmp_operand = {
    "1": ["Addr8"],
    "1Long": ["Addr32"],
    "2": ["Addr8", "Reg8"],
    "2Long": ["Addr32", "Reg8"],
    "3": ["Addr8", "Reg8", "Reg8"],
    "3Long": ["Addr32", "Reg8", "Reg8"]
}

json_op = {}
opcode = 0
# React Native / production Hermes builds define HERMES_RUN_WASM; bundles use
# those opcodes (e.g. Add32 … Store32). Include them so disasm matches real apps.
INCLUDE_HERMES_RUN_WASM = True
in_wasm = False
wasm_depth = 0


def addOp(name, operands):
    global opcode, json_op
    print(f"{opcode:3d} 0x{opcode:02x}  {name}")
    json_op[name] = operands
    opcode = opcode + 1


for line_num, line in enumerate(lines, 1):
    s = line.strip()
    if "#ifdef HERMES_RUN_WASM" in line:
        in_wasm = True
        wasm_depth += 1
        if not INCLUDE_HERMES_RUN_WASM:
            continue
        continue
    if in_wasm and not INCLUDE_HERMES_RUN_WASM:
        if s == "#endif" or line.startswith("#endif"):
            in_wasm = False
        continue
    if in_wasm and INCLUDE_HERMES_RUN_WASM:
        if s == "#endif" or (line.startswith("#endif") and "WASM" not in line):
            in_wasm = False
            wasm_depth = 0
            continue

    if line.startswith("DEFINE_OPCODE_"):
        match = re.search(r"\((\w+)((?:, \w+)*)\)", line)
        if not match:
            print(f"WARN line {line_num}: no match: {line!r}")
            continue
        name = match.group(1)
        rest = match.group(2)
        operands = [x.strip() for x in rest.split(",") if x.strip()] if rest else []
        addOp(name, operands)

    elif line.startswith("OPERAND_STRING_ID"):
        match = re.search(r"\((\w+), (\w+)\)", line)
        name = match.group(1)
        operandID = int(match.group(2)) - 1
        assert name in json_op, f"Opcode not found ({name}) line {line_num}"
        assert json_op[name][operandID] is not None, f"Operand {operandID} line {line_num}"
        json_op[name][operandID] += ":S"

    elif line.startswith("OPERAND_BIGINT_ID"):
        match = re.search(r"\((\w+), (\w+)\)", line)
        name = match.group(1)
        operandID = int(match.group(2)) - 1
        assert name in json_op, f"Opcode not found ({name})"
        json_op[name][operandID] += ":B"

    elif line.startswith("OPERAND_FUNCTION_ID"):
        match = re.search(r"\((\w+), (\w+)\)", line)
        name = match.group(1)
        operandID = int(match.group(2)) - 1
        assert name in json_op, f"Opcode not found ({name})"
        json_op[name][operandID] += ":F"

    elif line.startswith("DEFINE_JUMP_"):
        match = re.search(r"(\d)\((\w+)\)", line)
        num_op = match.group(1)
        name = match.group(2)
        addOp(name, jmp_operand[f"{num_op}"])
        addOp(f"{name}Long", jmp_operand[f"{num_op}Long"])

    elif line.startswith("ASSERT_"):
        pass
    elif line.startswith("DEFINE_RET_TARGET"):
        pass
    elif line.startswith("DEFINE_OPERAND_TYPE"):
        pass
    elif s.startswith("#") or s.startswith("//") or s.startswith("/*") or s.startswith("*"):
        pass
    elif s == "" or s.startswith("#undef") or s.startswith("LLVM_"):
        pass
    elif line_num <= 65:
        pass
    else:
        if line.strip():
            pass  # e.g. blank or unknown — ignore

out_path = f"{basepath}/../data/opcode.json"
f = open(out_path, "w", encoding="utf-8")
json.dump(json_op, f, indent=4)
f.close()
print(f"Wrote {out_path} ({len(json_op)} opcodes)")
