## What does this change?

<!-- A sentence or two. Link the issue it closes, if any. -->

## Why?

<!-- The problem being solved. Skip if the "what" already makes it obvious. -->

## Checklist

- [ ] Lint and typecheck pass (`ruff check .` / `npm run lint && npm run typecheck`)
- [ ] Tests pass (`pytest` / `npm run build`)
- [ ] No real `.env`, credentials, or answer words included
- [ ] API change? Updated `docs/api.md`
- [ ] Schema change? Added a migration, and `alembic heads` still shows one head
- [ ] Player-visible behaviour change? Described above
