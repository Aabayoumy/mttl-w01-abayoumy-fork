#!/usr/bin/env python3
"""Stage the Ameba SDK + pinned overlay files exactly as builder/engine.py would."""
import hashlib, json, os, pathlib, subprocess, sys, tarfile, urllib.request

HOME = pathlib.Path.home()
TOOLS = HOME / "mttl-tools"
SRC = HOME / "mttl_fork_check" / "source"
HW = SRC / "work" / "reference" / "ameba-arduino-1" / "Arduino_package" / "hardware"
LOCK = json.loads((HOME / "mttl_fork_check" / "builder" / "dependencies.lock.json").read_text())

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

# ---- 1. extract SDK ----
sdk_tar = TOOLS / "dl" / "ameba_sdk.tar.gz"
if not (HW / "platform.txt").is_file():
    HW.mkdir(parents=True, exist_ok=True)
    with tarfile.open(sdk_tar) as tf:
        names = tf.getnames()
    # find the prefix that directly contains platform.txt
    pref = None
    for n in names:
        if n.endswith("platform.txt"):
            pref = n[: -len("platform.txt")]
            break
    print("archive prefix for platform.txt:", repr(pref))
    with tarfile.open(sdk_tar) as tf:
        members = [m for m in tf.getmembers() if pref is None or m.name.startswith(pref)]
        for m in members:
            m.name = m.name[len(pref):] if pref else m.name
        tf.extractall(HW, members=[m for m in members if m.name])
else:
    print("SDK already staged")

print("platform.txt:", (HW / "platform.txt").is_file())
for probe in ("cores/arduino/Arduino.h", "variants/rtl8710/variant.cpp",
              "variants/rtl8710/linker_scripts/gcc/rtl8710-symbol-v03-img2_arduino_arduino.ld",
              "system/component/os/freertos/freertos_v8.1.2/Source/portable/MemMang/heap_5.c",
              "libraries/WiFi/src", "libraries/MQTTClient/src",
              "system/component/common/network/httpd"):
    print(f"  {'OK  ' if (HW / probe).exists() else 'MISS'} {probe}")

# ---- 2. overlay files (kind=sdkfile) ----
cache = TOOLS / "dl" / "overlay"
cache.mkdir(parents=True, exist_ok=True)
overlay = [a for a in LOCK["artifacts"] if a.get("kind") == "sdkfile"]
print(f"\noverlay files to place: {len(overlay)}")
bad, wrote, skipped = [], 0, 0
for a in overlay:
    dst = HW / a["relative"]
    blob = cache / a["file"]
    if not blob.is_file():
        try:
            with urllib.request.urlopen(a["url"], timeout=60) as r:
                blob.write_bytes(r.read())
        except Exception as exc:
            bad.append((a["relative"], f"download {exc}"))
            continue
    digest = sha256(blob)
    if digest != a["sha256"]:
        bad.append((a["relative"], f"sha256 {digest[:12]} != {a['sha256'][:12]}"))
        continue
    if dst.is_file() and sha256(dst) == a["sha256"]:
        skipped += 1
        continue
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(blob.read_bytes())
    wrote += 1

print(f"overlay written={wrote} already-correct={skipped} failures={len(bad)}")
for rel, why in bad:
    print("  FAIL", rel, "->", why)

# ---- 3. sanity ----
print("\nHW root:", HW)
print("has cores/arduino:", (HW / "cores" / "arduino").is_dir())
print("has variants/rtl8710:", (HW / "variants" / "rtl8710").is_dir())
print("has system:", (HW / "system").is_dir())
plat = (HW / "platform.txt").read_text(errors="replace")
for key in ("compiler.ameba.c.include=", "compiler.ameba.ar.list="):
    line = next((x for x in plat.splitlines() if x.startswith(key)), None)
    print(f"{key} {'present' if line else 'MISSING'}")
print("DONE step3")
