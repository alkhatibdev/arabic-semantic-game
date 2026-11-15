# api: FastAPI backend

Embeddings, scoring, game state and hints. See the
[root README](../README.md) for the full project, and
[docs/architecture.md](../docs/architecture.md) for how this fits together.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

cp .env.example .env          # set DATABASE_URL
alembic upgrade head
python scripts/init_daily_words.py
uvicorn app.main:app --reload
```

Requires PostgreSQL, and Redis unless you set `RATE_LIMIT_ENABLED=false`.
Interactive docs at <http://localhost:8000/docs>.

## Develop

```bash
pip install -r requirements-dev.txt
ruff check . && ruff format .
pytest                          # fast: no database, no model download

# integration suite against a throwaway Postgres (drops the public schema)
RUN_INTEGRATION_TESTS=1 DATABASE_URL=... pytest tests/api
```

## Layout

```
app/
├── api/v1/endpoints/   HTTP routes
├── services/           game rules
├── crud/               database queries
├── models/             SQLAlchemy tables
├── schemas/            Pydantic request/response shapes
└── core/               settings, logging, model loader, rate limiter
alembic/versions/       migrations
scripts/                seeding
data/words.sample.json  ten sample words (not the production list)
```

## Reference

- [Configuration](../docs/configuration.md)
- [API endpoints](../docs/api.md)
- [Scoring](../docs/scoring.md)
