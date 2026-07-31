#!/usr/bin/env python3
"""Local live Apply Queue — clicks write into the repo immediately.

Usage:
  python3 scripts/serve_apply_queue.py --date 2026-07-28
  open http://127.0.0.1:8765/

Open the served URL, not the static .html file, if you want live writes.

Endpoints:
  GET  /                    → queue page (live mode)
  GET  /static/...          → css / js assets
  GET  /api/queue?date=...  → items + counts + selectable dates
  GET  /api/state           → {passed: [...], applied: [...]}
  GET  /api/events          → SSE; emits `state-changed` when the CSVs move
  POST /api/applied         → status=applied (creates the row if needed)
  POST /api/pass            → archive Pass + status=passed
  POST /api/undo            → reverse the last applied/pass for a url
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_apply_queue as gaq  # noqa: E402
from js_lib import now_iso  # noqa: E402
from queue_watch import Watcher  # noqa: E402
from queue_writeback import (  # noqa: E402
    applied_urls,
    canon,
    passed_records,
    record_applied,
    record_pass,
    undo_applied,
    undo_pass,
)

STATIC_ROOT = ROOT / "static"

CONTENT_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
}


class Handler(BaseHTTPRequestHandler):
    day: str = date.today().isoformat()
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    # ---------------------------------------------------------------- send

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

    # ----------------------------------------------------------------- GET

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path in {"/", "/index.html", "/queue"}:
            items = gaq.collect(self.day)
            html = gaq.render_html(self.day, items, live=True, inline=False)
            self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
            return

        if path.startswith("/static/"):
            self._serve_static(path)
            return

        if path == "/api/queue":
            day = (parse_qs(parsed.query).get("date") or [self.day])[0]
            if not gaq.DATE_RE.fullmatch(day):
                self._json(400, {"error": "bad date"})
                return
            items = gaq.collect(day)
            self._json(200, gaq.bootstrap_payload(day, items, live=True))
            return

        if path == "/api/state":
            self._json(200, {"passed": passed_records(), "applied": sorted(applied_urls())})
            return

        if path == "/api/events":
            self._stream_events()
            return

        if path == "/api/health":
            self._json(200, {"ok": True, "day": self.day})
            return

        self._json(404, {"error": "not found"})

    def _serve_static(self, path: str) -> None:
        rel = path[len("/static/"):]
        target = (STATIC_ROOT / rel).resolve()
        # Never serve outside the static tree, whatever the client asks for.
        if not str(target).startswith(str(STATIC_ROOT.resolve())) or not target.is_file():
            self._json(404, {"error": "not found"})
            return
        ctype = CONTENT_TYPES.get(target.suffix, "application/octet-stream")
        self._send(200, target.read_bytes(), ctype)

    def _stream_events(self) -> None:
        """Server-sent events: tell open pages when repo state changed."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        watcher = Watcher()
        try:
            self.wfile.write(b"event: ready\ndata: {}\n\n")
            self.wfile.flush()
            while True:
                time.sleep(1.0)
                if watcher.changed():
                    self.wfile.write(b"event: state-changed\ndata: {}\n\n")
                else:
                    # Comment frame keeps proxies and idle sockets honest.
                    self.wfile.write(b": keep-alive\n\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            return

    # ---------------------------------------------------------------- POST

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

        if path == "/api/undo":
            action = (payload.get("action") or "").strip().lower()
            if action == "applied":
                result = undo_applied(url)
            elif action == "pass":
                result = undo_pass(url)
            else:
                self._json(400, {"error": "action must be 'applied' or 'pass'"})
                return
            code = 200 if result.get("ok") else 409
            self._json(code, {**result, "url": canon(url)})
            return

        self._json(404, {"error": "not found"})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-snapshot", action="store_true", help="skip writing the static fallback files")
    args = ap.parse_args()

    day = args.date
    if not gaq.latest_triage(day):
        dates = gaq.available_dates()
        if dates:
            print(f"no triage file for {day}; falling back to {dates[0]}")
            day = dates[0]

    items = gaq.collect(day)

    if not args.no_snapshot:
        gaq.OUT_DIR.mkdir(parents=True, exist_ok=True)
        (gaq.OUT_DIR / f"{day}.html").write_text(
            gaq.render_html(day, items, live=False, inline=True), encoding="utf-8"
        )
        (gaq.OUT_DIR / f"{day}.md").write_text(gaq.render_md(day, items), encoding="utf-8")

    Handler.day = day
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.daemon_threads = True
    print(f"Apply queue (LIVE): http://{args.host}:{args.port}/")
    print(f"date={day}  roles={len(items)}")
    print("Applied → status=applied in data/applications.csv")
    print("Pass    → data/job_decisions.csv + status=passed")
    print("Undo    → reverts the last applied/pass for that role")
    print("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
