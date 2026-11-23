#!/usr/bin/env python3
"""HID and SEEK - solver (k4ir0s). Usage: python3 solve.py hid_and_seek_v2.pcapng"""
import struct, sys
from parse import packets, urb

LAYOUT_12 = [  # rev 12 (19:40) -> decoy, mouse on USB addr 7
 "r t m x q h d v 5 ,", "z - 2 b { u : o p k", "0 j ! i BACK 8 3 c ENT 9",
 "n f SHIFT l s / e SPC ? .", "1 7 w y a } g _ 4 6"]
LAYOUT_13 = [  # rev 13 (20:13) -> real one, mouse on USB addr 5
 "3 SPC a c 7 BACK ! 0 w j", "6 t 1 m SHIFT x 8 u k g", ", 2 b - : r 5 { d 4",
 "_ s i ? n q / h o p", "l } . f ENT z v 9 e y"]
def grid(L): return [r.split() for r in L]
ORIGIN, DX, DY, W, H = (40,102), 80, 78, 70, 66

def s8(b): return b-256 if b>127 else b

def decode(reports, layout):
    x=y=0; prev=0; out=[]; shift=False
    for r in reports:
        x+=s8(r[1]); y+=s8(r[2]); btn=r[0]&1
        if btn and not prev:                      # rising edge = one click
            col=(x-ORIGIN[0])//DX; row=(y-ORIGIN[1])//DY
            inx=(x-ORIGIN[0])-col*DX < W; iny=(y-ORIGIN[1])-row*DY < H
            if 0<=col<10 and 0<=row<5 and inx and iny:
                k=layout[row][col]
                if k=="SHIFT": shift=not shift
                elif k=="BACK": out and out.pop()
                elif k=="SPC": out.append(" ")
                elif k=="ENT": out.append("\n")
                else: out.append(k.upper() if shift else k)
        prev=btn
    return "".join(out)

if __name__=="__main__":
    pk=[urb(p) for p in packets(sys.argv[1])]
    for dev,lay,name in ((7,LAYOUT_12,"rev12"),(5,LAYOUT_13,"rev13")):
        reps=[u['data'] for u in pk if u['dev']==dev and u['ep']==0x81 and len(u['data'])==4]
        print(f"USB {dev} + {name}: {decode(reps,grid(lay))}")
