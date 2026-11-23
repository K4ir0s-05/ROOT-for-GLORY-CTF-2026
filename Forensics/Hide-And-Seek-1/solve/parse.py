import struct, collections
def packets(path):
    d=open(path,'rb').read(); off=0
    while off<len(d):
        bt,bl=struct.unpack_from('<II',d,off)
        if bt==6:
            cap=struct.unpack_from('<I',d,off+20)[0]
            yield d[off+28:off+28+cap]
        off+=bl
def urb(p):
    return dict(type=chr(p[8]),xfer=p[9],ep=p[10],dev=p[11],data=p[48:])
if __name__=='__main__':
    c=collections.Counter()
    for p in packets('/mnt/user-data/uploads/hid_and_seek_v2.pcapng'):
        u=urb(p); c[(u['dev'],hex(u['ep']),u['xfer'],len(u['data']))]+=1
    for k,v in sorted(c.items()): print(k,v)
