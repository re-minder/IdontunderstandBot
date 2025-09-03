#!/bin/sh
set -eu

# Wrapper to start the bot gently (delay, single-instance, lowered priority)

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT_DIR"
PEX_PATH="$ROOT_DIR/dist/bot.pex"
LOG_PATH="$ROOT_DIR/bot.log"

sleep 30

CMD="/usr/bin/python3.8 $PEX_PATH"
if pgrep -f "$CMD" >/dev/null 2>&1; then
  exit 0
fi

exec /usr/bin/nice -n 10 /usr/bin/ionice -c2 -n7 $CMD >> "$LOG_PATH" 2>&1


