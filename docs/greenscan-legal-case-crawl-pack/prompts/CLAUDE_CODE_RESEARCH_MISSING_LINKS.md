# Claude Code Prompt — Resolve Missing Official Links

Use only when a target has `not_found` / `blocked` / incomplete historical reporting coverage.

For the target:

1. Start from its official `report_urls` seeds and official regulator `case_url`.
2. Search/discover only official company, authority, securities filing, or court domains first.
3. Record every checked URL and result in `source_discovery.json`.
4. Do not infer direct PDF slugs from year/name unless the official listing exposes that pattern and you verify it.
5. If no official historical report exists, set a reason code rather than using a random mirror.
6. If company/entity renamed or merged, add an explicit relationship record with effective date and keep historical entity boundaries.
7. Update `config/legal_case_targets.yaml` only after confirming the new seed is official and stable; add a regression fixture for JS/API discovery when appropriate.
