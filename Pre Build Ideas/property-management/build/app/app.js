/* Property OS — shared client helpers. No dependencies, no build step. */

const API = {
  async get(p) { const r = await fetch('/api' + p, { headers: { accept: 'application/json' } }); return r.json(); },
  async post(p, body) {
    const r = await fetch('/api' + p, {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body || {})
    });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw Object.assign(new Error(j.error || 'request failed'), { payload: j });
    return j;
  }
};

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

/* Escape everything that reaches innerHTML. Resident-authored text and vendor
   names flow into every view here; one unescaped field is a stored XSS. */
const esc = s => String(s ?? '').replace(/[&<>"']/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const money = n => {
  if (n == null) return '—';
  const r = Math.round(n) || 0;      // normalises -0, which rendered "$-0"
  return '$' + r.toLocaleString('en-US');
};
const pct = n => n == null ? '—' : Math.round(n * 100) + '%';

function hrs(h) {
  if (h == null) return '—';
  if (h < 1) return Math.round(h * 60) + 'm';
  if (h < 48) return (h < 10 ? h.toFixed(1) : Math.round(h)) + 'h';
  return (h / 24).toFixed(1) + 'd';
}

function ago(iso) {
  if (!iso) return '—';
  const s = (Date.now() - new Date(iso)) / 1000;
  if (s < 60) return 'just now';
  if (s < 3600) return Math.floor(s / 60) + 'm ago';
  if (s < 86400) return Math.floor(s / 3600) + 'h ago';
  if (s < 2592000) return Math.floor(s / 86400) + 'd ago';
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

const dateOnly = s => s ? new Date(s + (s.length <= 10 ? 'T12:00:00' : ''))
  .toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '—';

const STATUS_LABEL = {
  submitted: 'Submitted', assigned: 'Assigned',
  in_progress: 'In progress', resolved: 'Resolved'
};
const STATUS_ORDER = ['submitted', 'assigned', 'in_progress', 'resolved'];

/* A value the system declined to compute renders as its reason — never as 0.
   This helper is the single place that rule is enforced client-side. */
function statOrMissing(obj, key) {
  if (!obj) return { missing: 'not computed yet' };
  if (obj._missing) return { missing: obj._missing };
  const v = obj[key];
  return v == null ? { missing: obj._missing || 'not enough data' } : { value: v };
}

function tile(label, res, sub, fmt = String) {
  const body = res.missing
    ? `<div class="v miss">${esc(res.missing)}</div>`
    : `<div class="v">${esc(fmt(res.value))}</div>` + (sub ? `<div class="s">${esc(sub)}</div>` : '');
  return `<div class="tile"><div class="k">${esc(label)}</div>${body}</div>`;
}

function toast(msg, ms = 2600) {
  let t = $('.toast');
  if (!t) { t = document.createElement('div'); t.className = 'toast'; document.body.appendChild(t); }
  t.textContent = msg;
  t.classList.add('on');
  clearTimeout(t._h);
  t._h = setTimeout(() => t.classList.remove('on'), ms);
}

function tracker(status, resolutionKind) {
  const i = STATUS_ORDER.indexOf(status);
  const finished = status === 'resolved';
  return '<div class="track">' + STATUS_ORDER.map((s, n) => {
    // A resolved request's final step is DONE, not "currently happening" —
    // it was rendering as the step number instead of a checkmark.
    const isDone = n < i || (finished && n === i);
    const cls = isDone ? 'done' : n === i ? 'now' : '';
    const label = (s === 'resolved' && resolutionKind === 'deflected') ? 'Solved by you' : STATUS_LABEL[s];
    const link = n < STATUS_ORDER.length - 1
      ? `<div class="link ${n < i ? 'done' : ''}"></div>` : '';
    return `<div class="node ${cls}"><div class="bead">${isDone ? '✓' : n + 1}</div>
      <div class="lbl">${esc(label)}</div></div>${link}`;
  }).join('') + '</div>';
}

function timeline(events) {
  if (!events || !events.length) return '<div class="muted small">No activity recorded.</div>';
  return '<div class="tl">' + events.map(e => {
    const isAgent = String(e.actor).startsWith('agent:');
    const who = isAgent ? e.actor.slice(6) + ' agent'
      : String(e.actor).startsWith('tenant:') ? 'resident' : 'staff';
    const d = e.detail || {};
    const bits = Object.entries(d)
      .filter(([k, v]) => !['action', 'autonomous'].includes(k) && v != null && v !== '' &&
        !(Array.isArray(v) && !v.length))
      .slice(0, 4)
      .map(([k, v]) => `${k.replace(/_/g, ' ')}: ${Array.isArray(v) ? v.join('; ') : v}`);
    return `<div class="tl-i ${isAgent ? 'agent' : 'human'}">
      <div class="b"></div>
      <div class="stack grow">
        <div class="row wrap-r" style="gap:7px">
          <strong style="font-size:13.5px">${esc(String(e.kind).replace(/_/g, ' '))}</strong>
          ${e.rung ? `<span class="pill mute tiny">${esc(e.rung)}</span>` : ''}
          <span class="tiny muted">${esc(who)} · ${esc(ago(e.at))}</span>
        </div>
        ${bits.length ? `<div class="tiny muted">${esc(bits.join(' · '))}</div>` : ''}
      </div></div>`;
  }).join('') + '</div>';
}

/* Theme: respect the OS by default, remember an explicit choice. */
(function theme() {
  const saved = localStorage.getItem('pos-theme');
  if (saved) document.documentElement.setAttribute('data-theme', saved);
  window.toggleTheme = () => {
    const cur = document.documentElement.getAttribute('data-theme')
      || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    const next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('pos-theme', next);
  };
})();

if ('serviceWorker' in navigator) {
  addEventListener('load', () => navigator.serviceWorker.register('/sw.js').catch(() => {}));
}

/* Dataset self-description. When an import mixes an operator's real book with
   illustrative activity, every page says so — a demo that can be mistaken for
   the real ledger is worse than no demo. */
(async function notice(){
  try{
    const r = await fetch('/api/notice', {headers:{accept:'application/json'}});
    const {notice} = await r.json();
    if(!notice) return;
    const el = document.createElement('div');
    el.id = 'dataset-notice';
    el.textContent = notice;
    el.style.cssText = 'position:sticky;top:0;z-index:9999;background:#7a2118;color:#fff;'
      + 'font:600 11px/1.5 system-ui,-apple-system,sans-serif;letter-spacing:.06em;'
      + 'text-transform:uppercase;text-align:center;padding:6px 14px';
    document.body.prepend(el);
  }catch(e){}
})();
