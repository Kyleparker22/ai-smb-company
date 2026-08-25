import puppeteer from 'puppeteer-core';
const CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chans=['atlas','bella','bird','brett','charles','david','harry','janice','jim','katie','kemba','kimi','Reed','kolby','kori','kortney','luka','mario','michelle','pickle','polo','rafi','ray','reilly','sadie','webb'];
const html=`<html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1600px;height:900px;background:#0F1226;color:#F4EFE6;
 font-family:-apple-system,system-ui,sans-serif;padding:64px 84px;display:flex;flex-direction:column}
.k{font-family:ui-monospace,Menlo,monospace;font-size:15px;letter-spacing:.22em;text-transform:uppercase;color:#D4B27A}
h1{font-family:Georgia,serif;font-size:46px;font-weight:400;margin:14px 0 6px;letter-spacing:-.01em}
.sub{font-size:20px;color:rgba(244,239,230,.66);margin-bottom:30px;max-width:1050px;line-height:1.45}
.grid{display:grid;grid-template-columns:repeat(7,1fr);gap:9px;margin-bottom:26px}
.ch{font-family:ui-monospace,Menlo,monospace;font-size:14.5px;color:rgba(244,239,230,.82);
 background:#1b2140;border:1px solid rgba(244,239,230,.14);border-radius:3px;padding:9px 8px;text-align:center}
.ch.all{background:#B8965A;color:#0F1226;border-color:#B8965A;font-weight:600}
.rows{display:flex;flex-direction:column;gap:13px;border-top:1px solid rgba(244,239,230,.16);padding-top:22px}
.r{display:grid;grid-template-columns:250px 1fr;gap:22px;align-items:baseline}
.r .l{font-family:ui-monospace,Menlo,monospace;font-size:13.5px;color:#D4B27A;letter-spacing:.06em;text-transform:uppercase}
.r .v{font-size:19px;line-height:1.4;color:rgba(244,239,230,.88)}
.foot{margin-top:auto;font-family:ui-monospace,Menlo,monospace;font-size:13px;color:rgba(244,239,230,.42)}
</style></head><body>
<div class="k">The control surface</div>
<h1>Every agent has its own Slack channel.</h1>
<div class="sub">Its work lands there — scannable, auditable, in one place. And the Founder can command any agent in its channel and get the answer back as that agent.</div>
<div class="grid">${chans.map(c=>`<div class="ch">#${c}</div>`).join('')}<div class="ch all">#all-yourco</div></div>
<div class="rows">
 <div class="r"><div class="l">Posts</div><div class="v">Each agent to its own channel · the daily digest to <b>#all-yourco</b></div></div>
 <div class="r"><div class="l">Commands</div><div class="v">the Founder types in the channel, the agent replies as itself — the Founder-only allowlist</div></div>
 <div class="r"><div class="l">The gate holds</div><div class="v">Draft, read and post are allowed. <b>Send, delete and shell are denied</b> at the infrastructure level</div></div>
</div>
<div class="foot">Diagram — the channel map from runtime/slack-channels.md. Not a screenshot.</div>
</body></html>`;
const b=await puppeteer.launch({executablePath:CHROME,headless:'new'});
const p=await b.newPage(); await p.setViewport({width:1600,height:900,deviceScaleFactor:2});
await p.setContent(html,{waitUntil:'load'}); await new Promise(r=>setTimeout(r,300));
await p.screenshot({path:'cards/7d-slack.png'}); await b.close(); console.log('slack card rendered');
