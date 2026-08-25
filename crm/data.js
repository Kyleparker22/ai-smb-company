/* AUTO-GENERATED from data.json by server.py. Source of truth is data.json. */
window.CRM_DATA = {
  "meta": {
    "updated": "",
    "owner": "David",
    "note": "Empty store \u2014 vocabulary kept so the dashboards and checks have something to anchor to. Records fill as you work.",
    "referralTiers": {
      "rates": [
        10,
        12.5,
        15
      ],
      "thresholds": [
        6,
        11
      ],
      "override": 1
    },
    "repRecruiters": {},
    "mirrorSteps": [
      {
        "key": "felt",
        "label": "Named it to themselves",
        "ask": "Have they said the problem out loud, in their own words, unprompted?"
      },
      {
        "key": "internal",
        "label": "Said it to someone else inside",
        "ask": "Has anyone else in their world heard them say it \u2014 partner, ops lead, spouse?"
      },
      {
        "key": "budget",
        "label": "Knows where the money comes from",
        "ask": "Can they name the line this gets paid out of, without checking?"
      },
      {
        "key": "risk",
        "label": "Priced their personal downside",
        "ask": "Do they know what happens to THEM if this fails? Unanswered, it stalls at the last step."
      },
      {
        "key": "story",
        "label": "Has the sentence for their team",
        "ask": "What exact sentence do they use to explain this to the people it changes?"
      },
      {
        "key": "authority",
        "label": "Everyone who can say no has been in a room",
        "ask": "Who else can kill this, and have they been present rather than briefed?"
      },
      {
        "key": "switch",
        "label": "Pictured the first Monday after",
        "ask": "Can they describe a normal Monday once it's running? If not, it isn't real to them yet."
      }
    ],
    "mirrorRequires": {
      "givefirst": [
        "felt"
      ],
      "sitdown": [
        "felt",
        "internal"
      ],
      "audit": [
        "felt",
        "internal",
        "budget"
      ],
      "proposal": [
        "felt",
        "internal",
        "budget",
        "risk",
        "story"
      ],
      "signed": [
        "felt",
        "internal",
        "budget",
        "risk",
        "story",
        "authority"
      ],
      "build": [
        "felt",
        "internal",
        "budget",
        "risk",
        "story",
        "authority",
        "switch"
      ],
      "live": [
        "felt",
        "internal",
        "budget",
        "risk",
        "story",
        "authority",
        "switch"
      ],
      "expand": [
        "felt",
        "internal",
        "budget",
        "risk",
        "story",
        "authority",
        "switch"
      ]
    },
    "autonomy": {
      "note": "CRM action rungs per processes/autonomy-matrix.md. Kolby evals, the Founder promotes \u2014 never edited by an agent.",
      "windowDays": 30,
      "thresholds": {
        "R2": {
          "weeks": 4,
          "uses": 10
        },
        "R1": {
          "weeks": 8,
          "uses": 20
        }
      },
      "actions": [
        {
          "key": "read",
          "label": "Read / roll up the pipeline",
          "kind": "observation",
          "rung": "R3",
          "ceiling": "R3",
          "note": "inherently safe"
        },
        {
          "key": "deal-agent-note",
          "label": "Deal-agent status note",
          "kind": "observation",
          "rung": "R3",
          "ceiling": "R3",
          "note": "writes to agentLog only, reversible in git"
        },
        {
          "key": "adversarial-read",
          "label": "Adversarial read (spread)",
          "kind": "observation",
          "rung": "R3",
          "ceiling": "R3",
          "note": "analysis only, deterministic, writes no deal field"
        },
        {
          "key": "escalate",
          "label": "Raise an escalation",
          "kind": "observation",
          "rung": "R3",
          "ceiling": "R3",
          "note": "queues an ask; commits nothing"
        },
        {
          "key": "enrich",
          "label": "Enrich a company from its public site",
          "kind": "action",
          "rung": "R2",
          "ceiling": "R3",
          "note": "auto + reversible; fills CRM gaps"
        },
        {
          "key": "autolog",
          "label": "Auto-log an activity from mail/calendar",
          "kind": "action",
          "rung": "R1",
          "ceiling": "R2",
          "note": "lands in the pending queue; a human confirms"
        },
        {
          "key": "draft-touch",
          "label": "Draft the next touch",
          "kind": "action",
          "rung": "R1",
          "ceiling": "R2",
          "note": "drafting is free; sending is not"
        },
        {
          "key": "queue-artifact",
          "label": "Queue an artifact build",
          "kind": "action",
          "rung": "R1",
          "ceiling": "R2",
          "note": "spends build time \u2014 proposed, not started"
        },
        {
          "key": "stage-advance",
          "label": "Advance a deal a stage",
          "kind": "action",
          "rung": "R1",
          "ceiling": "R2",
          "note": "the exit criteria are a human judgement until evidence says otherwise"
        },
        {
          "key": "send-external",
          "label": "Send anything to a human outside yourco",
          "kind": "action",
          "rung": "R1",
          "ceiling": "R1",
          "note": "gated by design \u2014 the Founder sends, agents draft"
        }
      ]
    },
    "agents": [
      "Atlas",
      "Bella",
      "Bird",
      "Brett",
      "Charles",
      "David",
      "Harry",
      "Janice",
      "Jim",
      "Katie",
      "Kemba",
      "Kimi",
      "Reed",
      "Kolby",
      "Kori",
      "Kortney",
      "Luka",
      "Mario",
      "Melanie",
      "Michelle",
      "Pickle",
      "Polo",
      "Rafi",
      "Ray",
      "Reilly",
      "Sadie",
      "Webb"
    ],
    "verticals": [
      "Construction / Building",
      "Design",
      "DTC / E-commerce",
      "Financial / Wealth Advisory",
      "Food & Beverage",
      "Hardscaping / Design-Build",
      "Home Building / Residential",
      "Insurance",
      "Lab / Diagnostics",
      "Landscaping / Lawn",
      "Law Firm",
      "Painting / Home Services",
      "Real Estate",
      "Roofing",
      "Salon / Spa",
      "Staffing",
      "Digital Agency / Consultancy",
      "Other"
    ],
    "activityTypes": [
      "Call",
      "Email",
      "Text",
      "Booking",
      "Meeting",
      "Note",
      "Deliverable",
      "Demo",
      "Audit requested",
      "Audit delivered",
      "Proposal sent",
      "Stage change",
      "Warm intro made",
      "Referral ask",
      "Referral",
      "Connector note",
      "Research",
      "Other"
    ],
    "taskTypes": [
      "Call",
      "Email",
      "Text",
      "Meeting",
      "Send proposal",
      "Follow up",
      "Research",
      "Ask for an intro",
      "Check in",
      "Send materials",
      "Other"
    ],
    "creditFloorPct": 50,
    "activityTypeNotes": {
      "Referral ask": "You ASKED someone for a referral or an intro \u2014 the connector program's leading indicator. Log it whether or not anything came of it; the whole point is that asks are countable before referrals exist. 'Referral' is the lagging half: one arrived.",
      "Referral": "A referral ARRIVED. Pairs with 'Referral ask' \u2014 asks/referrals is the conversion.",
      "Warm intro made": "yourco MADE an introduction for someone else \u2014 the give-first half of the warm network. Deliberately distinct from 'Referral ask' (we asked someone for an intro) and from 'Referral' (one arrived). All three are separate acts and conflating them destroys the only funnel the connector program has.",
      "Audit delivered": "The free Audit was HANDED OVER \u2014 the report is in the prospect's hands, not merely scheduled. The Audit is the front door of the whole motion and until 2026-08-25 nothing counted one, so its conversion to an engagement was unknowable rather than merely unknown. Log it on the day the report lands; the conversion is this company later reaching a signed stage.",
      "Booking": "A slot was BOOKED \u2014 deliberately distinct from 'Meeting' (one was held). Added 2026-08-25 because contact.nextMeeting holds only the NEXT one: the moment a second booking is made the first is overwritten, so bookings were uncountable the same way stage history was. Webb's owned number is bookings at companies the site produced, and the site's Calendly links now carry utm_source so that attribution survives the click.",
      "Audit requested": "Someone asked for the free Audit \u2014 the front of the funnel, written by the site's intake form (runtime/site_intake.py). Deliberately distinct from 'Audit delivered': a request that never became an audit is a different failure from an audit that never became an engagement, and Bella's conversion is measured on the second."
    },
    "sourceChannels": [
      "founder-sourced",
      "warm-network",
      "referral",
      "intent-signal",
      "outbound",
      "inbound-site",
      "content",
      "event",
      "partner-target",
      "other"
    ],
    "sourceChannelNotes": {
      "_why": "Added 2026-08-25. `company.source` is free text and every intake path wrote its own string ('instantly (replied)', 'sadie intent (reddit)', 'audit intake form'), so no surface could ask which CHANNEL produced a company without prefix-matching prose. `channel` is the controlled answer; `source` still records the human detail. `channelSource` says how the value got there: recorded (stamped at intake) \u00b7 restated (a faithful rename of the old free-text source, no judgment added) \u00b7 inferred (a judgment \u2014 say so, and any metric may exclude it).",
      "founder-sourced": "the Founder put the row in by hand. Deliberately NOT the same as warm-network: it says who entered it, and claims nothing about how he knows them.",
      "warm-network": "An existing relationship or an intro \u2014 the stated GTM motion.",
      "referral": "A connector or a client sent them. Pairs with company.referrer.",
      "intent-signal": "Sadie's sweep surfaced them and a human promoted the signal to a row.",
      "outbound": "Replied to a cold campaign.",
      "inbound-site": "Came through a form on the site (audit intake, snapshot).",
      "content": "Came from a post, newsletter or video. Cannot be non-zero before anything is published \u2014 that is the launch-gate, not the audience.",
      "event": "Met in person at an event.",
      "partner-target": "A partnership prospect, not a client.",
      "other": "None of the above \u2014 and if this fills up, the vocabulary is wrong."
    },
    "artifactTypes": [
      "collateral",
      "video",
      "demo",
      "site",
      "document",
      "proposal",
      "other"
    ],
    "artifactTypeNotes": {
      "collateral": "Sales collateral Pickle produced \u2014 one-pager, battlecard, case study, deck. Registering it on a deal is what makes 'did this ever reach a buyer' countable: status `shown` or `reacted` means it did, `built` means it sat in the folder.",
      "video": "A produced video or demo reel (Reed). Registering it on a deal at status `shown`/`reacted` is what makes 'did this asset ever reach a prospect' countable. Same mechanism as `collateral`, and the same missing habit blocks both."
    },
    "stageHistoryNote": "deal.stageHistory \u2014 added 2026-08-25, and it is the one gap on this list that CANNOT be fixed after the fact. `stageSince` records only the CURRENT stage's entry date, so the moment a deal advances, the date it entered the previous stage is overwritten and gone. Nothing else recorded it: there are zero stage-change activities in the log. That means 'days from signature to go-live' (Janice) and 'days from discovery to go-live' (Kimi) would have been unmeasurable even AFTER client #1 \u2014 the data would already have been destroyed. Every entry is {stage, at, source}: `recorded` when the CRM wrote it at the moment of the move, `restated` for the backfilled current stage. History before the current stage is genuinely lost for existing deals; the metrics say so rather than filling it in.",
    "seqStatuses": [
      "not started",
      "sent",
      "opened",
      "replied-positive",
      "replied-negative",
      "bounced",
      "paused"
    ],
    "seqStatusNotes": {
      "_why": "Added 2026-08-25. The old vocabulary had a single undifferentiated `replied`, so 'positive reply rate' \u2014 the one number outbound copy is judged on anywhere \u2014 was not expressible. Instantly already classifies interest (runtime/instantly.py _is_warm), but that classification lived in a vendor's database and never reached the repo. `replied` is retained as a legacy value and counts toward CONTACTED, never toward POSITIVE: an old row must not be promoted to a win by a vocabulary change.",
      "replied-positive": "They replied with interest \u2014 the numerator. This is what runtime/promote.py acts on when it creates a CRM row.",
      "replied-negative": "They replied, and it was a no / unsubscribe / wrong-person. Logging it is the point: a reply rate that counts only the good ones is not a rate."
    }
  },
  "stages": [
    {
      "key": "pre-convo",
      "label": "Pre Convo",
      "hint": "a real human, no conversation about the work yet",
      "exit": "a real conversation held \u2014 business + decision-maker identified",
      "staleDays": 30,
      "owner": "the Founder"
    },
    {
      "key": "discovery",
      "label": "Discovery",
      "hint": "walking the proof, then diagnosing and quantifying the bottleneck",
      "exit": "pain named + data shared + bottleneck quantified in $",
      "staleDays": 14,
      "owner": "the Founder"
    },
    {
      "key": "demo-proposal",
      "label": "Demo and Proposal",
      "hint": "showing the built thing, then the priced proposal",
      "exit": "signed",
      "staleDays": 7,
      "owner": "the Founder"
    },
    {
      "key": "signed-onboarding",
      "label": "Signed & Onboarding",
      "hint": "scaffold fired, kickoff held, access granted",
      "exit": "build scoped + access in hand",
      "staleDays": 5,
      "owner": "Janice"
    },
    {
      "key": "build-implementation",
      "label": "Build & Implementation",
      "hint": "inside the build window",
      "exit": "feature-complete against the scoped modules",
      "staleDays": 5,
      "owner": "Sample Contact"
    },
    {
      "key": "testing",
      "label": "Testing",
      "hint": "shadow mode \u2014 running on real work, only we see the output",
      "exit": "eval gate PASS + verified against what we'd actually send",
      "staleDays": 7,
      "owner": "Kolby"
    },
    {
      "key": "live",
      "label": "Live",
      "hint": "operating; weekly readouts",
      "exit": "terminal \u2014 the engagement stays here. A new module is a NEW DEAL on this company, opened at Demo and Proposal and marked as an expansion.",
      "staleDays": 30,
      "owner": "Atlas"
    },
    {
      "key": "parked",
      "label": "Parked",
      "hint": "deliberately not now \u2014 with a reason",
      "exit": "re-open trigger fires",
      "staleDays": 365,
      "owner": "\u2014"
    }
  ],
  "companies": [],
  "contacts": [],
  "deals": [],
  "closed": [],
  "activities": [],
  "tasks": [],
  "repApplicants": [],
  "graph": {},
  "dispatch": [],
  "todos": []
};
