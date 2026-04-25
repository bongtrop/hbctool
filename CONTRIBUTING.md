# Contributing to hbctool

Thank you for your interest in contributing! This guide explains how to add support for new Hermes Bytecode versions and how to submit changes.

## Getting Started

1. Fork the repository and clone your fork.
2. Install dependencies:
   ```
   poetry install
   ```
3. Create a new branch for your feature:
   ```
   git checkout -b feat/your-feature-name
   ```

## Adding a New HBC Version

Each supported version lives in `hbctool/hbc/hbcXX/` where `XX` is the version number. To add version `N`:

### 1. Copy the closest existing version

```
cp -r hbctool/hbc/hbc85 hbctool/hbc/hbcN
```

Use the highest supported version that is less than `N` as your template.

### 2. Update `data/structure.json`

This file defines the binary layout. The `header` object must exactly match the `BytecodeFileHeader` struct in the Hermes source (`include/hermes/BCGen/HBC/BytecodeFileFormat.h` for the target version).

Key fields and their types:
- `["uint", 64, 1]` — 64-bit unsigned integer (1 value)
- `["uint", 32, 1]` — 32-bit unsigned integer
- `["uint", 8, N]` — array of N bytes
- `["bit", W, 1]` — bitfield of width W

### 3. Update `data/opcode.json`

This file maps opcode names to their operand type lists. The ordering is critical — position in the JSON object determines the opcode byte value.

Operand types:
- `"Reg8"` / `"Reg32"` — register (1 or 4 bytes)
- `"UInt8"` / `"UInt16"` / `"UInt32"` — unsigned integer
- `"Addr8"` / `"Addr32"` — relative branch offset
- `"Imm32"` — signed 32-bit immediate
- `"Double"` — 64-bit IEEE 754 double
- `"UInt16:S"` / `"UInt32:S"` — string table index (suffix `:S` marks it as a string reference)

To find the correct opcode list for a Hermes version, look at `lib/BCGen/HBC/BytecodeList.def` in the Hermes GitHub repository at the matching tag.

### 4. Update `parser.py`

If the new version adds new file segments (e.g., a new table), update `parse()` and `export()` accordingly, following the pattern used for existing segments.

### 5. Update `__init__.py`

- Rename the class to `HBCN`
- Update `getVersion()` to return `N`

### 6. Register the version in `hbctool/hbc/__init__.py`

```python
from hbctool.hbc.hbcN import HBCN

HBC = {
    N: HBCN,
    # ... existing versions
}
```

### 7. Update `hbctool/metadata.py` and `pyproject.toml`

Bump the version string following [Semantic Versioning](https://semver.org/).

### 8. Update `README.md` and `VERSION_HISTORY.md`

Add an entry to the supported versions table and the changelog.

## Running Tests

From the repository root (where `pyproject.toml` lives):

```
python3 test.py
python3 -m pytest test_new_versions.py -v
```

The root `test.py` is a small runner that loads `hbctool.test` and uses the correct working directory for bundled example bundles under `hbctool/hbc/hbc*/example/`.

## Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) style:

```
feat: Add HBC version N support

- Brief description of structural changes
- New opcodes added
- Any parser changes

Fixes #<issue-number>
```

## Pull Request Checklist

- [ ] Copied and updated `structure.json` matches the Hermes C++ header
- [ ] Opcode ordering in `opcode.json` verified against `BytecodeList.def`
- [ ] `parser.py` correctly handles all new segments in both `parse()` and `export()`
- [ ] `__init__.py` class name and `getVersion()` return value are correct
- [ ] New version registered in `hbctool/hbc/__init__.py`
- [ ] Version bumped in `metadata.py` and `pyproject.toml`
- [ ] `README.md` version table updated
- [ ] `VERSION_HISTORY.md` changelog updated
- [ ] All existing tests pass

## Code Style

- Follow the existing code patterns — no external formatter is enforced
- Avoid adding comments that merely restate what the code does
- Keep each version's folder self-contained; do not share mutable module-level state across versions
