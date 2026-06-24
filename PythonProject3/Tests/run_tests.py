from __future__ import annotations

import pathlib
import sys

# pyrefly: ignore [missing-import]
import pytest

if __name__ == "__main__":
    root = pathlib.Path(__file__).resolve().parents[2]
    sys.exit(pytest.main([str(root / "PythonProject3" / "Tests")]))