# hbctool 

[![Python 3.x](https://img.shields.io/badge/python-3.8%2B-yellow.svg)](https://python.org) [![PyPI version](https://badge.fury.io/py/hbctool.svg)](https://badge.fury.io/py/hbctool) [![Software License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](/LICENSE)

A command-line interface for disassembling and assembling the Hermes Bytecode.

Since the React Native team created their own JavaScript engine (named Hermes) for running the React Native application, the JavaScript source code is often compiled to the Hermes bytecode. In the penetration test project, I found that some React Native applications have already been migrated to the Hermes engine. It is really hard to analyze or patch those applications. Therefore, I created hbctool for helping any pentester to test the Hermes bytecode.

> [Hermes](https://hermesengine.dev/) is an open-source JavaScript engine optimized for running React Native apps on Android. For many apps, enabling Hermes will result in improved start-up time, decreased memory usage, and smaller app size. At this time Hermes is an opt-in React Native feature, and this guide explains how to enable it.

Special thanks to [ErbaZZ](https://github.com/ErbaZZ) and [Jusmistic](https://github.com/Jusmistic) for helping me research and develop this tool.

For more information, please visit:

[https://suam.wtf/posts/react-native-application-static-analysis-en/](https://suam.wtf/posts/react-native-application-static-analysis-en/)

## Screenshot

![hbctool Example](/image/hbctool_example.gif)

This video with MP4 format can be found at [/image/hbctool_example.mp4](/image/hbctool_example.mp4).

## Installation

To install hbctool, simply use pip:

```
pip install hbctool
```

## Usage

Please run `hbctool --help` to show the usage.

```
hbctool --help   
A command-line interface for disassembling and assembling
the Hermes Bytecode.

Usage:
    hbctool disasm <HBC_FILE> <HASM_PATH>
    hbctool asm <HASM_PATH> <HBC_FILE>
    hbctool --help
    hbctool --version

Operation:
    disasm              Disassemble Hermes Bytecode
    asm                 Assemble Hermes Bytecode

Args:
    HBC_FILE            Target HBC file
    HASM_PATH           Target HASM directory path

Options:
    --version           Show hbctool version
    --help              Show hbctool help manual

Examples:
    hbctool disasm index.android.bundle test_hasm
    hbctool asm test_hasm index.android.bundle
```

> For Android, the HBC file normally locates at `assets` directory with `index.android.bundle` filename.

After `hbctool disasm <bundle> <out_dir>`, the output directory contains **`instruction.hasm`** (disassembled bytecode), `string.json`, and `metadata.json` — not a file named `hbc_disasm.hasm`.

## Supported Versions

| HBC Version | Status    | React Native Era      | Key Features                          |
|-------------|-----------|-----------------------|---------------------------------------|
| 96          | ✅ NEW    | Latest 2026           | `hasAsync` flag in BytecodeOptions    |
| 94          | ✅ NEW    | 2025 stable           | BytecodeOptions refinements           |
| 90          | ✅ NEW    | 2024–2025             | BigInt support, `segmentID`, `functionSourceCount` |
| 85          | ✅        | 2023–2024             | Generator/async closures              |
| 84          | ✅        | 2023                  | —                                     |
| 76          | ✅        | Legacy                | —                                     |
| 74          | ✅        | Legacy                | —                                     |
| 62          | ✅        | Legacy                | —                                     |
| 59          | ✅        | Original              | —                                     |

## Contribution

Feel free to create an issue or submit a pull request in any way you want to contribute to this project.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

However, please run the unit tests before submitting the pull request.

From the **repository root** (the folder that contains `pyproject.toml`):

```
python3 test.py
python3 -m pytest test_new_versions.py -v
```

The root `test.py` runs the legacy unittest suite (23 tests) with the correct working directory. New HBC version checks live in `test_new_versions.py`.

I use poetry to build this tool. To build it yourself, simply execute:

1. `poetry install`
2. `poetry build`
3. `pip install --force-reinstall dist/hbctool-<VERSION>-py3-none-any.whl`

## Changelog

### v0.2.0
- Added HBC version 96 support (`hasAsync` in `BytecodeOptions`)
- Added HBC version 94 support (BytecodeOptions refinements)
- Added HBC version 90 support (BigInt opcodes, `segmentID`, `bigIntCount`, `bigIntStorageSize`, `functionSourceCount`)
- Updated Python requirement to 3.8+
- Added `LoadConstBigInt` and `LoadConstBigIntLongIndex` opcodes for v90+
- Added BigInt table and storage parsing
- Added FunctionSource table parsing

### v0.1.5
- Added HBC version 85 support

### v0.1.4
- Added HBC version 84 support

### v0.1.3 and earlier
- Initial versions with HBC 59, 62, 74, 76 support

## Troubleshooting

**`error: externally-managed-environment` (macOS Homebrew Python)**

Do not install into the system Python. Create a venv in the repo and install there:

```bash
cd /path/to/hbctool
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python3 -m pip install -e .
hbctool --help
```

**`hbctool: command not found`**

The shell only knows about `hbctool` after the package is installed into the **active** Python (use a venv as above, then `pip install -e .`):

```bash
cd /path/to/hbctool
source .venv/bin/activate
python3 -m pip install -e .
hbctool --help
```

Alternatively, from the same directory, without installing the script onto `PATH`:

```bash
python3 -m pip install docopt
cd /path/to/hbctool
PYTHONPATH=. python3 -m hbctool disasm /path/to/index.android.bundle ./out_hasms
```

**Unsupported HBC version error**

If you see `The HBC version (X) is not supported`, check the table above. If your version is listed and you still get this error, ensure you have the latest hbctool installed:

```
pip install --upgrade hbctool
```

**How to identify your HBC version**

The version is stored at bytes 8–11 (little-endian uint32) of the bundle file, immediately after the 8-byte magic number. You can check it with:

```python
import struct
with open("index.android.bundle", "rb") as f:
    f.seek(8)
    version = struct.unpack("<I", f.read(4))[0]
print(f"HBC version: {version}")
```

**Patched bundle fails to load**

Ensure the `fileLength` field in the header matches the actual file size after assembly. Also verify that instruction sizes have not exceeded their original bytecode size limits.

## Next Step

- Add the other Hermes bytecode versions
- Create a class abstraction
- Support overflow patching
- Do all TODO, NOTE, FIXME in source code
