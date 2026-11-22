# Nodefield — SEO, AI-engine optimisation, socials, outreach, link building, content

**Written 22 Nov 2026. Budget: $0. No fake numbers, no spam, no bought
links, no bought followers — ever. If we haven't measured it, we say so or
say nothing.**

## 0. Where the site stands (audited 22 Nov 2026)

- Good: all 15 pages have a title and meta description.
- Missing, fixed 22 Nov: **no sitemap.xml, no robots.txt, no llms.txt, no
  structured data.** All four added: `frontend/sitemap.xml`,
  `frontend/robots.txt`, `frontend/llms.txt`, JSON-LD (Organization +
  SoftwareApplication on the homepage, FAQPage on the FAQ page). All
  validated (JSON-LD parses, sitemap parses).
- Also fixed 22 Nov: the FAQ said "0 live workers / demo mode on
  localhost" — stale since the public API went live. Updated to the truth.
- Still to do: **Google Search Console verification + sitemap submission**
  (the tool sites went through this on 20 Nov — same process: add the
  verification file, submit the sitemap, then wait; indexing takes days to
  weeks and the first pages may sit unindexed, exactly as the tool sites
  did). Re-check indexing weekly; do not expect rankings in week one.

## 1. Google SEO — what can actually rank

**Honest assessment:** ranking for "AI inference API" or "cheap LLM API"
against Together, Fireworks, OpenRouter and Groq is not realistic in the
short term — they have years of authority. The winnable ground is
long-tail and original-data pages:

- **Target keywords (long-tail, low competition):** "Qwen3 API",
  "Qwen3-8B API price", "run Qwen3 on your GPU", "cheap inference API for
  open models", "OpenAI compatible inference API free", "earn money idle
  GPU inference", "inference API alternative to Together AI".
- **The pages that can rank:** the benchmark/status page (original measured
  data — nobody else has our numbers), the FAQ (exact-match questions
  people type), model pages (Qwen3-8B etc.), pricing (comparison intent).
- **How:** one keyword per page, in the title + first paragraph + one
  heading; internal links between related pages; keep every claim
  measurable and current. No keyword stuffing, no doorway pages, no
  AI-generated filler — Google's spam policies and the audience both
  punish it.
- **Timeframe:** 2–3 months before any meaningful organic traffic, if the
  content ships steadily. SEO is the slowest channel we have and the most
  durable. It does not replace the launch — it compounds after it.

## 2. AI-engine optimisation (AEO / GEO) — being cited by ChatGPT, Perplexity, Claude

This matters more than classic SEO for a dev tool in 2026: developers ask
AI assistants "what's the cheapest inference API for Qwen3?" and the
assistant answers from whatever it can cite.

- **llms.txt is live** (`frontend/llms.txt`, llmstxt.org format): a short
  factual summary of the project with links to every key page, including
  the "what is NOT true" section. This is the file AI crawlers look for.
- **FAQPage JSON-LD is live** on the FAQ page: 12 real questions with
  straight answers. AI Overviews and chatbots lift FAQ schema directly.
- **The strategy is to be the citable source for specific questions:**
  "how much can I earn from my GPU", "Qwen3-8B tokens per second T4",
  "cheapest Qwen3 API". Pages that answer one question clearly, with a
  number and a date, get cited; vague marketing pages don't.
- **Keep it current:** every measured run updates the status page and
  BENCHMARKS.md the same day. Stale numbers are worse than no numbers —
  an AI citing our old "0 workers" line is exactly what the FAQ fix
  prevented.
- **Do not** chase "GEO hacks" (hidden text, fake citations, prompt
  injection). They get caught and they destroy trust with the exact
  audience we need.

## 3. Socials — where, and how

| Channel | Role | Status |
|---|---|---|
| **X** | Build in public — the daily channel | 30-day calendar exists (`marketing/CONTENT_CALENDAR.md`, Day 1 thread updated in `marketing/BETA_POSTS.md`) |
| **Reddit** | Teach, don't pitch — r/LocalLLaMA, r/homelab, r/selfhosted | 10 educational outlines exist; read each sub's rules first, several ban self-promotion |
| **Discord** | Home base — beta community | Server live, 0 members; beta call drafted |
| **LinkedIn** | Founder story — professional audience | User has LinkedIn; occasional founder posts about building a marketplace on $0. Good for hiring/partners later, not for developers |
| **YouTube** | Deferred — screen-recorded demos only, when the product is worth filming | 10 short concepts + 5 demo concepts exist; no talking-head hype |
| **TikTok / Instagram** | No — wrong audience for dev infrastructure | — |

