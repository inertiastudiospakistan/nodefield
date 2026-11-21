# Nodefield — Decisions

Architecture Decision Records. Each entry: context, decision, consequences. Decisions are provisional until Phase 7; revisit when evidence changes.

## ADR-001 — Provisional name: Nodefield

**Context:** The product needs a short, memorable, internationally understandable name related to distributed computing, AI, GPUs, or shared infrastructure, suitable for a serious infrastructure company — not a crypto project.

**Candidate names considered (20 + extras evaluated):**

| Name | Verdict | Reason |
|---|---|---|
| **Nodefield** | **SELECTED (provisional)** | Short, pronounceable, evokes a field of nodes / distributed compute; no obvious live competitor found in initial checks; serious, not crypto-flavoured. |
| InferGrid | REJECTED | Live project at InferGrid.tech; a PyPI package of the same name exists. Collision risk. |
| GridInfer | REJECTED | Too close to InferGrid; confusingly similar, same collision risk. |
| InferMesh | REJECTED | Weak differentiation; "Infer" + mesh naming is crowded in the inference space. |
| VoltMesh | REJECTED | Existing mobility/energy project using the name. |
| VoltGrid | REJECTED | Same "Volt" family as VoltMesh; energy connotations mislead (we are compute, not power). |
| GridMind | REJECTED | Sounds like a generic AI brand; weak link to GPUs/inference. |
| ComputeShare | REJECTED | Descriptive but bland; hard to own as a brand, likely trademark-crowded. |
| GPUGrid | REJECTED | Descriptive, but "GPU" in the name narrows us if we later support other accelerators; also generic. |
| NodeForge | REJECTED | "Forge" is overused in dev-tool branding; also close to existing NodeForge projects. |
| FluxCompute | REJECTED | "Flux" is heavily used (Flux models, FluxCD, Flux framework) — collision and confusion risk. |
| OpenInfer | REJECTED | Descriptive and accurate, but generic; hard to trademark, and "Open" prefix is crowded. |
| TensorShare | REJECTED | "Tensor" is TensorFlow-associated; name is long and generic. |
| IdleCompute | REJECTED | Accurate but uninspiring; "idle" is a weak brand word. |
| CorePool | REJECTED | Sounds like a CPU/threading library, not a marketplace. |
| MeshInfer | REJECTED | Same crowded "Infer" family as InferMesh/GridInfer. |
| WattGrid | REJECTED | Energy connotation again; misleading for a compute marketplace. |
| GridWorks | REJECTED | Generic; multiple existing companies use GridWorks/Gridworks. |
| ComputeMesh | REJECTED | Descriptive but forgettable; crowded naming family. |
| SiliconShare | REJECTED | Long; "silicon" suggests chip manufacturing, not inference. |
| NodePool | REJECTED | Accurate but bland; "pool" suggests mining pools to some readers. |
| CommonCompute | REJECTED | Existing research network uses the name. |

**Decision:** Use **Nodefield** as the provisional name for all Phase 1 work.

**Consequences / open items:** Trademark search and domain-availability check are **still required before launch** and before any public branding commitment (logo lock-in, social handles, paid assets). If the check fails, pick from the shortlist above or re-run naming. Do not purchase a domain without founder approval.

## ADR-002 — Stdlib-only Python backend for the prototype

**Context:** The backend prototype must run anywhere with zero setup friction and zero cost, on machines the team doesn't control.

**Decision:** Prototype backend in Python using only the standard library (no FastAPI, no pip installs) for the waitlist API, demo inference API, and scheduler skeleton.

**Consequences:** Runs with `python3 server.py` and nothing else; trivially portable; but no production-grade framework features (validation, async, OpenAPI). FastAPI is the planned production backend — migrate when the prototype proves the flows, not before. Do not rebuild working prototype code for framework purity.

## ADR-003 — Static frontend, no build step

**Context:** The site must deploy free (Cloudflare Pages / GitHub Pages) and be editable by anyone with a text editor.

**Decision:** Plain HTML/CSS/JS, no Next.js build, no bundler, no framework for Phase 1.

**Consequences:** Fast, free hosting; zero build failures; but no components or SSR. If the product grows a logged-in dashboard with real state, revisit (Next.js + React + Tailwind per the original stack preference). Do not add a build step to fix a content problem.

## ADR-004 — Whole-request scheduling; no model splitting across consumer GPUs

**Context:** Splitting one model across geographically distributed consumer GPUs (tensor/pipeline parallelism over the public internet) is a research problem with terrible latency and reliability on home connections.

**Decision:** Assign each independent inference request to one suitable machine. Never split a single model across machines in Phase 1–4.

**Consequences:** Simpler, testable, honest about what consumer hardware can do. Large models that don't fit one consumer GPU are out of scope until proven otherwise. Revisit only with measured evidence that cross-machine inference is viable.

## ADR-005 — License: Apache-2.0 for code

**Context:** Need a licence that is permissive, business-friendly, and compatible with our model ecosystem.

**Decision:** Apache License 2.0 for all Nodefield code.

**Consequences:** Anyone may use, modify, and distribute the code commercially with attribution; includes a patent grant. Aligns with Qwen and Mistral models (both Apache-2.0). Does **not** cover models — Llama models remain under the Llama 3 Community License, which is separate and applies only to that model family. Contributors must be told the licence before contributing (see `CONTRIBUTING.md`).

## ADR-006 — No token, no blockchain

**Context:** Many distributed-compute projects fund themselves with a token. That creates regulatory, trust, and incentive problems and misleads users about how they get paid.

**Decision:** No token, no coin, no blockchain. When payments exist, they are fiat/credits through a normal payment processor. Provider payouts are money for completed work, not token rewards.

**Consequences:** No speculative hype, no tokenomics to design or defend, clearer legal position. Fundraising and payouts must work on ordinary rails — which is also why paid billing waits until Phase 7 gates are met.
