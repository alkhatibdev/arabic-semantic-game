# Contributing

Thanks for taking a look. This is a small project and almost everything is open
for improvement. The lists below are where help goes furthest.

## Good first contributions

- **Words.** The pool always needs more good Arabic words. See
  [Suggesting words](#suggesting-words).
- **Screenshots.** The README has light and dark captures of a game in
  progress; a win screen and a mobile view would round it out.
- **Tests.** The API has unit and integration suites; the web app has none.
  Component tests are the biggest gap.
- **Accessibility.** The modals got a pass recently; the guess list and score
  bars have not.

## Development setup

See the [Quickstart](README.md#quickstart) in the README. `docker compose up`
is the shortest path to a running stack.

### Backend checks

```bash
cd api
ruff check .          # lint
ruff format .         # format
pytest                # unit tests; no database or model download needed
```

Integration tests run against a real PostgreSQL and are skipped unless you ask
for them:

```bash
docker run -d --name pg -e POSTGRES_PASSWORD=postgres -p 55432:5432 postgres:16-alpine

RUN_INTEGRATION_TESTS=1 \
DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:55432/postgres \
pytest tests/api
```

They **drop and recreate the `public` schema**, so point them at a throwaway
database, never one you care about.

Both suites avoid the embedding model: `tests/conftest.py` installs a
`FakeModel`, so everything runs in a couple of seconds. Keep it that way: a
test that downloads 500 MB is a test nobody runs.

### Frontend checks

```bash
cd web
npm run lint
npm run typecheck
npm run format
npm run build
```

CI runs all of the above on every pull request.

### Database migrations

The schema is managed by Alembic. After changing a model:

```bash
cd api
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

Review the generated migration before committing. Autogenerate is a starting
point, not an oracle. Keep a single head.

## Suggesting words

A good target word is:

- A real Modern Standard Arabic word, written **without diacritics**
- A **single token**: no spaces, no multi-word phrases
- Concrete enough that semantic neighbours exist (`مطر`, `جسر`, `عدالة` are
  good; extremely rare or highly technical terms are not)
- Not offensive, and not a slur or a politically inflammatory term
- Not a private individual's name

Two ways to submit:

1. **Open an issue** using the *Word suggestion* template. Easiest, and the
   right choice for a handful of words.
2. **Open a pull request** adding to the word pool file. This is the path once
   the public word pool lands. See [docs/word-pool.md](docs/word-pool.md).

Every word is reviewed before it can appear. Nothing is auto-approved: a bad
word spoils the day for every player at once.

**Do not open an issue or PR that reveals a current or upcoming answer.**

## Pull requests

- Branch off `main` and keep the change focused.
- Make sure lint, typecheck and tests pass locally.
- Describe what changed and why. If it changes player-visible behaviour, say so
  explicitly.
- New API endpoints need a line in [docs/api.md](docs/api.md).

## Reporting bugs

Use the *Bug report* issue template. For anything with security implications,
follow [SECURITY.md](SECURITY.md) instead of filing a public issue.

## Code of conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).
