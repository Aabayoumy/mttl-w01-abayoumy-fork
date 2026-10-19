# Feature: per-channel overcurrent protection, trips isolated to the blamed outlet

Status: **built, host-verified (249 checks), the lock build flashed to both
strips** — LivingRoom `10.0.0.53` and BedRoom `10.0.0.54` (upgraded from `2.0.14`
in stages), both now reporting the build id **`abayoumy-lock`** on upstream
`2.0.17` — with settings round-trip verified and **no spurious trip on either
strip**. The per-outlet limit is now **automatic** — one current limit covers the
strip and every outlet — and that behaviour is **live** on both strips; the trip
*transition* itself has not been exercised on hardware yet. The HA trip-visibility
entity is live on both strips and reporting `0` (nothing cut). The auto-off timers
are **no longer announced to Home Assistant**, and the per-outlet **lock is now
authoritative and visible**: 27 entities per strip (was 34), zero timer entities.

**Rebased onto upstream `2.0.17`** (`311663e`) on 2026-10-19 — see the
*Rebase onto upstream 2.0.17* section. The branch sits on the release whose only
real change is the dashboard-loading / post-OTA-reconnect fix, and the resulting
build **`abayoumy`** (gap **1428 B**, 333,620 B, UI gzip 19,168 B) was built and
host-verified.

**The lock is now authoritative** (`cf02922`, 2026-10-19) — see *Commit 6: the
lock gates every command path*. A locked outlet is no longer switched by the web
UI, by Home Assistant (single outlet or ALL), by its own auto-off timer or by a
schedule; before this commit only the physical buttons obeyed the lock. The same
commit adds one Home Assistant entity — the lock sensor, **27 entities per strip**
(26 before) — and the build **`abayoumy-lock`** (gap **764 B**, 334,284 B, UI gzip
19,429 B) is the one that carries it. **Both strips now run `abayoumy-lock`**
(flashed 2026-10-19, behaviour exercised over the API, see *Sixth flash*), so this
is the live firmware.

**The dashboard is English only** (`f88dd17`, 2026-10-19) — see *Commit 7: the
dashboard drops Korean*. The Korean dictionary, every inline `ko`/`en` pair and the
header language selector are gone; `mttl_settings_default()` now writes `language=1`
(English) and the device build refuses Hangul in any gzipped asset. The dictionary and
the inline pairs were **3,390 B of the gzipped UI** (19,429 → 16,039), so the build
**`abayoumy-en`** (gap **4148 B**, 330,900 B, UI gzip 16,039 B) is the highest-headroom
build of the series. It is **built and host-verified, not yet flashed**: both strips
still run `abayoumy-lock`.

| | |
|---|---|
| Base | shipped series: `main` = `ebfb39d` (`v2.0.15-3-geb...`), tree `b187b492348a082f5fe7aa5d81fb272a9fa5451f`; rebased series: upstream tag `v2.0.17` = `311663e`, tree `420991a99008bf196bf5468e7770c45c4096e7c8` |
| Branch | `feature/protection-v2`, two lines. **Shipped (2.0.15 base)**, kept as `archive/protection-v2-2.0.15`, tree `b7a0d1f15ce1ab99c2d7b7b489aee501a9de1adb`: `9382e2a` (isolation; builder re-created it as `16c3a2f`), `ec34e41` (trip visibility; builder: `fcbc98e`), `9e8a7e1` (one limit for every outlet; builder: `6ca59da`), `0b7947d` (drop the safety note + named build id; builder: `2106825`), `6ff0735` (timers are not HA entities; builder: `419f225`). **Live (2.0.17 base)**, tree `49c3ef130d6cf8ff8276f72d5b79bdd229f89703`: `fc6338c`, `aa68f78`, `c7e8a5e`, `24a34dd`, `9a05d83`, `cf02922`, `f88dd17` — identical SHAs on both sides, because the builder fetched them from the Mac's bundle rather than replaying the rebase |
| Patches | **live series** (applies to `v2.0.17`): `patches/0001-per-channel-current-isolation.patch` (71,533 B) + `patches/0002-protection-trip-visibility.patch` (12,427 B) + `patches/0003-current-limit-every-outlet.patch` (35,340 B) + `patches/0004-ui-note-and-build-id.patch` (8,037 B) + `patches/0005-timers-are-not-ha-entities.patch` (30,686 B) + `patches/0006-lock-every-command-path.patch` (41,427 B) + `patches/0007-english-only-dashboard.patch` (132,659 B); archived 2.0.15 series in `patches/2.0.15/`; layout + rebase traps in `patches/README.md` |
| Artifacts | isolation: `build-linux/mttl-w01-2.0.15-isolation.fwr` 334,388 B `0e436af0…`, build_id `e3787c6fd511f577`; trip sensor: `build-linux/mttl-w01-2.0.15-trip-sensor.fwr` 334,692 B `9c1390b5…`, build_id `b3dba27349ceea73`; limit-per-outlet: `build-linux/mttl-w01-2.0.15-limit-per-outlet.fwr` 334,556 B `404c95ab…`, build_id `57d3230f785990ba`; named build: `build-linux/mttl-w01-2.0.15-abayoumy.fwr` 334,300 B `3499190b…`, build_id `abayoumy`; timers retired: `build-linux/mttl-w01-2.0.15-abayoumy-notimers.fwr` 333,372 B `a61d34a0…`, build_id `abayoumy-notimers`; (2.0.17, never flashed, superseded: `build-linux/mttl-w01-2.0.17-abayoumy.fwr` 333,620 B `90ff0bb5…`, build_id `abayoumy`); (**live on both strips** `build-linux/mttl-w01-2.0.17-abayoumy-lock.fwr` 334,284 B `b65c0e30…`, build_id **`abayoumy-lock`**); English only: `build-linux/mttl-w01-2.0.17-abayoumy-en.fwr` **330,900 B** `afb5fd1b…`, build_id **`abayoumy-en`** (built + host-verified, not flashed) |
| Manifests | `build-linux/manifest-isolation-e3787c6fd511f577.json`, `build-linux/manifest-trip-b3dba27349ceea73.json`, `build-linux/manifest-57d3230f785990ba.json`, `build-linux/manifest-abayoumy.json`, `build-linux/manifest-abayoumy-notimers.json`, `build-linux/manifest-2.0.17-abayoumy.json`, `build-linux/manifest-2.0.17-abayoumy-lock.json`, `build-linux/manifest-2.0.17-abayoumy-en.json` (plus the per-asset gzip reports `build-linux/ui-assets-2.0.17-abayoumy-lock.json` and `build-linux/ui-assets-2.0.17-abayoumy-en.json`) |
| Build log | `build-linux/build-0003-limit-per-outlet.log`, `build-linux/build-0004-abayoumy.log`, `build-linux/build-0005-abayoumy-notimers.log`, `build-linux/build-2.0.17-abayoumy.log`, `build-linux/build-2.0.17-abayoumy-lock.log` and `build-linux/build-2.0.17-abayoumy-en.log` (UI asset report, compile log, manifest of each archived build) |
| Contract run | `build-linux/contract3-js-c-limit-per-outlet/` (script, C harness, transcript; still valid — commits 4 and 5 do not touch the settings codec) |
| Source backup | `build-linux/fork-main+protection-v2+ha-wip.bundle` (git bundle: upstream `main` = `v2.0.17`, the `v2.0.17` tag, the live branch at `f88dd17`, the archived shipped line at `6ff0735`, and the parked HA branch; 7,101,326 B; `git bundle verify` passes; a fresh clone of it reproduces tree `49c3ef13…` on the live branch and `b7a0d1f1…` on the archive) |
| Built on | CT 106 `mttlbuild`, `10.0.0.19` (Debian 13, on pve2) — see `BUILD_LXC.md` |
| Flashed | LivingRoom `10.0.0.53`: isolation 524288 → 45056, trip build 45056 → 524288, limit-per-outlet 524288 → 45056, abayoumy 45056 → 524288, abayoumy-notimers 524288 → 45056; BedRoom `10.0.0.54`: `2.0.14` 524288 → 45056 (first flash of this branch on that strip), abayoumy 45056 → 524288, abayoumy-notimers 524288 → 45056 |

## What it does

Local protection, all on the strip, no cloud:

* highest fresh channel temperature → trips on the first exceed,
* corrected aggregate current → trips after two consecutive over-limit rounds,
* aggregate power → trips after two consecutive over-limit rounds,
* **one current limit applied to every outlet automatically**: the same
  `current_ma` that judges the total also judges each of the four channels, with
  the same two-round confirmation and only on rounds that actually read all four
  channels, so a half-populated round can never produce a per-channel verdict.
  There is no separate per-channel setting, no per-outlet UI and no separate
  enable bit: turning the overcurrent limit on (bit 1 = `0x02`) turns on both
  judgements.

`reason` keeps its original bit meaning (1 temperature / 2 current / 4 power) so
the web UI, MQTT and `/api/status` readers keep working.

### Attribution and cut policy (this commit)

