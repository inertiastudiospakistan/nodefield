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

- **No live GPU workers.** No contributor machine is connected to any coordinator. (A local CPU worker served the first real request on 21 Nov — see below — then stopped; nothing is running now.)
- **First real model serving through the Nodefield API: DONE 21 Nov 2026, 23:48 PKT** (see below). A real Qwen3-8B model has also been benchmarked on Colab, but not yet served through the API/scheduler from a GPU worker — that is the next step (Colab T4 worker via Cloudflare Tunnel, `docs/WORKER.md`).
- **No benchmarks run through the full methodology.** One single-run benchmark exists; 3-run medians, GPU-util/power/cost measurements still pending.
- **No Supabase account / database created.** Schema SQL exists in `infra/supabase_schema.sql` but has not been applied anywhere.
- **No Cloudflare account / Pages deployment.** Frontend is local-only.
- **No payments.** No billing, no provider payouts, no payment processor. Paid billing is deliberately not activated (see ROADMAP Phase 7 gates).
- **Discord server created 22 Nov 2026:** "Nodefield" (ID 1573941092695679038, https://discord.com/channels/1573941092695679038) — 5 categories, 15 text channels, 8 rules posted in #rules, welcome post in #announcements. Account fully rebranded: username "nodefield", display name "Nodefield", bio set, Nodefield logo avatar. Discord login saved in Secure Vault.
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
2. **Run the first GPU worker through the API:** Colab T4 worker per `docs/WORKER.md` (free Cloudflare Tunnel to expose the local API), Qwen3-8B, and record the GPU tok/s + TTFT in `BENCHMARKS.md`. The local CPU proof is done (6.44 tok/s); the GPU number is still unproven through the API.
3. **Founder creates accounts:** GitHub repo (public), Cloudflare (Pages), Supabase (free tier) — then apply `infra/supabase_schema.sql` and deploy the frontend per `infra/DEPLOY.md`.
4. **Trademark/domain check on "Nodefield"** and confirm or replace the provisional name before any public launch material is published.
5. **Create the Discord server** from `marketing/DISCORD.md` and publish the first honest dev update (Phase 1 progress, no fake numbers).

## Live deployment (21 Nov 2026)

- **Site:** https://nodefield-css.pages.dev/ (Cloudflare Pages, free, project `nodefield`, connected to GitHub repo, root `frontend`, no build step). Verified live: homepage 200 with exact headline; pricing/register/status/models/docs/dashboard all 200.
- **Code:** https://github.com/inertiastudiospakistan/nodefield (public, `main`, 54 files, Apache-2.0). `gh` CLI on this machine is authorised as inertiastudiospakistan (device flow); `gh auth setup-git` configured.
- **Database:** Supabase project `nodefield` (free, Singapore ap-southeast-1, Nano), https://wixdniuqdvridwnpsiio.supabase.co — tables providers, developers, api_keys, jobs created and verified in Table Editor. No RLS policies yet (decided at API wiring time).
- **Not yet done:** API is NOT yet wired to Supabase (waitlist still uses local SQLite demo); no live GPU workers; no real model serving; no benchmarks; no custom domain; no Discord/social accounts.

## First real end-to-end API request (21 Nov 2026, 23:48 PKT)

- **The API now serves real model output.** `POST /v1/chat/completions` → SQLite job queue → `agent/worker.py` (llama-cpp-python) → real reply labelled `"nodefield": {"source": "real"}` with measured tok/s + TTFT. New endpoints: `POST /api/workers/claim`, `POST /api/jobs/<id>/result`, `GET /api/jobs/<id>`. With no live worker the endpoint still returns the existing demo reply (verified with the worker stopped). API server itself stays stdlib-only.
- **Proof (job 3):** Qwen3-4B Q4_K_M on this machine's CPU (no GPU, 1.5 vCPU quota) — "Explain photosynthesis in two sentences." → a correct two-sentence answer, 64 tokens, **6.44 tok/s, TTFT 5,744 ms**, 15.7 s job time. Full numbers + raw JSON in `BENCHMARKS.md` and `backend/benchmarks/results/2026-11-21-qwen3-4b-cpu-local.json`. Streaming (`stream: true`) also verified with a real worker (SSE chunks + `[DONE]`).
- **Honest limits:** CPU-only and slow (6.44 tok/s vs 35.27 on the Colab T4); single request, not a 3-run median; an earlier same-evening run did only 1.41 tok/s with a `<think>` block in the reply — both fixed in the worker (2 threads, empty think block for Qwen3) and recorded in BENCHMARKS.md. llama-cpp-python 0.3.37 had to be built from source (~12 min) — no prebuilt wheel was used. Model file (~2.5 GB) lives in `agent/models/` (gitignored).
- **GPU-worker path documented** in `docs/WORKER.md` (Colab T4 + free Cloudflare Tunnel; tunnel NOT set up). Still not done: no GPU worker has served through the API yet; no custom domain; no Discord.

## First GPU request through the API (22 Nov 2026, 13:40 PKT)

- **Qwen3-8B Q4_K_M on a free Colab Tesla T4, served through the Nodefield API itself: 31.29 tokens/sec, 650 ms TTFT** (64 tokens, job 1, worker `colab-t4-1`). Streaming verified (SSE + `[DONE]`). Full measured results in `BENCHMARKS.md` (Run 3) + `backend/benchmarks/results/2026-11-22-qwen3-8b-t4-api.json` (transcribed from the run report).
- API + worker ran on the same Colab VM — no tunnel: Cloudflare quick tunnels and localtunnel both fail from the dev VM (egress filtered). A remote worker over the public internet is still unproven.
- Bugs: `--model qwen3-8b` silently served the 4B model — FIXED with `MODEL_MAP` in `agent/worker.py` (verified locally). First streaming attempt hung ~4 min with no SSE — OPEN, in KNOWN_ISSUES.md.
- Still not done: public API host, trademark/domain check, custom domain, first remote (non-Colab) GPU worker.

## First real benchmark (21 Nov 2026, 23:00 PKT)

- **Qwen3-8B Q4_K_M on a free Colab Tesla T4: 35.27 tokens/sec mean, 156 ms mean time-to-first-token** (5 fixed prompts, 128 tokens each, temp 0, llama.cpp CUDA). Model load 21.7 s, 5.2 GB VRAM of 15.4 GB. Full measured results + raw JSON in `BENCHMARKS.md` and `backend/benchmarks/results/2026-11-21-qwen3-8b-t4-colab.json`.
- Honest limits: single run (not 3-run median); model file was a Hugging Face cache hit, not a fresh download; throughput only — outputs ramble at fixed 128 tokens, no quality eval; no GPU-util/power/cost measured yet.
- Kaggle attempt blocked: account AdilMehmoodWarraich created, notebook drafted, but GPU + Internet locked behind phone verification (user-only step). Notebook: https://colab.research.google.com/drive/1mn4d9JBohZmXj3hVeDe6cAGZh34QtCq9
- Still not done: no live GPU workers; no real model serving through the Nodefield API; no custom domain; no Discord.

## Supabase wiring (21 Nov 2026, 22:04 PKT)

- Live waitlist form now writes straight to Supabase when the local backend is unreachable (frontend/assets/app.js: submitToSupabase, return=minimal). Verified live: POST to /rest/v1/providers returned HTTP 201.
- RLS enabled on all 4 tables; anon INSERT-only policies on providers/developers; GRANT INSERT TO anon on both tables. SELECT deliberately NOT granted to anon — waitlist emails must not be readable by visitors (a return=representation test correctly fails with 42501).
- Publishable anon key is embedded in app.js (by design — it can only insert waitlist rows). Service_role key was never copied or used.
- CLEANUP: one test row sits in providers (name "VERIFY TEST — delete me", email verify-test@nodefield.example) from the live verification. Delete it in the Supabase Table Editor.
- Still not done: no live GPU workers; no real model serving; no benchmarks; no custom domain; no Discord.
