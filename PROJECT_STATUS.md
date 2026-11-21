# Nodefield — Project Status

**As of: 21 November 2026**
**Phase: 1 — Foundation (in progress)**
**Budget spent: $0. Live workers: 0. Real models serving: 0. Revenue: $0.**

## What is done (this session)

- **Provisional name selected:** Nodefield (provisional — trademark/domain check still required). 20-name shortlist evaluated; see `DECISIONS.md`.
- **Competitor research done:** Vast.ai, RunPod, Together AI, Lambda, Modal, Akash, io.net, Render, Fireworks AI, Hyperbolic — see `docs/COMPETITORS.md` (third-party snapshots, Nov 2026, verify before quoting).
- **Landing page + 14 pages built:** `/`, `/providers`, `/developers`, `/models`, `/pricing`, `/how-it-works`, `/roadmap`, `/docs`, `/community`, `/faq`, `/privacy`, `/terms`, `/status`, `/register`, `/dashboard` — static frontend, no build step. Serves on port 8000.
- **Waitlist API:** contributor and developer registration endpoints (prototype, stdlib-only Python).
- **Demo inference API:** OpenAI-compatible `POST /v1/chat/completions` shape, streaming shape, token-usage reporting, API-key auth, rate limiting — returns clearly labelled demo responses; **does not run a real model**.
- **Scheduler skeleton:** job states (pending → assigned → running → completed / failed / cancelled), worker matching on model compatibility, VRAM, reliability, cost, latency; timeouts and retry logic sketched.
- **Agent prototype:** hardware detection, benchmark stub, contributor dashboard UI, pause/uninstall controls.
- **Pricing engine:** configurable engine accounting for GPU operating cost, electricity, provider payout, platform commission, failed requests, infrastructure — fed with placeholder costs only; **no real costs measured yet**.
- **Documentation set:** README, ROADMAP, DECISIONS, PROJECT_STATUS, BENCHMARKS (methodology only, empty results), KNOWN_ISSUES, CONTRIBUTING, `docs/` (architecture, competitors, models, security), `marketing/` (content calendar, Discord), `infra/` (deploy plan + Supabase schema SQL).

## What is NOT done

- **No live GPU workers.** No contributor machine is connected to any coordinator.
- **No real model serving.** No Qwen, Llama, or Mistral model has been run by Nodefield code. The demo API is a stub.
- **No benchmarks run.** `BENCHMARKS.md` has an empty results table by design.
- **No Supabase account / database created.** Schema SQL exists in `infra/supabase_schema.sql` but has not been applied anywhere.
- **No Cloudflare account / Pages deployment.** Frontend is local-only.
- **No payments.** No billing, no provider payouts, no payment processor. Paid billing is deliberately not activated (see ROADMAP Phase 7 gates).
- **No Discord server created.** Structure and guidelines are written in `marketing/DISCORD.md`; the server itself does not exist.
- **No social accounts created.** No X, Reddit, YouTube, or Product Hunt presence.
- **No GitHub repository published yet** (repo layout is local).
- **Name not trademark-checked; domain not checked or purchased** (and must not be purchased without founder approval).

## Blockers

1. **No GPU on the dev machine** — real model runs and benchmarks need a GPU environment (Kaggle/Colab within permitted use, or a volunteer's machine). Blocks Phase 2.
2. **Founder-owned accounts needed** — Supabase, Cloudflare, Discord, GitHub org, and any social accounts must be created by the founder (or with explicit founder approval). The agent cannot and should not create accounts in the founder's name.
3. **Name clearance** — Nodefield needs a trademark and domain-availability check before launch or any public branding commitment.
4. **Model licence review** — Llama 3 Community License terms (700M MAU cap) need a founder/legal read before Llama models are offered commercially.

## Next 5 tasks

1. **Verify the local prototype end-to-end:** serve frontend on 8000, backend on 8787, test all 14 pages, both registration flows, and the demo chat completions endpoint; record any failures in `KNOWN_ISSUES.md`.
2. **Run the first real model:** Qwen3-4B Q4 on a free GPU environment (Kaggle/Colab, within permitted use) and record the first honest benchmark row in `BENCHMARKS.md`.
3. **Founder creates accounts:** GitHub repo (public), Cloudflare (Pages), Supabase (free tier) — then apply `infra/supabase_schema.sql` and deploy the frontend per `infra/DEPLOY.md`.
4. **Trademark/domain check on "Nodefield"** and confirm or replace the provisional name before any public launch material is published.
5. **Create the Discord server** from `marketing/DISCORD.md` and publish the first honest dev update (Phase 1 progress, no fake numbers).

## Live deployment (21 Nov 2026)

- **Site:** https://nodefield-css.pages.dev/ (Cloudflare Pages, free, project `nodefield`, connected to GitHub repo, root `frontend`, no build step). Verified live: homepage 200 with exact headline; pricing/register/status/models/docs/dashboard all 200.
- **Code:** https://github.com/inertiastudiospakistan/nodefield (public, `main`, 54 files, Apache-2.0). `gh` CLI on this machine is authorised as inertiastudiospakistan (device flow); `gh auth setup-git` configured.
- **Database:** Supabase project `nodefield` (free, Singapore ap-southeast-1, Nano), https://wixdniuqdvridwnpsiio.supabase.co — tables providers, developers, api_keys, jobs created and verified in Table Editor. No RLS policies yet (decided at API wiring time).
- **Not yet done:** API is NOT yet wired to Supabase (waitlist still uses local SQLite demo); no live GPU workers; no real model serving; no benchmarks; no custom domain; no Discord/social accounts.

## Supabase wiring (21 Nov 2026, 22:04 PKT)

- Live waitlist form now writes straight to Supabase when the local backend is unreachable (frontend/assets/app.js: submitToSupabase, return=minimal). Verified live: POST to /rest/v1/providers returned HTTP 201.
- RLS enabled on all 4 tables; anon INSERT-only policies on providers/developers; GRANT INSERT TO anon on both tables. SELECT deliberately NOT granted to anon — waitlist emails must not be readable by visitors (a return=representation test correctly fails with 42501).
- Publishable anon key is embedded in app.js (by design — it can only insert waitlist rows). Service_role key was never copied or used.
- CLEANUP: one test row sits in providers (name "VERIFY TEST — delete me", email verify-test@nodefield.example) from the live verification. Delete it in the Supabase Table Editor.
- Still not done: no live GPU workers; no real model serving; no benchmarks; no custom domain; no Discord.
