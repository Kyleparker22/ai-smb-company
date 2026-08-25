/* Shared front-end helpers for the pre-build verticals.

   The one rule this file exists for: a value the server could not compute
   arrives as {_missing: "<why>"} and is rendered as `unmeasured — <why>`.
   There is no code path here that turns a missing value into 0. */

const API = {
  async get(p) { const r = await fetch(p); return r.json(); },
  async post(p, body) {
    const r = await fetch(p, { method: 'POST', headers: { 'Content-Type': 'application/json' },
                               body: JSON.stringify(body || {}) });
    return r.json();
  }
};

const fmt = {
  money: v => v == null ? null : '$' + Math.round(v).toLocaleString(),
  money2: v => v == null ? null : '$' + v.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
  num: v => v == null ? null : v.toLocaleString(),
  pct: v => v == null ? null : (v * 100).toFixed(1) + '%',
  hours: v => v == null ? null : v.toFixed(1) + 'h',
  when(iso) {
    if (!iso) return '—';
    const d = new Date(iso), now = new Date();
    const mins = Math.round((now - d) / 60000);
    if (Math.abs(mins) < 60) return mins <= 0 ? `in ${-mins}m` : `${mins}m ago`;
    const hrs = Math.round(mins / 60);
    if (Math.abs(hrs) < 48) return hrs <= 0 ? `in ${-hrs}h` : `${hrs}h ago`;
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  },
  date: iso => iso ? new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : '—',
  stamp: iso => iso ? new Date(iso).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : '—'
};

/* the refusal renderer — used everywhere a number could be absent */
function blank(reason) {
  return `<span class="blank" title="${esc(reason || 'not recorded')}">unmeasured — ${esc(reason || 'not recorded')}</span>`;
}

/* val(obj, 'field', formatter) → formatted value, or the labelled blank */
function val(obj, field, f) {
  if (obj == null) return blank('not recorded');
  if (typeof obj !== 'object') return f ? f(obj) : String(obj);
  if (obj._missing != null && obj[field] == null) return blank(obj._missing);
  const v = obj[field];
  if (v == null) return blank('not recorded');
  return f ? f(v) : String(v);
}

const esc = s => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/* ---------------------------------------------------------------- pieces */

function panel(title, note, bodyHtml, flush) {
  return `<div class="panel"><h2>${esc(title)}${note ? `<span class="note">${esc(note)}</span>` : ''}</h2>
          <div class="body${flush ? ' flush' : ''}">${bodyHtml}</div></div>`;
}

function stat(k, v, foot, cls) {
  return `<div class="stat ${cls || ''}"><div class="k">${esc(k)}</div>
          <div class="v">${v == null ? blank('not recorded') : v}</div>
          ${foot ? `<div class="f">${foot}</div>` : ''}</div>`;
}

