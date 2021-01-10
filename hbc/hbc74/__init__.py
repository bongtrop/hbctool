
from .parser import parse, INVALID_LENGTH
from .translator import disassemble
from struct import pack, unpack

NullTag = 0
TrueTag = 1 << 4
FalseTag = 2 << 4
NumberTag = 3 << 4
LongStringTag = 4 << 4
ShortStringTag = 5 << 4
ByteStringTag = 6 << 4
IntegerTag = 7 << 4
TagMask = 0x70

class HBC74:
    def __init__(self, f):
        self.obj = parse(f)

    def getObj(self):
        return self.obj

    def getVersion(self):
        return 74    

    def getHeader(self):
        return self.obj["header"]

    def getFunctionCount(self):
        return self.obj["header"]["functionCount"]

    def getFunction(self, fid, disasm=True):
        assert fid >= 0 and fid < self.getFunctionCount(), "Invalid function ID"

        functionHeader = self.obj["functionHeaders"][fid]
        offset = functionHeader["offset"]
        paramCount = functionHeader["paramCount"]
        registerCount = functionHeader["frameSize"]
        symbolCount = functionHeader["environmentSize"]
        bytecodeSizeInBytes = functionHeader["bytecodeSizeInBytes"]
        functionName = functionHeader["functionName"]

        instOffset = self.obj["instOffset"]
        start = offset - instOffset
        end = start + bytecodeSizeInBytes
        inst = self.obj["inst"][start:end]
        if disasm:
            inst = disassemble(inst)
        

        functionNameStr = self.getString(functionName)

        return functionNameStr, paramCount, registerCount, symbolCount, inst, functionHeader

    def getStringCount(self):
        return self.obj["header"]["stringCount"]

    def getString(self, sid):
        assert sid >= 0 and sid < self.getStringCount(), "Invalid string ID"

        stringTableEntry = self.obj["stringTableEntries"][sid]
        stringStorage = self.obj["stringStorage"]
        stringTableOverflowEntries = self.obj["stringTableOverflowEntries"]


        offset = stringTableEntry["offset"]
        length = stringTableEntry["length"]

        if length >= INVALID_LENGTH:
            stringTableOverflowEntry = stringTableOverflowEntries[offset]
            offset = stringTableOverflowEntry["offset"]
            length = stringTableOverflowEntry["length"]

        s = bytes(stringStorage[offset:offset + length])
        return s

    def _checkBufferTag(self, buf, iid):
        keyTag = buf[iid]
        if keyTag & 0x80:
            return (((keyTag & 0x0f) << 8) | (buf[iid + 1]), keyTag & TagMask)
        else:
            return (keyTag & 0x0f, keyTag & TagMask)

    def _SLPToString(self, tag, buf, iid, ind):
        start = iid + ind
        if tag == ByteStringTag:
            type = "String"
            val = buf[start]
            ind += 1
        elif tag == ShortStringTag:
            type = "String"
            val = unpack("<H", bytes(buf[start:start+2]))[0]
            ind += 2
        elif tag == LongStringTag:
            type = "String"
            val = unpack("<L", bytes(buf[start:start+4]))[0]
            ind += 4
        elif tag == NumberTag:
            type = "Number"
            val = unpack("<d", bytes(buf[start:start+8]))[0]
            ind += 8
        elif tag == IntegerTag:
            type = "Integer"
            val = unpack("<L", bytes(buf[start:start+4]))[0]
            ind += 4
        elif tag == NullTag:
            type = "Null"
            val = None
        elif tag == TrueTag:
            type = "Boolean"
            val = True
        elif tag == FalseTag:
            type = "Boolean"
            val = False
        else:
            type = "Empty"
            val = None
        
        return type, val, ind

    def getArrayBufferSize(self):
        return self.obj["header"]["arrayBufferSize"]

    def getArray(self, aid):
        assert aid >= 0 and aid < self.getArrayBufferSize(), "Invalid Array ID"
        tag = self._checkBufferTag(self.obj["arrayBuffer"], aid)
        ind = 2 if tag[0] > 0x0f else 1
        arr = []
        for _ in range(tag[0]):
            type, val, ind = self._SLPToString(tag[1], self.obj["arrayBuffer"], aid, ind)
            arr.append(val)
        
        return type, arr

    def getObjKeyBufferSize(self):
        return self.obj["header"]["objKeyBufferSize"]

    def getObjKey(self, kid):
        assert kid >= 0 and kid < self.getObjKeyBufferSize(), "Invalid ObjKey ID"
        tag = self._checkBufferTag(self.obj["objKeyBuffer"], kid)
        ind = 2 if tag[0] > 0x0f else 1
        keys = []
        for _ in range(tag[0]):
            type, val, ind = self._SLPToString(tag[1], self.obj["objKeyBuffer"], kid, ind)
            keys.append(val)
        
        return type, keys

    def getObjValueBufferSize(self):
        return self.obj["header"]["objValueBufferSize"]

    def getObjValue(self, vid):
        assert vid >= 0 and vid < self.getObjValueBufferSize(), "Invalid ObjValue ID"
        tag = self._checkBufferTag(self.obj["objValueBuffer"], vid)
        ind = 2 if tag[0] > 0x0f else 1
        keys = []
        for _ in range(tag[0]):
            type, val, ind = self._SLPToString(tag[1], self.obj["objValueBuffer"], vid, ind)
            keys.append(val)
        
        return type, keys
