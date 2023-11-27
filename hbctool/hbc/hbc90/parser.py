from hbctool.util import *
import json
import pathlib
import copy

basepath = pathlib.Path(__file__).parent.absolute()

MAGIC = 2240826417119764422
BYTECODE_ALIGNMENT = 4

INVALID_OFFSET = (1 << 23)
INVALID_LENGTH = (1 << 8) - 1

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
bigIntTableEntryS = structure["BigIntTableEntry"]
bigIntStorageS = structure["BigIntStorage"]
regExpTableEntryS = structure["RegExpTableEntry"]
regExpStorageS = structure["RegExpStorage"]
cjsModuleTableS = structure["CJSModuleTable"]
funSourceTableS = structure["FunctionSourceTable"]

def align(f):
    f.pad(BYTECODE_ALIGNMENT)

def parse(f):
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
            functionHeader["small"] = copy.deepcopy(functionHeader)
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

    # Segment XX: BigIntTable
    bigIntTable = []
    for _ in range(header["bigIntCount"]):
        bigIntEntry = {}
        for key in bigIntTableEntryS:
            bigIntEntry[key] = read(f, bigIntTableEntryS[key])

        bigIntTable.append(bigIntEntry)

    obj["bigIntTable"] = bigIntTable
    align(f)

    # Segment XX: BigIntStorage
    bigIntStorageS[2] = header["bigIntStorageSize"]
    bigIntStorage = read(f, bigIntStorageS)

    obj["bigIntStorage"] = bigIntStorage
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

    # Segment 14: FunctionSourceTable
    # Not doing anything with this data right now; just advancing the file
    # pointer
    funSourceTable = []
    for _ in range(header["functionSourceCount"]):
        funSourceEntry = {}
        for key in funSourceTableS:
            funSourceEntry[key] = read(f, funSourceTableS[key])

        funSourceTable.append(funSourceEntry)

    obj["funSourceTable"] = funSourceTable
    align(f)

    obj["instOffset"] = f.tell()
    obj["inst"] = f.readall()

    return obj

def export(obj, f):
    # Segment 1: Header
    header = obj["header"]
    for key in headerS:
        write(f, header[key], headerS[key])
    
    align(f)
    
    overflowedFunctionHeaders = []
    # Segment 2: Function Header
    functionHeaders = obj["functionHeaders"]
    for i in range(header["functionCount"]):
        functionHeader = functionHeaders[i]
        if "small" in functionHeader:
            for key in smallFunctionHeaderS:
                write(f, functionHeader["small"][key], smallFunctionHeaderS[key])
            
            overflowedFunctionHeaders.append(functionHeader)
        
        else:
            for key in smallFunctionHeaderS:
                write(f, functionHeader[key], smallFunctionHeaderS[key])

    align(f)

    # Segment 3: StringKind
    # FIXME : Do nothing just skip
    stringKinds = obj["stringKinds"]
    for i in range(header["stringKindCount"]):
        writeuint(f, stringKinds[i], bits=32)

    align(f)

    # Segment 3: IdentifierHash
    # FIXME : Do nothing just skip
    identifierHashes = obj["identifierHashes"]
    for i in range(header["identifierCount"]):
        writeuint(f, identifierHashes[i], bits=32)

    align(f)

    # Segment 4: StringTable
    stringTableEntries = obj["stringTableEntries"]
    for i in range(header["stringCount"]):
        for key in stringTableEntryS:
            stringTableEntry = stringTableEntries[i]
            write(f, stringTableEntry[key], stringTableEntryS[key])

    align(f)

    # Segment 5: StringTableOverflow
    stringTableOverflowEntries = obj["stringTableOverflowEntries"]
    for i in range(header["overflowStringCount"]):
        for key in overflowStringTableEntryS:
            stringTableOverflowEntry = stringTableOverflowEntries[i]
            write(f, stringTableOverflowEntry[key], overflowStringTableEntryS[key])

    align(f)

    # Segment 6: StringStorage
    stringStorage = obj["stringStorage"]
    stringStorageS[2] = header["stringStorageSize"]
    write(f, stringStorage, stringStorageS)

    align(f)

    # Segment 7: ArrayBuffer
    arrayBuffer = obj["arrayBuffer"]
    arrayBufferS[2] = header["arrayBufferSize"]
    write(f, arrayBuffer, arrayBufferS)

    align(f)

    # Segment 9: ObjKeyBuffer
    objKeyBuffer = obj["objKeyBuffer"]
    objKeyBufferS[2] = header["objKeyBufferSize"]
    write(f, objKeyBuffer, objKeyBufferS)

    align(f)

    # Segment 10: ObjValueBuffer
    objValueBuffer = obj["objValueBuffer"]
    objValueBufferS[2] = header["objValueBufferSize"]
    write(f, objValueBuffer, objValueBufferS)

    align(f)

    # Segment 11: RegExpTable
    regExpTable = obj["regExpTable"]
    for i in range(header["regExpCount"]):
        regExpEntry = regExpTable[i]
        for key in regExpTableEntryS:
            write(f, regExpEntry[key], regExpTableEntryS[key])

    align(f)    
    
    # Segment 12: RegExpStorage
    regExpStorage = obj["regExpStorage"]
    regExpStorageS[2] = header["regExpStorageSize"]
    write(f, regExpStorage, regExpStorageS)

    align(f)

    # Segment 13: CJSModuleTable
    cjsModuleTable = obj["cjsModuleTable"]
    for i in range(header["cjsModuleCount"]):
        cjsModuleEntry = cjsModuleTable[i]
        for key in cjsModuleTableS:
            write(f, cjsModuleEntry[key], cjsModuleTableS[key])
        
    align(f)

    # Segment 14: FunctionSourceTable
    funSourceTable = obj["funSourceTable"]
    for i in range(header["functionSourceCount"]):
        funSourceEntry = funSourceTable[i]
        for key in funSourceTableS:
            write(f, funSourceEntry[key], funSourceTableS[key])

    align(f)

    # Write remaining
    f.writeall(obj["inst"])

    # Write Overflowed Function Header
    for overflowedFunctionHeader in overflowedFunctionHeaders:
        smallFunctionHeader = overflowedFunctionHeader["small"]
        large_offset = (smallFunctionHeader["infoOffset"] << 16 )  | smallFunctionHeader["offset"]
        f.seek(large_offset)
        for key in functionHeaderS:
            write(f, overflowedFunctionHeader[key], functionHeaderS[key])

