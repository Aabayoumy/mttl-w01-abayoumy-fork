# Wiring the per-channel limits into Home Assistant — measured cost and options

The current limit works on the strip and applies to **every outlet** as well as to
the total, so there is no per-outlet setting to wire up any more — one limit in
the device web UI covers all four outlets. Putting the limits into Home Assistant
as proper MQTT `number` entities was implemented and then **measured against the
remaining firmware RAM budget**. It does not fit. This note records the numbers
and the realistic options, because the choice is a product decision, not a
technical one.

**Decision (2026-10-17): option C, trip visibility only — built, measured,
flashed to both strips (2026-10-18).** Details below; the parked branch and this
table are kept for the record.

Follow-up (2026-10-18, commit 5 `6ff0735`): the auto-off timers were removed from
the discovery table entirely, so a strip now announces **26** entities instead of
34 and HA keeps no timer entity — see the top of
`FEATURE-per-channel-current.md`. That change also **freed 928 B** of the same
budget this note is about.

Second follow-up (2026-10-19, commit 6 `cf02922`): the lock became authoritative
(every command path, not just the physical buttons) and it publishes its state, so
the table grew to **27** entities — the trip sensor at index 25 plus the new lock
sensor at index 26. See *The lock sensor* below. That change cost **664 B**, i.e.
gap 1428 → **764 B**; the discovery entity itself is the smaller part of it (the
gate, the refusal LED flash, the timer rule and the UI state account for the rest).

Third follow-up (2026-10-19, commit 7 `f88dd17`, build `abayoumy-en`): the dashboard is English only.
The entity list is **unchanged** (still **27** per strip), but dropping the Korean dictionary and the
inline `ko`/`en` pairs returned **3,390 B** of gzipped UI (19,429 → 16,039), so that build sits at a
**4,148 B** gap — the most headroom of the series. It is now flashed on **both** strips (2026-10-19,
`10.0.0.53` first, then `10.0.0.54`); on the BedRoom strip the `PVE1` outlet never dropped during
the OTA reboot, so the Proxmox host it feeds stayed up with an unbroken uptime.

## What shipped: option C, trip visibility only (measured 304 B)

The one thing HA is genuinely better at here is **telling you something was cut**.
That is what was built, on top of the firmware that isolates a trip to the blamed
outlet (`patches/0002-protection-trip-visibility.patch`; the flashed build `6ff0735`
= `abayoumy-notimers`, from `patches/0003-current-limit-every-outlet.patch` +
`patches/0004-ui-note-and-build-id.patch` + `patches/0005-timers-are-not-ha-entities.patch`,
gap **1676 B**). The patch series has since been rebased onto upstream `2.0.17`
(`311663e`, the dashboard-loading/post-OTA-reconnect release) without touching any
of this — same entity, same topic, same table — and that build (`abayoumy`) has a
**1428 B** gap. `abayoumy-lock` (commit 6, live on both strips since 2026-10-19)
adds the lock sensor and sits at **764 B**.

| | |
|---|---|
| entity | `sensor.mttl_<id>_protection` — "… Protection", `entity_category: diagnostic` |
| index | `MTTL_HA_TRIP_INDEX` = **25** (`MTTL_HA_ENTITIES` **27** since commit 6 appended the lock sensor at index 26; it was 26 after commit 5 removed the timers, and 33 → 34 when this sensor was appended) |
| state | **cut mask** of the outlets that are still off: bit 0 = outlet 1, bit 1 = 2, bit 2 = 3, bit 3 = 4; `0` = no cut in effect (all four cut = `15`) |
| attribute | `reason` — cause of the last trip: 1 temperature / 2 current / 4 power (latched, exactly as on `/api/device`) |
| topic | `<base>/protection`, **retained**, no expiry (a cut is a state, not a sample that can go stale) |
| payload | `{"mask":N,"reason":R}`; discovery sets `val_tpl: {{ value_json.mask }}` and `json_attr_t` on the same topic, so the mask is the state and the object becomes the attributes |
| published | on change of mask or cause, plus once after every (re)connect — it rides the existing 500 ms sensor rotation, so a cut reaches HA in about a second |
| cost | **304 B** (660 → **356 B** headroom), measured per object against the isolation build: `ha_discovery.o` +153, `device_app.o` +158, `protection.o` unchanged. The follow-up commit that made one limit cover every outlet gave **136 B back**, dropping the protection-tab safety note another **256 B**, and removing the timer entities another **928 B**: the flashed build `abayoumy-notimers` has a **1676 B** gap, and the 2.0.17 rebase (the UI fix costs 248 B) leaves **1428 B** |

Why it is not the ~200 B in the table below: the entity also carries the trip
*cause*. Dropping that attribute (plain numeric mask, no `val_tpl`) gives back
~95 B if the headroom is ever needed.

