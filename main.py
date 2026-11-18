"""Copy the finished entry image to the output directory.

Standard library only: the grading server installs nothing before it runs,
so this program uses no third-party packages at all.
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "entry.png"
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")

if not SRC.is_file():
    raise SystemExit(f"missing entry image: {SRC}")

OUT.mkdir(parents=True, exist_ok=True)
shutil.copyfile(SRC, OUT / "entry.png")
print(f"wrote {OUT / 'entry.png'} ({SRC.stat().st_size} bytes)")
