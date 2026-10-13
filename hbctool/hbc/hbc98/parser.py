from hbctool.util import *
import json
import pathlib
import copy

basepath = pathlib.Path(__file__).parent.absolute()

MAGIC = 2240826417119764422
BYTECODE_ALIGNMENT = 4

INVALID_OFFSET = (1 << 23)
INVALID_LENGTH = (1 << 8) - 1

# Bit in FunctionHeaderFlag indicating the small header only stores an offset to
# a large (overflowed) FunctionHeader.
# Layout: prohibitInvoke:2, strictMode:1, hasExceptionHandler:1, hasDebugInfo:1,
#         overflowed:1, kind:2  -> overflowed is bit 5.
OVERFLOWED_BIT = 5

structure = json.load(open(f"{basepath}/data/structure.json", "r"))

headerS = structure["header"]
functionHeaderS = structure["FuncHeader"]
overflowStringTableEntryS = structure["OverflowStringTableEntry"]
stringStorageS = structure["StringStorage"]
literalValueBufferS = structure["LiteralValueBuffer"]
objKeyBufferS = structure["ObjKeyBuffer"]
shapeTableEntryS = structure["ShapeTableEntry"]
bigIntTableEntryS = structure["BigIntTableEntry"]
bigIntStorageS = structure["BigIntStorage"]
regExpTableEntryS = structure["RegExpTableEntry"]
regExpStorageS = structure["RegExpStorage"]
cjsModuleTableS = structure["CJSModuleTable"]
functionSourceTableS = structure["FunctionSourceTable"]

# --- Bitfield helpers -------------------------------------------------------
# hbctool's generic BitReader/BitWriter mis-serializes words that pack three or
# more sub-fields (e.g. offset:25, paramCount:5, loopDepth:2). We therefore read
# and write those words as whole little-endian integers and split/combine the
# sub-fields here, which guarantees a byte-perfect round-trip.

# (name, bit width) in LSB-first order within each 32-bit word.
_SFH_W1 = [("offset", 25), ("paramCount", 5), ("loopDepth", 2)]
_SFH_W2 = [("bytecodeSizeInBytes", 14), ("functionName", 8),
           ("numberRegCount", 5), ("nonPtrRegCount", 5)]
# Third 32-bit word, laid out as individual bytes:
#   byte0: frameSize(8)  byte1: readCacheSize(8)
#   byte2: writeCacheSize(7) | privateNameCacheSize(1)  byte3: flags(8)
_SSTE = [("isUTF16", 1), ("offset", 23), ("length", 8)]

def _unpack_bits(word, fields):
    out = {}
    shift = 0
    for name, bits in fields:
        out[name] = (word >> shift) & ((1 << bits) - 1)
        shift += bits
    return out

def _pack_bits(d, fields):
    word = 0
    shift = 0
    for name, bits in fields:
        word |= (d[name] & ((1 << bits) - 1)) << shift
        shift += bits
    return word

def _read_small_func_header(f):
    w1 = readuint(f, bits=32)
    w2 = readuint(f, bits=32)
    frameSize = readuint(f, bits=8)
    readCacheSize = readuint(f, bits=8)
    b3 = readuint(f, bits=8)
    flags = readuint(f, bits=8)
    fh = {}
    fh.update(_unpack_bits(w1, _SFH_W1))
    fh.update(_unpack_bits(w2, _SFH_W2))
    fh["frameSize"] = frameSize
    fh["readCacheSize"] = readCacheSize
    fh["writeCacheSize"] = b3 & 0x7f
    fh["privateNameCacheSize"] = (b3 >> 7) & 1
    fh["flags"] = flags
    return fh

def _write_small_func_header(f, fh):
    writeuint(f, _pack_bits(fh, _SFH_W1), bits=32)
    writeuint(f, _pack_bits(fh, _SFH_W2), bits=32)
    writeuint(f, fh["frameSize"] & 0xff, bits=8)
    writeuint(f, fh["readCacheSize"] & 0xff, bits=8)
    writeuint(f, (fh["writeCacheSize"] & 0x7f) | ((fh["privateNameCacheSize"] & 1) << 7), bits=8)
    writeuint(f, fh["flags"] & 0xff, bits=8)

def _read_small_string_entry(f):
    word = readuint(f, bits=32)
    return _unpack_bits(word, _SSTE)

def _write_small_string_entry(f, e):
    writeuint(f, _pack_bits(e, _SSTE), bits=32)

def align(f):
    f.pad(BYTECODE_ALIGNMENT)

def _readEntries(f, count, entryS):
    entries = []
    for _ in range(count):
        entry = {}
        for key in entryS:
            entry[key] = read(f, entryS[key])
        entries.append(entry)
    return entries

def _writeEntries(f, entries, count, entryS):
    for i in range(count):
        entry = entries[i]
        for key in entryS:
            write(f, entry[key], entryS[key])