### Semantics that matter for automations

* The mask counts **only the outlets the last trip cut that are still off**.
  Restoring power returns it to `0`, which *re-arms* the entity — so a repeat
  trip fires a notification again. A latched "tripped" flag would notify once in
  the device's lifetime and never again.
* Outlet **names are deliberately not in the payload**: two outlets on this strip
  are both named `SBar`, names are free-form strings up to 64 bytes, and a first
  version that rendered them on the device measured **480 B** against this
  version's 304 B. The names are resolved on the HA side instead — the four
  switch entities already carry them.
* `reason` is latched from the last trip, so ignore it whenever the state is `0`.
* Notes: config byte-identical across the OTA, energy counters preserved, no
  spurious trip, every announced entity available in HA
  (`sensor.mttl_9d270aa_protection` = `0`, `mask`/`reason` attributes present).
  After the BedRoom strip (`10.0.0.54`) was flashed on 2026-10-18 it publishes the
  same entity as `sensor.mttl_941678b_protection` = `0`, so **both** strips report
  a cut in HA. Both strips now announce **26** entities — 52 captured ids over both
  (it was 59 before that sensor arrived and 68 while the timers were still
  announced): the trip sensor is still the new entity option C added, the eight
  timer entities per strip are simply gone, see the follow-up note above. The lock
  sensor (commit 6) takes that to **27** per strip once `abayoumy-lock` is flashed.

### The lock sensor (commit 6, `cf02922` — build `abayoumy-lock`, live on both strips)

The per-outlet padlock used to disable only the physical button; it now refuses
**every** command path (web UI, HA single and ALL, auto-off timers, schedules) and
protection still cuts. The state is published so HA can show which outlets are
protected from switching.

| | |
|---|---|
| entity | `sensor.mttl_<id>_lock` — "… Lock", `entity_category: diagnostic` |
| index | `MTTL_HA_LOCK_INDEX` = **26**, appended after the trip sensor (`MTTL_HA_ENTITIES` **27**) |
| state | the **locked outlet list** as text: `1`, `1,3`, `none` when nothing is locked (from `val_tpl: {{ value_json.locked }}`) |
| attribute | `mask` — the same nibble the device stores in `button_lock`: bit 0 = outlet 1 … bit 3 = outlet 4 |
| topic | `<base>/lock`, **retained**, no expiry (it describes a setting, not a sample) |
| payload | `{"mask":N,"locked":"1,3"}` / `{"mask":0,"locked":"none"}`; `json_attr_t` points at the same topic, so the list is the state and the mask an attribute |
| published | on change, plus once after every (re)connect — the app struct starts at `0xff` so a reconnect always republishes |
| cost | part of commit 6's **664 B** (gap 1428 → 764); the entity itself is one discovery branch plus one publish block, ~1/3 of that |

**Refused commands need no special handling.** The switches are announced with
`optimistic: false`, so when HA sends ON to a locked outlet the strip simply does
not move it, and HA reverts the entity to the device's real state on its own. The
strip also flashes that channel's LED three times (the same feedback a locked
button press gives) — useful when the command came from a script rather than a
dashboard.

**Reading it in a template.** `state_attr('sensor.mttl_9d270aa_lock','mask')` is
the nibble, so a Jinja check needs the `// 2 ** i` idiom (`mask // (2**i) % 2`)
because Jinja has no bitwise operators — the same trick the trip notification
uses. The text state is usually easier: `states('sensor.mttl_9d270aa_lock') != 'none'`.

**Caveat on a downgrade**: the config topic is retained, so flashing back to a
pre-commit-6 build leaves `sensor.mttl_<id>_lock` in HA as a stale entity that
never updates (the older firmware does not publish index 26). Clear
`homeassistant/sensor/mttl_<short>_lock/config` and `<base>/lock` if that happens.

**Live values after the flash (2026-10-19).** `sensor.mttl_9d270aa_lock` = `none`
/ `mask 0` on the LivingRoom strip (nothing locked). `sensor.mttl_941678b_lock` =
`1` / `mask 1` on the BedRoom strip: its `PVE1` outlet was already locked on the
*old* firmware, and the new one simply read that setting back and published it —
which is also the upgrade path any strip with an existing lock takes. That outlet
powers the Proxmox host, so it is worth stating the consequence: while it is
locked, **no** software command can switch it, in either direction. Recovery is
not a dead end, because the lock never blocks *configuration*: open the web UI,
unlock the outlet (or press its button), then switch it on. HA only needs to know
the state, which is exactly what this entity is for.


### Notification recipe (verified against this HA instance)

