#!/usr/bin/env python3
"""Local live Apply Queue — Pass writes into the repo immediately.

Usage:
  python3 scripts/serve_apply_queue.py --date 2026-07-26
  open http://127.0.0.1:8765/

Do NOT open the static .html file if you want live writes — use this server URL.
"""

from __future__ import annotations

import argparse
import csv
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
from sync_queue_decisions import update_applications, upsert_decisions  # noqa: E402


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
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self._send(code, raw, "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in {"/", "/index.html", "/queue"}:
            items = gaq.collect(self.day)
            html = gaq.render_html(self.day, items)
            # Inject live flag before script logic
            html = html.replace(
                "<script>\nconst KEY",
                "<script>\nwindow.APPLY_QUEUE_LIVE = true;\nconst KEY",
                1,
            )
            self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/api/passes":
            rows = []
            if gaq.JOB_DECISIONS.exists():
                with gaq.JOB_DECISIONS.open(newline="", encoding="utf-8") as f:
                    for r in csv.DictReader(f):
                        if (r.get("decision") or "").lower() == "pass":
                            rows.append(dict(r))
            self._json(200, {"decisions": rows})
            return
        if path == "/api/health":
            self._json(200, {"ok": True, "day": self.day})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return

        if path != "/api/pass":
            self._json(404, {"error": "not found"})
            return

        url = (payload.get("url") or "").strip()
        if not url:
            self._json(400, {"error": "url required"})
            return
        row = {
            "url": url,
            "company": payload.get("company") or "",
            "role": payload.get("role") or "",
            "job_id": payload.get("job_id") or "",
            "decision": "pass",
            "reason": (payload.get("reason") or "").strip(),
            "decided_at": payload.get("decided_at") or now_iso(),
            "source": "apply_queue_live",
        }
        added, updated = upsert_decisions([row])
        app_n = update_applications([row])
        self._json(
            200,
            {
                "ok": True,
                "job_decisions": {"added": added, "updated": updated},
                "applications_updated": app_n,
                "decision": row,
            },
        )


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
    print(f"date={args.date}")
    print("Pass → immediate write to data/job_decisions.csv (+ applications when matched)")
    print("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
