#!/usr/bin/env python3
"""Serve the Polar briefing on localhost.

Usage:
  python3 scripts/serve_polar_briefing.py
  open http://127.0.0.1:8766/
"""

from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEFING = ROOT / "docs" / "architecture" / "briefing"
SPRING = ROOT / "static" / "apply_queue" / "spring.js"


class BriefingHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        clean = path.split("?", 1)[0].split("#", 1)[0]
        if clean in ("/spring.js", "/docs/architecture/briefing/spring.js"):
            return str(SPRING)
        if clean == "/":
            return str(BRIEFING / "index.html")
        target = (BRIEFING / clean.lstrip("/")).resolve()
        if str(target).startswith(str(BRIEFING.resolve())) and target.is_file():
            return str(target)
        return str(BRIEFING / "index.html")

    def log_message(self, fmt: str, *args) -> None:
        print(f"briefing: {fmt % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the Polar briefing")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    if not BRIEFING.is_dir():
        raise SystemExit(f"missing {BRIEFING}")
    if not SPRING.is_file():
        raise SystemExit(f"missing {SPRING}")
    server = ThreadingHTTPServer((args.host, args.port), BriefingHandler)
    print(f"Polar briefing at http://{args.host}:{args.port}/")
    print("Arrow keys or swipe. Esc closes a band sheet.")
    server.serve_forever()


if __name__ == "__main__":
    main()
