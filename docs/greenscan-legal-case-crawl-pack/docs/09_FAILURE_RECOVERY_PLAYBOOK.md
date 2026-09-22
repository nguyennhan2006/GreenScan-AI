# 09 — Failure recovery playbook

## HTTP 403 / WAF

- Verify User-Agent/Accept headers and source policy.
- Check whether the document is reachable through official listing or regulator attachment route.
- Do not bypass access controls.
- If SEC: follow SEC fair-access style, contact-identifiable UA and low rate.
- Mark `BLOCKED_BY_SOURCE` if still inaccessible.

## 404 guessed URL

Do not mutate year/file slug blindly. Return to official listing seed and rediscover.

## robots.txt 403

Apply existing regression policy; never silently convert to global disallow.

## JS listing returns zero links

- inspect embedded JSON;
- inspect official API/XHR;
- use JS harvester;
- add fixture/regression test;
- fail run if `expected_listing=true` and zero candidates with no explicit reason.

## One entity dominates crawl

Apply per-target cap, scheduler round-robin and per-document-family cap. Log cap hits.

## Unknown year

Queue content-based year resolver; do not force from filename. Current 196 unknown-year docs prove this gate is necessary.

## TLS local proxy

Never use `verify=False`. Dev-only proxy trust shim may be activated explicitly; production must not depend on it.

## JSONL record mismatch

Check U+2028/U+2029/U+0085 escaping and reader `split("\n")`. Treat record-count mismatch as hard failure.

## Binary duplicate across multiple URLs

Keep one immutable binary object but retain multiple source/provenance records. Do not lose the authority/corporate source relationship.
