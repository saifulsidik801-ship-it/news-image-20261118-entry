#!/usr/bin/env python3
"""news-image-20261118 entry: write the front-page image to the output dir.

The image (entry.png, 1024x1024) sums up Wednesday 18 November 2026:
the U.S.-Iran exchange in the Gulf, Ukraine's second strike on the
Crimea bridge, Trump in Manila, Nvidia's $115.8bn quarter, Canada-China
trade, and Cyclone Akvan. The program is deterministic: it copies the
same file every run, so both runs write identical bytes.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    with open(src, "rb") as fh:
        head = fh.read(len(PNG_MAGIC))
    if head != PNG_MAGIC:
        print("entry.png is not a PNG file", file=sys.stderr)
        return 1
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote {} ({} bytes)".format(dst, os.path.getsize(dst)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
