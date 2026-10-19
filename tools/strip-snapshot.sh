#!/bin/sh
# Capture the evidence set used before/after an OTA flash of an MTTL-W01 strip.
# usage: sh tools/strip-snapshot.sh <dir> [ip]
#   e.g. sh tools/strip-snapshot.sh build-linux/preflight2-isolation-10.0.0.53 10.0.0.53
# Reads the HA long-lived token from $HA_TOKEN_FILE (default ~/.config/opencode/ha-token)
# so the token value never appears on the command line or in this file.
set -e
DIR=${1:?usage: strip-snapshot.sh <dir> [ip]}
IP=${2:-10.0.0.53}
HA=${HA_URL:-http://10.0.0.11:8123}
TOKEN_FILE=${HA_TOKEN_FILE:-$HOME/.config/opencode/ha-token}

mkdir -p "$DIR"
curl -s --max-time 8 "http://$IP/api/config"          > "$DIR/config.json"
curl -s --max-time 8 "http://$IP/api/device"          > "$DIR/device.json"
curl -s --max-time 8 "http://$IP/api/status"          > "$DIR/status.json"
curl -s --max-time 8 "http://$IP/api/firmware/status" > "$DIR/firmware-status.json"

if [ -r "$TOKEN_FILE" ]; then
    T=$(cat "$TOKEN_FILE")
    curl -s --max-time 20 -H "Authorization: Bearer $T" "$HA/api/states" \
        | jq -c '[.[]|select(.entity_id|test("mttl"))|{entity_id,state,last_updated}]' \
        > "$DIR/ha-entities.json"
    echo "HA entities captured: $(jq length "$DIR/ha-entities.json")"
else
    echo "no HA token at $TOKEN_FILE - skipped ha-entities.json"
fi

echo "captured $IP into $DIR:"
ls -l "$DIR"
