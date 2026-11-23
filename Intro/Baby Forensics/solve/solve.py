#!/usr/bin/env python3
"""Baby Forensics solver - GCDxGLORY CTF (author: K4ir0s)

Usage: python3 solve.py [parts.7z | folder with the part_*.txt files]
The archive needs `pip install py7zr` (or extract it yourself with 7z and pass the folder).
Writes solved.png: open it to read the flag.
"""
import base64, glob, re, sys, tempfile
from pathlib import Path

src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "files" / "parts.7z"

if src.is_file():                                   # .7z archive
    import py7zr
    folder = Path(tempfile.mkdtemp())
    with py7zr.SevenZipFile(src) as z:
        z.extractall(folder)
else:
    folder = src

parts, total = {}, set()
for path in glob.glob(str(folder / "**" / "*.txt"), recursive=True):
    header, body = Path(path).read_text().split("\n", 1)
    m = re.fullmatch(r"# part (\d+)/(\d+)", header.strip())   # the order is in the first line,
    parts[int(m.group(1))] = body.strip()                     # NOT in the (random) file name
    total.add(int(m.group(2)))

assert len(total) == 1 and sorted(parts) == list(range(1, total.pop() + 1)), "missing or duplicate part"
data = base64.b64decode("".join(parts[k] for k in sorted(parts)))
assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
Path("solved.png").write_bytes(data)
print(f"{len(parts)} parts -> solved.png ({len(data)} bytes). Open it to read the flag.")
