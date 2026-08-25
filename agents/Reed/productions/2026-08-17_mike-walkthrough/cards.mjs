import puppeteer from 'puppeteer-core';
import { mkdirSync } from 'fs';
mkdirSync('cards',{recursive:true});
const CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const S=(t,sub,kicker='')=>`<html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1600px;height:900px;background:#0F1226;color:#F4EFE6;
 font-family:Georgia,'Iowan Old Style',serif;display:flex;flex-direction:column;
 align-items:center;justify-content:center;text-align:center;padding:0 130px}
.k{font-family:ui-monospace,Menlo,monospace;font-size:17px;letter-spacing:.24em;
 text-transform:uppercase;color:#D4B27A;margin-bottom:30px}
h1{font-size:66px;font-weight:400;line-height:1.13;letter-spacing:-.015em;max-width:1180px}
.r{width:78px;height:2px;background:#B8965A;margin:34px 0}
p{font-family:-apple-system,system-ui,sans-serif;font-size:25px;line-height:1.5;
 color:rgba(244,239,230,.70);max-width:940px}
</style></head><body>
${kicker?`<div class="k">${kicker}</div>`:''}
<h1>${t}</h1>${sub?`<div class="r"></div><p>${sub}</p>`:''}
</body></html>`;

const cards=[
 ['01-title', S('yourco','A boutique AI company that diagnoses how a business really runs — then builds and <em>operates</em> the system that runs it.','for Mike · 17 August 2026')],
 ['08-honest', S('Everything you just saw is built.','$0 revenue · 0 clients · 0 audits delivered · 18 of 21 deals never contacted · 13 legal gates open, no counsel engaged','Where it actually stands')],
 ['09-end', S('The software is real.<br>The business hasn’t started.','Both halves are true. The second one is the work.','')],
];
const b=await puppeteer.launch({executablePath:CHROME,headless:'new'});
const p=await b.newPage(); await p.setViewport({width:1600,height:900,deviceScaleFactor:2});
for(const [n,html] of cards){ await p.setContent(html,{waitUntil:'load'});
  await new Promise(r=>setTimeout(r,300));
  await p.screenshot({path:`cards/${n}.png`}); console.log('  card',n); }
await b.close();
