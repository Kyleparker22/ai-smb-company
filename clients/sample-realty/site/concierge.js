/* ─────────────────────────────────────────────────────────────────────────────
   Sample Realty concierge — the 24/7 assistant widget (DEMO).

   This demo runs entirely client-side on scripted intents + live data from
   listings-data.js, so it genuinely answers listing questions and captures
   leads. AT ENGAGEMENT: the reply engine swaps to the operated AI service
   (Claude API via the yourco runtime) with the same UI — every conversation
   lands in the CRM and showing requests reach Kimi as drafted replies for
   her approval. The client-facing promise is "we answer instantly, a human
   confirms" — approval-gated, never auto-booked.

   Include with:  <script src="[base]listings-data.js"></script>
                  <script src="[base]concierge.js" data-base=""></script>
   data-base = path prefix to the site root from the current page ("" or "../").
   ──────────────────────────────────────────────────────────────────────────── */
(function(){
  const script = document.currentScript;
  const BASE = (script && script.dataset.base) || "";
  const L = window.PR_LISTINGS || [];

  /* ── artifact telemetry (disclosed) ─────────────────────────────────────
     A whisper of engagement data to the CRM: page view + a 15s heartbeat
     while the tab is visible. No identity, no cookies beyond a session tag.
     Disclosure lives in the demo ribbon/footer. Fails silently when the
     CRM isn't running. AT LAUNCH: point CRM_T at the hosted CRM. */
  (function(){
    const CRM_T = "http://localhost:8790/t";
    let sid = "";
    try { sid = sessionStorage.pr_sid || (sessionStorage.pr_sid = Math.random().toString(36).slice(2,10)); } catch(e){}
    const send = e => { try {
      const payload = JSON.stringify({ p: location.pathname + location.search, e, s: sid });
      if (navigator.sendBeacon) navigator.sendBeacon(CRM_T, new Blob([payload], {type:"text/plain"}));
      else fetch(CRM_T, {method:"POST", body: payload, keepalive:true}).catch(()=>{});
    } catch(err){} };
    send("view");
    setInterval(() => { if (document.visibilityState === "visible") send("beat"); }, 15000);
  })();

  /* ── styles ── */
  const css = document.createElement("style");
  css.textContent = `
  .pr-fab{position:fixed;right:22px;bottom:22px;z-index:90;width:60px;height:60px;border-radius:9999px;background:#EF0004;color:#fff;border:0;cursor:pointer;box-shadow:0 8px 28px rgba(19,19,24,.35);display:flex;align-items:center;justify-content:center;font-family:Didot,Georgia,serif;font-size:26px;transition:transform .2s ease}
  .pr-fab:hover{transform:scale(1.06)}
  .pr-fab .dot{position:absolute;top:4px;right:4px;width:12px;height:12px;border-radius:9999px;background:#F7F5F0;border:2px solid #EF0004}
  .pr-chat{position:fixed;right:22px;bottom:94px;z-index:91;width:min(390px,calc(100vw - 44px));max-height:min(600px,calc(100vh - 130px));background:#FCFBF8;border:1px solid rgba(19,19,24,.15);box-shadow:0 18px 60px rgba(19,19,24,.28);display:none;flex-direction:column;overflow:hidden}
  .pr-chat.open{display:flex}
  .pr-hd{background:#131318;color:#F7F5F0;padding:16px 20px;display:flex;justify-content:space-between;align-items:center}
  .pr-hd .t{font-family:Didot,Georgia,serif;font-size:17px}
  .pr-hd .t i{font-style:normal;color:#EF0004}
  .pr-hd .s{font-family:"Avenir Next",Avenir,sans-serif;font-size:8.5px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:rgba(247,245,240,.6);margin-top:2px;display:flex;align-items:center;gap:6px}
  .pr-hd .s:before{content:"";width:7px;height:7px;border-radius:9999px;background:#4CBB6C;display:inline-block}
  .pr-hd button{background:none;border:0;color:#F7F5F0;font-size:20px;cursor:pointer;line-height:1}
  .pr-log{flex:1;overflow-y:auto;padding:18px;display:flex;flex-direction:column;gap:12px}
  .pr-m{max-width:86%;padding:11px 15px;font-size:13.5px;line-height:1.6;font-family:"Hoefler Text",Baskerville,Georgia,serif}
  .pr-m.bot{background:#F2EFE9;border:1px solid rgba(19,19,24,.1);align-self:flex-start;border-radius:2px 14px 14px 14px}
  .pr-m.user{background:#131318;color:#F7F5F0;align-self:flex-end;border-radius:14px 2px 14px 14px}
  .pr-m .lst{margin-top:8px;border-top:1px solid rgba(19,19,24,.12);padding-top:8px}
  .pr-m .lst a{display:block;color:#131318;text-decoration:none;padding:7px 0;border-bottom:1px solid rgba(19,19,24,.08);font-size:13px}
  .pr-m .lst a:hover{color:#EF0004}
  .pr-m .lst a b{font-family:Didot,Georgia,serif;font-weight:400}
  .pr-m .lst a span{display:block;font-family:"Avenir Next",Avenir,sans-serif;font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:rgba(19,19,24,.55);margin-top:2px}
  .pr-chips{display:flex;flex-wrap:wrap;gap:8px;padding:0 18px 12px}
  .pr-chip{font-family:"Avenir Next",Avenir,sans-serif;font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;padding:8px 14px;border-radius:9999px;border:1px solid rgba(19,19,24,.2);background:#fff;cursor:pointer;color:#20202a}
  .pr-chip:hover{border-color:#EF0004;color:#EF0004}
  .pr-in{display:flex;gap:10px;padding:14px 16px;border-top:1px solid rgba(19,19,24,.12);background:#fff}
  .pr-in input{flex:1;font-family:"Avenir Next",Avenir,sans-serif;font-size:13.5px;padding:11px 14px;border:1px solid rgba(19,19,24,.18);border-radius:9999px;outline:none}
  .pr-in input:focus{border-color:#EF0004}
  .pr-in button{width:42px;height:42px;border-radius:9999px;background:#EF0004;color:#fff;border:0;cursor:pointer;font-size:16px}
  .pr-in button:hover{background:#c70004}
  .pr-note{font-family:"Avenir Next",Avenir,sans-serif;font-size:8.5px;letter-spacing:.06em;color:rgba(19,19,24,.45);text-align:center;padding:0 16px 10px;background:#fff}
  .pr-typing{display:inline-flex;gap:4px;padding:4px 2px}
  .pr-typing i{width:6px;height:6px;border-radius:9999px;background:rgba(19,19,24,.4);animation:prb 1.1s infinite}
  .pr-typing i:nth-child(2){animation-delay:.15s}
  .pr-typing i:nth-child(3){animation-delay:.3s}
  @keyframes prb{0%,60%,100%{transform:translateY(0);opacity:.5}30%{transform:translateY(-4px);opacity:1}}`;
  document.head.appendChild(css);

  /* ── markup ── */
  const fab = document.createElement("button");
  fab.className = "pr-fab"; fab.setAttribute("aria-label", "Chat with Sample Realty");
  fab.innerHTML = '"<span class="dot"></span>';
  const box = document.createElement("div");
  box.className = "pr-chat";
  box.innerHTML =
    '<div class="pr-hd"><div><div class="t">P<i>·</i>R Concierge</div>' +
    '<div class="s">Answers instantly · a human confirms</div></div>' +
    '<button aria-label="Close">×</button></div>' +
    '<div class="pr-log"></div><div class="pr-chips"></div>' +
    '<div class="pr-in"><input placeholder="Ask about a listing, book a showing…"/>' +
    '<button aria-label="Send">➤</button></div>' +
    '<div class="pr-note">Demo assistant · in production every conversation reaches Kimi as a drafted reply for her approval — nothing sends itself.</div>';
  document.body.appendChild(fab); document.body.appendChild(box);

  const log = box.querySelector(".pr-log"), chipsEl = box.querySelector(".pr-chips");
  const input = box.querySelector(".pr-in input"), send = box.querySelector(".pr-in button");

  /* ── helpers ── */
  function msg(html, who){
    const d = document.createElement("div");
    d.className = "pr-m " + who; d.innerHTML = html;
    log.appendChild(d); log.scrollTop = log.scrollHeight;
    return d;
  }
  function typing(cb, delay){
    const t = msg('<span class="pr-typing"><i></i><i></i><i></i></span>', "bot");
    setTimeout(() => { t.remove(); cb(); }, delay || 700);
  }
  function chips(list){
    chipsEl.innerHTML = "";
    list.forEach(c => {
      const b = document.createElement("button");
      b.className = "pr-chip"; b.textContent = c;
      b.addEventListener("click", () => handle(c));
      chipsEl.appendChild(b);
    });
  }
  function listingLinks(items){
    return '<div class="lst">' + items.map(l => {
      const href = BASE + "listings/" + (l.href || ("listing.html?id=" + l.slug));
      return '<a href="' + href + '"><b>' + l.address + " — " + l.price +
             (l.priceSuffix ? " " + l.priceSuffix : "") + "</b><span>" + l.facts + "</span></a>";
    }).join("") + "</div>";
  }
  const actives = L.filter(l => l.status === "active" || l.status === "coming");
  const lease = L.filter(l => l.status === "lease");
  const priceOf = l => parseInt(String(l.price).replace(/[^0-9]/g, "")) || 0;

  /* ── the lead-capture mini-flow ── */
  let flow = null;
  function startFlow(kind, intro){
    flow = { kind, step: 0, data: {} };
    typing(() => { msg(intro + " First — what's your name?", "bot"); chips([]); });
  }
  function flowNext(text){
    if (flow.step === 0) {
      flow.data.name = text; flow.step = 1;
      typing(() => msg("Thanks, " + text.split(" ")[0] + ". Best email or phone to reach you?", "bot"));
    } else if (flow.step === 1) {
      flow.data.contact = text; flow.step = 2;
      typing(() => msg(flow.kind === "showing"
        ? "And what day &amp; time work best for the showing?"
        : "Got it. Anything we should know before we reach out?", "bot"));
    } else {
      flow.data.detail = text;
      try {
        const leads = JSON.parse(localStorage.getItem("pr_concierge_leads") || "[]");
        leads.push({ ...flow.data, kind: flow.kind, at: new Date().toISOString() });
        localStorage.setItem("pr_concierge_leads", JSON.stringify(leads));
      } catch (e) {}
      const done = flow.kind === "showing"
        ? "Perfect — I've drafted the showing request for <b>Kimi's approval</b>; she'll confirm the exact time with you shortly. <i>(Demo — nothing actually sent.)</i>"
        : "Perfect — that's with <b>Kimi</b> now and she'll be in touch within the day. <i>(Demo — nothing actually sent.)</i>";
      flow = null;
      typing(() => { msg(done, "bot"); chips(["Active listings", "What's my home worth?", "Talk to Kimi"]); });
    }
  }

  /* ── intent engine (demo) ── */
  function handle(raw){
    const text = raw.trim(); if (!text) return;
    msg(text.replace(/</g, "&lt;"), "user"); input.value = "";
    if (flow) { flowNext(text); return; }
    const q = text.toLowerCase();
    const budget = (q.match(/\$?\s?(\d{3})[,.]?(\d{3})\b|\$?(\d{3})k/i));

    if (/book|showing|tour|visit|see (it|the|this)/.test(q)) {
      startFlow("showing", "Happy to set that up — showings run on your schedule, evenings and weekends included.");
    } else if (/worth|valuation|cma|value/.test(q)) {
      typing(() => { msg('That\'s our favorite question. Kimi builds every valuation personally — a real comparative market analysis, delivered within 24 hours. Start here: <div class="lst"><a href="' + BASE + 'tools/home-worth.html"><b>What\'s your home worth? →</b><span>Zillow has never walked your street. We have.</span></a></div>', "bot"); chips(["Active listings", "Book a showing", "Talk to Kimi"]); });
    } else if (/rent|lease/.test(q) && lease.length) {
      typing(() => { msg("We have one home available to rent right now:" + listingLinks(lease), "bot"); chips(["Book a showing", "Active listings", "Talk to Kimi"]); });
    } else if (/invest|rental|cap rate|cash flow/.test(q)) {
      typing(() => { msg('Investor? You\'ll like this: run any deal — including our listings — through the analyzer, then our property-management division runs the property after you buy. <div class="lst"><a href="' + BASE + 'tools/investor.html"><b>Investor analyzer →</b><span>Cap rate · cash flow · buy it, we\'ll run it</span></a></div>', "bot"); chips(["Active listings", "Talk to Kimi"]); });
    } else if (budget) {
      const cap = parseInt((budget[1] ? budget[1] + budget[2] : budget[3] + "000"), 10) * (budget[3] ? 1 : 1);
      const max = cap < 10000 ? cap * 1000 : cap;
      const fits = actives.filter(l => priceOf(l) <= max * 1.05);
      typing(() => { msg(fits.length
        ? "Here's what's on the market around that number:" + listingLinks(fits)
        : "Nothing active under that number this week — but coming-soons launch here first. Want me to put you on the private list?", "bot");
        chips(fits.length ? ["Book a showing", "Talk to Kimi"] : ["Join the private list", "Talk to Kimi"]); });
    } else if (/active|listing|for sale|available|market|homes/.test(q)) {
      typing(() => { msg("Here's everything we're representing right now:" + listingLinks(actives), "bot"); chips(["Book a showing", "What's my home worth?", "Talk to Kimi"]); });
    } else if (/private list|coming soon|early|first/.test(q)) {
      startFlow("privatelist", "Smart move — our coming-soons (like 1208 High Brook) appear to the private list before the portals.");
    } else if (/human|kimi|call|talk|contact|agent/.test(q)) {
      startFlow("contact", "Of course — Kimi personally returns every message.");
    } else if (/sell|selling/.test(q)) {
      typing(() => { msg('Selling starts with two things: what your home is worth, and what the launch looks like. <div class="lst"><a href="' + BASE + 'tools/home-worth.html"><b>Get your free valuation →</b><span>A real CMA from Kimi within 24 hours</span></a><a href="' + BASE + 'results.html"><b>See how our last sales went →</b><span>Under contract in 4 days · sold over asking</span></a></div>', "bot"); chips(["What's my home worth?", "Talk to Kimi"]); });
    } else {
      typing(() => { msg("I can help with listings, showings, valuations, renting, or investing — or connect you straight to Kimi. What sounds right?", "bot"); chips(["Active listings", "Book a showing", "What's my home worth?", "Talk to Kimi"]); });
    }
  }

  /* ── wiring ── */
  let opened = false;
  fab.addEventListener("click", () => {
    box.classList.toggle("open");
    if (!opened) {
      opened = true;
      typing(() => {
        msg("Welcome to Sample Realty — I'm the concierge, on duty around the clock. Ask me anything, even at 11pm; Kimi confirms everything personally.", "bot");
        chips(["Active listings", "Book a showing", "What's my home worth?", "Talk to Kimi"]);
      }, 500);
    }
  });
  box.querySelector(".pr-hd button").addEventListener("click", () => box.classList.remove("open"));
  send.addEventListener("click", () => handle(input.value));
  input.addEventListener("keydown", e => { if (e.key === "Enter") handle(input.value); });
})();
