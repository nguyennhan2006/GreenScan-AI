# Contributing

1. Create a focused issue describing the failure mode and expected behaviour.
2. Add or update a golden case before changing retrieval, prompts, models or scoring.
3. Keep modules replaceable through interfaces; avoid provider logic in domain code.
4. Run `make test` and `make lint` before opening a pull request.
5. Include before/after stage metrics, not only anecdotal examples.
6. Never commit confidential reports, API keys or personal data.

## Pull request acceptance

- Tests pass.
- No reduction beyond the agreed tolerance on the regression set.
- New output fields are documented and schema-versioned.
- Legal or scoring changes identify the reviewer and effective date.
