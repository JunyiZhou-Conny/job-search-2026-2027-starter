# /tailor-resume

VIP tailoring only. Regular Polar rows route to a frozen family one-pager. Do not generate a resume from a JD at apply time.

```bash
python3 scripts/resume_quality.py run --jd <jd-file> --out generated/resume_quality/<slug>
```

That command is the current `vip-tailor` stand-in. See `docs/resume/QUALITY_ENGINE.md`.

1. Use this path only for an exceptional high-priority application.
2. Read `validation_report.md` before any prose. A hard failure is not uploadable.
3. Facts come from `knowledge/evidence_bank.yaml`. The wording catalog may not add ownership, architecture, impact, or technologies.
4. Compile with `./scripts/compile_resume.sh generated/resume_quality/<slug>/resume.tex`.
5. Register `data/resume_versions.csv` only after a human accepts the file.
6. Leave Polar, form fill, and submit on the ROUTE path.

Do not invent skills, metrics, employers, or planned work written as done.
Do not restore `scripts/build_clusters.py`.
