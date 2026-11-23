#!/usr/bin/env python3
"""ALWAN solver - GCDSTE CTF: ROOTfor GLORY (author: K4ir0s)

Usage: python3 solve.py ../files/4lw4n.bmp
Needs: numpy, pillow, and one of: cryptography / pycryptodome / openssl binary.
"""
import base64, hashlib, re, string, struct, subprocess, sys
import numpy as np
from PIL import Image

path = sys.argv[1] if len(sys.argv) > 1 else "../files/4lw4n.bmp"
raw = open(path, "rb").read()

# --- Step 1: BMP header -> stride / start from "almost normal" DPI values
size_field = struct.unpack_from("<I", raw, 2)[0]
width = struct.unpack_from("<i", raw, 18)[0]
ppm_x, ppm_y = struct.unpack_from("<ii", raw, 38)
stride, start = ppm_x % 256, ppm_y % 256
print(f"[1] width={width} ppmX={ppm_x} ppmY={ppm_y} -> stride={stride} start={start}")

# --- Step 2: text lines appended after the pixel data
tail = raw[size_field:].decode(errors="ignore").replace("\x00", " ").split()
print(f"[2] {len(tail)} unlabeled lines after the BMP data")

# --- Step 3: key = SHA-256(riddle answer + width)
key = hashlib.sha256(f"4lw4n{width}".encode()).digest()
print("[3] key =", key.hex())

def aes_ctr_dec(iv: bytes, ct: bytes) -> bytes:
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        d = Cipher(algorithms.AES(key), modes.CTR(iv)).decryptor()
        return d.update(ct) + d.finalize()
    except ImportError:
        pass
    try:
        from Crypto.Cipher import AES
        from Crypto.Util import Counter
        ctr = Counter.new(128, initial_value=int.from_bytes(iv, "big"))
        return AES.new(key, AES.MODE_CTR, counter=ctr).decrypt(ct)
    except ImportError:
        return subprocess.run(["openssl", "enc", "-d", "-aes-256-ctr", "-K", key.hex(),
                               "-iv", iv.hex()], input=ct, capture_output=True).stdout

def readable(b: bytes) -> bool:
    return len(b) > 0 and all(chr(c) in string.printable for c in b)

part1 = part2 = None
for line in tail:
    if re.fullmatch(r"[0-9a-f]{56}", line):                  # hex: IV(16) + ciphertext(12)
        blob = bytes.fromhex(line)
        out = aes_ctr_dec(blob[:16], blob[16:])
        tag = "REAL" if readable(out) else "decoy (noise)"
        print(f"[4] hex {line[:8]}... -> {out!r}  [{tag}]")
        if readable(out):
            part2 = out.decode()
    else:                                                     # base64
        txt = base64.b64decode(line).decode(errors="replace")
        tag = "REAL" if txt.startswith("GCDSTE{") else "decoy"
        print(f"[2] base64 {line[:12]}... -> {txt}  [{tag}]")
        if txt.startswith("GCDSTE{"):
            part1 = txt

# --- Step 5: LSBs, 1 colour byte out of `stride`, B,G,R order
px = np.array(Image.open(path).convert("RGB"))
flat = px[..., ::-1].reshape(-1)
bits = flat[start:start + 28 * 8 * stride:stride] & 1
blob = np.packbits(bits).tobytes()
part3 = aes_ctr_dec(blob[:16], blob[16:]).decode()
print(f"[5] LSB blob = {blob.hex()}\n    -> {part3}")

print("\nFLAG:", part1 + part2 + part3)
