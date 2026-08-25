/* ─────────────────────────────────────────────────────────────────────────────
   Sample Realty — SINGLE SOURCE OF TRUTH for every listing on the site.

   The Listing Kit Builder (clients/sample-realty/tools/flyer-builder.html) emits an
   entry in EXACTLY this shape — build the listing there, switch to Listing Page,
   press "Copy the website entry", and paste the result below. Same slug scheme, so
   the builder's published page and this site's detail page resolve to one address.

   To add a listing (the whole flow):
     1. Drop its photos in  assets/listings/<slug>/photo-0.jpg … photo-N.jpg
        (photo-0 is the hero).
     2. Add ONE object to the top of the matching section below.
     Done — the homepage band, the listings page, and its detail page
     (listings/listing.html?id=<slug>) all update automatically.

   To mark a listing sold: change status to "sold", set price to the sold
   price, add soldNote. To remove: delete the object.

   status: "active" | "coming" | "lease" | "sold"
   Data + photos: Canopy MLS (Sample Contact is the listing agent).
   ──────────────────────────────────────────────────────────────────────────── */

window.PR_LISTINGS = [

  /* ── FOR SALE ─────────────────────────────────────────────────────────── */
  {
    slug: "1208-high-brook-drive",
    voScript: "Welcome to 1208 High Brook Drive, in Yourtown's Silver Creek community. This is a five-bedroom brick-front home on over half an acre — and it starts with a covered front porch made for rocking chairs and slow Southern evenings. Inside, the hardwoods have just been refinished in a light, modern finish, the paint is fresh throughout, and there's a full guest suite on the main level — perfect for visitors or multi-generational living. Thirty-two hundred square feet, a two-car garage, a community pool, and Cuthbertson schools. We're launching at seven twenty-four nine, with an open house Saturday, August eighth, from ten to noon. Prefer a private showing? Reach out and we'll walk it together — that's the boutique difference. Sample Realty Home and Land: we get you moving in the right direction.",
    status: "coming",
    badge: "Coming Soon · Aug 7",
    address: "1208 High Brook Drive",
    loc: "Silver Creek · Yourtown, ST 28173",
    price: "$724,900",
    facts: "5 beds · 3 baths · 3,202 sq ft · 0.56 acres",
    oh: "Open House — Sat, Aug 8 · 10:00 am – 12:00 pm",
    note: "Refinished hardwoods, fresh paint, main-level guest suite.",
    mls: "4409152",
    photoCount: 6,
    factrow: [["$724,900","List Price"],["5","Bedrooms"],["3","Baths"],["3,202","Square Feet"]],
    headline: "A brick-front classic on <em>half an acre.</em>",
    lede: "A covered front porch made for rocking chairs and peaceful Southern evenings — and a bright, freshly updated interior behind it.",
    body1: "Inside you'll find newly refinished hardwood floors in a modern light flat finish, fresh interior paint, and new carpet in the main-level guest suite. That sought-after main-level suite — with its own full bath — is ideal for visitors or multi-generational living.",
    body2: "Set on 0.56 acres in Yourtown's Silver Creek community, with a neighborhood pool and Cuthbertson schools. Built 2001 · 2-car garage · MLS #4409152.",
    features: [
      "Covered rocking-chair front porch",
      "Refinished hardwoods + fresh paint throughout",
      "Main-level guest suite with full bath",
      "0.56-acre lot in Silver Creek",
      "Community pool · Cuthbertson schools",
      "Open house Sat, Aug 8 · 10–12"
    ]
  },
  {
    slug: "12727-bullock-greenway",
    voScript: "This is 12727 Bullock Greenway Boulevard — Blakeney Greens, in the heart of South Yourtown. Step out the front door and you're walking to Blakeney's shops, restaurants, and groceries; step inside and you've got three stories of room to spread out. Luxury vinyl plank runs throughout, and the lower level gives you a flexible bedroom with its own full bath — guest suite, office, or media room, your call. Three bedrooms, three and a half baths, a one-car garage, and a community pool, listed at four thirty-five. Townhomes this close to Blakeney don't wait around. Book a showing on your schedule — evenings and weekends included — and we'll meet you there. Sample Realty Home and Land: we get you moving in the right direction.",
    status: "active",
    badge: "Active",
    address: "12727 Bullock Greenway Blvd",
    loc: "Blakeney Greens · Yourtown 28277",
    price: "$435,000",
    facts: "3 beds · 3.5 baths · 1,845 sq ft · townhome",
    note: "Steps from Blakeney shopping &amp; dining.",
    mls: "4394540",
    photoCount: 6,
    factrow: [["$435,000","List Price"],["3","Bedrooms"],["3.5","Baths"],["1,845","Square Feet"]],
    headline: "Steps from everything <em>Blakeney.</em>",
    lede: "One of South Yourtown's most sought-after locations — groceries, restaurants, boutiques, and seasonal events all within walking distance.",
    body1: "This spacious three-story townhome features luxury vinyl plank flooring throughout and a flexible lower-level bedroom with a full bath — ideal as a guest suite, office, or media room.",
    body2: "Blakeney Greens community with pool, one-car garage, built 2004. MLS #4394540.",
    features: [
      "Walk to Blakeney shopping &amp; dining",
      "Three-story plan — room to spread out",
      "Luxury vinyl plank flooring throughout",
      "Flexible lower-level bedroom + full bath",
      "One-car garage · community pool",
      "South Yourtown28277"
    ]
  },
  {
    slug: "9725-mattforest-circle",
    voScript: "Welcome to 9725 Mattforest Circle in Elizabeth Townes — Ballantyne, move-in ready. The kitchen's granite counters flow straight into a living area anchored by a gas-log fireplace you control from the couch. Upstairs, the primary suite has a fully renovated bath — floor-to-ceiling tiled shower, semi-frameless glass, new vanity. Two bedrooms, two and a half baths, fourteen hundred thirty-five square feet, with a one-car garage and a community pool — zoned for Hawk Ridge, Community House, and Ardrey Kell. Listed at three fifty-nine nine. If Ballantyne's been on your list, this is the one to see this week. Reach out and we'll open the door. Sample Realty Home and Land: we get you moving in the right direction.",
    status: "active",
    badge: "Active",
    address: "9725 Mattforest Circle",
    loc: "Elizabeth Townes · Ballantyne · Yourtown 28277",
    price: "$359,900",
    facts: "2 beds · 2.5 baths · 1,435 sq ft · townhome",
    note: "Move-in-ready, renovated primary bath.",
    mls: "4389671",
    photoCount: 6,
    factrow: [["$359,900","List Price"],["2","Bedrooms"],["2.5","Baths"],["1,435","Square Feet"]],
    headline: "Move-in-ready in the heart of <em>Ballantyne.</em>",
    lede: "A beautifully updated townhome with an open floor plan designed for comfortable living and entertaining.",
    body1: "The kitchen offers granite countertops and flows seamlessly into the living area, highlighted by a remote-controlled gas-log fireplace. The spacious primary suite features a fully renovated bathroom — stunning fully tiled shower, semi-frameless glass doors, and a new vanity.",
    body2: "Elizabeth Townes community with pool; Hawk Ridge / Community House / Ardrey Kell schools. Built 1999 · one-car garage · MLS #4389671.",
    features: [
      "Open floor plan, granite kitchen",
      "Gas-log fireplace with remote",
      "Fully renovated primary bath — tiled shower",
      "Semi-frameless glass + new vanity",
      "Community pool · Ardrey Kell schools",
      "Heart of Ballantyne, 28277"
    ]
  },
  {
    slug: "1210-sheldon-brook-lane",
    voScript: "This is 1210 Sheldon Brook Lane in Brookchase — Indian Land, just across the South Carolina line. Fresh updates everywhere you look: new carpet, fresh paint, quartz kitchen counters, updated lighting and hardware — and the appliances have all been replaced in recent years. Out back, an extended paver patio looks onto a landscaped treeline — morning coffee approved. Three bedrooms, two baths, and first-floor living, zoned for Indian Land's ten-out-of-ten-rated elementary school — all at two seventy-three five, with South Carolina's lighter tax bill working in your favor every month. Come see what your money buys on this side of the line. Sample Realty Home and Land: we get you moving in the right direction.",
    status: "active",
    badge: "Active",
    address: "1210 Sheldon Brook Lane",
    loc: "Brookchase · Fort Mill, SC 29707",
    price: "$273,500",
    facts: "3 beds · 2 baths · 1,130 sq ft · townhome",
    note: "Fresh updates, quartz counters, extended paver patio.",
    mls: "4383987",
    photoCount: 6,
    factrow: [["$273,500","List Price"],["3","Bedrooms"],["2","Baths"],["1,130","Square Feet"]],
    headline: "Fresh updates, <em>Indian Land</em> address.",
    lede: "A charming townhome with new carpet, fresh paint, quartz kitchen countertops, and updated lighting and hardware.",
    body1: "The floor plan offers ample first-floor living space, and the appliances have all been updated within the last few years. Outside, a beautiful extended paver patio overlooks a landscaped treeline.",
    body2: "Ideally located close to Indian Land's shopping and dining, zoned for the 10/10-rated Indian Land schools. Built 2006 · MLS #4383987.",
    features: [
      "Quartz kitchen counters + updated lighting",
      "New carpet and fresh paint",
      "Appliances updated in recent years",
      "Extended paver patio, landscaped treeline",
      "Indian Land schools (10/10 elementary)",
      "Minutes to shopping &amp; dining"
    ]
  },
  {
    slug: "11264-hyde-pointe-court",
    voScript: "Welcome to 11264 Hyde Pointe Court — a first-floor condo in Hyde Park, University City. No stairs, no wasted space: the upgraded kitchen with tiled backsplash opens straight into the family room, and the family room opens onto a covered patio made for unwinding. The primary bedroom brings a generous walk-in closet and its own full bath. Two bedrooms, two baths, community pool — at two twenty, it works two ways: a smart first home, or an investment in one of Yourtown's strongest rental corridors. Ask us about the numbers on both — and if you buy it as a rental, our property-management division will run it for you. Sample Realty Home and Land: we get you moving in the right direction.",
    status: "active",
    badge: "Active",
    address: "11264 Hyde Pointe Court",
    loc: "Hyde Park · Yourtown 28262",
    price: "$220,000",
    facts: "2 beds · 2 baths · 1,194 sq ft · first-floor condo",
    note: "Upgraded kitchen, covered patio — strong investment buy.",
    mls: "4354529",
    photoCount: 6,
    factrow: [["$220,000","List Price"],["2","Bedrooms"],["2","Baths"],["1,194","Square Feet"]],
    headline: "A first-floor condo that <em>works hard.</em>",
    lede: "Perfect first home or investment property — a beautiful first-floor condo in established Hyde Park.",
    body1: "LVP flooring runs through the main living areas, with upgraded kitchen cabinets and a tiled backsplash. The open-concept kitchen flows into the spacious family room, which opens to a covered patio — perfect for relaxing or entertaining.",
    body2: "The primary bedroom includes a generous walk-in closet and its own en-suite bathroom. Community pool; University City location. Built 2005 · MLS #4354529.",
    features: [
      "First-floor living — no stairs",
      "Upgraded kitchen, tiled backsplash",
      "Open concept to covered patio",
      "Primary suite with walk-in closet",
      "Community pool",
      "Investor-friendly — strong rental market"
    ]
  },

  /* ── FOR LEASE ────────────────────────────────────────────────────────── */
  {
    slug: "3524-donovan-place",
    status: "lease",
    badge: "For Lease",
    address: "3524 Donovan Place",
    loc: "Shannon Park · Yourtown 28215",
    price: "$2,600",
    priceSuffix: "/ month",
    facts: "4 beds · 2.5 baths · 2,002 sq ft · 12-month lease",
    note: "Split-level with fenced yard + bonus living space.",
    mls: "4395709",
    href: "donovan-place.html",   /* bespoke page — carries the cinematic tour */
    photoCount: 14,
    go: "View listing &amp; cinematic tour"
  },

  /* ── PENDING (buyer side) ─────────────────────────────────────────────── */
  {
    slug: "2275-whitebark-drive",
    status: "pending",
    badge: "Under Contract · Representing the Buyer",
    address: "2275 Whitebark Drive #148",
    loc: "The Pines at Sugar Creek · Indian Land, SC 29707",
    price: "$1,003,225",
    facts: "4 beds · 4.5 baths · 3,172 sq ft · new construction",
    note: "Toll Brothers \"William Elite\" — under construction, delivering 2026. Photos by Kimi from the buyer walk.",
    mls: "4401927",
    photoCount: 5,
    factrow: [["$1,003,225","Contract Price"],["4","Bedrooms"],["4.5","Baths"],["3,172","Square Feet"]],
    headline: "Built to order, watched <em>every step.</em>",
    lede: "We're representing the buyers on this Toll Brothers \"William Elite\" — a 1.5-story new build in The Pines at Sugar Creek, delivering 2026.",
    body1: "Buying new construction is its own discipline: pre-drywall walks, selection deadlines, builder-contract terms, and holding the builder to the punch list. We walk the site at every stage — these photos are from our construction visits, watching the details our buyers will live with.",
    body2: "Main-level living with a guest level up top, on 0.20 acres in Indian Land's Pines at Sugar Creek. Under contract · MLS #4401927.",
    features: [
      "Toll Brothers \"William Elite\" model",
      "1.5-story — primary living on the main",
      "New construction, delivering 2026",
      "Pre-drywall &amp; stage-by-stage walkthroughs by your agent",
      "0.20 acres · Lancaster County, SC",
      "Buyer representation, contract to keys"
    ]
  },

  /* ── RECENTLY SOLD ────────────────────────────────────────────────────── */
  {
    slug: "401-wingfoot-drive",
    status: "sold",
    badge: "Sold · June 2026",
    address: "401 Wingfoot Drive",
    loc: "Innisbrook at Firethorne · Yourtown, ST 28173",
    price: "Sold — $1,445,000",
    priceSuffix: "· over asking",
    facts: "5 beds · 4.5 baths · 4,446 sq ft · 0.95 acres",
    note: "Custom estate on nearly an acre of wooded grounds.",
    mls: "4350790",
    hero: "assets/listings/401-wingfoot-drive.jpg"
  },
  {
    slug: "7518-meadowgate-lane",
    status: "sold",
    badge: "Sold · July 2026",
    address: "7518 Meadowgate Lane",
    loc: "Weddington Chase · Marvin, ST 28173",
    price: "Sold — $1,200,000",
    facts: "6 beds · 5.5 baths · 5,398 sq ft · Marvin Ridge schools",
    note: "Under contract in 4 days.",
    mls: "4385632",
    hero: "assets/listings/7518-meadowgate-lane.jpg"
  }
];

