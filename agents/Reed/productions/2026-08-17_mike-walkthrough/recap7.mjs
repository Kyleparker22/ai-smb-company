import puppeteer from 'puppeteer-core';
const CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const b=await puppeteer.launch({executablePath:CHROME,headless:'new',args:['--window-size=1600,900','--hide-scrollbars']});
const p=await b.newPage(); await p.setViewport({width:1600,height:900,deviceScaleFactor:2});
await p.goto('http://localhost:8790/',{waitUntil:'networkidle2'});
await p.evaluate(()=>{const s=document.createElement('style');s.textContent='#mel,.mel{display:none!important}';document.head.appendChild(s);});
await sleep(2500);
const rec=await p.screencast({path:'scenes/07-crm-deals.webm'});
// Ride down the live deal ladder — the 23 deals with their exits and next actions.
for (const y of [700,1400,2100,2800]) { await p.evaluate(t=>window.scrollTo({top:t,behavior:'smooth'}),y); await sleep(2300); }
await sleep(600); await rec.stop(); await b.close();
console.log('scene 07 recaptured');
