# Show HN draft — Nodefield

> **DRAFT — DO NOT PUBLISH without the founder's explicit go-ahead.**
> The original draft in `marketing/CONTENT_CALENDAR.md` said not to publish
> until a genuinely functional prototype exists. That condition is now met
> (remote GPU worker through the public API, 22 Nov 2026), so this is the
> updated post. The name question (see `marketing/LAUNCH_PLAN.md` Gate 0)
> must be settled before posting — every public post cements the name.

**Title:** Show HN: Nodefield — inference API on idle consumer GPUs

**Body:**

We're building an open marketplace for AI inference on spare consumer GPUs.
Developers call an OpenAI-compatible API; GPU owners run a small agent and
get paid per completed job. Small quantized open-weight models first
(Qwen3, Mistral, Llama), whole requests scheduled to single machines — we
don't split models across the internet — no token, Apache-2.0 code.

What's real so far, all measured, nothing faked:

- Public API live at https://nodefield-api.onrender.com (free Render tier,
  so it sleeps when idle — first request after idle can take ~50s, we're
  upfront about that).
- First remote worker through it: a free Colab Tesla T4 served a real
  Qwen3-8B request end to end, 28.88 tokens/sec, 656 ms to first token.
  Job record is verifiable at /api/jobs/1 on the public API.
- Earlier runs: 35.27 tok/s benchmark on the same T4, 6.44 tok/s on CPU.
  Full numbers in the repo's BENCHMARKS.md.
- $0 spent so far. Site, waitlist, Discord and code all linked from the
  repo: https://github.com/inertiastudiospakistan/nodefield

What's not real yet: no persistent workers (the Colab VM is throwaway), no
paying users, no revenue. The agent is sandboxed inference only — it never
runs arbitrary customer code on a contributor's machine, and it can be
paused or uninstalled any time.

We'd love feedback on: the scheduling approach, the economics (is ~29 tok/s
on a T4 with a 20% marketplace cut competitive?), and — honestly — what it
would take for you to trust a contributor agent on your machine. That's the
part we think matters most, and the part we have the least data on.

One thing we'll get asked: yes, nodefield.com is a Finnish tech company
with the same name. We're a pre-launch project deciding whether to keep the
name or rename before launch — tell us if that would stop you using it.

---

**Posting notes (not part of the post):**
- Post on a weekday morning US time, Mon–Thu, ~8–9am Pacific.
- Only on a day a worker is actually up (start a fresh Colab T4 worker
  that morning).
- Answer every comment for the first 24 hours. The thread is the marketing.
- If the site/API falls over under load, say so in the thread — don't hide it.
