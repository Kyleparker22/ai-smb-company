#!/usr/bin/env python3
"""Adversarial deal reads — the confidence SPREAD.

One agent per deal is one opinion. This runs TWO, with opposed priors, over the
identical evidence bundle, and stores their DISAGREEMENT as a first-class field.

The split is not arbitrary — it is the real epistemic divide in any pipeline:

    PROSECUTION  credits only what THEY did. Our activity is not evidence of their
                 intent; it is evidence of our hope. Clock decay at full weight.
    DEFENSE      credits the whole record — our work, structural warmth, referral
                 path, scheduled next steps — and softens the clock where there is
                 a reason for the silence.

Both read the same facts. A wide spread means one thing precisely: *we* are the
only thing moving this deal. That is the stale-deal detector — and the top fact
the defence counts that the prosecution throws out is the contested fact, which
is also, already written, the next action.

Deterministic by design (the same half deal_agents.py runs): the scores need no
model and are reproducible. `--narrate` adds the LLM pass — two opposed prompts,
restricted to the bundle — for the prose and the named contested fact.

Run:
    python3 crm/adversarial.py            # score every in-motion deal, write results
    python3 crm/adversarial.py --dry      # print, write nothing
    python3 crm/adversarial.py --narrate  # + the LLM half (claude -p, two calls per deal)
"""
import json, os, sys, datetime, subprocess, fcntl

HERE = os.path.dirname(os.path.abspath(__file__))
# Playground switch: data files resolve under DATA_DIR, never HERE. HERE is CODE.
# Enforced by playground/check_isolation.py — a module that reads/writes off HERE
# will read the sandbox and WRITE LIVE, which is how synthetic connectors once
# landed in the real CRM (2026-08-07).
DATA_DIR = os.path.join(os.environ["YOURCO_DATA_ROOT"], "crm") if os.environ.get("YOURCO_DATA_ROOT") else HERE
REPO = os.path.dirname(HERE)
DATA = os.path.join(DATA_DIR, "data.json")
DATA_JS = os.path.join(DATA_DIR, "data.js")
TELEMETRY = os.path.join(DATA_DIR, "telemetry.jsonl")
OUT = os.path.join(DATA_DIR, "_deal-spread.json")
LOCK = os.path.join(REPO, "runtime", ".repo.lock")

TODAY = datetime.date.today()
BENCH = {"parked", "pre-convo"}   # Pre Convo has no buyer-side evidence to weigh yet
TERMINAL = {"live"}

# How long a buyer-side signal stays evidence of intent, in days. Past this the
# prosecution stops counting it at all; the defence decays it linearly.
THEM_HALFLIFE = 21
SPREAD_WIDE = 25          # >= this is a contested deal
NARRATE_TIMEOUT = 180


def _d(iso):
    try:
        return datetime.date.fromisoformat(str(iso)[:10])
    except Exception:
        return None


def age(iso):
    d = _d(iso)
    return None if not d else (TODAY - d).days


def heat_rollup():
    rows = {}
    if not os.path.exists(TELEMETRY):
        return rows
    with open(TELEMETRY) as f:
        for line in f:
            try:
                ev = json.loads(line)
            except Exception:
                continue
            p = str(ev.get("p", "")).split("?")[0]
            r = rows.setdefault(p, {"views": 0, "beats": 0, "last": ""})
            r["views" if ev.get("e") == "view" else "beats"] += 1
            r["last"] = max(r["last"], str(ev.get("ts", ""))[:19])
    return rows


