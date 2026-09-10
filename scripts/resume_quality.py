#!/usr/bin/env python3
"""Resume Quality Engine entry point.

    python3 scripts/resume_quality.py run --jd tests/fixtures/resume_quality/jds/twitch-swe.md \\
        --out generated/resume_quality/twitch-swe
    python3 scripts/resume_quality.py benchmark
    python3 scripts/resume_quality.py validate generated/resume_quality/twitch-swe/resume.tex
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rqe.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
