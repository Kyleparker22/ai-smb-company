/* evidence.js — renders a claim only while the check behind it is fresh.
 *
 * Any element with data-claim="<id>" is filled from site-evidence.json (written by
 * runtime/site_evidence.py). If the claim is unproven, or its check has gone stale against the
 * READER's clock, the number is withheld and what is missing is printed in its place.
 *
 * The markup must never carry a fallback number. If this script fails to run, or the JSON cannot
 * be read, every bound element must degrade to "unproven" — a hardcoded number surviving a failed
 * check is exactly the frozen-marketing-site behaviour this whole mechanism exists to prevent.
 */
(function () {
  'use strict';

  var MISSING_FILE = 'the evidence file could not be read, so nothing here can be shown as proven';

  function daysBetween(a, b) { return Math.floor((b - a) / 86400000); }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  /* A claim renders in exactly one of two ways. There is no partial state, no "approximately",
     no last-known-good — those are the ways a stale number stays on a page looking alive. */
  function renderProven(node, claim) {
    node.classList.add('is-proven');
    node.classList.remove('is-dark');
    node.textContent = '';
    node.appendChild(el('span', 'claim-text', claim.text));
    var f = el('span', 'claim-foot');
    f.appendChild(el('span', 'claim-check', claim.detail || ''));
    f.appendChild(el('span', 'claim-src', 'verified ' + claim.verifiedOn));
    node.appendChild(f);
  }

  /* A dark claim shows its SUBJECT, never its statement with the value knocked out — a sentence
     rendered around a hole ("— deny rules have survived an attack") reads as a broken page rather
     than a deliberate refusal, and the refusal is the whole point. */
  function renderDark(node, claim, why) {
    node.classList.add('is-dark');
    node.classList.remove('is-proven');
    node.textContent = '';
    node.appendChild(el('span', 'claim-flag', 'unproven'));
    node.appendChild(el('span', 'claim-text',
      (claim && claim.subject) ? claim.subject : 'This claim'));
    node.appendChild(el('span', 'claim-missing', why));
    node.appendChild(el('span', 'claim-foot',
      'We would rather show you this than a number we cannot stand behind.'));
  }

  function apply(data) {
    var nodes = document.querySelectorAll('[data-claim]');
    if (!nodes.length) return;

    var byId = {};
    var generated = data && data.generatedAt ? new Date(data.generatedAt) : null;
    (data && data.claims ? data.claims : []).forEach(function (c) { byId[c.id] = c; });

    Array.prototype.forEach.call(nodes, function (node) {
      var claim = byId[node.getAttribute('data-claim')];

      if (!claim) { renderDark(node, null, 'no check is registered for this claim'); return; }
      if (claim.state !== 'proven') { renderDark(node, claim, claim.missing || 'the check did not pass'); return; }

      /* Freshness is judged against the reader's clock, not the generator's. That is what makes
         the page go dark on its own if the generator stops running. */
      if (!generated || isNaN(generated.getTime())) {
        renderDark(node, claim, 'the evidence file has no readable timestamp'); return;
      }
      var age = daysBetween(generated, new Date());
      if (age > claim.ttlDays) {
        renderDark(node, claim,
          'the check behind this last ran ' + age + ' days ago and is good for ' +
          claim.ttlDays + '. It has gone quiet, so the number is withheld.');
        return;
      }
      renderProven(node, claim);
    });
  }

  function fail(why) {
    Array.prototype.forEach.call(document.querySelectorAll('[data-claim]'), function (node) {
      renderDark(node, null, why);
    });
  }

  function boot() {
    fetch('site-evidence.json', { cache: 'no-store' })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(apply)
      .catch(function () { fail(MISSING_FILE); });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
