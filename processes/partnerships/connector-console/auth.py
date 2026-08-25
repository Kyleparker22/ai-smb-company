#!/usr/bin/env python3
"""yourco — authentication for the Connector Console.

The console's v2 identity model was "the acting connector is whoever the URL says" — which means a
link is a credential, and changing `/c/alice` to `/c/bob` is a complete account takeover. This module
replaces that with a real one: **identity comes from an authenticated session and from nothing else.**
The URL is a *request*; the session is the *answer*.

Five properties this module holds, each of which is a thing that goes wrong when it is missing:

1. **yourco never learns a connector's passphrase.** An operator issues a single-use, expiring setup
   token; the connector sets their own passphrase at `/setup?token=…`. Only a `hashlib.scrypt` hash
   (per-user random salt, n=2^15/r=8/p=1) is ever stored. The plaintext exists in one HTTP request
   body and one local variable, and is never written to disk, to the attribution log, or to stdout.
2. **Fail closed, always.** A missing or unreadable credential store means *nobody* can sign in —
   never *everybody*. Same for a missing user, an unset passphrase, an expired session.
3. **Guessing is expensive and bounded.** scrypt makes each guess cost ~33MB and ~50ms; 5 failures
   locks the account for 15 minutes, doubling per lockout to a 24h cap; a per-IP window stops
   spraying across many accounts. Comparisons are `secrets.compare_digest`.
4. **A failure tells the attacker nothing.** One generic message for every failure mode — unknown
   account, wrong passphrase, never-set passphrase, locked out. The real reason goes to the operator's
   own stderr, where an attacker cannot read it.
5. **The audit log cannot be flooded by an attacker.** `crm/_attribution-log.jsonl` is append-only and
   `log_event` re-reads it to compute `seq`, so one line per login attempt would be both a pollution
   vector (attacker-chosen names on the permanent record) and an O(n²) DoS. So: sign-ins and
   completed setups are always logged; *failures are logged only for accounts that actually exist*,
   and only the first failure and the one that trips the lockout. Everything else goes to stderr.

Storage — `_auth.json` and `_sessions.json`, both **gitignored**, both `0600`, both written atomically
under an `flock` so the CLI and the server cannot tear each other's writes. Sessions are persisted
(not merely in-memory) so restarting the preview server does not sign everyone out; only the
SHA-256 of each session id is stored, so a leaked `_sessions.json` is not a set of bearer tokens.

This module is deliberately dependency-free (stdlib only) and knows nothing about the CRM. The server
decides *what* an identity may see; this file only decides *who they are*.

Usage is via `server.py` (`--issue-setup-token`, `--auth-list`, `--auth-revoke`); the functions here
are the whole API.
"""
import os, sys, json, time, hashlib, secrets, datetime, contextlib, fcntl

HERE = os.path.dirname(os.path.abspath(__file__))
# The store lives beside the console. Overridable ONLY for tests/throwaway stores — the adversarial
# suite points this at a temp dir so it never touches an operator's real credentials.
DIR = os.environ.get("YOURCO_CONNECTOR_AUTH_DIR") or HERE
STORE = os.path.join(DIR, "_auth.json")
SESSIONS = os.path.join(DIR, "_sessions.json")

# ---- parameters (every one of these is a security decision; change deliberately) -----------
KDF = {"algo": "scrypt", "n": 1 << 15, "r": 8, "p": 1, "dklen": 32}
MAXMEM = 128 * KDF["n"] * KDF["r"] * KDF["p"] * 2      # scrypt refuses below 128*n*r*p

MIN_PASSPHRASE = 12          # length beats character classes; this is a passPHRASE
MAX_PASSPHRASE = 1024        # bound the work an unauthenticated request can ask for

SETUP_TOKEN_HOURS = 72       # a setup link is short-lived and single-use
MAX_FAILED = 5               # failures before the account locks
LOCK_BASE_SECONDS = 15 * 60  # first lockout; doubles per lockout…
LOCK_MAX_SECONDS = 24 * 3600 # …to this cap

IDLE_SECONDS = 12 * 3600         # a session dies 12h after its last request
ABSOLUTE_SECONDS = 30 * 24 * 3600  # …and unconditionally at 30 days, however active

