#!/usr/bin/env python3
"""TCHWICH - solver (k4ir0s). Usage: python3 solve.py signal.damaged"""
import sys
from pathlib import Path
raw = Path(sys.argv[1] if len(sys.argv) > 1 else "signal.damaged").read_bytes()
noise = b"zzzt"
print("Injected 'zzzt' patterns:", raw.count(noise))      # 253
fixed = raw.replace(noise, b"")
Path("recovered.jpg").write_bytes(fixed)
print("JPEG header OK:", fixed[:2] == b"\xff\xd8", "| end marker OK:", fixed[-2:] == b"\xff\xd9")
i = fixed.find(b"GCDx")
if i >= 0:
    print("Decoy flag in EXIF comment:", fixed[i:fixed.find(b"}", i) + 1].decode())
print("Now open recovered.jpg: the real flag is engraved on the sword.")
