# Make demo.py importable when pytest is started from examples/starter.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