function table(cols, rows, rowFn) {
  if (!rows || !rows.length) return `<div class="body muted">Nothing here right now.</div>`;
  const head = cols.map(c => `<th class="${c.num ? 'num' : ''}">${esc(c.label)}</th>`).join('');
  const body = rows.map((r, i) => `<tr>${rowFn(r, i)}</tr>`).join('');
  return `<div class="scroll"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

function pill(text, cls) { return `<span class="pill ${cls || ''}">${esc(text)}</span>`; }

function rungPill(r) {
  const cls = { R0: '', R1: 'warn', R2: 'brand', R3: 'good' }[r] || 'bad';
  return `<span class="pill rung ${cls}">${esc(r || 'R?')}</span>`;
}

/* ---------------------------------------------------------------- the shared views */

function renderRoi(roi) {
  const rows = roi.lines.map(l => {
    const v = l.value == null ? blank(l._missing || 'not recorded')
                              : (l.kind === 'time_saved' && l.unit === 'hours' ? fmt.num(l.value) + ' h' : fmt.money(l.value));
    return `<tr><td><div class="strong">${esc(l.label)}</div>
      <div class="why mono">${esc(l.formula)}</div>
      ${l.assumption ? `<div class="why">assumption: ${esc(l.assumption)}</div>` : ''}
      ${l.note ? `<div class="why">${esc(l.note)}</div>` : ''}</td>
      <td>${pill(l.kind.replace('_', ' '), l.kind === 'scenario' ? 'warn' : l.kind === 'revenue' ? 'good' : '')}</td>
      <td class="num strong">${v}</td></tr>`;
  }).join('');
  const t = roi.totals;
  const totalRow = k => t[k].total == null
    ? `<tr><td colspan="2" class="muted">${k.replace('_', ' ')} subtotal</td><td class="num">${blank(`${t[k].blank} line(s) blank`)}</td></tr>`
    : `<tr><td colspan="2" class="strong">${k.replace('_', ' ')} subtotal${t[k].blank ? ` <span class="why">(${t[k].blank} line blank, excluded)</span>` : ''}</td>
       <td class="num strong">${k === 'time_saved' ? fmt.money(t[k].total) : fmt.money(t[k].total)}</td></tr>`;
  return panel(roi.title, 'computed from your numbers',
    `<div class="banner warn">${esc(roi.label)}</div>
     <div class="scroll"><table><thead><tr><th>Line</th><th>Kind</th><th class="num">Value / yr</th></tr></thead>
     <tbody>${rows}
     ${['revenue', 'cash_timing', 'time_saved', 'scenario'].filter(k => t[k].lines || t[k].blank).map(totalRow).join('')}
     </tbody></table></div>
     <ul class="reasons">${roi.rules.map(r => `<li>${esc(r)}</li>`).join('')}</ul>`, false);
}

function renderEvents(events, limit) {
  const rows = (events || []).slice(-(limit || 40)).reverse();
  return panel('Audit log', 'append-only — a correction is a new event, never an edit',
    table([{ label: 'When' }, { label: 'Action' }, { label: 'Actor' }, { label: 'Rung' }, { label: 'Subject' }],
      rows, e => `<td class="log at">${fmt.stamp(e.at)}</td>
        <td class="log">${esc(e.kind)}</td>
        <td class="log">${esc(e.actor)}</td>
        <td>${rungPill(e.rung)}</td>
        <td class="log muted">${esc(e.subject || '')}</td>`), true);
}

function renderAutomation(a) {
  if (a && a._missing) return stat('Automation rate', null, esc(a._missing));
  return stat('Automation rate', fmt.pct(a.rate),
    `${a.autonomous} of ${a.moving} pipeline-moving actions ran without a human · counted from the log`);
}

function renderAutonomy(matrix) {
  const rows = Object.entries(matrix).map(([k, v]) =>
    `<td class="mono">${esc(k)}</td><td>${rungPill(v.rung)}</td>
     <td class="why">${esc(v.reason)}</td>
     <td>${v.never_promote ? pill('never promotes', 'bad') : (v.limit != null ? pill('limit ' + v.limit) : '')}</td>`);
  return panel('Autonomy matrix', 'every action states its rung and why it sits there',
    table([{ label: 'Action' }, { label: 'Rung' }, { label: 'Why' }, { label: '' }],
      Object.entries(matrix), ([k, v]) =>
      `<td class="mono">${esc(k)}</td><td>${rungPill(v.rung)}</td>
       <td class="why">${esc(v.reason)}</td>
       <td>${v.never_promote ? pill('never promotes', 'bad') : (v.limit != null ? pill('limit ' + v.limit) : '')}</td>`), true);
}

function renderEval(e) {
  if (!e || e._missing) return panel('Eval', '', `<div class="muted">${blank(e ? e._missing : 'no eval run')}</div>`);
  const cls = e.costly_missed > 0 ? 'alert' : '';
  return panel(`Eval — ${e.name}`, `${e.n} labelled cases`,
    `<div class="grid">
      ${stat('Accuracy', fmt.pct(e.accuracy), 'all classes')}
      ${stat(`Recall on "${e.costly_label}"`, e.costly_recall == null ? null : fmt.pct(e.costly_recall),
        esc(e.costly_note), cls)}
      ${stat('Missed', fmt.num(e.costly_missed), 'the error that actually costs money', cls)}
      ${stat('False alarms', fmt.num(e.costly_false_alarms), 'cheap by comparison — deliberately')}
     </div>
     ${e.misses && e.misses.length ? `<div class="why" style="margin-top:10px">first misses: ${e.misses.slice(0, 5).map(m => `<span class="mono">${esc(String(m.input).slice(0, 60))}</span> → got ${esc(m.got)}, expected ${esc(m.expected)}`).join(' · ')}</div>` : ''}`);
}

function renderApprovals(list, onDecide) {
  if (!list || !list.length) return panel('Approval queue', 'the R1 floor', `<div class="muted">Nothing waiting on you.</div>`);
  return panel('Approval queue', `${list.length} waiting on a human`,
    table([{ label: 'Action' }, { label: 'What' }, { label: 'Why gated' }, { label: '' }], list,
      a => `<td class="mono">${esc(a.action)}</td>
        <td>${esc(a.detail && (a.detail.summary || a.detail.preview) || a.subject || '')}</td>
        <td class="why">${esc(a.reason)}</td>
        <td class="right"><button class="act primary" onclick="${onDecide}('${a.id}',true)">Approve</button>
        <button class="act" onclick="${onDecide}('${a.id}',false)">Reject</button></td>`), true);
}

/* tabs */
function tabs(names, onto) {
  const nav = document.querySelector('nav.tabs');
  nav.innerHTML = names.map((n, i) => `<button data-v="${n.id}" class="${i === 0 ? 'on' : ''}">${esc(n.label)}</button>`).join('');
  nav.addEventListener('click', e => {
    const b = e.target.closest('button'); if (!b) return;
    nav.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
    document.querySelectorAll('section.view').forEach(s => s.classList.toggle('on', s.id === 'v-' + b.dataset.v));
    if (onto) onto(b.dataset.v);
  });
}
