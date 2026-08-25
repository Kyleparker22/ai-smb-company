#!/usr/bin/env bash
# show.sh — bring up every YourCo cockpit in one step, then open the app.
#   ./show.sh        (re)start all FIVE servers and open the app's sign-in
#   ./show.sh stop   stop them all
#
# Five, not three: website · HQ · CRM · connector console · the app gateway. The header said
# "three servers … open the website" until 2026-08-24 — true before the app was built on 08-23,
# and wrong the moment it was, because what you now open is the gateway at :8820 and the other
# four are its backends. The COCKPITS array below is the real list; keep this comment counting it.
#
# Ports are READ FROM .claude/launch.json, never hardcoded here. That file is the single
# registry of every local surface and a consistency invariant already enforces
# that no two entries share a port. This script used to carry 8793/8791/8790 as literals,
# which meant a port moved in launch.json would silently break `./show.sh` — the exact
# duplicated-fact failure the workspace keeps getting caught by. Two prebuild ports were
# moved on 2026-08-22; that was the prompt for this change.
cd "$(dirname "$0")"

# name-in-launch.json : label : path to open
# Order matters: the gateway is LAST because it proxies the three above it, and starting it
# first would just mean 502s until the others bind. The app is what you actually open — HQ,
# the CRM and the console all live behind its single sign-in, so it is the URL launched at
# the end. The other four are its backends and must stay on 127.0.0.1.
COCKPITS=(
  "yourco-webb-pages:website:/yourco-site-v2/index.html"
  "yourco-hq:HQ-dash:/"
  "yourco-crm:CRM:/"
  "yourco-connector-console:console:/login"
  "yourco-app:APP:/"
)

port_for() {  # $1 = launch.json name -> prints the port, or nothing if absent
  python3 - "$1" <<'PY'
import json, sys
try:
    cfgs = json.load(open(".claude/launch.json"))["configurations"]
except Exception:
    sys.exit(1)
for c in cfgs:
    if c.get("name") == sys.argv[1]:
        print(c["port"]); break
PY
}

stop_port() {  # kill anything listening on $1; returns 0 if it killed something
  local pids; pids=$(lsof -ti tcp:"$1" 2>/dev/null)
  if [ -n "$pids" ]; then echo "$pids" | xargs kill -9 2>/dev/null; return 0; fi
  return 1
}

# Resolve every port up front so a missing/renamed entry fails loudly instead of half-starting.
PORTS=(); LABELS=(); PATHS=()
for entry in "${COCKPITS[@]}"; do
  name="${entry%%:*}"; rest="${entry#*:}"; label="${rest%%:*}"; urlpath="${rest#*:}"
  p=$(port_for "$name")
  if [ -z "$p" ]; then
    echo "show.sh: '$name' is not in .claude/launch.json — cannot resolve its port." >&2
    echo "         Add it there (that file is the registry) and re-run." >&2
    exit 1
  fi
  PORTS+=("$p"); LABELS+=("$label"); PATHS+=("$urlpath")
done

if [ "$1" = "stop" ]; then
  for p in "${PORTS[@]}"; do
    if stop_port "$p"; then echo "• stopped :$p"; else echo "• nothing on :$p"; fi
  done
  exit 0
fi

start() {  # $1=port  $2=cmd  $3=name — clean the port first so a wedged server can't block
  stop_port "$1" >/dev/null 2>&1
  ( $2 >"/tmp/yourco-$3.log" 2>&1 & )
}

start "${PORTS[0]}" "python3 -m http.server ${PORTS[0]} --directory agents/webb/pages" "site"
start "${PORTS[1]}" "python3 dashboard/server.py" "dashboard"
start "${PORTS[2]}" "python3 crm/server.py" "crm"
start "${PORTS[3]}" "python3 processes/partnerships/connector-console/server.py --serve ${PORTS[3]}" "console"
start "${PORTS[4]}" "python3 app/server.py" "app"

sleep 4  # give five servers a moment to bind before we check (the gateway is slowest)

check() {  # $1=port  $2=name  $3=url — confirm it's listening; show the error if not
  if lsof -ti tcp:"$1" >/dev/null 2>&1; then
    printf "  [ok]  %-9s %s\n" "$2" "$3"
  else
    echo "  [X]   $2 failed to start — last lines of /tmp/yourco-$2.log:"
    tail -n 8 "/tmp/yourco-$2.log" 2>/dev/null | sed 's/^/         /'
  fi
}

echo
echo "  YourCo cockpits:"
APP_URL=""
for i in "${!PORTS[@]}"; do
  url="http://127.0.0.1:${PORTS[$i]}${PATHS[$i]}"
  check "${PORTS[$i]}" "${LABELS[$i]}" "$url"
  [ "${LABELS[$i]}" = "APP" ] && APP_URL="$url"
done
echo
echo "  ► Sign in here:  ${APP_URL}"
echo "    Everything (HQ · CRM · Connectors) is behind that one login."
echo
echo "  Stop when done:  ./show.sh stop"
echo

open "$APP_URL" 2>/dev/null || xdg-open "$APP_URL" 2>/dev/null || true
