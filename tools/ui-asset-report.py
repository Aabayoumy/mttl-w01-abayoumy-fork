import json, re
a = json.load(open('standalone/results/network-ota-test/sdk/ui_assets.json'))
tot = 0
for x in sorted(a, key=lambda y: -y['gzip_bytes']):
    name = x.get('path', x.get('name', '?')).split('/')[-1]
    print('%-26s raw=%6d gzip=%6d' % (name, x.get('raw_bytes', 0), x['gzip_bytes']))
    tot += x['gzip_bytes']
print('total gzip:', tot)
s = open('standalone/ui/i18n.js', encoding='utf-8').read()
for m in re.finditer(r"protectionHint:'(.*?)',", s):
    t = m.group(1)
    print('protectionHint raw bytes:', len(t.encode('utf-8')), '|', t[:100])
