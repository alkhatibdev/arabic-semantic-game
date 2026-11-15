# API reference

Base URL: `http://localhost:8000` in development. Interactive docs are served at
`/docs` (Swagger) and `/redoc`.

All game endpoints are versioned under `/api/v1`. There is no authentication:
`user_id` is a client-generated UUID the API accepts at face value. See
[SECURITY.md](../SECURITY.md).

Dates are `YYYY-MM-DD` in **UTC**. Requests for a future date are rejected with
`403` on every endpoint that takes one.

## Meta

| Method | Path | Rate limit | Description |
|---|---|---|---|
| `GET` | `/health` | none | Liveness probe. Unmetered so load balancers can poll it. |
| `GET` | `/` | 60/min | Version and status. |

## Challenges

### `GET /api/v1/challenges/{challenge_date}`

`challenge_date` accepts a date or the literal `today`. Rate limit: 60/min.

```json
{ "date": "2026-11-15", "game_number": 42, "has_challenge": true }
```

`has_challenge` is `false` when no word has been seeded for that date;
`game_number` is then `0`.

## Game

### `POST /api/v1/game/guess`

Rate limit: 30/min.

```jsonc
// request
{ "user_id": "uuid", "challenge_date": "2026-11-15", "word": "مطر" }
```

```jsonc
// response
{
  "id": 1234,
  "word": "مطر",
  "similarity_score": 64.2,   // 0-100, what the player sees
  "cosine_similarity": 0.603, // raw measurement
  "is_correct": false,
  "attempt_number": 7,
  "created_at": "2026-11-15T09:30:00Z",
  "is_given_up": false
}
```

Guessing the same word twice returns the original row rather than creating a
duplicate. `400` for an empty word, `403` for a future date, `404` if no
challenge exists for that date.

### `POST /api/v1/game/giveup`

Rate limit: 10/min. Body is `{user_id, challenge_date}`. Returns the same shape
as a guess, with the target word revealed, `is_correct: true` and
**`is_given_up: true`**. That flag is how a client distinguishes giving up from
winning.

### `GET /api/v1/game/{challenge_date}/state/{user_id}`

Rate limit: 30/min. The endpoint the frontend actually uses: everything needed
to render a game in one call.

```jsonc
{
  "challenge_date": "2026-11-15",
  "game_number": 42,
  "guesses": [ /* GuessResponse[] */ ],
  "game_status": { "won": false, "attempts": 7, "won_at": null, "target_word": null },
  "has_won": false,
  "hints": [ { "hint_text": "...", "hint_order": 1 } ],
  "max_hints": 3
}
```

`target_word` is `null` until the player has won or given up.

### `GET /api/v1/game/{challenge_date}/guesses/{user_id}`

Rate limit: 30/min. The player's guesses, oldest first. That ordering is what
makes `attempt_number` meaningful. Clients sort by score for display.

### `GET /api/v1/game/{challenge_date}/status/{user_id}`

Rate limit: 30/min. Win state and attempt count only. `404` when no challenge
exists for the date.

## Hints

### `GET /api/v1/game/{challenge_date}/hints/{user_id}`

Rate limit: 60/min. Hints this player has already revealed.

### `POST /api/v1/game/{challenge_date}/hints/{user_id}`

Rate limit: 10/min. Reveals the next unseen hint.

```json
{ "hint_text": "يسقط من السماء", "hint_order": 1 }
```

- `403`: the player has used their allowance (`MAX_HINTS_PER_USER`)
- `404`: no challenge for that date, or no hints authored for that word

The `404` case is common today, because hints are authored by hand. On-demand
generation is the planned fix. See [roadmap.md](roadmap.md).

## Removed endpoints

Two endpoints were deleted before this project was open-sourced. They are listed
here so nobody reintroduces them:

- **`GET /api/v1/challenges/next-challenge/without-hints`** returned an unplayed
  target word to any anonymous caller, bypassing the future-date guard every
  other route enforces. It existed to help author hints offline.
- **`GET /populate-daily-words`** was an unauthenticated, publicly routed admin
  stub for seeding the database. Seeding belongs in
  `scripts/init_daily_words.py`.

A regression test in `api/tests/test_app.py` asserts both paths stay absent.
