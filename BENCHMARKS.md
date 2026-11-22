# Nodefield — Benchmarks

## Methodology

Every benchmark row in this file must come from a **real measured run** and record: hardware, model, quantisation, prompt set, date, and method. No hypothetical numbers, no vendor marketing figures presented as ours, no estimates in the results table.

### Metrics recorded per run

| Metric | Definition |
|---|---|
| Tokens/sec | Output tokens generated per second (steady-state, excluding prompt processing) |
| Time to first token (TTFT) | Milliseconds from request dispatch to first output token |
| Total response time | Milliseconds from request dispatch to final token |
| Input tokens / output tokens | Counted by the model's tokenizer |
| GPU utilisation | Mean % during generation (nvidia-smi / equivalent) |
| VRAM consumption | Peak GB during the run |
| Electricity consumption | Watts measured where possible (wall meter / nvidia-smi power draw); "not measured" if unavailable |
| Cost per 1M input tokens | (Measured operating cost per hour ÷ tokens/hour) × 1,000,000 — operating cost = electricity at local rate + hardware amortisation |
| Cost per 1M output tokens | Same, for output tokens |
| Provider payout / platform commission / gross margin | Computed by the pricing engine from measured cost — only once real costs exist |

### Method

1. Fixed prompt set (same prompts for every model/hardware combination, versioned in the repo).
2. Warm-up run discarded; 3 measured runs; report median.
3. Fixed context length and max output tokens per run; record both.
4. Record ambient facts: GPU model, driver version, llama.cpp/vLLM version, quant (e.g. Q4_K_M), OS, date, operator.
5. Publish the raw log alongside the summary row.

### Planned benchmark script interface (not yet built)

The agent will implement this interface in Phase 2. It does **not** exist yet — do not claim it is built.

```bash
python3 agent/benchmark.py \
  --model Qwen3-8B \
  --quant Q4_K_M \
  --prompt-set prompts/v1.json \
  --max-tokens 256 \
  --runs 3 \
  --out benchmarks/results/2026-12-xx-qwen3-8b-rtx4070.json
```

Output: one JSON file per run with all metrics above, plus a summary row appended to the results table below by hand (with the JSON file linked as evidence).

## Results

> **First real result recorded 21 Nov 2026** (see row below). All figures are measured, not estimated. One honest caveat: this is a **single run**, not the 3-run median the methodology calls for — treat it as a first data point, not a final number.

| Date | Hardware | Model | Quant | Prompt set | Tokens/sec | TTFT (ms) | Total (ms) | VRAM (GB) | GPU util % | Cost / 1M out tokens | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-21 | Tesla T4 (15,360 MiB), Google Colab free | Qwen3-8B | Q4_K_M | 5 fixed prompts, 128 max tokens, temp 0 | **35.27** (mean of 5) | **156** (mean) | ~3,600 (mean) | 5.2 | not measured | not measured | `backend/benchmarks/results/2026-11-21-qwen3-8b-t4-colab.json` |
| 2026-11-21 | **No GPU — dev VM CPU only** (4 vCPU visible, 1.5 vCPU quota, 7.7 GB RAM) | Qwen3-4B | Q4_K_M | 1 API request, 128 max tokens, temp 0 | **6.44** (decode phase) | **5,744** | 15,700 | ~2.6 (model file, mmap) | n/a (CPU) | not measured | `backend/benchmarks/results/2026-11-21-qwen3-4b-cpu-local.json` |
| 2026-11-22 | Tesla T4 (15,360 MiB), Google Colab free, **via the Nodefield API** | Qwen3-8B | Q4_K_M | 1 API request, 128 max tokens, temp 0 | **31.29** | **650** | ~2,700 (worker) | 5.1 | not measured | not measured | `backend/benchmarks/results/2026-11-22-qwen3-8b-t4-api.json` (transcribed from run report) |

### Run 3 — first GPU request through the Nodefield API, Qwen3-8B Q4_K_M on Colab T4 (22 Nov 2026, 08:13 UTC)

- **Path:** API server + worker both on the same Colab T4 VM (no tunnel — Cloudflare quick tunnels and localtunnel both fail from the dev VM, see below). `POST /v1/chat/completions` → job queue → worker `colab-t4-1` → real reply with `"nodefield": {"source": "real", "job_id": 1, "worker_id": "colab-t4-1", "model": "qwen3-8b", "tokens_per_second": 31.29, "ttft_ms": 649.9}`. Reply id `chatcmpl-real-d549200e649171f1`, 33 prompt / 64 completion tokens.
- **Reply (real model output):** "Photosynthesis is the process by which plants, algae, and some bacteria convert light energy into chemical energy, using carbon dioxide and water to produce glucose and oxygen. This process occurs primarily in the chloroplasts of plant cells and is essential for life on Earth as it provides oxygen and forms the base of the food chain."
- **GPU:** Tesla T4, 68°C, 30 W / 70 W, 5,071 MiB / 15,360 MiB used with the model loaded. Model load 25.9 s (fresh 4,794.9 MB download in 51 s — no cache hit this time).
- **Streaming:** verified on the third attempt — SSE chunks, `finish_reason: "stop"`, then `[DONE]`; job 3, 64 tokens in 2.2 s, 29.81 tok/s, TTFT 0.39 s. First streaming attempt hung ~4 min with no SSE delivered even though the worker completed the job — an unexplained transient API stall, recorded in KNOWN_ISSUES.md.
- **Bug caught and fixed the same day:** `--model qwen3-8b` alone downloaded the **4B** model, because `--model` was only a label and the worker always defaulted to the 4B repo/file. No request went to the wrong model (caught before submitting). Fixed with a `MODEL_MAP` in `agent/worker.py` — `--model` now selects the repo/file, and unknown models exit with an error instead of serving the wrong one. Verified locally: `--model qwen3-8b --no-download` now correctly looks for `Qwen3-8B-Q4_K_M.gguf`.
- **Caveats:** single request, not a 3-run median; the API and worker ran on the same throwaway VM (not a remote worker over the network); no power/cost measured. The tunnel failure means a remote worker over the public internet is still unproven — the next step is a public API host (e.g. Hugging Face Space) or a tunnel from a machine whose egress is not filtered.

