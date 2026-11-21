"""Entrypoint: copy the bundled poster to /output/entry.png.

Standard library only, no network, deterministic. Verifies the PNG
header and the 1024x1024 size before copying, so a broken image can
never be submitted by accident.
"""
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"), "entry.png")


def main():
    with open(SRC, "rb") as fh:
        head = fh.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit("entry.png is not a PNG file")
    width, height = struct.unpack(">II", head[16:24])
    if (width, height) != (1024, 1024):
        sys.exit("entry.png is %dx%d, expected 1024x1024" % (width, height))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    shutil.copyfile(SRC, OUT)
    print("copied entry.png (%dx%d) to %s" % (width, height, OUT))


if __name__ == "__main__":
    main()
