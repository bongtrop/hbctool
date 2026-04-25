#!/usr/bin/env python3
"""
Legacy unit tests runner (root of the repository).

Run from the repo root (same directory as pyproject.toml):

    python3 test.py

This sets PYTHONPATH and changes into the inner `hbctool/` package directory
so paths like `hbc/hbc59/example/index.android.bundle` resolve correctly.
"""
from __future__ import annotations

import os
import pathlib
import sys
import unittest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent
_INNER_PKG = _REPO_ROOT / "hbctool"

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# hbc59/62/74/76 tests open files relative to the inner package dir
os.chdir(_INNER_PKG)

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromName("hbctool.test")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
