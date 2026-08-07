# Commenting standard

**Mandate:** Agents must leave clear, concise comments on non-obvious code in every PR. Skipping useful comments is a process failure when the “why” is not obvious from names/types.

## Do

- Explain **why**, constraints, and invariants (security, confirm-before-save, SQLite quirks, LLM draft vs persist).
- Prefer one short module/file blurb or a single line above a tricky block.
- Keep comments accurate when behavior changes (update or delete stale ones).

## Don’t

- Narrate obvious code (`# increment i`, `# return result`).
- Paste large SPECs into source; link docs instead.
- Leave commented-out dead code.

## Examples

```python
# SQLite: allow FastAPI's threaded request handling on one connection.
return {"connect_args": {"check_same_thread": False}}
```

```python
# Metadata only — never store PDF bytes in activity logs.
```
