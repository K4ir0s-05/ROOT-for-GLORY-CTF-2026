#!/usr/bin/env python3
"""Ait Lmojawharat solver - GCDSTE CTF: ROOTfor GLORY (author: K4ir0s)

Usage : python3 solve.py [../files/k4ir0s_C0ll3ct10n.pptm]
Needs : pip install cryptography Pillow numpy
"""
import base64, hashlib, re, sys
import xml.etree.ElementTree as ET
from io import BytesIO
from zipfile import ZipFile
import numpy as np
from PIL import Image
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def unveil(data, prev_value):                    # XOR avec sha256 de la coupe precedente
    k = hashlib.sha256(prev_value.encode()).digest()
    return bytes(a ^ b for a, b in zip(data, k)).decode()

def hex_cuts(z):                                 # toutes les coupes hors cadre (x negatif)
    out = []
    for n in sorted(x for x in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", x)):
        s = z.read(n).decode()
        for m in re.finditer(r'<a:off x="-\d+".*?<a:t>CUT / engraver ticks: ([0-9A-F]+)</a:t>', s, re.S):
            out.append((n, bytes.fromhex(m.group(1)).decode()))
    return out

def lsb_blue_text(png_bytes):                    # canal bleu, bit de poids faible, MSB-first, ligne par ligne
    a = np.array(Image.open(BytesIO(png_bytes)).convert("RGB"))
    bits = (a[:, :, 2].reshape(-1) & 1)[:8 * 200]
    raw = np.packbits(bits).tobytes().split(b"\x00")[0]
    return raw.decode()

def main(path):
    z = ZipFile(path)
    cuts = hex_cuts(z)
    print("[+] Off-frame cuts :", cuts)
    # the real cut is the one whose seal number is <= 3 (the seal broke in 3 pieces)
    seal2 = [v.split("=")[1] for n, v in cuts if v.startswith("seal.") and int(v[5]) <= 3][0]
    ledger = re.search(r"ledger64=([A-Za-z0-9+/=]+)", z.read("docProps/custom.xml").decode()).group(1)
    s1 = unveil(base64.b64decode(ledger), seal2).split("=")[1]
    png = z.read("ppt/media/image4.png")
    payload = lsb_blue_text(png)
    assert payload.startswith("K4:")
    s3 = unveil(base64.b64decode(payload[3:]), s1).split("=")[1]
    print("[+] seal.1 =", s1, "| seal.2 =", seal2, "| seal.3 =", s3)
    password = "|".join([s1, seal2, s3])             # ordre = numero de sceau
    salt = hashlib.sha256(z.read("docProps/thumbnail.jpeg")).digest()[:16]
    key = hashlib.scrypt(password.encode(), salt=salt, n=2**18, r=8, p=1, dklen=32, maxmem=1024 * 1024 * 1024)
    inv = ET.fromstring(z.read("customXml/item1.xml"))
    for g in inv:
        blob = base64.b64decode(g.attrib["cert"])
        try:
            print("[OK]", g.attrib["id"], AESGCM(key).decrypt(blob[:12], blob[12:], b"K4-INV07").rstrip(b"\x00").decode())
        except InvalidTag:
            pass

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../files/k4ir0s_C0ll3ct10n.pptm")
