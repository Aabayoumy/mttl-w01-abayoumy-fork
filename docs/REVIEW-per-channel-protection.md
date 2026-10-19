# Review: experimental per-channel protection patch

> **Historical — superseded.** This reviews the *abandoned* first attempt
> (per-channel current **and** power, kept as `mttl_experimental_changes.patch`),
> which never shipped. The shipped feature is described in
> `FEATURE-per-channel-current.md` and its patch is
> `patches/0001-per-channel-current-isolation.patch`.

Scope: the 7 files modified in `source/standalone/firmware/` (patch saved as
`mttl_experimental_changes.patch`). Built on the LXC.

## Base / rebase log

The patch was originally cut against `main` = `ebfb39d`, then rebased onto the
`v2.0.15` release tag at the user's request.

| step | base | commit |
|---|---|---|
| original | `main` `ebfb39d` (3 commits past the tag) | — |
| rebased | tag `v2.0.15` = `4578e6d` | `0468c05` |

`experimental/per-channel-protection` is a **pure base move**: all 7 touched files
are byte-identical between `4578e6d` and `ebfb39d` (verified by blob hash), and the
rebased diff is byte-for-byte the original patch. Same commit hash on both the Mac
and the LXC build box.

**"2.0.15" is ambiguous** — the version string, the release tag and `main` are not
the same thing:

- tag `v2.0.15` = `4578e6d` "Release 2.0.15 HA timers and reduce sensor MQTT traffic"
- `main` = `ebfb39d`, three commits later, still version-stringed `2.0.15`:
  - `5b06933` **functional** — "Handle identical OTA uploads as already installed in
    2.0.15"; touches `sdk_ota_runtime.{c,h}`, `sdk_web.c`, `ui/ota-live.js` and
    regenerates `firmware/comMTTL-W01_2.0.15.fwr` (333204 → 333412 bytes)
  - `c363f0a`, `ebfb39d` — README/docs only

Basing on the tag therefore **drops `5b06933`**. Pick the base deliberately.

## Verdict

**Do not ship. The patch does not compile, and the issues that would survive a
compile fix are worse than the compile error.**

```
BUILD_EXIT=1
protection.c:10:6: error: 'mttl_protection_config' has no member named 'temp_enabled_per_channel'
protection.c:17:10: error: 'mttl_protection_config' has no member named 'temp_enabled_per_channel'
```

## What the upstream code already does (so the goal is narrower than assumed)

`protection.c` at HEAD already implements local protection with:

- temperature, **total** current, **total** power, bitmask-enabled, persisted
- a 2-consecutive-round confirm before tripping (`s->current_count` / `power_count`)
- `error_mask = enabled & ~valid & 7` → which enabled protections lack fresh data
- power compared as `p > power_w * 1000` (samples are **mW**, thresholds **W**)
- temperature handed in per-channel already (`mttl_protection_temperature` is
  called with `last_channel`)

So the genuinely *new* thing is per-channel rather than aggregate current/power
thresholds. Per-channel current and power samples already exist
(`s->current[ch].value`, `s->power[ch].value`).

## Blocking

| # | File | Defect |
|---|---|---|
| B1 | `protection.c:10,17` | Uses `c->temp_enabled_per_channel`, a field removed from `protection.h` in the same patch. Hard compile error. |

## Critical — silent, would ship if only B1 is fixed

| # | File | Defect | Consequence |
|---|---|---|---|
| C1 | `settings.c` | Version stays `out[0]=7` but the protection block grows 5 → 19 bytes, so the v7 tail is **78** bytes while `mttl_settings_unpack` still asserts `body[0]==7 ? 66`. Pack and unpack are mutually incompatible. | Stored settings are rejected on load → device falls back to **defaults: Wi-Fi, MQTT broker/credentials, channel names all lost**, back to SoftAP setup. The web save path would also reject its own body. Looks like a clean flash, then wipes config. Needs version **8** with the v4–v7 readers left intact. |
| C2 | `protection.c:95` | `power_w[i] > c->power_w[i]` compares **mW against W**. Upstream's correct form is `p > c->power_w*1000`. | Per-channel power protection trips at **1/1000** of the configured load → spurious ALL-OFF on essentially any load. |
| C3 | `protection.c:101` | `reason \|= (128 << i)` yields 128/256/512/1024, but `mttl_protection_state.reason` is `uint8_t` → truncated to 0. | Trip is reported with no reason; the value collides with the 0x08–0x10 numbering used for *enable* bits. `unsigned` return still requests ALL OFF, so only reporting breaks. |

## Regressions to existing features