`channel_mask` says *which* outlet caused a trip. A new `cut_mask` says which
relays to switch off, so a trip on one outlet no longer has to drop the whole
strip:

| cause | relays cut |
|---|---|
| per-channel current, one outlet | **that outlet only** |
| per-channel temperature, one outlet | **that outlet only** |
| aggregate current | all four |
| aggregate power | all four |
| aggregate **and** per-channel in the same round | **the attributed outlet(s) only** — with one limit for both judgements an outlet over the limit always takes the total over it in the same round, so the aggregate verdict is the same event, not a second one |
| unattributable / unknown cause | all four (fail-safe) |

`MTTL_PROTECTION_CUT_ALL` is `0x0f` and is the fail-safe value. The relay driver
already honoured a limited mask on the ALL target, so no driver change was
needed: `sdk_worker.c` gained `protection_off(unsigned mask)` and the requested
state is masked with `relay_desired &= ~mask`.

Temperature trips were previously unattributed; `mttl_protection_temperature()`
now takes the channel index (`sdk_meter.c` passes `last_channel`), which is what
makes the isolated temperature cut possible.

There is **no automatic re-enable** after a trip — upstream semantics (priority
ALL-OFF command, no persistent lock) are preserved.

> **Behaviour change that is already live on 10.0.0.53:** bit 0 (temperature) and
> bit 1 (current) are both on by default, and neither is opt-in any more. A
> per-channel temperature trip cuts **that outlet only**, and now a per-channel
> current trip does too: the current limit judges the total *and* every outlet, so
> an outlet over the limit is cut alone instead of dropping all four. Aggregate
> power, and an over-limit total that no single outlet explains (e.g. two outlets
> each just under the limit), still cut all four. On this strip every load draws
> 23–61 mA against a 16 A limit, so nothing can trip by accident — the change
> only shows up when something really does exceed the limit.

## Commit 4: the safety note comes off, the build gets a name (`0b7947d`)

Two UI-level changes — no firmware logic and no settings-codec change:

* The protection tab's closing note — *"No automatic ON or lock. Sensor failures
  show errors only. This does not replace hardware safety protection."* and its
  Korean counterpart — is **removed**. Local protection is implemented, so the
  sentence was misleading; the hint above the form still states the two-round
  policy, the mask/reason semantics and the ~10 s channel sampling. The form's 13
  ids and the `protection-state` line are untouched.
* The OTA build id can be **named**: `MTTL_OTA_BUILD_ID=abayoumy` is used verbatim
  in place of the random `secrets.token_hex(8)` (unset keeps the old behaviour).
  The OTA page's build-id guard was relaxed from `/^[0-9a-f]{16}$/` to
  `/^[0-9a-z][0-9a-z._-]{3,31}$/`, so a named build still appears in *Current
  build* and still drives the "Build verification: OK / NOT MATCHED" line after an
  upload. `/api/firmware/status` reports the name as-is.

## Commit 5: the timers stop being Home Assistant entities (`6ff0735`)

The auto-off timers are not wanted in HA at all, and deleting the entities in HA
alone never sticks: the strip re-announces all eight after every reconnect. So the
announcement is gone from the firmware:

* `ha_discovery.c`: the `index>=25` (`number` auto-off timer) and `index>=29`
  (`sensor` remaining-time) branches are deleted, and the component expression is
  now just `index<5?"switch":"sensor"`. `MTTL_HA_ENTITIES` 34 → **26**,
  `MTTL_HA_TRIP_INDEX` 33 → **25**: the trip entity moves to the end of the
  shorter table and keeps its topic and entity id.
* The two state publications that existed only to feed those entities are gone as
  well — `<base>/timerN` (retained, from `publish_sample`) and
  `<base>/timer_remainingN` (the once-per-5-s countdown publication) — together
  with the fields that fed them (`mqtt_timer_minutes`, `mqtt_remaining_*`) and
  `mttl_device_publish_remaining()`. The tick's cadence branch collapses to a plain
  `publish_sample()`.

What deliberately stays: the timers themselves (local timer logic, the device web
UI, the buttons) and the MQTT `…/timerN/set` command path — timers remain a device
feature, they are simply no longer *announced* to HA. `mqtt_timer_known` survives
as the acknowledgement flag used by the timer config-write path in `sdk_worker.c`.

The host test now asserts the whole table: 26 entries, no `number` component
anywhere, no topic containing `timer`, and a refusal at `MTTL_HA_ENTITIES` and
beyond.

HA-side cleanup (one-off, done 2026-10-18 while both strips still ran the older
build): the 16 retained `homeassistant/{number,sensor}/mttl_<id>_timer…/config`
topics were emptied (empty retained payload through `mqtt.publish`), as were the 16
orphaned retained state topics `mttl/standalone/<mac>/timerN` and
`…/timer_remainingN` left behind by the old firmware. HA dropped all 16 timer
entities — **68 → 52** captured ids, **26 per strip** (5 switches + 20 samples + the
trip sensor). Because the clear happened *before* the flash, the strips' own
post-flash discovery republish is the proof: no timer entity came back.

## Trip visibility for Home Assistant (commit 2: `ec34e41`)

A cut is local and silent — the strip's web UI is the only place that knows, and
it does not tell you when you are not looking at it. Commit 2 adds exactly one
Home Assistant entity for that, and nothing else:

| | |
|---|---|
| entity | `sensor.mttl_<id>_protection` ("… Protection", diagnostic) |
| index | `MTTL_HA_TRIP_INDEX` = **25**, the last index — commit 5 shortened the table from 34 to 26 entries, so nothing at or past index 26 is announced |
| state | cut mask of outlets **still off**: bit 0 = outlet 1 … bit 3 = outlet 4, `0` = no cut in effect |
| attribute | `reason` (1 temperature / 2 current / 4 power) — cause of the last trip, latched |
| topic | `<base>/protection`, retained, no expiry, republished after every (re)connect |
| payload | `{"mask":N,"reason":R}` with discovery `val_tpl: {{ value_json.mask }}` + `json_attr_t` |
| cost | **304 B** (660 → 356 B headroom), measured per object against the isolation build: `ha_discovery.o` +153, `device_app.o` +158, `protection.o` unchanged. Commit 3 then gave **136 B back**, and commits 4–5 another **1184 B**, so the shipped build sits at a **1676 B** gap |

Design points worth keeping:

* **The mask is "cut and still off"**, so restoring power returns the entity to
  `0` and re-arms it. That is what makes a *repeat* trip notify again; a latched
  tripped flag would notify once ever.
* **Outlet names stay on the HA side.** The switch entities already carry them
  (`switch.mttl_<id>_sw1..4`), two outlets here are both named `SBar`, and names
  are free-form strings up to 64 B. Rendering them on the device was built first
  and measured **480 B** instead of 304 B (`protection.o` +217,
  `ha_discovery.o` +116, `device_app.o` +162 → gap 660 → 180); that version was
  dropped in favour of the mask. Dropping the `reason` attribute from the shipped
  version would give back another ~95 B.
* The publication rides the existing 500 ms sensor rotation, so a cut reaches HA
  within about a second with no new task or timer.
* Nothing is published when nothing changes, so the MQTT traffic cost is one
  message per trip plus one per reconnect.
* HA-YAML for the notification (verified against this HA instance for masks
  0/1/2/4/8/5/15) is in **`HA-LIMITS-WIRING.md`**; it is not installed in your
  config yet.

## Why per-channel current and not also per-channel power

On one mains supply a per-channel power limit is the same judgement as a
per-channel current limit at a fixed voltage, so it adds little protection while
doubling the storage, the code and the UI. That matters here: see the RAM budget.
Only current is stored; the aggregate power limit is untouched.

### Settings format: version 8

v8 = v7 + 4 × `u16 channel_current_ma`: tail 66 → **74**, `needed` 82 → **90**,
packed size **118**, `body[0]==8?74:`, `if(body[0]>=7)`, storage total
118 + 38 = **156**. A v4–v7 record migrates with 16,000 mA defaults.

Commit 3 keeps that format **exactly** — no v9, no migration, same codec, same
record size, same tests. It changes what the four values *mean*: the firmware now
judges each channel against `current_ma` and never reads the array, and the web UI
mirrors the current limit into all four when it saves. So the stored record stays
self-consistent, `/api/config` keeps reporting `channel_current` for old readers,
and a downgrade to the isolation build behaves the same (the isolation code reads
the mirrored values as its per-channel limits).

## RAM budget — the constraint that shaped the design

`BD_RAM` is 434,176 B of **RAM** (`analysis/memory_bounds.ld`,
`__mttl_msp_limit = 0x1006F000`, `__mttl_msp_top = 0x10070000`). Code, rodata
(which includes the gzipped web UI) and data all live in `.ram_image2.text`
inside it. `static_gap_to_msp_bytes` is what is left below the reserved 4 KB MSP
stack, and `ASSERT(__HeapLimit <= __mttl_msp_limit)` is the hard guard — an
overrun fails the link, it cannot corrupt the stack at run time.

