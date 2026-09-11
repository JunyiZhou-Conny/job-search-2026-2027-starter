# VIP-tailor a resume

Use this only for an exceptional high-priority JD. Ordinary Polar ingest is `resumes/Perfect Resume/perfect_resume.pdf`.

- Compare the JD to `knowledge/evidence_bank.yaml`.
- Run `python3 scripts/resume_quality.py run --jd <file> --out generated/resume_quality/<slug>`.
- Keep the requirement id and claim id visible in `claim_map.yaml`.
- Do not add skills, metrics, ownership, or technologies that are not in the bank.
- A failed `validation_report.md` blocks upload.
- Keep the one-page compile gate.
- Do not edit `resumes/base/JZ_resume.tex` and do not restore cluster generation.
