# MTTL-W01 standalone firmware — Linux build recipe

Reproducible build of `af950833/mttl_w01_standalone` on a Linux host.

| host | state |
|---|---|
| **CT 106 `mttlbuild`, `root@10.0.0.19`** (Debian 13, 2 cores, 2 GB, unprivileged, `onboot=0`) — *current* | builds the shipped firmware; full build incl. FWR packaging **~12 s** |
| LXC `abayoumy@10.0.0.16` (AlmaLinux 9.8, x86_64) — *retired* | behind **pve1 (10.0.0.200), which is down**; unreachable from pve2 as well. Kept because the pristine-`main` numbers below were first measured there and CT 106 reproduces them exactly |

`mttlbuild` lives on **pve2 (10.0.0.210)**, reachable at `ssh root@10.0.0.19`
(SSH key trusted). Repo clone `~/mttl_fork_check`, tools in `~/mttl-tools`.

The clone's `feature/protection-v2` is the live fork line and currently sits on
upstream tag **`v2.0.17`** (`311663e`); the `archive/protection-v2-2.0.15` branch
keeps the previously shipped line. The recipe below and its numbers are the
pristine `ebfb39d` (= 2.0.15) baseline and are unaffected by that — see
`patches/README.md` for the series and `FEATURE-per-channel-current.md` for the
per-build RAM table.

## Target hardware (corrected)

The firmware targets **Realtek Ameba1 / RTL8710 (ARM Cortex-M3)**, *not* ESP8285.

Evidence:
- `source/standalone/image2_analysis.py` requires `(kind,machine,version)==(2,40,1)`
  → ELF32 LE, `EM_ARM`; sections `.image2.start.table` / `.ram_image2.text`.
- `builder/dependencies.lock.json` pins `arm-none-eabi-gcc 4.8.3-2014q1` and the
  Realtek SDK `ameba_1-2.0.12-build20220509`.
- Build flags: `-mcpu=cortex-m3 -mthumb -DBOARD_RTL8710 -DCONFIG_PLATFORM_8195A`,
  variant `variants/rtl8710`, linker `rtl8710-symbol-v03-img2_arduino_arduino.ld`.
- OTA layout `0xb000` / `0x80000` inside a 1 MB image (`ota_plan_make`).
- The live strip accepts and runs this `.fwr` over web OTA → empirically Ameba.

Matter remains infeasible, but for the correct reason: the official Matter SDK
has no Ameba1/RTL8710 port (only ESP32 / Silicon Labs / NXP etc.).

## Build requirements

`source/build.py` refuses to run unless both env vars are set:

```sh
export MTTL_GCC_DIR=$HOME/mttl-tools/gcc          # must contain bin/arm-none-eabi-*.exe
export MTTL_TERSER_ROOT=$HOME/mttl-tools/js/node_modules/terser
```

Python: `zopfli` (UI asset compression) and `unicorn` (ARM emulation of `setup()`).
Node: `terser@5.44.0` (UI minification; `minify_ui.cjs` reads `MTTL_TERSER_ROOT`).

Installed on CT 106 (`~/mttl-tools/venv`, `~/mttl-tools/js`):

| piece | version | note |
|---|---|---|
| ARM GCC | `arm-none-eabi-gcc 4.8.3 20140228` (`gcc-arm-none-eabi-4.8.3-2014q1-linux64`) | Windows-style `.exe` names shimmed; `.exe` shims for `gcc g++ size nm objdump objcopy ar ranlib ld as` |
| zopfli | **0.4.3** (the pinned version — no fallback needed) | Python 3.13.5 venv |
| unicorn | current | runs `setup()` for the build self-check |
| node / npm | 20.19.2 / 9.2.0 | |
| terser | 5.44.0 (pinned) | |
| host `cc` | GCC 14.2.0 | also used to run the host test suite |

The **host test suite** (`source/standalone/host_test/run.sh`) runs on both hosts
and both compilers: Apple clang 21 on the Mac and GCC 14.2.0 on CT 106 — 145
checks, 0 failures. GCC ≥ 12 reports upstream's deliberate dense one-liner style
as `-Werror=misleading-indentation`, so the harness probes for
`-Wno-misleading-indentation` and uses it only where the compiler accepts it
(clang and GCC 11 simply skip the option). The cross build never enables it.

### 1. ARM toolchain — exact pinned version, Linux64 build

```sh
curl -L -o gcc483.tar.gz \
  https://downloads.arduino.cc/gcc-arm-none-eabi-4.8.3-2014q1-linux64.tar.gz
mkdir -p ~/mttl-tools/gcc && tar xzf gcc483.tar.gz -C ~/mttl-tools/gcc --strip-components=1
```

The lock file pins only the *Windows* artifact
(`...-4.8.3-2014q1-windows.tar.gz`), so the Linux64 build of the same toolchain
version is used instead. **Deviation from the pinned hash — documented, not silent.**

The scripts hardcode Windows-style binary names (`arm-none-eabi-gcc.exe`,
`-g++.exe`, `-size.exe`, `-nm.exe`, `-objdump.exe`, `-objcopy.exe`), so create shims:

```sh
cd ~/mttl-tools/gcc/bin
for t in gcc g++ size nm objdump objcopy ar ranlib ld as; do
  [ -x arm-none-eabi-$t ] && ln -sf arm-none-eabi-$t arm-none-eabi-$t.exe
done
```

### 2. Python + Node deps

```sh
python3 -m pip install --user zopfli unicorn
mkdir -p ~/mttl-tools/js && cd ~/mttl-tools/js && npm install terser@5.44.0
```

### 3. Ameba SDK + pinned overlay files

