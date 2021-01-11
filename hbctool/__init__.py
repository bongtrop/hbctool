"""
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
"""
from docopt import docopt
from hbctool import metadata, hbc, hasm

def disasm(hbcfile, hasmpath):
    print(f"[*] Disassemble '{hbcfile}' to '{hasmpath}' path")
    f = open(hbcfile, "rb")
    hbco = hbc.load(f)
    f.close()

    header = hbco.getHeader()
    sourceHash = bytes(header["sourceHash"]).hex()
    version = header["version"]
    print(f"[*] Hermes Bytecode [ Source Hash: {sourceHash}, HBC Version: {version} ]")

    hasm.dump(hbco, hasmpath)
    print(f"[*] Done")

def asm(hasmpath, hbcfile):
    print(f"[*] Assemble '{hasmpath}' to '{hbcfile}' path")
    hbco = hasm.load(hasmpath)

    header = hbco.getHeader()
    sourceHash = bytes(header["sourceHash"]).hex()
    version = header["version"]
    print(f"[*] Hermes Bytecode [ Source Hash: {sourceHash}, HBC Version: {version} ]")

    f = open(hbcfile, "wb")
    hbc.dump(hbco, f)
    f.close()
    print(f"[*] Done")

def main():
    args = docopt(__doc__, version=f"{metadata.project} {metadata.version}")
    if args['disasm']:
        disasm(args['<HBC_FILE>'], args['<HASM_PATH>'])
    elif args['asm']:
        asm(args['<HASM_PATH>'], args['<HBC_FILE>'])
    

def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    main()

if __name__ == "__main__":
    main()