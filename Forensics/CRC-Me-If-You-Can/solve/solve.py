#!/usr/bin/env python3
"""CRC Me If You Can - GCDxGLORY CTF (author: K4ir0s)

Usage: python3 solve.py [folder with relay1.txt relay2.txt relay3.txt]
Standard library only.
"""
import re, sys
from collections import Counter
from pathlib import Path

PREFIX = "GCDxGLORY{"

def crc_msb(word, poly, init):
    r = init
    for byte in word.to_bytes(4, "big"):
        r ^= byte
        for _ in range(8):
            r = ((r << 1) ^ poly) & 0xFF if r & 0x80 else (r << 1) & 0xFF
    return r

def crc_lsb(word, poly, init):
    r = init
    for byte in word.to_bytes(4, "big"):
        r ^= byte
        for _ in range(8):
            r = (r >> 1) ^ poly if r & 1 else r >> 1
    return r

def ungray(g):
    i = 0
    while g:
        i ^= g
        g >>= 1
    return i

def load(path):
    """Keep lines whose first bit is 0, sort them by ungray(top byte)."""
    rows, decoys = {}, 0
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        m = re.fullmatch(r"([01]{32}) --> ([01]{8})", line.strip())
        if not m:
            raise ValueError("bad line: " + line)
        word, out = (int(x, 2) for x in m.groups())
        top = word >> 24
        if top & 0x80:          # decoy
            decoys += 1
            continue
        idx = ungray(top)
        if idx in rows:
            raise ValueError("duplicate position")
        rows[idx] = (word, out)
    if sorted(rows) != list(range(len(rows))):
        raise ValueError("missing positions")
    print(f"{path.name}: {len(rows)} positions, {decoys} decoys")
    return [rows[i] for i in range(len(rows))]

def candidates(relay, word, out, state):
    if relay == 3:                              # init=0, poly=state, xorout=letter
        vals = {crc_msb(word, state, 0) ^ out}
    else:                                       # init=state, poly=letter^state
        fn, xo = (crc_lsb, 0xFF) if relay == 2 else (crc_msb, 0)
        vals = {p ^ state for p in range(256) if (fn(word, p, state) ^ xo) == out}
    return {v for v in vals if 32 <= v < 127}

def decode(relay, rows, seed):
    state, res = seed, []
    for word, out in rows:
        res.append(candidates(relay, word, out, state))
        state = out                              # state = previous WRITTEN output
    return res

def main():
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "files"
    results = {}
    for relay in (1, 2, 3):
        rows = load(base / f"relay{relay}.txt")
        w0, o0 = rows[0]
        seeds = [s for s in range(256) if ord(PREFIX[0]) in candidates(relay, w0, o0, s)]
        print(f"Relay {relay} seeds compatible with 'G': {seeds}")
        if len(seeds) != 1:
            raise SystemExit("seed missing or ambiguous: analyse needed")
        results[relay] = decode(relay, rows, seeds[0])
    flag = ""
    for i in range(len(results[1])):
        votes = Counter(c for r in (1, 2, 3) for c in results[r][i])
        best = max(votes.values())
        win = [c for c, n in votes.items() if n == best]
        if len(win) != 1 or best < 2:
            raise SystemExit(f"vote ambiguous at position {i}")
        flag += chr(win[0])
    print("Flag:", flag)

if __name__ == "__main__":
    main()
