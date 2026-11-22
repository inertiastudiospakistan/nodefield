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
15. **Streaming stall (22 Nov 2026, OPEN).** On the first Colab T4 streaming attempt the worker completed the job (64 tokens, 30.85 tok/s) but the API delivered no SSE at all — curl hung ~4 min, no error in the API log. A clean retry streamed fine. Cause unknown; needs investigation before streaming is trusted (reproduce with a local worker + streaming request, check the SSE writer/flush path in `server.py`).
16. **No public API host; tunnels blocked from the dev VM (22 Nov 2026).** Cloudflare quick tunnel fails (`tls: first record does not look like a TLS handshake` on api.trycloudflare.com) and localtunnel never connects — the dev VM's egress is filtered. A remote GPU worker over the public internet is therefore still unproven; the Colab GPU run had the API and worker on the same VM. Next step: host the API somewhere public (e.g. a free Hugging Face Space) or tunnel from an unfiltered machine.

## Fixed (moved here from the list above — see PROJECT_STATUS.md)

- **Demo API now runs real models when a worker is up (21–22 Nov 2026).** `POST /v1/chat/completions` routes to a worker and returns a real reply labelled `"source": "real"`; demo fallback only when no worker is available. Proven on CPU (6.44 tok/s) and on a Colab T4 (31.29 tok/s).
- **Discord server created (22 Nov 2026).** Server "Nodefield" live with 15 channels; account rebranded to username `nodefield`.
- **Worker `--model` now maps to repo/file (22 Nov 2026).** `--model qwen3-8b` used to silently download the 4B model; `MODEL_MAP` in `agent/worker.py` fixes it, unknown models exit with an error.