IP_WINDOW_SECONDS = 15 * 60  # per-IP failure window (stops spraying across many accounts)
IP_MAX_FAILURES = 20

COOKIE = "yourco_console"

# ONE message for every failure. An attacker learns nothing about which accounts exist.
FAIL_MSG = "Sign-in failed. Check the name and passphrase, then try again."
SETUP_FAIL_MSG = "This setup link is not valid, has expired, or has already been used."

# A fixed hash the login path derives against when the account does not exist / has no passphrase, so
# an unknown-account failure costs the same ~50ms of scrypt as a wrong-passphrase failure.
_DUMMY_SALT = "00000000000000000000000000000000"


class AuthError(Exception):
    """Raised for operator-facing (CLI) problems only. Never surfaced to an HTTP client verbatim."""


# ---- the operator-side log (NOT the attribution log) ---------------------------------------
_LOGGER = None


def set_logger(fn):
    """Wire the attribution log in (`connector_ladder.log_event`). Tests pass their own collector."""
    global _LOGGER
    _LOGGER = fn


def _audit(event, **fields):
    if _LOGGER:
        try:
            _LOGGER(event, **fields)
        except Exception as e:                                    # a logging failure must never
            print(f"[auth] audit log failed: {e}", file=sys.stderr)  # become an auth failure
    return None


def _note(msg):
    """Operator-only detail. Goes to the server's stderr, which the HTTP client cannot read."""
    print(f"[auth] {msg}", file=sys.stderr)


# ---- time ----------------------------------------------------------------------------------
def _now():
    return time.time()


def _iso(ts=None):
    return datetime.datetime.fromtimestamp(ts if ts is not None else _now(),
                                           datetime.timezone.utc).isoformat(timespec="seconds")


# ---- store i/o -------------------------------------------------------------------------------
@contextlib.contextmanager
def _locked(path):
    """Cross-process exclusive lock, so the CLI and the server cannot interleave read-modify-writes."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    f = open(path + ".lock", "w")
    try:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield
    finally:
        try:
            fcntl.flock(f, fcntl.LOCK_UN)
        finally:
            f.close()


def _read(path, default):
    """A missing OR unreadable store yields the empty default — i.e. nobody can sign in. Fail closed."""
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else dict(default)
    except FileNotFoundError:
        return dict(default)
    except (ValueError, OSError) as e:
        _note(f"credential store {os.path.basename(path)} is unreadable ({e}) — refusing every "
              f"sign-in until it is repaired or removed")
        return dict(default)


def _write(path, data):
    """Atomic + 0600. The mode is set on the temp file BEFORE any secret lands in it."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)
    os.chmod(path, 0o600)


def _load_users():
    d = _read(STORE, {"version": 1, "users": {}})
    if not isinstance(d.get("users"), dict):   # a store missing/holding a junk `users` grants nobody
        d["users"] = {}
    return d


def _save_users(d):
    _write(STORE, d)


def _load_sessions():
    d = _read(SESSIONS, {"version": 1, "sessions": {}})
    if not isinstance(d.get("sessions"), dict):
        d["sessions"] = {}
    return d


def _save_sessions(d):
    _write(SESSIONS, d)


def _key(name):
    return (name or "").strip().lower()


# ---- hashing ----------------------------------------------------------------------------------
def _derive(passphrase, salt_hex, params=None):
    p = dict(KDF if params is None else params)
    return hashlib.scrypt(
        (passphrase or "").encode("utf-8"), salt=bytes.fromhex(salt_hex),
        n=int(p["n"]), r=int(p["r"]), p=int(p["p"]), dklen=int(p["dklen"]),
        maxmem=max(MAXMEM, 128 * int(p["n"]) * int(p["r"]) * int(p["p"]) * 2),
    ).hex()


def _token_hash(token, salt_hex):
    """Setup tokens are 256-bit random, so a salted SHA-256 is sufficient — there is nothing to guess."""
    return hashlib.sha256(bytes.fromhex(salt_hex) + (token or "").encode("utf-8")).hexdigest()


def _sid_hash(sid):
    return hashlib.sha256((sid or "").encode("utf-8")).hexdigest()


