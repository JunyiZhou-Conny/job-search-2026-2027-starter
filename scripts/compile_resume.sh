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

Options:
  --allow-overflow   compile even if a resume exceeds its page limit

Page limits: cluster resumes 1 page, resumes/base/ 2 pages (deliberate superset).
Override with RESUME_MAX_PAGES / RESUME_BASE_MAX_PAGES.
EOF
}

# A cluster resume that spills onto a second page still compiles and still looks
# fine locally, so it gets uploaded as a "one-pager". That is the failure this
# gate exists to catch.
page_limit_for() {
  case "$1" in
    resumes/base/*) echo "${RESUME_BASE_MAX_PAGES:-2}" ;;
    *) echo "${RESUME_MAX_PAGES:-1}" ;;
  esac
}

# pdflatex reports "Output written on x.pdf (1 page, 79450 bytes)". Fall back to
# Ghostscript when the log is unavailable; 0 means undetermined, never a pass.
page_count() {
  local pdf="$1" log="$2" n=""
  n="$(grep -oE 'Output written on [^(]*\([0-9]+ pages?' "$log" 2>/dev/null \
       | grep -oE '^|[0-9]+ pages?' | grep -oE '[0-9]+' | tail -1 || true)"
  if [[ -z "$n" ]] && command -v gs >/dev/null 2>&1; then
    n="$(gs -q -dNODISPLAY -dNOSAFER \
         -c "($pdf) (r) file runpdfbegin pdfpagecount = quit" 2>/dev/null || true)"
  fi
  echo "${n:-0}"
}

allow_overflow=0
args=()
for arg in "$@"; do
  case "$arg" in
    --allow-overflow) allow_overflow=1 ;;
    -h | --help)
      usage
      exit 0
      ;;
    *) args+=("$arg") ;;
  esac
done
set -- ${args[@]+"${args[@]}"}

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
overflow_n=0
overflow_list=""
undetermined_n=0
for tex in "${targets[@]}"; do
  outdir="$(dirname "$tex")"
  echo "→ Compiling $tex"
  latexmk -pdf -interaction=nonstopmode -outdir="$outdir" "$tex" >/tmp/resume_compile.log 2>&1 || {
    echo "FAILED: $tex (see /tmp/resume_compile.log)" >&2
    tail -n 40 /tmp/resume_compile.log >&2
    exit 1
  }
  pdf="${tex%.tex}.pdf"
  if [[ ! -f "$pdf" ]]; then
    echo "FAILED: expected $pdf missing" >&2
    exit 1
  fi

  bytes="$(wc -c <"$pdf" | tr -d ' ')"
  pages="$(page_count "$pdf" /tmp/resume_compile.log)"
  limit="$(page_limit_for "$tex")"

  if [[ "$pages" -eq 0 ]]; then
    echo "  OK $pdf ($bytes bytes) — WARN page count undetermined, verify by hand" >&2
    undetermined_n=$((undetermined_n + 1))
    ok=$((ok + 1))
  elif [[ "$pages" -gt "$limit" ]]; then
    echo "  OVERFLOW $pdf is $pages pages, limit $limit ($bytes bytes)" >&2
    overflow_n=$((overflow_n + 1))
    ok=$((ok + 1))
    overflow_list="${overflow_list}  - ${pdf}: ${pages} pages (limit ${limit})
"
  else
    echo "  OK $pdf ($pages page(s), $bytes bytes)"
    ok=$((ok + 1))
  fi
  # Drop noisy latexmk auxiliaries; keep .pdf + .tex
  latexmk -c -outdir="$outdir" "$tex" >/dev/null 2>&1 || true
done

if [[ "$overflow_n" -gt 0 ]]; then
  echo
  if [[ "$allow_overflow" -eq 1 ]]; then
    echo "WARNING: $overflow_n resume(s) over the page limit, allowed by --allow-overflow:" >&2
    printf '%s' "$overflow_list" >&2
  else
    echo "PAGE-COUNT GATE FAILED — do not upload:" >&2
    printf '%s' "$overflow_list" >&2
    echo "Trim bullets in resumes/base/JZ_resume.tex, rerun scripts/build_clusters.py," >&2
    echo "then recompile. Use --allow-overflow only when a longer PDF is intended." >&2
    exit 1
  fi
fi

if [[ "$undetermined_n" -gt 0 ]]; then
  echo "NOTE: $undetermined_n PDF(s) had no detectable page count." >&2
fi

echo "Compiled $ok PDF(s). Upload the .pdf next to each .tex when applying."
