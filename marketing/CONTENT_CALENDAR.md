# Nodefield — Marketing Content Calendar

**Budget: $0. Rule throughout: no fake users, no fake benchmarks, no fake earnings, no hype numbers. If we haven't measured it, we say so or say nothing. One account per platform; never spam; read each community's rules before posting.**

## 30-day X content calendar

One post idea per day. Mix: dev updates (real progress only), explainers, questions to the community, and honest "what we learned" posts. No post claims a result we haven't measured.

| Day | Post idea |
|---|---|
| 1 | Launch thread: what Nodefield is, why idle GPUs, what we're building first. Link to repo. |
| 2 | Explainer: what does "inference" actually mean, and why does it need GPUs? |
| 3 | Dev update: landing page is live locally — screenshot, repo link, what's next. |
| 4 | Explainer: Q4 quantisation in plain English — why a 8B model fits on a gaming GPU. |
| 5 | Question: what GPU do you have, and how many hours a day is it idle? (Poll.) |
| 6 | Dev update: waitlist API working locally — what the registration flow collects and why. |
| 7 | Explainer: OpenAI-compatible APIs — why swapping a base URL matters. |
| 8 | Honest post: what we don't know yet (can consumer GPUs beat datacentre inference on cost?). |
| 9 | Explainer: tokens/sec vs. time-to-first-token — the two numbers that decide inference cost. |
| 10 | Dev update: scheduler skeleton — job states, how matching will work. |
| 11 | Explainer: VRAM — why 8GB vs 12GB vs 24GB decides which models you can run. |
| 12 | Question: would you share spare GPU time if payout was per completed job? What would you need to trust it? |
| 13 | Explainer: llama.cpp vs vLLM — when each makes sense on consumer hardware. |
| 14 | Dev update: pricing engine — what goes into cost per 1M tokens (electricity, failures, commission). |
| 15 | Explainer: why we are NOT splitting one model across the internet (latency, reliability). |
| 16 | Honest post: competitor price snapshots we found, and why we won't quote them as our own. |
| 17 | Explainer: Apache-2.0 vs Llama Community License — why model licences matter. |
| 18 | Dev update: agent prototype — hardware detection and the dashboard. |
| 19 | Question: what would make you try a new inference API — price, speed, models, or something else? |
| 20 | Explainer: the economics of an idle RTX 4070 — electricity cost vs. potential payout (labelled estimate, assumptions shown). |
| 21 | Dev update: first real model run — or an honest post about why it hasn't happened yet. |
| 22 | Explainer: rate limiting and API keys — how we hash keys and why plaintext storage is never OK. |
| 23 | Honest post: our benchmark table is still empty, and why we won't fill it with guesses. |
| 24 | Explainer: what "sandboxed inference" means — why customers never run code on your machine. |
| 25 | Dev update: Discord server is live (if true) — what channels exist, come say hi. |
| 26 | Question: which model should we support after the first five? |
| 27 | Explainer: batch vs. priority inference — different prices for different urgency. |
| 28 | Dev update: roadmap check-in — which Phase 1 exit criteria are met, which aren't. |
| 29 | Honest post: the hardest problem so far, and what we're doing about it. |
| 30 | Month-in-review thread: what shipped, what didn't, what's next. Link to PROJECT_STATUS.md. |

## Reddit — 10 educational post outlines

**Rules first: read each subreddit's rules before posting, check whether self-promotion is allowed, never spam, one account only, no cross-posting the same thing to many subs at once. These are outlines, not copy-paste posts — adapt tone and depth to each community.**