# ---- per-IP throttle (in-memory; a restart forgets it, which is acceptable for a preview) -------
_ip_fails = {}


def _ip_prune(ip, now):
    keep = [t for t in _ip_fails.get(ip, []) if now - t < IP_WINDOW_SECONDS]
    if keep:
        _ip_fails[ip] = keep
    else:
        _ip_fails.pop(ip, None)
    return keep


def ip_blocked(ip):
    if not ip:
        return False
    return len(_ip_prune(ip, _now())) >= IP_MAX_FAILURES


def _ip_fail(ip):
    if ip:
        _ip_fails.setdefault(ip, []).append(_now())


# ---- accounts ----------------------------------------------------------------------------------
# ── roles ───────────────────────────────────────────────────────────────────────
# Three real roles, mapping onto yourco's own people taxonomy
# (decisions/2026-07-06_advisors-connectors-taxonomy.md):
#
#   partner    the 50/35/15 members — the Founder, Partner B, Mike. Everything.
#   advisor    full-time yourco salespeople. CRM + the console, no HQ:
#              HQ carries runway, the OA, partner splits and the finance model.
#   connector  external referral partners. Their OWN console page and nothing else.
#
# `operator` is the pre-2026-08-23 name for what is now `partner`, kept as a working
# alias because the Founder's live account carries it and an auth change must never lock the
# only administrator out of the system that grants access. New accounts get `partner`.
ROLE_AREAS = {
    "partner":   frozenset({"hq", "crm", "console"}),
    "operator":  frozenset({"hq", "crm", "console"}),   # legacy alias for partner
    "advisor":   frozenset({"crm", "console"}),
    "connector": frozenset({"console"}),
}
VALID_ROLES = tuple(ROLE_AREAS)


def areas_for(role):
    """Which app areas this role may reach. Unknown role -> nothing, never a default grant."""
    return ROLE_AREAS.get((role or "").lower(), frozenset())


def can_access(role, area):
    """The single authorisation predicate. Deny is the default for anything unrecognised."""
    return area in areas_for(role)


def is_console_admin(role):
    """Sees the whole connector program, not just one connector's own page.

    The console asked `role == "operator"` in six places. That test silently became wrong
    the moment more roles existed — a partner would have been handed the connector view.
    Ask this instead.
    """
    return (role or "").lower() in ("partner", "operator", "advisor")


def issue_setup_token(name, role="connector", hours=SETUP_TOKEN_HOURS):
    """Create/refresh an account and mint ONE single-use setup token. Returns (token, expires_iso).

    The token is returned here and nowhere else: it is not stored in plaintext, so a lost link is
    re-issued, never recovered. An existing passphrase keeps working until the new one is set — a
    re-issue is a reset, not a lockout. To cut access off immediately, use `revoke()`.
    """
    name = (name or "").strip()
    if not name:
        raise AuthError("A name is required.")
    if role not in VALID_ROLES:
        raise AuthError("role must be one of: " + ", ".join(VALID_ROLES) + ".")
    token = secrets.token_urlsafe(32)
    salt = secrets.token_hex(16)
    expires = _now() + float(hours) * 3600
    with _locked(STORE):
        d = _load_users()
        u = d["users"].get(_key(name)) or {
            "name": name, "role": role, "createdAt": _iso(), "kdf": dict(KDF),
            "salt": secrets.token_hex(16), "hash": None, "passphraseSetAt": None,
            "lastLogin": None, "failedAttempts": 0, "lockedUntil": None, "lockouts": 0,
        }
        u["name"], u["role"] = name, role
        u["setupToken"] = {"salt": salt, "hash": _token_hash(token, salt),
                           "issuedAt": _iso(), "expiresAt": expires, "usedAt": None}
        d["users"][_key(name)] = u
        _save_users(d)
    _audit("auth.setup_issued", connector=name, by="operator", role=role,
           expires=_iso(expires), note=f"Single-use setup link issued for {name} ({role}).")
    return token, _iso(expires)


