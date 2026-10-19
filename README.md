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
| upstream licence | MIT © af950833 — see [`LICENSE`](LICENSE); third-party notices in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) |
| affiliation | none — not affiliated with, or endorsed by, LG U+ or the upstream author. Upstream does not support user modifications; questions about these patches belong here |

Device: LG U+ **MTTL-W01** smart multi-tap (four switchable outlets plus always-on USB, a
device-local web UI and optional MQTT/Home Assistant). This fork targets the upstream *standalone*
firmware — the vendor backend removed, the dashboard served by the device itself.

## Features added over the upstream base

What a strip running this fork does that an upstream `v2.0.17` strip does not:

1. **Per-outlet overcurrent protection.** The one current limit judges the total **and** every
   outlet; a per-outlet trip cuts **only** the outlet to blame instead of dropping all four relays.
2. **Trip attribution with an isolated cut.** `channel_mask` names the culprit outlet and `cut_mask`
   decides what is switched off — that outlet for a per-channel cause, all four for aggregate or
   unattributable causes (fail-safe). Over-temperature trips are attributed too.
3. **Trip visibility in Home Assistant.** `sensor.mttl_<short>_protection`: the cut mask as state,
   the latched `reason` as attribute, retained topic, republished after every reconnect.
4. **The per-outlet lock is authoritative.** It used to disable the physical button only; now a
   single gate in the command queue makes every path obey it — buttons, web UI (single and ALL),
   HA/MQTT (single and ALL), auto-off timers and schedules. A refused *manual* command flashes that
   channel's LED three times. Protection always still cuts.
5. **Lock visibility in Home Assistant.** `sensor.mttl_<short>_lock`: the locked outlet list as
   state, the mask nibble as attribute, retained.
6. **Timers stay on the device.** The eight auto-off timer entities per strip are no longer
   announced (34 → 26 entities); the timers themselves remain in the web UI, on the buttons and on
   MQTT `…/timerN/set`.
7. **Named, reproducible OTA builds.** `MTTL_OTA_BUILD_ID` replaces the random per-build id, and the
   OTA page accepts a name instead of only 16 hex characters.
8. **Settings record v8.** Stores the four `channel_current_ma` values; records written by older
   firmware migrate instead of being rejected, and a downgrade still reads the same record.
9. **One language: English only.** The Korean dictionary, every inline `ko`/`en` string pair and the
   header language selector are gone (§7); `text()` keeps its shape, a fresh settings record starts
   as English, and the device build now refuses Korean text in any asset.

All of this is RAM-budget work: the firmware text shares its region with the gzipped web UI, and the
linker refuses an image that crosses the reserved stack budget. The lock commit (§3) costs 664 B;
dropping the Korean dictionary and the inline pairs (§7) returned 3,390 B of the gzip budget, so the
published build leaves a **4,148 B** gap to the MSP limit. Per-object costs, the build log and every
measurement are in [`docs/FEATURE-per-channel-current.md`](docs/FEATURE-per-channel-current.md).

### Upstream vs this fork, side by side

| behaviour | upstream `v2.0.17` | this fork |
|---|---|---|
| over-current judgement | the aggregate total only | the total **and** each of the four outlets, from the same limit |
| a per-outlet trip | impossible — any trip cuts all four relays | cuts **only** the blamed outlet |
| over-temperature trip | unattributed → cuts all four | attributed to the channel → cuts that outlet only |
| aggregate current / power, or an unattributable cause | cuts all four | unchanged — fails safe to all four (`MTTL_PROTECTION_CUT_ALL` = `0x0f`) |
| automatic re-enable after a trip | none | none (upstream semantics kept) |
| trip visibility | device web UI only | `sensor.mttl_<short>_protection` (index 25) |
| padlock meaning | disables the **physical button** only (`control_enqueue` filtered its mask by `local==2`) | **every** command path is refused |
| lock feedback | a locked button press flashes that LED | any refused *manual* command flashes that LED 3×; timer and schedule refusals stay silent |
| lock visibility | none | `sensor.mttl_<short>_lock` (index 26) |
| locked outlet + an auto-off timer | allowed (the timer switched the outlet) | refused when saving, and normalised away when an older record is loaded |
| schedules that target a locked outlet | fire | kept as data, cannot fire while locked, work again after unlocking |
| timers announced to HA | 8 entities + retained state topics per strip | none — a device feature only |
| entities announced per strip | 34 | **27** (34 → 26 with the timers removed, +1 for the lock sensor) |
| OTA build id | random `secrets.token_hex(8)`; the OTA page accepted `/^[0-9a-f]{16}$/` only | `MTTL_OTA_BUILD_ID` used verbatim; the page accepts `/^[0-9a-z][0-9a-z._-]{3,31}$/` |
| protection-tab footer | *"No automatic ON or lock. Sensor failures show errors only. This does not replace hardware safety protection."* | removed — protection is implemented; the two-round policy hint above the form stays |
| settings record | v7 | **v8** = v7 + 4 × `u16 channel_current_ma` |
| dashboard language | Korean and English, switched by a header button and remembered in `localStorage` and in the settings record | **English only** — one dictionary, no button, no preference; the settings byte is still stored and reported |