Rules across all of them: one account per platform, no cross-posting the
same post everywhere at once, no engagement bait, answer every reply for
the first 24 hours after a launch post.

## 4. Outreach — who, and how (no spam)

- **Dev-tool newsletters (free submissions):** Console.dev, TLDR
  (AI/Dev), Hacker Newsletter, Changelog Weekly. One submission each, with
  the repo link and the measured numbers. They only pick things up if the
  thing is real — ours now is.
- **Indie/startup communities:** Indie Hackers, Hacker News (Show HN —
  draft in `marketing/SHOW_HN.md`), r/SideProject. Same rule: one honest
  post, answer everything.
- **GPU communities:** GPU/hardware Discords and forums where people talk
  about idle cards. Ask, don't pitch — "would you run this?" beats "try
  this".
- **Direct, personal emails only.** One person at a time, naming something
  specific they wrote or built, with the repo link and one number. No
  bought lists, no mass mail, no follow-up spam. If someone doesn't reply,
  that's the answer.
- **What outreach never does:** promise earnings, promise uptime, or
  present the beta as a finished product.

## 5. Link building — $0, and only the honest kind

Links are what make Google trust the site, and at $0 they have to be
earned, not bought:

- **The benchmark page is the linkable asset.** Original measured data
  earns links from blogs, newsletters and other repos. Keep it updated
  after every run.
- **GitHub itself:** stars, forks and the repo README linking back to the
  site. Open source is a link magnet if the project is real.
- **Directories (free listings):** AlternativeTo, SaaSHub, Product Hunt
  (only when Stage 3-ready — see `marketing/LAUNCH_PLAN.md`).
- **Guest posts / dev blogs:** one honest build-log post ("what we learned
  building an inference marketplace on $0") pitched to a dev publication
  once the beta is real. The post links the benchmark page, not the
  homepage.
- **Answering questions:** Stack Overflow, Reddit, Discord — link the docs
  only where the docs genuinely answer the question.
- **Never:** bought links, link exchanges, comment spam, fake reviews.
  They work briefly and then cost the domain.

## 6. Content writing — the engine that feeds all of the above

The 30-day X calendar exists; the SEO content is the longer-lived half:

- **Two kinds of posts:** (a) build-in-public updates — real progress only,
  same day it happens; (b) evergreen guides — one keyword each, real
  numbers inside ("How to run Qwen3-8B on your own GPU", "What does
  inference actually cost per 1M tokens", "Q4 quantisation in plain
  English", "Time-to-first-token, explained").
- **Cadence:** 2–3 posts a week, not daily. Every post must contain
  something that was measured or built that week. If nothing shipped, the
  post is an honest "what we learned" — never filler.
- **Voice:** the user's standing rule applies to all of it — plain human
  language, no AI-sounding hype, no deflection, direct answers.
- **Where it lives:** X and Reddit for distribution; the durable versions
  live on the site (docs/FAQ/benchmark pages) so search and AI engines
  can find and cite them. Social posts point at the site, not the other
  way round.
- **Measurement:** add a free GoatCounter site for Nodefield (the tool
  sites already use GoatCounter) so we can see which channel actually
  sends visitors. Without it we're guessing which of these channels
  works. Do not optimise on vanity metrics (likes, impressions) — the
  numbers that matter are waitlist signups, workers online and jobs run.

## 7. Priority order (if time is short)

1. Search Console + sitemap submission (30 min, unlocks everything else).
2. Show HN + beta recruitment (the launch plan's Stages 1–2).
3. Two evergreen guides (Qwen3-on-your-GPU, inference cost) — the first
   SEO pages with a chance of ranking.
4. Newsletter submissions (Console.dev, TLDR) once the beta has a few
   users.
5. Product Hunt — last, only when the checklist is met.