def complete_setup(token, passphrase, confirm=None):
    """Redeem a setup token and set the account's passphrase. Returns (ok, name_or_None, message).

    Single-use by construction: `usedAt` is stamped in the same locked write that stores the hash, so
    a replay of the same token finds it spent. Every existing session for the account is destroyed —
    setting a new passphrase must end any session an attacker already holds.
    """
    token = (token or "").strip()
    if not token:
        return False, None, SETUP_FAIL_MSG
    if confirm is not None and passphrase != confirm:
        return False, None, "The two passphrases do not match."
    ok, why = passphrase_ok(passphrase)
    if not ok:
        return False, None, why

    with _locked(STORE):
        d = _load_users()
        now = _now()
        found = None
        for k, u in d["users"].items():                 # scan: constant work per account, no early-out
            t = u.get("setupToken") or {}
            if not t.get("hash") or not t.get("salt"):
                continue
            if secrets.compare_digest(_token_hash(token, t["salt"]), t["hash"]):
                found = (k, u, t)
        if not found:
            _note("setup attempted with an unrecognised token")
            return False, None, SETUP_FAIL_MSG
        k, u, t = found
        if t.get("usedAt"):
            _note(f"setup token replay refused for {u['name']} (already used {t['usedAt']})")
            return False, None, SETUP_FAIL_MSG
        if float(t.get("expiresAt") or 0) < now:
            _note(f"setup token expired for {u['name']} (expired {_iso(t.get('expiresAt') or 0)})")
            return False, None, SETUP_FAIL_MSG

        u["salt"] = secrets.token_hex(16)
        u["kdf"] = dict(KDF)
        u["hash"] = _derive(passphrase, u["salt"])      # the plaintext ends here
        u["passphraseSetAt"] = _iso()
        u["failedAttempts"], u["lockedUntil"], u["lockouts"] = 0, None, 0
        t["usedAt"] = _iso()
        d["users"][k] = u
        _save_users(d)
        name = u["name"]

    destroy_sessions_for(name)
    _audit("auth.setup_completed", connector=name, by=name,
           note=f"{name} set their console passphrase. yourco does not hold it.")
    return True, name, "Passphrase set. You can sign in now."


def passphrase_ok(p):
    if not isinstance(p, str) or len(p) < MIN_PASSPHRASE:
        return False, f"Choose a passphrase of at least {MIN_PASSPHRASE} characters."
    if len(p) > MAX_PASSPHRASE:
        return False, f"That passphrase is too long (max {MAX_PASSPHRASE} characters)."
    if p.strip() == "":
        return False, f"Choose a passphrase of at least {MIN_PASSPHRASE} characters."
    return True, ""


def revoke(name):
    """Delete the account and every session it holds. The immediate cut-off."""
    with _locked(STORE):
        d = _load_users()
        u = d["users"].pop(_key(name), None)
        _save_users(d)
    destroy_sessions_for(name)
    if u:
        _audit("auth.revoked", connector=u["name"], by="operator",
               note=f"Console access revoked for {u['name']}.")
    return bool(u)


def list_users():
    """Operator view of the store. Returns no hashes, no salts, no tokens — by construction."""
    d = _load_users()
    now = _now()
    out = []
    for u in d["users"].values():
        t = u.get("setupToken") or {}
        pending = bool(t) and not t.get("usedAt") and float(t.get("expiresAt") or 0) > now
        out.append({
            "name": u.get("name"), "role": u.get("role"),
            "passphraseSet": bool(u.get("hash")),
            "createdAt": u.get("createdAt"), "lastLogin": u.get("lastLogin"),
            "failedAttempts": u.get("failedAttempts") or 0,
            "locked": bool(u.get("lockedUntil") and float(u["lockedUntil"]) > now),
            "lockedUntil": _iso(u["lockedUntil"]) if u.get("lockedUntil") else None,
            "setupPending": pending,
            "setupExpires": _iso(t["expiresAt"]) if pending else None,
        })
    _rank = {"partner": 0, "operator": 0, "advisor": 1, "connector": 2}
    return sorted(out, key=lambda x: (_rank.get(x["role"], 9), (x["name"] or "").lower()))


