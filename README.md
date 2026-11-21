# Nodefield

**Your idle GPU could power the next generation of AI.**

Nodefield is an open marketplace for AI inference powered by distributed, underutilized GPU resources. It connects people with idle GPUs — gaming PCs, AI workstations, small server operators, universities — with developers who need affordable AI inference.

> **Status: Phase 1 — Foundation. Pre-launch. 0 live workers, 0 real model serving, $0 spent.**
> Everything in this repository is a working prototype or clearly labelled demonstration data. Nothing here is production infrastructure yet.

## The idea in one paragraph

GPU owners install a small agent on their machine, opt in to share spare capacity, and get paid when their hardware completes paid workloads. Developers call an OpenAI-compatible API (`POST /v1/chat/completions`) and get inference at a lower cost than hyperscaler clouds, because the compute is spare capacity that already exists. Nodefield schedules each request to a suitable machine and takes a commission. No token, no blockchain — fiat/credits only, when payments exist (they don't yet).

## Value propositions

| Audience | Proposition |
|---|---|
| **GPU owners** | "Earn from your unused GPU." No guaranteed earnings — payout depends on real demand, and none exists yet. |
| **Developers** | "Run AI models at lower costs." OpenAI-compatible API, so you can swap the base URL. Small quantized open-weight models first. |
| **Businesses** | "Access flexible AI infrastructure without owning GPUs." |

## Architecture

```
Developer client (OpenAI-compatible)
        │
        ▼
┌──────────────────┐     ┌──────────────┐
│  API Gateway     │────▶│  Scheduler   │
│  (FastAPI proto- │     │  (job queue, │
│   type, stdlib   │     │   worker      │
│   Python)        │     │   matching)   │
└──────┬───────────┘     └──────┬───────┘
       │                        │  assign job
       │                        ▼
       │              ┌──────────────────┐
       │              │  Worker agent    │
       │              │  (Tauri/Python,  │
       │              │   llama.cpp /    │
       │              │   vLLM on host)  │
       │              └──────────────────┘
       │
       ▼
┌──────────────────┐     ┌──────────────┐
│  Waitlist DB     │     │  Pricing     │
│  (Supabase       │     │  engine      │
│   Postgres —     │     │  (cost /     │
│   planned, not   │     │   payout /   │
│   yet created)   │     │   margin)    │
└──────────────────┘     └──────────────┘
```

Job lifecycle: `pending → assigned → running → completed | failed | cancelled`, with timeouts and retry. One whole request goes to one machine — we do **not** split a single model across geographically distributed consumer GPUs (see `DECISIONS.md`).

Full detail: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Repository layout

```
nodefield/
├── README.md                 # this file
├── ROADMAP.md                # Phases 1–7 with exit criteria
├── PROJECT_STATUS.md         # current status, blockers, next tasks
├── DECISIONS.md              # architecture decision records
├── BENCHMARKS.md             # methodology + empty results table (no results yet)
├── KNOWN_ISSUES.md           # honest list of what is broken/missing
├── CONTRIBUTING.md           # how to contribute
├── frontend/                 # static site, no build step (14 pages)
├── backend/
│   ├── api/                  # inference API prototype (stdlib-only Python)
│   └── scheduler/            # scheduler skeleton
├── agent/                    # GPU contributor desktop agent prototype
├── docs/
│   ├── ARCHITECTURE.md
│   ├── COMPETITORS.md
│   ├── MODELS.md
│   └── SECURITY.md
├── marketing/
│   ├── CONTENT_CALENDAR.md   # 30-day X calendar, Reddit, YouTube, Show HN draft
│   └── DISCORD.md            # Discord server structure and guidelines
└── infra/
    ├── DEPLOY.md             # $0 deployment plan
    └── supabase_schema.sql   # waitlist + jobs schema (not yet applied)
```

## Quickstart (local prototype)

No accounts, no keys, no installs beyond Python 3.11+ and Git.

```bash
git clone <repo-url> nodefield
cd nodefield

# Frontend — static site on port 8000
python3 -m http.server 8000 --directory frontend
# open http://localhost:8000

# Backend — demo inference API on port 8787
python3 backend/api/server.py
# POST http://localhost:8787/v1/chat/completions
```

The demo API returns clearly labelled **demo responses** — it does not run a real model. See `BENCHMARKS.md` for what is and isn't measured.

## $0 budget stack

| Layer | Choice | Free tier (verify before relying) |
|---|---|---|
| Frontend hosting | Cloudflare Pages | Free: 500 builds/month, unlimited static requests/bandwidth on free plan |
| Backend (later) | Cloudflare Workers / Python FastAPI | Workers free: 100,000 requests/day |
| Database + Auth | Supabase | Free: 500 MB Postgres, 50,000 MAU; **free projects pause after 1 week of inactivity — verify before relying** |
| Code hosting | GitHub | Free public repos, Actions minutes included |
| Models | Hugging Face | Open-weight models per their own licenses (see `docs/MODELS.md`) |
| Community | Discord | Free server |
| Dev GPU experiments | Kaggle / Google Colab | Free notebooks — **do not assume they permit persistent public endpoints or commercial production workloads** |

No paid resource has been created. No account for Cloudflare or Supabase has been created yet — the founder must create those (see `infra/DEPLOY.md`).

## Current status

- **Phase 1 (Foundation), in progress — Nov 2026.**
- Provisional name **Nodefield** selected (trademark/domain check still required before launch).
- Competitor research done — see `docs/COMPETITORS.md`.
- Landing page + 14 pages built (static frontend).
- Waitlist API, demo inference API, scheduler skeleton, agent prototype, pricing engine — prototypes only.
- **Not done:** no live GPU workers, no real model serving, no benchmarks run, no Supabase/Cloudflare accounts, no payments, no Discord server.
- Full status: [`PROJECT_STATUS.md`](PROJECT_STATUS.md). Roadmap: [`ROADMAP.md`](ROADMAP.md).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). PRs welcome; no secrets in PRs, ever.

