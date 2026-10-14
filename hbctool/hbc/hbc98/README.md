# Hermes Bytecode version 98

Support for Hermes Bytecode (HBC) **version 98**, as produced by recent React
Native / Hermes toolchains (validated against a React Native 0.86.x app).

Bytecode version 98 spans a wide range of Hermes commits (the version number was
not bumped for a long time). This module targets the **late v98** file format,
which differs substantially from v85 and earlier:

## File header

- Added `bigIntCount` / `bigIntStorageSize` (BigInt table + storage).
- The separate array buffer and object-value buffer were merged into a single
  `literalValueBuffer` (`literalValueBufferSize`).
- Added `objShapeTableCount` (object shape/hidden-class table).
- Added `numStringSwitchImms` (count of `StringSwitchImm` instructions).
- Added `functionSourceCount` (function source table); `cjsModuleOffset` removed
  in favour of `segmentID`.
- Header is 128 bytes (`padding[15]`).

## Function headers

`SmallFuncHeader` is 12 bytes with a new bit layout:

```
word1: offset:25, paramCount:5, loopDepth:2
word2: bytecodeSizeInBytes:14, functionName:8, numberRegCount:5, nonPtrRegCount:5
word3: frameSize:8, readCacheSize:8, writeCacheSize:7, privateNameCacheSize:1, flags:8
```

Because `functionName` is only 8 bits in the small header, most functions whose
name string-id is > 255 are stored as **overflowed** headers. The large header
offset is encoded as `(functionName << 24) | offset`, and the `overflowed` flag
is bit 5 of `FunctionHeaderFlag`.

## Segment order

`FunctionHeaders, StringKinds, IdentifierHashes, SmallStringTable,
OverflowStringTable, StringStorage, LiteralValueBuffer, ObjKeyBuffer,
ObjShapeTable, BigIntTable, BigIntStorage, RegExpTable, RegExpStorage,
CJSModuleTable, FunctionSourceTable`.

## Opcodes

219 opcodes (`data/opcode.json`), generated from the v98 `BytecodeList.def`
including `TypeOfIs`, `StringSwitchImm`, `JmpTypeOfIs`, `DefineOwn*`,
`LoadParentNoTraps`, and the `JmpBuiltinIs` family.

## Validation

`hbc.load()` followed by `hbc.dump()` reproduces a real v98 bundle
**byte-for-byte**, and all functions disassemble/re-assemble cleanly.
