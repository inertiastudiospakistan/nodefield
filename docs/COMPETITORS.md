# Nodefield — Competitor Research

**Researched: November 2026. All prices below are third-party snapshots — verify on each provider's pricing page before quoting them to anyone. Prices change; these figures will go stale.**

## How Nodefield differs (the short version)

Every competitor below is either (a) a rental marketplace for whole GPUs by the hour, (b) a managed inference API on datacentre hardware, or (c) a token-based decentralised network. Nodefield's intended difference: **idle consumer GPUs** (gaming PCs, workstations) serving **small quantized open-weight models** through an **OpenAI-compatible API**, with **no token** and payouts in fiat/credits for completed work only. That difference is a hypothesis until we have measured costs — see `BENCHMARKS.md`.

## Competitor table

| Provider | What they do | Indicative pricing (snapshot, verify) | How we differ |
|---|---|---|---|
| **Vast.ai** | GPU rental marketplace; hosts set prices; interruptible instances cheaper; users rent whole GPUs/servers by the hour | H100 from ~$1.73/hr per third-party snapshot, Oct 2026; interruptible cheaper than on-demand | Vast rents whole GPUs to people who manage them; we sell inference by the token on idle consumer cards, no server management for the buyer |
| **RunPod** | GPU cloud: serverless + pods; per-second billing; community + secure cloud pools | RTX 4090 ~$0.89/hr; H100 SXM ~$3.99/hr (per-second billing) | RunPod targets developers who run their own workloads on rented GPUs; we target developers who just want an API, and owners who just want to share spare capacity |
| **Together AI** | Managed inference API + GPU clusters; open models served on datacentre GPUs | H100 $3.99/hr on-demand, $1.99/hr preemptible (cluster pricing) | Together runs datacentre hardware; we run consumer hardware. Their inference API is the closest product analogue — our bet is lower cost from spare capacity |
| **Lambda** | GPU cloud (1-click clusters, on-demand instances); datacentre H100/A100 | H100 8x instances ~$3.99/hr per GPU (on-demand) | Lambda is datacentre rental for training and large inference; we are small-model inference on consumer GPUs |
| **Modal** | Serverless GPU compute; per-second billing; Python-native; free credit tier | Per-second billing; ~$30/month free credit | Modal is general serverless compute; we are a narrow inference API with a contributor marketplace |
| **Akash** | Decentralised cloud marketplace; reverse-auction bidding for compute; token-based (AKT) | Pricing set by reverse auction; network reported ~334 average available GPUs in Q1 2026 per third-party review | Akash is token-based and general compute; we are fiat/credits, inference-only, no token (ADR-006) |
| **io.net** | Decentralised GPU network; Ray clusters; markets itself on very large GPU counts | Advertised 100k+ GPUs vs **~5–7k verified per reviewers — flag the discrepancy**; do not quote their headline count as fact | io.net's headline GPU count is disputed by independent reviewers; we will not publish unverified network numbers — our dashboard will show only measured, labelled data |
| **Render** | 3D rendering (Render Network) expanding toward AI compute; token-based | Token-based pricing | Rendering-first, token-based; we are inference-first, fiat/credits |
| **Fireworks AI** | Managed inference API for open models; fast serving, function calling | Per-token inference pricing (varies by model) | Managed API on datacentre GPUs — closest competitor on the demand side; our cost edge, if any, must come from consumer spare capacity and be proven by benchmarks |
| **Hyperbolic** | Managed inference API + decentralised GPU network for open models | Per-token inference pricing (varies by model) | Closest overall analogue (decentralised GPUs + inference API); differentiator is our focus on small quantized models on consumer cards and radical transparency about measured performance |

## Gaps and risks this research surfaces

1. **The managed inference APIs (Together, Fireworks, Hyperbolic) already serve open models cheaply on datacentre hardware.** Our cost advantage is not guaranteed — it must be proven with real benchmarks (tokens/sec per dollar, including electricity and failure rates). If consumer GPUs can't beat datacentre inference on cost per 1M tokens, the business model fails. That is the Phase 4 question.
2. **Headline GPU counts in this space are unreliable** (see io.net above). We will never publish a network size we haven't measured.
3. **Vast.ai and RunPod already serve the "cheap GPU" demand well** for users willing to manage a server. Our buyer must be the developer who wants an API, not a server.
4. **Token-based networks (Akash, Render, io.net) carry regulatory and trust baggage** we avoid by design (ADR-006) — but they also have funding and liquidity we don't. Our $0-budget path is slower by necessity.

## Sources and method

- Provider pricing pages and third-party pricing snapshots, October–November 2026.
- Third-party reviews of Akash network size (Q1 2026) and io.net verified GPU counts.
- No provider was contacted; no prices were verified by a live purchase. **Re-check every figure on the provider's own pricing page before using it in marketing or sales material.**
