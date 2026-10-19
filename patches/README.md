# patches/ — the fork's commit series

Each patch exists twice: `.patch` is `git format-patch` output (apply with
`git am`), `.diff` is the plain `git diff` of the same commit (for reading).

## Live series — applies to upstream **v2.0.17** (`311663e`)

Base: upstream tag `v2.0.17` (identical to upstream `main`). Result: branch
`feature/protection-v2`, tree `3d273c6257ac67ef1c61000d66a193ba69e180a4`.

| patch | commit | what it does |
|---|---|---|
| `0001-per-channel-current-isolation` | `fc6338c` | per-outlet current limits; a trip cuts only the blamed outlet |
| `0002-protection-trip-visibility` | `aa68f78` | one HA protection sensor (index 25; `0006` later appends the lock sensor) |
| `0003-current-limit-every-outlet` | `c7e8a5e` | the limit applies to every outlet, not one |
| `0004-ui-note-and-build-id` | `24a34dd` | protection note removed; named OTA build ids |
| `0005-timers-are-not-ha-entities` | `9a05d83` | timers stop being HA entities (34 → 26 entities) |
| `0006-lock-every-command-path` | `cf02922` | the lock gates every command path; HA lock sensor (26 → 27 entities) |

Verified: `git am patches/000[1-6]-*.patch` on a clean `v2.0.17` checkout
reproduces tree `3d273c62…` exactly, and the host suite passes (249 checks, 0
failed).

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
