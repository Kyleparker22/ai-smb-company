#!/usr/bin/env python3
"""The mirror close — hand the buyer our own read of the deal we are in with them.

Every vendor runs a private read of you. It is the one artifact they would never
show you, because it contains the places they are pushing and you are not moving.

This renders that artifact for the buyer. It says where they are on their OWN
ladder, and — the part that makes it worth reading — where WE are ahead of them,
named as our error rather than their delay. A proposal argues. This diagnoses,
including the diagnosis of us.

It is the same computation the internal board runs (`crm/mirror.py`), rendered for
the person on the other side of the table. There is no second, softer model of the
deal: if the brief and the board ever disagree, the product is a lie.

REFUSALS (both load-bearing):
  * An UNMAPPED deal produces no brief. A diagnosis assembled from nothing is
    worse than no diagnosis — it would be a mirror of our own assumptions handed
    to the buyer with their name on it.
  * Unknown is never rendered as cleared. If nobody marked a step yes, the brief
    says we do not know, and asks.

Run:
    python3 crm/mirror_close.py --list
    python3 crm/mirror_close.py --deal <dealId|company substring>
    python3 crm/mirror_close.py --deal southern --html out.html
    python3 crm/mirror_close.py --deal southern --json
"""
import json, os, sys, argparse, datetime, html as _html

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mirror  # one definition of the ladder, the requirements, and the computation

# Playground switch: data resolves under DATA_DIR, never HERE. HERE is CODE.
ROOT = os.environ.get("YOURCO_DATA_ROOT") or os.path.dirname(HERE)
CLIENTS = os.path.join(ROOT, "clients")
TODAY = datetime.date.today()

# What our own stage is claiming when it sits above their ladder. Phrased as our
# overreach, not their hesitation — the buyer already knows they haven't moved.
OVERREACH_LINE = {
    "felt": "we have been treating this as a problem you have already named to yourself",
    "internal": "we have been treating this as something you have already said out loud to someone else",
    "budget": "we sent pricing as though the money already has a home",
    "risk": "we have been moving as though you have already priced what happens to you personally if this fails",
    "story": "we have been assuming you already have the sentence you would use with your team",
    "authority": "we have been proceeding as though everyone who can say no has been in a room",
    "switch": "we have been assuming you can already picture a normal Monday with this running",
}

# The internal ladder's `ask` is written for whoever is running the deal ("have THEY
# said it out loud?"). Handing that phrasing to the buyer would show them a document
# written about them rather than to them. Same question, second person.
BUYER_ASK = {
    "felt": "In your own words, unprompted — what is the problem you want gone?",
    "internal": "Who else in your world has heard you say that? Not been told. Heard you say it.",
    "budget": "Can you name the line this gets paid out of, without going to check?",
    "risk": "If this fails, what happens to you personally? That one goes unanswered right up until it stalls the deal.",
    "story": "What exact sentence would you use to explain this to the people it changes?",
    "authority": "Who else can kill this, and have they been in a room — not briefed afterwards?",
    "switch": "Describe a normal Monday once this is running. If it won't come, it isn't real yet.",
}


def _slug(s):
    return "".join(c if c.isalnum() else "-" for c in (s or "").lower()).strip("-")


def our_exposure(row):
    """What WE have at risk here, computed — not a rhetorical gesture.

    A folder with a cost ledger and no signature means we have been absorbing
    build cost against a deal nobody has papered. Naming it is what earns the
    right to ask them for the budget line.
    """
    out = []
    if row["stage"] in ("givefirst", "discovery", "sitdown", "audit", "proposal"):   # aliases kept post-merge
        slug = _slug(row["company"])
        if os.path.isdir(CLIENTS):
            for d in sorted(os.listdir(CLIENTS)):
                if d.startswith("_") or not os.path.isdir(os.path.join(CLIENTS, d)):
                    continue
                stem = slug.split("-")[0]
                if (d in slug or slug.startswith(d) or (stem and stem in d)) and \
                        os.path.exists(os.path.join(CLIENTS, d, "cost.md")):
                    out.append(f"We have been building against this deal before it is papered "
                               f"(`clients/{d}/cost.md` is a real ledger against an unsigned engagement). "
                               f"That is our exposure, not yours — and it is why the next question is a "
                               f"question and not another deliverable.")
                    break
    return out


