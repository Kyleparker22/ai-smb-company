/* Client demo kit — shared renderer. Reads window.DEMO (config.js), injects brand-colored
   CSS, and builds the page named in <body data-page="...">. You don't edit this file. */
(function () {
  var D = window.DEMO || {};
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };

  // derive a darker + a light tint from the brand hex
  function shade(hex, p) {
    hex = (hex || "#2c5f2d").replace("#", "");
    var n = parseInt(hex.length === 3 ? hex.replace(/(.)/g, "$1$1") : hex, 16);
    var r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255, f = p < 0;
    p = Math.abs(p); var m = function (x) { return Math.round((f ? x : 255 - x) * p) * (f ? -1 : 1) + x; };
    return "#" + ((1 << 24) + (m(r) << 16) + (m(g) << 8) + m(b)).toString(16).slice(1);
  }
  function tint(hex) { hex = (hex || "#2c5f2d").replace("#", ""); var n = parseInt(hex, 16);
    return "rgba(" + ((n >> 16) & 255) + "," + ((n >> 8) & 255) + "," + (n & 255) + ",.09)"; }

  var root = document.documentElement.style;
  root.setProperty("--brand", D.brand || "#2c5f2d");
  root.setProperty("--brand-d", shade(D.brand, -0.28));
  root.setProperty("--tint", tint(D.brand));

  var CSS = `
  :root{--bg:#f4f5f1;--card:#fff;--ink:#1c2419;--muted:#6b7280;--line:#e8e9e3;--green:#2f7d52;--green-d:#256643;--amber:#b07d1e;--grey:#9aa0a6;--red:#b23b32}
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--ink);font-family:-apple-system,system-ui,"Inter","Segoe UI",Helvetica,Arial,sans-serif;line-height:1.5;-webkit-font-smoothing:antialiased}
  .wrap{max-width:1000px;margin:0 auto;padding:0 20px 40px}
  a{color:inherit}
  /* phone frame */
  .center{display:flex;justify-content:center;min-height:100vh;padding:22px 14px}
  .phone{width:100%;max-width:390px;background:var(--card);border-radius:30px;overflow:hidden;box-shadow:0 20px 60px rgba(28,36,25,.22);align-self:flex-start}
  @media(max-width:430px){.phone{border-radius:0;box-shadow:none}.center{padding:0}}
  .bar{background:var(--brand);color:#fff;padding:16px 18px 14px;display:flex;align-items:center;gap:10px}
  .bar .logo{font-weight:700}.bar .secure{margin-left:auto;font-size:11px;color:rgba(255,255,255,.85);display:flex;gap:5px;background:rgba(255,255,255,.14);padding:4px 9px;border-radius:9999px}
  /* index */
  .top{background:var(--brand);color:#fff;padding:30px 0 26px}
  .top .logo{font-size:18px;font-weight:700;opacity:.9}.top h1{font-size:27px;font-weight:700;margin:12px 0 6px;letter-spacing:-.02em}
  .top p{font-size:14.5px;color:rgba(255,255,255,.85);max-width:56ch}
  .steps{margin:24px auto}
  .step{display:flex;gap:15px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin-bottom:12px;text-decoration:none;color:inherit;transition:border-color .15s}
  .step:hover{border-color:var(--brand)}.step.flow{cursor:default;background:var(--tint);border-color:transparent}.step.flow:hover{border-color:transparent}
  .step .n{width:30px;height:30px;border-radius:50%;background:var(--tint);color:var(--brand-d);font-weight:700;font-size:14px;display:flex;align-items:center;justify-content:center;flex:none}
  .step .tt{font-size:15.5px;font-weight:650}.step .ds{font-size:13px;color:var(--muted);margin-top:1px}.step .arr{color:var(--brand);font-size:18px}
  .note{font-size:12px;color:var(--muted);text-align:center;margin:8px 0 30px;line-height:1.6}.note b{color:var(--brand)}
  /* approval */
  .body{padding:18px}.lede{font-size:13px;color:var(--muted)}.h{font-size:19px;font-weight:680;margin:3px 0 14px;letter-spacing:-.01em}.h b{color:var(--brand)}
  .count{font-size:12.5px;color:var(--brand-d);font-weight:650;margin:-10px 0 14px}
  .req{border:1px solid var(--line);border-radius:14px;overflow:hidden;margin-bottom:13px}
  .rt{padding:12px 15px;border-bottom:1px solid var(--line);font-size:13px;color:var(--muted)}.rt b{color:var(--ink);font-weight:650;font-size:14px}
  .amt{display:flex;align-items:center;gap:9px;padding:13px 15px;background:var(--tint);border-bottom:1px solid var(--line)}
  .amt .v{font-size:23px;font-weight:720}.amt .s{font-size:11.5px;color:var(--muted)}.amt .tag{margin-left:auto;font-size:10px;font-weight:700;color:var(--brand-d);background:#fff;border:1px solid var(--line);border-radius:9999px;padding:3px 9px;text-transform:uppercase;letter-spacing:.03em}
  .msg{padding:14px 15px}.lbl{font-size:10.5px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
  .email{font-size:13.5px;color:#283226;white-space:pre-wrap;line-height:1.5}
  .bubble{background:var(--tint);border-radius:14px 14px 14px 4px;padding:10px 13px;font-size:13px;color:#283226;display:inline-block;max-width:92%;margin-top:6px}
  .together{font-size:11.5px;color:var(--muted);margin-top:10px}
  .acts{display:grid;gap:9px;padding:0 0 2px}.row2{display:grid;grid-template-columns:1fr 1fr;gap:9px}
  .btn{appearance:none;border:none;font:inherit;font-size:14px;font-weight:650;border-radius:11px;padding:12px;cursor:pointer}
  .approve{background:var(--green);color:#fff}.approve:active{background:var(--green-d)}.ghost{background:#fff;border:1px solid var(--line);color:var(--ink)}.decline{background:#fff;border:1px solid #eccfcc;color:var(--red)}
  .resolved{padding:13px 15px;font-size:14px;font-weight:600}.resolved.ok{color:var(--green-d);background:#f1f8f2}.resolved.no{color:var(--red);background:#fbf3f2}
  .result{padding:26px 18px;text-align:center}.result .ic{width:58px;height:58px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:30px;margin:0 auto 12px}
  .result.ok .ic{background:#dcefe0;color:var(--green-d)}.result h2{font-size:19px;font-weight:680;margin-bottom:6px}.result p{font-size:13.5px;color:var(--muted);max-width:30ch;margin:0 auto}
  .log{font-size:11.5px;color:var(--muted);margin-top:14px;background:#f5f6f3;border-radius:9px;padding:9px 12px;display:inline-block}
  /* board */
  .btop{background:var(--brand);color:#fff;padding:18px 0}.btop .wrap{display:flex;align-items:center;gap:12px;padding-bottom:0}
  .btop .logo{font-size:18px;font-weight:700}.btop .sub{font-size:13px;color:rgba(255,255,255,.78)}.btop .live{margin-left:auto;font-size:12px;display:flex;align-items:center;gap:7px;color:rgba(255,255,255,.9)}
  .pulse{width:8px;height:8px;border-radius:50%;background:#7fe0a0;box-shadow:0 0 0 3px rgba(127,224,160,.3);animation:p 2s infinite}@keyframes p{50%{box-shadow:0 0 0 6px rgba(127,224,160,0)}}
  .metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0}@media(max-width:720px){.metrics{grid-template-columns:repeat(2,1fr)}}
  .metric{background:var(--card);border:1px solid var(--line);border-radius:13px;padding:15px 16px}.metric .v{font-size:26px;font-weight:700;letter-spacing:-.02em}.metric .l{font-size:12px;color:var(--muted);margin-top:2px}.metric .v.ac{color:var(--brand)}
  .nudge{background:#fdf6e9;border:1px solid #f0e2c4;border-radius:12px;padding:13px 16px;margin-bottom:18px}.nudge h3{font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--amber);margin-bottom:8px}.nudge .it{font-size:13.5px;color:#4a3f24;padding:4px 0}
  h2.sec{font-size:13px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);margin:6px 0 12px}
  .job{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin-bottom:12px}.job.go{border-color:#bfe0c8;background:#f1f8f2}
  .jh{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}.jn{font-size:16px;font-weight:680}.jp{font-size:13px;color:var(--muted)}.jt{margin-left:auto;font-size:15px;font-weight:680}
  .badge{display:inline-block;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;border-radius:9999px;padding:3px 10px}.badge.go{background:#dcefe0;color:var(--green-d)}.badge.run{background:#eef0f2;color:#566}.badge.new{background:#eaf1fb;color:#2c5aa0}
  .gates{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:13px}@media(max-width:560px){.gates{grid-template-columns:1fr}}
  .gate{border:1px solid var(--line);border-radius:11px;padding:10px 12px;background:#fcfdfb}.gate .gl{font-size:10.5px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}.gate .gv{font-size:13.5px;font-weight:600;margin-top:3px;display:flex;align-items:center;gap:7px}
  .gi{width:17px;height:17px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px;color:#fff;flex:none}.done .gi{background:var(--green)}.pend .gi{background:var(--amber)}.wait .gi{background:var(--grey)}.done .gv{color:var(--green-d)}.pend .gv{color:#7a5616}.wait .gv{color:var(--muted)}
  .next{font-size:12.5px;color:var(--muted);margin-top:11px}.next b{color:var(--ink)}
  footer{text-align:center;padding:24px 0 0;font-size:12px;color:var(--muted)}footer b{color:var(--brand)}
  /* report */
  .sheet{max-width:760px;margin:22px auto;background:var(--card);border-radius:14px;overflow:hidden;box-shadow:0 10px 34px rgba(28,36,25,.14)}
  .rtop{background:var(--brand);color:#fff;padding:24px 30px}.rtop .logo{font-size:17px;font-weight:700}.rtop h1{font-size:24px;font-weight:680;margin:10px 0 4px}.rtop p{font-size:13.5px;color:rgba(255,255,255,.82)}
  .rbody{padding:24px 30px 16px}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}@media(max-width:620px){.stats{grid-template-columns:repeat(2,1fr)}}
  .stat .v{font-size:30px;font-weight:720;letter-spacing:-.02em;color:var(--brand-d)}.stat .v.ac{color:var(--green)}.stat .l{font-size:12.5px;color:var(--muted);margin-top:1px;line-height:1.35}
  .rh{font-size:12px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);margin:24px 0 11px}
  .did li{font-size:14px;margin-bottom:8px;list-style:none;padding-left:22px;position:relative}.did li::before{content:"✓";position:absolute;left:0;color:var(--green);font-weight:700}
  .rely{background:#f1f8f2;border:1px solid #cfe6d4;border-radius:12px;padding:16px 18px}.rg{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}@media(max-width:620px){.rg{grid-template-columns:1fr}}
  .rv{font-size:17px;font-weight:680;color:var(--green-d)}.rl{font-size:12px;color:var(--muted)}.rline{font-size:12.5px;color:#3a4a3a;margin-top:12px;border-top:1px solid #d7e8da;padding-top:11px}
  .rfoot{padding:18px 30px 24px;font-size:12px;color:var(--muted);border-top:1px solid var(--line)}.rfoot b{color:var(--brand)}
  .hidden{display:none}
  `;
  var s = document.createElement("style"); s.textContent = CSS; document.head.appendChild(s);

  // ---- renderers -----------------------------------------------------------
  function renderIndex(el) {
    el.innerHTML =
      '<div class="top"><div class="wrap"><div class="logo">' + esc(D.client) + ' × yourco</div>' +
      '<h1>Your setup, end to end</h1><p>' + esc(D.tagline) + '</p></div></div>' +
      '<div class="wrap"><div class="steps">' +
      (D.steps || []).map(function (st) {
        var inner = '<div class="n">' + st.n + '</div><div class="tx"><div class="tt">' + esc(st.title) +
          '</div><div class="ds">' + esc(st.desc) + '</div></div>' + (st.flow ? "" : '<div class="arr">→</div>');
        return st.flow ? '<div class="step flow">' + inner + '</div>'
                       : '<a class="step" href="' + esc(st.href) + '">' + inner + '</a>';
      }).join("") +
      '</div><div class="note">These are mockups on sample data — nothing here is live, and nothing was sent.<br>' +
      'The real build wires this to your tools, your number, and your mailbox. Built &amp; run by <b>yourco</b>.</div></div>';
  }

  function renderApproval(el) {
    var a = D.approval || {}, items = a.items || [];
    var cards = items.map(function (it, i) {
      var amt = it.locked ? '<div class="amt">🔒 <div><div class="v">' + esc(it.locked) + '</div><div class="s">' +
        esc(it.lockedSub || "") + '</div></div><span class="tag">locked</span></div>' : "";
      var sms = it.sms ? '<div style="margin-top:13px"><div class="lbl">Text to the client</div><div class="bubble">' + esc(it.sms) + '</div></div>' : "";
      var tog = it.together ? '<div class="together">✉️＋💬 ' + esc(it.together) + '</div>' : "";
      return '<div class="req" data-card><div class="rt">' + esc(it.kind) + ' → <b>' + esc(it.to) + '</b>' +
        (it.sub ? '<br>' + esc(it.sub) : "") + '</div>' + amt +
        '<div class="msg"><div class="lbl">Message to send</div><div class="email">' + esc(it.email) + '</div>' + sms + tog +
        '<div class="acts" style="margin-top:14px"><button class="btn approve" data-ok>Approve &amp; send</button>' +
        '<div class="row2"><button class="btn ghost" data-edit>Edit</button><button class="btn decline" data-no>Decline</button></div></div></div></div>';
    }).join("");
    el.innerHTML = '<div class="center"><div class="phone"><div class="bar"><span class="logo">' + esc(D.client) +
      '</span><span class="secure">🔒 secure link</span></div><div class="body"><div class="lede">Hi ' + esc(a.approver || "there") +
      ' — ' + esc(a.intro || "ready for your okay") + '.</div><div class="h">Approve before it <b>sends</b>.</div>' +
      '<div class="count" id="cnt">' + items.length + ' waiting on you</div>' + cards +
      '<div class="note" style="margin-top:6px">Nothing sends until you tap. The amount is computed and can\'t be changed here.<br>Built &amp; run by <b>yourco</b></div>' +
      '</div></div></div>';
    var left = items.length, cnt = document.getElementById("cnt");
    [].forEach.call(el.querySelectorAll("[data-card]"), function (c) {
      function done(ok) { if (c.dataset.done) return; c.dataset.done = 1; left--;
        c.innerHTML = '<div class="resolved ' + (ok ? "ok" : "no") + '">' + (ok ? "✓ Approved — sending now. (logged · " +
          new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }) + ")" : "✕ Declined — not sent; back to your team.") + '</div>';
        cnt.textContent = left > 0 ? left + " waiting on you" : "All caught up — nothing waiting on you."; }
      c.querySelector("[data-ok]").onclick = function () { done(true); };
      c.querySelector("[data-no]").onclick = function () { done(false); };
      var eb = c.querySelector("[data-edit]"); if (eb) eb.onclick = function () {
        var v = c.querySelector(".email"); var ta = document.createElement("textarea");
        ta.value = v.innerText; ta.style.cssText = "width:100%;min-height:170px;font:inherit;font-size:13.5px;border:1px solid var(--brand);border-radius:9px;padding:10px";
        v.replaceWith(ta); eb.textContent = "Done"; eb.onclick = function () { var nv = document.createElement("div"); nv.className = "email"; nv.textContent = ta.value; ta.replaceWith(nv); eb.textContent = "Edit"; };
      };
    });
  }

  function renderBoard(el) {
    var b = D.board || {};
    el.innerHTML = '<div class="btop"><div class="wrap"><span class="logo">' + esc(D.client) + '</span><span class="sub">' +
      esc(b.title || "jobs in flight") + '</span><span class="live"><span class="pulse"></span>watched live by yourco</span></div></div><div class="wrap">' +
      '<div class="metrics">' + (b.metrics || []).map(function (m) { return '<div class="metric"><div class="v' + (m.accent ? " ac" : "") + '">' + esc(m.v) + '</div><div class="l">' + esc(m.l) + '</div></div>'; }).join("") + '</div>' +
      ((b.nudges && b.nudges.length) ? '<div class="nudge"><h3>⚠ Needs a nudge</h3>' + b.nudges.map(function (n) { return '<div class="it">• ' + n + '</div>'; }).join("") + '</div>' : "") +
      '<h2 class="sec">Active jobs</h2>' +
      (b.jobs || []).map(function (j) {
        return '<div class="job' + (j.greenlit ? " go" : "") + '"><div class="jh"><span class="jn">' + esc(j.name) + '</span><span class="jp">' + esc(j.project) +
          '</span><span class="jt">' + esc(j.total) + '</span><span class="badge ' + esc(j.badgeClass || "run") + '" style="margin-left:auto">' + esc(j.badge) + '</span></div>' +
          '<div class="gates">' + (j.gates || []).map(function (g) { var ic = g.state === "done" ? "✓" : "…";
            return '<div class="gate ' + esc(g.state) + '"><div class="gl">' + esc(g.label) + '</div><div class="gv"><span class="gi">' + ic + '</span> ' + esc(g.text) + '</div></div>'; }).join("") + '</div>' +
          '<div class="next"><b>Next:</b> ' + esc(j.next) + '</div></div>';
      }).join("") +
      '<footer>Mockup on sample data · every send was approved by a human · built &amp; run by <b>yourco</b></footer></div>';
  }

  function renderReport(el) {
    var r = D.report || {};
    el.innerHTML = '<div class="sheet"><div class="rtop"><div class="logo">' + esc(D.client) + '</div><h1>' + esc(D.employee || "Your digital employee") +
      ' — ' + esc(r.period || "") + ' report</h1><p>What it did this month, and how reliably. Prepared by yourco.</p></div><div class="rbody">' +
      '<div class="stats">' + (r.stats || []).map(function (s) { return '<div class="stat"><div class="v' + (s.accent ? " ac" : "") + '">' + esc(s.v) + '</div><div class="l">' + esc(s.l) + '</div></div>'; }).join("") + '</div>' +
      '<div class="rh">What it handled</div><ul class="did">' + (r.did || []).map(function (d) { return '<li>' + esc(d) + '</li>'; }).join("") + '</ul>' +
      '<div class="rh">Reliability — the part you\'re paying for</div><div class="rely"><div class="rg">' +
      (r.reliability || []).map(function (x) { return '<div><div class="rv">' + esc(x.v) + '</div><div class="rl">' + esc(x.l) + '</div></div>'; }).join("") +
      '</div><div class="rline">' + esc(r.reliabilityLine || "") + '</div></div></div>' +
      '<div class="rfoot">Sample data · your employee, your email, your number — owned by you · built &amp; run by <b>yourco</b></div></div>';
  }

  var R = { index: renderIndex, approval: renderApproval, board: renderBoard, report: renderReport };
  function go() { var page = document.body.getAttribute("data-page"); var el = document.getElementById("app");
    if (el && R[page]) R[page](el); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", go); else go();
})();