def evidence(deal, data, heat):
    """The bundle both readers see. Every fact carries an ACTOR — that is the whole design.

    actor "them"  — the buyer did something (the only currency the prosecution accepts)
    actor "us"    — yourco did something (effort, not intent)
    actor "clock" — time passing (decay; the prosecution's main weapon)
    actor "structure" — durable properties: referral path, warm intro, priced deal
    """
    co = next((c for c in data.get("companies", []) or [] if c.get("id") == deal.get("companyId")), {})
    acts = [a for a in data.get("activities", []) or [] if a.get("companyId") == deal.get("companyId")]
    acts.sort(key=lambda a: str(a.get("date") or ""), reverse=True)
    stages = {s["key"]: s for s in data.get("stages", []) or []}
    cfg = stages.get(deal.get("stage"), {})
    facts = []

    def add(actor, weight, key, text, when=None):
        facts.append({"actor": actor, "w": weight, "key": key, "text": text, "when": when,
                      "age": age(when) if when else None})

    # --- them -------------------------------------------------------------
    reacted = [a for a in (deal.get("artifacts") or []) if a.get("status") == "reacted" and a.get("reaction")]
    for a in reacted:
        add("them", 30, "artifact-reaction", f"reacted to \"{a.get('name')}\": {a.get('reaction')}", a.get("date"))
    for a in acts:
        t = str(a.get("type") or "")
        if t in ("meeting", "call"):
            add("them", 26, f"{t}", f"{t}: {str(a.get('summary') or '')[:120]}", a.get("date"))
        elif t == "reply" or "replied" in str(a.get("summary") or "").lower():
            add("them", 24, "reply", str(a.get("summary") or "")[:120], a.get("date"))
    v = m = 0
    last_heat = ""
    for a in (deal.get("artifacts") or []):
        base = str(a.get("link") or "").split("?")[0]
        if not base:
            continue
        for p, r in heat.items():
            if p == base or (base.endswith("/") and p.startswith(base)):
                v += r["views"]; m += r["beats"] * 15 / 60
                last_heat = max(last_heat, r["last"])
    if v:
        add("them", min(28, 8 + v * 2), "heat", f"opened our material {v}x (~{round(m)} min)", last_heat[:10])

    # --- us ---------------------------------------------------------------
    built = [a for a in (deal.get("artifacts") or []) if a.get("status") == "built"]
    shown = [a for a in (deal.get("artifacts") or []) if a.get("status") == "shown"]
    for a in built:
        add("us", 10, "artifact-built", f"we built \"{a.get('name')}\" — not yet shown", a.get("date"))
    for a in shown:
        add("us", 14, "artifact-shown", f"we showed \"{a.get('name')}\" — no reaction logged", a.get("date"))
    for a in acts[:6]:
        if str(a.get("type")) in ("note", "deliverable", "stage", "email"):
            add("us", 8, "our-activity", f"{a.get('type')}: {str(a.get('summary') or '')[:110]}", a.get("date"))
    if deal.get("nextDraft"):
        add("us", 6, "draft-ready", "a touch is drafted and waiting to send")
    if (deal.get("twin") or {}):
        add("us", 6, "twin", f"digital twin filled in ({len(deal.get('twin') or {})} field(s))")

    # --- clock ------------------------------------------------------------
    lim = cfg.get("staleDays") or 10
    a_touch = age(deal.get("lastTouch")) if deal.get("lastTouch") else None
    if a_touch is not None:
        add("clock", min(40, round(40 * a_touch / max(lim, 1))), "stale",
            f"{a_touch}d since last touch (this stage's limit is {lim}d)", deal.get("lastTouch"))
    a_stage = age(deal.get("stageSince"))
    if a_stage is not None and a_stage > lim:
        add("clock", min(30, round(a_stage / 3)), "stuck",
            f"{a_stage}d parked in {cfg.get('label') or deal.get('stage')} without advancing", deal.get("stageSince"))
    them_ages = [f["age"] for f in facts if f["actor"] == "them" and f["age"] is not None]
    if not them_ages:
        add("clock", 34, "silent", "no buyer-side signal on record at all")
    elif min(them_ages) > THEM_HALFLIFE:
        add("clock", 24, "gone-quiet", f"last buyer-side signal was {min(them_ages)}d ago")
    if not deal.get("nextAction"):
        add("clock", 18, "no-next", "no next action on an in-motion deal")

    # --- structure --------------------------------------------------------
    if (co.get("referrer") or "").strip() or co.get("referredByCompany"):
        add("structure", 18, "referred", f"warm — referred by {co.get('referrer') or co.get('referredByCompany')}")
    if str(co.get("source") or "").lower().startswith(("warm", "network", "referral", "family", "friend")):
        add("structure", 14, "warm-source", f"warm source: {co.get('source')}")
    amt = float(deal.get("value") or 0) or (float(deal.get("retainer") or 0) * 12 + float(deal.get("buildFee") or 0))
    if amt:
        add("structure", 10, "priced", f"priced at ${round(amt):,}")
    else:
        add("clock", 12, "unpriced", "no value on the deal — nobody has agreed what this is worth")
    nd = _d(deal.get("nextDate"))
    if nd and nd >= TODAY:
        add("structure", 16, "scheduled", f"a next step is on the calendar for {nd.isoformat()}")

    return {"company": co.get("name") or deal.get("name"), "stage": deal.get("stage"),
            "stageLabel": cfg.get("label") or deal.get("stage"), "amount": amt, "facts": facts}


def decay(f, halflife):
    if f["age"] is None:
        return 1.0
    return max(0.0, 1.0 - (f["age"] / (halflife * 2.0)))


SCALE = 26.0    # points of net evidence per logistic unit


def _logistic(net):
    """Saturating, never hard-clamped — a reader that pegs at 100 has lost all resolution,
    and resolution is the entire point of a spread."""
    import math
    return round(100.0 / (1.0 + math.exp(-net / SCALE)))


