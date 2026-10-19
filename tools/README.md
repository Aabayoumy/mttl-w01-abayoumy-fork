# tools/ — how this fork is built, measured and compared

Scripts kept here so the work can be reproduced without the ad-hoc shell history.
They are *build/verification* helpers, not firmware sources: the firmware lives in
`patches/`, applied on top of an upstream release tag — `patches/README.md` records
which tag each series targets (`v2.0.17` is the live one).

## Where things run

| task | host |
|---|---|
| build the firmware | CT 106 `mttlbuild` — `ssh root@10.0.0.19` (on pve2, Debian 13) |
| host unit tests | either (Mac clang, or GCC 14 on CT 106) |
| flash a strip, snapshot evidence | Mac (needs LAN access to 10.0.0.x) |

## Build

```sh
# on CT 106
cd ~/mttl_fork_check/source
export MTTL_GCC_DIR=$HOME/mttl-tools/gcc
export MTTL_TERSER_ROOT=$HOME/mttl-tools/js/node_modules/terser
~/mttl-tools/venv/bin/python3 build.py            # ~12 s, all self-checks
~/mttl-tools/venv/bin/python3 /path/to/tools/measure-build.py
```

`measure-build.py` prints the four numbers that matter — `gap_to_msp_bytes`,
`fwr_bytes`, `fwr_sha256`, `build_id`, the round-trip/objcopy/OTA-field checks and
`ui_gzip_total` (cap 20,000). Run it **from the repo root of the source tree**.
The build does not clean its output dir: a failed build leaves the previous
`.fwr` in place, so always check `build_id` in `manifest.json`.

Since the 2.0.17 base the device serves **three** UI assets, not four:
`ota-live.js` is concatenated into `/live.js`, and `index.html` carries the inline
sequential loader. `ui_assets.json` therefore has three entries — the tools sum
whatever is in it, so nothing needs changing, but don't expect an `/ota-live.js`
line.

`build_id` is random (`secrets.token_hex(8)`) unless `MTTL_OTA_BUILD_ID` is set,
in which case that name is used verbatim everywhere the id appears
(`/api/firmware/status`, the OTA page, `manifest.json`). The shipped builds used
named ids, which is what makes them byte-reproducible:

```sh
# live series, based on upstream v2.0.17 (311663e)
MTTL_OTA_BUILD_ID=abayoumy-lock     ... build.py   # → 334,284 B, gap 764, 27 HA entities (current)
MTTL_OTA_BUILD_ID=abayoumy          ... build.py   # → 333,620 B, gap 1428, 26 HA entities (superseded)
# archived series, based on v2.0.15 (ebfb39d) — what the strips currently run
MTTL_OTA_BUILD_ID=abayoumy-notimers ... build.py   # → 333,372 B, gap 1676
MTTL_OTA_BUILD_ID=abayoumy          ... build.py   # → 334,300 B, gap 748
```

The OTA page only *shows* a build id that matches
`/^[0-9a-z][0-9a-z._-]{3,31}$/` (it was 16 hex before), so a named build still
appears in *Current build* and still drives the "Build verification" line. In the
2.0.17 UI the guard appears **three times** (`ui/ota-live.js`: the post-OTA
reconnect check, the `refreshStatus()` guard and the current-build label); the one
that remains as 16-hex matches the *uploaded filename* and is left alone. Rebase
time trap: upstream 2.0.17 reintroduced all three as 16-hex.

## Host unit tests

```sh
sh source/standalone/host_test/run.sh      # 249 checks, ~1 s, no cross toolchain
```

## Flash a strip (LivingRoom `10.0.0.53` is the low-risk one)

```sh
cd build-linux
curl -X POST http://10.0.0.53/api/firmware/upload \
     -H "Content-Type: application/x-mttl-fwr" \
     -H "Origin: http://10.0.0.53" -H "Expect:" \
     --max-time 90 \
     --data-binary @mttl-w01-2.0.17-abayoumy-lock.fwr
# → {"written":true,"activated":true,"rebooting":true}; back in ~45 s on the other slot
```

The upload is ~335 KB over Wi-Fi and takes **17–30 s**. `--max-time 20` silently
kills it mid-transfer (no response, and the strip stays on the old build — build
id unchanged, nothing half-written). Give it 90 s and be patient: the measured
2026-10-18 flashes took 26 s / 17 s to upload and ~45 s / ~40 s before the device
answered again. The **response body is the result**: an empty body (one such
attempt aborted at 75 s after the upload had already gone through) means *not
flashed* — confirm with `curl http://<ip>/api/firmware/status` and retry the exact
same command rather than assuming the worst.

Take the evidence before and after:

```sh
sh tools/strip-snapshot.sh build-linux/preflight-<name>-10.0.0.53  10.0.0.53
# ...flash...
sh tools/strip-snapshot.sh build-linux/postflight-<name>-10.0.0.53 10.0.0.53
diff <(jq -S . build-linux/preflight-<name>-10.0.0.53/config.json) \
     <(jq -S . build-linux/postflight-<name>-10.0.0.53/config.json)   # expect: no differences
```

