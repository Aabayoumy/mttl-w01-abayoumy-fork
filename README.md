# MTTL-W01 — per-outlet overcurrent protection fork (abayoumy)

**This repository contains my modifications only.** The upstream firmware project
[`af950833/mttl_w01_standalone`](https://github.com/af950833/mttl_w01_standalone) is **not**
redistributed here. Everything in this repo is either an annotated patch that applies on top of an
upstream release tag, documentation of those changes, a build/flash helper script, or a build of the
resulting tree.

| | |
|---|---|
| original source | <https://github.com/af950833/mttl_w01_standalone> |
| base this series applies to | upstream tag **`v2.0.17`** (commit `311663e`) |
| upstream licence | MIT © af950833 — see [`LICENSE`](LICENSE), third-party notices in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) |
| affiliation | none — not affiliated with, or endorsed by, LG U+ or the upstream author. Upstream does not support user modifications; questions about these patches belong here |

Device: LG U+ **MTTL-W01** smart multi-tap (ESP32, 4 switchable outlets + always-on USB,
device-local web UI, MQTT). The fork targets the upstream *standalone* firmware
(vendor backend removed, local dashboard + optional MQTT/Home Assistant).

## What the fork adds

| patch | commit | change |
|---|---|---|
| `0001-per-channel-current-isolation` | `fc6338c` | per-outlet current limits — a trip cuts **only** the outlet that is to blame, and only that outlet is cut |
| `0002-protection-trip-visibility` | `aa68f78` | protection state published to Home Assistant as one sensor (`channel_mask` + latched `reason`) |
| `0003-current-limit-every-outlet` | `c7e8a5e` | the current limit applies to every outlet, not one |
| `0004-ui-note-and-build-id` | `24a34dd` | protection note removed from the UI; OTA builds carry a named build id |
| `0005-timers-are-not-ha-entities` | `9a05d83` | timers stop being Home Assistant entities (34 → 26 entities); they stay device-local (web UI, buttons, `…/timerN/set`) |
| `0006-lock-every-command-path` | `cf02922` | per-outlet **lock**: every command path obeys it; HA lock sensor (26 → 27 entities) |

Settings records are version 8 (older records are normalised on load, not rejected); the settings
limit floor is 1000 mA; each trip is attributed to a specific outlet.

### What "locked" means (patch `0006`)

A locked outlet is not switched by **any** software path: physical buttons, the web UI (single and
ALL), Home Assistant/MQTT (single and ALL), the device-local auto-off timers and the schedules.
A refused *manual* command flashes that channel's LED three times; refusals coming from a timer or
schedule are silent. Lock state is published over MQTT and shown in HA. Two deliberate exceptions:

* **Protection is never blocked.** A trip cuts a locked outlet exactly as it cuts an unlocked one —
  the lock only stops commands, it must never stop safety.
* A locked outlet cannot have an auto-off timer (the timer would be a command path). The rule is
  applied on load, so a record written before the lock still loads cleanly.

Unlocking restores full control immediately — no reboot, and no queued command is replayed (the HA
command topics are not retained).

## Layout

| path | contents |
|---|---|
| `patches/` | the fork's commit series for upstream `v2.0.17`. `.patch` is `git format-patch` output (apply with `git am`); `.diff` is the same commit as a plain diff, for reading. `patches/README.md` documents each patch; `patches/2.0.15/` holds the earlier series based on the older 2.0.15 base (superseded, kept for reference) |
| `docs/` | `FEATURE-per-channel-current.md` — the full write-up (design, measurements, evidence); `HA-LIMITS-WIRING.md` — the Home Assistant entity contract; `REVIEW-per-channel-protection.md` — design review; `BUILD_LXC.md` — the build environment. Paths quoted inside these documents are relative to this repository's root |
| `tools/` | build/verify helpers (`measure-build.py`, `fwr-compare.py`, `fwr-asset-compare.py`, `sdk-overlays.py`, `ui-asset-report.py`, `strip-snapshot.sh`, `strip-config-write.py`) — see `tools/README.md` |
| `firmware/` | the latest compiled firmware, its manifest and `SHA256SUMS` |
| `LICENSE`, `THIRD_PARTY_NOTICES.md` | upstream MIT notice; third-party component notices carried over from upstream |

