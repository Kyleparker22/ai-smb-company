/* ============================================================================
   yourco — per-vertical config (the single source for vertical landing pages
   AND the online Revenue Leak Snapshot + report). One yourco entity, many vertical pages.
   Decision: decisions/2026-06-16_online-snapshot.md
            + 2026-06-16_audit-first-os-as-product + brand-architecture-vs-vertical-llcs.

   TO ADD A VERTICAL: copy a block below, change the slug key + content. The
   landing page (vertical-template.html?v=<slug>) and the Revenue Leak Snapshot
   (snapshot.html?v=<slug>) both render from it automatically. Owned by Bella.

   STATS RULE (brand: no fabricated numbers): every stat carries `src` + `url` —
   a real, citable source. Sadie (research agent) sources + cites each stat and hands
   them to Bella, who curates them here; the report renders the source as a clickable
   link, so nothing unsourced ships. If a stat is ever added without a source, use
   src "[verify]" (no url) and it will render visibly as unverified until cited. The
   ROI in the report is computed from the prospect's OWN inputs (math shown), not from
   these stats.
   RECENCY RULE (the Founder, 2026-06-16): every stat must be published within the last ~12
   months (2025-present). No recycled decade-old studies — for an AI-native company,
   dated citations undercut the brand. Sadie refreshes these on a recurring cadence.

   QUESTION TYPES: "number" (numeric), "select" (options[] + optional pct[] parallel
   array mapping each option to a fraction for the leak math), "text".
   The leak model in snapshot.html is generic and reads: leads, missed (pct),
   job_value, admin_hours — keep those four keys present in every vertical.
   ========================================================================== */