`/api/config` returning byte-identical JSON before and after is the settings
survival check (v8 records are not reset by an OTA). HA entity counts come from
`ha-entities.json`. The web UI is served gzipped — use `curl --compressed`.

## Writing settings from a script (the lock, the timers)

`POST /api/config` does **not** take JSON: the body is the packed v8 settings
record (the layout in `firmware/settings.c:mttl_settings_pack`), sent with
`X-MTTL-Keep-Password: 1` so the stored Wi-Fi/MQTT credentials survive a write
that does not carry them. `tools/strip-config-write.py` reproduces the web UI's
own encoder (`ui/live.js:settingsBody`) starting from the device's current
`/api/config`, so only the fields you name change:

```sh
python3 tools/strip-config-write.py 10.0.0.53 --show                 # read only
python3 tools/strip-config-write.py 10.0.0.53 --lock 8               # lock outlet 4
python3 tools/strip-config-write.py 10.0.0.53 --timers 0,0,0,30      # 30 min on outlet 4
python3 tools/strip-config-write.py 10.0.0.53 --lock 0 --timers 0,0,0,0
```

Exit status 0 means the device read back what was asked for. **Exit 1 with
"NOT confirmed" is not necessarily a failure**: a timer aimed at a locked outlet
is dropped by `mttl_settings_unpack` normalisation, so the write succeeds while
that one field never lands (that is the point of the rule). A `400` from the POST
means the whole record was refused and nothing was written.

Two things that are easy to get wrong:

* **`/api/control` is 0-based**: `body = [channel, on]`, where channels `0..3` are
  outlets 1..4 and **`4` means ALL**. A refused single channel answers `429`;
  a refused ALL answers `200` with the locked outlets merely masked out of it.
* **The MQTT base topic uses the full 12-hex MAC, not the HA id**:
  `mttl/standalone/d8aa59d270aa/timer4/set` (see `ha_discovery.c:identity()`),
  while HA entities are `mttl_9d270aa_*`. The lock sensor's state topic is
  `<base>/lock`; the auto-off timer commands are `<base>/timerN/set` (`N` = 1..4,
  payload = minutes, `0` cancels, max 1440). A timer only runs while its outlet is
  on, so a test on an off outlet proves nothing about it being armed.

## Retiring an entity from Home Assistant (make it stick)

Deleting an entity in the HA UI never sticks on its own: the strip republishes its
entire discovery table on every reconnect. Remove the announcement from the
firmware first, then clear the retained config topic — an **empty retained payload**
on a discovery topic is how HA deletes an entity:

```sh
T=$(cat ~/.config/opencode/ha-token)
curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" \
  -d '{"topic":"homeassistant/number/mttl_9d270aa_timer1/config","payload":"","retain":true}' \
  http://10.0.0.11:8123/api/services/mqtt/publish
```

Do that for every topic the retired entity used
(`<component>/mttl_<short_id>_<key>/config`) **and** for any retained state topic the
old firmware left behind (`<prefix>/standalone/<mac>/<key>`) — nothing subscribes to
those once the entity is gone. Clear them **before** flashing the new firmware: the
strip's post-flash republish is then the proof that it no longer announces the
entity. Commit 5 (`6ff0735` on the 2.0.15 base, `9a05d83` on the live 2.0.17 line,
the timers) did exactly this: 16 config topics + 16 orphaned state topics, and the
captured HA ids went 68 → 52 (26 per strip).

Commit 6 (`cf02922`, the lock) is the other direction: index 26 is *appended* to
the table, so nothing has to be cleared — the existing 26 entities keep their ids,
topics and indices, and `sensor.mttl_<id>_lock` simply appears on the next
reconnect (a downgrade afterwards is the case that needs the manual clear, see
`HA-LIMITS-WIRING.md`).

## Comparing an image with an upstream release

The `.fwr` payload is XOR-encoded with a key derived from the first 16 bytes;
`standalone/ota.transform_fwr()` in the source tree is its own inverse, so a
released image can be decoded and compared.

```sh
cd <source tree root>                       # imports standalone.ota
python3 tools/fwr-compare.py                # expects /tmp/official-*.fwr + /tmp/mine-*.fwr
python3 tools/fwr-asset-compare.py          # searches our UI gzip blobs inside both images
```

What this established for `v2.0.15` (see `BUILD_LXC.md`, "Hazards"): the UI asset
blobs are byte-identical to the release build; the local image carries 16 extra
bytes of code early in the image; the release's firmware sources are identical to
`main` `ebfb39d` (only the READMEs changed) — so the delta is the Windows-vs-Linux
build of the pinned GCC 4.8.3, not our source or the UI pipeline.

## Reports

`ui-asset-report.py` prints the per-file gzip budget (largest first) together with
the raw byte length of the protection hint strings, which is what you need when
adding UI text: **1 byte of gzipped UI text costs 1 byte of code budget**, since
both live in `.ram_image2.text`.
