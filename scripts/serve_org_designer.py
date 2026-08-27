#!/usr/bin/env python3
"""Local org designer. Writes a staffing plan. Does not hire Bots.

  python3 scripts/serve_org_designer.py
  open http://127.0.0.1:8766/
"""

from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from org_designer.model import draft_from_wire  # noqa: E402
from org_designer.service import (  # noqa: E402
    DesignRejected,
    OrgDesigner,
    RevisionConflict,
    SaveDesign,
    receipt_to_wire,
    review_to_wire,
    snapshot_to_wire,
)

STATIC_ROOT = ROOT / "static"
TEMPLATE = ROOT / "templates" / "org_designer" / "index.html"

CONTENT_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
}


class Handler(BaseHTTPRequestHandler):
    designer: OrgDesigner
    protocol_version = "HTTP/1.1"

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
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _payload(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if path in {"/", "/index.html", "/org"}:
            html = TEMPLATE.read_text(encoding="utf-8")
            qs = parse_qs(parsed.query)
            template = (qs.get("template") or [""])[0].strip() or None
            try:
                snap = self.designer.read(template)
            except KeyError:
                self._json(404, {"error": "unknown template"})
                return
            boot = json.dumps(snapshot_to_wire(snap), ensure_ascii=False).replace("</", "<\\/")
            html = html.replace("__BOOTSTRAP__", boot)
            self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path.startswith("/static/"):
            rel = path[len("/static/") :]
            target = (STATIC_ROOT / rel).resolve()
            if not str(target).startswith(str(STATIC_ROOT.resolve())) or not target.is_file():
                self._json(404, {"error": "not found"})
                return
            ctype = CONTENT_TYPES.get(target.suffix, "application/octet-stream")
            self._send(200, target.read_bytes(), ctype)
            return
        if path == "/api/org":
            qs = parse_qs(parsed.query)
            template = (qs.get("template") or [""])[0].strip() or None
            fresh = (qs.get("fresh") or [""])[0] == "1"
            try:
                snap = self.designer.read(template, fresh=fresh)
            except KeyError:
                self._json(404, {"error": "unknown template"})
                return
            self._json(200, snapshot_to_wire(snap))
            return
        if path == "/api/health":
            self._json(200, {"ok": True, "hire_allowed": False})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            payload = self._payload()
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return
        if path == "/api/org/review":
            draft = draft_from_wire(payload.get("draft") or payload)
            self._json(200, review_to_wire(self.designer.review(draft)))
            return
        self._json(404, {"error": "not found"})

    def do_PUT(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/api/org":
            self._json(404, {"error": "not found"})
            return
        try:
            payload = self._payload()
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return
        draft = draft_from_wire(payload.get("draft") or {})
        expected = str(payload.get("expected_revision") or "")
        write_brief = bool(payload.get("write_brief"))
        try:
            receipt = self.designer.save(
                SaveDesign(draft=draft, expected_revision=expected, write_brief=write_brief)
            )
        except DesignRejected as exc:
            self._json(422, {"error": "rejected", "issues": [
                {"code": i.code.value, "path": i.path, "message": i.message} for i in exc.issues
            ]})
            return
        except RevisionConflict as exc:
            self._json(409, {"error": "revision conflict", "expected": exc.expected, "actual": exc.actual})
            return
        self._json(200, receipt_to_wire(receipt))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8766)
    ap.add_argument("--root", default=str(ROOT))
    args = ap.parse_args()
    Handler.designer = OrgDesigner.at(Path(args.root))
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.daemon_threads = True
    print(f"Org designer: http://{args.host}:{args.port}/")
    print("Saves ORG_CHART.json + ORG_CHART.md. Export writes ORG_SPAWN_BRIEF.md.")
    print("Does not hire Bots. Does not write GROK_BOT_HANDOFF.md.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
