# Polar briefing

A localhost talk for the current Polar architecture. It is the navigable companion to the mermaid posters. It is not a second policy source.

## Run

```bash
python3 scripts/serve_polar_briefing.py
```

Open `http://127.0.0.1:8766/`. Do not open the HTML file from disk. The server maps `spring.js` from `static/apply_queue/`.

Arrow keys, space, or swipe move through the talk. Chapter pills jump. The last scene opens the six bands. Esc closes a band sheet.

Deep links use hashes such as `/#resume` and `/#map`.

## What it is allowed to claim

Every scene carries a truth badge.

- `production` is live Polar policy on current `main`.
- `designed` is specified and not the default Polar path yet.
- `press` is public writing, not Polar telemetry.
- `historical` is the August 2026 friends deck, not this loop.

The site must not show funnel rates, Sheet volume, or `data/applications.csv` counts as Polar production.

Resume attach today is the Simplify profile resume. `ai_infra_v1` exists on `main`. Polar is not wired to it. VIP tailor is exceptional.

## Sources

- `docs/architecture/POLAR_SYSTEM.md`
- `knowledge/polar_operator.yaml`
- `docs/resume/QUALITY_ENGINE.md`
- `docs/policy/SUBMIT_ROLLOUT.md`

Re-check copy with `python3 scripts/validate_polar_briefing.py`.