## License decision: Apache-2.0 for code

Nodefield code is licensed under the **Apache License 2.0**. Why:

- Permissive: anyone can use, modify, and distribute the code, including commercially, with attribution.
- Compatible with the model ecosystem we build on: Qwen and Mistral models are Apache-2.0 licensed, so our code license aligns with the largest part of our model stack.
- Patent grant: Apache-2.0 includes an express patent licence, which matters for infrastructure software.
- Well understood by companies, contributors, and package ecosystems.

**Important scope note:** the Apache-2.0 licence covers *Nodefield's code*. It does **not** cover the models served through the platform — each model carries its own licence. In particular, the Llama family is under the **Llama 3 Community License** (separate licence, with a 700M monthly-active-user cap and other conditions), which applies only to that model family. Model licences are documented per model in [`docs/MODELS.md`](docs/MODELS.md).

## Security policy — summary

- The agent never executes arbitrary code from marketplace customers on contributor machines. Workloads are sandboxed inference requests only.
- The agent never secretly uses a GPU, never hides activity, never accesses personal files. Users can pause or uninstall at any time.
- API keys are stored hashed (SHA-256 with a secret prefix); never in plaintext.
- Vulnerability reporting: security contact to be published by the founder — see [`docs/SECURITY.md`](docs/SECURITY.md). Do not invent a security email.
- Full policy: [`docs/SECURITY.md`](docs/SECURITY.md).

## What Nodefield is not

- Not a cryptocurrency or token project. No token, no mining, no blockchain claims.
- Not a promise of earnings. GPU contributors are paid only when real paid workloads complete — and there are no paid workloads yet.
- Not production infrastructure. The demo API, demo dashboard numbers, and any benchmark figures shown anywhere are labelled demo until real measured runs exist.