The template below was rendered through this HA instance's `POST /api/template`
for all 21 mask × cause combinations (masks 0/1/2/4/8/5/15 × reasons 1/2/4) and
named the right outlets and cause every time. Jinja has no bitwise operators,
hence the `// 2 ** i` idiom; the outlet names come from the switch entities, so
renaming an outlet on the device keeps this correct (and it survives the two
outlets that are both called `SBar`):

```yaml
automation:
  - alias: "MTTL-LivingRoom protection cut"
    triggers:
      - trigger: state
        entity_id: sensor.mttl_9d270aa_protection
    conditions:
      - "{{ trigger.to_state.state != trigger.from_state.state
            and trigger.to_state.state | int(0) > 0 }}"
    actions:
      - action: notify.persistent_notification        # replace with your notifier
        data:
          title: "MTTL-LivingRoom: outlet cut"
          message: >-
            {% set ns = namespace(n=[]) %}
            {% for i in range(4) %}{% if ((trigger.to_state.state | int(0) // (2 ** i)) % 2) == 1 %}
            {% set ns.n = ns.n + [state_attr('switch.mttl_9d270aa_sw' ~ (i+1), 'friendly_name')] %}
            {% endif %}{% endfor %}
            {{ ns.n | join(', ') if ns.n else 'no outlet cut' }} —
            {{ {1:'over-temperature',2:'over-current',4:'power limit'}.get(
                 trigger.to_state.attributes.reason, 'unknown cause') }}
```

Tell me if you want this installed in `configuration.yaml` (and which notifier) —
it is not in your config yet, so nothing notifies you today.

## What was implemented (parked on `wip/ha-limit-entities`)

| piece | detail |
|---|---|
| discovery | 4 × `number`, key `chcurrent1..4`, `cmd_t` `…/chcurrentN/set`, unit A, 1–16 A, step 0.1, `ent_cat: config` (`MTTL_HA_ENTITIES` 33 → 37 at the time; the base table is **26** since commit 5 removed the timers, so this parked patch needs a rebase anyway) |
| state | retained `…/chcurrentN` published like the timers, with a change cache so it is not spammed |
| command | `mttl_mq_current_command()` — strict topic + payload validation, amps with up to three decimals converted to exact milliamps (no float, no rounding), range-checked 1000–16000 mA |
| apply | `mttl_device_current_command()` → `protection_config_request()` stages a full settings image and lets the worker own the NOR write, exactly like `timer_config_request()` |
| tests | none added yet; would need `mqtt_command.c` + `mqtt_wire.c` + `mqtt_session.c` in the host harness |

Patch: `patches/wip-0002-ha-limit-entities-does-not-fit.patch` (~17 KB).
Branch `wip/ha-limit-entities` exists on the Mac clone **and** on the builder
container. It is not on `feature/protection-v2`, because it does not build.

## The measurement

```
ld: application overlaps reserved MSP budget        <-- ASSERT(__HeapLimit <= __mttl_msp_limit)
```

With the MSP limit temporarily raised (diagnostic only; file restored, tree
verified clean) the real gap comes out as:

| | bytes |
|---|---|
| budget available (`static_gap_to_msp_bytes` for the flashed isolation build) | **660** |
| cost of the HA surface as implemented | **1,004** |
| result: `__HeapLimit` | **344 past the limit** |
| after the chosen option C was built (for reference) | **356** left |
| flashed build after commits 3–5 — `abayoumy-notimers` | **1676** left |
| rebased onto upstream `2.0.17` — `abayoumy` (never flashed, superseded) | **1428** left |
| lock build, now live on both strips — `abayoumy-lock` | **764** left |
| English-only dashboard — `abayoumy-en` (built, not flashed) | **4148** left |

Rough split of the 1,004 B, from the diff and the build log (estimates, ±20 %):
discovery branch + literals ≈ 275, command parser ≈ 300, engine dispatch +
device apply + hook binding ≈ 150, staged NOR write ≈ 230, state publication
loop ≈ 180.

## The budget is shared with the web UI

`sum(gzip) < 20000` is asserted, and the gzipped UI sits in the same
`.ram_image2.text` RAM region as code. So **removing 1 byte of UI text buys
exactly 1 byte of code budget** — but gzip only recovers ~0.4 bytes per raw
byte, so paying 350 B would mean deleting ~900 raw bytes of UI prose (the
protection hints and labels). No dead code exists to reclaim: the bundle has no
unused top-level functions, unused i18n keys are already filtered out, and the
release link carries no test scaffolding.

## Options

Firmware costs are estimates from the measured attempt; anything chosen has to be
confirmed by a real build (the link guard makes a wrong guess fail loudly, not
silently).