# ---- sign in -----------------------------------------------------------------------------------
def verify(name, passphrase, ip=None):
    """Check a sign-in. Returns (ok, user_or_None, message) — message is ALWAYS `FAIL_MSG` on failure.

    Exactly one scrypt derivation runs on every path (including unknown-account and locked-out), so
    the wall-clock cost of a failure does not distinguish "no such person" from "wrong passphrase".
    """
    now = _now()
    if ip_blocked(ip):
        _note(f"per-IP throttle: refusing sign-in attempts from {ip}")
        _derive(passphrase or "", _DUMMY_SALT)               # keep the timing profile flat
        return False, None, FAIL_MSG

    with _locked(STORE):
        d = _load_users()
        u = d["users"].get(_key(name))
        # Derive FIRST, unconditionally, against the real salt when there is one and a fixed dummy
        # otherwise. Both branches do the same work; only the comparison differs.
        salt = (u or {}).get("salt") or _DUMMY_SALT
        params = (u or {}).get("kdf") or KDF
        try:
            got = _derive(passphrase or "", salt, params)
        except Exception as e:                               # malformed stored params → fail closed
            _note(f"kdf failure for {_key(name)!r}: {e}")
            got = None

        stored = (u or {}).get("hash")
        locked = bool(u and u.get("lockedUntil") and float(u["lockedUntil"]) > now)
        match = bool(got and stored and secrets.compare_digest(got, stored))

        if u is None:
            _note(f"sign-in refused: no account named {(name or '').strip()!r}")
            _ip_fail(ip)
            return False, None, FAIL_MSG
        if locked:
            _note(f"sign-in refused: {u['name']} is locked until {_iso(u['lockedUntil'])}")
            _ip_fail(ip)
            return False, None, FAIL_MSG                     # correct passphrase does NOT bypass a lockout
        if stored is None:
            _note(f"sign-in refused: {u['name']} has not set a passphrase yet")
            _ip_fail(ip)
            return False, None, FAIL_MSG
        if not match:
            u["failedAttempts"] = int(u.get("failedAttempts") or 0) + 1
            first = u["failedAttempts"] == 1
            tripped = u["failedAttempts"] >= MAX_FAILED
            if tripped:
                u["lockouts"] = int(u.get("lockouts") or 0) + 1
                span = min(LOCK_BASE_SECONDS * (2 ** (u["lockouts"] - 1)), LOCK_MAX_SECONDS)
                u["lockedUntil"] = now + span
                u["failedAttempts"] = 0
            d["users"][_key(name)] = u
            _save_users(d)
            _note(f"sign-in refused: wrong passphrase for {u['name']}"
                  + (f" — LOCKED for {int(span // 60)} min" if tripped else
                     f" ({u['failedAttempts']}/{MAX_FAILED})"))
            _ip_fail(ip)
            # Logged only for a REAL account, and only twice per lockout cycle: the append-only
            # attribution log must not be floodable by an unauthenticated stranger.
            if first or tripped:
                _audit("auth.login_failed", connector=u["name"],
                       locked=bool(tripped), note=("Failed console sign-in" +
                       (" — account locked after repeated failures." if tripped else ".")))
            return False, None, FAIL_MSG

        u["failedAttempts"], u["lockedUntil"] = 0, None
        u["lastLogin"] = _iso(now)
        d["users"][_key(name)] = u
        _save_users(d)
        _ip_prune(ip, now)

    _audit("auth.login", connector=u["name"], role=u.get("role"),
           note="Signed in to the connector console.")
    return True, {"name": u["name"], "role": u.get("role") or "connector"}, ""


# ---- sessions ------------------------------------------------------------------------------------
def create_session(name, role):
    """Mint a 256-bit session id. Only its SHA-256 is stored; the id itself lives in the cookie."""
    sid = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(32)
    now = _now()
    with _locked(SESSIONS):
        s = _load_sessions()
        s["sessions"][_sid_hash(sid)] = {
            "name": name, "role": role, "csrf": csrf,
            "created": now, "lastSeen": now, "absoluteExpiry": now + ABSOLUTE_SECONDS}
        _prune(s, now)
        _save_sessions(s)
    return sid, csrf