### Run 2 — first REAL end-to-end API request, Qwen3-4B Q4_K_M on CPU (21 Nov 2026, 18:48 UTC)

- **Path:** `POST /v1/chat/completions` → job queue (SQLite) → `agent/worker.py` polls, claims, runs llama.cpp → `POST /api/jobs/<id>/result` → API returns the real reply with `"nodefield": {"source": "real", "job_id": 3, "worker_id": "local-cpu-1", "tokens_per_second": 6.44, "ttft_ms": 5744.2}`. Job 3 in the API database records model, prompt, status, worker, timing, token counts and `result_source: "real"`.
- **Request:** "Explain photosynthesis in two sentences.", max_tokens 128, temp 0. **Reply (real model output, 64 tokens):** "Photosynthesis is the process by which plants, algae, and some bacteria convert light energy, usually from the sun, into chemical energy in the form of glucose, using carbon dioxide and water. This process occurs in the chloroplasts of plant cells and is essential for producing oxygen and forming the basis of most food chains."
- **Runtime:** llama-cpp-python 0.3.37 (built from source — no prebuilt wheel was used for this Python/platform), worker `n_threads=2`, `n_ctx=1024`, `n_gpu_layers=0`. Model load 11.5 s (warm page cache; 27.9 s cold). Model file sha256 `7485fe6f…fdf5`, 2,497,280,256 bytes.
- **Measured:** prompt 33 tokens (tokenizer-counted, includes the empty `<think></think>` block the worker adds for Qwen3 to disable reasoning output), completion 64 tokens, TTFT 5,744 ms, **6.44 tok/s** (decode phase: completion tokens ÷ (total − TTFT)), job total 15.7 s, curl wall time 16.3 s.
- **Caveats, stated plainly:**
  - Single request, not the 5-prompt set and not a 3-run median.
  - CPU-only and slow: 6.44 tok/s is usable for a demo but far below the T4's 35.27 tok/s. The bottleneck is the 1.5 vCPU quota on this VM, not the model.
  - An earlier run the same evening with the default `n_threads=4` managed only **1.41 tok/s** (TTFT 8.3 s) and the reply contained a `<think>` reasoning block, because the worker's first ChatML prompt did not suppress Qwen3 thinking. Both fixes are in the worker now (2 threads, empty think block for Qwen3). The 1.41 number is real and is kept here, not hidden.
  - Demo fallback verified with the worker stopped: the same request returns the unchanged demo reply (no `nodefield` field). Streaming verified with a real worker: SSE chunks + `[DONE]`.
  - GPU utilisation, power draw and cost per 1M tokens were **not measured**.

### Run 1 — Qwen3-8B Q4_K_M on Colab T4 (21 Nov 2026, 18:00 UTC)

- **Runtime:** llama-cpp-python (llama.cpp, CUDA), Python 3.13.16. Model load: 21.7 s. VRAM after load: 5,187 MiB of 15,360 MiB.
- **Script:** `backend/benchmarks/benchmark_qwen3_8b.py` (run unmodified; two earlier attempts failed on missing CUDA libraries — fixed by adding `/usr/lib64-nvidia` and the pip NVIDIA directories to `LD_LIBRARY_PATH`, no script change).
- **Per-prompt (all 128 output tokens):** photosynthesis 32.50 tok/s, TTFT 439 ms; Fibonacci 35.58 tok/s, TTFT 160 ms; France capital 36.26 tok/s, TTFT 70 ms; Hamlet 36.06 tok/s, TTFT 46 ms; groceries 35.94 tok/s, TTFT 63 ms.
- **Caveats, stated plainly:**
  - The model file was already in the Hugging Face cache on that recycled Colab VM (download took 0.3 s) — that is a cache hit, not a fresh ~5 GB download.
  - This measures **throughput only, not quality**: at temp 0 with a fixed 128 tokens the outputs ramble and repeat (e.g. the Fibonacci answer loops the same sentence; the France answer drifts into follow-up questions). A quality eval is a separate job.
  - GPU utilisation, power draw and cost per 1M tokens were **not measured** — those columns stay empty until a run measures them.
  - Single run, not 3-run median.
- **What this means:** an 8B model at Q4 fits comfortably on a 15 GB T4 (~5.2 GB used) and generates ~35 tok/s — fast enough for interactive chat on a free-tier GPU. It says nothing yet about cost, reliability, or sustained multi-user serving.
- **Kaggle note:** the same benchmark was first attempted on Kaggle (account AdilMehmoodWarraich created 21 Nov, notebook drafted) but Kaggle locks GPU + Internet behind phone verification on a new account, so the run moved to Colab. The Kaggle notebook remains as a draft if phone verification is ever completed.

## Comparison with established providers

Once real rows exist, this section will compare our measured cost per 1M tokens against published per-token pricing from Together AI, Fireworks AI, and Hyperbolic — using their public pricing pages, dated, and noting that datacentre pricing and consumer-GPU pricing are not directly comparable (different reliability, latency, and scale). No comparison will be published until we have at least one real row.