Needed at
`source/work/reference/ameba-arduino-1/Arduino_package/hardware`
(this is the Arduino package layout: `platform.txt`, `cores/`, `variants/`,
`libraries/`, `system/`).

```sh
curl -L -o ameba_sdk.tar.gz \
  https://raw.githubusercontent.com/Ameba-AIoT/ameba-arduino-1/819d5a3252a4294847dc035bc431b1437dddbee3/Arduino_package/release/ameba_1-2.0.12-build20220509.tar.gz
# sha256 must equal 9f76a7d82a1f98ea283927824415f19c9047a160e65287e60390a6fb69c5084b
# archive prefix is 'hardware/' — strip it when extracting:
tar xzf ameba_sdk.tar.gz -C .../Arduino_package/hardware --strip-components=1
```

Then apply the 49 `kind:"sdkfile"` overlays from `builder/dependencies.lock.json`
into the same directory, verifying each against its pinned `sha256`. The helper
used for this is `/tmp/mttl_lxc_step3.py` on the Mac (staging script, not in repo).

### 4. Build

```sh
cd source && python3 build.py     # → --ota-test --sensor-test --relay-test
```

Output: `source/standalone/results/network-ota-test/`
- `comMTTL-W01_2.0.15.fwr` ← flashable via web OTA
- `mttl-w01-2.0.15-network-OTA-test.{bin,fwr}`, `independent-body.bin`
- `sdk/offline-only.axf`, `sdk/build.log`, `sdk/sections.txt`, `setup-disassembly.txt`
- `manifest.json` (build_id, sha256, warning counts, RAM margins)

## Self-checks the build performs

`build_network_test.py` is not just a compiler driver — it asserts:

- `__HeapLimit <= __mttl_msp_limit` and the 4 KB MSP reserve is intact
- Image2 body contains the expected RAM-settings marker; version `2.0.15` present
- `setup()` disassembly contains a direct `bl mttl_sdk_worker_start`
- `setup()` is *executed* on ARM via Unicorn for `worker_start` return 0 and 1
- `objcopy` output byte-matches the Image2 body
- BIN↔FWR round-trip, `LGU+-TAP-HW002` hardware signature, `mttl_native_ota_hardware == 0x10006018`

## Baseline result (clean HEAD `ebfb39d`) — measured on CT 106

Identical to the values first measured on the old AlmaLinux LXC (GCC 11), i.e.
the host/toolchain-generational difference does not move a single byte of this
image:


| field | value |
|---|---|
| version / profile | 2.0.15 / `NETWORK_OTA_TEST_RAM_SETTINGS` |
| build_id | `84c578024d1cfbe8` (random per build: `secrets.token_hex(8)`) |
| fwr sha256 | `25a4b6d143d6d533c0dd4a5a9f6718ff0f7bfd3b4d25da91c07923ac535db0b1` |
| fwr size | 333,428 bytes |
| link warnings | 1035 (700 = SDK C++ literal-suffix noise) |
| static gap to MSP limit | **1620 bytes** — very little RAM headroom |
| UI gzip total | 18,791 bytes (cap 20,000) |
| fwr sha256 | `9a745526f94c10a1f6b1359835e0a2d8608f2726ecdc127432ba7d7d4512eb4e` (build `a48d845527a572f0`) |
| initial RTOS heap | 39,936 bytes (sensor-test profile) |
| settings sectors | `0xee000`, `0xef000` |

## Hazards

- **The build does not clean its output directory.** A failed build leaves the
  previous `.fwr` in place — check `manifest.json`'s `build_id` before flashing.
- **`build_id` is random per build** (`secrets.token_hex(8)` → `ota_test_config.h`),
  so two builds of identical source differ in sha256. Rebuilds are **not
  byte-reproducible by design**; the OTA page's build-verification will never match
  a previously flashed build. Compare source, not build_id.
- **Cannot reproduce upstream's exact release bytes — but the cause is *not*
  the UI, and not this host.** Pristine `main` gives 333,428 B here vs the v2.0.15
  release asset's 333,412 B: a constant **+16 B**. This was investigated by
  decoding both images (the vendor XOR is self-inverse, see
  `tools/fwr-compare.py` and `tools/fwr-asset-compare.py`):

  * the four gzipped **UI asset blobs are byte-identical** to the release build —
    each is found verbatim in the released image, exactly 16 bytes earlier, so
    the pinned `zopfli 0.4.3` / `terser 5.44.0` pipeline matches upstream
    exactly. The earlier "zopfli 0.2.3 fallback" explanation in this file was
    **wrong**;
  * the release build's source is the tree of `5b06933` ("Handle identical OTA
    uploads…", committed 18 s before the asset was replaced). `git diff 5b06933
    ebfb39d` touches **only `README.md` / `README_EN.md`** — the firmware sources
    are identical, so this is not a source difference;
  * the 16 bytes sit in **code/rodata early in the image** (everything from
    address `0x10006048` on carries literal addresses shifted by +8/+16, while
    the asset blobs are only shifted by 16). Most plausible cause: the pinned
    toolchain is the **Windows** build of GCC 4.8.3-2014q1 (`dependencies.lock.json`)
    while we use its **Linux64** build, so codegen differs by 16 bytes.

  Immaterial in practice: all build self-checks pass, and Linux-built images run
  on real hardware (both strips). Byte identity is unreachable anyway because of
  the random `build_id`.
- Upstream HEAD is **2.0.15**; the strip currently reports **2.0.14**. HEAD has
  never been flashed to this device.
- `--no-watchdog` / `--legacy-relay-timing` are comparison-only flags requiring
  `--ota-test`; do not ship them.