def _prune(s, now):
    dead = [k for k, v in s["sessions"].items()
            if now - float(v.get("lastSeen") or 0) > IDLE_SECONDS
            or now > float(v.get("absoluteExpiry") or 0)]
    for k in dead:
        s["sessions"].pop(k, None)
    return len(dead)


def session_for(sid):
    """Resolve a cookie value to an identity, or None. Enforces idle + absolute expiry, touches lastSeen.

    Anything unexpected — no cookie, an unknown id, an expired id, a store that will not read —
    returns None. There is no path here that guesses an identity.
    """
    if not sid or not isinstance(sid, str) or len(sid) > 512:
        return None
    now = _now()
    h = _sid_hash(sid)
    with _locked(SESSIONS):
        s = _load_sessions()
        rec = s["sessions"].get(h)
        if not rec:
            return None
        if now - float(rec.get("lastSeen") or 0) > IDLE_SECONDS or now > float(rec.get("absoluteExpiry") or 0):
            s["sessions"].pop(h, None)
            _save_sessions(s)
            return None
        rec["lastSeen"] = now
        s["sessions"][h] = rec
        _prune(s, now)
        _save_sessions(s)
    return {"name": rec["name"], "role": rec.get("role") or "connector", "csrf": rec.get("csrf") or ""}


def destroy_session(sid):
    if not sid:
        return False
    with _locked(SESSIONS):
        s = _load_sessions()
        gone = s["sessions"].pop(_sid_hash(sid), None)
        if gone:
            _save_sessions(s)
    if gone:
        _audit("auth.logout", connector=gone.get("name"), note="Signed out of the connector console.")
    return bool(gone)


def destroy_sessions_for(name):
    k = _key(name)
    with _locked(SESSIONS):
        s = _load_sessions()
        dead = [h for h, v in s["sessions"].items() if _key(v.get("name")) == k]
        for h in dead:
            s["sessions"].pop(h, None)
        if dead:
            _save_sessions(s)
    return len(dead)


def check_csrf(session, presented):
    tok = (session or {}).get("csrf") or ""
    return bool(tok) and bool(presented) and secrets.compare_digest(str(presented), tok)


# ---- cookies ---------------------------------------------------------------------------------------
def is_local_host(host):
    """Secure-cookie decision. Anything that is not plainly a loopback name gets `Secure`."""
    h = (host or "").split(",")[0].strip().lower()
    if h.startswith("["):                      # [::1]:8807
        h = h[1:h.find("]")] if "]" in h else h[1:]
    elif h.count(":") == 1:
        h = h.split(":")[0]
    return h in ("localhost", "127.0.0.1", "::1", "0.0.0.0", "")


def set_cookie(sid, host):
    """HttpOnly + SameSite=Strict + Path=/ + Max-Age; Secure whenever this is not loopback."""
    bits = [f"{COOKIE}={sid}", "Path=/", "HttpOnly", "SameSite=Strict",
            f"Max-Age={int(IDLE_SECONDS)}"]
    if not is_local_host(host):
        bits.append("Secure")
    return "; ".join(bits)


def clear_cookie(host):
    bits = [f"{COOKIE}=", "Path=/", "HttpOnly", "SameSite=Strict", "Max-Age=0"]
    if not is_local_host(host):
        bits.append("Secure")
    return "; ".join(bits)


def cookie_from_header(header):
    """Parse the session id out of a raw Cookie header without importing a parser that may raise."""
    for part in (header or "").split(";"):
        k, _, v = part.strip().partition("=")
        if k == COOKIE:
            return v.strip().strip('"')
    return None


if __name__ == "__main__":
    print(__doc__.strip().splitlines()[0])
    print(f"store:    {STORE}")
    print(f"sessions: {SESSIONS}")
    print(f"kdf:      scrypt n={KDF['n']} r={KDF['r']} p={KDF['p']} dklen={KDF['dklen']}")
    users = list_users()
    print(f"accounts: {len(users)}")
    for u in users:
        print(f"  {u['role']:<9} {u['name']:<24} passphrase={'set' if u['passphraseSet'] else 'NOT SET'}"
              f"{'  LOCKED' if u['locked'] else ''}{'  setup-pending' if u['setupPending'] else ''}")
    print("\n(no secret is printable from this module — hashes, salts, and tokens are never returned)")
