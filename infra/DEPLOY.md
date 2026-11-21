# Nodefield — $0 Deployment Plan

**Status: plan only. No account has been created, nothing is deployed. The founder must create the accounts below — the agent cannot create accounts in the founder's name.**

## Target architecture (free tiers)

| Layer | Service | Free tier | Notes |
|---|---|---|---|
| Frontend | Cloudflare Pages | 500 builds/month, unlimited static requests | Static site, no build step — deploy is a directory upload / git push |
| Backend (later) | Cloudflare Workers | 100,000 requests/day | Only when the API outgrows local prototyping |
| Database + Auth | Supabase | 500 MB Postgres, 50,000 MAU | **Free projects pause after 1 week of inactivity — verify before relying** |
| Code | GitHub | Free public repos | Actions minutes included |
| Community | Discord | Free server | See `marketing/DISCORD.md` |

## Step 1 — GitHub repo setup (founder)

1. Create a public repo (e.g. `nodefield/nodefield`) under an org or personal account the founder controls.
2. Push this local tree.
3. Add: `LICENSE` (Apache-2.0 text), `CODE_OF_CONDUCT.md`, `SECURITY.md` at repo root (pointing to `docs/SECURITY.md` until the security contact is published).
4. Add `.github/` templates: `pull_request_template.md`, `ISSUE_TEMPLATE/bug_report.md`, `ISSUE_TEMPLATE/feature_request.md`.
5. Enable branch protection on `main` (require PR review) once there is more than one contributor.
6. **Never commit secrets.** Check `.gitignore` covers `.env`, keys, and credentials before the first push.

## Step 2 — Cloudflare Pages (founder creates account)

1. Founder creates a Cloudflare account (free plan, no card required for Pages free tier — verify at signup).
2. In the dashboard: Workers & Pages → Create → Pages → Connect to Git → select the Nodefield repo.
3. Build settings: framework preset **None** (static site, no build step); build command empty; output directory `frontend`.
4. Deploy. The site gets a `*.pages.dev` subdomain — that is the temporary public URL. Do not buy a custom domain without founder approval (and not until the Nodefield name check clears).
5. Verify all 14 pages load, then add the URL to `PROJECT_STATUS.md`.

## Step 3 — Supabase (founder creates project)

1. Founder creates a Supabase account and a free-tier project.
2. In the SQL editor, run `infra/supabase_schema.sql` (tables below).
3. Enable Row Level Security on all tables and restrict writes to the service role / authenticated admin — public anonymous inserts only where the waitlist form needs them, with rate limiting.
4. Set up Supabase Auth (email) for the dashboard when it exists; do not roll custom auth.
5. Store the project URL and anon/service keys in the founder's secret store — **never in the repo**.
6. **Caveat:** free projects pause after 1 week idle. Before launch, verify current pause behaviour and plan a keep-alive or an upgrade path.

## Step 4 — What is deliberately NOT deployed yet, and why

| Item | Why not yet |
|---|---|
| Public inference API | No real model is serving; the demo API is a stub. Deploying it publicly would misrepresent prototype infrastructure as production. |
| Payments / billing | Phase 7 gates unmet: no reliability data, no validated pricing, no payment processor, no fundable payout path. |
| Discord server | Structure is written; server creation is a founder action (account ownership). |
| Custom domain | Name not trademark-checked; no domain purchase without founder approval. |
| Auto-updating agent | Update signing not implemented; no auto-update until it is (see `docs/SECURITY.md`). |

## Local verification (before any deploy)

```bash
python3 -m http.server 8000 --directory frontend   # http://localhost:8000
python3 backend/api/server.py                       # http://localhost:8787
```

Check: all 14 pages render, both registration forms submit to the waitlist API, demo chat completions returns a labelled demo response. Record failures in `KNOWN_ISSUES.md`.
