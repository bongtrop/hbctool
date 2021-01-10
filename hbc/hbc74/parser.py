from util import *
import json
import pathlib

basepath = pathlib.Path(__file__).parent.absolute()

MAGIC = 2240826417119764422
BYTECODE_ALIGNMENT = 4

INVALID_OFFSET = (1 << 23)
INVALID_LENGTH = (1 << 8) - 1

def align(f):
    f.pad(BYTECODE_ALIGNMENT)

def parse(f):
    structure = json.load(open(f"{basepath}/data/structure.json", "r"))

    headerS = structure["header"]
    smallFunctionHeaderS = structure["SmallFuncHeader"]
    functionHeaderS = structure["FuncHeader"]
    stringTableEntryS = structure["SmallStringTableEntry"]
    overflowStringTableEntryS = structure["OverflowStringTableEntry"]
    stringStorageS = structure["StringStorage"]
    arrayBufferS = structure["ArrayBuffer"]
    objKeyBufferS = structure["ObjKeyBuffer"]
    objValueBufferS = structure["ObjValueBuffer"]
    regExpTableEntryS = structure["RegExpTableEntry"]
    regExpStorageS = structure["RegExpStorage"]
    cjsModuleTableS = structure["CJSModuleTable"]

    obj = {}

    # Segment 1: Header
    header = {}
    for key in headerS:
        header[key] = read(f, headerS[key])
    
    obj["header"] = header
    align(f)
    
    # Segment 2: Function Header
    functionHeaders = []
    for i in range(header["functionCount"]):
        functionHeader = {}
        for key in smallFunctionHeaderS:
            functionHeader[key] = read(f, smallFunctionHeaderS[key])
        
        if (functionHeader["flags"] >> 5) & 1:
            saved_pos = f.tell()
            large_offset = (functionHeader["infoOffset"] << 16 )  | functionHeader["offset"]
            f.seek(large_offset)
            for key in functionHeaderS:
                functionHeader[key] = read(f, functionHeaderS[key])

            f.seek(saved_pos)

        functionHeaders.append(functionHeader)

    obj["functionHeaders"] = functionHeaders
    align(f)

    # Segment 3: StringKind
    # FIXME : Do nothing just skip
    stringKinds = []
    for _ in range(header["stringKindCount"]):
        stringKinds.append(readuint(f, bits=32))

    obj["stringKinds"] = stringKinds
    align(f)

    # Segment 3: IdentifierHash
    # FIXME : Do nothing just skip
    identifierHashes = []
    for _ in range(header["identifierCount"]):
        identifierHashes.append(readuint(f, bits=32))
    
    obj["identifierHashes"] = identifierHashes
    align(f)

    # Segment 4: StringTable
    stringTableEntries = []
    for _ in range(header["stringCount"]):
        stringTableEntry = {}
        for key in stringTableEntryS:
            stringTableEntry[key] = read(f, stringTableEntryS[key])
        
        stringTableEntries.append(stringTableEntry)

    obj["stringTableEntries"] = stringTableEntries
    align(f)

    # Segment 5: StringTableOverflow
    stringTableOverflowEntries = []
    for _ in range(header["overflowStringCount"]):
        stringTableOverflowEntry = {}
        for key in overflowStringTableEntryS:
            stringTableOverflowEntry[key] = read(f, overflowStringTableEntryS[key])
        
        stringTableOverflowEntries.append(stringTableOverflowEntry)
    
    obj["stringTableOverflowEntries"] = stringTableOverflowEntries
    align(f)

    # Segment 6: StringStorage
    stringStorageS[2] = header["stringStorageSize"]
    stringStorage = read(f, stringStorageS)

    obj["stringStorage"] = stringStorage
    align(f)

    # Segment 7: ArrayBuffer
    arrayBufferS[2] = header["arrayBufferSize"]
    arrayBuffer = read(f, arrayBufferS)

    obj["arrayBuffer"] = arrayBuffer
    align(f)

    # Segment 9: ObjKeyBuffer
    objKeyBufferS[2] = header["objKeyBufferSize"]
    objKeyBuffer = read(f, objKeyBufferS)

    obj["objKeyBuffer"] = objKeyBuffer
    align(f)

    # Segment 10: ObjValueBuffer
    objValueBufferS[2] = header["objValueBufferSize"]
    objValueBuffer = read(f, objValueBufferS)

    obj["objValueBuffer"] = objValueBuffer
    align(f)

    # Segment 11: RegExpTable
    regExpTable = []
    for _ in range(header["regExpCount"]):
        regExpEntry = {}
        for key in regExpTableEntryS:
            regExpEntry[key] = read(f, regExpTableEntryS[key])
        
        regExpTable.append(regExpEntry)

    obj["regExpTable"] = regExpTable
    align(f)    
    
    # Segment 12: RegExpStorage
    regExpStorageS[2] = header["regExpStorageSize"]
    regExpStorage = read(f, regExpStorageS)

    obj["regExpStorage"] = regExpStorage
    align(f)

    # Segment 13: CJSModuleTable
    cjsModuleTable = []
    for _ in range(header["cjsModuleCount"]):
        cjsModuleEntry = {}
        for key in cjsModuleTableS:
            cjsModuleEntry[key] = read(f, cjsModuleTableS[key])
        
        cjsModuleTable.append(cjsModuleEntry)

    obj["cjsModuleTable"] = cjsModuleTable
    align(f)

    obj["instOffset"] = f.tell()
    obj["inst"] = f.readall()

    return obj
