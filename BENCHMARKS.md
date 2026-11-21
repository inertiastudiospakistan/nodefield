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
