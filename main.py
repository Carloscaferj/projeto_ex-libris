#!/usr/bin/env python3
"""Ponto de entrada legado que preserva `python main.py`."""

from pathlib import Path
import sys

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from exlibris.cli import main

if __name__ == "__main__":
    main()
