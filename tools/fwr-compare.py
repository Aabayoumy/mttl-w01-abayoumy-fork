import sys, struct
sys.path.insert(0, '/tmp/mttl_fork_check/source')
from standalone.ota import transform_fwr, inspect_image

off = open('/tmp/official-2.0.15.fwr', 'rb').read()
mine = open('/tmp/mine-baseline.fwr', 'rb').read()
print('encoded sizes : official %d, mine %d' % (len(off), len(mine)))
io, im = inspect_image(off), inspect_image(mine)
print('official info :', io)
print('mine info     :', im)

ro, rm = transform_fwr(off), transform_fwr(mine)
print('decode check  : official %s, mine %s' % (io.decoded == ro, im.decoded == rm))
lo, lm = struct.unpack_from('<I', ro, 0)[0], struct.unpack_from('<I', rm, 0)[0]
print('body sizes    : official %d, mine %d (delta %+d)' % (lo, lm, lm - lo))
print('load addrs    : official 0x%08X, mine 0x%08X' % (
    struct.unpack_from('<I', ro, 4)[0], struct.unpack_from('<I', rm, 4)[0]))

bo, bm = ro[16:16 + lo], rm[16:16 + lm]
print('checksum      : official 0x%08X, mine 0x%08X' % (
    struct.unpack_from('<I', ro, 16 + lo)[0], struct.unpack_from('<I', rm, 16 + lm)[0]))

# longest common prefix / suffix
n = min(len(bo), len(bm))
p = 0
while p < n and bo[p] == bm[p]:
    p += 1
s = 0
while s < n - p and bo[len(bo) - 1 - s] == bm[len(bm) - 1 - s]:
    s += 1
print('\ncommon prefix : %d bytes (0x%X)' % (p, p))
print('common suffix : %d bytes' % s)

mo, mm = bo[p:len(bo) - s], bm[p:len(bm) - s]
print('middle        : official %d bytes, mine %d bytes' % (len(mo), len(mm)))
print('official mid  :', mo[:64].hex(' '))
print('mine mid      :', mm[:64].hex(' '))

# locate the insertion: after the differing head, do the tails realign?
for skip in range(0, 80):
    if mm[skip:skip + 64] and mo[:64] == mm[skip:skip + 64]:
        print('\nmine has %d extra byte(s) at offset %d before the streams realign' % (skip, p))
        break
else:
    print('\nno simple insertion offset found in the first 80 bytes')

# print the differing head as ascii-ish
print('\nofficial head ascii:', ''.join(chr(c) if 32 <= c < 127 else '.' for c in mo[:48]))
print('mine     head ascii:', ''.join(chr(c) if 32 <= c < 127 else '.' for c in mm[:48]))
