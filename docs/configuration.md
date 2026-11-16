# Configuration

Both services read plain env files. Nothing secret is required to run locally.

## API

The settings class is `api/app/core/config.py`. Values come from the
environment, falling back to an env file.

### Which file is loaded

In priority order:

1. `ENV_FILE=<path>` if set, which overrides everything
2. `.env`, the conventional name and the one to use
3. `.env.dev` (or `.env.prod` when `ENVIRONMENT=production`), kept for
   existing deployments

So `cp .env.example .env` is all that's needed. (An earlier version loaded only
`.env.dev`, which meant the conventional filename was silently ignored and
startup failed with an opaque `DATABASE_URL Field required`.)

### Variables

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | *(none)* | **Required.** Must use the `postgresql+asyncpg://` scheme. |
| `ENVIRONMENT` | `development` | Labels logs and Sentry events. Does **not** turn on SQL echo. |
| `LOG_LEVEL` | `INFO` | Standard Python levels. |
| `SQL_ECHO` | `false` | Echoes every statement **and its bound parameters** to stdout. Debugging only. |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | **JSON array**, not a comma-separated string. |
| `ML_MODEL_NAME` | `silma-ai/silma-embedding-matryoshka-v0.1` | Any sentence-transformers model. |
| `WORD_SEED_FILE` | `data/words.sample.json` | Used by `scripts/init_daily_words.py`. See [the seed file format](#seed-file-format). |
| `MAX_HINTS_PER_USER` | `3` | Served to clients in the game-state response. |
| `RATE_LIMIT_ENABLED` | `true` | See below. |
| `RATE_LIMIT_STORAGE_URI` | `redis://localhost:6379` | |
| `SENTRY_DSN` | *(empty)* | Sentry is skipped entirely when unset. |
| `FORWARDED_ALLOW_IPS` | `127.0.0.1` | Read by uvicorn, not by the app. See [behind a proxy](#behind-a-proxy). |

### Rate limiting and Redis

With `RATE_LIMIT_ENABLED=true`, **Redis is a hard requirement**: the limiter
stores counters there and requests fail without it.

Setting it to `false` substitutes a no-op dependency, so the app runs with no
Redis at all. Convenient locally; do not do it in public, since the API has no
authentication and nothing else bounds request volume.

### Behind a proxy

Requests are bucketed by **the IP uvicorn reports**, which for a direct
connection is the peer address. The application deliberately does not read
`X-Forwarded-For` itself: any client can send that header, and a version that
trusted it let every caller choose its own bucket, which is the same as having
no rate limit at all.

If you run behind nginx, a load balancer or a CDN, every request arrives from
the proxy, so without configuration the whole internet shares one bucket. Tell
uvicorn which peers are allowed to speak for others:

```bash
FORWARDED_ALLOW_IPS="10.0.0.5" uvicorn app.main:app --host 0.0.0.0 --port 8000
```

`--proxy-headers` is already on by default. uvicorn then rewrites the client
address from the forwarded headers **only** when the connecting peer is in that
list. Set it to your proxy's address; never set it to `*`, which restores the
original problem.

### Sentry and privacy

`send_default_pii` is **off**. Enabling it would send client IPs, headers and
request bodies, and those bodies here contain player UUIDs and guessed
words. For an anonymous game with no privacy policy, that is not a reasonable
default.

### Seed file format

`scripts/init_daily_words.py` accepts three shapes. Hints are optional, and
words without an explicit date get consecutive dates from `--start-date`.

```jsonc
["كتاب", "بحر"]                                   // dated from --start-date
{"words": ["كتاب", "بحر"]}                        // same, with a wrapper key
{"words": [
  {"word": "كتاب", "hints": ["يُقرأ", "له صفحات"]},   // hints seeded alongside
  {"word": "بحر", "date": "2026-12-01"}            // explicit date
]}
```

```bash
python scripts/init_daily_words.py --dry-run                    # report, write nothing
python scripts/init_daily_words.py --file /path/words.json      # your own list
python scripts/init_daily_words.py --shuffle --start-date 2026-12-01
```

Dates that already have a word are skipped, so re-running is safe.

## Web

Next.js inlines `NEXT_PUBLIC_*` variables **at build time**, not at runtime. A
Docker image built with one `NEXT_PUBLIC_API_URL` cannot be repointed by
changing the environment at `docker run`. Rebuild instead. The Dockerfile
takes them as build args for this reason.

| Variable | Default | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Browser-visible, so it must be reachable from the user's machine, not a Docker service name. |
| `NEXT_PUBLIC_SITE_URL` | `http://localhost:3000` | Used as `metadataBase` for canonical and OG URLs. |
| `NEXT_PUBLIC_GA_MEASUREMENT_ID` | *(empty)* | No analytics scripts are emitted when unset. |

None of these are secrets: anything prefixed `NEXT_PUBLIC_` is visible in the
shipped JavaScript by design. Never put a private key behind that prefix.

Local overrides belong in `web/.env.local`, which is gitignored.

## Deployment notes

- Run migrations before starting the API: `alembic upgrade head`.
- Point a persistent volume at the Hugging Face cache (`HF_HOME`) so the model
  is not re-downloaded on every deploy.
- `/health` is unmetered and is the right target for liveness probes. `/` is
  rate-limited at 60/min and will trip aggressive pollers.
- Set `CORS_ORIGINS` to your real frontend origin. The default is localhost
  only, deliberately, so a fork does not inherit anyone else's origins.
- Set `FORWARDED_ALLOW_IPS` if anything sits in front of the API, or rate
  limiting will bucket every visitor together. See [behind a proxy](#behind-a-proxy).
- Leave `SQL_ECHO` off outside debugging: it writes every query and its bound
  parameters, which include player UUIDs and guessed words, to stdout.
- The `docker-compose.yml` Postgres and Redis are bound to `127.0.0.1` and use
  throwaway credentials. They are for local development; do not expose them.