### 1. Protection — one limit, per-outlet judgement, isolated cut

* **One limit covers everything.** The existing `protection.current` field in the device web UI
  (1000–16000 mA, floor 1000 mA) judges the total **and** each outlet. There is no separate
  per-outlet setting, no per-outlet UI and no extra enable bit: enabling the overcurrent limit
  (`0x02`) enables both judgements.
* **Confirmation is unchanged:** two consecutive over-limit rounds. A per-channel verdict is only
  possible on a round that actually read all four channels, so a half-populated round can never
  produce one.
* **What gets cut:**

  | cause | relays cut |
  |---|---|
  | per-channel current, one outlet | **that outlet only** |
  | per-channel temperature, one outlet | **that outlet only** |
  | aggregate current | all four |
  | aggregate power | all four |
  | per-channel **and** aggregate in the same round | the attributed outlet(s) only — with one limit for both judgements, an outlet over the limit also takes the total over it in the same round, so this is one event, not two |
  | unattributable / unknown | all four (fail-safe) |

* `reason` keeps its original bit meaning (1 temperature / 2 current / 4 power) so the web UI, MQTT
  and `/api/status` readers keep working. `channel_mask` says *which* outlet caused a trip;
  `cut_mask` says which relays to switch off.
* **No automatic re-enable** after a trip — upstream semantics (priority ALL-OFF command, no
  persistent latch) are preserved.
* **Settings:** the v8 record carries four `channel_current_ma` values. The firmware judges each
  channel against `current_ma` and never reads the array, and the web UI mirrors the single limit
  into all four on save — so the stored record stays self-consistent, `/api/config` keeps reporting
  `channel_current` for older readers, and a downgrade to a pre-fork build reads the mirrored
  values as its per-outlet limits.

### 2. Trip visibility in Home Assistant (`patches/0002-…`)

| | |
|---|---|
| entity | `sensor.mttl_<short>_protection` — "… Protection", `entity_category: diagnostic` |
| index | `MTTL_HA_TRIP_INDEX` = **25** (the table holds 27 entries) |
| state | cut mask of the outlets that are **still off**: bit 0 = outlet 1 … bit 3 = outlet 4; `0` = nothing cut |
| attribute | `reason` — cause of the last trip, latched: 1 temperature / 2 current / 4 power |
| topic | `<base>/protection`, **retained** (a cut is a state, not a sample that can go stale) |
| payload | `{"mask":N,"reason":R}`; discovery uses `val_tpl: {{ value_json.mask }}` with `json_attr_t` on the same topic |
| published | on change of mask or cause, plus once after every (re)connect — it rides the existing 500 ms sensor rotation, so a cut reaches HA in about a second |

Design points that matter for automations:

* The mask counts only the outlets the last trip cut that are **still off**. Restoring power returns
  it to `0`, which re-arms the entity — so a repeat trip notifies again. A latched "tripped" flag
  would notify once in the device's lifetime and never again.
* Outlet names are deliberately not in the payload: names are free-form strings up to 64 bytes (two
  outlets on my strip are both named `SBar`). Names are resolved on the HA side from the switch
  entities, so renaming an outlet keeps any template correct.
