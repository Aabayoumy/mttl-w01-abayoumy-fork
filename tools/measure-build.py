import json
m=json.load(open('standalone/results/network-ota-test/manifest.json'))
f=[x for x in m['files'] if x['path'].endswith('.fwr')][0]
print('gap_to_msp_bytes :',m['static_gap_to_msp_bytes'])
print('fwr_bytes        :',f['bytes'])
print('fwr_sha256       :',f['sha256'])
print('build_id         :',m['build_id'])
print('roundtrip        :',m['bin_fwr_roundtrip'],'| objcopy match:',m['objcopy_byte_match'],'| native ota field:',m['native_ota_hardware_field_verified'])
a=json.load(open('standalone/results/network-ota-test/sdk/ui_assets.json'))
print('ui_gzip_total    :',sum(x['gzip_bytes'] for x in a),'/ 20000')
