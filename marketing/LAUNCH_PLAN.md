# Nodefield — Go-Public Launch Plan

**Written 22 Nov 2026, after the core loop was proven (remote Colab T4 → public
Render API, 28.88 tok/s, real reply). Budget: $0. Nothing in this plan is
published, posted or submitted without the founder's say-so — drafts live in
`marketing/`, publishing is a separate, explicit decision each time.**

## The honest starting point

The product works. That is the easy part. The hard part — and the user is right
that it is the hardest part — is that Nodefield is a **two-sided marketplace
with zero users on either side**: it needs GPU owners and developers at the same
time, and neither side gets value until the other shows up. There is no budget
to buy either side. So the whole launch is: earn attention with real proof,
convert it into a small beta, and let the beta become the story.

What we have to market with (all real, all measured):
- Public API live: https://nodefield-api.onrender.com (health verified)
- First remote GPU worker through it: Qwen3-8B, 28.88 tok/s, 656 ms TTFT
- Open-source repo (Apache-2.0), 15-page site, Discord server live
- $0 spent, no fake users, no fake numbers anywhere

What we do NOT have yet: a persistent worker (the Colab VM is throwaway and
will recycle), a single real user, revenue, or a settled name.

## Gate 0 — the name decision (before anything public)

**nodefield.com belongs to a live Finnish tech/design company.** Same name, same
broad field. Every public post cements the name further, so this is decided
before launch, not after. Options:

- **(a) Keep Nodefield.** Use nodefield.ai or nodefield.dev as the domain (both
  show no live site; a registrar check is still needed to confirm they are
  free to register). Accept the confusion risk with the Finnish company and be
  ready to answer for it when someone on HN points it out — they will.
- **(b) Rename now.** Costs about a day: site, repo references, Discord
  server/account, docs. Cheap now, expensive after launch.

Founder's call. Nothing in Stages 1–3 starts until this is settled, because
every post, handle and link carries the name.

## Gate 1 — survive first contact (launch prep, all $0)

Do these before driving any traffic:

- [ ] **Keep the API warm.** Render's free tier sleeps when idle; a first
  request after idle takes ~50 s. A GitHub Actions cron pinging `/api/health`
  every 10 minutes keeps it warm (free on a public repo).
  → `.github/workflows/keep-alive.yml` (added with this plan).
- [ ] **A worker up on launch day.** The Colab worker dies when its VM
  recycles. For any launch moment (Show HN especially), start a fresh Colab T4
  worker that morning and keep the tab open. The status page already tells the
  truth about 0 workers — do not fake it.
- [ ] **Delete the test row** "VERIFY TEST — delete me" from the Supabase
  providers table (owed since 21 Nov).
- [ ] **Decide on the streaming stall** (KNOWN_ISSUES #15: one streaming attempt
  hung ~4 min with no SSE). Either fix the SSE flush path before launch, or
  disclose it in the launch post as a known issue. Do not let a visitor find
  it first.
- [ ] **X and Reddit accounts.** One account per platform, in the founder's
  name where possible. If they do not exist yet, creating them is a
  browser task (Google sign-in). Do not create sockpuppets or extra accounts.
- [ ] **Status page already shows the real numbers + Discord link** (done
  22 Nov). Keep it updated after every measured run.

## Stage 1 — private beta (weeks 1–2): recruit, don't broadcast

Goal (the original beta targets): **20 GPU contributors, 10 developer
testers, 3 models.** Channels, in this order:

1. **Discord** (already live, 0 members). Post the welcome + beta call in
   #announcements. Draft in `marketing/BETA_POSTS.md`. The server is the
   home base — every other channel points here.
2. **X — build in public.** The 30-day calendar in
   `marketing/CONTENT_CALENDAR.md` exists but is stale (it predates every real
   result). Day 1 becomes the launch thread with the real proof; days after
   that follow the calendar, updated with measured numbers only. Draft thread
   in `marketing/BETA_POSTS.md`.
3. **Reddit — teach, don't pitch.** The 10 educational outlines in the
   calendar are the right shape (r/LocalLLaMA, r/homelab, r/selfhosted).
   Read each subreddit's rules first; several ban self-promotion outright.
   One good post with real numbers beats ten pitches. First candidate: the
   "what we learned building an inference marketplace on $0" post — only once
   the beta is real.
4. **Direct asks, not spam.** A short message to people already talking about
   idle GPUs / local inference, one at a time, no mass messaging, no
   cross-posting the same thing everywhere at once.

Success for Stage 1 is not signups — it is **ten people who run a job and tell
us what broke**. Their complaints are the next build list. If nobody comes,
the answer is not louder marketing; it is asking the few who looked why they
didn't try it.

## Stage 2 — Show HN (the big free lever)

Hacker News is the highest-leverage free channel for a dev-infrastructure
project like this, and the draft in `marketing/CONTENT_CALENDAR.md` said
"DO NOT PUBLISH until a genuinely functional prototype exists". That condition
is now met. Updated draft: `marketing/SHOW_HN.md` — **draft only, never
published without the founder's explicit go-ahead.**

- **When:** after Stage 1 has at least a few real beta users, on a weekday
  morning US time (Mon–Thu, ~8–9am Pacific is the usual window). Never on a
  day the worker is down.
- **What to expect:** a traffic spike, hard technical questions, and someone
  pointing out the Finnish Nodefield — answer honestly, in the thread, the
  same day. The post leads with measured numbers, not promises.
- **Survival:** Render free + one Colab worker will be slow under a spike.
  Say so in the post. A slow honest demo beats a fast fake one, and the
  thread will forgive slowness it was warned about.
- **After:** answer every comment for the first 24 hours. The thread is the
  marketing — the post is just the door.

## Stage 3 — Product Hunt (NOT yet)

The checklist in `marketing/CONTENT_CALENDAR.md` is the gate: final name,
screenshots of the real product, a screen-recorded demo, and — the binding
constraint — **at least one working signup path a hunter can complete the
same day**. That means a beta a stranger can actually join and use, which
does not exist yet. Defer until Stage 1 produces it. Do not launch a
half-usable product to a launch audience; you only get one first impression
there.

## What we are NOT doing

- No paid ads, no paid launch, no press outreach until beta users exist
  (there is no story yet — "we built it" is not a story, "ten strangers use
  it" is).
- No fake users, testimonials, benchmarks or earnings — ever. The brief
  forbids it and the audience for this product will check.
- No token, no crypto framing, no "decentralised" claims.
- No mass-posting, no engagement bait, no cross-posting the same post to
  many communities at once.

## How we will know it is working

- Beta: 20 GPU contributors, 10 dev testers, 3 models (the original targets).
- One real developer who was not recruited by us runs a second job.
- One GPU owner who was not recruited by us keeps their worker up for a
  week.
- If Stage 1 produces none of that in two weeks, stop and rethink the offer
  (price? trust? setup friction?) before spending more effort on reach.
