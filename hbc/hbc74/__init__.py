
from .parser import parse
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

    def getVersion(self):
        return 74    

    def getHeader(self):
        return self.obj["header"]

    def getFunction(self, fid):
        assert fid >= 0 and fid < self.obj["header"]["functionCount"], "Invalid function ID"

        functionHeader = self.obj["functionHeaders"][fid]
        offset = functionHeader["offset"]
        paramCount = functionHeader["paramCount"]
        bytecodeSizeInBytes = functionHeader["bytecodeSizeInBytes"]
        functionName = functionHeader["functionName"]

        instOffset = self.obj["instOffset"]
        start = offset - instOffset
        end = start + bytecodeSizeInBytes
        inst = disassemble(self.obj["inst"][start:end])

        functionNameStr = self.getString(functionName)

        return functionNameStr, paramCount, inst

    def getString(self, sid):
        assert sid >= 0 and sid < self.obj["header"]["stringCount"], "Invalid string ID"

        stringTableEntry = self.obj["stringTableEntries"][sid]
        stringStorage = self.obj["stringStorage"]

        offset = stringTableEntry["offset"]
        length = stringTableEntry["length"]

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

    def getArray(self, aid):
        assert aid >= 0 and aid < self.obj["header"]["arrayBufferSize"], "Invalid string ID"
        tag = self._checkBufferTag(self.obj["arrayBuffer"], aid)
        ind = 2 if tag[0] > 0x0f else 1
        arr = []
        for _ in range(tag[0]):
            type, val, ind = self._SLPToString(tag[1], self.obj["arrayBuffer"], aid, ind)
            arr.append(val)
        
        return type, arr

    def getObjKey(self, kid):
        assert kid >= 0 and kid < self.obj["header"]["objKeyBufferSize"], "Invalid string ID"
        tag = self._checkBufferTag(self.obj["objKeyBuffer"], kid)
        ind = 2 if tag[0] > 0x0f else 1
        keys = []
        for _ in range(tag[0]):
            type, val, ind = self._SLPToString(tag[1], self.obj["objKeyBuffer"], kid, ind)
            keys.append(val)
        
        return type, keys

    def getObjValue(self, vid):
        assert vid >= 0 and vid < self.obj["header"]["objValueBufferSize"], "Invalid string ID"
        tag = self._checkBufferTag(self.obj["objValueBuffer"], vid)
        ind = 2 if tag[0] > 0x0f else 1
        keys = []
        for _ in range(tag[0]):
            type, val, ind = self._SLPToString(tag[1], self.obj["objValueBuffer"], vid, ind)
            keys.append(val)
        
        return type, keys
