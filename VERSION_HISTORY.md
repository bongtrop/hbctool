# Version History

This document tracks the Hermes Bytecode format changes across supported hbctool versions.

## HBC Version 96

**hbctool support added:** v0.2.0  
**Hermes release era:** React Native 2026 (latest)

### Changes from v94

- `BytecodeOptions` gains the `hasAsync` bit flag:
  ```cpp
  union BytecodeOptions {
    struct {
      bool staticBuiltins : 1;
      bool cjsModulesStaticallyResolved : 1;
      bool hasAsync : 1;   // NEW
    };
    uint8_t _flags;
  };
  ```
- Header total size unchanged (124 bytes)
- No new opcodes relative to v94

---

## HBC Version 94

**hbctool support added:** v0.2.0  
**Hermes release era:** React Native 2025 stable

### Changes from v90

- Minor `BytecodeOptions` struct refinements
- Header layout identical to v90
- No new opcodes relative to v90

---

## HBC Version 90

**hbctool support added:** v0.2.0  
**Hermes release era:** React Native 2024–2025

### Changes from v85

#### Header fields (all uint32 unless noted)

| Field             | Change                                          |
|-------------------|-------------------------------------------------|
| `bigIntCount`     | **NEW** — number of BigInt literals             |
| `bigIntStorageSize` | **NEW** — byte size of BigInt storage block   |
| `cjsModuleOffset` | **RENAMED** to `segmentID`                      |
| `functionSourceCount` | **NEW** — number of preserved function sources |
| `padding`         | Reduced from 31 bytes to 19 bytes               |

Header total size remains 124 bytes.

#### New file segments

- **BigInt Table** — array of `{offset: uint32, length: uint32}` entries (one per BigInt literal)
- **BigInt Storage** — raw byte blob containing serialised BigInt data
- **Function Source Table** — array of `{first: uint32, second: uint32}` pairs (functionID → stringID mapping for preserved source)

For v90–v96, `data/opcode.json` is generated from **upstream** `BytecodeList.def` (see `hbc9x/tool/opcode_generator.py`). The generator includes the `HERMES_RUN_WASM` block (Add32 … Store32), because React Native’s Hermes build defines it — real bundles use those opcode bytes.

#### New opcodes (relative to older hbctool v85 list)

`LoadConstBigInt` / `LoadConstBigIntLongIndex` appear after `LoadConstDouble`, with `OPERAND_BIGINT_ID` in the C++ list (in JSON these operands are `UInt16:B` / `UInt32:B` for tooling). Other newer entries include `CreateInnerEnvironment`, `ThrowIfHasRestrictedGlobalProperty`, `ToNumeric`, and closure opcodes with `OPERAND_FUNCTION_ID` (shown as `:F` in JSON).

Exact opcode **indices** change whenever Hermes adds instructions; do not hard-code byte values. Regenerate `opcode.json` from the matching `BytecodeList.def` tag when upgrading.

---

## HBC Version 85

**hbctool support added:** v0.1.5  
**Hermes release era:** React Native 2023–2024

### Notable fields (relative to v84)

- Generator and async closure opcodes (`CreateGeneratorClosure`, `CreateAsyncClosure`, etc.)
- `SaveGenerator` jump instruction

---

## HBC Version 84

**hbctool support added:** v0.1.4  
**Hermes release era:** React Native 2023

---

## HBC Version 76

**hbctool support added:** v0.1.x  
**Hermes release era:** Legacy

---

## HBC Version 74

**hbctool support added:** v0.1.x  
**Hermes release era:** Legacy

---

## HBC Version 62

**hbctool support added:** v0.1.x  
**Hermes release era:** Legacy

---

## HBC Version 59

**hbctool support added:** v0.1.0  
**Hermes release era:** Original Hermes release

---

## Header Size Reference

All supported versions use a 124-byte file header. The total size is maintained by adjusting the `padding` field as new fields are added.

| Version | uint32 fields | option (uint8) | padding (bytes) | Total |
|---------|--------------|----------------|-----------------|-------|
| 59–85   | 15           | 1              | 31              | 124   |
| 90–96   | 18           | 1              | 19              | 124   |