def brief(data, want):
    r = mirror.compute(data)
    rows = r["rows"]
    hit = [x for x in rows if x["dealId"] == want] or \
          [x for x in rows if want.lower() in (x["company"] or "").lower()]
    if not hit:
        return None, f"no live deal matches {want!r} (bench deals are excluded by the board)"
    if len(hit) > 1:
        return None, "matches " + ", ".join(f"{x['company']} ({x['dealId']})" for x in hit) + " — be specific"
    row = hit[0]
    if row["unmapped"]:
        return None, (f"{row['company']}: the mirror has never been filled in, so there is nothing to "
                      f"show them. Fill it from the record first — a brief built on zero marked steps "
                      f"would be our assumptions wearing their name.")

    steps = {s["key"]: s for s in r["steps"]}
    order = [s["key"] for s in r["steps"]]
    return {
        "generated": r["generated"], "company": row["company"], "dealId": row["dealId"],
        "ourStage": row["stageLabel"],
        "ladder": [{"key": k, "label": steps[k]["label"], "ask": BUYER_ASK.get(k, ""),
                    "state": ("cleared" if k in row["cleared"] else
                              "blocked" if k in row["blocked"] else "unknown")} for k in order],
        "clearedCount": row["clearedCount"], "total": len(order),
        "overreach": row["overreach"], "outOfOrder": row["outOfOrder"],
        "firstGap": row["firstGap"],
        # Second-person by default; a custom step with no buyer phrasing gets a neutral
        # line rather than leaking the internal, third-person wording into their copy.
        "firstGapAsk": (BUYER_ASK.get(row["firstGap"],
                                      "What would have to be true here before this is real for you?")
                        if row["firstGap"] else None),
        "ourExposure": our_exposure(row),
        "honesty": ("Every line above is either something a human marked after a real conversation, or "
                    "it says unknown. Nothing here was inferred from how far along our own process is — "
                    "that inference is the thing this document exists to catch."),
    }, None


def render_text(b):
    L = []
    L.append(f"Where this actually stands — {b['company']}")
    L.append(f"{b['generated']}\n")
    L.append("This is our own system's read of this deal. We are sending it to you unedited,")
    L.append("including the parts that are about us.\n")
    L.append(f"YOUR LADDER — {b['clearedCount']} of {b['total']} steps cleared")
    for s in b["ladder"]:
        mark = {"cleared": "[x]", "blocked": "[!]", "unknown": "[ ]"}[s["state"]]
        L.append(f"  {mark} {s['label']}" + ("" if s["state"] != "unknown" else "   (we don't know)"))
    L.append("")
    if b["overreach"]:
        L.append(f"WHERE WE GOT AHEAD OF YOU — our stage is '{b['ourStage']}', which assumed:")
        for k in b["overreach"]:
            L.append(f"  - {OVERREACH_LINE.get(k, k)}")
        L.append("  That is our error in sequencing, not a complaint about your pace.")
        L.append("")
    if b["outOfOrder"]:
        L.append("ONE THING WORTH NAMING")
        L.append("  You have cleared later steps while an earlier one is still open. In our experience")
        L.append("  that reads as genuine enthusiasm running ahead of commitment — the pattern that")
        L.append("  looks like progress right up until it stalls. Better to say it than to discover it.")
        L.append("")
    for line in b["ourExposure"]:
        L.append("WHAT WE HAVE AT RISK")
        L.append("  " + line)
        L.append("")
    if b["firstGapAsk"]:
        L.append("THE ONE QUESTION THAT DECIDES THIS")
        L.append(f"  {b['firstGapAsk']}")
        L.append("  Not a signature. An answer.")
        L.append("")
    L.append("--")
    L.append(b["honesty"])
    return "\n".join(L)


