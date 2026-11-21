# Contributing to Nodefield

Thanks for considering a contribution. Nodefield is pre-launch, open source under the **Apache License 2.0**, and built on a $0 budget — so clear, small, well-tested contributions matter more than big rewrites.

## Before you start

- Read `README.md`, `ROADMAP.md`, and `DECISIONS.md` so your change fits the direction.
- Check `PROJECT_STATUS.md` and `KNOWN_ISSUES.md` — the highest-value work is listed there.
- Open an issue first for anything larger than a typo fix, so work doesn't duplicate or conflict.

## How to contribute

1. Fork the repo and create a branch from `main` (`feat/short-name` or `fix/short-name`).
2. Keep changes small and focused — one thing per PR.
3. Run the prototype locally before submitting:
   - Frontend: `python3 -m http.server 8000 --directory frontend`
   - Backend: `python3 backend/api/server.py`
   - Confirm the pages and endpoints you touched still work.
4. Don't add dependencies without discussing it first — the prototype is stdlib-only by design (ADR-002).
5. Write a clear PR description: what changed, why, how you tested it.
6. Never include secrets, API keys, tokens, or personal data in a PR. If you find one committed by accident, tell a maintainer immediately — don't just delete it in a follow-up commit (history still holds it).

## PR template

Use the template in `.github/pull_request_template.md` (to be added with the GitHub repo setup — see `infra/DEPLOY.md`). Until it exists, include in your PR body: summary, motivation, test steps, and any docs updated.

## Issue templates

Planned (with repo setup): bug report (what happened / expected / steps / environment) and feature request (problem / proposal / alternatives). Until they exist, file issues with those headings in the body.

## Code of conduct — summary

- Be kind and constructive; assume good faith.
- No harassment, discrimination, or personal attacks — in issues, PRs, or Discord.
- Give credit; don't present others' work as your own.
- Maintainers may close or decline contributions that don't fit the roadmap; that's not personal.
- The full code of conduct lives in `CODE_OF_CONDUCT.md` (to be added at repo publication). Until then, this summary governs.

## Licensing

By contributing, you agree your contribution is licensed under the **Apache License 2.0**, the same licence as the rest of the codebase. See `LICENSE` (to be added at repo publication) and `DECISIONS.md` ADR-005. Model licences are separate — don't bundle model weights in a PR.
