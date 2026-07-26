#!/usr/bin/env bash
# Compile one or more resume .tex files to submit-ready PDFs (same basename).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v latexmk >/dev/null 2>&1; then
  echo "latexmk not found. Install TeX Live / MacTeX first." >&2
  exit 1
fi

usage() {
  cat <<'EOF'
Usage:
  scripts/compile_resume.sh                       # compile all cluster .tex
  scripts/compile_resume.sh resumes/data_ml/*.tex # compile specific files
  scripts/compile_resume.sh data_ml               # compile one cluster folder
EOF
}

targets=()
if [[ $# -eq 0 ]]; then
  while IFS= read -r f; do
    targets+=("$f")
  done < <(find resumes/base resumes/cloud_swe resumes/data_ml resumes/health_ai -name '*.tex' 2>/dev/null | sort)
elif [[ $# -eq 1 && -d "resumes/$1" ]]; then
  while IFS= read -r f; do
    targets+=("$f")
  done < <(find "resumes/$1" -name '*.tex' | sort)
else
  for arg in "$@"; do
    if [[ -f "$arg" ]]; then
      targets+=("$arg")
    elif [[ -f "resumes/$arg" ]]; then
      targets+=("resumes/$arg")
    else
      echo "Not found: $arg" >&2
      exit 1
    fi
  done
fi

if [[ ${#targets[@]} -eq 0 ]]; then
  echo "No .tex files to compile." >&2
  usage
  exit 1
fi

ok=0
for tex in "${targets[@]}"; do
  outdir="$(dirname "$tex")"
  echo "→ Compiling $tex"
  latexmk -pdf -interaction=nonstopmode -outdir="$outdir" "$tex" >/tmp/resume_compile.log 2>&1 || {
    echo "FAILED: $tex (see /tmp/resume_compile.log)" >&2
    tail -n 40 /tmp/resume_compile.log >&2
    exit 1
  }
  pdf="${tex%.tex}.pdf"
  if [[ -f "$pdf" ]]; then
    echo "  OK $pdf ($(wc -c <"$pdf" | tr -d ' ') bytes)"
    ok=$((ok + 1))
  else
    echo "FAILED: expected $pdf missing" >&2
    exit 1
  fi
  # Drop noisy latexmk auxiliaries; keep .pdf + .tex
  latexmk -c -outdir="$outdir" "$tex" >/dev/null 2>&1 || true
done

echo "Compiled $ok PDF(s). Upload the .pdf next to each .tex when applying."
