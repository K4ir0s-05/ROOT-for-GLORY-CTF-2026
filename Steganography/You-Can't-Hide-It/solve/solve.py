#!/usr/bin/env python3
"""YOU CANT HIDE IT - solver (k4ir0s)
Usage: python3 solve.py ah_ok.jpg
Needs: pip install pillow  +  the `openssl` command (1.1.1 or newer) + unzip support in Python
"""
import base64, subprocess, sys, zipfile, io
from pathlib import Path
from PIL import Image

path = sys.argv[1] if len(sys.argv) > 1 else "ah_ok.jpg"
raw = Path(path).read_bytes()
img = Image.open(path)

# 1) EXIF ImageDescription (tag 270) holds a Base64 clue
clue = base64.b64decode(img.getexif()[270]).decode()
print("Clue:", clue)

# 2) Password = width x height + "_9lb"
w, h = img.size
password = f"{w}x{h}_9lb"
print("Password:", password)

# 3) Carve the OpenSSL data that starts right after the JPEG end marker (FF D9)
p = raw.index(b"Salted__")
assert raw[p - 2:p] == bytes.fromhex("ffd9"), "Salted__ is not right after FFD9"
payload = raw[p:]
print(f"Encrypted payload at offset {p} ({len(payload)} bytes)")

# 4) Decrypt: AES-256-CBC, PBKDF2, 100000 iterations
zipdata = subprocess.run(
    ["openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-iter", "100000",
     "-pass", f"pass:{password}"],
    input=payload, capture_output=True, check=True).stdout

# 5) The result is a ZIP containing courier_note.txt
with zipfile.ZipFile(io.BytesIO(zipdata)) as z:
    print(z.read("courier_note.txt").decode())