## Apply, build, flash

```sh
# 1. get the original source at the base tag
git clone https://github.com/af950833/mttl_w01_standalone.git
cd mttl_w01_standalone && git checkout v2.0.17

# 2. apply this series (resulting tree: 3d273c6257ac67ef1c61000d66a193ba69e180a4)
git am /path/to/mttl-w01-abayoumy-fork/patches/000[1-6]-*.patch

# 3. host unit tests (no hardware needed) — expect 249 checks, 0 failed
sh source/standalone/host_test/run.sh

# 4. build (needs the upstream builder + the vendor toolchain; see tools/README.md)
export MTTL_GCC_DIR=$HOME/mttl-tools/gcc
export MTTL_TERSER_ROOT=$HOME/mttl-tools/js/node_modules/terser
export MTTL_OTA_BUILD_ID=abayoumy-lock          # named id -> byte-reproducible build
~/mttl-tools/venv/bin/python3 build.py
```

Flash over the air on the local network (the strip swaps boot slots and reboots; uploads take
~20–30 s and it answers again ~20–40 s later):

```sh
curl -X POST http://<strip-ip>/api/firmware/upload \
  -H "Content-Type: application/x-mttl-fwr" -H "Origin: http://<strip-ip>" -H "Expect:" \
  --max-time 90 --data-binary @firmware/mttl-w01-2.0.17-abayoumy-lock.fwr
curl -s http://<strip-ip>/api/firmware/status      # expect build_id abayoumy-lock, version 2.0.17
```

## The build in `firmware/`

| | |
|---|---|
| file | `mttl-w01-2.0.17-abayoumy-lock.fwr` |
| size | 334,284 bytes |
| sha256 | `b65c0e30e1c9ffb641b406de5e652d4721fc02baa70fa3ce5cd1335b81d6067b` |
| build id / version | `abayoumy-lock` / `2.0.17` (base `v2.0.17`) |
| profile | `NETWORK_OTA_TEST_RAM_SETTINGS` (relay, OTA write, settings flash, watchdog enabled) |
| RAM gap to MSP | 764 bytes free (4,096-byte stack reserve) |
| UI assets | 3 assets, 19,429 bytes gzip total (cap 20,000) |

Only the latest build is published. Earlier ids (`abayoumy`, `abayoumy-notimers`) were intermediate
steps toward `abayoumy-lock`.

## Home Assistant

With MQTT discovery the fork contributes **27 entities per strip**: the four switches plus an ALL
switch, voltage/current/power/energy per outlet and totals, and two safety sensors —
`…_protection` (trip state, `channel_mask` + latched `reason`) and `…_lock` (lock mask). The entity
contract, topics and payloads are in [`docs/HA-LIMITS-WIRING.md`](docs/HA-LIMITS-WIRING.md).
Timers are intentionally **not** HA entities: they are configured on the device. MQTT is needed for
Home Assistant visibility/control only — protection, timers, schedules and the lock work on the
device without any broker.

## Verification

Each build was flashed and checked on two physical strips before being published: OTA slot swap,
byte-identical `/api/config` before/after, preserved energy counters, UI assets matching the
manifest, and behavioural tests of the trip isolation and the lock (buttons, web UI single/ALL,
HA single/ALL, timers, schedules — including a trip while the outlet was locked). Raw transcripts
are not included in this repository.

## Licence

The patches and documentation here are my modifications of MIT-licensed upstream work and are
released under the same terms — [`LICENSE`](LICENSE), copyright notice © 2026 af950833 retained.
Third-party components (SDK, compiler, runtime) are **not** relicensed by this repository: the
compiled firmware contains them, and their own terms continue to apply — see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
