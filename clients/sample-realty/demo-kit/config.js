/* ============================================================================
   CLIENT DEMO KIT — the ONLY file you edit per client.
   Fill this in, open index.html, and you have a branded walkthrough to show a
   prospect what their digital employee would do — before they sign anything.
   Everything below is SAMPLE data (currently Sample Client, the reference example).
   ========================================================================== */
window.DEMO = {
  client: "Sample Client",                 // client / company name
  brand: "#2c5f2d",                       // their brand color (header + accents)
  employee: "your digital employee",      // the employee's name once chosen, or leave generic
  useCase: "Installation Proposal Automation",
  tagline: "When an Installation proposal signs in Aspire, your employee runs the early-stage coordination — and you approve anything customer-facing from your phone. Here's the whole thing, on a sample job.",

  // The walkthrough hub (index.html). flow:true = a non-clickable "what happens" step.
  steps: [
    { n: 1, flow: true, title: "A proposal signs in Aspire",
      desc: "Your employee reads it, applies your tiers, sorts materials, spots subs — and drafts everything. Nothing sends yet." },
    { n: 2, href: "approval.html", title: "Charlene approves the deposit",
      desc: "The client email + text, with the amount locked by code. One tap to send." },
    { n: 3, href: "board.html", title: "Watch every job from one board",
      desc: "Deposit, suppliers, subs — where each job stands, plus a daily nudge list of anything stuck." },
    { n: 4, href: "report.html", title: "A monthly report of what it did",
      desc: "Volume, outcomes, hours saved — and the reliability behind it." },
  ],

  // The one-tap approval screen (approval.html).
  approval: {
    approver: "Charlene",
    intro: "one message is ready for your okay",
    items: [
      { kind: "Client deposit", to: "Robert & Amanda Chen",
        sub: "Backyard paver patio + seating wall",
        locked: "$16,975.00", lockedSub: "35% of $48,500.00 · computed by code",
        email: "Subject: Deposit Request — Your Backyard Patio Project\n\nHi Robert and Amanda,\n\nThank you for choosing Sample Client for your backyard paver patio, seating wall, and landscape lighting project.\n\nTo reserve your spot on our schedule, we're requesting your deposit of $16,975.00, which represents 35% of the $48,500.00 project total.\n\nYou can pay by Zelle, check, or card.\n\nWarm regards,\nSouthern Cut",
        sms: "Hi Robert & Amanda! Your Sample Client deposit of $16,975.00 is ready, and a detailed email is on its way. Thanks so much!",
        together: "Sends as email and text together, from your own number." },
    ],
  },

  // The live status board (board.html).
  board: {
    title: "jobs in flight",
    metrics: [
      { v: "4", l: "jobs in flight" },
      { v: "1", l: "greenlit this week", accent: true },
      { v: "11", l: "messages you approved" },
      { v: "~9", l: "hrs of coordination saved this week", accent: true },
    ],
    nudges: [
      "<b>Volt Lighting</b> (Chen patio) — order sent 2 days ago, no reply. Auto-follow-up drafted, waiting for your okay.",
      "<b>Chen deposit</b> — requested 3 days ago, not yet received. Reminder draft ready.",
    ],
    jobs: [
      { name: "Robert & Amanda Chen", project: "Backyard paver patio + seating wall", total: "$48,500", badge: "in progress", badgeClass: "run",
        gates: [
          { label: "Deposit", state: "pend", text: "Requested — awaiting payment" },
          { label: "Suppliers", state: "pend", text: "1 of 2 confirmed" },
          { label: "Subcontractors", state: "wait", text: "Notice approved, awaiting reply" }],
        next: "chase Volt Lighting + the Chen deposit (drafts waiting on you)." },
      { name: "Brennan Residence", project: "Outdoor kitchen + fire feature", total: "$96,400", badge: "in progress", badgeClass: "run",
        gates: [
          { label: "Deposit", state: "done", text: "Received" },
          { label: "Suppliers", state: "done", text: "3 of 3 confirmed" },
          { label: "Subcontractors", state: "pend", text: "Mason confirming dates" }],
        next: "one sub left to confirm, then it greenlights automatically." },
      { name: "Whitfield Residence", project: "Driveway + front walkway", total: "$31,200", badge: "greenlit ✓", badgeClass: "go", greenlit: true,
        gates: [
          { label: "Deposit", state: "done", text: "Received" },
          { label: "Suppliers", state: "done", text: "2 of 2 confirmed" },
          { label: "Subcontractors", state: "done", text: "1 of 1 confirmed" }],
        next: "All systems go. Cleared 2 days ago — crew starts Jul 14." },
    ],
  },

  // The monthly outcome report (report.html).
  report: {
    period: "June",
    stats: [
      { v: "23", l: "signed installation proposals handled" },
      { v: "$418K", l: "in deposits requested, on time" },
      { v: "61", l: "supplier + sub orders drafted" },
      { v: "19", l: "jobs greenlit" },
      { v: "~3.5 hrs", l: "avg from signed → first client contact (was ~2 days)" },
      { v: "~31", l: "hours of coordination saved this month", accent: true },
    ],
    did: [
      "Deposit requests sent the same hour a proposal signed — every payment tier applied correctly.",
      "Material orders routed to shop vs job site and sent, with delivery dates tracked.",
      "Subs notified with scope + windows; chased the ones that went quiet until they confirmed.",
      "Flagged deposits and replies that were sitting too long, before they became a problem.",
    ],
    reliability: [
      { v: "0", l: "messages sent without your approval" },
      { v: "100%", l: "of dollar figures computed by tested code" },
      { v: "99.9%", l: "uptime · 0 missed signed proposals" },
    ],
    reliabilityLine: "Every send this month was approved by a human. The eval suite re-ran before each change shipped, and a duplicate deposit was caught and blocked once. Nothing reached a customer that you didn't see first.",
  },
};
