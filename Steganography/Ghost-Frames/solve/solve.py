#!/usr/bin/env python3
"""GHOST FRAMES - solver (k4ir0s)
Usage: python3 solve.py ghost_frames.gif
Needs: pip install pillow numpy
"""
import sys
from PIL import Image
import numpy as np

gif = Image.open(sys.argv[1] if len(sys.argv) > 1 else "ghost_frames.gif")
print(f"{gif.n_frames} frames, size {gif.size}")

# 1) Find the "ghost" frames: their red LSB plane looks like random noise (~50% ones),
#    while in normal frames it is almost all zeros.
lsb = []
for i in range(gif.n_frames):
    gif.seek(i)
    red = np.array(gif.convert("RGB"))[:, :, 0]
    lsb.append(red & 1)
    print(f"frame {i+1:2d}: red-LSB ones = {(red & 1).mean():.3f}")

noisy = [i for i, p in enumerate(lsb) if 0.3 < p.mean() < 0.7]
print("noisy frames (1-based):", [i + 1 for i in noisy])

# 2) XOR the two shares -> the flag mask
a, b = noisy[:2]
flag = (lsb[a] ^ lsb[b]) * 255
Image.fromarray(flag.astype("uint8")).save("flag.png")
# also save each share (looks like noise on its own)
for name, idx in (("share_a.png", a), ("share_b.png", b)):
    Image.fromarray((lsb[idx] * 255).astype("uint8")).save(name)
print("saved flag.png -> open it and read the flag")
