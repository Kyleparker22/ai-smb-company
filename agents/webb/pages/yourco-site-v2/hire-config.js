/* ============================================================================
   yourco — Ready-to-Hire catalog (the off-the-shelf, subscribe-and-go employees).
   Drives hire.html (the catalog) + hire-onboarding.html (the guided intake wizard).
   Decision: decisions/2026-06-16_two-motions-productized-employees.md
            + spec: processes/off-the-shelf-employees.md.

   These are the PRE-SCOPED, high-reliability patterns from the productization ladder —
   the ones that need only config (not custom scoping). Anything more custom routes to
   the Audit → custom OS motion.

   PRICING: `price` is null until Polo locks the SKU prices (pricing/v0/ready-to-hire.md).
   Null renders as "Pricing at launch". Billing model: month-to-month, pause/cancel anytime,
   no minimum (the Founder 2026-06-17) — the low-friction entry; the custom OS keeps the 6-mo minimum.

   ONBOARDING (owned by Janice, the Onboarding Agent): each employee lists `needs` (what we collect
   to build + integrate it) and `haveHandy` (the checklist shown if they'd rather do a 10-min call).
   The wizard (hire-onboarding.html) renders `needs`; the "book a call" fallback shows `haveHandy`.
   Janice keeps these fields right per pattern and runs the resulting onboarding → hands to Kimi to build.
   ========================================================================== */
