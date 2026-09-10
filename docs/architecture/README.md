# Polar system architecture

This folder is the current visual mental model of Polar production on `main`.

Open [`POLAR_SYSTEM.md`](POLAR_SYSTEM.md) first. That page says how to read the maps.

Editable Mermaid sources:

- [`polar-system-map.mmd`](polar-system-map.mmd) is the master lifecycle poster.
- [`polar-apply-worker.mmd`](polar-apply-worker.mmd) is one `apply-ready-jobs` worker.
- [`polar-state-concurrency.mmd`](polar-state-concurrency.mmd) is queue status, claims, and requisition ownership.
- [`polar-learning-loop.mmd`](polar-learning-loop.mmd) is production learning through human merge.

Rendered posters live in [`rendered/`](rendered/). Open the SVG at full size. Do not judge the map from a 1600-pixel thumbnail.

Re-check the maps against live policy with `python3 scripts/validate_polar_system_map.py`.
Render them with `python3 scripts/render_polar_system_map.py --png`.
