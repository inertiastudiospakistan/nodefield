# Beta recruitment posts — drafts

> **DRAFTS — DO NOT POST without the founder's explicit go-ahead for each
> one.** Every post links the real proof (public API, benchmark numbers,
> repo). Nothing here claims users, revenue or earnings we don't have.

## 1. Discord #announcements — beta call

**Title:** Private beta is open — we need GPU owners and developers

Nodefield's core loop works now: a GPU on the other side of the internet
served a real request through our public API (Qwen3-8B, 28.88 tokens/sec).
The API is live at https://nodefield-api.onrender.com, the code is open
source at https://github.com/inertiastudiospakistan/nodefield, and so far
we've spent $0.

We're opening a small private beta: 20 GPU contributors, 10 developer
testers, 3 models to start. What we're asking:

- **GPU owners:** run the agent (docs in the repo), keep it up when you
  can, tell us what breaks. It runs sandboxed inference only — never
  arbitrary code on your machine — and you can pause or uninstall it any
  time.
- **Developers:** point your OpenAI-compatible client at our API, run a
  real job, tell us what broke. Same deal — we want the complaints, that's
  the build list.

No payments yet — this beta is about proving the loop with real people
before any money moves. If you want in, say hi in #introductions and tell
us what GPU you have (or what you'd want to run).

## 2. X — launch thread (replaces the stale Day 1 in CONTENT_CALENDAR.md)

**1/** We built an AI inference marketplace on $0 — and this week the core
loop actually worked: a GPU on the other side of the internet served a
real request through our public API.

Here's what it is, what we measured, and what we need next. 🧵

**2/** The idea is simple: millions of gaming GPUs sit idle most of the
day. Developers need affordable inference. Nodefield connects them —
OpenAI-compatible API on one side, a small agent on your GPU on the other.

**3/** What we measured (real runs, not estimates):
• Qwen3-8B on a free Colab T4: 35.27 tokens/sec benchmark
• Same model through our public API from a remote worker: 28.88 tok/s,
  656 ms to first token
• Same model on CPU: 6.44 tok/s (for the full table, repo's BENCHMARKS.md)

**4/** The API is live: https://nodefield-api.onrender.com
The code is open source (Apache-2.0):
https://github.com/inertiastudiospakistan/nodefield

**5/** What's NOT true yet: no persistent workers, no paying users, no
revenue. The agent is sandboxed inference only — never arbitrary code on
your machine, pause or uninstall any time.

**6/** We're opening a small private beta: 20 GPU contributors, 10 dev
testers. If you have a GPU sitting idle, or an app that needs cheap
inference, our Discord is where it happens: [Discord link]

**7/** We're building this in public, $0 budget, no fake numbers. If it
fails, you'll see it fail. If you want to watch — or help break it — follow
along.

## 3. Reddit — r/LocalLLaMA post outline (adapt to the subreddit's rules first)

**Title idea:** We built an inference marketplace on spare GPUs for $0 —
and a remote T4 just served a real request through it. Here's what we
measured.

**Shape:** short build log, not a pitch. What we built, the stack (Python
stdlib API, llama.cpp worker, Render free tier, Colab T4), the measured
numbers (35.27 tok/s benchmark, 28.88 tok/s through the public API, 6.44
tok/s CPU), what broke along the way (Render sleeps when idle, first
heartbeat failed then recovered; the worker model-map bug that silently
served the 4B model), what isn't true yet (no persistent workers, no users,
no payments), and the ask (beta testers — GPU owners and developers — in
our Discord).

**Rules:** read r/LocalLLaMA's rules before posting; check whether
self-promotion is allowed and in what form. One post, one subreddit, no
cross-posting the same thing elsewhere the same day.