| build | `static_gap_to_msp_bytes` | .fwr bytes | UI gzip | built on |
|---|---|---|---|---|
| pristine `main` `ebfb39d` | **1620** | 333,428 | 18,791 | CT 106 (re-confirmed; old LXC gave the same numbers) |
| first attempt (per-channel current **and** power, full UI) | **68** | 334,980 | 19,602 | old LXC (AlmaLinux 9, GCC 11) |
| lean version (current only, trimmed UI) | **748** | 334,300 | 19,224 | old LXC |
| lean + isolated cuts (`9382e2a`) | **660** | 334,388 | 19,231 | CT 106 |
| **shipped: + HA trip sensor (`ec34e41`)** | **356** | 334,692 | 19,231 | CT 106 |
| **shipped: one limit for every outlet (`9e8a7e1`)** | **492** | 334,556 | 19,112 | CT 106 |
| **shipped: safety note dropped + named build id (`0b7947d`)** | **748** | 334,300 | **18,877** | CT 106 |
| **shipped: timers are not HA entities (`6ff0735`)** | **1676** | 333,372 | **18,877** | CT 106 |
| **rebased onto upstream `2.0.17` (live branch, never flashed — superseded by `abayoumy-lock`)** | **1428** | 333,620 | **19,168** | CT 106 |
| **lock gates every command path (`cf02922`, flashed on both strips)** | **764** | 334,284 | **19,429** | CT 106 |
| **English-only dashboard (`f88dd17`, built + host-verified, not flashed)** | **4148** | 330,900 | **16,039** | CT 106 |

Per-channel current plus isolated cuts cost **960 B** (1620 → 660); the HA trip
sensor cost another **304 B** (660 → 356). Commit 3 gave **136 B back**
(356 → 492) by deleting the separate per-channel limit plumbing (the enable bit,
the array reads, the error-reporting bit) and took the gzipped UI from 19,231 to
**19,112 B** by removing the four-slider section. Commit 4 is UI-only and gave
another **256 B back** (492 → 748): the protection tab's safety note is gone —
204 B of `index.html` (the inline Korean fallback plus its wrapper) and 300 B of
`i18n.js` (both languages), against +13 B for the wider build-id guard in
`ota-live.js` — so the gzipped UI is **18,877 B** (`index.html` 15,427 /
`i18n.js` 5,941 / `live.js` 28,323 / `ota-live.js` 4,019 raw). That equality —
*image shrinks 256 B, static gap grows 256 B* — is the check that the two pools
are the same pool: `static_gap + .fwr bytes = 335,048` holds for every build in
this table.
Commit 5 is firmware-only and gave a further **928 B back** (748 → 1676): the two
discovery branches and their name templates, the eight timer state payloads, the
countdown publication and the struct fields behind it. The gzipped UI did not
move (18,877 B), so the invariant held again: 1676 + 333,372 = 335,048.
The 2.0.17 rebase took **248 B** (1676 → 1428). Every C-side change upstream made
is a version *label*, and `"2.0.15"`/`"2.0.17"` are the same length, so all of it
is UI: gzip went 18,877 → **19,168 B** (`index.html` 15,427 → 16,201 raw for the
inline loader, and `live.js` absorbed the former `ota-live.js` while coming out
*smaller* than the sum of the two, because the concatenated file shares one gzip
dictionary). The image grew 43 B **less** than the UI gained, because the asset
table now holds three entries instead of four. Invariant again:
1428 + 333,620 = 335,048.
The lock commit cost **664 B** (1428 → 764) and is split cleanly by the two
pools: **261 B of gzipped UI** (19,168 → 19,429 — the padlock tooltip now says
what the lock really does, the per-outlet toggle is disabled while locked, and
the timer editor shows a locked channel as unavailable; `live.js` is 12,051 B
gzipped) and **403 B of C**: the lock branch in `ha_discovery.c`, the lock
publication in `device_app.c` (the locked-outlet list, the `…/lock` topic, one
flag byte in the app struct, and `payload[24]` grown to `payload[40]`), the
refusal in `mttl_settings_valid` plus the load-time normalisation loop in
`mttl_settings_unpack`, and the extra `else if` in the gate. Invariant once
more: 764 + 334,284 = 335,048. This is the first build where a feature was paid
for mostly by C-side code rather than by UI text.
Per-channel power and the full UI were dropped after the first attempt consumed
1552 B. A future overflow fails the link assert; the newlib heap is separately
bounded to TCM (`__mttl_newlib_start`/`__mttl_newlib_limit` around `0x2000xxxx`),
so the gap is pure slack rather than live heap.

The UI headroom is the same pool: `sum(gzip) < 20000` is asserted, and the
gzipped UI bytes occupy the same RAM region as code, so **1 byte of UI text
costs exactly 1 byte of code budget**.

## Verification performed

1. **Host unit test** — `sh source/standalone/host_test/run.sh` (system `cc`, no
   cross toolchain, ~1 s): **249 checks, 0 failures** (227 before commit 6), on
   both Apple clang 21 (macOS) and GCC 14.2.0 (Debian 13 container). Covers
   * inclusive limits (never trips exactly at the limit),
   * first-round temperature trip, two-round aggregate current/power trips,
     confirmation reset on recovery, `error_mask` only for enabled limits,
   * the aggregate power W-vs-mW boundary (`limit*1000`),
   * per-channel: single and multiple outlets, attribution mask, NULL-array
     rounds, disabled limit, the shared limit (an outlet over it while the total
     is under the limit cannot happen in reality but is a valid unit case), a
     channel exactly at the limit, and that the stored v8 per-channel values are
     **not** limits,
   * **the cut policy**: per-channel current and per-channel temperature cut only
     the blamed outlet; aggregate power cuts all four; aggregate current + a
     per-channel verdict in the same round cuts **only the blamed outlet(s)**; an
     aggregate trip no outlet explains cuts all four; unknown/unattributable cause
     cuts all four,
   * settings v8 round trip, buffer guard, storage wrapper,
   * rejection of unknown enable bits, out-of-range limits, wrong tail length,
   * **migration of an already-stored v1/v4/v5/v6/v7 record** to v8: aggregate
     limits and credentials preserved, per-channel limits defaulted,
   * **the Home Assistant entity contract** (`ha_discovery.c` was added to the
     harness for this): the trip sensor's discovery topic, `uniq_id`,
     `default_entity_id`, `stat_t`, `val_tpl`, `json_attr_t`, availability topic
     and the absence of an expiry, plus a regression guard that indices 0 and 5
     still produce exactly the topics they always did, that the last sampled
     sensor is `temperature4` (index 24), that **no index emits a `number`
     component or a topic containing `timer`** (commit 5), and that
     `MTTL_HA_ENTITIES` and 33 are both refused. Commit 6 extends it to the lock
     sensor (index 26: topic, `stat_t`, `val_tpl` on `locked`, `json_attr_t`,
     diagnostic category, no expiry) and pins the new table size (27, trip 25,
     lock 26),
   * **the lock/timer rule and its migration** (commit 6): a timer on a locked
     channel is refused by `mttl_settings_valid` *and* by `mttl_settings_pack`,
     the same timer on an unlocked channel is still accepted, and a stored v8 or
     v7 record that holds both loads with the timer cleared instead of being
     rejected — the case an upgrading strip hits. The `old[n-17]`/`old[n-12]`
     byte offsets in that test are the documented tail layout, so a format
     change that silently moves the lock byte fails the test.
   The harness probes for `-Wno-misleading-indentation` and uses it only where
   the compiler accepts it: upstream's deliberate dense one-liner style trips
   `-Werror=misleading-indentation` on GCC ≥ 12 (GCC 11 and clang are silent).
   This is a harness concern only — the cross build never enables that warning.
2. **Mutation checks** — the cut policy and the limit source are pinned by
   mutations that compile: mis-assigning `cut_mask` is caught (4 failures), and
   reading the stored v8 per-channel array as the limit again is caught by
   **14 failures**, so "each channel is judged against `current_ma`" cannot
   regress silently. The four older cut-policy mutations are each caught by a
   specific assertion in `test_protection_cut_policy()`.
3. **JS encoder → C decoder contract test** — the real `settingsBody()` is lifted
   out of `ui/live.js` and run in node; its output is fed to the firmware's own
   `mttl_settings_unpack`. Re-run for this commit: a 141-byte body (test strings)
   decodes with every field matching, the v8 tail reads
   `channel_current=[1234,1234,1234,1234]` for `current: 1234` — the encoder now
   mirrors the single limit, which is the point of the UI change — and re-packing
   reproduces byte-identical output, so a UI save cannot silently alter settings.
   Negative cases (enable bit `0x10`, 999 mA / 16001 mA / non-integer) are refused
   by both sides. Script, harness and transcript:
   `build-linux/contract3-js-c-limit-per-outlet/`.
4. **Build assertions** — `bin_fwr_roundtrip`, `objcopy_byte_match`,
   `native_ota_hardware_field_verified`, image/format checks, `ui gzip < 20000`,
   preview-word and unique-id checks, and the MSP gap guard all pass.
