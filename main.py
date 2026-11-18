"""Copy the finished entry image to the output directory.

Standard library only: the grading server installs nothing before it runs,
so this program uses no third-party packages at all.
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

OUT.mkdir(parents=True, exist_ok=True)
shutil.copyfile(HERE / "entry.png", OUT / "entry.png")
print(f"wrote {OUT / 'entry.png'}")
