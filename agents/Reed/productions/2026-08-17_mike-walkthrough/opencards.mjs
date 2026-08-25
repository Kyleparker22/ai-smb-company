import puppeteer from 'puppeteer-core';
const CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const base=`*{margin:0;padding:0;box-sizing:border-box}
body{width:1600px;height:900px;background:#0F1226;color:#F4EFE6;font-family:-apple-system,system-ui,sans-serif;padding:62px 84px;display:flex;flex-direction:column}
.k{font-family:ui-monospace,Menlo,monospace;font-size:15px;letter-spacing:.22em;text-transform:uppercase;color:#D4B27A}
h1{font-family:Georgia,serif;font-size:46px;font-weight:400;margin:14px 0 34px;letter-spacing:-.01em}`;

const motion=`<html><head><meta charset="utf-8"><style>${base}
.flow{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:34px}
.st{background:#1b2140;border:1px solid rgba(244,239,230,.15);border-radius:3px;padding:22px 20px;position:relative}
.st .n{font-family:ui-monospace,Menlo,monospace;font-size:12px;color:#D4B27A;letter-spacing:.16em;text-transform:uppercase}
.st h2{font-family:Georgia,serif;font-size:27px;font-weight:400;margin:9px 0 8px}
.st p{font-size:16px;line-height:1.45;color:rgba(244,239,230,.7)}
.st.hero{background:#B8965A;border-color:#B8965A}
.st.hero .n{color:rgba(15,18,38,.66)} .st.hero h2,.st.hero p{color:#0F1226}
.st.hero p{color:rgba(15,18,38,.8)}
.line{border-top:1px solid rgba(244,239,230,.16);padding-top:22px;font-size:21px;line-height:1.5;color:rgba(244,239,230,.86)}
.line b{color:#D4B27A}
</style></head><body>
<div class="k">The motion</div><h1>Diagnose first. Then build it. Then run it.</h1>
<div class="flow">
 <div class="st hero"><div class="n">Step one · paid</div><h2>Audit</h2><p>A week learning how the business actually runs, and pricing where it leaks.</p></div>
 <div class="st"><div class="n">Step two</div><h2>Build</h2><p>A custom AI system scoped from what the audit found — not a template.</p></div>
 <div class="st"><div class="n">Step three</div><h2>Operate</h2><p>We run it. Reliability, evals, approvals and upgrades stay ours.</p></div>
 <div class="st"><div class="n">Then</div><h2>Expand</h2><p>One working capability becomes the next, inside an account that already trusts us.</p></div>
</div>
<div class="line">The client never touches a model, a token, or a server. <b>They buy an outcome, and we stay on the hook for it.</b></div>
</body></html>`;

const pillars=`<html><head><meta charset="utf-8"><style>${base}
.g{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:30px}
.p{background:#1b2140;border:1px solid rgba(244,239,230,.14);border-radius:3px;padding:17px 16px}
.p h3{font-family:Georgia,serif;font-size:22px;font-weight:400;margin-bottom:5px}
.p span{font-size:14.5px;color:rgba(244,239,230,.62);line-height:1.35;display:block}
.rows{display:flex;flex-direction:column;gap:12px;border-top:1px solid rgba(244,239,230,.16);padding-top:22px}
.r{display:grid;grid-template-columns:220px 1fr;gap:22px;align-items:baseline}
.r .l{font-family:ui-monospace,Menlo,monospace;font-size:13px;color:#D4B27A;letter-spacing:.06em;text-transform:uppercase}
.r .v{font-size:18.5px;line-height:1.42;color:rgba(244,239,230,.87)}
</style></head><body>
<div class="k">What we build for a client</div><h1>Eight areas of a business. We scope which from the audit.</h1>
<div class="g">
 <div class="p"><h3>Intake</h3><span>Calls, forms, after-hours — nothing missed</span></div>
 <div class="p"><h3>Sales</h3><span>Follow-up, quoting, proposals</span></div>
 <div class="p"><h3>Marketing</h3><span>Content and demand that actually ships</span></div>
 <div class="p"><h3>Customer</h3><span>Retention, reviews, recall</span></div>
 <div class="p"><h3>Operations</h3><span>Scheduling, dispatch, delivery</span></div>
 <div class="p"><h3>Back office</h3><span>Invoicing, AR, data entry</span></div>
 <div class="p"><h3>Company brain</h3><span>What the business knows, searchable</span></div>
 <div class="p"><h3>Training</h3><span>Onboarding and how-we-do-it</span></div>
</div>
<div class="rows">
 <div class="r"><div class="l">Three shapes</div><div class="v">A named digital employee · headless automation · or a client-facing AI product</div></div>
 <div class="r"><div class="l">How it's priced</div><div class="v">Flat monthly retainer — <b>we absorb every model cost</b>, so efficiency is our problem, not the invoice's</div></div>
</div>
</body></html>`;

const b=await puppeteer.launch({executablePath:CHROME,headless:'new'});
const p=await b.newPage(); await p.setViewport({width:1600,height:900,deviceScaleFactor:2});
for(const [n,h] of [['1b-motion',motion],['1c-pillars',pillars]]){
  await p.setContent(h,{waitUntil:'load'}); await new Promise(r=>setTimeout(r,300));
  await p.screenshot({path:`cards/${n}.png`}); console.log('  card',n); }
await b.close();
