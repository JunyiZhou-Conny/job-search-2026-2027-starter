#!/usr/bin/env python3
"""Fetch public Grok Bot / pstack / Poteto sources into a directory.

Default output is /tmp/agent-sources. Does not log in. Public GET only.

  python3 scripts/research/fetch_agent_sources.py
  python3 scripts/research/fetch_agent_sources.py --out /tmp/agent-sources
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = (
    "Mozilla/5.0 (compatible; job-search-research/1.0; "
    "+https://github.com/JunyiZhou-Conny/job-search-2026-2027-starter)"
)

URLS = [
    "https://t.co/zWiTOPKXPr",
    "https://raw.githubusercontent.com/cursor/plugins/main/pstack/docs/guide/README.md",
    "https://raw.githubusercontent.com/cursor/plugins/main/pstack/docs/guide/02-poteto-mode.md",
    "https://raw.githubusercontent.com/cursor/plugins/main/pstack/docs/guide/06-verify-and-ship.md",
    "https://raw.githubusercontent.com/cursor/plugins/main/pstack/docs/guide/07-overnight.md",
    "https://maven.com/p/e23d9c",
    "https://docs.x.ai/grok-bot/use-cases",
    "https://docs.x.ai/grok-bot/faq",
    "https://docs.x.ai/grok-bot/computer-and-apps",
    "https://docs.x.ai/grok-bot/approvals-security-and-privacy",
    "https://x.ai/news/introducing-grok-bot",
    "https://x.ai/news/grok-bot-more-plans",
    "https://api.fxtwitter.com/poteto",
]


def slug(url: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", url).strip("_")[:160]


def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    ctx = ssl.create_default_context()
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            body = resp.read()
            return {
                "url": url,
                "ok": True,
                "status": resp.status,
                "final_url": resp.geturl(),
                "bytes": len(body),
                "elapsed_s": round(time.time() - started, 2),
                "body": body,
            }
    except urllib.error.HTTPError as exc:
        body = exc.read() if exc.fp else b""
        return {
            "url": url,
            "ok": False,
            "status": exc.code,
            "bytes": len(body),
            "error": str(exc),
            "elapsed_s": round(time.time() - started, 2),
            "body": body,
        }
    except (urllib.error.URLError, TimeoutError, OSError, ssl.SSLError) as exc:
        return {
            "url": url,
            "ok": False,
            "status": None,
            "bytes": 0,
            "error": f"{type(exc).__name__}: {exc}",
            "elapsed_s": round(time.time() - started, 2),
            "body": b"",
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="/tmp/agent-sources")
    args = parser.parse_args()
    out = Path(args.out)
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    results = []
    for url in URLS:
        print(f"FETCH {url}", flush=True)
        result = fetch(url)
        body = result.pop("body")
        if body:
            path = raw / f"{slug(url)}.bin"
            path.write_bytes(body)
            result["path"] = str(path)
        results.append(result)
        print(
            f"  -> status={result.get('status')} ok={result.get('ok')} "
            f"bytes={result.get('bytes')} err={result.get('error')}",
            flush=True,
        )
        time.sleep(0.3)

    index = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    index_path = out / "index.json"
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"WROTE {index_path}", flush=True)


if __name__ == "__main__":
    main()