| # | option | firmware cost | headroom left | what HA gets | what it costs elsewhere |
|---|---|---|---|---|---|
| A | **HA-only via the strip's existing REST API**: a `rest` sensor for the limits and trip state | **0** | 660 | visibility of limits + trips in dashboards/automations | no HA *control*; the web UI stays the place to change limits; setting needs a firmware endpoint because `/api/config` takes a binary packed body |
| B | **MQTT command + retained state topics, entities defined in HA YAML** (mA units, no discovery in firmware) | ≈ 600 | ≈ 60 | read **and** write from HA (native `number` entities, no discovery) | 4 entities to paste into `configuration.yaml` (I write them); mA instead of A; a decimal-A payload instead of mA would cost ≈ 150 B more, which does not fit |
| C | **Trip visibility only**: one MQTT entity for "protection tripped + which outlet" | ≈ 200 | ≈ 450 | HA notification when an outlet is cut — the thing HA is actually good at here | limits stay in the web UI |
| D | **Full discovery entities**, paid for by trimming UI prose | 1,004 | ≈ 0 | exactly the original plan (4 sliders in HA appear by themselves) | delete ~900 raw bytes of UI text (protection hints/labels); no budget left for anything else |
| E | **Leave the firmware as it is** | 0 | 660 | nothing new | limits and trips are visible in the device web UI only |

**Chosen: C** (measured at 304 B; that left 356 B, the later "one limit for every
outlet" change gave 136 B back, and commits 4–5 brought the flashed build to a
**1676 B** gap — see the top of this file; the 2.0.17 rebase leaves **1428 B**).

### Recommendation (as written before the decision)

**C, optionally C + A.** The protection is local and trips are rare, so the
high-value HA integration is *being told when something was cut* — that is ~200 B
and leaves real headroom for future fixes. Limit *changes* are a rare
configuration action, and the device's own web UI already does it better than a
HA slider would (it shows the temperature, current and power limits together, in
both languages, and the current limit is the per-outlet limit — so one field
covers all four outlets).

Option **B** is the right answer if you want to read *and* change the limits from
HA and accept YAML-defined entities in mA units — the only version that fits
without damaging anything else. **D** is technically possible but trades visible
UI text away and leaves zero slack; **E** is the safe default.

## Notes (kept for the record; the first bullet is now implemented)

* Done: the trip entity publishes on **change** of the live cut mask or the trip
  cause, is **retained**, and is republished on every reconnect — so HA sees the
  right value after a broker restart, an HA restart or a strip reboot. Verified
  on the live strip (`sensor.mttl_9d270aa_protection` = `0`, attributes
  `mask`/`reason`; 26 entities per strip since commit 5, 27 since commit 6
  appended the lock sensor).
* Done, 2026-10-18 (commit 5 `6ff0735`): the eight auto-off timer entities per
  strip are no longer announced and their state topics (`…/timerN`,
  `…/timer_remainingN`) are no longer published — timers stay a device feature
  (web UI, buttons, MQTT `…/timerN/set`). The 16 retained config topics and 16
  orphaned state topics were cleared in HA; a strip announces **26** entities and
  none of them is a timer.
* Done, 2026-10-19 (commit 6 `cf02922`, build `abayoumy-lock`): the lock refuses
  every command path and publishes its state — see *The lock sensor* above. A
  strip announces **27** entities from that build on; the 26 of the flashed build
  keep their ids and topics.
* Done, 2026-10-19 (commit 7 `f88dd17`, build `abayoumy-en`): the dashboard is English only — the
  entity list does not change (**27** per strip), but the freed gzipped UI moved the gap from 764 B
  to **4,148 B**, so the parked limit-control surface (≈1,004 B) would fit again if it were ever
  wanted.
* Still unbuilt, if ever wanted:
  * **HA control of the limits** (options B/D) — parked on `wip/ha-limit-entities`,
    does not fit today: ~1,004 B discovery-and-command version (link failure) or
    ~600 B as HA-YAML entities in mA.
  * **The per-outlet limit needs no HA representation at all**: there is no
    per-channel enable bit any more (bit 3 is reserved), the current limit judges
    the total *and* each outlet, and it is live on this strip.
  * **Option A**, a zero-firmware-cost `rest` sensor for the limits
    (`/api/config` is readable over plain HTTP and the payload is small), if you
    want the numbers visible in HA without any firmware change — say the word and
    I will write it as YAML. Note `/api/config` still reports four
    `channel_current` values, and with one limit for every outlet they are all the
    same number.
* The device's HTTP API is unauthenticated on the LAN (the web UI uses it that
  way), so a `rest` sensor adds no new exposure — but it also means the strip
  should stay on the trusted `IOT` VLAN/SSID.
* Anything that changes a limit must write through the staged NOR path
  (`config_occupied` / `config_ready` / `energy_barrier_state` guards) so it can
  never collide with an in-flight relay or energy write.
