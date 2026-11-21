# Nodefield Architecture

**Status:** Phase 1 prototype design. The gateway, scheduler, and agent exist as prototypes; no live workers are connected. This document describes the intended system and what is actually built today.

## System diagram

```
                    ┌─────────────────────┐
                    │  Developer client   │
                    │  (any OpenAI-compat │
                    │   SDK / curl)       │
                    └──────────┬──────────┘
                               │ HTTPS, API key
                               ▼
┌──────────────┐   ┌───────────────────────┐   ┌──────────────────┐
│  Landing /   │   │  API Gateway          │   │  Waitlist DB     │
│  dashboard   │   │  - auth (hashed keys) │──▶│  (Supabase       │
│  (static     │   │  - rate limiting      │   │   Postgres —     │
│   frontend)  │   │  - token accounting   │   │   planned)       │
└──────────────┘   └───────────┬───────────┘   └──────────────────┘
                               │ enqueue job
                               ▼
                    ┌───────────────────────┐
                    │  Scheduler            │
                    │  - worker registry    │
                    │  - matching: model,   │
                    │    VRAM, reliability, │
                    │    cost, latency      │
                    │  - timeouts + retry   │
                    └───────────┬───────────┘
                                │ assign (TLS)
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
   ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
   │ Worker agent #1  │ │ Worker agent #2  │ │ Worker agent #n  │
   │ llama.cpp / vLLM │ │ llama.cpp / vLLM │ │ llama.cpp / vLLM │
   │ on contributor   │ │ on contributor   │ │ on contributor   │
   │ GPU (opt-in)     │ │ GPU (opt-in)     │ │ GPU (opt-in)     │
   └──────────────────┘ └──────────────────┘ └──────────────────┘
```

A separate **pricing engine** consumes measured cost data (tokens/sec, electricity where measurable, failure rate) and computes cost per 1M tokens, provider payout, platform commission, and margin. It is currently fed placeholder costs only.

## Components

| Component | Tech (planned / prototype) | State |
|---|---|---|
| Frontend | Static HTML/CSS/JS, no build step | Built (14 pages) |
| API gateway | Python stdlib prototype → FastAPI in production | Prototype (demo responses only) |
| Scheduler | Python stdlib prototype | Skeleton |
| Worker agent | Tauri + Python-based agent; llama.cpp / vLLM runtime | Prototype (detection + dashboard UI) |
| Waitlist DB | Supabase Postgres (free tier) | Schema written, not created |
| Pricing engine | Python | Prototype, placeholder costs |

## Data flows

1. **Registration:** contributor/developer submits form → waitlist API validates → row in `providers` / `developers` table (Supabase, planned). API keys are issued manually at first; stored only as hashes.
2. **Inference request:** client sends `POST /v1/chat/completions` with API key → gateway authenticates, rate-limits, counts tokens → scheduler picks a worker → worker runs the model locally → tokens stream back through gateway → usage recorded.
3. **Worker heartbeat:** agent reports GPU model, VRAM, utilisation, uptime, queue length to the scheduler; stale workers (no heartbeat) are removed from the pool.
4. **Benchmark:** agent runs a reference prompt set, reports tokens/sec, time-to-first-token, latency, VRAM, GPU utilisation → recorded in `BENCHMARKS.md` and the benchmark dashboard.

## Job lifecycle

```
pending → assigned → running → completed
                          ↘ failed → (retry, max N) → failed
pending → cancelled (client or timeout)
```

- **Timeouts:** per-request timeout; a worker that stops responding has its job re-queued to another worker.
- **Retry:** failed jobs retry up to a configured limit, then surface as failed to the client with an error, not a silent drop.
- **No model splitting:** one request goes to one machine (ADR-004).

## Scheduling

Simple scoring in Phase 1–4. For each candidate worker:

1. **Model compatibility** — does it have the requested model loaded (or can it load it within VRAM)?
2. **Available VRAM** — model + KV cache must fit with headroom.
3. **Reliability** — historical success rate and uptime; new workers start unproven and get limited traffic.
4. **Expected cost** — provider's declared price vs. measured efficiency.
5. **Latency** — coarse geographic region + measured round-trip.

Highest score wins. No machine is assigned work it cannot fit.

## Security model

- **No arbitrary code execution.** Workers run sandboxed inference only: a prompt in, tokens out. Marketplace customers never run code on contributor machines. Ever.
- **Least privilege.** The agent runs as a normal user process, accesses only its own working directory and the GPU; no personal files, no browsing history, no other apps.
- **Explicit consent.** Participation is opt-in; the agent shows what it is doing at all times; pause and uninstall are one click. The agent never secretly uses a GPU and never claims a machine is earning when it is merely connected.
- **Encrypted communications (planned).** All coordinator traffic over TLS; API keys authenticated per request. TLS is planned for the production coordinator — the local prototype uses plain HTTP on localhost only.
- **API key hashing.** Keys are stored as SHA-256 hashes with a secret prefix; plaintext keys are shown once at issuance and never stored. See `docs/SECURITY.md`.
- **Signed updates (planned).** Agent updates will be signed; unsigned updates are rejected. Not yet implemented — no auto-update exists in the prototype.
- **Emergency shutdown.** The coordinator can halt a worker; the user can kill the agent locally at any time.
- **Workload validation.** Prompts are validated (size limits, content policy) before dispatch; oversized or malformed requests are rejected at the gateway, not on the worker.

## What is not yet built

- Real TLS coordinator, real worker registry, real model loading.
- Signed updates, sandbox enforcement beyond process boundaries.
- Production FastAPI gateway (stdlib prototype only).
- Supabase database (schema exists, not applied).
