from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from rqe.judge import arena, arena_markdown, validate_pdf_pages, validate_tex, validation_markdown
from rqe.jd import parse_jd_file
from rqe.load import BANK_PATH, PHILOSOPHY_PATH, ROOT, load_bank
from rqe.plan import all_strategies, match_job
from rqe.render import (
    BaseDoc,
    BASE_TEX,
    build_candidate,
    dump_claim_map,
    dump_requirement_map,
    interview_defense_markdown,
    rejected_markdown,
    strategy_markdown,
)
from rqe.models import Candidate, ValidationReport

BASELINE_DIR = ROOT / "tests" / "fixtures" / "resume_quality" / "baselines"
HISTORICAL_BASELINE = {
    "swe": BASELINE_DIR / "2026-08-24_cloud-swe_v1.3.tex",
    "ml_ai": BASELINE_DIR / "2026-08-24_data-ml_v1.3.tex",
    "data": BASELINE_DIR / "2026-08-24_data-ml_v1.3.tex",
    "health_ai": BASELINE_DIR / "2026-08-24_health-ai_v1.3.tex",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else text + "\n")


def _dump_yaml(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def _baseline_path(family: str) -> Path | None:
    path = HISTORICAL_BASELINE.get(family)
    if path is not None and path.is_file():
        return path
    return None


def _baseline_candidate(family: str) -> Candidate | None:
    tex_path = _baseline_path(family)
    if tex_path is None:
        return None
    from rqe.models import Strategy

    tex = tex_path.read_text()
    empty = Strategy(
        name="narrative",
        family=family,
        narrative="historical one-page cluster used only as a benchmark artifact",
        include_projects=(),
        exclude_projects=(),
        section_order=(),
        bullets={},
        skills_order=(),
        dimensions={},
    )
    return Candidate(name="narrative", strategy=empty, tex=tex, used_claim_ids=())


def run_job(jd_path: Path, out_dir: Path, *, compile_pdf: bool, strategy_name: str | None) -> int:
    bank = load_bank()
    job = parse_jd_file(jd_path)
    matches = match_job(bank, job)
    strategies = all_strategies(bank, job, matches)
    if strategy_name:
        strategies = [s for s in strategies if s.name == strategy_name]
        if not strategies:
            raise SystemExit(f"unknown strategy {strategy_name!r}")
    base = BaseDoc(BASE_TEX.read_text())
    candidates = {s.name: build_candidate(bank, s, base) for s in strategies}

    validations: dict[str, ValidationReport] = {}
    for name, cand in candidates.items():
        validations[name] = validate_tex(bank, cand.tex, cand.used_claim_ids)

    baseline = _baseline_candidate(job.family)
    contestants = dict(candidates)
    if baseline is not None:
        contestants["baseline"] = baseline
        validations["baseline"] = validate_tex(bank, baseline.tex, ())

    votes = arena(job, matches, bank, contestants, validations)

    tallies: dict[str, int] = {}
    vetoed_names = {name for name, report in validations.items() if not report.ok}
    for v in votes:
        if v.veto or v.winner in {"tie", "veto", "baseline"}:
            continue
        if v.winner in vetoed_names:
            continue
        tallies[v.winner] = tallies.get(v.winner, 0) + 1
    if tallies:
        winner_name = max(tallies, key=lambda k: (tallies[k], k))
    else:
        winner_name = next((n for n in candidates if validations[n].ok), next(iter(candidates)))
    winner = candidates[winner_name]

    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    _write(out_dir / "resume.tex", winner.tex)
    _dump_yaml(out_dir / "requirement_map.yaml", dump_requirement_map(job))
    _dump_yaml(out_dir / "claim_map.yaml", dump_claim_map(matches))
    _write(out_dir / "strategy.md", strategy_markdown(job, winner.strategy, bank))
    _write(out_dir / "rejected_claims.md", rejected_markdown(bank, winner.strategy, matches))
    _write(out_dir / "arena_report.md", arena_markdown(votes, validations))
    _write(out_dir / "validation_report.md", validation_markdown(validations[winner_name]))
    _write(out_dir / "interview_defense.md", interview_defense_markdown(bank, winner.strategy))
    for name, cand in candidates.items():
        _write(out_dir / f"candidate_{name}.tex", cand.tex)
    if baseline is not None:
        _write(out_dir / "baseline.tex", baseline.tex)

    meta = {
        "job": {"company": job.company, "title": job.title, "family": job.family, "source": job.source},
        "winner": winner_name,
        "bank_sha": _sha(BANK_PATH),
        "philosophy_sha": _sha(PHILOSOPHY_PATH),
        "base_tex_sha": _sha(BASE_TEX),
        "jd_sha": _sha(jd_path),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": "none (deterministic v0)",
    }
    _dump_yaml(out_dir / "run_meta.yaml", meta)

    if compile_pdf:
        script = ROOT / "scripts" / "compile_resume.sh"
        proc = subprocess.run(
            [str(script), str(out_dir / "resume.tex")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        (out_dir / "compile.log").write_text(proc.stdout + "\n" + proc.stderr)
        if proc.returncode != 0:
            print(proc.stdout)
            print(proc.stderr, file=sys.stderr)
            return proc.returncode
        pdf_report = validate_pdf_pages(out_dir / "resume.pdf")
        if pdf_report.issues:
            _write(out_dir / "validation_report.md", validation_markdown(pdf_report))
            if not pdf_report.ok:
                return 1
    print(f"wrote {out_dir} winner={winner_name} family={job.family}")
    return 0 if validations[winner_name].ok else 1


def cmd_validate(tex_path: Path) -> int:
    bank = load_bank()
    report = validate_tex(bank, tex_path.read_text())
    print(validation_markdown(report), end="")
    return 0 if report.ok else 1


def cmd_benchmark(out_root: Path, *, compile_pdf: bool) -> int:
    fixtures = sorted((ROOT / "tests" / "fixtures" / "resume_quality" / "jds").glob("*.md"))
    if not fixtures:
        raise SystemExit("no JD fixtures under tests/fixtures/resume_quality/jds")
    out_root = out_root.resolve()
    rc = 0
    index = []
    for jd in fixtures:
        dest = out_root / jd.stem
        code = run_job(jd, dest, compile_pdf=compile_pdf, strategy_name=None)
        rc = rc or code
        index.append({"jd": str(jd.relative_to(ROOT)), "out": str(dest.relative_to(ROOT)), "exit": code})
    _dump_yaml(out_root / "index.yaml", {"runs": index})
    return rc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resume Quality Engine")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="extract, match, generate, judge one JD")
    run_p.add_argument("--jd", required=True, type=Path)
    run_p.add_argument("--out", required=True, type=Path)
    run_p.add_argument("--strategy", choices=["recruiter", "hiring_manager", "impact", "narrative"])
    run_p.add_argument("--compile", action="store_true")

    val_p = sub.add_parser("validate", help="run the factual validator on a .tex file")
    val_p.add_argument("tex", type=Path)

    bench_p = sub.add_parser("benchmark", help="run the three fixture JDs")
    bench_p.add_argument("--out", type=Path, default=ROOT / "generated" / "resume_quality")
    bench_p.add_argument("--compile", action="store_true")

    args = parser.parse_args(argv)
    if args.cmd == "run":
        return run_job(args.jd, args.out, compile_pdf=args.compile, strategy_name=args.strategy)
    if args.cmd == "validate":
        return cmd_validate(args.tex)
    if args.cmd == "benchmark":
        return cmd_benchmark(args.out, compile_pdf=args.compile)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
