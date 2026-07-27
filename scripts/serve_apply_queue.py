#!/usr/bin/env python3
"""Local live Apply Queue — clicks write into the repo immediately.

Usage:
  python3 scripts/serve_apply_queue.py --date 2026-07-27
  open http://127.0.0.1:8765/

Open the served URL, not the static .html file, if you want live writes.

Endpoints:
  GET  /                → queue page in LIVE mode
  GET  /api/state       → {passed: [...], applied: [...]} to hydrate the page
  POST /api/pass        → archive Pass + status=passed
  POST /api/applied     → status=applied (creates the row if needed)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_apply_queue as gaq  # noqa: E402
from js_lib import now_iso  # noqa: E402
from queue_writeback import (  # noqa: E402
    applied_urls,
    canon,
    passed_records,
    record_applied,
    record_pass,
)


class Handler(BaseHTTPRequestHandler):
    day: str = date.today().isoformat()

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj: object) -> None:
        self._send(
            code,
            json.dumps(obj, ensure_ascii=False).encode("utf-8"),
            "application/json; charset=utf-8",
        )

    def _payload(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in {"/", "/index.html", "/queue"}:
            items = gaq.collect(self.day)
            html = gaq.render_html(self.day, items)
            html = html.replace(
                "<script>\nconst KEY",
                "<script>\nwindow.APPLY_QUEUE_LIVE = true;\nconst KEY",
                1,
            )
            self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/api/state":
            self._json(
                200,
                {
                    "passed": passed_records(),
                    "applied": sorted(applied_urls()),
                },
            )
            return
        if path == "/api/health":
            self._json(200, {"ok": True, "day": self.day})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            payload = self._payload()
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return

        url = (payload.get("url") or "").strip()
        if not url:
            self._json(400, {"error": "url required"})
            return
        payload.setdefault("decided_at", now_iso())

        if path == "/api/pass":
            payload["decision"] = "pass"
            payload["source"] = "apply_queue_live"
            result = record_pass([payload])
            self._json(200, {"ok": True, **result, "url": canon(url)})
            return

        if path == "/api/applied":
            payload["source"] = payload.get("source") or "apply_queue_live"
            result = record_applied([payload])
            self._json(200, {"ok": True, **result, "url": canon(url)})
            return

        self._json(404, {"error": "not found"})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()

    items = gaq.collect(args.date)
    gaq.OUT_DIR.mkdir(parents=True, exist_ok=True)
    (gaq.OUT_DIR / f"{args.date}.html").write_text(
        gaq.render_html(args.date, items), encoding="utf-8"
    )
    (gaq.OUT_DIR / f"{args.date}.md").write_text(
        gaq.render_md(args.date, items), encoding="utf-8"
    )

    Handler.day = args.date
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Apply queue (LIVE): http://{args.host}:{args.port}/")
    print(f"date={args.date}  roles={len(items)}")
    print("Applied → status=applied in data/applications.csv")
    print("Pass    → data/job_decisions.csv + status=passed")
    print("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