5. **Artifact traceability (all five builds)** — each archived manifest's
   `files[].sha256` equals `sha256` of the `.fwr` archived next to it (the built
   `comMTTL-W01_2.0.15.fwr` is byte-identical to
   `mttl-w01-2.0.15-network-OTA-test.fwr`), the lossless FWR round-trip and
   `objcopy` byte-match assertions pass, and the build id the strip reports on
   `/api/firmware/status` matches the manifest: isolation `e3787c6fd511f577`,
   trip build `b3dba27349ceea73`, limit-per-outlet `57d3230f785990ba`, named build
   `abayoumy` (334,300 B, `3499190b…`, gap 748 B), shipped build `abayoumy-notimers`
   (333,372 B, `a61d34a0…`, gap 1676 B). Commit 4 touches no firmware C file and
   commit 5 touches no settings-codec file, so the contract run above still
   describes the shipped image; the build id is the only non-deterministic field,
   and it is now pinnable. The later 2.0.17 build (`abayoumy`, 333,620 B,
   `90ff0bb5…`, gap 1428 B) was traced the same way — manifest `sha256` equals the
   archived `.fwr`, and a clean rebuild reproduced it byte for byte.
6. **HA-side template** — the notification template documented in
   `HA-LIMITS-WIRING.md` was rendered through this HA instance's
   `POST /api/template` for all 21 mask × cause combinations
   (masks 0/1/2/4/8/5/15 × reasons 1/2/4) and named the right outlets and the
   right cause every time — including the two outlets that are both named `SBar`,
   which is exactly why the mask is the interface and names are looked up from
   the switch entities on the HA side.

### Defects found and fixed during this redo

* The first attempt's silent C1 (settings version left at 7 while the tail grew)
  is structurally impossible now: the version byte, the tail-length table and the
  reader branches are all pinned by the host test, and `needed` tracks the tail.
  Regression-checked by mutation (relabelling v8 as v7 → 19 failures).
* The first attempt's C2 (power compared mW against W) was real; the per-channel
  case is gone and the aggregate case now has a boundary regression test.
* During the redo the host test caught the codec reading the per-channel arrays
  interleaved while the writer grouped them.
* The contract test caught the web UI accepting `enabled` up to 31 while the
  firmware mask accepted at most 15 — a UI save would have been rejected.
* Temperature attribution was missing entirely (every temperature trip looked
  aggregate); fixed by passing the channel index from `sdk_meter.c`.

## On-hardware verification — LivingRoom strip `10.0.0.53`, 2026-10-17

Flash used `POST /api/firmware/upload` with `Content-Type: application/x-mttl-fwr`,
`Origin: http://10.0.0.53` and the raw `.fwr` (the build already applies the
vendor XOR payload encoding via `package_body()`, so no separate step is needed).
Response `{"written":true,"activated":true,"rebooting":true}`, 334,388 B in 20 s;
device back after ~15 s.

Evidence is kept under `build-linux/preflight2-isolation-10.0.0.53/` and
`build-linux/postflight2-isolation-10.0.0.53/` (`config.json`, `device.json`,
`status.json`, `firmware-status.json`, `ha-entities.json` on both sides).

| check | result |
|---|---|
| before | `2.0.15`, build_id `39177b4d88998675`, slot 524288, `enabled:7`, `channel_current:[16000×4]` |
| after | `2.0.15`, build_id **`e3787c6fd511f577`**, slot 45056, same `enabled` and limits |
| `/api/config` delta vs before | **none — byte-identical** (v8 record survived the OTA) |
| protection state | `{"reason":0,"error":0,"channel_mask":0}` → **no spurious trip** |
| relay states | TV/SBar/SBar on and drawing, SW 4 off — unchanged |
| energy counters | `[1093,44,236,4]` before and after |
| Wi-Fi / MQTT | state 5, SSID `IOT`, rssi −72 dBm, values updating |
| web UI | served, gzipped (mount with `curl --compressed`) |
| HA | 33 of 33 entities available, 0 unavailable |
| uptime at check | 730 s, still clean |
| recovery path | `restore_versions: ["1.0.66","1.0.68"]` still offered |

Side effect of the reboot (not of the feature): the strip re-announces its MQTT
discovery, so the eight timer entities reappear in HA — they had been deleted
earlier, which is why this strip showed 33 entities where the BedRoom strip showed
25. Any reboot did this until commit 5 stopped the announcement altogether: since
then both strips announce 26 entities, and no timer entity survives a reconnect.

Protection tripping itself has **not** been exercised on hardware yet: a
per-channel trip needs > 1000 mA (≈ 220 W) on one outlet because the limit floor
is deliberately kept at upstream's 1 A, while every load on this strip draws
24–61 mA. See "Not done yet".

### Second flash — the shipped trip build (`ec34e41`), same strip

Artifact `build-linux/mttl-w01-2.0.15-trip-sensor.fwr` (334,692 B,
sha256 `9c1390b51f1afd3dd9c22ee6171e552c6916faa51db233a2ceec364ffb398441`),
build_id `b3dba27349ceea73`. Evidence in
`build-linux/preflight3-trip-10.0.0.53/` and
`build-linux/postflight3-trip-10.0.0.53/`.

Operational note: the upload is ~335 KB over Wi-Fi and takes **~25 s**. My first
attempts used `curl --max-time 20`/`25` and were killed mid-transfer with no
response at all (the device then simply kept running the old build, build id
unchanged — no half-written slot, no brick). Use `--max-time 40` or more.

| check | result |
|---|---|
| before | build_id `e3787c6fd511f577`, slot 524288→45056 build, `enabled:7`, `channel_current:[16000×4]` |
| after | build_id **`b3dba27349ceea73`**, slot 524288, same `enabled`, same four limits |
| `/api/config` delta vs before | **none — byte-identical** (`diff` of the two snapshots) |
| protection state | `{"reason":0,"error":0,"channel_mask":0}` → **no spurious trip** |
| relay states | identical pre/post (TV off, SBar/SBar on, SW 4 off) |
| energy counters | `[1093,44,237,4]` before and after (channel 3 gained 1 Wh between the two flashes, as expected — it is the loaded outlet) |
| MQTT | reconnects within ~30 s, then state 5 continuously |
| **HA entities** | **34 of 34** available; the new one is `sensor.mttl_9d270aa_protection` = `0` with attributes `mask: 0`, `reason: 0`, i.e. the discovery, the `val_tpl` and the attribute topic were all accepted by HA. Snapshot diff over *both* strips: exactly one new entity id, no other change (58 → 59 captured ids) |
| recovery path | `restore_versions: ["1.0.66","1.0.68"]` still offered, `ota_ready: true` |

The trip *transition* (mask going non-zero in HA) rides on the deferred hardware
trip test below; everything else about the entity is verified live.

### Third flash — one limit for every outlet (`9e8a7e1`), same strip, 2026-10-18

Artifact `build-linux/mttl-w01-2.0.15-limit-per-outlet.fwr` (334,556 B, sha256
`404c95abf9e9ff1484463503c548ed25816768dabf3ea5c038be679080a5e901`), build_id
`57d3230f785990ba`, gap **492 B**. Evidence in
`build-linux/preflight4-limit-per-outlet-10.0.0.53/` and
`build-linux/postflight4-limit-per-outlet-10.0.0.53/`; the build's own log is
`build-linux/build-0003-limit-per-outlet.log`.

| check | result |
|---|---|
| before | build_id `b3dba27349ceea73`, slot 524288, `enabled:7`, `channel_current:[16000×4]` |
| after | build_id **`57d3230f785990ba`**, slot 45056, same `enabled`, same four stored values |
| `/api/config` delta vs before | **none — byte-identical** |
| protection state | `sensor.mttl_9d270aa_protection` = `0` with attributes `mask: 0`, `reason: 0` → **no spurious trip** |
| relay states | identical pre/post (SW 1 off, SBar/SBar on, SW 4 off); MQTT reconnected, switches not `unavailable` |
| energy counters | `[1093,44,246,4]` before and after |
| Wi-Fi / MQTT | state 5, SSID `IOT`, rssi −74 dBm, `meter_initialized: 15`, `hardware_ready: true` |
| **web UI** | the served `index.html`, `live.js` and `i18n.js` were fetched with `curl --compressed` before and after: **16 per-channel references before, 0 after**; the old section title is gone, the new hint text is present, and all 13 ids the protection form still uses are present exactly once |
| HA | 34 of 34 entities available, identical entity-id set (59 captured ids over both strips) |
| recovery path | `restore_versions: ["1.0.66","1.0.68"]`, `ota_ready: true` |
| upload | `{"written":true,"activated":true,"rebooting":true}` in 30 s; device answering again after ~53 s |

### Fourth flash — the named build `abayoumy`, and the first flash on the BedRoom strip, 2026-10-18

Artifact `build-linux/mttl-w01-2.0.15-abayoumy.fwr` (334,300 B, sha256
`3499190b55a020f93fe407ba449d96580a83f784e531b91306a622688d14ffb7`), build_id
**`abayoumy`**, gap **748 B** (a clean rebuild of the same tree reproduced both
numbers byte for byte). Evidence in `build-linux/preflight5-abayoumy-10.0.0.53/`
+ `build-linux/postflight5-abayoumy-10.0.0.53/` and
`build-linux/preflight5-abayoumy-10.0.0.54/` +
`build-linux/postflight5-abayoumy-10.0.0.54/`; the build log is
`build-linux/build-0004-abayoumy.log`.

