#!/usr/bin/env bash
# Start the playground — the REAL servers, pointed at synthetic data.
#
#   ./playground/run.sh          start CRM :8890 + HQ :8891 + Connector Console :8892
#   ./playground/run.sh stop     stop them
#
# Nothing here copies code. YOURCO_DATA_ROOT is the entire isolation mechanism: the servers
# read/write playground/data/ instead of the repo, and CRM_GIT_SYNC is force-disabled inside
# the server whenever that variable is set, so the sandbox can never commit.
set -uo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DATA="$REPO/playground/data"
PIDS="$REPO/playground/.pids"

if [ "${1:-start}" = "stop" ]; then
  [ -f "$PIDS" ] && while read -r pid; do kill "$pid" 2>/dev/null && echo "stopped $pid"; done < "$PIDS"
  rm -f "$PIDS"; exit 0
fi

if [ ! -d "$DATA" ]; then
  echo "no playground data yet — seeding with defaults (15 live clients)"
  python3 "$REPO/playground/seed.py" || exit 1
fi

: > "$PIDS"
YOURCO_DATA_ROOT="$DATA" PORT=8890 python3 "$REPO/crm/server.py"       >"$REPO/playground/.crm.log" 2>&1 &
echo $! >> "$PIDS"
YOURCO_DATA_ROOT="$DATA" PORT=8891 python3 "$REPO/dashboard/server.py" >"$REPO/playground/.hq.log"  2>&1 &
echo $! >> "$PIDS"

YOURCO_DATA_ROOT="$DATA" python3 "$REPO/processes/partnerships/connector-console/server.py" \
  --serve 8892 >"$REPO/playground/.console.log" 2>&1 &
echo $! >> "$PIDS"

sleep 1
echo "playground up — SYNTHETIC DATA, nothing here touches live"
echo "  CRM  http://127.0.0.1:8890"
echo "  HQ   http://127.0.0.1:8891"
echo "  Connector Console  http://127.0.0.1:8892"
echo "stop with: ./playground/run.sh stop"