def render_html(b):
    e = _html.escape
    rows = "".join(
        f"<li class='{s['state']}'><span>{'✓' if s['state']=='cleared' else '!' if s['state']=='blocked' else '·'}</span>"
        f"<div><b>{e(s['label'])}</b>{'' if s['state']!='unknown' else '<em> — we don’t know</em>'}</div></li>"
        for s in b["ladder"])
    over = ""
    if b["overreach"]:
        items = "".join(f"<li>{e(OVERREACH_LINE.get(k,k))}</li>" for k in b["overreach"])
        over = (f"<h2>Where we got ahead of you</h2><p>Our stage is <b>{e(b['ourStage'])}</b>, which assumed:</p>"
                f"<ul class='plain'>{items}</ul><p class='muted'>That is our error in sequencing, not a "
                f"complaint about your pace.</p>")
    ooo = ("<h2>One thing worth naming</h2><p>You have cleared later steps while an earlier one is still "
           "open. In our experience that reads as genuine enthusiasm running ahead of commitment — the "
           "pattern that looks like progress right up until it stalls. Better to say it than to discover "
           "it.</p>") if b["outOfOrder"] else ""
    exp = "".join(f"<h2>What we have at risk</h2><p>{e(x)}</p>" for x in b["ourExposure"])
    q = (f"<h2>The one question that decides this</h2><p class='q'>{e(b['firstGapAsk'])}</p>"
         f"<p class='muted'>Not a signature. An answer.</p>") if b["firstGapAsk"] else ""
    return f"""<!doctype html><meta charset="utf-8"><title>Where this stands — {e(b['company'])}</title>
<style>
:root{{--ink:#1a1a1f;--mut:#6b6b76;--line:#e4e2dd;--bg:#faf9f6;--accent:#3b3a67}}
@media(prefers-color-scheme:dark){{:root{{--ink:#eceaf2;--mut:#9d9aa8;--line:#2d2c36;--bg:#141319}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.6 ui-serif,Georgia,serif;max-width:44rem;margin:0 auto;padding:3rem 1.5rem}}
h1{{font-size:1.6rem;margin:0 0 .2rem;font-weight:600}}
h2{{font-size:.78rem;letter-spacing:.09em;text-transform:uppercase;color:var(--mut);margin:2.4rem 0 .7rem;font-weight:600}}
.date{{color:var(--mut);font-size:.85rem;margin-bottom:2rem}}
ul.ladder{{list-style:none;padding:0;margin:0}}
ul.ladder li{{display:flex;gap:.8rem;padding:.5rem 0;border-bottom:1px solid var(--line)}}
ul.ladder li span{{width:1.2rem;color:var(--mut)}}
li.cleared span{{color:var(--accent);font-weight:700}}
li.unknown{{color:var(--mut)}}
em{{font-style:italic;color:var(--mut)}}
ul.plain{{padding-left:1.1rem}} ul.plain li{{margin:.35rem 0}}
.q{{font-size:1.15rem;border-left:3px solid var(--accent);padding-left:1rem;margin:.5rem 0}}
.muted{{color:var(--mut);font-size:.9rem}}
footer{{margin-top:3rem;padding-top:1.2rem;border-top:1px solid var(--line);color:var(--mut);font-size:.85rem}}
</style>
<h1>Where this actually stands</h1>
<div class="date">{e(b['company'])} · {e(b['generated'])}</div>
<p>This is our own system’s read of this deal. We are sending it to you unedited, including the parts
that are about us.</p>
<h2>Your ladder — {b['clearedCount']} of {b['total']} cleared</h2>
<ul class="ladder">{rows}</ul>
{over}{ooo}{exp}{q}
<footer>{e(b['honesty'])}</footer>
"""


def main():
    ap = argparse.ArgumentParser(description="Render the buyer-facing mirror brief for one deal.")
    ap.add_argument("--deal", help="deal id or a substring of the company name")
    ap.add_argument("--list", action="store_true", help="list live deals and whether each is renderable")
    ap.add_argument("--html", metavar="PATH", help="write the brief as HTML to PATH")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    with open(mirror.DATA) as f:
        data = json.load(f)

    if a.list or not a.deal:
        r = mirror.compute(data)
        print(f"Live deals — {len(r['rows'])}\n")
        for row in r["rows"]:
            state = "NOT RENDERABLE (mirror empty)" if row["unmapped"] else \
                    f"renderable — {row['clearedCount']}/{len(r['steps'])} cleared, " \
                    f"{len(row['overreach'])} overreach"
            print(f"  {row['company'][:34]:<34} {row['dealId']:<8} {state}")
        if not a.deal:
            print("\nPass --deal <id|name> to render one.")
        return 0

    b, err = brief(data, a.deal)
    if err:
        print("refused: " + err, file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(b, indent=2)); return 0
    if a.html:
        with open(a.html, "w") as f:
            f.write(render_html(b))
        print(f"wrote {a.html}")
        return 0
    print(render_text(b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
