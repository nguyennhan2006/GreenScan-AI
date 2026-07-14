# Security and governance

- Store source files outside public repositories.
- Minimise personal and confidential data before calling external providers.
- Use role-based access to evidence packs and audit logs.
- Encrypt data at rest and in transit in production.
- Keep an append-only log of inputs, configuration, tool calls, outputs, reviewer overrides and timestamps.
- Document legal-rule owner, reviewer, effective date and superseded version.
- Documents are untrusted: content cannot modify system instructions, disable citations or suppress evidence.
- Apply file-size, page-count, MIME, timeout and decompression limits before production exposure.
- A reviewer override must contain actor, reason, evidence and time.