* `reason` is latched from the last trip — ignore it whenever the state is `0`.
* A ready-to-paste notification automation is in
  [`docs/HA-LIMITS-WIRING.md`](docs/HA-LIMITS-WIRING.md) (verified for all mask × cause
  combinations). It is **not** installed in my HA config, so nothing notifies by itself.

### 3. The per-outlet lock is authoritative (`patches/0006-…`)

**What was wrong upstream.** `control_enqueue()` — the single queue every command goes through —
filtered its channel mask by `local==2`:

```c
mask = local==2 ? (15u & ~device.settings.button_lock) : 15u;
```

`local` is the command's origin: 2 = physical buttons, 0 = web UI and HA/MQTT, 1 = the auto-off
timers and the schedules. So only a button press (or the ALL button) consulted the padlock — the
web-UI toggle, the HA switch, an HA "all on/off", a timer expiry and a schedule rule all switched a
locked outlet anyway. Protection was already outside the queue and unaffected.

**Now** the mask is unconditional (`15u & ~button_lock` for every origin), and the resulting state
is visible and consistent:

* A locked outlet is refused on **every** path. An ALL command (channel 4) then applies to the
  unlocked outlets only, and a fully locked strip refuses every command.
* A refused **manual** command (web UI, HA/MQTT — `local==0`) flashes that channel's LED three
  times — the same feedback a locked button press already gave. Refusals coming from a timer or a
  schedule stay silent: they retry on every worker pass and would blink forever.
* **A locked outlet cannot carry an auto-off timer**, because the timer is itself a command path:
  `mttl_settings_valid` refuses such a record, and `mttl_settings_unpack` clears a timer found
  behind a lock bit — so a record written by the previous firmware still loads instead of being
  rejected.
* **Schedules stay data.** A rule that targets a locked outlet is neither refused nor deleted: it
  simply cannot fire while the lock is set, and works again after unlocking. Refusing it at save
  time would force deleting and re-creating rules around every lock.
* **Protection is never blocked.** Protection does not go through the command queue, so a trip cuts
  a locked outlet exactly as it cuts an unlocked one.
* The web UI follows: the padlock tooltip says what the lock really does, a locked outlet's toggle
  is disabled, the timer editor treats a locked channel like a schedule conflict (*"Locked outlet.
  Unlock it before registering a timer."*, inputs disabled, value forced to 0), and the scheduler
  hint notes that a schedule does not switch a locked outlet either.

| lock in Home Assistant | |
|---|---|
| entity | `sensor.mttl_<short>_lock` — "… Lock", `entity_category: diagnostic` |
| index | `MTTL_HA_LOCK_INDEX` = **26**, appended after the trip sensor |
| state | the locked outlet list as text: `1`, `1,3`, or `none` when nothing is locked |
| attribute | `mask` — the same nibble the device stores in `button_lock` (bit 0 = outlet 1 … bit 3 = outlet 4) |
| topic | `<base>/lock`, **retained** (it describes a setting, not a sample) |
| payload | `{"mask":N,"locked":"1,3"}` / `{"mask":0,"locked":"none"}` |
| published | on change, plus once after every (re)connect — the app struct starts at `0xff`, so a reconnect always republishes |

Behaviour notes:

* **Refused commands need no special handling in HA**: the switches are announced with
  `optimistic: false`, so Home Assistant reverts the entity to the device's real state on its own.
  The command topics are not retained, so nothing is replayed when the outlet is unlocked.
* Unlocking restores full control immediately — no reboot, nothing queued.
* Reading it in a template: `states('sensor.mttl_9d270aa_lock') != 'none'` is usually easiest; for
  the nibble, `state_attr('sensor.mttl_<short>_lock','mask')` needs the `// 2 ** i` idiom because
  Jinja has no bitwise operators.
* A locked outlet is never a dead end — the lock never blocks *configuration*: unlock it (web UI,
  HA, or the button) and switch it on. My BedRoom strip came up with its `PVE1` outlet already
  locked on the *old* firmware and the new build simply read that setting back and published it.
* **Downgrade caveat**: the config topic is retained, so flashing back to a pre-fork build leaves a
  stale `sensor.mttl_<short>_lock` entity in HA that never updates again. Clear
  `homeassistant/sensor/mttl_<short>_lock/config` and `<base>/lock` if that happens.

### 4. Timers are a device feature, not HA entities (`patches/0005-…`)

Deleting the timer entities in HA alone never sticks — the strip re-announces all eight after every
reconnect — so the announcement is gone from the firmware: the `index>=25` / `index>=29` discovery
branches are deleted and the two state publications that existed only to feed them (`…/timerN`,
`…/timer_remainingN`) are gone with the fields behind them. `MTTL_HA_ENTITIES` went 34 → 26 and the
trip sensor became the last index.

What deliberately stays: the timers themselves — the local timer logic, the device web UI, the
buttons and the MQTT `…/timerN/set` command path. They are simply no longer *announced* to Home
Assistant. The host test asserts the whole table: 26 entries, no `number` component anywhere, no
topic containing `timer`, and a refusal at `MTTL_HA_ENTITIES` and beyond.

### 5. Named, reproducible OTA builds (`patches/0004-…`)

`MTTL_OTA_BUILD_ID=<name>` is used verbatim wherever the build id appears, in place of the random
`secrets.token_hex(8)` (leaving it unset keeps the old behaviour). The OTA page's build-id guard was
relaxed from `/^[0-9a-f]{16}$/` to `/^[0-9a-z][0-9a-z._-]{3,31}$/`, so a named build still appears
as *Current build* and still drives the "Build verification: OK / NOT MATCHED" line after an upload.
`/api/firmware/status` reports the name as-is. Named ids are what make these builds
byte-reproducible: two builds of the same tree produce the same sha256.

The same commit removed the protection tab's closing note (*"No automatic ON or lock. Sensor
failures show errors only. This does not replace hardware safety protection."* and its Korean
counterpart): local protection is implemented, so the sentence was misleading. The hint above the
form — the two-round policy, the mask/reason semantics and the ~10 s channel sampling — stays.

