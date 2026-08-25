/* os-blueprint.js — the ONE source for "the OS we'd build for <business>".
 *
 * Both the configurator (build-your-os.html) and the shareable blueprint (blueprint.html) render
 * from this file. It exists because the alternative — the same taxonomy pasted into two pages —
 * is the exact failure this repo has a rule against: a fact changed in one place and left stale in
 * the other. There is no second copy of BIZ or FLOWS anywhere.
 *
 * Illustrative by construction. This is a sketch of how modules coordinate, never a quote; which
 * modules a business actually gets, and in what order, is decided in the audit.
 */
(function (root) {
  'use strict';

const BIZ = {
  landscaping:{label:"Landscaping / hardscaping",icon:"🌳",
    mods:[
      {p:"Intake",n:"Front Desk",d:"Answers every call/text, qualifies the job, books the estimate — 24/7.",start:true},
      {p:"Sales",n:"Estimate Follow-up",d:"Chases sent estimates until they're signed or declined."},
      {p:"Operations",n:"Scheduler + Weather Rescheduler",d:"Books crews, reshuffles rained-out jobs, notifies clients."},
      {p:"Marketing",n:"Review Engine",d:"Asks happy clients for reviews at the right moment."},
      {p:"Back Office",n:"Deposit + Invoice",d:"Drafts deposit requests and invoices off signed work (approval-gated)."},
      {p:"Company Brain",n:"Crew Knowledge",d:"Every SOP, spec, and supplier answer, instantly searchable."}
    ],
    demo:{title:"Front Desk",sub:"a missed call, handled",lines:[
      {who:"Caller",txt:"Hi, looking for a quote on a paver patio — but no one picked up."},
      {who:"OS",ai:1,txt:"This is Sample Client — sorry we missed you! I can help right now. Roughly how big is the patio, and what's your zip?"},
      {who:"Caller",txt:"~400 sq ft, 28206."},
      {who:"OS",ai:1,txt:"Perfect — that's in our service area. I've got Thursday 9am or Friday 1pm for an on-site estimate. Which works? (Owner's already notified.)"}
    ]}},
  dental:{label:"Dental practice",icon:"🦷",
    mods:[
      {p:"Intake",n:"Front Desk + Booking",d:"Books appointments, screens insurance, handles after-hours calls.",start:true},
      {p:"Customer",n:"Recall + Reminders",d:"Brings patients back on schedule; cuts no-shows."},
      {p:"Marketing",n:"Reactivation",d:"Wins back lapsed patients with the right nudge."},
      {p:"Back Office",n:"Claims + Billing Prep",d:"Preps claims and statements for your team to approve."},
      {p:"Company Brain",n:"Practice SOPs",d:"Front-desk answers, policies, and protocols on demand."}
    ],
    demo:{title:"Front Desk + Booking",sub:"an after-hours call",lines:[
      {who:"Caller",txt:"My crown popped off — can I get in tomorrow? Also do you take Delta Dental?"},
      {who:"OS",ai:1,txt:"Oh no — let's get you seen. Yes, we're in-network with Delta Dental. I have 8:40am or 11:20am tomorrow with Dr. Lee. Which is better?"},
      {who:"Caller",txt:"8:40 works."},
      {who:"OS",ai:1,txt:"Booked. I've sent a confirmation + the new-patient form by text, and flagged it as a same-day repair so the team preps the room."}
    ]}},
  restaurant:{label:"Restaurant",icon:"🍽️",
    mods:[
      {p:"Intake",n:"Reservations + Inbound",d:"Takes bookings and the waitlist, answers hours/menu questions.",start:true},
      {p:"Operations",n:"Catering + Events Intake",d:"Captures event requests and drafts the proposal."},
      {p:"Marketing",n:"Social + Promos",d:"Posts specials and fills slow nights."},
      {p:"Customer",n:"Review + Feedback",d:"Routes complaints fast, harvests good reviews."},
      {p:"Back Office",n:"Vendor Invoices",d:"Sorts and preps supplier invoices."}
    ],
    demo:{title:"Reservations + Inbound",sub:"a Friday-night booking",lines:[
      {who:"Caller",txt:"Table for 6 tonight around 7:30?"},
      {who:"OS",ai:1,txt:"7:30 is fully booked, but I have 8:15 for 6 — or I can add you to the 7:30 waitlist and text you the moment it opens. Preference?"},
      {who:"Caller",txt:"8:15 is fine."},
      {who:"OS",ai:1,txt:"Done — table for 6 at 8:15 under your name, confirmation texted. See you tonight!"}
    ]}},
  law:{label:"Law firm",icon:"⚖️",
    mods:[
      {p:"Intake",n:"Intake + Conflict Check",d:"Screens new matters, runs a conflict check, drafts the intake for attorney review.",start:true},
      {p:"Operations",n:"Matter + Deadline Tracker",d:"Watches every deadline and doc expiry across matters."},
      {p:"Marketing",n:"Content + AI Search",d:"Keeps the firm visible where clients now search."},
      {p:"Back Office",n:"Billing + AR",d:"Drafts invoices and chases receivables."},
      {p:"Company Brain",n:"Firm Knowledge",d:"Precedent, templates, and policy — answered with citations."}
    ],
    demo:{title:"Intake + Conflict Check",sub:"a new-matter inquiry (drafts for your review — never gives legal advice)",lines:[
      {who:"Lead",txt:"I was rear-ended last week and want to know if I have a case."},
      {who:"OS",ai:1,txt:"I'm sorry that happened. I can't give legal advice, but I can get you in front of an attorney. A few quick questions to set up your consult, then our team reviews it."},
      {who:"OS",ai:1,txt:"…ran a conflict check (clear), drafted the intake summary, and flagged it for attorney review. Consult offered: Tue 10am."}
    ]}},
  ecommerce:{label:"E-commerce",icon:"🛒",
    mods:[
      {p:"Customer",n:"Support + Returns",d:"Answers WISMO, handles returns by your rules, escalates the rest.",start:true},
      {p:"Marketing",n:"Listings + Email",d:"Writes product copy and lifecycle email."},
      {p:"Sales",n:"Win-back + Abandoned Cart",d:"Recovers carts and re-engages lapsed buyers."},
      {p:"Back Office",n:"Reconciliation",d:"Matches orders, payouts, and refunds."},
      {p:"Company Brain",n:"Product Knowledge",d:"Every SKU detail and policy, instantly."}
    ],
    demo:{title:"Support + Returns",sub:"a where's-my-order ticket",lines:[
      {who:"Customer",txt:"Order #4821 still hasn't shipped — getting frustrated."},
      {who:"OS",ai:1,txt:"Apologies for the wait. #4821 cleared the warehouse this morning and ships today — tracking will hit your inbox by 6pm. For the delay, here's 15% off your next order."},
      {who:"Customer",txt:"Ok thanks. Actually one item runs small, can I exchange?"},
      {who:"OS",ai:1,txt:"Of course — it's within the 30-day window. I've started the exchange for the next size up and emailed a prepaid return label."}
    ]}},
  realestate:{label:"Real estate",icon:"🏠",
    mods:[
      {p:"Sales",n:"Lead Follow-up + Speed-to-Lead",d:"Responds to every new lead in seconds, qualifies, books the showing.",start:true},
      {p:"Intake",n:"Front Desk",d:"Fields inbound calls and routing."},
      {p:"Marketing",n:"Listing Marketing",d:"Generates the listing copy, social, and email blast."},
      {p:"Customer",n:"Past-client Nurture",d:"Stays in touch for referrals and repeat deals."},
      {p:"Back Office",n:"Transaction Coordination",d:"Tracks dates, docs, and contingencies to close."}
    ],
    demo:{title:"Lead Follow-up + Speed-to-Lead",sub:"a portal lead, 11pm",lines:[
      {who:"Lead",txt:"Is 142 Oak St still available? Saw it on Zillow."},
      {who:"OS",ai:1,txt:"It is! Beautiful 3-bed. Are you looking to tour it, and are you working with a lender yet? I can hold Sat 11am or Sun 2pm."},
      {who:"Lead",txt:"Sat 11 works, not pre-approved yet."},
      {who:"OS",ai:1,txt:"Booked Sat 11am, and I'll text you a 2-minute pre-approval link so you're ready to offer. Your agent's looped in."}
    ]}},
  salon:{label:"Salon / spa",icon:"✂️",
    mods:[
      {p:"Intake",n:"Booking + Front Desk",d:"Books from text/DM/call, fills cancellations, answers questions.",start:true},
      {p:"Customer",n:"Rebooking + Reminders",d:"Gets clients back on the calendar; cuts no-shows."},
      {p:"Marketing",n:"Promos + Social",d:"Posts openings and fills the slow days."},
      {p:"Back Office",n:"Payments + Reporting",d:"Reconciles tips, payouts, and the daily numbers."}
    ],
    demo:{title:"Booking + Front Desk",sub:"an Instagram DM",lines:[
      {who:"Client",txt:"Any balayage openings this week? 🙏"},
      {who:"OS",ai:1,txt:"Yes! Maya has Thu 1pm or Fri 10am for balayage (about 3 hrs). Want me to book one?"},
      {who:"Client",txt:"Fri 10!"},
      {who:"OS",ai:1,txt:"Booked with Maya, Fri 10am — confirmation + a $25-deposit link texted to you. We'll remind you the day before."}
    ]}},
  other:{label:"Something else",icon:"✨",
    mods:[
      {p:"Intake",n:"Front Desk",d:"Captures and qualifies every inbound, books the next step.",start:true},
      {p:"Sales",n:"Lead Follow-up",d:"Never lets a lead go cold."},
      {p:"Marketing",n:"Content + Reviews",d:"Keeps you visible and well-reviewed."},
      {p:"Customer",n:"Support",d:"Handles the routine, escalates the rest."},
      {p:"Back Office",n:"Invoicing + Books prep",d:"Chases cash and preps the numbers."},
      {p:"Company Brain",n:"Knowledge",d:"Your business's answers, on demand."}
    ],
    demo:{title:"Front Desk",sub:"a missed inquiry, captured",lines:[
      {who:"Caller",txt:"Hi, do you handle [what I need]? Tried calling earlier."},
      {who:"OS",ai:1,txt:"We do — sorry we missed you! Quick question to point you right, then I'll book you in with the right person."},
      {who:"OS",ai:1,txt:"…qualified the request, booked the next step, and notified the owner. Nothing slips through."}
    ]}}
};

/* how the modules hand work to each other — one job, end to end. Keyed to the archetypes above. */
const FLOWS={
  landscaping:[
    {p:"Intake",n:"Front Desk",did:"Catches the missed paver-patio call, qualifies the job, books the on-site estimate.",pass:"the qualified lead"},
    {p:"Operations",n:"Scheduler + Weather",did:"Slots the estimator and the crew — and auto-reschedules if rain rolls in.",pass:"the confirmed visit"},
    {p:"Sales",n:"Estimate Follow-up",did:"After the quote goes out, it chases the signature until it's signed or declined.",pass:"the signed job"},
    {p:"Back Office",n:"Deposit + Invoice",did:"Drafts the deposit request off the signed work — held for your okay before it sends.",pass:"a booked, paid job"}
  ],
  dental:[
    {p:"Intake",n:"Front Desk + Booking",did:"Takes the after-hours crown call, screens insurance, books the repair.",pass:"the booked patient"},
    {p:"Customer",n:"Recall + Reminders",did:"Texts the confirmation + new-patient form, then a reminder to kill the no-show.",pass:"a confirmed, prepped visit"},
    {p:"Back Office",n:"Claims + Billing Prep",did:"Pre-fills the insurance claim and statement for your team to approve.",pass:"a clean claim"}
  ],
  restaurant:[
    {p:"Intake",n:"Reservations + Inbound",did:"Books the Friday table — or works the waitlist — after the host stand's gone home.",pass:"the reservation"},
    {p:"Operations",n:"Catering + Events",did:"If it's a party, captures the event details and drafts the proposal.",pass:"the event lead"},
    {p:"Customer",n:"Review + Feedback",did:"After the visit, routes any complaint fast and asks happy guests for a review.",pass:"a saved guest + a 5-star review"}
  ],
  law:[
    {p:"Intake",n:"Intake + Conflict Check",did:"Screens the new matter, runs the conflict check, drafts the intake — never gives legal advice.",pass:"a vetted matter"},
    {p:"Operations",n:"Deadline Tracker",did:"Once it's opened, watches every deadline and document expiry.",pass:"an on-track matter"},
    {p:"Back Office",n:"Billing + AR",did:"Drafts the invoices and chases the receivables.",pass:"a paid matter"}
  ],
  ecommerce:[
    {p:"Customer",n:"Support + Returns",did:"Answers the where's-my-order, handles the return by your rules.",pass:"the resolved customer"},
    {p:"Sales",n:"Win-back + Cart",did:"Recovers the abandoned cart and re-engages the lapsed buyer.",pass:"the recovered order"},
    {p:"Back Office",n:"Reconciliation",did:"Matches the order, the payout, and the refund so the books stay clean.",pass:"clean books"}
  ],
  realestate:[
    {p:"Sales",n:"Speed-to-Lead",did:"Answers the 11pm portal lead in seconds, qualifies, books the showing + sends a pre-approval link.",pass:"a qualified buyer"},
    {p:"Marketing",n:"Listing Marketing",did:"Spins up the listing copy, social, and email blast to pull in more leads.",pass:"a fuller funnel"},
    {p:"Back Office",n:"Transaction Coordination",did:"Once under contract, tracks every date, doc, and contingency to close.",pass:"a clean close"}
  ],
  salon:[
    {p:"Intake",n:"Booking + Front Desk",did:"Books the balayage from a DM and fills a last-minute cancellation.",pass:"the booked appointment"},
    {p:"Customer",n:"Rebooking + Reminders",did:"Sends the deposit link + reminder, then rebooks them before they leave.",pass:"a repeat client"},
    {p:"Marketing",n:"Promos + Social",did:"Posts the open chairs to fill the slow days.",pass:"a full calendar"}
  ],
  other:[
    {p:"Intake",n:"Front Desk",did:"Captures and qualifies every inbound, books the next step.",pass:"the qualified lead"},
    {p:"Sales",n:"Lead Follow-up",did:"Chases it until it converts or closes out — nothing goes cold.",pass:"the won customer"},
    {p:"Back Office",n:"Invoicing + Books",did:"Drafts the invoice (held for your okay) and preps the numbers.",pass:"cash in the door"}
  ]
};


const ALIASES=[
  ['dental',['dental','dentist','orthodon','ortho','teeth','oral surg','endodon','periodon']],
  ['law',['law ','lawyer','attorney','legal','counsel','paralegal','litigat']],
  ['realestate',['real estate','realtor','realty','broker','property','listing','mortgage']],
  ['restaurant',['restaurant','cafe','café','coffee','bistro','eatery','diner','food truck','catering','bakery','pizz','kitchen','grill']],
  ['salon',['salon','spa','hair','barber','nail','beauty','medspa','aesthetic','botox','lash','massage','tattoo']],
  ['ecommerce',['ecommerce','e-commerce','online store','online shop','shopify','webstore','dtc','retail','boutique','apparel','merch']],
  ['landscaping',['landscap','hardscap','lawn','paver','patio','yard','irrigation','tree service','garden','snow removal','pool']]
];
function classify(q){ const s=' '+q.toLowerCase()+' ';
  for(const [k,keys] of ALIASES){ for(const kw of keys){ if(s.includes(kw)) return k; } }
  return 'other'; }
function esc(s){return s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function clean(s){return esc(s.trim().replace(/\s+/g,' ').slice(0,48));}


  /* Renders into any element, so the configurator and the standalone blueprint cannot drift. */
  function renderInto(stage, k, name) {

  const b=BIZ[k]; name=name||b.label;
  const cards=b.mods.map(m=>{
    const start=!!m.start;
    return `<div class="osb-mod ${start?'start':'exp'}">
      <div class="pill-tag">${m.p}</div>
      <h4>${m.n}</h4>
      <p>${m.d}</p>
      <span class="badge">${start?'▶ Start here':'expand to'}</span>
    </div>`;
  }).join('');
  const flow=(FLOWS[k]||FLOWS.other);
  const steps=flow.map((s,i2)=>`<li class="fstep" style="--i:${i2}">
        <div class="fnode"><span class="fp">${s.p}</span><span class="fn">${s.n}</span></div>
        <div class="fdid">${s.did}</div>
        <div class="fpass"><span class="farr">&darr;</span> hands off <b>${s.pass}</b></div>
      </li>`).join('');
  stage.innerHTML=`
    <p class="osb-intro">Here&rsquo;s the AI OS we&rsquo;d build for <b>${name}</b> &mdash; coordinated, and operated by us. Begin with the highlighted module; add the rest as you grow.</p>
    <div class="osb-board">${cards}</div>
    <div class="osb-flow">
      <div class="dh"><div class="dot">${b.icon}</div><div><div class="dt">Watch the system work together</div><div class="ds">one job, passed module to module &mdash; no handoff dropped</div></div></div>
      <ol class="flow-steps">${steps}
        <li class="fstep final" style="--i:${flow.length}">
          <div class="fnode"><span class="fp">Company Brain &middot; Approvals</span><span class="fn">Logged &amp; gated</span></div>
          <div class="fdid">Every step is captured, so the OS gets sharper each time &mdash; and anything that sends money or reaches a customer waits for <b>your approval</b> first.</div>
        </li>
      </ol>
    </div>
    <p class="osb-note">Illustrative — a sketch of how the modules coordinate. Your full OS (which modules, in what order) is scoped in the audit. Nothing here is a quote.</p>`;

  }

  root.OSBlueprint = {
    BIZ: BIZ, FLOWS: FLOWS, ALIASES: ALIASES,
    classify: classify, clean: clean, esc: esc, renderInto: renderInto
  };
})(window);
