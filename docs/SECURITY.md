# Nodefield — Security Policy

**Version: 1.0 — 21 November 2026 (Phase 1, pre-launch). This policy will be reviewed before any worker connects or any key is issued.**

## What the agent will do

- Run **sandboxed inference only**: receive a prompt, run it through a local model (llama.cpp / vLLM), return tokens. Nothing else.
- Run as a normal user process with least privilege; access only its own working directory and the GPU.
- Show the user everything it is doing: current job, GPU utilisation, VRAM, uptime, earnings (only when real payments exist).
- Let the user pause participation or uninstall at any time, with one click.
- Authenticate to the coordinator and communicate over TLS (planned for production; local prototype uses plain HTTP on localhost only).
- Validate workloads before running them (size limits, content policy) at the gateway.

## What the agent will never do

- **Never execute arbitrary code** supplied by marketplace customers on contributor machines.
- **Never secretly use a GPU** or hide activity from the user.
- **Never access personal files**, browsing history, or other applications.
- **Never claim a machine is earning money when it is merely connected** to the network. Earnings are reported only for completed paid workloads — and there are no paid workloads yet.
- **Never collect passwords for external services** or unnecessary personal information.
- Never mine cryptocurrency, never run background tasks unrelated to an assigned inference job.

## API keys

- Keys are issued manually at first (later automated). A plaintext key is shown **once** at issuance and never stored.
- Stored form: SHA-256 hash with a secret prefix. The database holds hashes only.
- Keys are scoped per developer account; rate limits apply per key.
- A compromised key can be revoked by the founder/admin; rotation is supported.
- Never commit a key, never put one in a URL, never paste one into a chat log or issue.

## Updates

- **Signed updates (planned, not yet implemented).** Agent updates will be signed; unsigned updates are rejected by the agent. No auto-update exists in the prototype — do not claim otherwise.
- Until signing is implemented, updates are manual installs from the official GitHub releases page only.

## Data handling

- Registration data (name/username, email, country, GPU details) is stored only to operate the waitlist and the marketplace. No sale of data, no third-party sharing except the infrastructure providers that host it (Supabase, Cloudflare — accounts not yet created).
- Inference prompts are processed to produce a response and are not retained longer than needed for token accounting and abuse prevention. Retention policy to be finalised before launch.
- No personal files are ever read from contributor machines.

## Vulnerability reporting

- **Security contact to be published by the founder.** There is no security email address yet — do not invent one, and do not report vulnerabilities to a guessed address.
- Once published, the contact will be listed here and in `SECURITY.md` at the repo root.
- If you find a vulnerability now: do not exploit it, do not publish it, and report it to the founder through the project's normal contact channel. Include steps to reproduce, impact, and (if you have one) a suggested fix.
- We aim to acknowledge reports promptly and to fix verified critical issues before any public launch. No bug bounty exists (budget is $0).

## Scope

This policy covers Nodefield code (frontend, backend, agent, scheduler, docs). It does not cover third-party models, Hugging Face, Supabase, or Cloudflare — each has its own security posture and terms.
