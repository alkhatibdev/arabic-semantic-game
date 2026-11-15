# Architecture

Two services, one database, one cache.

```
   Browser
      │  anonymous UUID in localStorage, sent with every call
      ▼
┌──────────────┐   NEXT_PUBLIC_API_URL    ┌──────────────────┐
│  web         │ ───────────────────────► │  api             │
│  Next.js 16  │                          │  FastAPI         │
│  App Router  │ ◄─────────────────────── │                  │
└──────────────┘      JSON                └────────┬─────────┘
                                                   │
                            ┌──────────────────────┼─────────────────┐
                            ▼                      ▼                 ▼
                    ┌───────────────┐      ┌─────────────┐   ┌───────────────┐
                    │  PostgreSQL   │      │   Redis     │   │ sentence-     │
                    │  game state   │      │ rate limits │   │ transformers  │
                    └───────────────┘      └─────────────┘   └───────────────┘
```

## Request flow for a guess

1. `POST /api/v1/game/guess` with `{user_id, challenge_date, word}`.
2. The route rejects future dates and empty words, then hands off to
   `GameService.submit_guess`.
3. The user row is created if this UUID has never been seen.
4. The target word for that date is loaded from `daily_words`.
5. `SimilarityService.calculate_similarity_async` embeds both words and takes
   the cosine. This runs in a worker thread, because `model.encode()` is a synchronous
   CPU-bound call and would otherwise stall the event loop for every other
   request in flight.
6. The guess is stored. A repeat of the same word returns the existing row
   rather than inserting a duplicate.
7. The response carries the 0-100 score, the raw cosine, correctness, and the
   player's attempt count.

The session commits once, in the `get_db` dependency's teardown.

## Layers in `api/app`

| Layer | Responsibility |
|---|---|
| `api/v1/endpoints/` | HTTP concerns: parsing, status codes, rate-limit dependencies |
| `services/` | Game rules: scoring, hint allowance, win detection |
| `crud/` | Database queries, one module per model |
| `models/` | SQLAlchemy tables |
| `schemas/` | Pydantic request and response shapes |
| `core/` | Settings, logging, model loading, rate limiter |

Endpoints never touch the ORM directly; services never build HTTP responses.

## Database schema

| Table | Purpose |
|---|---|
| `users` | Anonymous players. Primary key is the client-supplied UUID. |
| `daily_words` | One row per date: the target word. `date` is unique. |
| `user_guesses` | Every guess, with both scores. Unique on (user, word, guess) so a repeat is idempotent. `is_given_up` marks the revealed answer. |
| `word_hints` | Hints, keyed by word text and ordered by `hint_order`. |
| `user_word_hints` | Which hints a given player has unlocked. |

`user_guesses.cosine_similarity` keeps the raw value alongside the scaled
`similarity_score`, so the scoring curve can be changed later without losing
the underlying measurement.

## Model loading

`ModelLoader` is a singleton that imports `sentence_transformers` and downloads
the model **on first use, not at import**. This matters: Alembic, the seed
scripts and the test suite all import modules in this chain, and none of them
should pull in torch or wait on a 500 MB download.

The model is loaded eagerly in the FastAPI lifespan, so the first player does
not pay for it.

## Frontend state

There is no state library. `GameBoard` owns the game state in `useState` and
passes it down; two React contexts carry cross-cutting concerns (`ThemeContext`,
`ToastContext`). All API calls go through the single `fetchApi` wrapper in
`web/lib/api.ts`, which converts non-2xx responses into a typed `ApiError`
carrying the HTTP status. The UI branches on `err.status` for 403 and 404.

Dates are UTC everywhere. `getTodayDateUTC()` and `shiftDateUTC()` in
`web/lib/utils.ts` deliberately avoid local-time round-trips, which would move
the current challenge by a day for players west of UTC.