/* Buyer-side closed sales (last 2 years, Canopy MLS). Kimi represented the
   BUYER — MLS photos belong to the listing side, so these render photo-free
   until Kimi supplies her own; drop photos in assets/listings/<slug>/ and
   add photoCount to promote one to a full card. */
window.PR_BUYER_SOLDS = [
  { address: "9413 Hinson Drive",        loc: "Sardis Forest · Yourtown, ST",      price: "$520,000" },
  { address: "16059 Harbor Hill Drive",  loc: "Chateau · Yourtown",           price: "$495,000" },
  { address: "405 Prine Place",          loc: "Brixton · Yourtown",           price: "$480,527" },
  { address: "436 Nathaniel Way",        loc: "Brixton · Yourtown",           price: "$449,999" },
  { address: "432 Nathaniel Way",        loc: "Brixton · Yourtown",           price: "$405,661" },
  { address: "6327 Cherry Blossom Circle", loc: "Sun City Carolina · Indian Land, SC", price: "$405,000" },
  { address: "14726 Inter Milan Way",    loc: "Riviera · Yourtown",           price: "$375,000" },
  { address: "7422 Larwill Lane",        loc: "Sutton Farms · Yourtown",      price: "$375,000" },
  { address: "4014 Ashby Lane",          loc: "Windsor Trace · Fort Mill, SC",     price: "$272,000" },
  { address: "1032 Eagles Nest Lane",    loc: "Hanover Place · Indian Land, SC",   price: "$271,000" },
  { address: "5208 Avon Court",          loc: "Windsor Trace · Fort Mill, SC",     price: "$260,500" }
];