def read_prosecution(bundle):
    """Only buyer-side action counts, and it expires. Clock at full weight."""
    alive, cited = 0.0, []
    for f in bundle["facts"]:
        if f["actor"] == "them":
            if f["age"] is not None and f["age"] > THEM_HALFLIFE:
                continue                            # expired — the prosecution does not count it
            k = f["w"] * decay(f, THEM_HALFLIFE)
            if k > 0:
                alive += k; cited.append((round(k), f))
    dead = sum(f["w"] for f in bundle["facts"] if f["actor"] == "clock")
    cited += [(f["w"], f) for f in bundle["facts"] if f["actor"] == "clock"]
    cited.sort(key=lambda x: -x[0])
    return _logistic(alive - dead), [c[1] for c in cited[:4]]


def read_defence(bundle):
    """The whole record counts. The clock is softened where there is a reason for the silence."""
    net, cited = 0.0, []
    pots = {"us": 0.0, "structure": 0.0}            # our effort and their structure both saturate:
    caps = {"us": 40.0, "structure": 30.0}          # no volume of OUR work proves THEIR intent
    scheduled = any(f["key"] == "scheduled" for f in bundle["facts"])
    for f in bundle["facts"]:
        if f["actor"] in ("them", "us", "structure"):
            k = f["w"] * (decay(f, THEM_HALFLIFE * 2) if f["actor"] == "them" else
                          (decay(f, 45) if f["actor"] == "us" else 1.0))
            if f["actor"] in pots:
                room = max(0.0, caps[f["actor"]] - pots[f["actor"]])
                k = min(k, room)
                pots[f["actor"]] += k
            net += k; cited.append((round(k), f))
        else:
            soften = 0.45 if scheduled else 0.8     # a booked next step is a reason for silence
            net -= f["w"] * soften
            cited.append((round(f["w"] * soften * 0.5), f))
    cited.sort(key=lambda x: -x[0])
    return _logistic(net), [c[1] for c in cited[:4]]


def contested_fact(bundle):
    """The load-bearing disagreement: the biggest thing the defence counts and the prosecution throws out."""
    ours = [f for f in bundle["facts"] if f["actor"] in ("us", "structure")]
    expired = [f for f in bundle["facts"] if f["actor"] == "them" and f["age"] is not None and f["age"] > THEM_HALFLIFE]
    pool = sorted(ours + expired, key=lambda f: -f["w"])
    if not pool:
        return None
    top = pool[0]
    why = ("the prosecution discards it — it is our effort, not their intent"
           if top["actor"] == "us" else
           ("the prosecution discards it — structure is not action" if top["actor"] == "structure"
            else f"the prosecution discards it — {top['age']}d old, past the {THEM_HALFLIFE}d intent window"))
    return {"fact": top["text"], "actor": top["actor"], "weight": top["w"], "why": why}


def next_action_from_spread(bundle, pros, defn, contest):
    """The disagreement, written as the move that would settle it."""
    co = bundle["company"]
    if contest and contest["actor"] == "us":
        return f"Convert our own work into their action: put \"{contest['fact']}\" in front of {co} and ask for a dated response."
    if contest and contest["actor"] == "structure":
        return f"Structure is doing the work, not the buyer — use the warm path to {co} to get one buyer-side commitment on the record."
    if contest and contest["actor"] == "them":
        return f"Their last real signal has expired — re-open with a direct reference to it and ask the closing question."
    if pros >= 60 and defn >= 60:
        return f"Both readers agree {co} is alive — advance it; the exit criteria are the only thing in the way."
    return f"Neither reader can find buyer-side evidence for {co} — ask the disqualifying question and free the slot."


NARRATE_SYS = {
    "prosecution": ("You are the PROSECUTION on a sales deal. Your job is to argue this deal is DEAD. "
                    "You may cite ONLY the evidence bundle given. Buyer-side actions are the only evidence "
                    "of intent; the seller's own activity proves nothing. Default to dead where evidence is "
                    "absent. Reply with JSON only: {\"alive\": 0-100, \"case\": \"<=40 words\", "
                    "\"killer\": \"the single strongest fact for your side\"}"),
    "defence": ("You are the DEFENCE on a sales deal. Your job is to argue this deal is ALIVE. "
                "You may cite ONLY the evidence bundle given. Structural warmth, work delivered, and a "
                "scheduled next step all count. Reply with JSON only: {\"alive\": 0-100, "
                "\"case\": \"<=40 words\", \"killer\": \"the single strongest fact for your side\"}")
}


