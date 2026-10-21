# patches/ — the fork's commit series

Each patch exists twice: `.patch` is `git format-patch` output (apply with
`git am`), `.diff` is the plain `git diff` of the same commit (for reading).

## Live series — applies to upstream **v2.1.0** (`2932fb8`)

Base: upstream tag `v2.1.0` (upstream `main`). Result: branch
`feature/protection-v2-2.1`, tree `164b27dc885a1dec7e063aa0d5180651ad57fab5`.

| patch | commit | what it does |
|---|---|---|
| `0001-per-channel-current-isolation` | `c678dac` | per-outlet current limits; a trip cuts only the blamed outlet |
| `0002-protection-trip-visibility` | `7229d41` | one HA protection sensor (index 25; `0006` later appends the lock sensor) |
| `0003-current-limit-every-outlet` | `9771e87` | the limit applies to every outlet, not one |
| `0004-ui-note-and-build-id` | `f2a47bc` | protection note removed; named OTA build ids |
| `0005-timers-are-not-ha-entities` | `6bc9f85` | timers stop being HA entities (34 → 26 entities) |
| `0006-lock-every-command-path` | `c95df42` | the lock gates every command path; HA lock sensor (26 → 27 entities) |
| `0007-english-only-dashboard` | `8b5ee54` | English-only dashboard; Korean dictionary, inline `ko`/`en` pairs and the language selector removed (entity list unchanged) |
| `0008-arabic-main-page-device-language` | `f4b4d05` | Egyptian Arabic for the main page only; language stored in the settings record |
| `0009-settings-import-legacy-record` | `98d6fae` | one-time import of the 2.0.x settings record into the 2.1.0 journal |
| `0010-settings-tab-arabic-pages` | `ce49d0c` | Wi-Fi/MQTT/Firmware/Logs behind one Settings tab with a chip row; Egyptian Arabic for the power pages (editors and event log included); the Settings group stays English and LTR; RTL at the document root |

Verified: `git am patches/0001-*.patch … 0010-*.patch` on a clean `v2.1.0`
checkout reproduces tree `164b27d…` exactly, the host suite passes (265 checks,
0 failed) and the four dashboard/OTA/i18n node tests pass (i18n: 9 checks).

## Upstream 2.1.0 storage (why `0009` exists)

Upstream replaced the two 4 KiB settings sectors with a 128-record append
journal (1 KiB records, CRC32 + sequence, two 64 KiB banks at `0x70000` and
`0xE0000`), erases in 4-record groups and skips a write when the record is
byte-identical. Energy is now flushed hourly (local-clock high-water, 5 s retry)
instead of every 5 minutes. OTA grew a `first_end` so a slot-A image stops at
`0x70000` and can never erase the journal.

Upstream deliberately does **not** migrate the 2.0.x record, so the first 2.1.0
boot starts from defaults: Wi-Fi, MQTT, names, limits, lock, timers, schedule,
language and energy are lost and the strip returns to its setup AP. `0009`
reads the newer of the two legacy 2 KiB slots (`0xEE000`/`0xEF000`) through
`mttl_settings_choose()`/`mttl_settings_extract()`, writes it into the journal,
and then erases both legacy sectors so the import runs at most once and cannot
resurrect stale settings. `host_test` pins the decode half; the flash half
reuses the journal writer's own read-back path.


## What "locked" means (patch 0006)

A locked outlet is not switched by **any** command path: physical buttons, web
UI, HA/MQTT (single and ALL), the device-local auto-off timers and the
schedules. Two things stay outside that rule:

- **Protection** never enters the command queue (`protection_off()` writes the
  relay state directly), so a locked outlet is still cut for over-temperature,
  over-current or over-power. Re-energising a cut outlet needs an unlock first.
- **A locked outlet cannot carry an auto-off timer**: `mttl_settings_valid()`
  refuses one (mirroring the schedule conflict rule) and
  `mttl_settings_unpack()` clears one found in a stored record so an older
  record still loads. A *schedule rule* that targets a locked outlet is kept as
  data and simply cannot fire; it works again after unlocking.

All of it is one gate: `control_enqueue()` in `sdk_worker.c` masks by
`button_lock` for every `local` value (0 = web/HA, 1 = timer/schedule,
2 = buttons). A refused manual command (local 0) flashes the same three LED
edges a locked button press flashes; timers and schedules retry every pass, so
they are dropped silently.

When rebasing, re-check this gate: any new command path must route through
`control_enqueue()`, and a reintroduced `local`-based bypass re-opens the hole
the feature closes.

Two things to know when this series is rebased onto a newer upstream UI:

- `0004` must relax **three** `^[0-9a-f]{16}$` build-id guards in
  `ui/ota-live.js` (post-OTA reconnect check, `refreshStatus()` guard,
  current-build label). With a *named* build id left as 16-hex, the OTA page
  never becomes ready and post-OTA auto-reload never fires. Our guard is
  `/^[0-9a-z][0-9a-z._-]{3,31}$/`.
- `0005` discards upstream's timer work in `device_app.c/.h` and
  `integration_mock.c` (2.0.16 "configured duration while OFF"). Keep our
  deletion and drop the `mqtt_remaining_minutes[4]` cache field that otherwise
  merges back in unused.

The remaining `-build-([0-9a-f]{16})\.fwr` filename pattern is deliberately
untouched: it only pre-fills the "Build verification" line when a vendor-named
file is uploaded.

## Archived series — applies to upstream **v2.0.15** (`ebfb39d`)

`2.0.15/` — the series the currently flashed strips were built from
(build id `abayoumy-notimers`), kept for reference and reproducibility only.

## Parked

`wip-0002-ha-limit-entities-does-not-fit.patch` — the abandoned approach of
exposing per-channel overcurrent limits as HA number entities (does not fit the
MQTT payload budget). Written against the 2.0.15 base; needs a rebase if it is
ever picked up again.