1. **Unused GPU economics** (r/LocalLLaMA, r/homelab): what a gaming GPU costs per idle hour in electricity, and the arithmetic of sharing spare capacity. Label all figures as estimates with assumptions.
2. **Quantized models explained** (r/LocalLLaMA): Q4 vs Q8 vs FP16 — VRAM, speed, quality trade-offs, with a simple table.
3. **Consumer GPU inference: what actually fits** (r/buildapc, r/LocalLLaMA): which models fit 8/12/16/24 GB cards, and why context length matters as much as model size.
4. **llama.cpp on a gaming PC: a beginner's walkthrough** (r/LocalLLaMA, r/selfhosted): getting a first local model running, common errors.
5. **Time-to-first-token matters more than you think** (r/MachineLearning, r/LocalLLaMA): why TTFT decides chat UX and how it is measured.
6. **Why distributed inference is hard** (r/MachineLearning, r/homelab): latency, reliability, and why we assign whole requests to one machine instead of splitting models.
7. **The real cost of an inference API call** (r/artificial, r/LocalLLaMA): electricity, hardware amortisation, failure rates — the full cost stack.
8. **Open-weight model licences, plainly explained** (r/opensource, r/LocalLLaMA): Apache-2.0 vs Llama Community License and what they mean for hosting.
9. **Building a GPU agent users can trust** (r/selfhosted, r/homelab): sandboxing, pause/uninstall, no arbitrary code — the security design.
10. **What we learned building an inference marketplace on $0** (r/startups, r/SideProject): honest build log — what worked, what didn't, what we'd do differently. Only post once there is a real thing to show.

Target communities: r/LocalLLaMA, r/homelab, r/selfhosted, r/buildapc, r/MachineLearning, r/artificial, r/opensource, r/startups, r/SideProject. Study each one's rules first; several ban self-promotion outright.

## YouTube

### 10 short-video concepts (30–60s)

1. "Your GPU is idle 20 hours a day. Here's what that means."
2. "Q4 quantisation in 60 seconds."
3. "What is inference? (No jargon.)"
4. "8GB vs 24GB VRAM: which models fit?"
5. "We built an inference API with $0 — here's the stack."
6. "Time to first token, explained with a stopwatch."
7. "Why we don't split models across the internet."
8. "How API keys should be stored (and how they shouldn't)."
9. "Our benchmark table is empty — on purpose."
10. "One click to pause: the agent dashboard."

### 5 technical demonstration concepts

1. First real model run: Qwen3-4B answering through our API, screen-recorded, with tokens/sec on screen.
2. Agent dashboard walkthrough: detection, benchmark, pause, uninstall.
3. Scheduler demo: a request routed to a worker, job states visible live.
4. Benchmark run, start to finish: method, hardware, raw numbers.
5. Pricing engine: from measured electricity cost to cost per 1M tokens.

### 3 project introduction scripts (outlines)

1. **"What is Nodefield?" (2 min):** the problem (idle GPUs, expensive inference), the idea (marketplace), the honest state (prototype, no live network yet), the ask (join the waitlist, run the agent when beta opens).
2. **"How it works" (3 min):** developer sends a request → gateway → scheduler → your GPU → tokens back; what the agent does and doesn't do; security in plain language.
3. **"Why we're building in public" (2 min):** $0 budget, open source, empty benchmark table, what we will and won't claim.

Prioritise screen recordings and actual product demonstrations over talking-head hype. No burned-in claims we can't back up.

## Hacker News — Show HN draft

> **UPDATED 22 Nov 2026: the draft now lives in `marketing/SHOW_HN.md`
> (real numbers, remote-worker proof). The draft below is superseded — do
> not post from here.**

**Title:** Show HN: Nodefield — inference API on idle consumer GPUs

**Body (draft):** We're building an open marketplace for AI inference on spare consumer GPUs. Developers call an OpenAI-compatible API; GPU owners run a small agent and get paid per completed job. Small quantized open-weight models first (Qwen3, Mistral, Llama), whole-request scheduling, no token, Apache-2.0 code. Currently: [honest state at time of posting — e.g. "one model serving on a test machine, benchmarks at <link>"]. Repo: <link>. We'd love feedback on: the scheduling approach, the economics (our measured cost per 1M tokens is $X — is that competitive?), and what would make you trust a contributor agent on your machine.

Update the bracketed honest-state line at publish time. Never publish with demo data presented as live.

## Product Hunt — assets checklist

> **NOT READY — do not launch until users can actually use the service.**

- [ ] Product name, tagline, description (final, post trademark check)
- [ ] Logo (SVG + PNG, light/dark)
- [ ] Screenshots of the real product (dashboard, playground, agent) — no mockups presented as product
- [ ] Demo video (real product, screen-recorded)
- [ ] First comment from the maker (honest state, what works, what's next)
- [ ] Pricing page live with real or clearly labelled beta pricing
- [ ] At least one working signup path a hunter can complete the same day
