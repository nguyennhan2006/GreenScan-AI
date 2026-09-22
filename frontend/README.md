# GreenScan AI — web UI (v2)

React 19 + Vite 8 + Tailwind 4. No router library: `src/lib/router.jsx` is a
tiny hash router so deep links (`#/runs/<id>/claims/<claim>`) survive a reload
and a saved run can be opened straight from a URL.

```bash
npm install
npm run dev        # http://localhost:5173, proxies /api → http://localhost:8000
npm run build
npm run lint
```

Start the API first: `python -m quantum_gw.cli serve --port 8000` from the repo root.

## Layout

| Path | Screen |
| --- | --- |
| `#/start` | reviewer name (no accounts exist; the name goes into the review trail) |
| `#/new` | 3-step intake: sources → configuration → run |
| `#/runs` | saved runs (`GET /v1/runs`), rename, reopen |
| `#/runs/:id` | overview: work queues, missing attributes, verdict distribution, gates |
| `#/runs/:id/claims` | claim list with status filters |
| `#/runs/:id/claims/:claimId` | claim detail in audit order; `?tab=review` jumps to the decision bar |
| `#/runs/:id/review` | review queue by workflow state |
| `#/runs/:id/export` | evidence-pack downloads |
| `#/legal` | legal registry (`GET /v1/legal/corpus`) |
| `#/settings` | reviewer, model gateway (read-only), gold stats |

Design rules (what may never appear: company scores, rankings, accusatory
wording) are in `../docs/05-ui/PRODUCTION_UI_SPEC_2026-09-20.md` §1 and §4.6.
Semantic colours live in `src/components/badges.jsx`; the five mandatory
attributes and the row model in `src/lib/claims.js`.