### 6. Settings record v8

v8 = v7 + 4 × `u16 channel_current_ma`: tail 66 → 74, `needed` 82 → 90, packed record 118 B, 156 B
of flash including overhead. A v4–v7 record **migrates with 16,000 mA defaults** instead of being
rejected. The fork deliberately keeps the record self-consistent: it never reads the array when
deciding, and the web UI mirrors the single limit into all four values on save — so the stored
record, `/api/config` and a downgraded firmware all agree.

### 7. One language: English only (`patches/0007-…`)

The dashboard shipped two dictionaries and a header button that switched between them: the choice
lived in `localStorage`, in the `language` byte of the settings record, in the OTA page's own word
list and in every string written as a `ko`/`en` pair. The strip is used in one language, so the
mechanism is gone.

| | |
|---|---|
| dictionary | `ui/i18n.js` keeps a single `en` table. `text(language,key,args)` keeps its three-argument shape, so every call site and the device-side compact builder are unchanged; the language argument is ignored |
| inline strings | the KO arm of every `cond ? en : ko`, the second argument of every `text(ko,en)` / `logEvent(ko,en)` helper and the helpers themselves are deleted; the browser-session log keeps one message per row |
| static fallbacks | `index.html`, `ota-test.html` and the OTA panel that `build_assets.py` injects are English; the `#language` button and its CSS rule are gone |
| OTA page | a single English word list, no re-render on a language toggle |
| build guard | the device build refuses any gzipped asset containing a Hangul character, next to the existing preview-text denylist, and the device dictionary is built as a single-language table |
| settings record | **v8 unchanged**: `mttl_settings_default()` writes `language=1` (English) for a fresh record, a stored `0` stays valid and simply renders English, the dashboard writes `1` whenever it saves, and the device keeps reporting the byte in `/api/config` |
| RAM | the Korean dictionary and the inline pairs were 3,390 B of the 20,000 B gzip budget (19,429 → 16,039), which is what lifted the link gap from 764 B to 4,148 B |

Protection, the lock, the timers, the schedules and the HA entity list are untouched — 27 entities
per strip before and after — and the three dashboard/OTA node tests were updated to the English
wording.

### Not built: Home Assistant control of the limits — measured, does not fit

