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

> **NO RESULTS YET — no benchmarks have been run.** This table is intentionally empty. It will only gain rows from real measured runs with hardware, model, quant, date, and method recorded. Any figure shown anywhere else (marketing, landing page, social posts) that is not in this table is a target or demo figure and must be labelled as such.

| Date | Hardware | Model | Quant | Prompt set | Tokens/sec | TTFT (ms) | Total (ms) | VRAM (GB) | GPU util % | Cost / 1M out tokens | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — | — | — | — | — |

## Comparison with established providers

Once real rows exist, this section will compare our measured cost per 1M tokens against published per-token pricing from Together AI, Fireworks AI, and Hyperbolic — using their public pricing pages, dated, and noting that datacentre pricing and consumer-GPU pricing are not directly comparable (different reliability, latency, and scale). No comparison will be published until we have at least one real row.