| # | File | Defect | Consequence |
|---|---|---|---|
| R1 | `ha_discovery.c:39` | `component` changed from `index<5?"switch":(index<25\|\|index>=29)?"sensor":"number"` to `(index<25\|\|index>=33)?"sensor":(index<33?"binary_sensor":"number")`. Indices 25–32 now resolve to `binary_sensor`. | The **existing** timer entities 25–28 (`number`) and 29–32 (timer-remaining `sensor`) are re-announced under the wrong component → duplicate/broken timer entities in HA. |
| R2 | `ha_discovery.h` | `MTTL_HA_ENTITIES` 33 → 49, but state publishing only rotates indices **5..24** (`MTTL_HA_SAMPLE_ENTITIES 25`, `device_app.c:72`) and `mqtt_sensor_value[MTTL_HA_SENSOR_COUNT=20]` covers exactly indices 5–24. | Entities 25–48 are announced to HA and then never receive a state → **24 permanently `unknown` entities**. The 8 new `number` entities additionally need `cmd_t` handlers in `mqtt_command.c`; none were added. |
| R3 | `protection.c` | `error_mask` recomputation (`enabled & ~valid & 7`) removed from `mttl_protection_round`; `sdk_meter.c` instead preserves old bits. | `error_mask` latches permanently and no longer means "stale reading". `/api/status` + `/api/config` expose `protection.error` → UI reports stale faults. |

## Incomplete / contract mismatches

| # | File | Defect |
|---|---|---|
| I1 | `device_app.c:108` (not patched) | `"current":%u` / `"power":%u` cast `s->protection.current_ma` / `power_w`, now arrays → **decay to pointers**, printing addresses as thresholds. Compiles (warning only), API silently wrong. |
| I2 | `ui/live.js:69` + save-verify list (not patched) | Still uses the scalar contract `{enabled,temperature,current,power}` and verifies `['enabled','temperature','current','power']`. Against the new API the UI shows garbage and its "Flash save not confirmed" retry never matches → UI reports a failed save. |
| I3 | `selftest.c` | Mangled: `c->power_w[0]` on a struct value, `mttl_protection_default(&c) \|\| 1` (void in `\|\|`), `mttl_protection_config ctmp = mttl_protection_default(&c2)` (void initializer), bare `{0,0,0,0}` compound literals as call arguments (syntax error), `.merged` member on `unsigned`, duplicate declarations of `m`/`c2`. |
| I4 | `protection.c:45` | `if(!s \|\| !mttl_protection_valid(c)) return 0;` → an out-of-range config silently disables protection instead of failing safe. Pre-existing, but a safety feature should request ALL OFF (or reject the config at the API boundary). |
| I5 | `protection.c:56,70` | Total thresholds reuse `current_ma[0]` / `power_w[0]`, conflating channel 1's per-channel limit with the aggregate limit. Original had separate scalars. |

## Hygiene

- `selftest.c` is **not referenced by any build script** (only its own header
  includes it) — the repo's only test is dead code. Restoring it and actually
  wiring it in (it needs only `protection.c` + `settings.c`, so it can build for
  the host) would have caught B1, C2 and C3 immediately.
- Build output dir is not cleaned; after the failed build the previous pristine
  `.fwr` was still present in `standalone/results/network-ota-test/`.

## Required design, if this feature is wanted

1. **Settings version 8.** Keep v4–v7 readers untouched; add per-channel arrays as
   a *new* tail section with an explicit new length. Bump `MTTL_SETTINGS_BODY_MAX`
   checks accordingly.
2. **Keep aggregate thresholds separate** from per-channel ones — do not overload
   channel 0.
3. **Units:** per-channel power compares `power_w[i] > (int32_t)c->power_w[i]*1000`.
4. **Widen the trip report** (`uint16_t`/`uint32_t reason`, or a channel bitmask
   + cause) and update `device_app.c` JSON + HA/web consumers together.
5. **Keep `error_mask` recomputed** each round.
6. **Either** extend HA properly — `MTTL_HA_ENTITIES`, `MTTL_HA_SAMPLE_ENTITIES`,
   `mqtt_sensor_value[]` sizing, `publish_sample()` rotation, and `mqtt_command.c`
   handlers for the new `number` set topics — **or** ship v1 with web-UI-only
   configuration and no new HA entities. The web-only route is far less work and
   avoids dead entities.
7. Update `device_app.c` settings JSON + `ui/index.html` + `ui/live.js` in the same
   commit as the struct change.
8. Restore `selftest.c` and add it to a host-side test target.

## RAM note

Baseline `static_gap_to_msp_bytes = 1620`. `mttl_settings` is embedded in the
device struct, so per-channel config costs ~12 bytes of the settings buffer
(negligible), but the build asserts `__HeapLimit <= __mttl_msp_limit`, so any
sizable RAM addition fails the build rather than silently corrupting the stack.
Treat that 1.6 KB as a budget to be spent deliberately.
