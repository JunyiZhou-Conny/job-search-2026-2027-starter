#!/usr/bin/env python3
"""Render Polar architecture maps with a CJK-capable font."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "docs" / "architecture"
RENDERED = ARCH / "rendered"
CONFIG = ARCH / "mermaid.json"
FONT = Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")
CHROME = shutil.which("google-chrome") or shutil.which("chromium")
SOURCES = (
    "polar-system-map.mmd",
    "polar-apply-worker.mmd",
    "polar-state-concurrency.mmd",
    "polar-learning-loop.mmd",
)


def _mmdc() -> list[str]:
    npx = shutil.which("npx")
    if npx is None:
        raise SystemExit("npx is required to render Mermaid")
    return [npx, "--yes", "@mermaid-js/mermaid-cli@11.4.2"]


def render_svg(source: Path, width: int) -> Path:
    RENDERED.mkdir(parents=True, exist_ok=True)
    out = RENDERED / f"{source.stem}.svg"
    cmd = _mmdc() + [
        "-i",
        str(source),
        "-o",
        str(out),
        "-b",
        "white",
        "-w",
        str(width),
        "-c",
        str(CONFIG),
    ]
    subprocess.run(cmd, check=True)
    return out


def svg_to_png(svg: Path) -> Path:
    if CHROME is None:
        raise SystemExit("google-chrome is required for CJK PNG rendering")
    html = RENDERED / f"{svg.stem}.html"
    png = RENDERED / f"{svg.stem}.png"
    svg_text = svg.read_text(encoding="utf-8")
    match = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', svg_text)
    raw_w = float(match.group(1)) if match else 2400
    raw_h = float(match.group(2)) if match else 1600
    scale = min(8000 / raw_w, 4000 / raw_h, 1.0)
    width = int(raw_w * scale) + 48
    height = int(raw_h * scale) + 48
    font_href = FONT.as_uri() if FONT.is_file() else ""
    html.write_text(
        f"""<!DOCTYPE html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8"/>
<style>
@font-face {{
  font-family: "PolarCJK";
  src: url("{font_href}") format("collection");
}}
html, body {{
  margin: 0;
  padding: 16px;
  background: #ffffff;
}}
svg {{
  width: {int(raw_w * scale)}px;
  height: {int(raw_h * scale)}px;
}}
svg, svg text, svg tspan {{
  font-family: PolarCJK, "WenQuanYi Micro Hei", "WenQuanYi Zen Hei", sans-serif !important;
}}
</style>
</head>
<body>
{svg_text}
</body>
</html>
""",
        encoding="utf-8",
    )
    with tempfile.TemporaryDirectory(prefix="polar-mmd-") as profile:
        try:
            subprocess.run(
                [
                    CHROME,
                    "--headless=new",
                    "--disable-gpu",
                    "--hide-scrollbars",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--font-render-hinting=medium",
                    "--virtual-time-budget=4000",
                    f"--user-data-dir={profile}",
                    f"--window-size={width},{height}",
                    f"--screenshot={png}",
                    html.as_uri(),
                ],
                check=False,
                timeout=25,
            )
        except subprocess.TimeoutExpired:
            pass
    if not png.is_file() or png.stat().st_size < 1000:
        raise SystemExit(f"chrome did not write {png}")
    return png


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", type=int, default=4200)
    parser.add_argument("--png", action="store_true")
    parser.add_argument("--only", action="append")
    args = parser.parse_args(argv)
    names = args.only or list(SOURCES)
    for name in names:
        source = ARCH / name
        svg = render_svg(source, args.width)
        print(f"svg {svg.relative_to(ROOT)}")
        if args.png:
            png = svg_to_png(svg)
            print(f"png {png.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
