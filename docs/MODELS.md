# Nodefield — Launch Models

**Status: planned, not validated. No benchmarks have been run yet — see `BENCHMARKS.md`. Model choice is provisional and will change based on measured performance and licence review.**

## Selection principles

1. **Small quantized models first.** A model must fit and run well on a consumer GPU (8–24 GB VRAM). If it needs a datacentre card, it is not a launch model.
2. **Licence must permit the intended usage.** Commercial hosting/serving is the intended usage — check each licence, don't assume.
3. **Open weights.** No proprietary API-wrapped models.
4. **Quality per VRAM.** Prefer models that are strong for their size (Qwen3 and Mistral families lead here).

## Launch models (5)

| Model | Parameters | Licence | Q4 VRAM (approx.) | Min. GPU | Notes |
|---|---|---|---|---|---|
| Qwen3-4B | 4B | Apache 2.0 | ~2.5 GB | 6 GB VRAM | First model to run (Phase 2). Small, fast, permissive licence. |
| Qwen3-8B | 8B | Apache 2.0 | ~5.2 GB | 8 GB VRAM | The workhorse: good quality, fits most gaming GPUs. |
| Qwen3-14B | 14B | Apache 2.0 | ~9.3 GB | 12 GB VRAM | Largest launch model; needs a 12 GB+ card (e.g. RTX 3060 12GB, 4070 Ti). |
| Llama-3.1-8B | 8B | **Llama 3 Community License** | ~5.2 GB | 8 GB VRAM | Strong, widely requested — but licence has a **700M monthly-active-user cap** and other conditions. Needs a founder/legal read before commercial serving. |
| Mistral-7B | 7B | Apache 2.0 | ~4.5 GB | 8 GB VRAM | Permissive licence, well tested in llama.cpp/vLLM. |

Q4 VRAM figures are approximate (weights + minimal overhead; actual usage depends on context length and KV cache — a long context can add several GB). They are planning estimates, not measured results. Measured VRAM per model will be recorded in `BENCHMARKS.md` once runs exist.

### Model categories (per brief)

- **Small (1B–4B):** Qwen3-4B (and later Qwen3-1.7B / Llama-3.2-1B/3B if validated).
- **Medium (7B–8B):** Qwen3-8B, Llama-3.1-8B, Mistral-7B.
- **Larger (12B–14B):** Qwen3-14B.

## Why small quantized models first

- They fit consumer GPUs that actually exist in gaming PCs (8–16 GB VRAM is the common range).
- Q4 quantisation roughly halves VRAM vs. FP16 with a small quality cost, and is well supported by llama.cpp.
- Faster time-to-first-token and higher tokens/sec on modest hardware — which is exactly the cost advantage we need to prove.
- Lower failure modes: fewer OOM kills, shorter model-load times.

## Licences — read before serving

- **Apache 2.0** (Qwen3 family, Mistral-7B): permissive; commercial use, modification, and distribution allowed with attribution. Our code licence (Apache-2.0) aligns with these.
- **Llama 3 Community License** (Llama-3.1-8B): separate licence with conditions, including a 700M MAU threshold above which a separate licence from Meta is required, plus acceptable-use restrictions. It applies **only to the Llama model family**, not to Nodefield's code. Do not serve Llama models commercially until the licence has been reviewed.

## What is NOT yet validated

- No benchmarks have been run for any model on any hardware (see `BENCHMARKS.md` — empty results table).
- Q4 VRAM figures above are estimates from model size, not measurements.
- No model has been loaded by Nodefield code; no inference has been served.
- Model quality (benchmark scores, human eval) has not been evaluated by us — published model-card scores are the vendors', not ours.
- Additional candidates (Qwen3-1.7B, Llama-3.2-3B, Mistral Small, Gemma) are **not** launch models; they are future candidates pending Phase 2 results.