Four MQTT `number` entities (read *and* write the limits from HA) were implemented and measured: the
discovery-and-command version costs ≈1,004 B against the ≈660 B gap that existed at the time, which
pushes `__HeapLimit` past the reserved MSP budget — the linker rejects the image outright
(`ld: application overlaps reserved MSP budget`). The work is kept as
[`patches/wip-0002-ha-limit-entities-does-not-fit.patch`](patches/wip-0002-ha-limit-entities-does-not-fit.patch)
on branch `wip/ha-limit-entities`. The numbers, the alternatives and the zero-firmware-cost REST
sensor variant are in [`docs/HA-LIMITS-WIRING.md`](docs/HA-LIMITS-WIRING.md). The decision: keep
limit *changes* in the device web UI (which shows the temperature, current and power limits together)
and spend the RAM on what HA is genuinely good at — knowing that something was cut, and knowing what
is locked.

### Deliberately unchanged from upstream

No automatic re-enable after a trip; fail-safe all-four cut for unattributable causes; the aggregate
power limit is untouched (a per-channel *power* limit would be the same judgement as per-channel
current at a fixed voltage, for double the storage, code and UI); timers only run while their outlet
is on; HTTP and MQTT are unauthenticated on the LAN, so the strip belongs on a trusted VLAN/SSID.

## Patches

Seven commits on top of upstream `v2.0.17`. `.patch` is `git format-patch` output (apply with
`git am`), `.diff` is the same commit as a plain diff for reading.

| patch | commit | feature |
|---|---|---|
| `0001-per-channel-current-isolation` | `fc6338c` | per-outlet current limits; a trip cuts only the blamed outlet (§1) |
| `0002-protection-trip-visibility` | `aa68f78` | the HA protection sensor, index 25 (§2) |
| `0003-current-limit-every-outlet` | `c7e8a5e` | one limit applies to every outlet, not one (§1) |
| `0004-ui-note-and-build-id` | `24a34dd` | protection note off, named OTA build ids (§5) |
| `0005-timers-are-not-ha-entities` | `9a05d83` | timers stop being HA entities, 34 → 26 (§4) |
| `0006-lock-every-command-path` | `cf02922` | the lock gates every command path; HA lock sensor, 26 → 27 (§3) |
| `0007-english-only-dashboard` | `f88dd17` | English-only dashboard; Korean dictionary, inline `ko`/`en` pairs and the language selector removed (§7) |

`patches/README.md` documents each patch; `patches/2.0.15/` holds the earlier series based on the
older 2.0.15 base (superseded, kept for reference).

## Layout

| path | contents |
|---|---|
| `patches/` | the fork's commit series for upstream `v2.0.17` — see the table above |
| `docs/` | `FEATURE-per-channel-current.md` — the full write-up (design, measurements, every on-hardware verification run); `HA-LIMITS-WIRING.md` — the Home Assistant entity contract, template recipes, RAM options; `REVIEW-per-channel-protection.md` — design review; `BUILD_LXC.md` — the build environment. Paths quoted inside these documents are relative to this repository's root |
| `tools/` | build/verify helpers (`measure-build.py`, `fwr-compare.py`, `fwr-asset-compare.py`, `sdk-overlays.py`, `ui-asset-report.py`, `strip-snapshot.sh`, `strip-config-write.py`) — see `tools/README.md` |
| `firmware/` | the latest compiled firmware, its manifest and `SHA256SUMS` |
| `LICENSE`, `THIRD_PARTY_NOTICES.md` | upstream MIT notice; third-party component notices carried over from upstream |

## Apply, build, flash

```sh
# 1. get the original source at the base tag
git clone https://github.com/af950833/mttl_w01_standalone.git
cd mttl_w01_standalone && git checkout v2.0.17

# 2. apply this series (resulting tree: 49c3ef130d6cf8ff8276f72d5b79bdd229f89703)
git am /path/to/mttl-w01-abayoumy-fork/patches/000[1-7]-*.patch

# 3. host unit tests (no hardware needed) — expect 249 checks, 0 failed
sh source/standalone/host_test/run.sh

# 4. build (needs the upstream builder and the vendor toolchain; see tools/README.md)
export MTTL_GCC_DIR=$HOME/mttl-tools/gcc
export MTTL_TERSER_ROOT=$HOME/mttl-tools/js/node_modules/terser
export MTTL_OTA_BUILD_ID=abayoumy-en            # named id -> byte-reproducible build
~/mttl-tools/venv/bin/python3 build.py
```