/* Track record — computed from the firm's actual Canopy MLS closed data,
   Aug 2024–Aug 2026 (the "My Closed Listings (2 years)" export + the two
   2026 listing-side sales). Update when new closings land; the homepage
   stats band and results page read from here. */
window.PR_STATS = {
  closedTransactions: 19,          /* 17 closed (2-yr export, incl. leases) + Wingfoot + Meadowgate */
  closedVolume: "$6.9M+",          /* sum of closed sale prices, listing + buyer side */
  fastestContract: "4 days",       /* 7518 Meadowgate Ln — listed to under contract */
  overAsking: "0.4%",              /* 401 Wingfoot Dr — sold over list */
  years: "24+",
  source: "Canopy MLS closed data, Aug 2024 – Aug 2026"
};

/* Market pulse — refreshed monthly. AT LAUNCH: wire to the runtime's monthly
   market-pulse loop (median/DOM from Canopy for her zips + Freddie Mac PMMS
   rate). Values below are the Aug 2026 snapshot for the demo. */
window.PR_MARKET = {
  updated: "August 2026",
  medianClosed: "$405,000",        /* median of the firm's last-24-mo closed sales */
  medianNote: "median of our own last 24 months of closings",
  rate: "6.25%",                   /* 30-yr fixed, matches mortgage-tool default */
  rateNote: "30-year fixed, national average",
  fastest: "4 days",
  fastestNote: "our fastest listing-to-contract, 2026"
};