def narrate(bundle, side):
    payload = json.dumps({"company": bundle["company"], "stage": bundle["stageLabel"],
                          "amount": bundle["amount"],
                          "evidence": [{"actor": f["actor"], "fact": f["text"], "ageDays": f["age"]}
                                       for f in bundle["facts"]]}, indent=1)
    try:
        r = subprocess.run(["claude", "-p", "--append-system-prompt", NARRATE_SYS[side],
                            f"Evidence bundle:\n{payload}\n\nReturn only the JSON."],
                           capture_output=True, text=True, timeout=NARRATE_TIMEOUT, cwd=REPO)
        txt = ((r.stdout or "") + (r.stderr or "")).strip()
        i, j = txt.find("{"), txt.rfind("}")
        if i >= 0 and j > i:
            return json.loads(txt[i:j + 1])
        if "login" in txt.lower():
            return {"error": "the claude CLI is not logged in on this host — narration skipped, "
                             "scores are unaffected (they are deterministic)"}
        return {"error": f"no parseable JSON from the model: {txt[:100]}"}
    except FileNotFoundError:
        return {"error": "claude CLI not on PATH — narration skipped, scores are unaffected"}
    except Exception as e:
        return {"error": str(e)[:120]}


def compute(data, do_narrate=False):
    heat = heat_rollup()
    rows = []
    for deal in data.get("deals", []) or []:
        stage = deal.get("stage")
        if stage in BENCH or stage in TERMINAL:
            continue
        b = evidence(deal, data, heat)
        pros, pcite = read_prosecution(b)
        defn, dcite = read_defence(b)
        spread = abs(defn - pros)
        verdict = ("contested" if spread >= SPREAD_WIDE else
                   ("agree-alive" if (pros + defn) / 2 >= 55 else
                    "agree-dead" if (pros + defn) / 2 < 40 else "agree-uncertain"))
        contest = contested_fact(b)
        row = {"dealId": deal["id"], "company": b["company"], "stage": stage, "stageLabel": b["stageLabel"],
               "amount": b["amount"], "prosecution": pros, "defence": defn, "spread": spread,
               "verdict": verdict, "contested": contest,
               "prosecutionCites": [f["text"] for f in pcite],
               "defenceCites": [f["text"] for f in dcite],
               "nextAction": next_action_from_spread(b, pros, defn, contest),
               "facts": b["facts"], "date": TODAY.isoformat()}
        if do_narrate:
            row["narration"] = {"prosecution": narrate(b, "prosecution"), "defence": narrate(b, "defence")}
        rows.append(row)
    rows.sort(key=lambda r: -r["spread"])
    return {"generated": TODAY.isoformat(), "wideAt": SPREAD_WIDE, "intentWindowDays": THEM_HALFLIFE,
            "reads": rows,
            "method": ("Two readers, one evidence bundle, opposed priors. The prosecution counts only "
                       f"buyer-side action inside a {THEM_HALFLIFE}-day intent window and applies the clock at full "
                       "weight; the defence counts the whole record and softens the clock when a next step is booked. "
                       "The spread is the disagreement, not a confidence interval.")}


def persist(result):
    lock = open(LOCK, "a+")
    fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        with open(OUT, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        with open(DATA) as f:
            fresh = json.load(f)
        by = {r["dealId"]: r for r in result["reads"]}
        for deal in fresh.get("deals", []) or []:
            r = by.get(deal.get("id"))
            if r:                                    # compact mirror so the board renders without a fetch
                deal["spread"] = {"date": r["date"], "prosecution": r["prosecution"], "defence": r["defence"],
                                  "spread": r["spread"], "verdict": r["verdict"],
                                  "contested": (r["contested"] or {}).get("fact", ""),
                                  "nextAction": r["nextAction"]}
        tmp = DATA + ".tmp.adv"
        with open(tmp, "w") as f:
            json.dump(fresh, f, indent=2, ensure_ascii=False)
        os.replace(tmp, DATA)
        with open(DATA_JS, "w") as f:
            f.write("/* AUTO-GENERATED from data.json by server.py. Source of truth is data.json. */\n")
            f.write("window.CRM_DATA = " + json.dumps(fresh, indent=2, ensure_ascii=False) + ";\n")
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)


def main():
    with open(DATA) as f:
        data = json.load(f)
    res = compute(data, do_narrate="--narrate" in sys.argv)
    for r in res["reads"]:
        bar = "█" * round(r["spread"] / 5)
        print(f"{r['company'][:30]:<30} prosecution {r['prosecution']:>3} | defence {r['defence']:>3} "
              f"| spread {r['spread']:>3} {bar}  {r['verdict']}")
        if r["contested"]:
            print(f"    contested: {r['contested']['fact']}\n               ({r['contested']['why']})")
        print(f"    → {r['nextAction']}")
        if r.get("narration"):
            for side in ("prosecution", "defence"):
                n = r["narration"][side]
                print(f"    {side}: {n.get('case') or n.get('error')}")
    if "--dry" in sys.argv:
        print("\n(dry — nothing written)")
        return
    persist(res)
    print(f"\nwrote {os.path.basename(OUT)} + mirrored spread onto {len(res['reads'])} deal(s)")


if __name__ == "__main__":
    main()
