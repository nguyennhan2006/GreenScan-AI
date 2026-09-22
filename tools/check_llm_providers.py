#!/usr/bin/env python3
"""Check which model providers are reachable, and prove routing resolves.

Run this right after pasting an API key -- it answers "is my key working"
without starting the API or the pipeline.

    python tools/check_llm_providers.py
    python tools/check_llm_providers.py --provider fpt --live
    python tools/check_llm_providers.py --task claim_extraction

`--live` sends one tiny completion. Without it, only configuration and
healthcheck are inspected and no tokens are spent.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").split("\n"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", type=Path, default=REPO / ".env")
    ap.add_argument("--provider", action="append", default=[])
    ap.add_argument("--task", default=None, help="Show routing for one task")
    ap.add_argument("--live", action="store_true", help="Send one real completion")
    args = ap.parse_args()

    load_dotenv(args.env)

    from quantum_gw.providers.registry import PROVIDERS
    from quantum_gw.settings import load_gateway_settings

    s = load_gateway_settings()
    names = args.provider or list(PROVIDERS)

    print(f"active provider : {s.provider}")
    print(f"fallback order  : {', '.join(s.fallback_order)}")
    print(f"routing file    : {s.routing_file}\n")

    rows = []
    for name in names:
        try:
            p = PROVIDERS[name](s)
        except Exception as exc:  # noqa: BLE001
            rows.append((name, "BUILD-ERROR", "-", str(exc)[:60]))
            continue
        configured = p.is_configured()
        info = p.model_info()
        if not configured:
            rows.append((name, "not configured", info.model or "-", "no key/url/model set"))
            continue
        try:
            healthy = p.healthcheck()
        except Exception as exc:  # noqa: BLE001
            rows.append((name, "UNREACHABLE", info.model or "-", f"{type(exc).__name__}: {exc}"[:60]))
            continue
        note = info.endpoint or ""
        if healthy and args.live:
            try:
                r = p.generate([{"role": "user", "content": "Reply with the single word: ok"}])
                note = f"live reply: {r.text.strip()[:40]!r}"
            except Exception as exc:  # noqa: BLE001
                note = f"live call failed: {type(exc).__name__}: {exc}"[:70]
        rows.append((name, "READY" if healthy else "configured, unhealthy",
                     info.model or "-", note))

    width = max(len(r[0]) for r in rows)
    for name, status, model, note in rows:
        print(f"  {name:<{width}}  {status:<22} {model:<34} {note}")

    if args.task:
        import yaml
        rf = REPO / s.routing_file
        routing = (yaml.safe_load(rf.read_text(encoding="utf-8")) or {}).get("routing", {})
        cfg = routing.get(args.task)
        print(f"\ntask '{args.task}': {cfg or 'not in routing.yaml'}")
        if cfg and cfg.get("primary") == "deterministic":
            print("  -> solved in Python; no model is called for this task by design.")

    ready = [r[0] for r in rows if r[1] == "READY"]
    print(f"\n{len(ready)} provider(s) ready: {', '.join(ready) or 'none'}")
    if not ready:
        print("Nothing is reachable. The pipeline still runs on deterministic heuristics,\n"
              "but any task routed to a model will fall through its chain and fail.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