/* Shared card renderer. base = path prefix to the site root ("" on the
   homepage, "../" from /listings/). Returns HTML for one card. */
window.PR_renderCard = function (l, base) {
  const hero = l.hero ? base + l.hero
                      : base + "assets/listings/" + l.slug + "/photo-0.jpg";
  const href = l.status === "sold" ? null
             : base + "listings/" + (l.href || ("listing.html?id=" + l.slug));
  const badgeClass = { active: "active", coming: "coming", lease: "lease", sold: "sold", pending: "coming" }[l.status];
  const price = l.price
    ? '<div class="price">' + l.price + (l.priceSuffix ? ' <span>' + l.priceSuffix + '</span>' : '') + '</div>' : '';
  const go = href ? '<span class="go">' + (l.go || "View listing &amp; cinematic tour") + '</span>' : '';
  const oh = l.oh ? '<div class="oh">' + l.oh + '</div>' : '';
  const note = l.note ? '<div class="note">' + l.note + (l.mls ? " MLS #" + l.mls : "") + '</div>' : '';
  const inner =
    '<div class="photo"><div class="badge ' + badgeClass + '">' + l.badge + '</div>' +
    '<img src="' + hero + '" alt="' + l.address + " — " + l.loc + '" loading="lazy"/></div>' +
    '<div class="meta"><h3>' + l.address + '</h3>' +
    '<div class="loc">' + l.loc + '</div>' + price +
    '<div class="facts">' + l.facts + '</div>' + oh + go + note + '</div>';
  return href
    ? '<a class="card" href="' + href + '">' + inner + '</a>'
    : '<div class="card">' + inner + '</div>';
};
