import pytest
from hbctool.hbc import HBC


def test_v90_registered():
    assert 90 in HBC


def test_v94_registered():
    assert 94 in HBC


def test_v96_registered():
    assert 96 in HBC


def test_all_versions():
    expected = [59, 62, 74, 76, 84, 85, 90, 94, 96]
    for v in expected:
        assert v in HBC, f"Version {v} missing!"


def test_v90_class_instantiates():
    hbc = HBC[90]()
    assert hbc.getVersion() == 90


def test_v94_class_instantiates():
    hbc = HBC[94]()
    assert hbc.getVersion() == 94


def test_v96_class_instantiates():
    hbc = HBC[96]()
    assert hbc.getVersion() == 96


def test_v90_opcode_bigint():
    import json
    import pathlib
    path = pathlib.Path(__file__).parent / "hbctool" / "hbc" / "hbc90" / "data" / "opcode.json"
    opcodes = json.loads(path.read_text())
    opcode_list = list(opcodes.keys())
    assert "LoadConstBigInt" in opcodes
    assert "LoadConstBigIntLongIndex" in opcodes
    assert opcodes["LoadConstBigInt"] == ["Reg8", "UInt16:B"]
    assert opcodes["LoadConstBigIntLongIndex"] == ["Reg8", "UInt32:B"]
    idx_double = opcode_list.index("LoadConstDouble")
    idx_bigint = opcode_list.index("LoadConstBigInt")
    idx_bigint_long = opcode_list.index("LoadConstBigIntLongIndex")
    idx_string = opcode_list.index("LoadConstString")
    assert idx_bigint == idx_double + 1, "LoadConstBigInt must follow LoadConstDouble"
    assert idx_bigint_long == idx_double + 2, "LoadConstBigIntLongIndex must be 2 after LoadConstDouble"
    assert idx_string == idx_double + 3, "LoadConstString must be 3 after LoadConstDouble"


def test_v90_structure_header_fields():
    import json
    import pathlib
    path = pathlib.Path(__file__).parent / "hbctool" / "hbc" / "hbc90" / "data" / "structure.json"
    structure = json.loads(path.read_text())
    header = structure["header"]
    assert "bigIntCount" in header
    assert "bigIntStorageSize" in header
    assert "segmentID" in header
    assert "functionSourceCount" in header
    assert "cjsModuleOffset" not in header
    assert header["padding"] == ["uint", 8, 19]


def test_v85_structure_unchanged():
    import json
    import pathlib
    path = pathlib.Path(__file__).parent / "hbctool" / "hbc" / "hbc85" / "data" / "structure.json"
    structure = json.loads(path.read_text())
    header = structure["header"]
    assert "cjsModuleOffset" in header
    assert "bigIntCount" not in header
    assert header["padding"] == ["uint", 8, 31]


def test_v96_structure_same_as_v94():
    import json
    import pathlib
    base = pathlib.Path(__file__).parent / "hbctool" / "hbc"
    s94 = json.loads((base / "hbc94" / "data" / "structure.json").read_text())
    s96 = json.loads((base / "hbc96" / "data" / "structure.json").read_text())
    assert s94 == s96


def test_existing_versions_still_registered():
    for v in [59, 62, 74, 76, 84, 85]:
        assert v in HBC, f"Existing version {v} was accidentally removed!"
