from __future__ import annotations
"""Bootstrap runner.
Ensures `./src` is on sys.path so imports work reliably.
Run with:
    python run.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from image_hunter.app import main  # Import after sys.path adjustment

if __name__ == "__main__":
    raise SystemExit(main())
