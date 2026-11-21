# Nodefield frontend

Static frontend for Nodefield — an open marketplace for AI inference on idle GPUs.
Plain HTML + CSS + JavaScript. No build step, no external fonts, images, or CDNs.
The site works fully offline from local files (API features need the backend).

## Serve it

From this directory (`frontend/`):

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000/

## Backend

The demo backend runs on port **8787** (`http://localhost:8787`):

- `GET /api/health` — backend health
- `GET /api/stats` — waitlist/worker counts
- `POST /api/waitlist` — provider/developer registration
  (`{"kind": "provider"|"developer", ...fields}`)
- `GET /api/keys` — list API key prefixes only (never secrets)
- `POST /api/keys` — create a demo key (shown once)
- `GET /api/models` — launch-candidate models
- `POST /v1/chat/completions` — OpenAI-compatible chat completions

If the backend is not running, the status page, dashboard, playground and
registration forms say so honestly. Registration falls back to saving the
entry in the browser's localStorage under key `nodefield-waitlist` and tells
the user it has NOT reached a server.

## Pages

index, providers, developers, models, pricing, how-it-works, roadmap, docs,
community, faq, privacy, terms, status, register, dashboard.

Shared layout: `assets/style.css` + `assets/app.js`; every page carries the
same header/nav/footer markup. Nav collapses to a stacked menu under 720px.

## Honesty rules enforced on this site

- No fake testimonials, customers, statistics, or network activity.
- Network numbers are 0 (real pre-launch counts) or labelled
  "DEMO — illustrative only, not real data".
- Pricing is labelled proposed launch pricing, not yet live; no billing active.
- No earnings are promised to GPU providers anywhere on the site.
- All five launch-candidate models are "Planned — not yet serving live traffic".