def parse(f):
    obj = {}

    # Segment 1: Header
    header = {}
    for key in headerS:
        header[key] = read(f, headerS[key])

    obj["header"] = header
    align(f)

    # Segment 2: Function Headers (SmallFuncHeader; overflow -> large FuncHeader)
    functionHeaders = []
    for i in range(header["functionCount"]):
        functionHeader = _read_small_func_header(f)

        if (functionHeader["flags"] >> OVERFLOWED_BIT) & 1:
            functionHeader["small"] = copy.deepcopy(functionHeader)
            saved_pos = f.tell()
            large_offset = (functionHeader["functionName"] << 24) | functionHeader["offset"]
            f.seek(large_offset)
            for key in functionHeaderS:
                functionHeader[key] = read(f, functionHeaderS[key])
            f.seek(saved_pos)

        functionHeaders.append(functionHeader)

    obj["functionHeaders"] = functionHeaders
    align(f)

    # Segment 3: StringKinds (run-length encoded; stored opaque)
    stringKinds = [readuint(f, bits=32) for _ in range(header["stringKindCount"])]
    obj["stringKinds"] = stringKinds
    align(f)

    # Segment 4: IdentifierHashes
    identifierHashes = [readuint(f, bits=32) for _ in range(header["identifierCount"])]
    obj["identifierHashes"] = identifierHashes
    align(f)

    # Segment 5: SmallStringTable
    obj["stringTableEntries"] = [_read_small_string_entry(f) for _ in range(header["stringCount"])]
    align(f)

    # Segment 6: OverflowStringTable
    obj["stringTableOverflowEntries"] = _readEntries(f, header["overflowStringCount"], overflowStringTableEntryS)
    align(f)

    # Segment 7: StringStorage
    stringStorageS[2] = header["stringStorageSize"]
    obj["stringStorage"] = read(f, stringStorageS)
    align(f)

    # Segment 8: LiteralValueBuffer (merged array + object value buffers)
    literalValueBufferS[2] = header["literalValueBufferSize"]
    obj["literalValueBuffer"] = read(f, literalValueBufferS)
    align(f)

    # Segment 9: ObjKeyBuffer
    objKeyBufferS[2] = header["objKeyBufferSize"]
    obj["objKeyBuffer"] = read(f, objKeyBufferS)
    align(f)

    # Segment 10: ObjShapeTable
    obj["objShapeTable"] = _readEntries(f, header["objShapeTableCount"], shapeTableEntryS)
    align(f)

    # Segment 11: BigIntTable
    obj["bigIntTable"] = _readEntries(f, header["bigIntCount"], bigIntTableEntryS)
    align(f)

    # Segment 12: BigIntStorage
    bigIntStorageS[2] = header["bigIntStorageSize"]
    obj["bigIntStorage"] = read(f, bigIntStorageS)
    align(f)

    # Segment 13: RegExpTable
    obj["regExpTable"] = _readEntries(f, header["regExpCount"], regExpTableEntryS)
    align(f)

    # Segment 14: RegExpStorage
    regExpStorageS[2] = header["regExpStorageSize"]
    obj["regExpStorage"] = read(f, regExpStorageS)
    align(f)

    # Segment 15: CJSModuleTable
    obj["cjsModuleTable"] = _readEntries(f, header["cjsModuleCount"], cjsModuleTableS)
    align(f)

    # Segment 16: FunctionSourceTable
    obj["functionSourceTable"] = _readEntries(f, header["functionSourceCount"], functionSourceTableS)
    align(f)

    obj["instOffset"] = f.tell()
    obj["inst"] = f.readall()

    return obj

def export(obj, f):
    header = obj["header"]
    for key in headerS:
        write(f, header[key], headerS[key])
    align(f)

    overflowedFunctionHeaders = []
    functionHeaders = obj["functionHeaders"]
    for i in range(header["functionCount"]):
        functionHeader = functionHeaders[i]
        if "small" in functionHeader:
            _write_small_func_header(f, functionHeader["small"])
            overflowedFunctionHeaders.append(functionHeader)
        else:
            _write_small_func_header(f, functionHeader)
    align(f)

    for i in range(header["stringKindCount"]):
        writeuint(f, obj["stringKinds"][i], bits=32)
    align(f)

    for i in range(header["identifierCount"]):
        writeuint(f, obj["identifierHashes"][i], bits=32)
    align(f)

    for i in range(header["stringCount"]):
        _write_small_string_entry(f, obj["stringTableEntries"][i])
    align(f)

    _writeEntries(f, obj["stringTableOverflowEntries"], header["overflowStringCount"], overflowStringTableEntryS)
    align(f)

    stringStorageS[2] = header["stringStorageSize"]
    write(f, obj["stringStorage"], stringStorageS)
    align(f)

    literalValueBufferS[2] = header["literalValueBufferSize"]
    write(f, obj["literalValueBuffer"], literalValueBufferS)
    align(f)

    objKeyBufferS[2] = header["objKeyBufferSize"]
    write(f, obj["objKeyBuffer"], objKeyBufferS)
    align(f)

    _writeEntries(f, obj["objShapeTable"], header["objShapeTableCount"], shapeTableEntryS)
    align(f)

    _writeEntries(f, obj["bigIntTable"], header["bigIntCount"], bigIntTableEntryS)
    align(f)

    bigIntStorageS[2] = header["bigIntStorageSize"]
    write(f, obj["bigIntStorage"], bigIntStorageS)
    align(f)

    _writeEntries(f, obj["regExpTable"], header["regExpCount"], regExpTableEntryS)
    align(f)

    regExpStorageS[2] = header["regExpStorageSize"]
    write(f, obj["regExpStorage"], regExpStorageS)
    align(f)

    _writeEntries(f, obj["cjsModuleTable"], header["cjsModuleCount"], cjsModuleTableS)
    align(f)

    _writeEntries(f, obj["functionSourceTable"], header["functionSourceCount"], functionSourceTableS)
    align(f)

    # Write remaining (function bytecode, info, debug info, footer)
    f.writeall(obj["inst"])

    # Write back overflowed (large) function headers at their offsets.
    for overflowedFunctionHeader in overflowedFunctionHeaders:
        smallFunctionHeader = overflowedFunctionHeader["small"]
        large_offset = (smallFunctionHeader["functionName"] << 24) | smallFunctionHeader["offset"]
        f.seek(large_offset)
        for key in functionHeaderS:
            write(f, overflowedFunctionHeader[key], functionHeaderS[key])
