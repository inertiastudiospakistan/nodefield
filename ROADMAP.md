# Nodefield Roadmap

> All dates are **targets, not commitments**. All Phase 6 numbers are **goals, not achievements**. A phase is done only when its exit criteria are met and verified — never on the basis of a plan or a backtest alone.

## Phase 1 — Foundation

**Target: Nov 2026**

- Research competitors (done — see `docs/COMPETITORS.md`).
- Select provisional project name (done — Nodefield, provisional).
- Create GitHub repositories / repo layout.
- Build landing page + full site (14 pages).
- Create GPU contributor and developer registration flows.
- Set up free infrastructure plan (Cloudflare Pages, Supabase — accounts not yet created).
- Create documentation (this repo).

**Exit criteria:** repo public with README, roadmap, architecture, competitor and model docs; landing page serves locally on port 8000; waitlist API serves locally on port 8787; no fake users, revenue, or benchmarks anywhere.

## Phase 2 — First AI Model

**Target: Dec 2026**

- Access a free GPU environment (Kaggle / Colab — within their permitted use; not as production).
- Run a suitable open-weight model locally (Qwen3-4B Q4 first — smallest, Apache-2.0).
- Benchmark inference honestly (tokens/sec, time-to-first-token, latency, VRAM) and record results in `BENCHMARKS.md`.
- Build a basic chat interface (playground) backed by a real model.
- Build an API prototype serving a real model on a test machine.

**Exit criteria:** at least one real model answering `POST /v1/chat/completions` on a test machine; first real benchmark row recorded with hardware, model, quant, date, and method; playground works end-to-end against that model.

## Phase 3 — GPU Agent

**Target: Jan 2027**

- Hardware detection (GPU model, VRAM, OS, RAM, CPU).
- Local benchmark (tokens/sec on a reference model).
- Contributor dashboard (utilisation, VRAM, temperature where supported, uptime, jobs).
- Secure registration (agent authenticates to coordinator; no arbitrary code execution).
- Connect test machines to the coordinator; pause/uninstall works.

**Exit criteria:** agent runs on Windows, detects a real GPU, reports capacity to the coordinator, completes a benchmark, and can be paused and uninstalled cleanly; security review of the agent completed (see `docs/SECURITY.md`).

## Phase 4 — Marketplace

**Target: Feb 2027**

- Implement scheduler (whole-request assignment; model compatibility, VRAM, reliability, cost, latency).
- Register approved workers.
- Route test inference requests end-to-end through the scheduler to real workers.
- Measure reliability (success rate, latency, failure modes).
- Calculate actual operating costs per 1M tokens.

**Exit criteria:** a test request flows client → gateway → scheduler → worker → response with a real model; measured reliability and cost numbers published in `BENCHMARKS.md`; pricing engine fed with real costs, not estimates.

## Phase 5 — Community

**Target: Feb–Mar 2027**

- Launch Discord server (structure in `marketing/DISCORD.md`).
- Publish development updates (weekly, honest, with real numbers or none).
- Recruit initial GPU owners and developers.
- Gather feedback and act on it publicly.

**Exit criteria:** Discord server live with channels, rules, and onboarding; at least one public dev update per week for a month; a feedback loop (bug reports / feature requests) operating.

## Phase 6 — Private Beta

**Target: Mar–Apr 2027**

**Targets (goals, not achievements):**

- 20 functioning GPU contributors.
- 10 developer testers.
- 3 supported models.
- Working API (OpenAI-compatible, authenticated, rate-limited).
- Public benchmark results.

**Exit criteria:** all five targets met simultaneously and verified from real system data; no target is claimed on the basis of signups alone — a "functioning contributor" is one that has completed real workloads; a "developer tester" is one that has made real API calls.

## Phase 7 — Public Launch

**Target: only when gating conditions are met — no fixed date.**

Proceed **only when all** of the following hold:

- [ ] Security testing complete (agent sandboxing, update signing, key handling reviewed).
- [ ] The inference API works reliably under beta load (measured uptime and error rates published).
- [ ] Provider consent is implemented (explicit opt-in, pause, uninstall, resource limits).
- [ ] Pricing is economically viable (real measured cost per 1M tokens < price charged, after provider payout and commission).
- [ ] Legal and payment requirements are addressed (terms, privacy, payment processing, provider compensation actually fundable).
- [ ] No fake users, testimonials, revenue, or benchmarks anywhere on the site.

**Exit criteria:** public launch announcement published with real numbers; paid billing activated only after the conditions above are met.