LivingRoom `10.0.0.53`:

| check | result |
|---|---|
| before | build_id `57d3230f785990ba`, slot 45056, `enabled:7`, `channel_current:[16000×4]` |
| after | build_id **`abayoumy`**, slot 524288, same `enabled`, same four stored values |
| `/api/config` delta vs before | **none — byte-identical** |
| protection state | `sensor.mttl_9d270aa_protection` = `0`, attributes `mask: 0`, `reason: 0` → **no spurious trip** |
| relay states | identical pre/post (TV off, SBar/SBar on, SW 4 off) |
| energy counters | `[1094,44,251,5]` → `[1094,44,252,5]` (the loaded outlet gained 1 Wh, nothing reset) |
| Wi-Fi / MQTT | state 5, SSID `IOT`, rssi −72 dBm, `meter_initialized: 15`, `hardware_ready: true` |
| **web UI** | served `index.html`/`i18n.js`/`live.js`/`ota-live.js` fetched with `curl --compressed`: sizes 15,427 / 5,941 / 28,323 / 4,019 — exactly the build report's raw sizes. **`protectionNote` references: 0 (1 line before), the note text: 0**, the hint still present, all 13 form ids present |
| HA | 34 of 34 available, identical 59-id set over both strips |
| recovery path | `restore_versions: ["1.0.66","1.0.68"]`, `ota_ready: true` |
| upload | `{"written":true,"activated":true,"rebooting":true}` in 26 s; answering again after ~45 s |

BedRoom `10.0.0.54` — **first flash on the strip that carries the real load**
(`PVE1` was on and `locked`, ~81 W):

| check | result |
|---|---|
| before | `2.0.14`, build_id `bde584ccbe78cbce`, slot 524288, `enabled:7`, `temperature:80`, `current:16000`, `power:2000`, `button_lock:1`, **no `channel_current` key** (v7 record) |
| after | `2.0.15`, build_id **`abayoumy`**, slot 45056, same enabled/limits/`button_lock`/`schedule_hex` |
| `/api/config` delta vs before | exactly one addition — `"channel_current":[16000,16000,16000,16000]`: the **v7 → v8 migration on real hardware**, defaulting the four stored values to the total limit, nothing else touched |
| protection state | `{"reason":0,"error":0,"channel_mask":0}` → **no spurious trip** |
| relay states | all four channels still on, `PVE1` still `locked`; PVE1 81.3 W → 83.7 W (load unchanged) |
| energy counters | `[378,0,296,182]` → `[380,0,296,182]`, per-channel `meter_wh` 420→422 / 0 / 368 / 226 — preserved, not reset |
| Wi-Fi / MQTT | state 5, SSID `IOT`, rssi −59 dBm, `meter_initialized: 15` |
| **web UI** | same four served files, same sizes, `protectionNote` 0, note text 0, hint present |
| HA | 59 → **68** captured ids, nothing lost; the 9 new ones are this strip's 8 timer entities (re-announced by the reboot, as documented for 53) plus `sensor.mttl_941678b_protection` = `0` (`mask: 0`, `reason: 0`) |
| recovery path | `restore_versions: ["1.0.66","1.0.68"]`, `ota_ready: true` |
| upload | `{"written":true,"activated":true,"rebooting":true}` in 17 s; answering again after ~40 s |

Upload reliability, one more data point: the **first** attempt on 53 returned an
empty body after 75 s and the strip kept running the old build — no partial slot,
no brick — and the identical retry succeeded in 26 s. That matches the
`--max-time` note above: treat an empty response as "not flashed, old build still
running" and confirm with `/api/firmware/status` before retrying.

### Fifth flash — the timers leave Home Assistant (`6ff0735`), both strips, 2026-10-18

Artifact `build-linux/mttl-w01-2.0.15-abayoumy-notimers.fwr` (333,372 B, sha256
`a61d34a00772191b37b992c7cf8ddb35d6aa7534d0fd76a64fa552f0308501f7`), build_id
**`abayoumy-notimers`**, gap **1676 B**, UI gzip unchanged at **18,877 B**; the
build log is `build-linux/build-0005-abayoumy-notimers.log`. Evidence in
`build-linux/{preflight6,postflight6}-notimers-10.0.0.53/` and
`build-linux/{preflight6,postflight6}-notimers-10.0.0.54/`.

The order matters and is the proof: the 16 retained timer config topics were
emptied **before** the flash, so the 26-entity result afterwards can only come from
the strip's own discovery republish — if the firmware still announced timers, they
would have come straight back.

| check (both strips) | result |
|---|---|
| before | `10.0.0.53` build_id `abayoumy`, slot 524288; `10.0.0.54` build_id `abayoumy`, slot 45056 |
| after | build_id **`abayoumy-notimers`** — `10.0.0.53` slot **45056**, `10.0.0.54` slot **524288** (the OTA swaps slots) |
| `/api/config` delta vs before | **none — byte-identical on both strips** (the v8 record survived the OTA) |
| protection state | both `sensor.mttl_*_protection` = `0`, attributes `mask: 0`, `reason: 0` → **no spurious trip** |
| relay states | unchanged: 53 TV off, SBar/SBar on, SW 4 off; 54 **all four still on, `PVE1` on and `locked`** |
| energy counters | 53 `[1094,44,252,5]` → `[1094,44,254,5]`; 54 `[527,0,296,185]` → `[531,0,296,185]` — preserved, not reset |
| **HA entities** | **26 per strip, 52 total, 0 timer entities** (5 switches + 20 samples + the trip sensor each), and the 16 timer entities stayed gone across the post-flash republish |
| **web UI** | all four assets fetched and gunzipped: **byte-identical to the build manifest** (`index.html` 15,427 / `i18n.js` 5,941 / `live.js` 28,323 / `ota-live.js` 4,019, sha256 match), `protectionNote` 0 |
| BedRoom load | `PVE1` 85.7 W at 88 s uptime, aggregate 87 W, all four outlets on — the Proxmox host stayed up |
| recovery path | `restore_versions: ["1.0.66","1.0.68"]`, `ota_ready: true` |
| upload | 53 `{"written":true,"activated":true,"rebooting":true}` in 26 s (answering again ~45 s later); 54 in 17 s (~40 s later) |

### Sixth flash — the authoritative lock (`cf02922`), both strips, 2026-10-19

Artifact `build-linux/mttl-w01-2.0.17-abayoumy-lock.fwr` (334,284 B, sha256
`b65c0e30e1c9ffb641b406de5e652d4721fc02baa70fa3ce5cd1335b81d6067b`), build_id
**`abayoumy-lock`**, gap **764 B**, UI gzip **19,429 B**; build log
`build-linux/build-2.0.17-abayoumy-lock.log`. Evidence in
`build-linux/{preflight7,postflight7}-lock-10.0.0.{53,54}/` and
`build-linux/locktest-10.0.0.53/` (the behaviour transcript).

Order as always: `10.0.0.53` first, `10.0.0.54` only after it had settled — and 54
powers the Proxmox host, so `PVE1` was watched across its reboot (`ping 10.0.0.210`
in the same loop as the poll: it never dropped).

| check | result |
|---|---|
| before | both `abayoumy-notimers` 2.0.15; 53 slot 45056, 54 slot 524288 |
| after | both **`abayoumy-lock` 2.0.17** — 53 slot **524288**, 54 slot **45056** (the OTA swaps slots) |
| upload | 53 in 24 s, 54 in 18 s; answering again after ~35 s and ~16 s |
| `/api/config` delta vs before | **none — byte-identical on both strips** |
| energy counters | 53 `[1103,44,281,5]` and 54 `[1475,7,359,239]` — identical before and after (not reset by the OTA) |
| protection | both `0`, `mask: 0`, `reason: 0`. Right after 54's first boot `/api/device` showed `error: 4` for a few seconds: that is `sdk_meter.c`'s "no valid power round yet" flag, cleared by the first real round — a boot artifact, not a trip |
| relay states | unchanged: 53 TV off, SBar/SBar on, SW 4 off; 54 **PVE1 on and still `locked`**, the other three off |
| **HA entities** | **27 per strip, 54 total** (+1 each: the lock sensor). `sensor.mttl_9d270aa_lock` = `none` / `mask 0` (nothing locked), `sensor.mttl_941678b_lock` = `1` / `mask 1` — the BedRoom lock was set on the *old* firmware and is simply read back and published by the new one, which is the upgrade path a strip with an existing lock takes |
| web UI | all three assets fetched and gunzipped, **byte-identical to the manifest** (`/` 16,201/4,818, `/i18n.js` 5,941/2,560, `/live.js` 34,291/12,051) on both strips |
| runtime stack | `worker_observed_stack_descent_bytes` **2168** B on both strips, against the 1536-word (6144 B) `mttl_network` task — ~35 % used, so the publish buffer growth (24 → 40 B) and the two extra gate locals are comfortably inside it |
| recovery path | `restore_versions: ["1.0.66","1.0.68"]`, `ota_ready: true` |

