2026-07-05 — Client-build stack defaults locked (Supabase / Firecrawl / markitdown)

Source: the Founder's tool triage (`decisions/2026-07-05_tool-triage.md`)
Pattern: Repeated "should we use X?" churn resolves to three defaults that pass the moat test: Supabase = default backend whenever a build needs a real DB + auth + tenant isolation (RLS; first natural fit = Conduit); markitdown = client-doc → markdown ingestion for the Company Brain pillar at discovery; Firecrawl (hosted API, not an installed framework) = prospect/client own-site → markdown for audit prep and AEO scans — public pages only, robots.txt respected, never ToS-gated platforms.
Implication: Bella/Kimi/Janice — reach for these defaults instead of re-evaluating per engagement; deviations need a reason logged. Trigger-gated pillar ingredients (Chatwoot for Customer-pillar support desks, Stirling PDF for Back Office PDF ops, Coolify at the 2nd live client) fire per `runtime/activation-triggers.md` §Tool triggers — flag the trigger at discovery, don't pre-install. Sample Product stays on Cloudflare D1 (no churn).
Audience: Bella (audit), Kimi (delivery), Janice (onboarding), Kemba (platform)

Triggers: agent:kimi, agent:bella, agent:kemba, client build, stack choice, supabase, firecrawl, skill:scaffold-engagement