window.YOURCO_HIRE = {
  // billing terms (shown on the catalog + onboarding)
  terms: {
    model: "month-to-month",
    pause: "Pause anytime — unused time rolls over.",
    cancel: "Cancel anytime. No contracts, no minimum.",
    note: "yourco builds, runs, and keeps it reliable — you never touch the infrastructure."
  },

  employees: [
    {
      slug: "receptionist",
      name: "AI Front Desk",
      tagline: "Answers every call, day or night — books the job.",
      does: "Picks up every call (after-hours, overflow, or all of them), answers questions in your voice, qualifies the caller, and books the appointment straight onto your calendar. The missed-call leak, closed. <b>Ready for AI shoppers too</b> — when Google's \"Ask for Me\" agent calls for your price &amp; availability, it answers cleanly and wins you the booking.",
      bestFor: "Any business losing calls while on the job or after hours.",
      price: 749,
      voice: true,
      live: "Live in 48 hours",
      needs: [
        { k: "services", label: "What you do / your main services", type: "textarea", placeholder: "e.g. lawn maintenance, installs, irrigation…" },
        { k: "hours", label: "Your business hours (and when you want it to answer)", type: "text", placeholder: "Mon–Fri 8–5; answer 24/7" },
        { k: "phone", label: "Your business phone number (we set up forwarding)", type: "text", placeholder: "(555) 123-4567" },
        { k: "calendar", label: "What you use for scheduling / your calendar", type: "text", placeholder: "Google Calendar, Jobber, Calendly…" },
        { k: "booking_rules", label: "How you want appointments booked", type: "textarea", placeholder: "Job types, lengths, what to ask before booking…" },
        { k: "voice_notes", label: "How should it sound? (tone, what to say / never say)", type: "textarea", placeholder: "Friendly, local, never quote firm prices…" }
      ],
      haveHandy: ["Access to your calendar/scheduling tool", "Your phone provider login (for call forwarding)", "A list of your services", "Your typical appointment types + lengths", "Anything it should never say (e.g. firm prices)"]
    },
    {
      slug: "missed-call-textback",
      name: "Missed-Call Text-Back",
      tagline: "Every missed call gets an instant text — before they call the next guy.",
      does: "The second a call goes unanswered, it auto-texts the caller: a friendly note, a way to book, and a real reply thread. Recovers the callers who'd otherwise dial a competitor.",
      bestFor: "Anyone who can't always pick up but doesn't want to lose the lead.",
      price: 249,
      voice: false,
      live: "Live in 24 hours",
      needs: [
        { k: "phone", label: "Your business phone number", type: "text", placeholder: "(555) 123-4567" },
        { k: "text_msg", label: "What the auto-text should say", type: "textarea", placeholder: "Hi! Sorry we missed you — what can we help with? Book here: …" },
        { k: "booking_link", label: "A booking link or next step (optional)", type: "text", placeholder: "your Calendly / booking URL" },
        { k: "voice_notes", label: "Tone notes", type: "text", placeholder: "casual, local, no jargon" }
      ],
      haveHandy: ["Your phone provider login (for call forwarding)", "Your booking link if you have one", "How you'd want the text to read"]
    },
    {
      slug: "review-responder",
      name: "Review Responder",
      tagline: "Replies to every Google & Yelp review — in your voice.",
      does: "Drafts a thoughtful reply to every new review (you approve, or let it auto-post the good ones), protecting your reputation and your local search ranking without the daily chore.",
      bestFor: "Local businesses living and dying by their star rating.",
      price: 249,
      voice: false,
      live: "Live in 24 hours",
      needs: [
        { k: "profiles", label: "Your review profiles (links)", type: "textarea", placeholder: "Google Business Profile + Yelp URLs" },
        { k: "tone", label: "How should replies sound?", type: "textarea", placeholder: "Warm, grateful, owner's voice; how to handle negative ones…" },
        { k: "approval", label: "Auto-post 5-star replies, or approve everything first?", type: "text", placeholder: "Approve everything / auto-post positives only" }
      ],
      haveHandy: ["Access to your Google Business Profile", "Your Yelp login if applicable", "A sense of how you'd reply to a tough review"]
    },
    {
      slug: "reminder-recall",
      name: "Reminder & Recall",
      tagline: "Cuts no-shows, re-books lapsed customers.",
      does: "Texts appointment reminders to cut no-shows, and quietly re-engages customers who haven't been back — bringing repeat revenue you're currently leaving on the table.",
      bestFor: "Appointment-based businesses with no-shows or lapsing customers.",
      price: 299,
      voice: false,
      live: "Live in 48 hours",
      needs: [
        { k: "calendar", label: "Your scheduling tool / where appointments live", type: "text", placeholder: "Jobber, Google Calendar, your CRM…" },
        { k: "reminder_msg", label: "Reminder message + timing", type: "textarea", placeholder: "Text 24h + 1h before; friendly tone" },
        { k: "recall_rule", label: "When should a customer get a 'come back' nudge?", type: "text", placeholder: "Haven't booked in 6 months" }
      ],
      haveHandy: ["Access to your scheduling/customer tool", "Your typical reminder cadence", "How long before a customer is 'lapsed'"]
    },
    {
      slug: "faq-responder",
      name: "Inbox & FAQ Responder",
      tagline: "Answers the same questions so you don't have to.",
      does: "Handles inbound emails and form/website questions — hours, pricing ranges, availability, 'do you service my area' — instantly and accurately, escalating the real ones to you.",
      bestFor: "Anyone drowning in repetitive inbound questions.",
      price: 299,
      voice: false,
      live: "Live in 24 hours",
      needs: [
        { k: "inbox", label: "Which inbox / form should it watch?", type: "text", placeholder: "info@yourbiz.com / website contact form" },
        { k: "faqs", label: "Your most common questions + the answers", type: "textarea", placeholder: "Hours, service area, pricing ranges, lead times…" },
        { k: "escalate", label: "What should it hand to you instead of answering?", type: "text", placeholder: "Anything about a complaint or a custom quote" }
      ],
      haveHandy: ["Access to the inbox or form you want covered", "Your top 10 FAQs + answers", "What you'd rather handle yourself"]
    },
    {
      slug: "lead-intake",
      name: "Lead Intake & Booking",
      tagline: "Qualifies every new lead and books the next step.",
      does: "Greets every inbound lead, asks your qualifying questions, captures the details into your CRM, and books the estimate or call — so no lead sits unworked.",
      bestFor: "Sample Company 46 with steady inbound leads that slip through the cracks.",
      price: 449,
      voice: false,
      live: "Live in 48 hours",
      needs: [
        { k: "source", label: "Where do leads come in?", type: "text", placeholder: "Website form, phone, Facebook, Angi…" },
        { k: "qualify", label: "Your qualifying questions", type: "textarea", placeholder: "What to ask to know if it's a real job" },
        { k: "crm", label: "Where should leads + notes land?", type: "text", placeholder: "Your CRM / spreadsheet / email" },
        { k: "next_step", label: "What's the booked next step?", type: "text", placeholder: "An estimate visit / a call" }
      ],
      haveHandy: ["Access to your CRM or where leads should land", "Your qualifying questions", "Your calendar for booking the next step"]
    }
  ],

  /* Persona bundles — the "package several employees for a persona" play (the Logan Kilpatrick /
     DesignJoy insight: a persona has ~N needs, not one). A bundle is the on-ramp to the OS without
     the audit, and the up-sell bridge to the custom OS. `price` null until Polo locks (a bundle
     discount vs. hiring separately). `includes` = employee slugs above. */
  bundles: [
    {
      slug: "front-office",
      name: "The Front Office",
      tagline: "Never miss a lead — answer, recover, and protect your reputation.",
      includes: ["receptionist", "missed-call-textback", "review-responder"],
      bestFor: "Any local business that lives on inbound calls + its star rating.",
      price: null
    },
    {
      slug: "booked-solid",
      name: "Booked Solid",
      tagline: "Fill the calendar and keep it full.",
      includes: ["receptionist", "lead-intake", "reminder-recall"],
      bestFor: "Appointment-based businesses fighting no-shows + empty slots.",
      price: null
    },
    {
      slug: "growth-stack",
      name: "The Growth Stack",
      tagline: "The closest thing to a full front office, for a fraction of one hire.",
      includes: ["receptionist", "lead-intake", "reminder-recall", "review-responder", "missed-call-textback"],
      bestFor: "Owners ready to hand off the whole front office — the bridge to a custom AI OS.",
      price: null
    }
  ]
};