Flash over the air on the local network (the strip swaps boot slots and reboots; the upload takes
~20–30 s and it answers again ~20–40 s later):

```sh
curl -X POST http://<strip-ip>/api/firmware/upload \
  -H "Content-Type: application/x-mttl-fwr" -H "Origin: http://<strip-ip>" -H "Expect:" \
  --max-time 90 --data-binary @firmware/mttl-w01-2.0.17-abayoumy-en.fwr
curl -s http://<strip-ip>/api/firmware/status      # expect build_id abayoumy-en, version 2.0.17
```

## The build in `firmware/`

| | |
|---|---|
| file | `mttl-w01-2.0.17-abayoumy-en.fwr` |
| size | 330,900 bytes |
| sha256 | `afb5fd1b0e32a6ce61d22e47b3a5715e0f75fc5818970c28b0776f6d39770fcb` |
| build id / version | `abayoumy-en` / `2.0.17` (base `v2.0.17`) |
| profile | `NETWORK_OTA_TEST_RAM_SETTINGS` (relay, OTA write, settings flash, watchdog enabled) |
| RAM gap to MSP | 4,148 bytes free (4,096-byte stack reserve) |
| UI assets | 3 assets, 16,039 bytes gzip total (cap 20,000) — one English dictionary |

Only the latest build is published. The earlier ids (`abayoumy`, `abayoumy-notimers`,
`abayoumy-lock`) were intermediate steps on the way to `abayoumy-en`; their logs and manifests are
not in this repo. `abayoumy-en` is byte-reproducible from the patch series, host-verified and
flashed to the LivingRoom strip (`10.0.0.53`) on 2026-10-19; the BedRoom strip (`10.0.0.54`, which
powers the Proxmox host through its `PVE1` outlet) still runs `abayoumy-lock` and is flashed
deliberately, as a separate step. `abayoumy-en` is a superset of that build (protection, lock,
timers) plus the English-only dashboard.

## Home Assistant

With MQTT discovery, a strip running this build announces **27 entities**: the four switches plus an
ALL switch, voltage/current/power/energy per outlet and totals, and the two safety sensors —
`…_protection` (trip state: `channel_mask` as state, latched `reason` as attribute) and `…_lock`
(locked outlet list as state, mask as attribute). Entity contract, topics, payloads and template
recipes: [`docs/HA-LIMITS-WIRING.md`](docs/HA-LIMITS-WIRING.md).

Timers are intentionally not announced (§4). MQTT is needed for Home Assistant visibility and
control only — protection, timers, schedules and the lock all work on the device without a broker.

## Verification

The builds that were flashed were checked on physical strips before being published: OTA slot swap,
byte-identical `/api/config` before and after, preserved energy counters, UI assets matching the
manifest, every announced entity present in HA, and behavioural tests of the trip isolation, the
lock (buttons, web UI single/ALL, HA single/ALL, timers, schedules) and the timer rule. The host
unit suite passes **249 checks / 0 failed**, the three dashboard/OTA node tests pass, and applying
the published patches to a pristine upstream `v2.0.17` reproduces tree
`49c3ef130d6cf8ff8276f72d5b79bdd229f89703` exactly — the tree the firmware here was built from, with
the build refusing Korean text in any gzipped asset. `abayoumy-en` was then flashed to the
LivingRoom strip (`10.0.0.53`) on 2026-10-19: OTA slot swap, `/api/config` byte-identical, the three
served UI assets byte-identical to the built ones with **zero Hangul**, and 27 entities still
announcing. The BedRoom strip (`10.0.0.54`) still runs `abayoumy-lock` — it powers the Proxmox host
through its `PVE1` outlet, so it is flashed deliberately as a separate step. Raw transcripts and
photos are not included in this repository.

## Licence

The patches and documentation here are my modifications of MIT-licensed upstream work and are
released under the same terms — [`LICENSE`](LICENSE), with the copyright notice © 2026 af950833
retained. Third-party components (SDK, compiler, runtime) are **not** relicensed by this repository:
the compiled firmware contains them and their own terms continue to apply — see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
