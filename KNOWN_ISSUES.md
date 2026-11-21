# Nodefield — Known Issues

**Updated: 21 November 2026.** Honest list of what is broken, missing, or unvalidated. If something here is fixed, move it to `PROJECT_STATUS.md` and delete the line — don't leave stale issues.

## Blocking / structural

1. **No GPU on the dev machine.** Real model runs and benchmarks cannot happen here. Blocks Phase 2 until a GPU environment (Kaggle/Colab within permitted use, or a volunteer machine) is available.
2. **Demo API does not run a real model.** `POST /v1/chat/completions` returns canned demo responses. Anyone testing the API must be told this; the responses are labelled demo.
3. **No live workers.** The scheduler has no workers to schedule to. All dashboard "network activity" is demo data and labelled as such.
4. **No Supabase / Cloudflare accounts created.** The schema exists (`infra/supabase_schema.sql`) but is unapplied; the frontend is local-only. Founder must create the accounts.
5. **Name not trademark-checked.** "Nodefield" is provisional. Do not commit to it in paid assets or public branding until checked (see `DECISIONS.md` ADR-001).

## Free-tier limits to verify before relying on

6. **Supabase free tier pauses after 1 week of inactivity.** A paused project needs manual reactivation; the waitlist would stop working silently. Verify current behaviour before launch; consider a keep-alive or a paid tier later.
7. **Cloudflare Workers free tier: 100,000 requests/day.** Enough for a beta, not for scale. The free Pages tier (500 builds/month) is fine for the static site.
8. **Kaggle / Colab free notebooks do not permit persistent public inference endpoints or commercial production workloads.** They are for isolated experiments only — do not build the service on them.

## Not yet implemented

9. **No payments.** No billing, no provider payouts, no payment processor. Do not promise earnings.
10. **No signed agent updates.** Update signing is planned (see `docs/SECURITY.md`); the prototype has no auto-update at all.
11. **No TLS on the prototype coordinator.** Local prototype uses plain HTTP on localhost only. Production coordinator must use TLS before any worker connects.
12. **No Discord server, no social accounts.** Structures and calendars are written; the accounts/servers don't exist.
13. **Llama licence review outstanding.** Llama 3 Community License (700M MAU cap) needs a founder/legal read before Llama models are served commercially.
14. **Pricing engine fed with placeholder costs.** Cost per 1M tokens, payouts, and margins are unvalidated until real benchmarks exist.
