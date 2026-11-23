#!/usr/bin/env python3
"""Wach Katshof Kolchi (cv_b0ub0u.pdf) - solver by k4ir0s
Usage: python3 solve.py cv_b0ub0u.pdf [TOKEN]
       TOKEN = the 5 faint digits you read on the page (default 35276)
Needs: pip install pypdf cryptography

The syllable lists A and B (LEX[16*i+j] = A[i] + B[j]) come from spec.txt,
which was given to the players.
"""
import re, sys, hashlib, struct, collections
from pypdf import PdfReader
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

A = "ba ze mo ki sa lu ta re ha ni do fa gu ya wa che".split()
B = "rak lim dan bou fel mat zar ssa hib nou qar jed tir wan ley kar".split()
LEX = [a + b for a in A for b in B]          # 256 words

path = sys.argv[1] if len(sys.argv) > 1 else "cv_b0ub0u.pdf"
token = sys.argv[2] if len(sys.argv) > 2 else "35276"
pdf = open(path, "rb").read()
reader = PdfReader(path)

def leet(s):                      # a->4, e->1, o->0 (i stays, 3 is taken by "ain")
    return s.replace("a", "4").replace("e", "1").replace("o", "0")

# 1) bait key: zero-width characters at the end of /Keywords
kw = reader.metadata["/Keywords"]
bits = "".join("1" if c == "\u200c" else "0" for c in kw if c in "\u200b\u200c")
bait = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
print("bait key (decoy):", bait.decode())

# 2) comments in the (decompressed) page content stream, grouped by tag
content = reader.pages[0].get_contents().get_data().decode("latin1")
by = collections.defaultdict(list)
for line in content.splitlines():
    m = re.match(r"%\s+(\w+)\s+(\S+)", line)
    if m:
        by[m.group(1)].append(m.group(2))

# 3) unreferenced objects of 45 bytes (29 ct + 16 GCM tag)
referenced = {int(x) for x in re.findall(rb"(\d+) 0 R", pdf)}
blobs = {}
for m in re.finditer(rb"(\d+) 0 obj\s*<< /Length 45 >>\s*stream\n(.{45})\nendstream", pdf, re.S):
    if int(m.group(1)) not in referenced:
        blobs[int(m.group(1))] = m.group(2)

def attempt(key: bytes, tag: str):
    # keyword base32 alphabet: key characters first, then the rest in order
    std = "abcdefghijklmnopqrstuvwxyz234567"
    seen = []
    for c in key.decode():
        if c in std and c not in seen:
            seen.append(c)
    alpha = "".join(seen) + "".join(c for c in std if c not in seen)
    # 5 bits per symbol -> 32 bytes: ct(4) | salt(16) | nonce(12)
    bits = "".join(format(alpha.index(c), "05b") for c in "".join(by[tag]))
    car = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits) - 7, 8))
    ct, salt, nonce = car[:4], car[4:20], car[20:32]
    # honey cipher: 4 bytes -> 4 words
    ks = hashlib.sha256(key + b"|honey|" + struct.pack(">I", 0)).digest()[:4]
    words = []
    for c, k in zip(ct, ks):
        words.append(LEX[(c - k) % 256])
    pw = hashlib.scrypt("-".join(words).encode(), salt=salt, n=2**16, r=8, p=1,
                        maxmem=2**28, dklen=32)
    for n, blob in sorted(blobs.items()):
        try:
            return AESGCM(pw).decrypt(nonce, blob, None).decode(), f"words={words} object={n}"
        except Exception:
            pass
    return None, f"words={words}, no object opened"

# decoy chain (bait key + 'ctm' tag), then the real chain
res, info = attempt(bait, "ctm");   print("DECOY :", res, "|", info)
real_key = (leet("lebra") + "_" + token).encode()
print("real key:", real_key.decode())
res, info = attempt(real_key, "cid"); print("REAL  :", res, "|", info)
