import sys, struct, subprocess, json
sys.path.insert(0, '/tmp/mttl_fork_check/source')
from standalone.ota import transform_fwr

off = transform_fwr(open('/tmp/official-2.0.15.fwr', 'rb').read())
mine = transform_fwr(open('/tmp/mine-baseline.fwr', 'rb').read())
LOAD = 0x10006000
bo = off[16:16 + struct.unpack_from('<I', off, 0)[0]]
bm = mine[16:16 + struct.unpack_from('<I', mine, 0)[0]]

# asset symbols measured on my build (nm): name, address, size
assets = [('mttl_asset_1', 0x10007cf4, 0x09fd), ('mttl_asset_0', 0x10006bce, 0x1126),
          ('mttl_asset_2', 0x100086f1, 0x267f), ('mttl_asset_3', 0x1000adc0, 0x07c5)]
print('asset bytes in my image :', sum(s for _, _, s in assets))
print('decoded body sizes      : official %d, mine %d' % (len(bo), len(bm)))

for name, addr, size in assets:
    o = addr - LOAD
    blob = bm[o:o + size]
    p_self = bm.find(blob)
    p_off = bo.find(blob)
    print('%-14s size=%5d mine@0x%05X found: mine@%s official@%s' % (
        name, size, o, hex(p_self) if p_self >= 0 else 'no',
        hex(p_off - 16) if p_off >= 0 else 'NO -- blob differs from the release build'))

# does a gzip header appear at the same offset in both?
for name, addr, size in assets:
    o = addr - LOAD
    print('%s: mine hdr %s | official hdr %s' % (name, bm[o:o + 6].hex(), bo[o:o + 6].hex()))
