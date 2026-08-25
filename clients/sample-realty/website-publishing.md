# Publishing to SampleRealtyteam.com — what's needed

> **Status: BLOCKED on one DNS record and one decision about who hosts.**
> The builder side is finished and tested. Nothing here has been requested from Sample Realty yet.
> Sample Realty is a prospect — see `_README.md`. Do not send this until that's resolved.

## The short version

Kimi builds a cinematic tour and a listing page inside the Listing Kit Builder today. Both are finished, real, and self-contained. What she can't do is put them on the internet — a file on a laptop can't publish itself.

One button in the builder closes that gap. It needs two things that only Sample Realty can give:

1. **A subdomain** — one DNS record pointing `listings.SampleRealtyteam.com` at the publisher
2. **A decision on who runs the publisher** — the small service that receives a page and serves it

Everything else is built.

---

## 1. The DNS ask (for whoever runs the website)

> We'd like to add a subdomain for property tours and listing pages:
>
> **Record:** `CNAME` · **Name:** `listings` · **Value:** *(provided once the host is chosen)*
>
> This creates `listings.SampleRealtyteam.com` as a separate address. It does **not** touch, move, redirect or change the existing website in any way — the main site keeps serving exactly as it does now. It can be removed at any time by deleting the one record, and nothing on the current site would be affected.

That's the whole request. It's deliberately narrow: no access to her existing site, no hosting migration, no CMS credentials, nothing that can break what's already working. If the answer is no, the fallback is hosting the same pages on a URL we own and linking to them — worse for her brand, identical for the buyer.

## 2. Who runs the publisher

The subdomain has to point *somewhere*. That somewhere is a small service that accepts a finished page and serves it. Three options, in the order I'd argue for them:

| | Who operates it | Notes |
|---|---|---|
| **yourco runs it** | yourco | Fastest. Ties hosting and uptime to an yourco engagement — appropriate once signed, premature before. Small ongoing cost, and an obligation that outlives the demo. |
| **Her existing web host** | Her web person | Cleanest ownership. Depends entirely on what her site runs on and whether her web person will take it. Unknown until asked. |
| **Her own Cloudflare/Netlify account** | Sample Realty | She owns everything, yourco configures it. Slowest to set up, best long-term. |

**This is a commercial decision, not a technical one.** All three work. It should not be made before Stage 0.

---

## 3. What the publisher has to do

Small enough to be one Cloudflare Worker plus a bucket. Proven shape — same as Sample Product.

**Endpoint:** `POST {host}/publish`

```
Authorization: Bearer <per-agent key>
Content-Type: application/json

{ "slug":    "listing/2304-highland-forest-drive",
  "kind":    "page" | "tour",
  "address": "2304 Highland Forest Drive",
  "city":    "Yourtown",
  "html":    "<!doctype html>…"     // fully self-contained, photos embedded
}
```

**Response:** `200 {"url": "https://listings.SampleRealtyteam.com/listing/2304-highland-forest-drive"}`

Requirements:

- **Store and serve** the HTML at the slug. Republishing the same slug replaces it.
- **CORS** — the builder posts from a local file or a browser tab, so the Worker must send `Access-Control-Allow-Origin` and answer the preflight. Miss this and every publish fails with a network error that looks like the internet is down.
- **Size** — payloads run 150–400 KB because photos are embedded. Allow 10 MB.
- **Auth** — a per-agent bearer key, revocable independently. `401` on a bad key; the builder already reports that specifically.
- **Unpublish** — `DELETE /publish/{slug}` with the same bearer key. **Wired and tested in the builder.** Return `200` on success; `404` is treated as already-gone, not an error.
- **No listing index.** Pages are reachable by link only. An auto-generated "all listings" page at a brokerage subdomain drifts stale and starts making claims nobody is maintaining.

## 4. Security

- The key lives in the agent's browser, nowhere else. It is **not** in the builder file — a builder file can be emailed around safely; a key inside one cannot.
- Anyone holding the key can publish to the subdomain. It's a password. If the laptop is lost or an assistant leaves, rotate it.
- Keys are per-agent so one can be revoked without disturbing anyone else.

## 5. What the builder already refuses to publish

Publishing is a one-way door — it puts property marketing on the public internet under her brokerage's name. The button will not fire until:

- The **address** and **city** are filled in (the address becomes the web address)
- At least one **photo** exists (both pages are built from them)
- The **fair-housing screen is clear** — any flagged phrase blocks the publish and is named
- The **disclaimer line** is present

Then it shows the exact URL and asks for confirmation before anything leaves the browser. Publishing is always a deliberate human action: per the autonomy matrix this sits at **R1**, and website publishing may only earn autonomy after a clean streak — never on day one.

## 6. Keeping a published page honest

A *Just Listed* page still live after closing is the failure that costs credibility rather than time. Three layers, because each one alone fails:

**1. Status drives the page.** Every listing carries a status — Active / Under contract / Sold / Withdrawn. Changing it acts immediately: *Under contract* offers to republish with the corrected banner; *Sold* or *Withdrawn* offers to **take the page down**. A red banner sits above the preview whenever the live page disagrees with the listing, with the fix one click away, and every other saved listing is checked on open — the stale one is by definition the one she isn't looking at.

**2. The page expires on its own.** Every published page carries an expiry (**90 days**, reset on each republish). Past it, the page hides the listing and shows a short "no longer current, please get in touch" notice with her name and number. This is the layer that survives everything else failing — a page nobody revisits stops claiming a status forever, even if the builder is never opened again and the publisher never hears from anyone. Verified: fresh renders the listing, expired renders the notice.

**3. The publisher is the real watchdog — and it isn't built.** Layers 1 and 2 both run in a browser. A file on a shut laptop can't take anything down, and a self-expiring page still shows a stale status right up until its expiry. The durable version belongs on the publisher: a scheduled check that reads listing status from the MLS feed and retires pages without anyone remembering. **That needs the Canopy feed access described above** — the same credential the MLS fact-check needs. Until then, layers 1 and 2 are the honest ceiling and should be described as such.

## 7. Still open

- **Brokerage identification.** The page carries the firm name, disclaimer and Equal Housing Opportunity in the footer. **NC/SC advertising rules need a compliance read before anything goes public** (Ray) — the current footer is a reasonable default, not a verified one.
- **Real lead capture.** The enquiry form is `mailto:` today, which works with no backend but records nothing. Once a publisher exists, the same service should accept form posts so every enquiry is captured whether or not the buyer finishes the email — that's also the hook speed-to-lead needs.
