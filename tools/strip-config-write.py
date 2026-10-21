#!/usr/bin/env python3
"""Write a strip's settings the same way the device web UI does.

The UI does not POST JSON: it packs the v8 settings record itself and POSTs it
to /api/config with `X-MTTL-Keep-Password: 1`, so the stored Wi-Fi and MQTT
credentials survive a write that does not carry them. This tool reproduces that
byte for byte (the layout is pinned in host_test/protection_settings_test.c and
in firmware/settings.c:mttl_settings_pack), starting from the device's own
GET /api/config output so nothing else changes.

usage:
  strip-config-write.py <ip> [--lock N] [--timers a,b,c,d] [--language N] [--show]

  --lock N          button_lock nibble, 0..15 (bit 0 = outlet 1 ... bit 3 = outlet 4)
  --timers a,b,c,d  auto-off minutes per outlet, 0..65535
  --language N      dashboard language stored in the record: 1 English, 2 Egyptian Arabic
  --show            only print the current settings, do not write

Exit status is 0 only when the device accepted the body AND reads back the
values that were asked for (the response to the POST alone proves nothing: the
save is asynchronous).
"""
import json
import sys
import time
import urllib.error
import urllib.request

TIMEOUT = 8


def get(ip, path):
    with urllib.request.urlopen(f"http://{ip}{path}", timeout=TIMEOUT) as r:
        return json.load(r)


def build_body(cfg, lock, timers, language):
    """Reproduce ui/live.js settingsBody() for an existing configuration."""
    prot = cfg["protection"]
    body = bytearray()
    body += bytes([8, language, 1 if cfg["enabled"] else 0,
                   cfg["port"] & 255, (cfg["port"] >> 8) & 255])
    # Credentials are deliberately empty: X-MTTL-Keep-Password keeps the stored ones.
    fields = [cfg["device"], *cfg["channels"], "", "", cfg["broker"],
              cfg["user"], "", cfg["topic"]]
    for value in fields:
        raw = (value or "").encode()
        body += bytes([len(raw)]) + raw
    body += bytes([prot["enabled"],
                   prot["temperature"] & 255, (prot["temperature"] >> 8) & 255,
                   prot["current"] & 255, (prot["current"] >> 8) & 255,
                   prot["power"] & 255, (prot["power"] >> 8) & 255])
    body += bytes.fromhex(cfg["schedule_hex"])          # 50 bytes, unpacked by the firmware
    body += bytes([lock & 15])
    for minutes in timers:
        body += bytes([minutes & 255, (minutes >> 8) & 255])
    for _ in range(4):                                  # v8 tail: per-channel limits, mA
        body += bytes([prot["current"] & 255, (prot["current"] >> 8) & 255])
    return bytes(body)


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    ip = argv[1]
    lock = None
    timers = None
    language = None
    show_only = False
    i = 2
    while i < len(argv):
        if argv[i] == "--lock":
            i += 1
            lock = int(argv[i])
        elif argv[i] == "--timers":
            i += 1
            timers = [int(x) for x in argv[i].split(",")]
            if len(timers) != 4:
                print("--timers needs four comma-separated values", file=sys.stderr)
                return 2
        elif argv[i] == "--language":
            i += 1
            language = int(argv[i])
            if language not in (1, 2):
                print("--language is 1 (English) or 2 (Egyptian Arabic)", file=sys.stderr)
                return 2
        elif argv[i] == "--show":
            show_only = True
        else:
            print(f"unknown argument {argv[i]}", file=sys.stderr)
            return 2
        i += 1

    cfg = get(ip, "/api/config")
    print(f"{ip}: {cfg['device']} lock={cfg.get('button_lock')} "
          f"timers={cfg.get('timer_minutes')} language={cfg.get('language')} "
          f"persistent={cfg.get('persistent')}")
    if show_only:
        return 0
    if lock is None and timers is None and language is None:
        print("nothing to write (pass --lock, --timers and/or --language)", file=sys.stderr)
        return 2

    want_lock = cfg.get("button_lock", 0) if lock is None else lock
    want_timers = cfg.get("timer_minutes", [0, 0, 0, 0]) if timers is None else timers
    want_language = cfg.get("language", 1) if language is None else language
    body = build_body(cfg, want_lock, want_timers, want_language)
    print(f"writing {len(body)} B (lock={want_lock} timers={want_timers} "
          f"language={want_language})")

    request = urllib.request.Request(
        f"http://{ip}/api/config", data=body, method="POST",
        headers={"Content-Type": "application/octet-stream",
                 "X-MTTL-Keep-Password": "1",
                 "Origin": f"http://{ip}"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as r:
            print(f"POST /api/config -> {r.status} {r.read().decode(errors='replace')}")
    except urllib.error.HTTPError as exc:
        # A refusal is a result, not a crash: 400 = the record failed validation
        # (e.g. a timer on a locked outlet), 429 = busy/not ready.
        print(f"POST /api/config -> {exc.code} {exc.read().decode(errors='replace')}")
        return 1

    # The save is queued behind the flash write; poll like the UI does.
    for _ in range(12):
        time.sleep(0.5)
        now = get(ip, "/api/config")
        if (now.get("button_lock", 0) == want_lock
                and now.get("timer_minutes") == want_timers
                and now.get("language") == want_language):
            print(f"confirmed: lock={now['button_lock']} timers={now['timer_minutes']} "
                  f"language={now['language']}")
            return 0
    print(f"NOT confirmed (device reads lock={now.get('button_lock')} "
          f"timers={now.get('timer_minutes')} language={now.get('language')})",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
