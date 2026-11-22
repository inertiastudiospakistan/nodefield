# Nodefield — Economics: what can this earn, and what could it sell for?

**Written 22 Nov 2026. All figures from measured runs or stated assumptions —
nothing here is a promise. Prices are the proposed tiers in
`backend/api/pricing.py` (Economy $0.15/$0.60, Standard $0.30/$1.20,
Priority $0.60/$2.40 per 1M input/output tokens; 80% provider / 20%
platform split). Competitor prices are third-party snapshots, labelled as
such — verify on the providers' own pages before launch.**

## 1. Unit economics — one GPU (measured)

Basis: Qwen3-8B Q4_K_M on a Tesla T4, **28.88 tokens/sec** through the public
API (Run 4, 22 Nov 2026).

| Item | Value |
|---|---|
| Output tokens per hour at 100% utilisation | 28.88 × 3,600 ≈ **104,000 (≈0.104M)** |
| Gross revenue per GPU-hour at Standard ($1.20/1M out) | 0.104 × $1.20 ≈ **$0.125/hr** (+ ~$0.01–0.02/hr input tokens → **~$0.14/hr**) |
| Provider share (80%) | **~$0.11/hr** before electricity |
| Platform share (20%) | **~$0.028/hr** per GPU |
| Provider electricity (250–400 W rig, $0.15/kWh) | $0.04–0.06/hr |
| **Provider net, 100% utilisation** | **~$0.05–0.07/hr → $36–50/month** |
| **Provider net, realistic 25% utilisation** | **~$9–13/month per T4-class GPU** |

An RTX 4090 is roughly 2× a T4 on 8B models (estimate, not measured) —
~$20–25/month at 25% utilisation. A bigger model (14B, 70B) earns more
per token in absolute dollars but far fewer tokens per second, so the
per-hour figure does not scale up with model size.

**The honest provider pitch is therefore modest:** tens of dollars a month
for hardware you already own and leave on — not a salary, not mining-era
money. Anyone promising a GPU owner hundreds a month from this is lying.
The FAQ already says we don't know yet; these numbers are the first
evidence-based range, and they must be labelled as estimates until real
beta data exists.

## 2. The uncomfortable finding — our prices vs. datacentre inference

Third-party snapshots (Nov 2026, verify before launch):

| Provider | Llama 3.1 8B, $/1M tokens |
|---|---|
| Together AI | **$0.18** in / **$0.18** out |
| Fireworks AI | **$0.20** / **$0.20** |
| Groq | **$0.05** in / **$0.08** out |
| Cerebras | **$0.10** / **$0.10** |
| DeepInfra | **$0.02** in / **$0.04** out |

Our proposed Standard is **$0.30 in / $1.20 out** — the output price is
**6.7× Together's** and **15× Groq's**. Even Economy ($0.60 out) is 3.3×
Together. Datacentre H100s serve 8B models at 10–30× the throughput per
GPU, so they win commodity 8B chat on price and always will.

**Implication: Nodefield cannot compete on "cheaper 8B chat".** The proposed
pricing must be revalidated before launch. The options:

- **Reprice:** make Economy the headline tier, or price per model against
  the datacentre rate with a small discount, not a premium.
- **Compete where datacentres don't:** custom / fine-tuned models, models
  the big providers don't serve, uncensored models, privacy (your data never
  touches a big cloud), batch/off-peak pricing, regions the big clouds
  serve badly.
- **Sell the story, not the token:** open marketplace, provider earnings,
  no lock-in — but that only works if the price is at least close.

Do not launch with Standard pricing as-is. The pricing engine supports
per-model prices; use it.

## 3. Platform revenue scenarios (Standard pricing, T4-class GPUs)

| GPUs | Utilisation | Gross / month | Platform (20%) / month | Platform / year |
|---|---|---|---|---|
| 100 | 25% | $2,520 | ~$500 | ~$6k |
| 200 | 25% | $5,040 | ~$1,000 | ~$12k |
| 1,000 | 25% | $25,200 | ~$5,000 | ~$60k |
| 1,000 | 50% | $50,400 | ~$10,000 | ~$120k |
| 10,000 | 25% | $252,000 | ~$50,000 | ~$600k |

Reading it backwards: **$1,000/month of platform revenue needs ~200 GPUs
at 25% utilisation; $10,000/month needs ~2,000.** Utilisation is the whole
game — a GPU that is merely connected earns nothing, and neither does the
platform. These are scenarios from the measured throughput, not forecasts.

## 4. What could it sell for?

**Today: essentially $0.** No users, no revenue, no persistent workers,
provisional name, and the code is Apache-2.0 open source — anyone can fork
it, so the code itself is not a sellable moat. What is sellable in future is
the network, the brand and the users.

Illustrative scenarios only (early-stage marketplaces are typically valued
at roughly 5–10× annual recurring revenue when growing fast — a rule of
thumb, not a promise):

| State | Indicative value |
|---|---|
| Pre-revenue, no users (today) | ~$0 (assets only: domain, repo) |
| $5k MRR, growing ($60k ARR) | ~$0.3–0.6M (pre-seed territory) |
| $50k MRR ($600k ARR) | ~$3–6M |
| $500k MRR ($6M ARR) | ~$30–60M+ |

A strategic sale (to Together, RunPod, Vast, Akash, io.net or a cloud
provider) would be priced on the network and the user base, not the code —
buyers in this space acquire distribution and GPU supply. If it never gets
users, it is unsellable at any price. If it gets 10,000 GPUs and real
volume, it is a real company and the sale conversation starts itself.

## 5. What to do with this

1. **Revalidate pricing before launch** (Section 2) — the current tiers
   would lose on price to every datacentre provider.
2. **Measure real provider earnings in the beta** — replace the estimates
   in Section 1 with beta data before ever quoting earnings publicly.
3. **Do not quote a valuation to anyone** until there is revenue; the
   numbers in Section 4 are for the founder's planning only.
4. **The earning engine is volume × utilisation**, not price per token.
   Everything in the launch plan serves that: more GPUs, more developers,
   higher utilisation.
