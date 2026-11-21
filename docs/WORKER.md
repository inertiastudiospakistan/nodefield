# Nodefield Worker — running a real model

The worker (`agent/worker.py`) is the piece that turns the demo API into
real inference. It polls the API for pending jobs, runs them through a
local GGUF model with llama-cpp-python, and posts the result back. The
same code runs on a CPU-only machine and on a GPU worker (e.g. a Colab
T4) — GPU offload is decided at runtime from hardware detection, no
code changes.

## How it works

```
Developer ──POST /v1/chat/completions──▶ API (port 8787)
                                        │ creates job (pending)
                                        │ waits up to 150s
Worker ◀── POST /api/workers/claim ─────┤ (oldest pending job
     │                                   │  for a model it serves)
     │ runs model (llama.cpp)            │
     └── POST /api/jobs/<id>/result ────▶│ job completed (real)
API ──returns real output + nodefield ──▶ Developer
     {"source": "real", "tokens_per_second": …, "ttft_ms": …}
```

- **Job queue:** plain HTTP + the API's SQLite `jobs` table. States:
  `pending → assigned → running → completed | failed`, with a 180 s
  timeout and 2 retries — a claimed job that is never finished is
  re-queued for another worker.
- **Routing:** the API only routes to a worker when it heartbeated
  within the last 120 s **and** lists the requested model as loaded.
  Otherwise the caller gets the existing clearly-labelled demo reply —
  never an error, never a fake "real" reply.
- **Honesty:** a reply is labelled `real` only when the model generated
  it. Token counts come from the model's own tokenizer; tok/s and TTFT
  are measured wall-clock. A worker that cannot serve a job refuses it
  (it never claims models it hasn't loaded; if model load fails it exits
  instead of claiming anything).
- **Safety:** the worker never executes arbitrary code from the network.
  It accepts only chat messages and returns generated text.

## Running locally (CPU)

```bash
# 1. venv + the worker's only dependency (the API stays stdlib-only)
python3 -m venv .venv
.venv/bin/pip install llama-cpp-python

# 2. start the API
python3 backend/api/server.py          # port 8787

# 3. start the worker (downloads Qwen3-4B Q4_K_M, ~2.6 GB, on first run)
.venv/bin/python agent/worker.py --model qwen3-4b

# 4. test (create a key first: POST /api/keys {"email": "you@example.com"})
curl -s http://localhost:8787/v1/chat/completions \
  -H "Authorization: Bearer <key>" -H "Content-Type: application/json" \
  -d '{"model": "qwen3-4b",
       "messages": [{"role": "user",
                     "content": "Explain photosynthesis in two sentences."}],
       "max_tokens": 128}'
```

Expected: a real model answer plus
`"nodefield": {"source": "real", "job_id": …, "worker_id": …,
"tokens_per_second": …, "ttft_ms": …}`. Stop the worker and repeat the
same curl to see the demo fallback.

Options: `--api URL`, `--model qwen3-4b|qwen3-8b`, `--n-ctx 1024`
(smaller = less RAM on CPU), `--n-gpu-layers -1|0`,
`--repo/--file` to serve a different GGUF, `--once` to process a
single job then exit, `--no-download` to fail instead of downloading.
Env vars `NODEFIELD_API_URL`, `NODEFIELD_MODEL`, `NODEFIELD_WORKER_ID`,
`NODEFIELD_MODEL_DIR`, `NODEFIELD_HF_REPO`, `NODEFIELD_HF_FILE` do the
same. Model files live in `agent/models/` (gitignored — never committed).

## Running on a Colab T4 (GPU worker)

The same worker, pointed at a reachable API. The local API on
`localhost:8787` is **not** reachable from Colab, so expose it first.

1. **Expose the local API** with a free Cloudflare Tunnel (do this on
   the machine running the API; no tunnel is set up in this repo):
   ```bash
   cloudflared tunnel --url http://localhost:8787
   # note the https://<name>.trycloudflare.com URL it prints
   ```
   The tunnel URL becomes the worker's `--api` value. Keep the tunnel
   running for the whole session — the URL is temporary and changes on
   restart.
2. **Open the benchmark notebook** (it already has the Colab runtime
   working): https://colab.research.google.com/drive/1mn4d9JBohZmXj3hVeDe6cAGZh34QtCq9
   — or start a fresh notebook. Runtime → Change runtime type →
   Hardware accelerator **GPU (T4)**.
3. **In a notebook cell**, install the worker dependency and fetch the
   worker code:
   ```python
   !pip install -q llama-cpp-python --extra-index-url \
       https://abetlen.github.io/llama-cpp-python/whl/cu124
   !git clone https://github.com/inertiastudiospakistan/nodefield
   ```
4. **Run the worker** (replace the tunnel URL with yours):
   ```python
   !cd nodefield && python agent/worker.py --api https://<name>.trycloudflare.com \
       --model qwen3-8b --worker-id colab-t4-1
   ```
   With a GPU present the worker offloads all layers (`n_gpu_layers=-1`)
   automatically; Qwen3-8B Q4_K_M (~5 GB) is the default model for the
   GPU path — override with `--repo Qwen/Qwen3-8B-GGUF --file
   Qwen3-8B-Q4_K_M.gguf --model qwen3-8b`. First run downloads the
   model (~5 GB) into the notebook VM.
5. **Submit a request** to your local API as above with
   `"model": "qwen3-8b"`. The response should carry
   `"nodefield": {"source": "real", …}` with the T4's tok/s and TTFT.
6. **Stop cleanly:** interrupt the notebook cell (or Runtime →
   Interrupt execution). The worker stops polling; any in-flight job is
   re-queued by the API after its 180 s timeout.

Notes and limits (stated plainly):

- The tunnel URL is public while it runs: anyone who guesses it can
  submit jobs to your local API. This is a **demo/test setup only** —
  do not expose it beyond a test session, and do not put real keys or
  paid workloads behind it. Production needs TLS + auth on the
  coordinator (see `docs/ARCHITECTURE.md`).
- Colab's free tier is for interactive experimentation; do not assume
  it permits persistent public endpoints or commercial production
  workloads. The notebook VM is recycled — the downloaded model and
  the worker disappear with it.
- The worker cell blocks the notebook while it runs; keep the tab open
  for the whole test session.