**The behaviour test is the point of this build**, and it ran on `10.0.0.53`
(outlet 4 = `SW 4`, off and drawing nothing, was the subject; nothing else was
disturbed except the TV, once, by an `ALL` command that was *supposed* to switch
the unlocked outlets — see below):

| step | command | result |
|---|---|---|
| lock outlet 4 | `tools/strip-config-write.py 10.0.0.53 --lock 8` | `202 {"accepted":true}` → read-back `lock=8`; HA lock sensor `4` / `mask 8` |
| single locked outlet | `POST /api/control` `[3,1]` | **`429 Output disabled, busy or faulted`**, `SW 4` stayed off |
| HA switch | `switch.turn_on` on `switch.mttl_9d270aa_sw4` | service accepts, **entity stays `off`** (`optimistic: false`), device unchanged |
| ALL with one locked | `POST /api/control` `[4,1]` | **`200 {"accepted":true}`** — and that is correct: the command *is* accepted for the unlocked subset, which is why the TV (off) came on while `SW 4` stayed off. The gate keeps the command and passes it `mask = 7` |
| timer on a locked outlet | `--timers 0,0,0,30` | `202` accepted, but the timer **never lands**: `mttl_settings_unpack` normalises it away, so the write succeeds with the timer dropped (the tool reports "not confirmed", which is it being strict about the field, not the write failing) |
| same write, both fields | `--lock 1 --timers 1,0,0,0` | **decisive**: the lock *did* change (`lock bits [True,False,False,False]`) while the timer on that same channel was dropped — normalisation, not a blanket refusal |
| timer on an unlocked outlet | `--timers 1,0,0,0` | accepted and stored (`timer_minutes [1,0,0,0]`), then cleared with `--timers 0,0,0,0` — the rule is not over-broad |
| MQTT timer on a locked outlet | `mqtt.publish mttl/standalone/d8aa59d270aa/timer4/set` = `5`, outlet 4 **on** and locked | no timer: `timer_running` stays `0`, deadline `0`. A timer only runs while its outlet is on (`core.c`: `mttl_timer_tick`), so the outlet was switched on first to make this a real test |
| same publish, unlocked | `--lock 0` then the publish again | **armed**: `timer_running=8` (bit 3), deadline set — the path works, so the refusal above is the lock, not a broken topic. `payload 0` cancels it again |
| everything locked | `--lock 15` | single ON `429`, ALL ON `429`, ALL OFF `429`, HA `switch.mttl_9d270aa_all` `turn_off` accepted but **nothing moved** (soundbars still on, TV still off); lock sensor `1,2,3,4` / `mask 15` |
| unlock | `--lock 0` | single ON then OFF on the same outlet both `200` **and the outlet actually switched** (`SW 4` on → off) — the gate is not stuck, and unlocking needs no reboot |

Three API details worth remembering, all discovered here: `/api/control` takes a
**0-based** channel (`0..3` = outlets 1..4, `4` = ALL), one byte each for channel
and state; a refused *single* channel is `429` while a refused subset of an ALL
command is a `200` with the locked outlets simply masked out; and the MQTT base
topic is not built from the HA id but from the **full 12-hex MAC**
(`mttl/standalone/d8aa59d270aa`, see `ha_discovery.c:identity()`), while the HA
entities use the 7-hex short id (`mttl_9d270aa`) — two namespaces, and the lock
sensor lives on `<base>/lock` in the first one.

The one thing a remote test cannot see is the **three LED edges** on a refused
manual command — the refusal itself is proven above, the blink still needs eyes.
The other pending hardware item is unchanged: a **protection trip on a locked
outlet** (the lock must never block a cut). The full transcript of this test is
`build-linux/locktest-10.0.0.53/transcript.txt`.

## Rebase onto upstream 2.0.17 (2026-10-19) — build `abayoumy`, never flashed (superseded by `abayoumy-lock`)

Upstream shipped two releases after our base `ebfb39d`: **2.0.16** and **2.0.17**
(`311663e`, identical to upstream `main`). Our base is an ancestor of both, so
this is a plain 3-way rebase, not a merge, and `v2.0.17` contains `v2.0.16`.

**What upstream actually changed** (delta `ebfb39d` → `v2.0.17`: 20 files,
+186/−32 lines):

| upstream change | relevance to this fork |
|---|---|
| `device_app.c/.h`, `integration_mock.c` — 2.0.16: HA timer sensors show the configured duration while OFF | **discarded**: that publication existed only to feed the timer entities commit 5 removed. The resulting dead `mqtt_remaining_minutes[4]` cache field is dropped with it |
| `ha_discovery.c`, `sdk_baseline.cpp`, `sdk_web.c` (×2), `mttl-source.json`, `build_assets.py`, `ui/{index,live,ota-test,app}` | taken: version labels `2.0.15` → `2.0.17` (same string length, so no size change) |
| `ui/ota-live.js`, `ui/device-loader.js` (new), `build_assets.py` asset assembly | taken: 2.0.17's real fix |
| `tests/*.cjs` (3 new node tests) | inert — not wired into any build step |
| `recovery/**`, `docs/**`, `firmware/*.fwr` | documentation and assets only: 2.0.16 is largely the ST-Link V2 recovery guide plus a bundled stock recovery FWR |

**2.0.17 has no C-side functional change.** The fix is entirely in the web UI:
`ota-live.js` is concatenated into `/live.js` (the Firmware tab can no longer lose
its initialisation on its own), the `<script>` tags are replaced by a small inline
loader that fetches `/i18n.js` then `/live.js` sequentially and retries failed
downloads every 3 s on every tab, the status request gets an 8 s timeout and a 3 s
retry, and after an update the page waits 5 s, polls reconnection every 3 s for up
to 2 min and reloads once a **new** Build ID appears. Settings format, protection
logic, MQTT schema, HA entity list and the OTA protocol are untouched — which is
why nothing has to change on the HA side at that commit (still 26 entities per
strip; commit 6 later appends the lock sensor as index 26, making 27). The vendor
notes one caveat: installing 2.0.17 *from an older page* needs a single manual
refresh; later updates reload themselves.

**How the rebase was done** (`git rebase --onto v2.0.17 ebfb39d`, on the shipped line):

* commits 1–3 apply **clean**;
* commit 4 conflicts in `ui/ota-live.js` — **the trap**: 2.0.17 hard-codes
  `/^[0-9a-f]{16}$/` in three new places (post-OTA reconnect check, `refreshStatus()`
  guard, current-build label). Left as-is, our *named* build ids would leave the OTA
  page permanently "not ready" and kill post-OTA auto-reload, so the relaxed guard
  `/^[0-9a-z][0-9a-z._-]{3,31}$/` is re-applied to all three. The remaining
  `-build-([0-9a-f]{16})\.fwr` filename pattern is deliberately untouched: it only
  pre-fills the "Build verification" line for vendor-named uploads;