window.YOURCO_VERTICALS = {

  /* ----------------------------- LANDSCAPING ----------------------------- */
  landscaping: {
    name: "Landscaping",
    eyebrow: "for landscaping & lawn-care companies",
    heroPain: "Every missed call is a season's contract going to the next crew.",
    heroSub: "Crews are in the field, the phone rings out, and the estimate you'd have won books with someone who answered. yourco audits where your business leaks, then builds the AI system that catches every lead, quotes faster, and follows up — so you stop losing work you already earned.",
    probHead: "Where landscaping businesses quietly leak revenue.",
    bottlenecks: [
      { title: "Missed & after-hours calls", desc: "You're on a job; the phone goes to voicemail. Most homeowners don't leave one — they call the next landscaper in the search results." },
      { title: "Slow estimates & quotes", desc: "Quotes take days because only you write them, at night. The fastest quote usually wins the job — and you're rarely fastest." },
      { title: "Follow-up that never happens", desc: "Warm leads who didn't book the first time rarely get a second touch. No system, no nudge, no recovered revenue." }
    ],
    osPitch: "For a landscaping company that means an AI front desk that answers 24/7 and books the estimate, an estimate assistant that turns quotes around same-day, and a follow-up agent that re-touches every warm lead — coordinated as one system you don't have to run.",
    closeHead: "stop losing jobs you already paid to win.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them and the job is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "46%", l: "of home-services leads from digital marketing convert on the phone call — the call is where the job is won", src: "Invoca, 2025", url: "https://www.pmmag.com/articles/106597-home-services-call-performance-report-46-lead-conversion-rate-segment-benchmarks" }
    ],
    quickAudit: {
      intro: "Six quick questions. We'll show you — on your own numbers — roughly what's leaking and what an AI system could recover. Takes about two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls or leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 120" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average job worth to you?", placeholder: "$1,000" },
        { k: "admin_hours", type: "number", label: "Hours a week you (the owner) spend on quotes, scheduling, and follow-up?", placeholder: "e.g. 12" },
        { k: "quote_speed", type: "select", label: "How fast does a typical estimate go out?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Stop missing calls", "Get quotes out faster", "Follow up with every lead", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: {
        name: "AI Front Desk — your missed calls, handled",
        desc: "An AI receptionist, live in 48 hours, that answers every call day or night, qualifies the job, and books the estimate straight onto your calendar. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable. You just take the booked work."
      },
      outcomes: [
        "Every call answered — in your voice, 24/7, even mid-job and after hours.",
        "Same-day estimates, drafted for your approval instead of piling up for the evening.",
        "Every warm lead re-touched automatically, so fewer jobs slip away."
      ]
    }
  },

  /* ----------------------------- HARDSCAPING ----------------------------- */
  hardscaping: {
    name: "Hardscaping",
    eyebrow: "for hardscape & outdoor-living contractors",
    heroPain: "High-ticket patios and walls don't wait for a callback.",
    heroSub: "A hardscape project is worth more than most home-service jobs — which means every dropped lead, slow proposal, or missed follow-up is real money walking to a competitor. yourco audits where it leaks, then builds the AI system that captures, quotes, and chases every opportunity.",
    probHead: "Where hardscape contractors lose high-value work.",
    bottlenecks: [
      { title: "Missed inquiries on big-ticket jobs", desc: "A single patio or retaining-wall lead can be worth five figures. Miss the call while you're on site and it goes to whoever picks up." },
      { title: "Slow, manual proposals", desc: "Detailed hardscape proposals take days to assemble. The homeowner has three quotes by the time yours lands — and momentum is gone." },
      { title: "Long sales cycles with no follow-up", desc: "Hardscape buyers research for weeks. Without a system nudging them, your warm lead cools and signs with the contractor who stayed in touch." }
    ],
    osPitch: "For a hardscape contractor that means an AI front desk that captures and qualifies every high-value inquiry, a proposal assistant that drafts detailed quotes fast, and a long-cycle follow-up agent that keeps you top-of-mind until the homeowner signs — one system, run for you.",
    closeHead: "don't let a five-figure patio book with someone who answered first.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "55%", l: "of home-service customers now expect a response within an hour — 28% expect it immediately", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "48%", l: "of answered calls fail to give the caller the pricing they asked for", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking on these high-value jobs and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many project inquiries do you get a month?", hint: "Patios, walls, full outdoor-living jobs — a rough count.", placeholder: "e.g. 40" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not respond to quickly enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average hardscape project worth to you?", placeholder: "$12,000" },
        { k: "admin_hours", type: "number", label: "Hours a week you (or a lead) spend building proposals, scheduling, and following up?", placeholder: "e.g. 15" },
        { k: "proposal_speed", type: "select", label: "How long does a detailed proposal usually take to go out?", options: ["Same day", "2–3 days", "A week+", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Capture every inquiry", "Get proposals out faster", "Follow up through the long sales cycle", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: {
        name: "AI Front Desk + Proposal Assistant — every high-value lead, captured and quoted",
        desc: "Live in 48 hours: an AI front desk that captures and qualifies every project inquiry around the clock, books the site visit, and kicks off a fast, detailed proposal draft for your approval. You sign off on anything customer-facing; yourco builds it, runs it, and keeps it reliable."
      },
      outcomes: [
        "Every high-value inquiry captured and qualified — not lost to voicemail mid-install.",
        "Detailed proposals drafted fast, so you're first in the homeowner's inbox, not third.",
        "Automated follow-up across the multi-week sales cycle, so warm leads don't cool and sign elsewhere."
      ]
    }
  },

  /* -------------------------------- HVAC --------------------------------- */
  hvac: {
    name: "HVAC",
    eyebrow: "for HVAC contractors",
    heroPain: "In a heat wave, the phone never stops — and every call you miss is a system install you didn't win.",
    heroSub: "When it's 98° or 12° outside, homeowners call until someone answers. If your techs are on calls and the phone rings out, that emergency — and the replacement it could've become — books with the next company. yourco audits where you leak, then builds the AI system that answers, dispatches, and follows up.",
    probHead: "Where HVAC companies lose work they already earned.",
    bottlenecks: [
      { title: "Missed & after-hours emergency calls", desc: "Peak season and after hours are when the money is — and when techs can't pick up. Those callers don't wait; they call the next company in the results." },
      { title: "Slow dispatch & scheduling", desc: "Booking and dispatch live in your head and on the truck. The lag costs you same-day jobs and frustrates the customers you do reach." },
      { title: "Estimates & maintenance plans that never get a follow-up", desc: "Install quotes and service-agreement upsells go out, then silence. No system re-touches them, so high-margin work slips away." }
    ],
    osPitch: "For an HVAC company that means an AI front desk that answers 24/7 through every heat wave, qualifies the emergency, and books or dispatches the call — plus a follow-up agent that chases every install quote and maintenance-plan renewal. One system, run for you.",
    closeHead: "stop losing peak-season installs to whoever answered first.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them and the job is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$159.4B", l: "U.S. heating & air-conditioning contractor market in 2026", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/market-size/heating-air-conditioning-contractors/1945/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — especially in peak season — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "Across the year — a rough average is fine.", placeholder: "e.g. 200" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough — especially after hours and in peak season?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average job worth to you?", hint: "Blend of service calls and installs.", placeholder: "$1,500" },
        { k: "admin_hours", type: "number", label: "Hours a week you (or office staff) spend on scheduling, dispatch, and follow-up?", placeholder: "e.g. 20" },
        { k: "after_hours", type: "select", label: "What happens to a call that comes in after hours?", options: ["We have a 24/7 answer", "Voicemail", "An answering service takes a message", "It rings out"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call, 24/7", "Dispatch & schedule faster", "Follow up on every estimate & plan", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk + Dispatch — every call answered, every emergency booked",
        desc: "Live in 48 hours: an AI receptionist that answers every call day or night, qualifies the emergency, books or routes it to dispatch, and follows up on estimates and maintenance plans. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable through every peak." },
      outcomes: [
        "Every call answered through the heat wave — no more peak-season jobs lost to voicemail.",
        "Faster dispatch and scheduling, so you book the same-day work instead of losing it.",
        "Automatic follow-up on install quotes and maintenance renewals — the high-margin work stops slipping."
      ]
    }
  },

  /* ------------------------------- PLUMBING ------------------------------ */
  plumbing: {
    name: "Plumbing",
    eyebrow: "for plumbing companies",
    heroPain: "A burst pipe doesn't leave a voicemail. It calls the next plumber.",
    heroSub: "Plumbing emergencies are now-or-never: if you don't answer, they're already dialing someone else. Between jobs on site and calls after hours, the leads you paid to generate slip straight to competitors. yourco audits where it leaks, then builds the AI system that catches every call, books it, and follows up.",
    probHead: "Where plumbing companies lose jobs.",
    bottlenecks: [
      { title: "Missed emergency & after-hours calls", desc: "You're under a sink or it's 11pm — the call goes to voicemail, and an emergency caller never waits. They call the next plumber and book on the spot." },
      { title: "Slow scheduling", desc: "Booking lives on your phone and in your truck, so dispatching the right tech to the right job lags — and you lose same-day work." },
      { title: "Estimates with no follow-up", desc: "Bigger jobs — repipes, water heaters, remodels — get quoted, then forgotten. No system nudges the homeowner, so the job books elsewhere." }
    ],
    osPitch: "For a plumbing company that means an AI front desk that answers every emergency 24/7, qualifies it, and books or dispatches — plus a follow-up agent that re-touches every estimate. One system, run for you, so you stop losing now-or-never calls.",
    closeHead: "stop sending emergencies to the next plumber.",
    stats: [
      { n: "1 in 3", l: "plumbing calls goes unanswered — just a 66% answer rate across the trade", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "55%", l: "of home-service customers now expect a response within an hour — 28% expect it immediately", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$191.4B", l: "U.S. plumbing market in 2026, growing at a 3.1% five-year CAGR", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/industry/plumbers/1946/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — especially on emergencies and after hours — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", placeholder: "e.g. 180" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average job worth to you?", placeholder: "$650" },
        { k: "admin_hours", type: "number", label: "Hours a week you (or office staff) spend on scheduling and follow-up?", placeholder: "e.g. 15" },
        { k: "after_hours", type: "select", label: "What happens to a call that comes in after hours?", options: ["We have a 24/7 answer", "Voicemail", "An answering service takes a message", "It rings out"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every emergency, 24/7", "Schedule & dispatch faster", "Follow up on every estimate", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every emergency caught and booked",
        desc: "Live in 48 hours: an AI receptionist that answers every call around the clock, qualifies the emergency, and books or dispatches it — then follows up on the bigger estimates. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every emergency answered, 24/7 — no more now-or-never calls going to voicemail.",
        "Faster scheduling and dispatch, so you capture the same-day work.",
        "Automatic follow-up on repipe, water-heater, and remodel quotes that used to go cold."
      ]
    }
  },

  /* ------------------------------ ELECTRICAL ----------------------------- */
  electrical: {
    name: "Electrical",
    eyebrow: "for electrical contractors",
    heroPain: "The homeowner with no power calls until someone answers. Make sure it's you.",
    heroSub: "Electrical calls range from urgent outages to high-ticket panel upgrades and rewires — and every one you miss while on a job is revenue walking to a competitor. yourco audits where your business leaks, then builds the AI system that answers, books, and follows up on every lead.",
    probHead: "Where electrical contractors lose work.",
    bottlenecks: [
      { title: "Missed & after-hours calls", desc: "On a job or after hours, the phone rings out — and an urgent caller calls the next electrician rather than wait." },
      { title: "Slow scheduling for site visits", desc: "Panel upgrades and rewires need a visit to quote; manual booking drags, and the homeowner cools on the project." },
      { title: "High-ticket quotes with no follow-up", desc: "Big jobs get estimated, then go quiet. Without a system re-touching them, the work signs with whoever stayed in contact." }
    ],
    osPitch: "For an electrical contractor that means an AI front desk that answers every call, qualifies it, and books the visit — plus a follow-up agent that chases every panel-upgrade and rewire quote. One system, run for you.",
    closeHead: "stop losing panel upgrades to the electrician who picked up.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "55%", l: "of home-service customers expect a response within an hour — electrical faults rarely wait for a callback", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$347.5B", l: "U.S. electricians market in 2026", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/market-size/electricians/189/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", placeholder: "e.g. 120" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average job worth to you?", hint: "Blend of service calls and bigger projects.", placeholder: "$900" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on scheduling, quoting, and follow-up?", placeholder: "e.g. 14" },
        { k: "quote_speed", type: "select", label: "How fast does a typical estimate go out?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call", "Book site visits faster", "Follow up on every quote", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every visit booked",
        desc: "Live in 48 hours: an AI receptionist that answers every call, qualifies it, books the site visit, and follows up on your high-ticket quotes. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — urgent outages and big projects alike, no more voicemail leaks.",
        "Site visits booked faster, before the homeowner cools on the project.",
        "Automatic follow-up on panel-upgrade and rewire quotes that used to slip away."
      ]
    }
  },

  /* ------------------------------- ROOFING ------------------------------- */
  roofing: {
    name: "Roofing",
    eyebrow: "for roofing companies",
    heroPain: "Every missed call is a $10,000 roof going to the next roofer.",
    heroSub: "Storm season, crews on the roof, the phone ringing out — the leads you paid for end up in a competitor's pipeline. yourco audits where your business leaks, then builds the AI system that catches every call, books the inspection, and follows up on every estimate.",
    probHead: "The chaos that's capping your growth.",
    bottlenecks: [
      { title: "Missed & after-hours calls", desc: "Crews can't answer mid-job; homeowners call the next roofer. Storm spikes make it dramatically worse." },
      { title: "Slow inspection scheduling", desc: "Quotes and inspections drag because booking lives in your head and your truck — and momentum is lost." },
      { title: "Leads that never get a second touch", desc: "Estimates sent, then silence — no system to follow up while you're on a roof, so the job signs elsewhere." }
    ],
    osPitch: "For a roofer that means an AI front desk that answers 24/7 (storm season included), books the inspection, and follows up on every estimate — coordinated as one system, not five disconnected tools.",
    closeHead: "stop letting roofs walk to the competition.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them and the roof is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$92.5B", l: "U.S. roofing contractor market in 2026 — with ~109,000 businesses competing for the call", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/market-size/roofing-contractors/198/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — especially through storm spikes — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "Storm months run higher — a yearly average is fine.", placeholder: "e.g. 90" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average roofing job worth to you?", placeholder: "$10,000" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on scheduling inspections, quoting, and follow-up?", placeholder: "e.g. 16" },
        { k: "quote_speed", type: "select", label: "How fast does a typical estimate go out after the inspection?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call, storm season included", "Book inspections faster", "Follow up on every estimate", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every storm-season call, handled",
        desc: "Live in 48 hours: an AI receptionist that answers every call day or night (storm spikes included), qualifies the job, books the inspection, and follows up on every estimate. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered through storm season — no more $10k roofs lost to voicemail.",
        "Inspections booked faster, while the homeowner's roof is still top of mind.",
        "Automatic follow-up on every estimate, so fewer roofs walk to the competition."
      ]
    }
  },

  /* ----------------------------- RESTORATION ----------------------------- */
  restoration: {
    name: "Restoration",
    eyebrow: "for water & fire damage restoration companies",
    heroPain: "A flooded house can't wait for a callback — and neither can the insurance clock.",
    heroSub: "Restoration is the most time-critical trade there is: the homeowner with water rising calls every company until one answers, and the first on site usually wins the job. Miss that call and a five-figure mitigation books with a competitor. yourco audits where you leak, then builds the AI system that captures every emergency and starts the intake instantly.",
    probHead: "Where restoration companies lose emergency jobs.",
    bottlenecks: [
      { title: "Missed 24/7 emergency calls", desc: "Damage doesn't keep business hours. If a 2am flood call hits voicemail, that mitigation job is gone — the homeowner calls until someone picks up." },
      { title: "Slow intake & dispatch", desc: "Every minute of delay means more damage and a colder lead. Manual intake slows the crew getting on site — where the job is won." },
      { title: "Insurance-coordination admin overload", desc: "Documentation, adjusters, and claims paperwork bury your team — time that isn't spent answering the next emergency." }
    ],
    osPitch: "For a restoration company that means an AI front desk that answers every emergency 24/7, runs the intake instantly, and dispatches the crew — plus help with the insurance-documentation load. One system, run for you, so you're first on site.",
    closeHead: "be the company that answers at 2am — and wins the job.",
    stats: [
      { n: "55%", l: "of home-service customers now expect a response within an hour — 28% expect it immediately", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — in an emergency, that's who wins", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$7.2B", l: "U.S. damage-restoration market in 2025 (water & fire), growing ~4.5% a year", src: "IBISWorld, 2025", url: "https://www.ibisworld.com/united-states/market-size/damage-restoration-services/6278/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking on these time-critical jobs and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many emergency calls/leads do you get a month?", placeholder: "e.g. 60" },
        { k: "missed", type: "select", label: "What share do you miss, or not respond to fast enough — especially overnight?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average restoration job worth to you?", placeholder: "$8,000" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on intake, dispatch, and insurance paperwork?", placeholder: "e.g. 25" },
        { k: "after_hours", type: "select", label: "What happens to a call that comes in overnight?", options: ["We have a true 24/7 answer", "Voicemail", "An answering service takes a message", "It rings out"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every emergency, 24/7", "Get crews on site faster", "Tame the insurance paperwork", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Emergency Intake — every 2am call answered and dispatched",
        desc: "Live in 48 hours: an AI front desk that answers every emergency around the clock, runs the intake instantly, and dispatches the crew — then helps carry the insurance-documentation load. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every emergency answered, 24/7 — you become the company that picks up at 2am.",
        "Faster intake and dispatch, so your crew is first on site, where the job is won.",
        "The insurance-paperwork load lightened, freeing your team to answer the next emergency."
      ]
    }
  },

  /* ----------------------------- GARAGE DOOR ----------------------------- */
  "garage-door": {
    name: "Garage Door",
    eyebrow: "for garage door companies",
    heroPain: "A stuck door is an urgent call — and it books with whoever answers first.",
    heroSub: "A car trapped behind a broken door is a now problem; the homeowner calls down the list until someone picks up. Between installs and service runs, the calls you miss become a competitor's same-day jobs. yourco audits where you leak, then builds the AI system that answers, schedules, and follows up.",
    probHead: "Where garage door companies lose jobs.",
    bottlenecks: [
      { title: "Missed service & after-hours calls", desc: "Techs are on a job; the phone rings out. An urgent caller doesn't wait — they book the same-day repair with the next company." },
      { title: "Slow scheduling", desc: "Manual booking lags, so you lose the same-day repair work that's the bread and butter of the trade." },
      { title: "Replacement quotes with no follow-up", desc: "Full door and opener replacements get quoted, then go quiet. No system re-touches the homeowner, so the higher-ticket job slips away." }
    ],
    osPitch: "For a garage door company that means an AI front desk that answers every call, schedules the repair, and dispatches the tech — plus a follow-up agent that chases every door-replacement quote. One system, run for you.",
    closeHead: "stop sending same-day repairs to the company that answered first.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "46%", l: "of home-services leads from digital marketing convert on the phone call — the call is where the job is won", src: "Invoca, 2025", url: "https://www.pmmag.com/articles/106597-home-services-call-performance-report-46-lead-conversion-rate-segment-benchmarks" },
      { n: "268%", l: "ROI on a garage-door replacement — the #1 home-improvement project for resale, on a $4,672 average job", src: "Sample Company 47, 2025 Cost vs. Value Report", url: "https://www.wayne-dalton.com/blogs/detail/resi/why-new-garage-door-tops-list-for-roi-home-improvement" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", placeholder: "e.g. 110" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average job worth to you?", hint: "Blend of repairs and replacements.", placeholder: "$450" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on scheduling and follow-up?", placeholder: "e.g. 12" },
        { k: "after_hours", type: "select", label: "What happens to a call that comes in after hours?", options: ["We have a 24/7 answer", "Voicemail", "An answering service takes a message", "It rings out"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call", "Schedule same-day repairs faster", "Follow up on every replacement quote", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every repair booked",
        desc: "Live in 48 hours: an AI receptionist that answers every call, schedules the repair, dispatches the tech, and follows up on replacement quotes. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more same-day repairs lost to voicemail.",
        "Faster scheduling, so you capture the urgent work instead of losing it.",
        "Automatic follow-up on door and opener replacement quotes that used to go cold."
      ]
    }
  },

  /* ----------------------------- TREE SERVICE ---------------------------- */
  "tree-service": {
    name: "Tree Service",
    eyebrow: "for tree service & arborist companies",
    heroPain: "After a storm, the phone explodes — and you can only win the jobs you actually answer.",
    heroSub: "Storms drive a surge of urgent removal calls, and crews in the field can't pick up. The leads you miss in those windows are exactly the high-value emergency jobs you want most. yourco audits where you leak, then builds the AI system that captures every call, books the estimate visit, and follows up.",
    probHead: "Where tree service companies lose work.",
    bottlenecks: [
      { title: "Missed calls during storm surges", desc: "When demand spikes, crews are out and the phone rings out — and urgent removal jobs book with whoever answered." },
      { title: "Slow estimate visits", desc: "Most tree jobs need an on-site look to quote; manual scheduling drags, and the homeowner books the company that came out first." },
      { title: "Follow-up that never happens", desc: "Quotes for removals and ongoing maintenance go out, then silence — no system re-touches them, so the work slips away." }
    ],
    osPitch: "For a tree service that means an AI front desk that answers every call through storm surges, books the estimate visit, and follows up on every quote. One system, run for you, so you capture the surge instead of missing it.",
    closeHead: "stop losing storm-surge jobs to whoever picked up.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them, especially after a storm", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$39.5B", l: "U.S. tree-trimming services market in 2025", src: "IBISWorld, 2025", url: "https://www.ibisworld.com/united-states/market-size/tree-trimming-services/6064/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — especially through storm surges — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "Storm months spike — a yearly average is fine.", placeholder: "e.g. 70" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough — especially after storms?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average tree job worth to you?", placeholder: "$1,200" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on scheduling estimates and follow-up?", placeholder: "e.g. 12" },
        { k: "quote_speed", type: "select", label: "How fast do you get out to quote a job?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call, surge included", "Book estimate visits faster", "Follow up on every quote", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every storm-surge call, captured",
        desc: "Live in 48 hours: an AI receptionist that answers every call through the surge, qualifies the job, books the estimate visit, and follows up on every quote. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered through storm surges — the high-value removals stop slipping away.",
        "Estimate visits booked faster, so you're the company that came out first.",
        "Automatic follow-up on removal and maintenance quotes that used to go cold."
      ]
    }
  },

  /* ----------------------------- SEPTIC & WELL --------------------------- */
  "septic-well": {
    name: "Septic & Well",
    eyebrow: "for septic & well service companies",
    heroPain: "A backed-up septic system is an emergency — and it calls until someone answers.",
    heroSub: "Between scheduled pumping and now emergencies, septic and well calls don't wait. Miss the call while you're on a job and the homeowner — and the system replacement it might've become — books with a competitor. yourco audits where you leak, then builds the AI system that answers, schedules, and follows up.",
    probHead: "Where septic & well companies lose jobs.",
    bottlenecks: [
      { title: "Missed emergency & after-hours calls", desc: "A backup or a dry well is urgent; if the phone rings out, the homeowner calls the next company and books on the spot." },
      { title: "Slow scheduling for pumping & service", desc: "Routine pumping and service bookings lag with manual scheduling, so you lose efficient route-filling work." },
      { title: "System-replacement quotes with no follow-up", desc: "High-ticket septic or well replacements get quoted, then go quiet. Without follow-up, that major work signs elsewhere." }
    ],
    osPitch: "For a septic & well company that means an AI front desk that answers every emergency, schedules pumping and service, and follows up on every replacement quote. One system, run for you, so the urgent calls and the big jobs stop slipping.",
    closeHead: "stop sending backups — and replacements — to the next company.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "55%", l: "of home-service customers now expect a response within an hour — 28% expect it immediately", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$8.1B", l: "U.S. septic, drain & sewer cleaning market in 2025, up 4.3% on the year", src: "IBISWorld, 2025", url: "https://www.ibisworld.com/united-states/market-size/septic-drain-sewer-cleaning-services/4710/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", placeholder: "e.g. 90" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average job worth to you?", hint: "Blend of pumping/service and replacements.", placeholder: "$500" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on scheduling and follow-up?", placeholder: "e.g. 12" },
        { k: "after_hours", type: "select", label: "What happens to a call that comes in after hours?", options: ["We have a 24/7 answer", "Voicemail", "An answering service takes a message", "It rings out"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every emergency, 24/7", "Schedule pumping & service faster", "Follow up on every replacement quote", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every emergency answered, every job scheduled",
        desc: "Live in 48 hours: an AI receptionist that answers every call, qualifies the emergency, schedules pumping and service, and follows up on replacement quotes. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every emergency answered, 24/7 — no more urgent calls going to voicemail.",
        "Faster scheduling for pumping and service, filling your routes efficiently.",
        "Automatic follow-up on septic and well replacement quotes — the big jobs stop slipping."
      ]
    }
  },

  /* ------------------------------- WEDDINGS ------------------------------ */
  weddings: {
    name: "Weddings",
    eyebrow: "for wedding venues, planners & vendors",
    heroPain: "The couple who didn't hear back booked the vendor who answered.",
    heroSub: "Couples inquire with a dozen vendors at once, on the highest-emotion purchase of their lives — and the first warm, fast reply usually wins the booking. Miss the inquiry or answer slow and a five-figure wedding books elsewhere. yourco audits where it leaks, then builds the AI system that captures every inquiry, books the tour, and follows up through the whole planning cycle.",
    probHead: "Where wedding businesses lose bookings.",
    bottlenecks: [
      { title: "Missed & slow-answered inquiries", desc: "Couples message many vendors simultaneously; the one who replies first and warmest gets the tour. Voicemail or a next-day email loses them." },
      { title: "Slow tour / consultation scheduling", desc: "Booking a venue tour or consult drags through email tag — and an excited couple cools fast or books the vendor who got them in the door first." },
      { title: "Follow-up across a long planning cycle", desc: "Weddings are booked months out with many touchpoints; without a system nurturing every lead, warm couples slip away mid-decision." }
    ],
    osPitch: "For a wedding business that means an AI front desk that captures and warmly answers every inquiry 24/7, books the tour or consult, and nurtures each couple across the long planning cycle — one system, run for you, so no booking slips.",
    closeHead: "stop losing weddings to the vendor who replied first.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.invoca.com/blog/how-much-missed-sales-calls-cost-home-services-businesses" },
      { n: "55%", l: "of customers now expect a response within an hour — 28% expect it immediately", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "46%", l: "of leads from digital marketing convert on the phone call — the call is where it's won", src: "Invoca, 2025", url: "https://www.pmmag.com/articles/106597-home-services-call-performance-report-46-lead-conversion-rate-segment-benchmarks" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking on these high-value bookings and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inquiries do you get a month?", placeholder: "e.g. 50" },
        { k: "missed", type: "select", label: "What share do you miss, or not respond to fast/warmly enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average booking worth to you?", placeholder: "$6,000" },
        { k: "admin_hours", type: "number", label: "Hours a week spent answering inquiries, scheduling tours, and following up?", placeholder: "e.g. 15" },
        { k: "response_speed", type: "select", label: "How fast does a typical inquiry get a real reply?", options: ["Within minutes", "A few hours", "Next day", "When we get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every inquiry fast", "Book tours/consults faster", "Nurture couples through the cycle", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every inquiry answered, every tour booked",
        desc: "Live in 48 hours: an AI front desk that warmly answers every inquiry around the clock, books the tour or consult, and nurtures each couple through the planning cycle. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every inquiry answered fast and warm — you're the vendor who replied first.",
        "Tours and consults booked before the couple cools or books elsewhere.",
        "Automated nurture across the long planning cycle, so warm couples don't slip away."
      ]
    }
  },

  /* ------------------------------- PET CARE ------------------------------ */
  "pet-care": {
    name: "Pet Care",
    eyebrow: "for grooming, boarding, daycare & vet practices",
    heroPain: "Every missed call is a grooming client booking with whoever picked up.",
    heroSub: "Pet-care is recurring, appointment-driven revenue — grooming every few weeks, boarding every trip — and it lives or dies on answering the booking call and keeping the calendar full. Missed calls, no-shows, and clients who never rebook are pure leak. yourco audits where it leaks, then builds the AI system that books, reminds, and rebooks.",
    probHead: "Where pet-care businesses lose recurring revenue.",
    bottlenecks: [
      { title: "Missed & after-hours booking calls", desc: "Hands are full with the animals; the phone rings out — and the pet parent books with the next groomer or kennel who answered." },
      { title: "No-shows & empty slots", desc: "Forgotten appointments leave gaps you can't refill same-day — lost revenue you never get back." },
      { title: "Recurring clients who never rebook", desc: "Grooming is a 4–8 week cycle; without a nudge, a loyal client lapses and you don't notice until the chair's empty." }
    ],
    osPitch: "For a pet-care business that means an AI front desk that answers and books every call, a reminder agent that cuts no-shows, and a recall agent that rebooks the recurring clients automatically — one system, run for you, keeping the calendar full.",
    closeHead: "stop letting a full calendar leak out one missed call at a time.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.invoca.com/blog/how-much-missed-sales-calls-cost-home-services-businesses" },
      { n: "20%", l: "of service pros respond to a new lead within an hour — beat them and the booking is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "46%", l: "of leads from digital marketing convert on the phone call — the call is where it's won", src: "Invoca, 2025", url: "https://www.pmmag.com/articles/106597-home-services-call-performance-report-46-lead-conversion-rate-segment-benchmarks" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many booking calls/requests a month?", placeholder: "e.g. 150" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average appointment worth to you?", hint: "Grooming, boarding stay, visit…", placeholder: "$90" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on booking, reminders, and rebooking?", placeholder: "e.g. 12" },
        { k: "rebook", type: "select", label: "How do recurring clients get rebooked today?", options: ["We rebook before they leave", "We text/call later", "They reach out when they remember", "It's hit or miss"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer & book every call", "Cut no-shows", "Rebook recurring clients", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk + Reminders — book every call, fill every slot",
        desc: "Live in 48 hours: an AI front desk that answers and books every call, sends reminders to cut no-shows, and rebooks your recurring clients automatically. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every booking call answered — no more clients lost to voicemail.",
        "Fewer no-shows and same-day gaps from automated reminders.",
        "Recurring clients rebooked on cycle, so the calendar stays full."
      ]
    }
  },

  /* --------------------------- WASTE & RECYCLING ------------------------- */
  "waste-recycling": {
    name: "Waste & Recycling",
    eyebrow: "for junk removal, hauling & dumpster-rental companies",
    heroPain: "A full truck's worth of work goes to whoever answered the quote call.",
    heroSub: "Junk removal, hauling, and dumpster rental run on inbound quote-and-schedule calls — and the crew is on a job, not by the phone. Every missed call is a same-day haul booking with a competitor. yourco audits where it leaks, then builds the AI system that quotes, books, and schedules every job.",
    probHead: "Where waste & hauling companies lose jobs.",
    bottlenecks: [
      { title: "Missed quote & booking calls", desc: "Crews are loading trucks, not answering phones — and a customer who needs it hauled today books the next company that picks up." },
      { title: "Slow quoting & scheduling", desc: "Manual quoting and route scheduling lag, so you lose the same-day and next-day jobs that fill the truck." },
      { title: "Quotes that never get a follow-up", desc: "Bigger cleanouts and recurring commercial pickups get quoted, then go quiet — no system re-touches them, so the job books elsewhere." }
    ],
    osPitch: "For a waste & hauling company that means an AI front desk that answers every call, gives a quote, books and schedules the pickup, and follows up on the bigger jobs — one system, run for you, so the truck stays full.",
    closeHead: "stop sending same-day hauls to the company that answered.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.invoca.com/blog/how-much-missed-sales-calls-cost-home-services-businesses" },
      { n: "55%", l: "of customers now expect a response within an hour — 28% expect it immediately", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "20%", l: "of service pros respond to a new lead within an hour — beat them and the haul is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many quote/booking calls a month?", placeholder: "e.g. 130" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average job worth to you?", hint: "Haul, cleanout, dumpster rental…", placeholder: "$450" },
        { k: "admin_hours", type: "number", label: "Hours a week spent quoting, booking, and scheduling pickups?", placeholder: "e.g. 14" },
        { k: "quote_speed", type: "select", label: "How fast does a quote go out?", options: ["On the call", "Same day", "1–2 days", "When we get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call", "Quote & schedule faster", "Follow up on every quote", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call quoted, booked, and scheduled",
        desc: "Live in 48 hours: an AI front desk that answers every call, gives a quote, books and schedules the pickup, and follows up on the bigger cleanouts and commercial jobs. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every quote call answered — no more same-day hauls lost to voicemail.",
        "Faster quoting and scheduling, so the truck stays full.",
        "Automatic follow-up on cleanout and commercial quotes that used to go cold."
      ]
    }
  },

  /* --------------------------- ACCOUNTING & CPA -------------------------- */
  "accounting-cpa": {
    name: "Accounting & CPA Firms",
    eyebrow: "for accounting & CPA firms",
    heroPain: "Every tax-season call you miss is a client signing with another firm.",
    heroSub: "Returns are due, your team is heads-down, and the phone rings out — so the new client who'd have signed books with the firm that picked up. yourco audits where your firm leaks, then builds the AI system that answers every call, runs new-client intake, and follows up on every lead.",
    probHead: "Where accounting firms quietly lose clients.",
    bottlenecks: [
      { title: "Missed calls in busy season", desc: "Heads-down on returns, the phone goes to voicemail — and prospective clients rarely leave one. They call the next firm in the search results." },
      { title: "Slow, manual client intake", desc: "New-client onboarding lives in email threads and PDFs. The slower the intake, the colder the lead — and the more your staff drowns in admin." },
      { title: "Lead follow-up that never happens", desc: "Consultations that don't sign the first time rarely get a second touch. No system, no nudge, no recovered engagement." }
    ],
    osPitch: "For an accounting firm that means an AI front desk that answers every call (busy season included) and books the consult, an intake assistant that collects everything a new client needs to provide, and a follow-up agent that re-touches every lead — coordinated as one system you don't have to run.",
    closeHead: "stop losing clients you already earned to a voicemail box.",
    stats: [
      { n: "$26,000+", l: "The average small business loses over $26,000 a year to missed calls — every unanswered ring is a client calling someone else.", src: "Ambs Call Center, September 2025", url: "https://www.ambscallcenter.com/blog/cost-of-a-missed-call" },
      { n: "73 days", l: "Filling a CPA-credentialed role now takes 73 days on average — 41% longer than non-CPA hires, so the work piles onto your existing team.", src: "Talentfoot, March 2026", url: "https://talentfoot.com/cpa-time-to-fill-stats/" },
      { n: "$158.4B", l: "US accounting services is a $158.4 billion market across 85,412 firms — you're competing for the same clients with the same staffing crunch.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/market-size/accounting-services/1398/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — especially through busy season — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls or new-client inquiries do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 80" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average client worth to you per year?", placeholder: "$2,500" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on intake, scheduling, and follow-up?", placeholder: "e.g. 15" },
        { k: "season", type: "select", label: "How much does call volume spike in tax season?", options: ["It's manageable", "Noticeably busier", "We're underwater", "We turn work away"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call, busy season included", "Speed up client intake", "Follow up with every lead", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every busy-season call, handled",
        desc: "Live in 48 hours: an AI receptionist that answers every call (tax season included), qualifies the prospect, books the consult, and runs new-client intake. You approve anything client-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered through busy season — no more new clients lost to voicemail.",
        "Faster, cleaner new-client intake, so leads don't go cold and staff stop drowning in admin.",
        "Automatic follow-up on every consultation, so fewer engagements walk to another firm."
      ]
    }
  },

  /* ------------------------------- DENTAL ------------------------------- */
  dental: {
    name: "Dental Practices",
    eyebrow: "for dental practices",
    heroPain: "Every unanswered call is a new patient booking with the practice down the street.",
    heroSub: "Your front desk is with a patient, the phone rings out, and the new patient who'd have booked calls the next office instead. Add no-shows and recall gaps, and the chair sits empty — staffed, but earning nothing. yourco audits where your practice leaks, then builds the AI system that answers every call, books the appointment, and fills the schedule.",
    probHead: "Where dental practices quietly leak revenue.",
    bottlenecks: [
      { title: "Missed new-patient calls", desc: "Front desk is checking someone out; the call goes to voicemail. New patients don't leave one — they book with the practice that answers." },
      { title: "No-shows & empty chairs", desc: "A missed appointment is a chair you staffed for, earning nothing — and most no-shows never reschedule on their own." },
      { title: "Recall & follow-up gaps", desc: "Patients due for a cleaning, or who didn't rebook, quietly slip through. No system to bring them back." }
    ],
    osPitch: "For a dental practice that means an AI front desk that answers every call and books the appointment, automated reminders that cut no-shows, and a recall agent that brings patients back — coordinated as one system, so your chairs stay full.",
    closeHead: "stop letting new patients — and full chairs — walk to the practice down the street.",
    stats: [
      { n: "32%", l: "Nearly a third of calls to dental practices go unanswered — most callers just dial the next office instead of leaving a voicemail.", src: "Reach, June 2025", url: "https://www.getreach.co/blog/32-of-dental-calls-go-unanswered-how-to-fix-it" },
      { n: "$105,000+", l: "The average dental practice loses six figures a year to no-shows and missed appointments — empty chairs you already staffed for.", src: "Clerri, March 2026", url: "https://clerri.com/blog/dental-patient-no-show-statistics" },
      { n: "$196.1B", l: "The US dentist industry is a $196 billion market across roughly 179,000 practices — and front-desk capacity is what caps each one's growth.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/market-size/dentists/1557/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed calls, no-shows, and recall — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 250" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's a new patient worth to you (first-year or lifetime)?", placeholder: "$1,200" },
        { k: "admin_hours", type: "number", label: "Hours a week your front desk spends on scheduling, reminders, and recall?", placeholder: "e.g. 20" },
        { k: "no_show", type: "select", label: "What's your no-show situation?", options: ["Rare", "A few a week", "Several a week", "It's a real problem"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every new-patient call", "Cut no-shows", "Fill recall & rebookings", "Stop drowning in front-desk admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every patient call answered, every chair filled",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books and confirms appointments, sends reminders to cut no-shows, and works your recall list. You approve anything patient-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every new-patient call answered — no more booking the practice down the street.",
        "Fewer no-shows, so the chairs you staffed for actually earn.",
        "Recall and rebookings worked automatically, so the schedule stays full."
      ]
    }
  },

  /* ------------------------- PROPERTY MANAGEMENT ------------------------ */
  "property-management": {
    name: "Property Management",
    eyebrow: "for property management companies",
    heroPain: "Every missed call is a unit staying vacant — or a tenant emergency going unanswered.",
    heroSub: "Prospects call about a listing while your team is showing units or buried in maintenance, and the inquiry goes cold — so they rent the next place. Meanwhile after-hours emergencies ring out. yourco audits where you leak, then builds the AI system that answers every call, fields leasing inquiries, and routes maintenance — day or night.",
    probHead: "Where property managers lose units and burn out.",
    bottlenecks: [
      { title: "Missed leasing inquiries", desc: "Prospects call about a listing and get voicemail — then rent the next place. Every day a unit sits vacant is rent you'll never recover." },
      { title: "After-hours emergencies", desc: "Maintenance doesn't keep business hours. A burst pipe at midnight that rings out means a furious tenant and a bigger repair bill." },
      { title: "Tenant-call & follow-up overload", desc: "Routine tenant calls and leasing follow-up bury your team — time not spent filling units." }
    ],
    osPitch: "For a property manager that means an AI front desk that answers every call, qualifies and follows up on leasing inquiries, and triages maintenance 24/7 — coordinated as one system you don't have to staff around the clock.",
    closeHead: "stop letting vacant units — and 2am emergencies — go to voicemail.",
    stats: [
      { n: "77%", l: "77% of renters want a response within a single day — slow follow-up sends prospective tenants to the next listing.", src: "Leasey.AI (citing Zillow Group), May 2026", url: "https://www.leasey.ai/resources/research/what-happens-to-apartment-inquiries-on-weekends-and-after-hours-multifamily-lead-conversion-analysis" },
      { n: "60%", l: "Leasing teams that only answer phones during business hours lose 60% of after-hours inquiries entirely.", src: "Leasey.AI, May 2026", url: "https://www.leasey.ai/resources/research/leasing-conversion-rate-automation-benchmarks" },
      { n: "$139.9B", l: "US property management is a $139.9B industry across roughly 340,000 firms — a crowded market where responsiveness wins.", src: "IBISWorld, May 2026", url: "https://www.ibisworld.com/united-states/industry/property-management/1356/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed leasing calls and after-hours gaps — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls/inquiries do you get a month?", hint: "Prospective tenants plus tenant calls — a rough number is fine.", placeholder: "e.g. 150" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's a filled unit worth to you (monthly rent or annual management fee)?", placeholder: "$1,800" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on calls, leasing follow-up, and maintenance coordination?", placeholder: "e.g. 25" },
        { k: "after_hours", type: "select", label: "What happens to an after-hours emergency call?", options: ["We have a true 24/7 answer", "Voicemail", "An answering service takes a message", "It rings out"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every leasing inquiry", "Handle after-hours emergencies", "Follow up to fill units faster", "Stop drowning in tenant calls"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every leasing call caught, every emergency routed",
        desc: "Live in 48 hours: an AI front desk that answers every call, qualifies and follows up on leasing inquiries, and triages maintenance around the clock — routing true emergencies the moment they come in. You approve anything tenant-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every leasing inquiry answered and followed up — units fill faster, vacancy days drop.",
        "After-hours emergencies caught and routed at 2am, not discovered at 8am.",
        "Routine tenant calls handled, freeing your team to actually lease."
      ]
    }
  },

  /* ------------------------------- MED SPA ------------------------------ */
  "med-spa": {
    name: "Med Spas",
    eyebrow: "for med spas & aesthetic practices",
    heroPain: "Every missed call is a high-value client booking their package somewhere else.",
    heroSub: "Demand for aesthetics is booming — but if the booking is slow or the phone rings out, the client books with whoever makes it easy. Add no-shows on staffed slots and warm consults that never get followed up, and the revenue leaks. yourco audits where your med spa leaks, then builds the AI system that captures every booking and follows up on every consult.",
    probHead: "Where med spas leak booming demand.",
    bottlenecks: [
      { title: "Slow or missed bookings", desc: "Clients book with whoever answers first. A slow form or a missed call sends a high-value treatment to the spa down the road." },
      { title: "No-shows on staffed slots", desc: "An empty chair you staffed and prepped for is pure lost revenue — and most no-shows never rebook on their own." },
      { title: "Consults that never get followed up", desc: "Warm consultation leads who didn't book the first time rarely get a second touch. No system, no recovered package." }
    ],
    osPitch: "For a med spa that means an AI front desk that answers and books 24/7, reminders that cut no-shows, and a follow-up agent that re-touches every consult — coordinated as one system, so booming demand actually lands on your calendar.",
    closeHead: "stop letting high-value clients book with whoever answered first.",
    stats: [
      { n: "79%", l: "79% of med spa clients abandon a booking when it's too slow or hard — they book with whoever makes it easy.", src: "Zenoti, October 2025", url: "https://www.zenoti.com/thecheckin/salon-spa-booking-communication-trends" },
      { n: "23–34%", l: "Aesthetic and medical appointment no-shows run 23–34% nationwide — every empty chair is lost revenue you already staffed for.", src: "Prospyr, May 2025", url: "https://www.prospyrmed.com/blog/post/solving-no-show-problems-in-aesthetic-practices" },
      { n: "$8.4B", l: "The US med spa market hit ~$8.4B across 10,488+ locations — booming demand, but only if you capture the calls coming in.", src: "Covenant Health Advisors, April 2025", url: "https://covenanthealthadvisors.com/2025-medspa-market-outlook/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through slow bookings, no-shows, and un-followed consults — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls/booking inquiries do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 120" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average client worth to you (treatment or package)?", placeholder: "$1,500" },
        { k: "admin_hours", type: "number", label: "Hours a week your front desk spends on booking, reminders, and follow-up?", placeholder: "e.g. 18" },
        { k: "booking", type: "select", label: "How do most clients try to book?", options: ["They call", "Online or DM", "Walk-in", "A mix"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Capture every booking", "Cut no-shows", "Follow up on every consult", "Stop drowning in front-desk admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every booking captured, every consult followed up",
        desc: "Live in 48 hours: an AI front desk that answers and books 24/7, confirms and reminds to cut no-shows, and follows up on every consultation. You approve anything client-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every booking captured — high-value clients land on your calendar, not a competitor's.",
        "Fewer no-shows, so the slots you staffed for actually earn.",
        "Automatic follow-up on every consult, so warm leads turn into booked packages."
      ]
    }
  },

  /* ----------------------------- REAL ESTATE ---------------------------- */
  "real-estate": {
    name: "Real Estate",
    eyebrow: "for real estate agents & brokerages",
    heroPain: "The first agent to call back usually wins the client — and you're rarely first.",
    heroSub: "A buyer or seller fills out a form, you're at a showing, and by the time you call back they're working with the agent who answered in five minutes. Speed-to-lead decides who gets the commission. yourco audits where your pipeline leaks, then builds the AI system that responds instantly, qualifies the lead, and follows up until they book.",
    probHead: "Where real estate leads slip away.",
    bottlenecks: [
      { title: "Slow speed-to-lead", desc: "Leads go cold in minutes. At a showing or on a call, you can't respond fast enough — and the fastest agent wins the client." },
      { title: "Missed & after-hours inquiries", desc: "Buyers browse at night and call on impulse. If it rings out, they're on to the next agent before morning." },
      { title: "Follow-up that never happens", desc: "Most online leads need many touches to convert. Without a system, warm leads go untouched and the commission walks." }
    ],
    osPitch: "For an agent or brokerage that means an AI front desk that responds to every lead in seconds, qualifies buyers and sellers, books the showing or call, and follows up until they're ready — coordinated as one system, so you're always the first to call back.",
    closeHead: "stop losing commissions to the agent who called back first.",
    stats: [
      { n: "21x", l: "Respond to a web lead within 5 minutes and you're 21x more likely to convert it than after 30.", src: "AgentZap (Real Trends / InsideSales Lead Response Study), May 2026", url: "https://agentzap.ai/blog/real-estate-lead-statistics" },
      { n: "1–4%", l: "Online leads from Zillow, Realtor.com and paid ads typically convert at just 1–4% from inquiry to closing.", src: "Conversion Realtor, February 2026", url: "https://conversionrealtor.com/conversion-research/real-estate-conversion-rate-benchmark" },
      { n: "1.45M", l: "NAR counts 1,453,690 Realtors competing for the same buyers and sellers you are.", src: "National Association of Realtors, 2025", url: "https://www.nar.realtor/magazine/real-estate-news/nar-membership-remains-above-forecast" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through slow response and dropped follow-up — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many leads/inquiries do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 60" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not respond to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average commission worth to you per closing?", placeholder: "$9,000" },
        { k: "admin_hours", type: "number", label: "Hours a week you spend chasing leads, scheduling showings, and following up?", placeholder: "e.g. 15" },
        { k: "speed", type: "select", label: "How fast do you typically respond to a new online lead?", options: ["Within minutes", "Within an hour", "Same day", "When I can"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Respond to every lead instantly", "Never miss an after-hours inquiry", "Follow up until they convert", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Lead Response — first to call back, every time",
        desc: "Live in 48 hours: an AI front desk that responds to every lead in seconds, qualifies buyers and sellers, books the showing or call, and follows up until they're ready. You approve anything client-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every lead answered in seconds — you're the first agent to call back, so you win the client.",
        "After-hours inquiries captured overnight, not lost to the next agent by morning.",
        "Relentless follow-up on every lead, so warm prospects convert instead of going cold."
      ]
    }
  },

  /* ------------------------------ LAW FIRMS ----------------------------- */
  "law-firms": {
    name: "Law Firms",
    eyebrow: "for law firms & solo attorneys",
    heroPain: "The first lawyer to answer usually signs the client — and your phone is going to voicemail.",
    heroSub: "A potential client with a problem calls firm after firm until one picks up — and that's who they hire. You're in court or with a client, the call rings out, and the case signs elsewhere. yourco audits where your firm leaks, then builds the AI system that answers every call, runs intake, and follows up on every lead.",
    probHead: "Where law firms lose clients before they sign.",
    bottlenecks: [
      { title: "Missed & after-hours calls", desc: "You're in court or in a meeting; the prospective client calls the next firm. Most never leave a voicemail — they just hire whoever answered." },
      { title: "Slow, manual intake", desc: "New-matter intake lives in callbacks and forms. Every hour of delay is a colder lead — and a client who's already talking to another firm." },
      { title: "Lead follow-up that never happens", desc: "Consultations that don't sign the first time rarely get a second touch. No system, no nudge, no recovered case." }
    ],
    osPitch: "For a law firm that means an AI front desk that answers every call 24/7 and books the consult, an intake assistant that captures the matter details, and a follow-up agent that re-touches every lead — coordinated as one system you don't have to run.",
    closeHead: "stop letting signed cases go to the firm that picked up first.",
    stats: [
      { n: "78%", l: "78% of legal clients hire the first lawyer who answers — yet 35% of calls to firms go unanswered.", src: "Bigger Law Firm Magazine (Law Leaders study), August 2025", url: "https://www.biggerlawfirm.com/news/new-national-study-finds-35-of-law-firm-calls-go-unanswered-costing-industry-an-estimated-109-billion-annually/" },
      { n: "14%", l: "The average law firm converts just 14% of its leads from first inquiry into a signed client.", src: "AgentZap (citing Clio), May 2026", url: "https://agentzap.ai/blog/law-firm-lead-generation-statistics" },
      { n: "$405.3B", l: "US law firms are a $405.3B industry across 159,398 firms — a massive, competitive market for the same clients.", src: "IBISWorld, 2025", url: "https://www.ibisworld.com/united-states/market-size/law-firms/1389" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed calls and slow intake — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls or new-matter inquiries do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 70" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average case or client worth to you?", placeholder: "$3,500" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on intake, scheduling, and follow-up?", placeholder: "e.g. 15" },
        { k: "after_hours", type: "select", label: "What happens to a call that comes in after hours?", options: ["We have a true 24/7 answer", "Voicemail", "An answering service takes a message", "It rings out"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call, 24/7", "Speed up client intake", "Follow up with every lead", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every prospective-client call answered",
        desc: "Live in 48 hours: an AI receptionist that answers every call 24/7, qualifies the matter, books the consult, and runs intake. You approve anything client-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered, 24/7 — no more signed cases lost to voicemail.",
        "Faster, cleaner intake, so leads don't cool while they talk to another firm.",
        "Automatic follow-up on every consult, so fewer cases walk away."
      ]
    }
  },

  /* -------------------------- INSURANCE AGENCIES ------------------------ */
  "insurance-agencies": {
    name: "Insurance Agencies",
    eyebrow: "for independent insurance agencies",
    heroPain: "Quote shoppers buy from whoever answers first — and a one-minute delay can cost you the policy.",
    heroSub: "A prospect requesting a quote calls several agencies; the first to respond usually writes the policy. You're with a client, the call rings out, and the premium binds elsewhere. Add renewals that slip, and clients quietly walk. yourco audits where your agency leaks, then builds the AI system that answers every call, quotes faster, and works every renewal.",
    probHead: "Where insurance agencies lose policies.",
    bottlenecks: [
      { title: "Slow lead response", desc: "In insurance, minutes matter — a delayed response sends the quote to a faster agent. Speed-to-lead is the whole game." },
      { title: "Missed quote calls", desc: "On the phone with one client while three more call for quotes. The ones that ring out bind with someone else." },
      { title: "Renewal & follow-up gaps", desc: "Renewals and warm leads slip without a system. Every lapsed client is recurring revenue gone." }
    ],
    osPitch: "For an insurance agency that means an AI front desk that answers every call and starts the quote instantly, plus follow-up that works every renewal and lead — coordinated as one system, so the fastest responder is always you.",
    closeHead: "stop losing policies to the agent who called back first.",
    stats: [
      { n: "391%", l: "In insurance sales, a response delay of more than one minute drops your odds of converting the lead by 391%.", src: "VanillaSoft, March 2025", url: "https://vanillasoft.com/blog/the-importance-of-speed-to-lead-in-the-insurance-industry" },
      { n: "84%", l: "The average insurance agency retains just 84% of clients — roughly 1 in 6 walks every year if renewals aren't worked.", src: "Insurance Back Office Hub, November 2025", url: "https://insurancebackofficehub.com/insurance-retention-statistics" },
      { n: "435,454", l: "There are 435,454 insurance brokerages and agencies in the US as of 2026 — a crowded field where the fastest responder wins.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/number-of-businesses/insurance-brokers-agencies/1331/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through slow quotes and missed renewals — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many quote calls or leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 100" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not respond to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average policy/client worth to you (annual commission)?", placeholder: "$1,200" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on quoting, renewals, and follow-up?", placeholder: "e.g. 18" },
        { k: "speed", type: "select", label: "How fast do you typically respond to a new quote request?", options: ["Within minutes", "Within an hour", "Same day", "When I can"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Respond to every quote instantly", "Never miss a call", "Work every renewal", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every quote answered, every renewal worked",
        desc: "Live in 48 hours: an AI front desk that answers every call, starts the quote instantly, and follows up on renewals and warm leads. You approve anything client-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every quote request answered fast — you become the agent who responds first.",
        "Renewals worked automatically, so fewer clients lapse and walk.",
        "Warm leads followed up, so more quotes actually bind."
      ]
    }
  },

  /* -------------------------- MORTGAGE BROKERS -------------------------- */
  "mortgage-brokers": {
    name: "Mortgage Brokers",
    eyebrow: "for mortgage brokers & loan officers",
    heroPain: "Most borrowers apply with one lender — usually the first to call back.",
    heroSub: "A borrower inquires, you're heads-down on another file, and by the time you respond they've applied with the lender who answered first. Speed-to-lead decides who funds the loan. yourco audits where your pipeline leaks, then builds the AI system that responds instantly, qualifies the borrower, and follows the application through.",
    probHead: "Where mortgage leads slip away.",
    bottlenecks: [
      { title: "Slow speed-to-lead", desc: "Borrowers go with whoever responds first — and most submit only one application. Lose those minutes, lose the loan." },
      { title: "Missed & after-hours inquiries", desc: "Buyers shop nights and weekends. An inquiry that rings out is a loan funding with another lender by Monday." },
      { title: "Application follow-up gaps", desc: "Pre-approvals and warm leads stall without a system to keep them moving — and the deal goes cold." }
    ],
    osPitch: "For a mortgage broker that means an AI front desk that responds to every lead in seconds, qualifies the borrower, books the call, and follows the application through — coordinated as one system, so you're always first to respond.",
    closeHead: "stop losing loans to the lender who answered first.",
    stats: [
      { n: "21x", l: "Leads contacted within five minutes are 21x more likely to become a qualified opportunity — speed-to-lead decides who wins the loan.", src: "Sayvo (citing HBR/MIT Lead Response study), February 2026", url: "https://sayvo.ai/insights/mortgage-speed-to-lead-statistics-2026" },
      { n: "~70%", l: "Nearly seven in 10 Americans submit only one application when getting a mortgage — the first lender to respond usually wins.", src: "Yahoo Finance (citing Zillow), January 2026", url: "https://finance.yahoo.com/news/nearly-70-us-homebuyers-dont-120000765.html" },
      { n: "$9.1B", l: "US loan brokers are a $9.1 billion industry in 2026 — a large, competitive market where speed-to-lead is your edge.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/industry-statistics/market-size/loan-brokers-united-states/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through slow response and dropped follow-up — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many leads/inquiries do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 80" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not respond to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average commission worth to you per funded loan?", placeholder: "$6,000" },
        { k: "admin_hours", type: "number", label: "Hours a week you spend chasing leads, qualifying, and following up?", placeholder: "e.g. 15" },
        { k: "speed", type: "select", label: "How fast do you typically respond to a new lead?", options: ["Within minutes", "Within an hour", "Same day", "When I can"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Respond to every lead instantly", "Never miss an after-hours inquiry", "Keep applications moving", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Lead Response — first to call back, every time",
        desc: "Live in 48 hours: an AI front desk that responds to every lead in seconds, qualifies the borrower, books the call, and keeps applications moving. You approve anything client-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every lead answered in seconds — you're the first lender to respond, so you win the loan.",
        "After-hours inquiries captured overnight, not lost by Monday.",
        "Applications kept moving, so fewer pre-approvals stall and die."
      ]
    }
  },

  /* ------------------------- WEALTH MANAGEMENT -------------------------- */
  "wealth-management": {
    name: "Sample Contact",
    eyebrow: "for wealth management firms & RIAs",
    heroPain: "A high-net-worth prospect goes with the advisor who responds first — make sure that's you.",
    heroSub: "Acquiring new clients is the hardest part of running an advisory firm, and most still lean on referrals while inbound prospects slip away. A prospect inquires, the response is slow, and the relationship — and the assets — go to a faster advisor. yourco audits where your firm leaks, then builds the AI system that responds instantly, qualifies the prospect, and follows up until they book.",
    probHead: "Where advisory firms leave growth on the table.",
    bottlenecks: [
      { title: "Slow prospect response", desc: "High-value prospects choose whoever responds first. Slow follow-up sends the relationship — and the AUM — elsewhere." },
      { title: "Missed inquiries", desc: "Calls and inquiries that ring out while you're with a client rarely come back. Each one is years of fees lost." },
      { title: "Over-reliance on referrals", desc: "When new-client growth depends on referrals alone, inbound leads go un-worked — and the pipeline stays thin." }
    ],
    osPitch: "For an advisory firm that means an AI front desk that responds to every inquiry, qualifies the prospect, books the intro meeting, and follows up until they're ready — coordinated as one system, so growth doesn't depend on referrals alone.",
    closeHead: "stop letting high-value prospects book with a faster advisor.",
    stats: [
      { n: "78%", l: "78% of prospects choose the firm that responds first — when a high-net-worth lead inquires, speed to reply decides who wins them.", src: "LeadResponse, 2026", url: "https://leadresponse.co/blog/speed-to-lead-statistics" },
      { n: "57%", l: "57% of RIAs name new-client acquisition their top challenge, even as 93% still lean on referrals — slow follow-up leaves growth on the table.", src: "InvestmentNews (Cerulli data), November 2025", url: "https://www.investmentnews.com/practice-management/billion-dollar-rias-prioritize-organic-growth-as-industry-consolidation-accelerates/262947" },
      { n: "16,544", l: "16,544 SEC-registered advisers now manage $176.8 trillion for 73.7 million clients — a vast market where the responsive firm captures the prospect.", src: "Investment Adviser Association, 2026 Snapshot", url: "https://www.investmentadviser.org/industry-snapshots/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through slow response and referral-only growth — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many prospect inquiries or leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 40" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not respond to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average client worth to you (annual fee or lifetime)?", placeholder: "$5,000" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on prospect intake, scheduling, and follow-up?", placeholder: "e.g. 12" },
        { k: "speed", type: "select", label: "How fast do you typically respond to a new prospect?", options: ["Within minutes", "Within an hour", "Same day", "When I can"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Respond to every prospect fast", "Never miss an inquiry", "Grow beyond referrals", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every prospect answered, every lead worked",
        desc: "Live in 48 hours: an AI front desk that responds to every inquiry, qualifies the prospect, books the intro meeting, and follows up until they're ready. You approve anything client-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every prospect answered fast — you're the advisor who responds first, so you win the relationship.",
        "Inbound inquiries captured, so growth no longer depends on referrals alone.",
        "Relentless follow-up, so high-value prospects convert instead of drifting."
      ]
    }
  },

  /* --------------------------- TITLE & ESCROW -------------------------- */
  "title-escrow": {
    name: "Title & Escrow",
    eyebrow: "for title & escrow companies",
    heroPain: "Agents send orders to the title company that answers — responsiveness is the #1 reason they choose you.",
    heroSub: "When a real estate agent needs a title company, they pick the one that's most responsive — ahead of price or speed of closing. A missed call from an agent or buyer is an order routed to a competitor. yourco audits where you leak, then builds the AI system that answers every call, opens the order, and keeps every closing coordinated.",
    probHead: "Where title & escrow companies lose orders.",
    bottlenecks: [
      { title: "Missed agent & buyer calls", desc: "Agents route orders to whoever picks up. A call that rings out is an order — and a referral relationship — going to another title company." },
      { title: "Slow order intake", desc: "New orders stall in voicemail and email. The slower the intake, the more agents quietly switch to a more responsive partner." },
      { title: "Closing-coordination overload", desc: "Updates, documents, and status calls bury your team — time not spent winning the next order." }
    ],
    osPitch: "For a title & escrow company that means an AI front desk that answers every call, opens the order, and keeps agents and buyers updated through closing — coordinated as one system, so you're the most responsive title partner in your market.",
    closeHead: "stop letting orders route to the title company that answered first.",
    stats: [
      { n: "39%", l: "Responsiveness and communication of the title officer is the #1 reason agents pick a title company — ahead of accuracy or price.", src: "The Real Brokerage Agent Survey via Business Wire, August 2025", url: "https://markets.financialcontent.com/clarkebroadcasting.mymotherlode/article/bizwire-2025-8-20-reals-july-agent-survey-agent-optimism-index-jumps-to-four-month-high-as-transaction-activity-shows-signs-of-improvement" },
      { n: "78%", l: "78% of homebuyers go with the first agent who responds — speed wins the relationship, and the order follows.", src: "AgentZap (citing NAR 2025 Generational Trends), May 2026", url: "https://agentzap.ai/blog/real-estate-lead-statistics" },
      { n: "$17.1B", l: "The US title insurance industry is a $17.1B market across roughly 1,027 firms — every missed order goes to a competitor.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/industry/title-insurance/4784/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed agent calls and slow intake — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls or orders do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 120" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average closing or order worth to you?", placeholder: "$1,500" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on order intake, status calls, and coordination?", placeholder: "e.g. 22" },
        { k: "after_hours", type: "select", label: "What happens to a call that comes in after hours?", options: ["We have a true 24/7 answer", "Voicemail", "An answering service takes a message", "It rings out"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every agent call", "Speed up order intake", "Keep closings coordinated", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every agent call answered, every order opened",
        desc: "Live in 48 hours: an AI front desk that answers every call, opens the order, and keeps agents and buyers updated through closing. You approve anything client-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every agent and buyer call answered — you become the most responsive title partner in your market.",
        "Faster order intake, so agents stop drifting to a quicker competitor.",
        "Closings kept coordinated, freeing your team to win the next order."
      ]
    }
  },

  /* ------------------------------ BOOKKEEPING --------------------------- */
  bookkeeping: {
    name: "Bookkeeping Firms",
    eyebrow: "for bookkeeping firms",
    heroPain: "Every missed call is a small business handing its books to another bookkeeper.",
    heroSub: "A business owner ready to hand off their books calls around until someone picks up — and that's who they hire. You're deep in a client's reconciliation, the phone rings out, and the engagement signs elsewhere. yourco audits where your firm leaks, then builds the AI system that answers every call, runs client onboarding, and follows up on every lead.",
    probHead: "Where bookkeeping firms quietly lose clients.",
    bottlenecks: [
      { title: "Missed prospect calls", desc: "Heads-down in the books, the phone goes to voicemail — and prospects rarely leave one. They hire the firm that answered." },
      { title: "Slow client onboarding", desc: "New-client onboarding lives in email threads and document requests. The slower it moves, the colder the lead and the more your team drowns in admin." },
      { title: "Lead follow-up that never happens", desc: "Prospects who didn't sign the first time rarely get a second touch. No system, no nudge, no recovered engagement." }
    ],
    osPitch: "For a bookkeeping firm that means an AI front desk that answers every call and books the consult, an onboarding assistant that collects everything a new client needs to hand over, and a follow-up agent that re-touches every lead — coordinated as one system you don't have to run.",
    closeHead: "stop losing recurring clients to a voicemail box.",
    stats: [
      { n: "85%", l: "85% of people whose call goes unanswered never call back — a missed call is usually a lost client.", src: "Dialzara, December 2025", url: "https://dialzara.com/blog/missed-calls-hidden-costs-and-ai-solutions" },
      { n: "96%", l: "96% of CFOs now rely on an outside finance or accounting provider, up from 79% a year earlier — demand is surging.", src: "Insignia Resources, 2026", url: "https://www.insigniaresource.com/research/accounting-outsourcing-statistics/" },
      { n: "331,316", l: "There are 331,316 US payroll & bookkeeping firms competing for clients — speed and follow-up win the work.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/number-of-businesses/payroll-bookkeeping-services/1397" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed calls and slow onboarding — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls or new-client inquiries do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 50" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average client worth to you per year?", placeholder: "$3,600" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on onboarding, scheduling, and follow-up?", placeholder: "e.g. 14" },
        { k: "onboarding", type: "select", label: "How fast does a new client get onboarded once they say yes?", options: ["Same week", "1–2 weeks", "3+ weeks", "When we get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call", "Speed up client onboarding", "Follow up with every lead", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every prospect answered, every client onboarded",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the consult, and runs new-client onboarding. You approve anything client-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every prospect call answered — no more recurring clients lost to voicemail.",
        "Faster onboarding, so new clients start (and pay) sooner and staff stop drowning in admin.",
        "Automatic follow-up on every lead, so fewer engagements walk to another firm."
      ]
    }
  },

  /* --------------------------- PUBLIC ADJUSTERS ------------------------- */
  "public-adjusters": {
    name: "Public Adjusters",
    eyebrow: "for public adjusters",
    heroPain: "After a disaster, the adjuster who answers first signs the claim.",
    heroSub: "When a storm hits, policyholders call every public adjuster they can find — and the first to pick up and start the claim usually wins it. You're on a roof or with an adjuster, the phone rings out, and the claim signs with a competitor. yourco audits where you leak, then builds the AI system that answers every call, runs claim intake, and follows up on every lead.",
    probHead: "Where public adjusters lose claims.",
    bottlenecks: [
      { title: "Missed calls during surges", desc: "After a storm, call volume spikes and the overflow goes to voicemail — where desperate policyholders don't wait. They call the next adjuster." },
      { title: "Slow claim intake", desc: "Every hour of delay on a fresh claim is a colder lead and more time for a competitor to sign it. Manual intake can't keep up with a surge." },
      { title: "Lead follow-up that never happens", desc: "Policyholders who didn't sign the first call rarely get a second touch. No system, no nudge, no recovered claim." }
    ],
    osPitch: "For a public adjuster that means an AI front desk that answers every call through a storm surge, runs the claim intake instantly, and follows up on every lead — coordinated as one system, so you're first on every claim.",
    closeHead: "be the adjuster who answers when the storm hits — and signs the claim.",
    stats: [
      { n: "23%", l: "Only 23% of companies answer a new lead within five minutes — after a disaster, the adjuster who responds first signs the claim.", src: "Optifai, April 2026", url: "https://optif.ai/learn/questions/lead-response-time-benchmark/" },
      { n: "$100B", l: "US insured catastrophe losses hit $100 billion in 2025 — every claim is a policyholder who needs it filed fast.", src: "Artemis / Gallagher Re, January 2026", url: "https://www.artemis.bm/news/us-insured-catastrophe-losses-in-2025-12-above-10-year-avg-at-100bn-gallagher-re/" },
      { n: "[verify]", l: "Policyholders who use a public adjuster typically recover materially higher settlements than filing the claim alone.", src: "[verify]", url: "" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — especially through storm surges — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls or claim leads do you get a month?", hint: "Storm months run higher — a yearly average is fine.", placeholder: "e.g. 60" },
        { k: "missed", type: "select", label: "What share do you miss, or not respond to fast enough — especially during surges?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average claim worth to you in fees?", placeholder: "$4,000" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on intake, documentation, and follow-up?", placeholder: "e.g. 20" },
        { k: "surge", type: "select", label: "What happens to call volume after a major storm?", options: ["We handle it fine", "It gets tight", "We're overwhelmed", "We turn claims away"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call through a surge", "Speed up claim intake", "Follow up with every lead", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every storm-surge call answered and intaked",
        desc: "Live in 48 hours: an AI front desk that answers every call (storm surges included), runs claim intake instantly, and follows up on every lead. You approve anything client-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered through a surge — you become the adjuster who picks up when it matters.",
        "Faster claim intake, so you sign the claim before a competitor does.",
        "Automatic follow-up on every lead, so fewer claims walk away."
      ]
    }
  },

  /* ------------------------------ VETERINARY ---------------------------- */
  veterinary: {
    name: "Veterinary Clinics",
    eyebrow: "for veterinary clinics",
    heroPain: "Every unanswered call is a pet owner booking with the clinic across town.",
    heroSub: "Your front desk is with a client and a nervous dog, the phone rings out, and the pet owner who needed an appointment calls the next clinic. Add no-shows and after-hours calls, and the schedule leaks. yourco audits where your clinic leaks, then builds the AI system that answers every call, books the appointment, and keeps the schedule full.",
    probHead: "Where veterinary clinics quietly leak revenue.",
    bottlenecks: [
      { title: "Missed client calls", desc: "Front desk is juggling a full lobby; calls go to voicemail. As many as 1 in 4 ring out — and pet owners book with whoever answers." },
      { title: "No-shows & after-hours calls", desc: "A missed appointment is a slot you staffed for, earning nothing — and after-hours questions that ring out send clients to an ER or a competitor." },
      { title: "Front-desk overload", desc: "Phones, check-ins, and reminders bury your team — time not spent on patients or booking the next appointment." }
    ],
    osPitch: "For a veterinary clinic that means an AI front desk that answers every call and books the appointment, reminders that cut no-shows, and after-hours coverage — coordinated as one system, so your schedule stays full and your team isn't drowning in phones.",
    closeHead: "stop letting pet owners — and full appointment slots — go to the clinic across town.",
    stats: [
      { n: "24–28%", l: "24–28% of calls to the average veterinary clinic go unanswered — as many as 1 in 4 lost appointments.", src: "Peerlogic, July 2025", url: "https://www.peerlogic.com/post/how-many-calls-are-you-missing--and-whats-it-costing-your-clinic" },
      { n: "$100,000+", l: "A typical three-doctor practice loses north of $100,000 a year from missed calls and wasted marketing spend.", src: "Today's Veterinary Business, November 2025", url: "https://todaysveterinarybusiness.com/the-six-figure-problem-with-your-phone-system/" },
      { n: "$74.5B", l: "The US veterinary services market is $74.5 billion in 2026 — a large, growing field of practices competing for the call.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/market-size/veterinary-services/1447/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed calls and no-shows — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 400" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average appointment or client worth to you?", placeholder: "$350" },
        { k: "admin_hours", type: "number", label: "Hours a week your front desk spends on phones, scheduling, and reminders?", placeholder: "e.g. 25" },
        { k: "no_show", type: "select", label: "What's your no-show situation?", options: ["Rare", "A few a week", "Several a week", "It's a real problem"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every client call", "Cut no-shows", "Cover after-hours calls", "Stop drowning in front-desk admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every client call answered, every slot filled",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books and confirms appointments, sends reminders to cut no-shows, and covers after-hours. You approve anything client-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every client call answered — no more appointments lost to the clinic across town.",
        "Fewer no-shows, so the slots you staffed for actually earn.",
        "After-hours calls covered, so worried pet owners reach you, not a competitor."
      ]
    }
  },

  /* ----------------------------- CHIROPRACTIC --------------------------- */
  chiropractic: {
    name: "Chiropractic Practices",
    eyebrow: "for chiropractic practices",
    heroPain: "Every missed call is a new patient booking with the practice down the street.",
    heroSub: "Your front desk is adjusting workflow between patients, the phone rings out, and the new patient who'd have booked calls the next office. Add no-shows on staffed slots, and the schedule leaks. yourco audits where your practice leaks, then builds the AI system that answers every call, books the appointment, and keeps your table busy.",
    probHead: "Where chiropractic practices quietly leak revenue.",
    bottlenecks: [
      { title: "Missed new-patient calls", desc: "Front desk is with a patient; the call goes to voicemail. New patients don't leave one — they book with the practice that answers." },
      { title: "No-shows & cancellations", desc: "A missed visit is a slot you staffed for, earning nothing — and most no-shows never rebook on their own." },
      { title: "Front-desk & follow-up overload", desc: "Phones, check-ins, and recare reminders bury your team — time not spent adjusting or booking the next patient." }
    ],
    osPitch: "For a chiropractic practice that means an AI front desk that answers every call and books the appointment, reminders that cut no-shows, and follow-up that brings patients back — coordinated as one system, so your table stays busy.",
    closeHead: "stop letting new patients — and full slots — walk to the practice down the street.",
    stats: [
      { n: "23%", l: "Nearly 1 in 4 calls to medical practices go unanswered — sent to voicemail, abandoned on hold, or disconnected.", src: "AgentZap (citing Talkdesk Healthcare Report), 2025", url: "https://agentzap.ai/blog/medical-practice-phone-statistics" },
      { n: "$1,500", l: "The average new chiropractic patient is worth about $1,500 in lifetime revenue — so every missed call is real money walking out.", src: "Gitnux Chiropractic Statistics Report, February 2026", url: "https://gitnux.org/chiropractic-facts-and-statistics/" },
      { n: "$24.0B", l: "The US chiropractic industry is a $24.0 billion market in 2026 across roughly 66,000 practices.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/industry-statistics/market-size/chiropractors-united-states/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed calls and no-shows — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 200" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's a new patient worth to you (lifetime value)?", placeholder: "$1,500" },
        { k: "admin_hours", type: "number", label: "Hours a week your front desk spends on phones, scheduling, and recare?", placeholder: "e.g. 18" },
        { k: "no_show", type: "select", label: "What's your no-show situation?", options: ["Rare", "A few a week", "Several a week", "It's a real problem"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every new-patient call", "Cut no-shows", "Bring patients back for recare", "Stop drowning in front-desk admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every patient call answered, every slot filled",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books and confirms appointments, sends reminders to cut no-shows, and works your recare list. You approve anything patient-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every new-patient call answered — no more booking the practice down the street.",
        "Fewer no-shows, so the slots you staffed for actually earn.",
        "Recare and rebookings worked automatically, so your table stays busy."
      ]
    }
  },

  /* --------------------------- PHYSICAL THERAPY ------------------------- */
  "physical-therapy": {
    name: "Physical Therapy Clinics",
    eyebrow: "for physical therapy clinics",
    heroPain: "Every missed call is a referral booking their course of care somewhere else.",
    heroSub: "Your front desk is rooming a patient, the phone rings out, and the referral who needed to schedule calls the next clinic. Add no-shows and drop-offs mid-plan, and a full course of care leaks. yourco audits where your clinic leaks, then builds the AI system that answers every call, books the evaluation, and keeps patients on their plan.",
    probHead: "Where physical therapy clinics quietly leak revenue.",
    bottlenecks: [
      { title: "Missed referral & patient calls", desc: "Front desk is with a patient; the call goes to voicemail. Referrals book with whoever answers — a whole plan of care, gone." },
      { title: "No-shows & mid-plan drop-off", desc: "Each missed visit is a staffed slot earning nothing — and a patient who drops off mid-plan is a course of care left unfinished." },
      { title: "Front-desk & scheduling overload", desc: "Phones, authorizations, and reminders bury your team — time not spent treating or booking the next eval." }
    ],
    osPitch: "For a physical therapy clinic that means an AI front desk that answers every call and books the evaluation, reminders that cut no-shows, and follow-up that keeps patients on their plan — coordinated as one system, so your schedule stays full.",
    closeHead: "stop letting referrals — and full plans of care — walk to the next clinic.",
    stats: [
      { n: "23%", l: "23% of calls to medical practices go unanswered — voicemail, hold drop-off, or disconnect.", src: "AgentZap (citing Talkdesk Healthcare Report), 2025", url: "https://agentzap.ai/blog/medical-practice-phone-statistics" },
      { n: "$252,000+", l: "No-shows can cost a PT practice up to $252,000+ in lost revenue per year.", src: "Second Door, August 2025", url: "https://seconddoor.app/blog/patient-no-shows-are-killing-your-pt-practice-heres-how-to-fix-it" },
      { n: "7,399", l: "There are 7,399 physical therapy rehabilitation centers in the US — a competitive field where responsiveness fills the schedule.", src: "IBISWorld, 2025", url: "https://www.ibisworld.com/united-states/number-of-businesses/physical-therapy-rehabilitation-centers/6047/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed calls and no-shows — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls or referrals do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 150" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's a full course of care worth to you per patient?", placeholder: "$1,400" },
        { k: "admin_hours", type: "number", label: "Hours a week your front desk spends on phones, scheduling, and authorizations?", placeholder: "e.g. 22" },
        { k: "no_show", type: "select", label: "What's your no-show situation?", options: ["Rare", "A few a week", "Several a week", "It's a real problem"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every referral call", "Cut no-shows", "Keep patients on their plan", "Stop drowning in front-desk admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every referral answered, every plan kept on track",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the evaluation, sends reminders to cut no-shows, and follows up to keep patients on their plan. You approve anything patient-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every referral call answered — no more plans of care lost to the next clinic.",
        "Fewer no-shows, so the slots you staffed for actually earn.",
        "Patients kept on their plan, so courses of care get finished."
      ]
    }
  },

  /* -------------------------- CONCRETE & MASONRY ------------------------ */
  "concrete-masonry": {
    name: "Concrete & Masonry",
    eyebrow: "for concrete & masonry contractors",
    heroPain: "Every missed call is a pour going to the next contractor.",
    heroSub: "You're on a job site with the phone in your truck, the call rings out, and the homeowner who wanted a driveway, patio, or foundation books the contractor who picked up. yourco audits where your business leaks, then builds the AI system that answers every call, quotes faster, and follows up on every bid.",
    probHead: "Where concrete contractors quietly lose work.",
    bottlenecks: [
      { title: "Missed & after-hours calls", desc: "Hands in the mud, phone in the truck — the call goes to voicemail, and most callers just dial the next contractor." },
      { title: "Slow estimates & bids", desc: "Bids take days because you write them at night. The fastest quote usually wins the pour — and you're rarely fastest." },
      { title: "Follow-up that never happens", desc: "Bids sent, then silence. No system to follow up while you're on a job, so the work signs elsewhere." }
    ],
    osPitch: "For a concrete contractor that means an AI front desk that answers every call and books the estimate, an estimate assistant that turns bids around fast, and a follow-up agent that re-touches every bid — coordinated as one system you don't have to run.",
    closeHead: "stop letting pours walk to the contractor who answered first.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them and the pour is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$110.5B", l: "US concrete contractors are a $110.5B market across ~94,000 firms — highly fragmented, no player holds even 5% share.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/industry/concrete-contractors/200/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 80" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average job worth to you?", placeholder: "$6,000" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on bids, scheduling, and follow-up?", placeholder: "e.g. 14" },
        { k: "quote_speed", type: "select", label: "How fast does a typical estimate go out?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Stop missing calls", "Get bids out faster", "Follow up on every bid", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every bid followed up",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the estimate, and follows up on every bid. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more pours lost to voicemail.",
        "Faster bids, while the job is still top of mind for the homeowner.",
        "Automatic follow-up on every bid, so fewer jobs walk to the competition."
      ]
    }
  },

  /* --------------------------- FOUNDATION REPAIR ----------------------- */
  "foundation-repair": {
    name: "Foundation Repair",
    eyebrow: "for foundation repair contractors",
    heroPain: "A cracking foundation is an urgent call — and the first to answer wins the job.",
    heroSub: "A homeowner watching a crack spread calls every foundation company until one picks up — and that's who inspects and signs the job. Miss that call and a five-figure repair books elsewhere. yourco audits where you leak, then builds the AI system that answers every call, books the inspection, and follows up on every estimate.",
    probHead: "Where foundation repair companies lose jobs.",
    bottlenecks: [
      { title: "Missed urgent calls", desc: "Foundation problems feel like emergencies. A call that rings out is a worried homeowner dialing the next company." },
      { title: "Slow inspection scheduling", desc: "Inspections and estimates drag because booking lives in your head. The faster you're on site, the more likely you sign the job." },
      { title: "Estimates that never get a second touch", desc: "High-ticket estimates go quiet. Without follow-up, a five-figure repair signs with whoever stayed in touch." }
    ],
    osPitch: "For a foundation repair company that means an AI front desk that answers every call, books the inspection, and follows up on every estimate — coordinated as one system, so you're first on site and first to close.",
    closeHead: "stop letting five-figure repairs walk to the company that answered first.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 worried homeowners never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "55%", l: "of home-service customers now expect a response within an hour — 28% expect it immediately", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — on an urgent repair, that's who wins", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking on these urgent jobs and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 70" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average repair job worth to you?", placeholder: "$8,000" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on scheduling inspections, estimating, and follow-up?", placeholder: "e.g. 16" },
        { k: "quote_speed", type: "select", label: "How fast does a typical estimate go out after the inspection?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every urgent call", "Book inspections faster", "Follow up on every estimate", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every urgent call answered, every estimate followed up",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the inspection, and follows up on every estimate. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every urgent call answered — no more worried homeowners lost to voicemail.",
        "Inspections booked faster, so you're first on site where the job is won.",
        "Automatic follow-up on every estimate, so fewer five-figure repairs walk away."
      ]
    }
  },

  /* ------------------------------- FLOORING ----------------------------- */
  flooring: {
    name: "Flooring",
    eyebrow: "for flooring contractors",
    heroPain: "Every missed call is a floor going to the next installer.",
    heroSub: "You're measuring a job or laying tile, the phone rings out, and the homeowner who wanted new floors books the installer who answered. yourco audits where your business leaks, then builds the AI system that answers every call, quotes faster, and follows up on every estimate.",
    probHead: "Where flooring contractors quietly lose jobs.",
    bottlenecks: [
      { title: "Missed & after-hours calls", desc: "On a job with your hands full, the call goes to voicemail — and the homeowner books the next installer in the search results." },
      { title: "Slow estimates", desc: "Quotes take days because only you write them. The fastest quote usually wins the floor." },
      { title: "Follow-up that never happens", desc: "Estimates sent, then silence. No system to follow up while you're installing, so the job signs elsewhere." }
    ],
    osPitch: "For a flooring contractor that means an AI front desk that answers every call and books the measure, an estimate assistant that turns quotes around fast, and a follow-up agent that re-touches every estimate — coordinated as one system you don't have to run.",
    closeHead: "stop letting floors walk to the installer who answered first.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them and the floor is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$34.0B", l: "US flooring installation is a $34.0B market spread across ~104,000 businesses — fiercely competitive and hard to stand out in.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/industry/flooring-installers/196/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 90" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average job worth to you?", placeholder: "$5,000" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on quotes, scheduling, and follow-up?", placeholder: "e.g. 12" },
        { k: "quote_speed", type: "select", label: "How fast does a typical estimate go out?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Stop missing calls", "Get quotes out faster", "Follow up on every estimate", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every estimate followed up",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the measure, and follows up on every estimate. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more floors lost to voicemail.",
        "Faster quotes, so you're the first installer back to the homeowner.",
        "Automatic follow-up on every estimate, so fewer jobs walk to the competition."
      ]
    }
  },

  /* ----------------------- KITCHEN & BATH REMODELING ------------------- */
  "kitchen-bath": {
    name: "Kitchen & Bath Sample Company 47",
    eyebrow: "for kitchen & bath remodelers",
    heroPain: "Every missed call is a remodel going to the contractor who picked up.",
    heroSub: "A homeowner ready to remodel their kitchen calls around for consultations — and books the remodeler who answers and shows up fast. You're on a job, the call rings out, and a high-ticket remodel signs elsewhere. yourco audits where you leak, then builds the AI system that answers every call, books the consultation, and follows up on every bid.",
    probHead: "Where remodelers quietly lose projects.",
    bottlenecks: [
      { title: "Missed consultation calls", desc: "On a job site, the phone goes to voicemail — and the homeowner books a consult with the remodeler who answered." },
      { title: "Slow consultation scheduling & bids", desc: "Consults and bids drag when booking lives in your head. The remodeler who's fastest to the kitchen table usually wins it." },
      { title: "Follow-up that never happens", desc: "Big-ticket bids go quiet. Without follow-up, the remodel signs with whoever stayed in touch." }
    ],
    osPitch: "For a kitchen & bath remodeler that means an AI front desk that answers every call and books the consultation, plus follow-up on every bid — coordinated as one system you don't have to run.",
    closeHead: "stop letting remodels walk to the contractor who answered first.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them and the remodel is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$175.4B", l: "US remodeling is a $175.4B market with ~704,000 firms competing — homeowners have endless options for their kitchen or bath.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/industry/remodeling/2013/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 60" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average remodel worth to you?", placeholder: "$25,000" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on consults, bids, and follow-up?", placeholder: "e.g. 14" },
        { k: "quote_speed", type: "select", label: "How fast does a typical bid go out after the consult?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Stop missing calls", "Book consultations faster", "Follow up on every bid", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every bid followed up",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the consultation, and follows up on every bid. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more remodels lost to voicemail.",
        "Consultations booked faster, so you're first to the kitchen table.",
        "Automatic follow-up on every bid, so fewer high-ticket jobs walk away."
      ]
    }
  },

  /* ---------------------------- FENCING & DECKS ------------------------ */
  "fencing-decks": {
    name: "Fencing & Decks",
    eyebrow: "for fence & deck builders",
    heroPain: "Every missed call is a fence or deck going to the next builder.",
    heroSub: "You're setting posts or framing a deck, the phone rings out, and the homeowner who wanted a fence books the builder who answered. yourco audits where your business leaks, then builds the AI system that answers every call, quotes faster, and follows up on every estimate.",
    probHead: "Where fence & deck builders quietly lose jobs.",
    bottlenecks: [
      { title: "Missed & after-hours calls", desc: "Hands full on a build, the call goes to voicemail — and the homeowner books the next builder." },
      { title: "Slow estimates", desc: "Quotes take days because only you write them. The fastest quote usually wins the job." },
      { title: "Follow-up that never happens", desc: "Estimates sent, then silence. No system to follow up while you're building, so the work signs elsewhere." }
    ],
    osPitch: "For a fence or deck builder that means an AI front desk that answers every call and books the estimate, an estimate assistant that turns quotes around fast, and a follow-up agent that re-touches every estimate — coordinated as one system you don't have to run.",
    closeHead: "stop letting fences and decks walk to the builder who answered first.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them and the job is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$20.4B", l: "US fence construction is a $20.4B market with ~315,000 contractors competing — a crowded trade where speed wins.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/industry/fence-construction/2022/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 80" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average job worth to you?", placeholder: "$8,000" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on quotes, scheduling, and follow-up?", placeholder: "e.g. 12" },
        { k: "quote_speed", type: "select", label: "How fast does a typical estimate go out?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Stop missing calls", "Get quotes out faster", "Follow up on every estimate", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every estimate followed up",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the estimate, and follows up on every quote. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more fences and decks lost to voicemail.",
        "Faster quotes, so you're the first builder back to the homeowner.",
        "Automatic follow-up on every estimate, so fewer jobs walk to the competition."
      ]
    }
  },

  /* ------------------------------- PAINTING ----------------------------- */
  painting: {
    name: "Painting",
    eyebrow: "for painting contractors",
    heroPain: "Every missed call is a paint job going to the next contractor.",
    heroSub: "You're up a ladder with a brush in hand, the phone rings out, and the homeowner who wanted their house painted books the contractor who answered. yourco audits where your business leaks, then builds the AI system that answers every call, quotes faster, and follows up on every estimate.",
    probHead: "Where painting contractors quietly lose jobs.",
    bottlenecks: [
      { title: "Missed & after-hours calls", desc: "On a job with a brush in hand, the call goes to voicemail — and the homeowner books the next painter." },
      { title: "Slow estimates", desc: "Quotes take days because only you write them. The fastest quote usually wins the job." },
      { title: "Follow-up that never happens", desc: "Estimates sent, then silence. No system to follow up while you're painting, so the work signs elsewhere." }
    ],
    osPitch: "For a painting contractor that means an AI front desk that answers every call and books the estimate, an estimate assistant that turns quotes around fast, and a follow-up agent that re-touches every estimate — coordinated as one system you don't have to run.",
    closeHead: "stop letting paint jobs walk to the contractor who answered first.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them and the job is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$28.2B", l: "US house painting is a $28.2B industry with 223,209 contractors — large, but highly fragmented and fiercely competitive.", src: "IBISWorld, 2025", url: "https://www.ibisworld.com/united-states/market-size/house-painting-decorating-contractors/5738/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 90" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average job worth to you?", placeholder: "$4,000" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on quotes, scheduling, and follow-up?", placeholder: "e.g. 12" },
        { k: "quote_speed", type: "select", label: "How fast does a typical estimate go out?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Stop missing calls", "Get quotes out faster", "Follow up on every estimate", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every estimate followed up",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the estimate, and follows up on every quote. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more paint jobs lost to voicemail.",
        "Faster quotes, so you're the first painter back to the homeowner.",
        "Automatic follow-up on every estimate, so fewer jobs walk to the competition."
      ]
    }
  },

  /* ----------------------------- WINDOW & DOOR -------------------------- */
  "window-door": {
    name: "Window & Door",
    eyebrow: "for window & door companies",
    heroPain: "Every missed call is a replacement job going to the next installer.",
    heroSub: "A homeowner ready to replace their windows calls around for quotes — and books the company that answers and gets a consultation on the calendar fast. You're on an install, the call rings out, and the job signs elsewhere. yourco audits where you leak, then builds the AI system that answers every call, books the consultation, and follows up on every quote.",
    probHead: "Where window & door companies quietly lose jobs.",
    bottlenecks: [
      { title: "Missed quote calls", desc: "On an install, the phone goes to voicemail — and the homeowner books a consult with whoever answered." },
      { title: "Slow consultation scheduling", desc: "Consults and quotes drag when booking lives in your head. The faster you're at the kitchen table, the more likely you win the job." },
      { title: "Follow-up that never happens", desc: "Quotes go quiet. Without follow-up, the replacement job signs with whoever stayed in touch." }
    ],
    osPitch: "For a window & door company that means an AI front desk that answers every call and books the consultation, plus follow-up on every quote — coordinated as one system you don't have to run.",
    closeHead: "stop letting replacement jobs walk to the installer who answered first.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them and the job is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$6.7B", l: "US window installation is a $6.7B market across just 25,194 firms — a focused field where local visibility wins the work.", src: "IBISWorld, 2025", url: "https://www.ibisworld.com/united-states/market-size/window-installation/4869/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 80" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average job worth to you?", placeholder: "$10,000" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on quotes, scheduling, and follow-up?", placeholder: "e.g. 12" },
        { k: "quote_speed", type: "select", label: "How fast does a typical quote go out after the consult?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Stop missing calls", "Book consultations faster", "Follow up on every quote", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every quote followed up",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the consultation, and follows up on every quote. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more replacement jobs lost to voicemail.",
        "Consultations booked faster, so you're first to the kitchen table.",
        "Automatic follow-up on every quote, so fewer jobs walk to the competition."
      ]
    }
  },

  /* ------------------------- GENERAL CONTRACTORS ----------------------- */
  "general-contractors": {
    name: "General Contractors",
    eyebrow: "for general contractors",
    heroPain: "Every missed call is a project going to the contractor who picked up.",
    heroSub: "A homeowner or developer with a project calls around for bids — and the contractor who answers and responds fast gets the walkthrough. You're managing a job site, the call rings out, and the project signs elsewhere. yourco audits where you leak, then builds the AI system that answers every call, books the walkthrough, and follows up on every bid.",
    probHead: "Where general contractors quietly lose projects.",
    bottlenecks: [
      { title: "Missed & after-hours calls", desc: "On a job site all day, the phone goes to voicemail — and the lead books the contractor who answered." },
      { title: "Slow bid scheduling", desc: "Walkthroughs and bids drag when booking lives in your head. The fastest contractor to respond usually gets the project." },
      { title: "Follow-up that never happens", desc: "Bids go quiet. Without follow-up, the project signs with whoever stayed in touch." }
    ],
    osPitch: "For a general contractor that means an AI front desk that answers every call and books the walkthrough, plus follow-up on every bid — coordinated as one system you don't have to run.",
    closeHead: "stop letting projects walk to the contractor who answered first.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them and the project is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$315.5B", l: "US commercial building construction tops $315.5B — a massive market where GCs compete hard on bids, speed, and reliability.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/industry-statistics/market-size/commercial-building-construction-united-states/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 70" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average project worth to you?", placeholder: "$30,000" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on walkthroughs, bids, and follow-up?", placeholder: "e.g. 16" },
        { k: "quote_speed", type: "select", label: "How fast does a typical bid go out?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Stop missing calls", "Book walkthroughs faster", "Follow up on every bid", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every bid followed up",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the walkthrough, and follows up on every bid. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more projects lost to voicemail.",
        "Walkthroughs booked faster, so you're the first GC to respond.",
        "Automatic follow-up on every bid, so fewer projects walk to the competition."
      ]
    }
  },

  /* ------------------------------ HOME BUILDERS ------------------------- */
  "home-builders": {
    name: "Home Builders",
    eyebrow: "for home builders",
    heroPain: "Every missed call is a buyer taking their build to another builder.",
    heroSub: "A buyer ready to build a custom home calls around — and the builder who answers and books a consultation earns the relationship. You're on a site or with a client, the call rings out, and a high-value build signs elsewhere. yourco audits where you leak, then builds the AI system that answers every call, books the consultation, and follows up on every lead.",
    probHead: "Where home builders quietly lose buyers.",
    bottlenecks: [
      { title: "Missed buyer calls", desc: "On a site all day, the phone goes to voicemail — and the buyer books a consult with the builder who answered." },
      { title: "Slow consultation scheduling", desc: "Consults drag when booking lives in your head. On a long sales cycle, the first builder to engage usually wins the buyer." },
      { title: "Follow-up that never happens", desc: "Buyers on a long timeline go quiet without nurture. Without follow-up, the build signs with whoever stayed in touch." }
    ],
    osPitch: "For a home builder that means an AI front desk that answers every call and books the consultation, plus follow-up that nurtures every buyer through a long sales cycle — coordinated as one system you don't have to run.",
    closeHead: "stop letting high-value builds walk to the builder who answered first.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them and the buyer is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$169.8B", l: "US home builders make up a $169.8B industry — high-value projects, long sales cycles, intense competition for every buyer.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/industry-statistics/market-size/home-builders-united-states/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 40" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average build worth to you (your margin)?", placeholder: "$75,000" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on consults, lead nurture, and follow-up?", placeholder: "e.g. 14" },
        { k: "quote_speed", type: "select", label: "How fast does a buyer get a consultation booked?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every buyer call", "Book consultations faster", "Nurture every buyer", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every buyer answered, every lead nurtured",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the consultation, and nurtures every buyer through a long sales cycle. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every buyer call answered — no more builds lost to voicemail.",
        "Consultations booked faster, so you're the first builder to engage.",
        "Every buyer nurtured through the timeline, so fewer high-value builds drift away."
      ]
    }
  },

  /* ------------------------------ EXCAVATION ---------------------------- */
  excavation: {
    name: "Excavation",
    eyebrow: "for excavation & site-work contractors",
    heroPain: "Every missed call is a site-work job going to the next contractor.",
    heroSub: "You're running a machine or grading a site, the phone rings out, and the builder or homeowner who needed excavation books the contractor who answered. yourco audits where your business leaks, then builds the AI system that answers every call, quotes faster, and follows up on every bid.",
    probHead: "Where excavation contractors quietly lose jobs.",
    bottlenecks: [
      { title: "Missed & after-hours calls", desc: "In the cab all day, the call goes to voicemail — and the job books with whoever answered." },
      { title: "Slow bids", desc: "Bids take time because only you price them. The fastest, most responsive contractor usually wins the work." },
      { title: "Follow-up that never happens", desc: "Bids sent, then silence. No system to follow up while you're on a machine, so the work signs elsewhere." }
    ],
    osPitch: "For an excavation contractor that means an AI front desk that answers every call and books the estimate, an estimate assistant that turns bids around fast, and a follow-up agent that re-touches every bid — coordinated as one system you don't have to run.",
    closeHead: "stop letting site-work jobs walk to the contractor who answered first.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them and the job is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$142.5B", l: "US excavation contracting is a $142.5B market — capital-heavy, bid-driven work where responsiveness wins the next job.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/market-size/excavation-contractors/206/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 60" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average job worth to you?", placeholder: "$12,000" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on bids, scheduling, and follow-up?", placeholder: "e.g. 12" },
        { k: "quote_speed", type: "select", label: "How fast does a typical bid go out?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Stop missing calls", "Get bids out faster", "Follow up on every bid", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every bid followed up",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the estimate, and follows up on every bid. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more site-work jobs lost to voicemail.",
        "Faster bids, so you're the first contractor back to the builder.",
        "Automatic follow-up on every bid, so fewer jobs walk to the competition."
      ]
    }
  },

  /* ------------------------------ AUTO REPAIR --------------------------- */
  "auto-repair": {
    name: "Auto Repair",
    eyebrow: "for auto repair shops",
    heroPain: "Every missed call is a repair going to the shop down the road.",
    heroSub: "Your team is under a hood, the phone rings out, and the customer who needed a repair calls the next shop. yourco audits where your shop leaks, then builds the AI system that answers every call, books the appointment, and follows up — so you stop losing work you'd have won.",
    probHead: "Where auto repair shops quietly lose work.",
    bottlenecks: [
      { title: "Missed calls", desc: "Techs are working on cars, not answering phones. Calls go to voicemail — and most customers just dial the next shop." },
      { title: "Slow scheduling", desc: "Booking lives at the front counter. When no one's free to pick up, the appointment goes to a competitor." },
      { title: "Follow-up that never happens", desc: "Estimates and declined work go quiet. No system to follow up, so repairs you quoted never come back." }
    ],
    osPitch: "For an auto repair shop that means an AI front desk that answers every call and books the appointment, plus follow-up on estimates and declined work — coordinated as one system you don't have to run.",
    closeHead: "stop letting repairs drive to the shop down the road.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "$26,000+", l: "The average small business loses over $26,000 a year to missed calls — every unanswered ring is a customer at another shop.", src: "Ambs Call Center, September 2025", url: "https://www.ambscallcenter.com/blog/cost-of-a-missed-call" },
      { n: "$92.1B", l: "US auto repair is a $92.1B market across 307,000 shops — fragmented, with no chain holding even 5% share.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/market-size/auto-mechanics/1689/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 250" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average repair worth to you?", placeholder: "$450" },
        { k: "admin_hours", type: "number", label: "Hours a week your front counter spends on phones and scheduling?", placeholder: "e.g. 18" },
        { k: "quote_speed", type: "select", label: "How fast does a customer get a callback or quote?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call", "Book appointments faster", "Follow up on every estimate", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every bay booked",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the appointment, and follows up on estimates and declined work. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more repairs lost to the shop down the road.",
        "Faster scheduling, so the bays stay full.",
        "Automatic follow-up on estimates, so more quoted work actually comes back."
      ]
    }
  },

  /* ------------------------------ PEST CONTROL ------------------------- */
  "pest-control": {
    name: "Pest Control",
    eyebrow: "for pest control companies",
    heroPain: "Every missed call is a customer booking with the next exterminator.",
    heroSub: "A homeowner with a pest problem wants it gone now — and books whoever answers. Your techs are on routes, the call rings out, and the job goes elsewhere. yourco audits where your business leaks, then builds the AI system that answers every call, books the service, and follows up on every lead.",
    probHead: "Where pest control companies quietly lose jobs.",
    bottlenecks: [
      { title: "Missed & after-hours calls", desc: "Techs on routes can't answer; urgent pest calls go to voicemail — and the homeowner calls the next company." },
      { title: "Slow scheduling", desc: "When booking depends on someone at a desk, calls that come in during routes get lost." },
      { title: "Follow-up & recurring plans", desc: "One-time jobs that could become recurring contracts slip without follow-up — recurring revenue left on the table." }
    ],
    osPitch: "For a pest control company that means an AI front desk that answers every call and books the service, plus follow-up that turns one-time jobs into recurring plans — coordinated as one system you don't have to run.",
    closeHead: "stop letting pest jobs walk to the next exterminator.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them and the job is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$29.7B", l: "US pest control is a $29.7B market and still growing — steady recurring demand, but a crowded field of local operators.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/industry-statistics/market-size/pest-control-united-states/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 150" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average job worth to you?", placeholder: "$300" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on phones, scheduling, and follow-up?", placeholder: "e.g. 16" },
        { k: "quote_speed", type: "select", label: "How fast does a customer get scheduled?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call", "Book service faster", "Turn jobs into recurring plans", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every job booked",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the service, and follows up to turn one-time jobs into recurring plans. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more jobs lost to the next exterminator.",
        "Faster scheduling, so urgent pest calls book with you.",
        "Follow-up that turns one-time jobs into recurring revenue."
      ]
    }
  },

  /* ---------------------------- CLEANING SERVICES ---------------------- */
  "cleaning-services": {
    name: "Cleaning Services",
    eyebrow: "for residential cleaning & maid services",
    heroPain: "Every missed call is a recurring client booking with another cleaner.",
    heroSub: "A homeowner wants a cleaner booked — and goes with whoever answers and quotes fast. Your crews are on jobs, the call rings out, and a recurring client signs elsewhere. yourco audits where your business leaks, then builds the AI system that answers every call, quotes the clean, and follows up on every lead.",
    probHead: "Where cleaning companies quietly lose clients.",
    bottlenecks: [
      { title: "Missed calls", desc: "Crews are cleaning, not answering. Calls go to voicemail — and the homeowner books the next cleaner." },
      { title: "Slow quotes & booking", desc: "Quotes and scheduling drag when there's no one to pick up. The fastest to respond usually wins the recurring client." },
      { title: "Follow-up that never happens", desc: "One-time cleans that could become weekly clients slip without follow-up." }
    ],
    osPitch: "For a cleaning company that means an AI front desk that answers every call, quotes the clean, and books it, plus follow-up that turns one-time jobs into recurring clients — coordinated as one system you don't have to run.",
    closeHead: "stop letting recurring clients book with another cleaner.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them and the client is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$17B", l: "US residential maid services is a $17B market — steady growth, highly fragmented, and intensely competitive locally.", src: "Kentley Insights / GlobeNewswire, 2026", url: "https://www.globenewswire.com/news-release/2026/04/16/3275153/28124/en/United-States-Residential-Maid-Services-Industry-Report-2026-The-Most-Comprehensive-Analysis-Ever-of-the-Little-Researched-17-Billion-Market.html" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 120" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average client worth to you (a clean, or monthly recurring)?", placeholder: "$200" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on quotes, scheduling, and follow-up?", placeholder: "e.g. 14" },
        { k: "quote_speed", type: "select", label: "How fast does a typical quote go out?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call", "Quote & book faster", "Turn cleans into recurring clients", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every clean booked",
        desc: "Live in 48 hours: an AI receptionist that answers every call, quotes the clean, books it, and follows up to turn one-time jobs into recurring clients. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more recurring clients lost to another cleaner.",
        "Faster quotes and booking, so you win the client first.",
        "Follow-up that turns one-time cleans into weekly recurring revenue."
      ]
    }
  },

  /* ------------------------------ POOL SERVICE ------------------------- */
  "pool-service": {
    name: "Pool Service",
    eyebrow: "for pool service & maintenance companies",
    heroPain: "Every missed call is a pool going to the next service company.",
    heroSub: "A pool owner wants service or a repair, your techs are on routes, the call rings out, and they book the company that answered. yourco audits where your business leaks, then builds the AI system that answers every call, books the service, and follows up on every lead.",
    probHead: "Where pool service companies quietly lose work.",
    bottlenecks: [
      { title: "Missed & seasonal-spike calls", desc: "Techs on routes can't answer, and season spikes make it worse. Calls go to voicemail — and the owner calls the next company." },
      { title: "Slow scheduling & quotes", desc: "Booking and repair quotes drag when no one's at a desk. The fastest to respond usually wins the account." },
      { title: "Follow-up & recurring plans", desc: "One-time service that could become a recurring maintenance plan slips without follow-up." }
    ],
    osPitch: "For a pool service company that means an AI front desk that answers every call and books the service, plus follow-up that turns jobs into recurring maintenance plans — coordinated as one system you don't have to run.",
    closeHead: "stop letting pools walk to the next service company.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — beat them and the account is yours", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$8.8B", l: "US pool cleaning is an $8.8B market across nearly 79,000 businesses — recurring revenue, but a fragmented, competitive field.", src: "IBISWorld, 2025", url: "https://www.ibisworld.com/united-states/market-size/swimming-pool-cleaning-services/4832/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many calls/leads do you get a month?", hint: "Season months run higher — an average is fine.", placeholder: "e.g. 100" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average job or account worth to you?", placeholder: "$250" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on phones, scheduling, and follow-up?", placeholder: "e.g. 14" },
        { k: "quote_speed", type: "select", label: "How fast does a customer get scheduled or quoted?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call", "Book service faster", "Turn jobs into recurring plans", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every account booked",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the service, and follows up to turn jobs into recurring maintenance plans. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more pools lost to the next service company.",
        "Faster scheduling through season spikes, so you win the account.",
        "Follow-up that turns one-time service into recurring maintenance revenue."
      ]
    }
  },

  /* --------------------------------- SOLAR ----------------------------- */
  solar: {
    name: "Solar",
    eyebrow: "for solar installers",
    heroPain: "Every slow lead is a homeowner signing with the installer who called first.",
    heroSub: "Solar is a speed-to-lead game — a homeowner requesting a quote goes with whoever responds first and books the consultation. Slow follow-up and the deal is gone. yourco audits where your pipeline leaks, then builds the AI system that responds instantly, qualifies the lead, books the consultation, and follows up until they sign.",
    probHead: "Where solar installers quietly lose deals.",
    bottlenecks: [
      { title: "Slow lead response", desc: "Solar leads go cold fast and they're expensive. The first installer to respond usually wins the homeowner." },
      { title: "Missed & after-hours inquiries", desc: "Homeowners research at night and inquire on impulse. An inquiry that rings out is a deal signing with a faster installer." },
      { title: "Follow-up that never happens", desc: "Solar is a considered purchase that needs many touches. Without a system, warm leads go cold and the install signs elsewhere." }
    ],
    osPitch: "For a solar installer that means an AI front desk that responds to every lead in seconds, qualifies the homeowner, books the consultation, and follows up until they sign — coordinated as one system, so you're always first to respond.",
    closeHead: "stop losing installs to the installer who called back first.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "20%", l: "of home-service pros respond to a new lead within an hour — and solar is the ultimate speed-to-lead game", src: "Jobber, 2026 Home Service Trends Report", url: "https://www.getjobber.com/home-service-trends-report/" },
      { n: "$21.6B", l: "US solar panel installation is a $21.6B market — large and growing, with installers competing hard on price and speed.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/market-size/solar-panel-installation/4494/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through slow response and dropped follow-up — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many leads/inquiries do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 120" },
        { k: "missed", type: "select", label: "What share do you miss, or not respond to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average install worth to you (your margin)?", placeholder: "$8,000" },
        { k: "admin_hours", type: "number", label: "Hours a week spent chasing leads, qualifying, and following up?", placeholder: "e.g. 16" },
        { k: "speed", type: "select", label: "How fast do you typically respond to a new lead?", options: ["Within minutes", "Within an hour", "Same day", "When I can"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Respond to every lead instantly", "Never miss an inquiry", "Follow up until they sign", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Lead Response — first to respond, every time",
        desc: "Live in 48 hours: an AI front desk that responds to every lead in seconds, qualifies the homeowner, books the consultation, and follows up until they sign. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every lead answered in seconds — you're the first installer to respond, so you win the homeowner.",
        "After-hours inquiries captured, not lost to a faster installer overnight.",
        "Relentless follow-up, so expensive leads convert instead of going cold."
      ]
    }
  },

  /* ----------------------------- ORTHODONTICS -------------------------- */
  orthodontics: {
    name: "Orthodontics",
    eyebrow: "for orthodontic practices",
    heroPain: "Every missed call is a new case starting at the practice down the street.",
    heroSub: "A parent ready to start their kid's treatment calls to book a consult — and goes with the practice that answers. Your front desk is with a patient, the call rings out, and a multi-thousand-dollar case signs elsewhere. yourco audits where your practice leaks, then builds the AI system that answers every call, books the consult, and keeps the schedule full.",
    probHead: "Where orthodontic practices quietly lose cases.",
    bottlenecks: [
      { title: "Missed new-patient calls", desc: "Front desk is chairside; the call goes to voicemail. New patients book the practice that answered." },
      { title: "No-shows & cancellations", desc: "A missed appointment is a chair you staffed for, earning nothing — and ortho no-shows and late cancels add up fast." },
      { title: "Consult follow-up gaps", desc: "Consults that don't start treatment the first visit rarely get a second touch. No system, no recovered case." }
    ],
    osPitch: "For an orthodontic practice that means an AI front desk that answers every call and books the consult, reminders that cut no-shows, and follow-up that turns consults into started cases — coordinated as one system, so your chairs stay full.",
    closeHead: "stop letting new cases start at the practice down the street.",
    stats: [
      { n: "32%", l: "Nearly a third of calls to dental practices go unanswered — most are patients trying to book.", src: "Reach, June 2025", url: "https://www.getreach.co/blog/32-of-dental-calls-go-unanswered-how-to-fix-it" },
      { n: "7.4%", l: "7.4% of orthodontic patients no-show without notice, on top of 15.5% who cancel in advance.", src: "Orthodontic Products (Planet DDS Outlook), March 2025", url: "https://orthodonticproductsonline.com/practice-management/business-development/2025-dental-industry-outlook-orthodontic-practices-see-growth-amid-economic-uncertainty/" },
      { n: "2,711", l: "There are 2,711 orthodontic practices competing for new patients across the US in 2025.", src: "IBISWorld, 2025", url: "https://www.ibisworld.com/industry-statistics/number-of-businesses/orthodontists-united-states/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed calls and no-shows — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 180" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average case worth to you?", placeholder: "$5,500" },
        { k: "admin_hours", type: "number", label: "Hours a week your front desk spends on phones, scheduling, and reminders?", placeholder: "e.g. 18" },
        { k: "no_show", type: "select", label: "What's your no-show & late-cancel situation?", options: ["Rare", "A few a week", "Several a week", "It's a real problem"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every new-patient call", "Cut no-shows & late cancels", "Turn consults into started cases", "Stop drowning in front-desk admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every consult booked",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the consult, sends reminders to cut no-shows, and follows up to start cases. You approve anything patient-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every new-patient call answered — no more cases starting down the street.",
        "Fewer no-shows and late cancels, so the chairs you staffed for earn.",
        "Consults followed up, so more turn into started cases."
      ]
    }
  },

  /* ---------------------------- PLASTIC SURGERY ------------------------ */
  "plastic-surgery": {
    name: "Plastic Surgery",
    eyebrow: "for plastic surgery & cosmetic practices",
    heroPain: "Every missed call is a high-value procedure booking with another surgeon.",
    heroSub: "A prospective patient researching an elective procedure books a consult with the practice that answers and follows up. Your team is in the OR or with a patient, the call rings out, and a five-figure procedure goes elsewhere. yourco audits where your practice leaks, then builds the AI system that answers every call, books the consult, and follows up on every lead.",
    probHead: "Where plastic surgery practices quietly lose patients.",
    bottlenecks: [
      { title: "Missed consult calls", desc: "Front desk is busy; the call goes to voicemail. High-intent patients book a consult with whoever answered." },
      { title: "Lead follow-up gaps", desc: "Elective procedures are a considered decision needing many touches. Without follow-up, the consult signs elsewhere." },
      { title: "No-shows on high-value slots", desc: "A missed consult or surgery slot is significant lost revenue — and staffed time gone." }
    ],
    osPitch: "For a plastic surgery practice that means an AI front desk that answers every call and books the consult, reminders that protect high-value slots, and follow-up that nurtures every lead to surgery — coordinated as one system you don't have to run.",
    closeHead: "stop letting high-value procedures book with another surgeon.",
    stats: [
      { n: "29%", l: "Healthcare practices miss 29% of inbound patient calls — every missed call is a high-intent patient booking elsewhere.", src: "Keona Health (citing Invoca), 2025", url: "https://www.keonahealth.com/resources/missed-calls-healthcare-call-abandonment-roi" },
      { n: "1%", l: "Cosmetic surgical procedures rose 1% and minimally invasive treatments 3% in 2024 — elective demand held through economic uncertainty.", src: "American Society of Plastic Surgeons (via PR Newswire), June 2025", url: "https://www.prnewswire.com/news-releases/interest-in-aesthetic-health-remained-consistent-despite-economic-uncertainty-in-2024-according-to-new-report-from-american-society-of-plastic-surgeons-302490893.html" },
      { n: "$21.63B", l: "The US cosmetic surgery market is valued at $21.63 billion in 2025 — a high-value elective market growing 7.4% a year.", src: "Precedence Research, April 2026", url: "https://www.precedenceresearch.com/cosmetic-surgery-market" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed consults and dropped follow-up — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls or consult inquiries do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 100" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average procedure worth to you?", placeholder: "$8,000" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on consult booking, follow-up, and reminders?", placeholder: "e.g. 16" },
        { k: "no_show", type: "select", label: "What's your consult no-show situation?", options: ["Rare", "A few a week", "Several a week", "It's a real problem"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every consult call", "Follow up every lead to surgery", "Protect high-value slots", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every consult answered, every lead nurtured",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the consult, sends reminders that protect high-value slots, and nurtures every lead toward surgery. You approve anything patient-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every consult call answered — no more high-value procedures booking elsewhere.",
        "Every lead nurtured, so more consults convert to surgery.",
        "Fewer no-shows on high-value slots, protecting staffed time."
      ]
    }
  },

  /* ------------------------------ DERMATOLOGY -------------------------- */
  dermatology: {
    name: "Dermatology",
    eyebrow: "for dermatology practices",
    heroPain: "Every missed call is a patient booking with a derm who picked up — if they can get in at all.",
    heroSub: "Dermatology demand far outstrips access — the average wait is over a month. A patient with a skin concern calls around for the soonest opening and books whoever answers. Your front desk is slammed, the call rings out, and the appointment goes elsewhere. yourco audits where your practice leaks, then builds the AI system that answers every call, books the appointment, and keeps the schedule full.",
    probHead: "Where dermatology practices quietly leak revenue.",
    bottlenecks: [
      { title: "Missed patient calls", desc: "Front desk is overwhelmed; calls go to voicemail. Patients book wherever they can get in soonest — and that means whoever answered." },
      { title: "Long waits & access friction", desc: "When booking is hard, patients give up and go elsewhere. Every abandoned call is a visit — medical or cosmetic — lost." },
      { title: "No-shows & front-desk overload", desc: "Missed appointments and a buried front desk drain both revenue and staff capacity." }
    ],
    osPitch: "For a dermatology practice that means an AI front desk that answers every call and books the appointment, reminders that cut no-shows, and overflow coverage for a slammed front desk — coordinated as one system, so the schedule stays full and your team isn't drowning in phones.",
    closeHead: "stop letting patients — medical and cosmetic — book with the derm who picked up.",
    stats: [
      { n: "42%", l: "Medical practices miss 42% of incoming calls during business hours — every missed call is a patient who may book elsewhere.", src: "AnswerNet, May 2025", url: "https://answernet.com/costs-of-missed-calls-in-medical-offices-and-how-to-avoid-them/" },
      { n: "36.5 days", l: "The average wait for a dermatology appointment is now 36.5 days — patients with skin concerns won't wait that long.", src: "AMN Healthcare, 2025", url: "https://www.amnhealthcare.com/amn-insights/physician/blog/the-growing-challenges-with-physician-appointment-wait-times/" },
      { n: "$10.0B", l: "US dermatology is a $10.0 billion market in 2025 — capturing more of every inbound call directly grows your share.", src: "IBISWorld, 2025", url: "https://www.ibisworld.com/united-states/market-size/dermatologists/4168/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed calls and booking friction — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 300" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average visit or patient worth to you?", placeholder: "$350" },
        { k: "admin_hours", type: "number", label: "Hours a week your front desk spends on phones, scheduling, and reminders?", placeholder: "e.g. 22" },
        { k: "no_show", type: "select", label: "What's your no-show situation?", options: ["Rare", "A few a week", "Several a week", "It's a real problem"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every patient call", "Make booking easier", "Cut no-shows", "Stop drowning in front-desk admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every slot filled",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books the appointment, sends reminders to cut no-shows, and covers an overwhelmed front desk. You approve anything patient-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every patient call answered — no more visits lost to the derm who picked up.",
        "Easier booking, so patients don't give up and go elsewhere.",
        "Fewer no-shows and a lighter front-desk load, so the schedule stays full."
      ]
    }
  },

  /* ----------------------------- FAMILY MEDICAL ------------------------ */
  "family-medical": {
    name: "Family Medical",
    eyebrow: "for family medical & primary care practices",
    heroPain: "Every missed call is a patient — and their whole family — going to another practice.",
    heroSub: "Your front desk is juggling a full waiting room, the phone rings out, and the patient trying to book, refill, or ask a question gives up and calls another practice. yourco audits where your practice leaks, then builds the AI system that answers every call, books the appointment, handles routine requests, and keeps the schedule full.",
    probHead: "Where primary care practices quietly leak revenue.",
    bottlenecks: [
      { title: "Missed patient calls", desc: "Front desk is checking patients in; calls go to voicemail. Patients book, or switch, to a practice that answers." },
      { title: "No-shows", desc: "A missed appointment is a slot you staffed for, earning nothing — and primary care no-shows run high." },
      { title: "Refill & routine-request overload", desc: "Refills, results, and scheduling questions bury your front desk — time not spent on patients in the room." }
    ],
    osPitch: "For a primary care practice that means an AI front desk that answers every call, books appointments, and handles routine requests like refills and scheduling, plus reminders that cut no-shows — coordinated as one system, so your team isn't drowning in phones.",
    closeHead: "stop letting patients — and their families — leave for a practice that answered.",
    stats: [
      { n: "42%", l: "The average medical practice misses 42% of incoming calls during business hours — those are patients calling competitors.", src: "AnswerNet, May 2025", url: "https://answernet.com/costs-of-missed-calls-in-medical-offices-and-how-to-avoid-them/" },
      { n: "$200", l: "Each no-show costs a primary care practice about $200 in lost revenue, with average no-show rates near 19%.", src: "Clearwave, October 2025", url: "https://www.clearwaveinc.com/blog/the-average-no-show-rate-in-primary-care-and-how-to-reduce-it/" },
      { n: "$290.9B", l: "The US primary care physician market is estimated at $290.9 billion in 2025 — a large, fragmented field of practices.", src: "Mordor Intelligence, February 2025", url: "https://www.mordorintelligence.com/industry-reports/united-states-primary-care-physician-market" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed calls and no-shows — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 350" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average visit or patient worth to you?", placeholder: "$250" },
        { k: "admin_hours", type: "number", label: "Hours a week your front desk spends on phones, refills, and scheduling?", placeholder: "e.g. 25" },
        { k: "no_show", type: "select", label: "What's your no-show situation?", options: ["Rare", "A few a week", "Several a week", "It's a real problem"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every patient call", "Cut no-shows", "Tame refill & routine requests", "Stop drowning in front-desk admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, routine requests handled",
        desc: "Live in 48 hours: an AI receptionist that answers every call, books appointments, handles routine requests like refills and scheduling, and sends reminders to cut no-shows. You approve anything patient-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every patient call answered — no more families leaving for a practice that answered.",
        "Fewer no-shows, so the slots you staffed for earn.",
        "Routine requests handled, freeing your front desk for patients in the room."
      ]
    }
  },

  /* ----------------------------- PEPTIDE CLINICS ----------------------- */
  "peptide-clinics": {
    name: "Peptide Clinics",
    eyebrow: "for peptide & longevity clinics",
    heroPain: "Every missed call is a cash-pay patient booking with another clinic.",
    heroSub: "Demand for peptide therapy and longevity medicine is surging — but a prospective cash-pay patient books with the clinic that answers and follows up. Your team is with a patient, the call rings out, and a high-value program signs elsewhere. yourco audits where your clinic leaks, then builds the AI system that answers every call, runs intake, and follows up on every lead.",
    probHead: "Where peptide & longevity clinics leak booming demand.",
    bottlenecks: [
      { title: "Missed patient calls", desc: "Front desk is busy; calls go to voicemail. Cash-pay patients book with whoever answered." },
      { title: "Slow intake", desc: "Longevity and peptide intake is involved. The slower it moves, the colder the lead — and the more your team drowns in admin." },
      { title: "Lead follow-up gaps", desc: "High-value programs are a considered purchase needing many touches. Without follow-up, the program signs elsewhere." }
    ],
    osPitch: "For a peptide or longevity clinic that means an AI front desk that answers every call, runs intake, and follows up on every lead — coordinated as one system, so surging demand actually lands on your calendar.",
    closeHead: "stop letting cash-pay patients book with another clinic.",
    stats: [
      { n: "29%", l: "Healthcare practices miss 29% of inbound patient calls — every missed call is a cash-pay patient booking elsewhere.", src: "Keona Health (citing Invoca), 2025", url: "https://www.keonahealth.com/resources/missed-calls-healthcare-call-abandonment-roi" },
      { n: "$6.02B", l: "The longevity clinic market jumps from $5.35B (2025) to $6.02B in 2026 — demand is surging, capacity is the constraint.", src: "Research and Markets, 2026", url: "https://www.researchandmarkets.com/reports/6225936/longevity-clinic-market-report" },
      { n: "$21.24B", l: "The US peptide therapeutics market hit $21.24B in 2025 — a fast-growing cash-pay wellness category.", src: "Precedence Research, 2025", url: "https://www.precedenceresearch.com/peptide-therapeutics-market" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed calls and slow intake — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls or inquiries do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 80" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average patient or program worth to you?", placeholder: "$1,500" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on intake, scheduling, and follow-up?", placeholder: "e.g. 16" },
        { k: "onboarding", type: "select", label: "How fast does a new patient get onboarded once they say yes?", options: ["Same week", "1–2 weeks", "3+ weeks", "When we get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call", "Speed up intake", "Follow up on every lead", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every lead worked",
        desc: "Live in 48 hours: an AI front desk that answers every call, runs patient intake, and follows up on every lead. You approve anything patient-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more cash-pay patients booking with another clinic.",
        "Faster intake, so leads don't cool and staff stop drowning in admin.",
        "Relentless follow-up, so surging demand converts to booked programs."
      ]
    }
  },

  /* ---------------------------- WELLNESS CLINICS ----------------------- */
  "wellness-clinics": {
    name: "Wellness Clinics",
    eyebrow: "for wellness & longevity clinics",
    heroPain: "Every missed call is a cash-pay patient taking their membership elsewhere.",
    heroSub: "Demand for functional and longevity medicine is booming — but a prospective patient books with the clinic that answers and follows up. Your team is with a patient, the call rings out, and a high-value membership signs elsewhere. yourco audits where your clinic leaks, then builds the AI system that answers every call, runs intake, and follows up on every lead.",
    probHead: "Where wellness clinics leak booming demand.",
    bottlenecks: [
      { title: "Missed patient calls", desc: "Front desk is busy; calls go to voicemail. Cash-pay patients book with whoever answered." },
      { title: "Slow intake & membership onboarding", desc: "Functional-medicine intake is involved. The slower it moves, the colder the lead and the more your team drowns in admin." },
      { title: "Lead follow-up gaps", desc: "Memberships and programs are a considered purchase needing many touches. Without follow-up, the patient signs elsewhere." }
    ],
    osPitch: "For a wellness or longevity clinic that means an AI front desk that answers every call, runs intake, and follows up on every lead and membership inquiry — coordinated as one system, so booming demand actually lands on your calendar.",
    closeHead: "stop letting cash-pay patients take their membership elsewhere.",
    stats: [
      { n: "41%", l: "41% of patients have switched providers partly because they couldn't reach their old practice by phone.", src: "Press Ganey 2025 (via AgentZap), May 2026", url: "https://agentzap.ai/blog/medical-practice-phone-statistics" },
      { n: "24.9%", l: "The complementary & alternative medicine market is growing 24.9% a year — demand for your approach is surging.", src: "Market.us, March 2025", url: "https://market.us/report/alternative-and-complementary-medicine-market/" },
      { n: "$2T", l: "The US wellness economy is now $2 trillion — the largest in the world, at roughly $6,000 spent per person yearly.", src: "Global Wellness Institute, March 2025", url: "https://globalwellnessinstitute.org/press-room/press-releases/gow-us-econ-valued-at-2trillion/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed calls and slow intake — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls or inquiries do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 90" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average patient or membership worth to you?", placeholder: "$1,500" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on intake, scheduling, and follow-up?", placeholder: "e.g. 16" },
        { k: "onboarding", type: "select", label: "How fast does a new patient get onboarded once they say yes?", options: ["Same week", "1–2 weeks", "3+ weeks", "When we get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call", "Speed up intake", "Follow up on every lead", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every lead worked",
        desc: "Live in 48 hours: an AI front desk that answers every call, runs intake, and follows up on every lead and membership inquiry. You approve anything patient-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more cash-pay patients taking their membership elsewhere.",
        "Faster intake, so leads don't cool and staff stop drowning in admin.",
        "Relentless follow-up, so booming demand converts to booked memberships."
      ]
    }
  },

  /* ------------------------------- IV THERAPY -------------------------- */
  "iv-therapy": {
    name: "IV Therapy",
    eyebrow: "for IV therapy & hydration businesses",
    heroPain: "Every missed call is a booking going to the next IV bar.",
    heroSub: "A client who wants a drip books with whoever answers and gets them on the schedule fast. Your team is with a client or on a mobile run, the call rings out, and the booking goes elsewhere. yourco audits where your business leaks, then builds the AI system that answers every call, books the appointment, and dispatches mobile visits.",
    probHead: "Where IV therapy businesses leak bookings.",
    bottlenecks: [
      { title: "Missed booking calls", desc: "Staff is starting a drip or driving to a mobile visit; the call goes to voicemail — and the client books the next IV bar." },
      { title: "Slow scheduling & mobile dispatch", desc: "Booking and mobile dispatch drag when no one's free to pick up. The fastest to respond wins the client." },
      { title: "Follow-up & membership gaps", desc: "One-time drips that could become memberships slip without follow-up — recurring revenue left on the table." }
    ],
    osPitch: "For an IV therapy business that means an AI front desk that answers every call, books the appointment, dispatches mobile visits, and follows up to turn drips into memberships — coordinated as one system you don't have to run.",
    closeHead: "stop letting bookings drip away to the next IV bar.",
    stats: [
      { n: "26%", l: "of phone calls to local businesses go unanswered — 1 in 4 callers never reaches anyone", src: "Invoca, Dec 2025", url: "https://www.prnewswire.com/news-releases/new-invoca-study-finds-pricing-request-phone-calls-from-googles-ai-surged-over-300-in-november-302637352.html" },
      { n: "8.9%", l: "IV hydration therapy demand is climbing fast — on track to reach $4.6B by 2030 at 8.9% a year.", src: "Mordor Intelligence, August 2025", url: "https://www.mordorintelligence.com/industry-reports/iv-hydration-therapy-market" },
      { n: "$2.43B", l: "The US IV hydration market is projected to more than double from $1.11B (2024) to $2.43B by 2034.", src: "Precedence Research, August 2025", url: "https://www.precedenceresearch.com/intravenous-hydration-therapy-market" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls or booking inquiries do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 120" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average visit or client worth to you?", placeholder: "$150" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on booking, dispatch, and follow-up?", placeholder: "e.g. 14" },
        { k: "booking", type: "select", label: "How do most clients try to book?", options: ["They call", "Online or DM", "Walk-in", "A mix"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call", "Book & dispatch faster", "Turn drips into memberships", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every visit booked",
        desc: "Live in 48 hours: an AI front desk that answers every call, books the appointment, dispatches mobile visits, and follows up to turn drips into memberships. You approve anything client-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more bookings lost to the next IV bar.",
        "Faster scheduling and mobile dispatch, so you win the client.",
        "Follow-up that turns one-time drips into recurring memberships."
      ]
    }
  },

  /* -------------------------- HORMONE / TRT CLINICS ------------------- */
  "hormone-trt": {
    name: "Hormone / TRT Clinics",
    eyebrow: "for hormone & TRT clinics",
    heroPain: "Every missed call is a cash-pay patient starting treatment somewhere else.",
    heroSub: "Demand for hormone and testosterone therapy is surging — and a prospective patient starts with the clinic that answers and makes intake easy. Your team is with a patient, the call rings out, and a recurring cash-pay program signs elsewhere. yourco audits where your clinic leaks, then builds the AI system that answers every call, runs intake, and follows up on every lead.",
    probHead: "Where hormone & TRT clinics leak surging demand.",
    bottlenecks: [
      { title: "Missed patient calls", desc: "Front desk is busy; calls go to voicemail. Cash-pay patients start with whoever answered." },
      { title: "Slow intake", desc: "Hormone-therapy intake — labs, history — is involved. The slower it moves, the colder the lead." },
      { title: "Refill & follow-up overload", desc: "Refill requests and warm leads bury your front desk and slip without a system — recurring revenue at risk." }
    ],
    osPitch: "For a hormone or TRT clinic that means an AI front desk that answers every call, runs intake, handles refill requests, and follows up on every lead — coordinated as one system, so surging demand lands on your calendar.",
    closeHead: "stop letting cash-pay patients start treatment somewhere else.",
    stats: [
      { n: "82%", l: "82% of patients give a provider just 1 or 2 tries before switching — every missed call is a lost patient.", src: "Tebra (The Intake), October 2025", url: "https://www.tebra.com/theintake/patient-experience/tips-and-trends/patient-survey-questions-preferences-habits" },
      { n: "11M", l: "US testosterone therapy prescriptions hit 11 million in 2024 — demand for your clinic is surging.", src: "We Will Cure, August 2025", url: "https://wewillcure.com/insights/therapeutics/care-delivery/startups-disrupt-testosterone-therapy-market-as-younger-men-fuel-demand" },
      { n: "$356.3M", l: "The US testosterone replacement therapy market reached $356.3M in 2025 and keeps climbing.", src: "Custom Market Insights, May 2026", url: "https://www.custommarketinsights.com/report/us-testosterone-replacement-therapy-market/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed calls and slow intake — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls or inquiries do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 100" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average patient or program worth to you?", placeholder: "$1,200" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on intake, refills, and follow-up?", placeholder: "e.g. 16" },
        { k: "onboarding", type: "select", label: "How fast does a new patient get onboarded once they say yes?", options: ["Same week", "1–2 weeks", "3+ weeks", "When we get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call", "Speed up intake", "Handle refill requests", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every lead worked",
        desc: "Live in 48 hours: an AI front desk that answers every call, runs intake, handles refill requests, and follows up on every lead. You approve anything patient-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more cash-pay patients starting treatment elsewhere.",
        "Faster intake, so leads don't cool while they wait.",
        "Refills handled and leads followed up, so recurring revenue holds."
      ]
    }
  },

  /* ------------------------- RECOVERY & COLD PLUNGE -------------------- */
  "recovery-cold-plunge": {
    name: "Recovery & Cold Plunge",
    eyebrow: "for recovery, cold plunge & cryotherapy studios",
    heroPain: "Every missed call is a membership going to the next recovery studio.",
    heroSub: "Recovery — cold plunge, sauna, cryo — is booming, and a prospective member books with the studio that answers and makes it easy. Your team is running sessions, the call rings out, and the membership signs elsewhere. yourco audits where your studio leaks, then builds the AI system that answers every call, books the session, and follows up on every lead.",
    probHead: "Where recovery studios leak booming demand.",
    bottlenecks: [
      { title: "Missed booking calls", desc: "Staff is running a session or a mobile setup; the call goes to voicemail — and the prospect books the next studio." },
      { title: "Slow booking & membership sign-up", desc: "Bookings and membership questions drag when no one's free to pick up. The fastest to respond wins the member." },
      { title: "Follow-up gaps", desc: "Drop-in clients who could become members slip without follow-up — recurring revenue left on the table." }
    ],
    osPitch: "For a recovery studio that means an AI front desk that answers every call, books the session, and follows up to turn drop-ins into members — coordinated as one system you don't have to run.",
    closeHead: "stop letting memberships walk to the next recovery studio.",
    stats: [
      { n: "62%", l: "62% of callers who can't reach a business immediately call a competitor instead — every missed call is a lost booking.", src: "Aira (citing Dialzara), March 2026", url: "https://www.getaira.io/blog/missed-business-calls-statistics" },
      { n: "$0.87B", l: "The global cold plunge tub market hit $0.87B in 2025 and is growing 8.3% a year through 2035 — demand is surging.", src: "Future Market Insights, May 2025", url: "https://www.futuremarketinsights.com/reports/cold-plunge-tub-market" },
      { n: "10.6%", l: "The cryotherapy market reached $6.1B in 2025 and is forecast to grow 10.6% a year — recovery demand is climbing.", src: "Future Market Insights, April 2026", url: "https://www.futuremarketinsights.com/reports/cryotherapy-market" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls or booking inquiries do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 100" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average member or client worth to you?", placeholder: "$150" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on booking, sign-ups, and follow-up?", placeholder: "e.g. 12" },
        { k: "booking", type: "select", label: "How do most clients try to book?", options: ["They call", "Online or DM", "Walk-in", "A mix"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call", "Book & sign up faster", "Turn drop-ins into members", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every session booked",
        desc: "Live in 48 hours: an AI front desk that answers every call, books the session, and follows up to turn drop-ins into members. You approve anything client-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more memberships lost to the next studio.",
        "Faster booking and sign-up, so you win the member.",
        "Follow-up that turns drop-ins into recurring memberships."
      ]
    }
  },

  /* --------------------------- MOVING & STORAGE ------------------------ */
  "moving-storage": {
    name: "Moving & Storage",
    eyebrow: "for moving & storage companies",
    heroPain: "Whoever quotes first usually wins the move — and your phone is going to voicemail.",
    heroSub: "A family planning a move calls several companies for quotes and books the one that answers and quotes fast. Your crews are on a job, the call rings out, and the move books elsewhere. yourco audits where your business leaks, then builds the AI system that answers every call, quotes fast, and follows up on every lead.",
    probHead: "Where moving companies lose jobs.",
    bottlenecks: [
      { title: "Missed quote calls", desc: "Crews are loading a truck; the call goes to voicemail — and the customer books the mover who answered." },
      { title: "Slow quotes & seasonal spikes", desc: "Summer demand overwhelms the phones. The fastest quote usually wins the move — and you're rarely fastest." },
      { title: "Follow-up that never happens", desc: "Quotes sent, then silence. No system to follow up while you're on a job, so the move signs elsewhere." }
    ],
    osPitch: "For a moving company that means an AI front desk that answers every call (peak season included), quotes fast, and follows up on every lead — coordinated as one system you don't have to run.",
    closeHead: "stop letting moves book with the company that quoted first.",
    stats: [
      { n: "78%", l: "78% of buyers go with the first company that responds — in moving, whoever quotes first usually wins the job.", src: "LeadAngel, March 2025", url: "https://www.leadangel.com/blog/operations/speed-to-lead-statistics/" },
      { n: "41%", l: "41% of all US moves happen May through August — your phones spike, and missed quotes go straight to a competitor.", src: "moveBuddha, August 2025", url: "https://www.movebuddha.com/blog/moving-industry-statistics/" },
      { n: "$25.7B", l: "The US moving services market is $25.7B across 9,430 companies in 2026 — you're competing on speed, not just price.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/industry/moving-services/1154/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many quote calls/leads do you get a month?", hint: "Peak season runs higher — an average is fine.", placeholder: "e.g. 150" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average move worth to you?", placeholder: "$2,500" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on quotes, scheduling, and follow-up?", placeholder: "e.g. 16" },
        { k: "quote_speed", type: "select", label: "How fast does a typical quote go out?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call", "Quote faster", "Follow up on every lead", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered, every quote followed up",
        desc: "Live in 48 hours: an AI front desk that answers every call (peak season included), quotes fast, and follows up on every lead. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered — no more moves lost to the company that quoted first.",
        "Faster quotes through peak season, so you win the job.",
        "Automatic follow-up on every lead, so fewer moves walk to the competition."
      ]
    }
  },

  /* ------------------------- COMMERCIAL CLEANING ---------------------- */
  "commercial-cleaning": {
    name: "Commercial Cleaning",
    eyebrow: "for commercial cleaning & janitorial companies",
    heroPain: "Every missed call is a contract going to the cleaner who answered first.",
    heroSub: "A facility manager shopping for a cleaning vendor calls around for bids — and the company that responds first usually wins the contract. Your crews are on site, the call rings out, and a recurring contract signs elsewhere. yourco audits where your business leaks, then builds the AI system that answers every call, books the walkthrough, and follows up on every bid.",
    probHead: "Where commercial cleaning companies lose contracts.",
    bottlenecks: [
      { title: "Missed bid calls", desc: "Crews are cleaning, not answering. Bid inquiries go to voicemail — and the facility manager calls the next company." },
      { title: "Slow bid & walkthrough scheduling", desc: "Bids and site walkthroughs drag when no one's free to pick up. The fastest to respond usually wins the contract." },
      { title: "Follow-up that never happens", desc: "Bids go quiet. Without follow-up, the recurring contract signs with whoever stayed in touch." }
    ],
    osPitch: "For a commercial cleaning company that means an AI front desk that answers every call, books the walkthrough, and follows up on every bid — coordinated as one system you don't have to run.",
    closeHead: "stop letting contracts go to the cleaner who answered first.",
    stats: [
      { n: "78%", l: "78% of buyers hire the company that responds to their inquiry first — speed wins the contract.", src: "Vendasta, August 2025", url: "https://www.vendasta.com/blog/lead-response-time/" },
      { n: "31%", l: "31% of cleaning businesses name competition a top concern, while 58% report rising customer demand.", src: "Jobber, June 2026", url: "https://www.getjobber.com/academy/cleaning/cleaning-industry-trends/" },
      { n: "$81.9B", l: "The US janitorial services market hit $81.9 billion in 2025 — a large, contract-driven opportunity.", src: "Grand View Research, 2025", url: "https://www.grandviewresearch.com/industry-analysis/us-janitorial-services-market-report" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many bid calls/leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 80" },
        { k: "missed", type: "select", label: "What share do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average contract worth to you (monthly)?", placeholder: "$2,000" },
        { k: "admin_hours", type: "number", label: "Hours a week spent on bids, walkthroughs, and follow-up?", placeholder: "e.g. 14" },
        { k: "quote_speed", type: "select", label: "How fast does a typical bid go out?", options: ["Same day", "1–2 days", "3+ days", "When I get to it"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call", "Book walkthroughs faster", "Follow up on every bid", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every bid call answered, every bid followed up",
        desc: "Live in 48 hours: an AI front desk that answers every call, books the walkthrough, and follows up on every bid. You approve anything customer-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every bid call answered — no more contracts lost to the cleaner who answered first.",
        "Faster walkthroughs, so you're first to respond and win the contract.",
        "Automatic follow-up on every bid, so fewer recurring contracts walk away."
      ]
    }
  },

  /* ----------------------------- BOUTIQUE HOTELS ---------------------- */
  "boutique-hotels": {
    name: "Boutique Hotels",
    eyebrow: "for boutique & independent hotels",
    heroPain: "Every missed call is a direct booking lost — or handed to an OTA that skims your margin.",
    heroSub: "A guest who calls to book direct, or an after-hours reservation inquiry, goes to voicemail — and rebooks through an OTA that takes 15-25%, or with another property. yourco audits where your hotel leaks, then builds the AI system that answers every call 24/7, captures the direct booking, and handles event and reservation inquiries.",
    probHead: "Where boutique hotels leak bookings and margin.",
    bottlenecks: [
      { title: "Missed & after-hours reservation calls", desc: "Front desk is helping a guest or it's the middle of the night; the call rings out — and the booking goes to an OTA or another property." },
      { title: "Lost direct bookings", desc: "Every booking pushed to an OTA costs you 15-25%. A captured direct call is full margin." },
      { title: "Event & inquiry follow-up gaps", desc: "Wedding and event inquiries that don't get a fast response book elsewhere." }
    ],
    osPitch: "For a boutique hotel that means an AI front desk that answers every call 24/7, captures direct bookings, and handles reservation and event inquiries — coordinated as one system, so you keep the margin OTAs would skim.",
    closeHead: "stop letting direct bookings — and your margin — slip to the OTAs.",
    stats: [
      { n: "31%", l: "After-hours calls make up 31% of reservation inquiries — every one rings while your front desk is dark.", src: "AgentZap, March 2026", url: "https://agentzap.ai/blog/hospitality-industry-phone-statistics-15-numbers-every-hotel-owner-should-know-in-2026" },
      { n: "15–25%", l: "OTAs like Expedia and Booking.com take 15-25% per stay; a direct booking on your own site costs you 0%.", src: "Prostay, August 2025", url: "https://www.prostay.com/blog/hotel-booking-statistics-2025-market-insights-and-trends/" },
      { n: "$36.5B", l: "US boutique hotels are a $36.5 billion industry across 6,092 properties — independents competing on experience, not scale.", src: "IBISWorld, September 2025", url: "https://www.ibisworld.com/united-states/industry/boutique-hotels/5464/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed calls and OTA leakage — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound reservation calls/inquiries do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 200" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not get back to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average direct booking worth to you?", placeholder: "$600" },
        { k: "admin_hours", type: "number", label: "Hours a week your front desk spends on phones, reservations, and inquiries?", placeholder: "e.g. 18" },
        { k: "after_hours", type: "select", label: "What happens to an after-hours reservation call?", options: ["We have a true 24/7 answer", "Voicemail", "An answering service takes a message", "It rings out"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Answer every call 24/7", "Capture direct bookings", "Follow up on event inquiries", "Stop drowning in admin"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every call answered 24/7, every direct booking captured",
        desc: "Live in 48 hours: an AI front desk that answers every call around the clock, captures direct bookings, and handles reservation and event inquiries. You approve anything guest-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every reservation call answered, day or night — no more bookings lost to an OTA or another property.",
        "More direct bookings captured, so you keep the margin OTAs would skim.",
        "Event and wedding inquiries followed up, so fewer book elsewhere."
      ]
    }
  },

  /* ----------------------------- SPORTS & FITNESS --------------------- */
  "sports-fitness": {
    name: "Sports & Fitness",
    eyebrow: "for gyms, studios & fitness facilities",
    heroPain: "Every missed call is a membership joining the studio that called back first.",
    heroSub: "A prospect ready to join calls or messages, your team is running a class or on the floor, the inquiry goes cold, and they join the studio that responded first. yourco audits where your facility leaks, then builds the AI system that answers every call, books the tour, and follows up until they join.",
    probHead: "Where gyms & studios leak memberships.",
    bottlenecks: [
      { title: "Missed membership calls", desc: "Staff is coaching or on the floor; calls and DMs go unanswered — and the prospect joins whoever responded first." },
      { title: "Slow lead follow-up", desc: "Membership leads need fast, persistent follow-up. Without a system, warm prospects go cold." },
      { title: "Tour no-shows & member churn", desc: "No-shows on tours and members who drift away both leak revenue without reminders and re-engagement." }
    ],
    osPitch: "For a gym or studio that means an AI front desk that answers every call, books the tour, follows up until they join, and re-engages members at risk of churning — coordinated as one system you don't have to run.",
    closeHead: "stop letting memberships join the studio that answered first.",
    stats: [
      { n: "78%", l: "78% of buyers go with whoever responds first — in fitness, the studio that calls back first wins the membership.", src: "Vendasta, August 2025", url: "https://www.vendasta.com/blog/lead-response-time/" },
      { n: "66.4%", l: "The average health club retained just 66.4% of members in 2024 — about a third walk away each year.", src: "Health & Fitness Association, September 2025", url: "https://www.healthandfitness.org/2025-fitness-industry-benchmarking-report/" },
      { n: "77M", l: "US gyms and studios served a record 77 million members in 2024 — the demand is there to capture.", src: "Health & Fitness Association, October 2025", url: "https://www.healthandfitness.org/how-77-million-fitness-members-work-out-new-hfa-data-reveals-shifting-equipment-training-and-membership-trends/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through slow response and churn — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many membership calls/leads do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 120" },
        { k: "missed", type: "select", label: "What share do you miss, or not respond to fast enough?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average member worth to you (annual or lifetime)?", placeholder: "$800" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on lead follow-up, tours, and reminders?", placeholder: "e.g. 16" },
        { k: "speed", type: "select", label: "How fast do you respond to a new membership lead?", options: ["Within minutes", "Within an hour", "Same day", "When I can"] },
        { k: "top_pain", type: "select", label: "If you could fix ONE thing tomorrow, which would it be?", options: ["Respond to every lead fast", "Book more tours", "Follow up until they join", "Reduce member churn"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every lead answered, every tour booked",
        desc: "Live in 48 hours: an AI front desk that answers every call, books the tour, follows up until they join, and re-engages members at risk of churning. You approve anything member-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every membership lead answered fast — no more prospects joining the studio that responded first.",
        "More tours booked and followed up, so more leads convert to members.",
        "At-risk members re-engaged, so fewer churn out."
      ]
    }
  },

  /* ------------------------------ FUNERAL HOMES ----------------------- */
  "funeral-homes": {
    name: "Funeral Homes",
    eyebrow: "for funeral homes",
    heroPain: "When a family loses someone, they call the funeral home that answers — at any hour.",
    heroSub: "Most families reach out the moment they need help, often in the middle of the night. A call that goes to voicemail sends a grieving family to another funeral home. yourco audits where your firm leaks, then builds the AI system that answers every call with care, 24/7, takes the arrangement details, and follows up on every pre-need inquiry.",
    probHead: "Where funeral homes lose families who need them.",
    bottlenecks: [
      { title: "Missed after-hours calls", desc: "Loss doesn't keep business hours. Nearly 40% of calls come after hours — and a family in crisis won't leave a voicemail." },
      { title: "Arrangement intake under pressure", desc: "When you're with one family, the next call still needs a calm, careful answer. Voicemail isn't that." },
      { title: "Pre-need follow-up gaps", desc: "Pre-need inquiries that aren't followed up quietly go elsewhere — future arrangements lost." }
    ],
    osPitch: "For a funeral home that means an AI front desk that answers every call with care, 24/7, captures the details a grieving family shares, and follows up on every pre-need inquiry — coordinated as one system, so no family who needs you reaches a voicemail.",
    closeHead: "be the funeral home that answers when a family needs you most.",
    stats: [
      { n: "40%", l: "Nearly 40% of death notifications reach a funeral home outside standard business hours, when families most need an answer.", src: "NextPhone, May 2026", url: "https://www.getnextphone.com/blog/funeral-home-answering-service" },
      { n: "63.4%", l: "The US cremation rate is projected to reach 63.4% in 2025, reshaping how families plan their goodbyes.", src: "NFDA via PRWeb, September 2025", url: "https://www.prweb.com/releases/americans-choosing-cremation-at-historic-rates-nfda-report-finds-302556357.html" },
      { n: "$23.9B", l: "US funeral services is a $23.9 billion field, where each family's first call truly matters.", src: "IBISWorld, 2026", url: "https://www.ibisworld.com/united-states/market-size/funeral-homes/1726/" }
    ],
    quickAudit: {
      intro: "Six quick questions. On your own numbers, we'll show you roughly what's leaking — through missed after-hours calls — and what an AI system could recover. About two minutes.",
      questions: [
        { k: "leads", type: "number", label: "Roughly how many inbound calls do you get a month?", hint: "A rough number is fine.", placeholder: "e.g. 40" },
        { k: "missed", type: "select", label: "What share of those do you miss, or not answer in person?", options: ["Under 10%", "10–25%", "25–50%", "More than half"], pct: [0.07, 0.17, 0.37, 0.6] },
        { k: "job_value", type: "number", label: "What's an average service worth to you?", placeholder: "$7,000" },
        { k: "admin_hours", type: "number", label: "Hours a week your team spends on calls, intake, and pre-need follow-up?", placeholder: "e.g. 16" },
        { k: "after_hours", type: "select", label: "What happens to a call that comes in after hours?", options: ["A person always answers", "Voicemail", "An answering service takes a message", "It rings out"] },
        { k: "top_pain", type: "select", label: "If you could improve ONE thing, which would it be?", options: ["Answer every call, 24/7", "Handle arrangements with care", "Follow up on pre-need", "Ease the admin load"] }
      ]
    },
    report: {
      firstBuild: { name: "AI Front Desk — every family's call answered with care, 24/7",
        desc: "Live in 48 hours: an AI front desk that answers every call with care around the clock, captures the details a grieving family shares, and follows up on pre-need inquiries. You approve anything family-facing; yourco builds it, runs it, and keeps it reliable." },
      outcomes: [
        "Every call answered with care, day or night — no family who needs you reaches a voicemail.",
        "Arrangement details captured calmly, even when your team is with another family.",
        "Pre-need inquiries followed up, so future arrangements aren't lost."
      ]
    }
  }

};
