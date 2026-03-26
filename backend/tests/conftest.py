"""Pytest configuration for the backend test suite."""
import sys
from pathlib import Path

# Make `app` importable from the backend root without installing the package.
sys.path.insert(0, str(Path(__file__).parent.parent))