* commit 5 conflicts in `device_app.c` + `integration_mock.c` (our deletion vs
  upstream's improved publication) → our deletion wins, and the vestigial
  `mqtt_remaining_minutes[4]` field that auto-merged into `device_app.h` is removed;
  `ha_discovery.c` auto-merges and keeps `"sw":"2.0.17"`.

Result: the five commits on `311663e`, tree `13eca34e…`, **host suite 227 checks /
0 failed**, all firmware files syntax-clean, and `git am` of the regenerated
`patches/` series on a pristine `v2.0.17` reproduces that very tree.

**Measured cost** (CT 106, build id `abayoumy`; a clean rebuild with the same id
reproduced the manifest `sha256` exactly):

| | flashed `abayoumy-notimers` | **rebased `abayoumy`** |
|---|---|---|
| gap to MSP | 1676 | **1428** |
| `.fwr` bytes | 333,372 | **333,620** |
| UI assets served | 4 | **3** |
| UI gzip total | 18,877 | **19,168** / 20,000 |
| `sha256` | `a61d34a0…` | `90ff0bb5489e09cbe9768d65b42246c2847970f9aab9ff371f56b6cd92113bc0` |
| artifact | `build-linux/mttl-w01-2.0.15-abayoumy-notimers.fwr` | `build-linux/mttl-w01-2.0.17-abayoumy.fwr` |

Repo layout followed the same movement: the live series is `patches/0001…0005`
(2.0.15 series archived in `patches/2.0.15/`, see `patches/README.md`), the shipped
line became branch `archive/protection-v2-2.0.15`, the bundle was refreshed
(7,086,990 B, now also carrying the `v2.0.17` tag), and the flashed strips are
unchanged at `abayoumy-notimers`.

## Commit 6: the lock gates every command path (2026-10-19) — build `abayoumy-lock`, flashed to both strips

**The problem, as observed on hardware.** The padlock in the web UI disabled the
*physical button* of that outlet and nothing else. `control_enqueue()` — the one
queue every command goes through — filtered its channel mask by `local==2`:

    mask = local==2 ? (15u & ~device.settings.button_lock) : 15u;

`local` is the origin of the command: 2 = physical buttons, 0 = web UI and
HA/MQTT, 1 = the auto-off timers and the schedules. So only a button press (or
the ALL button) consulted the lock; the web UI toggle, the HA switch, an HA
"all on/off", a timer expiry and a schedule rule all switched a locked outlet
anyway. Protection was already outside the queue and unaffected.

**What changed** — one gate, plus the plumbing that makes the resulting state
visible and consistent:

| area | change |
|---|---|
| `sdk_worker.c` `control_enqueue` | the mask is no longer conditional: `15u & ~button_lock` for *every* `local`. A locked channel is refused on every path, an ALL command (channel 4) then applies to the unlocked outlets only, and a fully locked strip refuses every command |
| refusal feedback | a refused **manual** command (local 0 only) sets `lock_flash_requested` for the blamed channel — all locked channels for channel 4 — and wakes the relay task, so the channel LED runs the same three on/off edges a locked button press already ran. Timer and schedule refusals stay silent: they retry on every worker pass and would blink forever |
| `settings.c` + `settings.h` | a locked outlet cannot carry an auto-off timer: `mttl_settings_valid` refuses one (mirroring the pre-existing schedule/timer conflict rule) and `mttl_settings_unpack` clears a timer found behind a lock bit, so a record written by the previous firmware still loads instead of being rejected. `settings.h` documents the new meaning of `button_lock` |
| `ha_discovery.c/.h` | new entity index 26 (`MTTL_HA_LOCK_INDEX`), `MTTL_HA_ENTITIES` 26 → 27: a retained diagnostic sensor on `…/lock` whose state is the list of locked outlets and whose `json_attr_t` carries the mask |
| `device_app.c/.h` | publishes `{"mask":N,"locked":"1,3"}` (`"none"` when nothing is locked) on `…/lock` whenever the lock changes and after every reconnect (`mqtt_lock_mask` starts at 0xff) |
| `ui/live.js`, `ui/timer.js`, `ui/scheduler.js` | the padlock tooltip says what the lock really does; a locked outlet's toggle is disabled; the timer editor treats a locked channel like a schedule conflict (inputs disabled, value forced to 0, note *"Locked outlet. Unlock it before registering a timer."*); the scheduler hint notes that a locked outlet is not switched by its schedules either |

**Schedules stay data.** Unlike a timer, a *rule* that targets a locked outlet is
neither refused nor deleted: it simply cannot fire while the lock is set, and it
works again after unlocking. Refusing it at save time would force the user to
delete rules before locking an outlet and re-create them afterwards — worse than
a rule that is temporarily inert. The firmware skips it through the same gate.

**Home Assistant.** Entity 26 is `sensor.mttl_<short>_lock`: state = the locked
outlet list (`"1,3"`, `"none"` when nothing is locked), attribute `mask` = the
same nibble as `button_lock`, `entity_category: diagnostic`, no expiry — it
describes a setting, not a sample. A refused switch command needs no special
handling, because the HA switches are `optimistic: false`: Home Assistant snaps
back to the device's real state on its own.

**Verification.** Host suite **249 checks / 0 failed** (was 227; the new checks
cover the refusal, the load-time normalisation and the lock entity), `git am` of
`patches/000[1-6]-*.patch` on a pristine `v2.0.17` reproduces tree `3d273c62…`
exactly, and a second build on CT 106 with the same id reproduced the artifact
`sha256`:

| | rebased `abayoumy` | **lock `abayoumy-lock`** |
|---|---|---|
| gap to MSP | 1428 | **764** |
| `.fwr` bytes | 333,620 | **334,284** |
| UI assets served | 3 | 3 |
| UI gzip total | 19,168 | **19,429** / 20,000 |
| `sha256` | `90ff0bb5…` | `b65c0e30e1c9ffb641b406de5e652d4721fc02baa70fa3ce5cd1335b81d6067b` |
| artifact | `build-linux/mttl-w01-2.0.17-abayoumy.fwr` | `build-linux/mttl-w01-2.0.17-abayoumy-lock.fwr` |

**Build id.** `abayoumy-lock` instead of reusing `abayoumy`: the two 2.0.17 images
differ in content, and sharing a label would make "is it already installed?" and
any support question ambiguous. The marker stays the user's; only the suffix
distinguishes the lock release.

**Not yet exercised on hardware.** After flashing, confirm: lock one outlet, then
try the web toggle, the HA switch, HA "all", a timer and a schedule on it — each
must be refused, the manual attempts must flash that channel's LED three times,
`sensor.…_lock` must name the outlet, and an over-limit load on the *locked*
outlet must still be cut.

## Commit 7: the dashboard drops Korean (`f88dd17`, 2026-10-19) — build `abayoumy-en`, built and host-verified, not flashed

The dashboard carried a second, Korean dictionary and a header button that switched between the two
languages. The choice was stored in `localStorage`, in the `language` byte of the settings record, in
the OTA page's own word list, and every user-visible string existed twice — once as the KO arm of a
`cond ? en : ko` ternary, or as the first argument of a `text(ko,en)` / `logEvent(ko,en)` helper. The
strip is used in one language, so all of it is gone.

| file | before | after |
|---|---|---|
| `ui/i18n.js` | `ko` + `en` dictionaries (5,941 B raw, 2,560 B gzip in the filtered device copy) | one `en` dictionary (2,847 B raw, 1,360 B gzip); `text(language,key,args)` keeps its three-argument shape so no call site and no build step changed, and ignores the language argument |
| `ui/live.js` | `let language`, `preferences.language`, per-row `ko`/`en` log messages, ~19 KO/EN ternaries | no `language`; the session log keeps one message per row; `settingsBody()` writes `language:1` and the save-confirmation loop compares against `1` |
| `ui/app.js` (preview only) | `preferences.language`, `applyLanguage()`, the `#language` click handler | `applyText()`, `documentElement.lang='en'`, no preference |
| `ui/timer.js`, `ui/scheduler.js` | a `text(ko,en)` helper and 44 KO/EN pairs, no helper left | plain English strings, the `language` mount parameter is gone |
| `ui/ota-live.js` | `words={ko:[…],en:[…]}`, `words.ko.push(…)` and a re-render hooked to the language button | one `words` array; the hook is gone |
| `ui/index.html` | 638 Hangul characters of static fallback text, the `#language` button + its CSS rule, `<html lang="ko">` | English fallbacks taken from the dictionary, no button, `<html lang="en">` |
| `ui/ota-test.html` | bilingual Korean/English test page | English |
| `build_assets.py` | bilingual i18n filtering, Korean fallback rewrites, `messages['ko']` bookkeeping | single-language filtering; the device build asserts **no Hangul** in any gzipped asset |
| `firmware/settings.c` | `mttl_settings_default()` left `language = 0` (Korean) | writes `language = 1` (English) for a fresh record |

The settings record is deliberately still **v8 and unchanged**. `mttl_settings_valid()` keeps
accepting `0`, so a strip that already stored Korean loads its record normally instead of being
rejected, and the byte stops mattering: the dashboard is English whatever it says, and every save
writes `1`. No migration, no version bump, no downgrade hazard.

Measurements (CT 106, `MTTL_OTA_BUILD_ID=abayoumy-en`, two builds byte-identical):

| | |
|---|---|
| `.fwr` | **330,900 B** (was 334,284 B for `abayoumy-lock`) |
| sha256 | `afb5fd1b0e32a6ce61d22e47b3a5715e0f75fc5818970c28b0776f6d39770fcb` |
| `static_gap_to_msp_bytes` | **4148** (was 764) |
| UI gzip | **16,039 B** of the 20,000 B budget (was 19,429 B): `/` 4,459 (was 4,818), `/i18n.js` 1,360 (was 2,560), `/live.js` 10,220 (was 12,051) |
| checks | host suite 249 / 0 failed; the three dashboard/OTA node tests pass; `node --check` clean on every UI script |

So the Korean dictionary and the inline pairs were worth **3,390 B of gzipped UI**, and the link gap
grew from 764 B to 4,148 B — the first real headroom the series has had since the HA limit-control
surface was measured at ≈1,004 B (see the section below). Flashing this build is the next step; until
then both strips keep running `abayoumy-lock`.

## HA control surface for the limits — measured, does not fit (decided: not built)

Wiring the limits into HA as four MQTT `number` entities was implemented on
`wip/ha-limit-entities` (`patches/wip-0002-ha-limit-entities-does-not-fit.patch`):
discovery entries, `…/chcurrentN/set` command parsing, retained state
publication, and a staged NOR write reusing the timer path.

It **costs 1,004 B and the link fails**:

```
ld: application overlaps reserved MSP budget      (ASSERT(__HeapLimit <= __mttl_msp_limit))
```

Measured overflow (diagnostic build with the MSP limit temporarily raised, then
restored): `__HeapLimit` lands **344 B past** the real limit — i.e. gap
660 → **−344**. Only 660 B of budget existed and the surface needed ~1 KB.

**Resolved on 2026-10-17: the decision was trip visibility only (option C in
`HA-LIMITS-WIRING.md`), which cost 304 B and left 356 B.** The limits stay
settable in the device's own web UI, which shows all four per-channel limits, the
three aggregate limits and the enable mask together — better than four HA sliders
would. The full HA control surface (~1,004 B, or ~600 B as HA-YAML entities in
mA) remains parked on `wip/ha-limit-entities` and does not fit. A zero-firmware-
cost REST sensor for *reading* the limits is still available if wanted.

## Caveats

* **Downgrade**: **both** strips have now persisted a v8 record, so firmware
  ≤ 2.0.14 can no longer read their settings — it would fall back to defaults
  (credentials lost, setup AP). Unavoidable with a persisted-format version bump;
  re-provisioning via the setup AP is straightforward (`addon/tools/provision.py`).
* Upstream README: *"Failed installation may require debugger recovery"* — there
  is no automatic slot rollback, so flashing a strip that carries a real load
  (PVE host, TV) is a production risk. The device's own web UI keeps offering the
  stock `1.0.66` / local `1.0.68` restore images, which is the practical recovery
  path.
* The build is not byte-reproducible across runs: `build_id` defaults to
  `secrets.token_hex(8)`, embedded twice, so two builds of one tree differ in
  exactly 32 bytes (the two 16-byte ids plus the trailing FWR checksum) and in
  the reported build id. Everything else is byte-identical, and sizes are stable.
  Set `MTTL_OTA_BUILD_ID=<name>` to pin it (the shipped builds used `abayoumy`, then
  `abayoumy-notimers`, and the 2.0.17 rebase uses `abayoumy` again); a clean rebuild
  with the same name reproduced the manifest's `sha256` exactly, every time.
* The per-outlet limit is **live, not opt-in**: the overcurrent checkbox (bit 1)
  is on, and there is no separate per-channel enable bit any more. Bit 3 is
  reserved — a stored record that has it set still loads, but nothing reads it.
  The stored v8 per-channel values are inert by design: the firmware judges each
  channel against `current_ma` and the UI mirrors that value into them.
* A **downgrade to a pre-commit-5 build** (isolation / trip / limit-per-outlet /
  `abayoumy`) brings the eight timer entities back on the next reconnect: that
  firmware still announces them, and HA re-creates what the strip republishes.
  Re-clear the 16 `…/config` topics afterwards, or stay on `abayoumy-notimers`.
* A **downgrade back to the isolation build** would read those mirrored values as
  its per-channel limits (16 A each, the same value) and would then cut all four
  whenever one outlet was over — the pre-commit-3 behaviour. That build is kept at
  `build-linux/mttl-w01-2.0.15-isolation.fwr`.
* **Downgrading from the 2.0.17 build to the 2.0.15-based one** (`abayoumy-notimers`,
  i.e. the build the bundle keeps as `archive/protection-v2-2.0.15`) is safe for the
  settings record — both carry the same v8 codec — but the older UI is what you get
  back: no sequential script loader, and the OTA page reverts to the 2.0.15
  reconnect behaviour. Nothing in HA changes either way.
* **The 2.0.17 build is verified the same way as the previous ones but on a new
  base**: tree equality between the Mac clone and the builder, 249 host checks
  (227 for the rebase, +22 for the lock), byte-identical gzipped UI against the
  manifest on both strips, and the invariant above. Since 2026-10-19 both strips
  run it (`abayoumy-lock`), and the lock's behaviour was exercised over the API on
  `10.0.0.53` — see *Sixth flash*. What is still untested on hardware is the LED
  triple-flash and a protection trip, the two items in *Not done yet*.
* **The lock changes what "turning an outlet on" means** — after this build, an
  outlet that is locked cannot be switched on remotely at all, including by the
  HA "all" switch and by a schedule. That is the requested behaviour, but it is
  also the one way to make a strip *look* broken: if an outlet stops responding to
  HA, check its padlock (and `sensor.mttl_<short>_lock`) before the logs. The lock
  is stored in the same settings record, so it survives a reboot and an OTA.
* **Downgrading from the lock build to a pre-commit-6 build** (the rebase
  `abayoumy`, or `abayoumy-notimers`) reverts the lock to "physical button only"
  and, more visibly, leaves the retained `homeassistant/sensor/mttl_<short>_lock/config`
  topic behind: the older firmware never publishes index 26 again, so Home
  Assistant keeps a lock entity that never updates. Clear that topic (and
  `…/lock` state) if you downgrade for long, the same way the timer topics had to
  be cleared when commit 5 was flashed.

## Not done yet

* **Flash the lock build — done, 2026-10-19.** Both strips run
  `build-linux/mttl-w01-2.0.17-abayoumy-lock.fwr` (334,284 B, `b65c0e30…`, build
  id `abayoumy-lock`): 53 first, 54 after it settled, `PVE1` powered throughout.
  Evidence and numbers in *Sixth flash* above. The superseded
  `2.0.17-abayoumy.fwr` was never flashed and needs no flash: `abayoumy-lock` is
  that build plus commit 6.
* **Two hardware checks a remote session cannot finish:**
  * **the three LED edges** on a refused manual command — every refusal itself is
    proven (see the *Sixth flash* table), but only eyes can confirm the blink that
    tells the user *why* the outlet did not move. Same effect as pressing a locked
    channel's own button.
  * **a protection trip on a locked outlet** — that is the one interaction between
    the lock and the safety logic, and the one that must never regress: protection
    writes the relay directly and never enters the command queue, so a locked
    outlet must still be cut. Do it as part of the trip test below.
* **Hardware trip test** — run it **on the flashed `abayoumy-lock` build**. Needs
  a ≥ 220 W (> 1 A) load on one outlet (a hair dryer trips it decisively). There is
  no per-channel enable bit to arm any more: **lower the current limit itself** to
  1 A (the slider's floor), plug the load into one outlet and switch it on.
  Expected: only that outlet loses power (`cut_mask` = its bit), `channel_mask`
  names it, and `sensor.mttl_9d270aa_protection` goes `0` → that bit (1/2/4/8) with
  the cause in `reason`, then back to `0` once the outlet is switched on again
  (re-energising re-arms the notification). Afterwards restore the limit to 16 A.
  All strip loads are currently far below 1 A, so this cannot happen by accident.
  Note this also exercises the **new** policy: with the limit at 1 A the aggregate
  trip fires in the same round as the per-channel one, and the blamed outlet must
  be cut **alone** rather than all four — that is the behaviour commit 1 introduced
  and the one thing only real hardware can confirm. Do it on the LivingRoom strip:
  `sensor.mttl_9d270aa_protection` there, `sensor.mttl_941678b_protection` on the
  BedRoom strip, which would trip the Proxmox host's outlet.
* **Runtime stack after the lock build — checked, fine.** `payload[24]` grew to
  `payload[40]` in the worker's publish path and the gate gained two `int` locals,
  so it was measured on the flashed build: `worker_observed_stack_descent_bytes`
  = **2168 B** on both strips (field is in **`/api/memory`**, not `/api/device`)
  against the 1536-word (6144 B) `mttl_network` task — ~35 % used. The link-time
  gap (764 B) is static RAM; this is the running figure, and both have headroom.
* **HA control surface for the limits** — decided against (option C chosen);
  parked on `wip/ha-limit-entities`, 1,004 B and a link failure.
* **BedRoom strip (`10.0.0.54`)** runs the same `abayoumy-lock` build (flashed
  2026-10-19, `PVE1` on and powering the Proxmox host throughout, no trip). Its
  trip entity is `sensor.mttl_941678b_protection`, its lock entity
  `sensor.mttl_941678b_lock`. **`PVE1` is locked** (`button_lock = 1`, a setting
  that was already on the old firmware and carried straight over — it is the
  BedRoom strip's own choice, not something this build added), so now that the lock
  is authoritative no software command can switch that outlet in *either*
  direction: not the web UI, not HA, not the ALL switch, not a timer. That is the
  requested behaviour, and the way back is deliberately not a dead end —
  **the lock never blocks configuration**, so unlock the outlet (`--lock 0`, the
  web UI's padlock, or the physical button) and then switch it on. Worth knowing
  before a support call: if `PVE1` is ever off, *unlock first, then switch on*.
* **Recovery is unchanged**: `restore_versions: ["1.0.66","1.0.68"]`, and the
  fallback slot holds the previous build until the next flash (an OTA swaps slots,
  it is not a rollback — flashing the older image again is the rollback).
* **Timers out of Home Assistant — done (commit 5, `6ff0735`), 2026-10-18**: the
  firmware no longer announces the eight timer entities and no longer publishes
  `…/timerN` or `…/timer_remainingN`, so a reconnect can no longer bring them back.
  The 16 retained `…/config` topics and the 16 orphaned `…/timer…` state topics were
  cleared in HA; both strips stayed at 26 entities across the post-flash republish
  (68 → 52 captured ids). It freed **928 B** — gap 748 → **1676 B**, more than the
  entire parked HA limit control surface had needed.
