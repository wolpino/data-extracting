# Roadmap (post-MVP)

Short “with more time” list — not built in the 4h window unless spare time after a green public deploy. Aligns with SPEC SHOULD/CUT and DECISIONS.

## Next hardening

1. **Auth / shared API key** — gate write + `/extract` on the public URL
2. **Rate limiting** — especially `/extract` + Gemini quota
3. **Postgres** — durable DB on Render (replace ephemeral SQLite)
4. **Confirm UX** — modal near action (replace top-of-page banner)

## Product / data

- Spec B Order fields: `status`, `notes`, `equipment_type`
- Multi-MIME extract (images, DOCX) via the existing `bytes + content_type → draft` boundary
- Citation / page hints from documents
- Broader DME intake fields (insurance, HCPCS, NPI) if required

## Engineering

- Alembic migrations (replace `create_all` for prod)
- Caching / batch / async job queues (SPEC S3)
- Dependency scanning CI; security headers / CSP beyond platform defaults
- Malware scanning of uploads; real PHI retention policy (N/A for Buffy fake demo data)

Planning handoff prompt: [prompts/post-pr5-planning-agent.md](./prompts/post-pr5-planning-agent.md).
