# Nodefield Backend (prototype)

Python standard library only — **zero dependencies, nothing to install**.
Runs anywhere with Python 3.11+ (`python3 server.py`).

## Run

```bash
cd backend/api
python3 server.py            # listens on 0.0.0.0:8787
python3 server.py --port 9000
```

Stop with Ctrl+C (clean shutdown). Each request is logged to stdout.

## Layout

```
backend/
  api/
    server.py               # single-file HTTP API (port 8787)
    pricing.py              # pricing engine (pure functions)
    gpu_compatibility.py    # GPU compatibility DB + classify()
    gpu_compatibility.json  # same table as JSON, for the frontend
    requirements.txt        # no dependencies (stdlib only)
    data/nodefield.db       # SQLite DB, created on first run
  scheduler/
    scheduler.py            # worker scoring / job assignment / registry
agent/
  agent.py                  # contributor agent prototype
  config.json               # resource limits + paused flag
  README.md                 # agent security rules
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | `{"status":"ok","service":"nodefield-api","mode":"demo","gpu_workers_online":0,"version":"0.1.0"}` |
| GET | `/api/stats` | Real counts from SQLite (providers, developers, keys, jobs) + demo note |
| GET | `/api/models` | The 5 launch-candidate models (all `status: "planned"`) |
| POST | `/api/waitlist` | Provider/developer waitlist signup → `201 {"ok":true,"id":<int>,"kind":...}` |
| POST | `/api/keys` | Create an API key (full key shown **once**) |
| GET | `/api/keys?email=...` | List key prefix/label/created_at only — never hashes or full keys |
| POST | `/v1/chat/completions` | OpenAI-compatible chat (demo response, see below) |
| GET/POST | `/api/jobs` | List / create jobs (assigned via the scheduler module) |
| GET/POST | `/api/workers` | List workers / worker heartbeat (used by the agent) |

## Test with curl

```bash
# Health + models
curl localhost:8787/api/health
curl localhost:8787/api/models

# Waitlist signup (provider)
curl -X POST localhost:8787/api/waitlist -H 'Content-Type: application/json' \
  -d '{"kind":"provider","name":"Ada","email":"ada@example.com","country":"PK",
       "gpu_manufacturer":"NVIDIA","gpu_model":"RTX 3060 12GB","gpu_vram_gb":12,
       "system_ram_gb":32,"os":"Windows 11","internet":"100 Mbps",
       "available_hours":"18:00-23:00","beta_interest":true}'

# Waitlist signup (developer)
curl -X POST localhost:8787/api/waitlist -H 'Content-Type: application/json' \
  -d '{"kind":"developer","email":"dev@example.com","application":"chatbot",
       "monthly_tokens":1000000,"preferred_models":["qwen3-8b"],
       "desired_features":["streaming"]}'

# Create an API key (copy the key — it is never shown again)
curl -X POST localhost:8787/api/keys -H 'Content-Type: application/json' \
  -d '{"email":"dev@example.com","label":"test"}'
# List keys (prefixes only)
curl 'localhost:8787/api/keys?email=dev@example.com'

# Chat completions — demo mode, no key needed
curl -X POST localhost:8787/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"model":"qwen3-8b","messages":[{"role":"user","content":"Hello"}]}'
# Streaming
curl -N -X POST localhost:8787/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"model":"qwen3-8b","messages":[{"role":"user","content":"Hello"}],"stream":true}'
# With a key (replace KEY with the one returned above)
curl -X POST localhost:8787/v1/chat/completions -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer KEY' \
  -d '{"model":"qwen3-8b","messages":[{"role":"user","content":"Hello"}]}'

# Jobs
curl -X POST localhost:8787/api/jobs -H 'Content-Type: application/json' \
  -d '{"model":"qwen3-8b","prompt":"Summarise this.","priority":"standard"}'
curl localhost:8787/api/jobs

# Stats
curl localhost:8787/api/stats
```

## Self-tests (no server needed)

```bash
cd backend/scheduler && python3 -m scheduler   # demo workers, VRAM filter assert
cd backend/api && python3 pricing.py            # worked pricing example
cd backend/api && python3 gpu_compatibility.py  # classify() examples + export JSON
cd agent && python3 agent.py --report           # hardware report for this machine
```

## Where the DB lives

`backend/api/data/nodefield.db` (SQLite, created on first run). It holds
waitlist rows, API-key **hashes** (SHA-256 only — full keys are never
stored), workers, and jobs. Delete the file to reset the demo data.

## Honest limits

- **Demo inference only.** No live GPU worker is connected and no model
  is actually loaded. `/v1/chat/completions` returns a clearly-labelled
  demo message; token counts are word-count approximations, stated as such.
- **No GPU on this machine.** The dev VM has no GPU (`nvidia-smi` absent),
  so the agent reports "no GPU detected" and its benchmark is a CPU
  timing loop only.
- **No real benchmarks or economics yet.** Prices in `pricing.py` are
  provisional launch targets, not measured costs. Nothing here proves
  the marketplace can compete — that needs real hardware benchmarks.
- **No payments.** Keys are issued for testing; no billing, no payouts.
- **Rate limit:** 60 requests/minute per key (or per IP without a key),
  in-memory only (resets on restart).
