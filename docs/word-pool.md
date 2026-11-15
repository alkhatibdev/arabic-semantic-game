# The word pool

> **Status: design, not yet implemented.** This describes the next release.
> What ships today is described under [Today](#today-dates-pinned-at-seed-time).

## Today: dates pinned at seed time

`scripts/init_daily_words.py` reads a word list and writes one `daily_words` row
per date, months in advance. That makes the word list an answer key: anyone
holding it knows every future answer.

Which is why the real list is **not in this repository**. Only
`api/data/words.sample.json` (ten words, so a fresh clone is playable) is
tracked. That is a workaround, not a design: it means the most valuable
community contribution (more words) is the one thing nobody outside the project
can make.

## Next: selection at play time

Move the choice from seed time to play time, and the problem disappears.

### `word_pool`

A new table holding candidate words, with no dates attached:

| Column | Notes |
|---|---|
| `id` | |
| `word` | Unique |
| `status` | `pending` / `approved` / `rejected` |
| `source` | `seed` / `community` |
| `submitted_by` | Nullable player UUID |
| `times_used` | How many times this word has been a daily answer |
| `last_used_on` | Date of its most recent use, nullable |
| `created_at`, `reviewed_at`, `reviewed_by` | |

`daily_words` keeps its unique `date` column, which archive permalinks and game
numbering depend on, and gains a `word_pool_id` foreign key.

### Picking a word

A new `get_or_create_for_date` runs on the first request for a date that has no
row yet:

1. **Candidates**: `status = 'approved'`, and either never used or
   `last_used_on` older than `WORD_REUSE_COOLDOWN_DAYS` (default 180).
2. **Fairest first**: take the minimum `times_used` among candidates, then pick
   uniformly at random within that group.
3. **Commit**: insert the `daily_words` row, increment `times_used`, set
   `last_used_on`.

**Recycling is free.** Once every approved word sits at `times_used = k`, step 2
draws from the whole pool again at `k`. There is no exhaustion branch to write
and no "we ran out of words" failure mode. A hard fallback ignores the cooldown
if it ever starves the candidate set.

**Concurrency is the one real hazard.** Two players hitting a new date in the
same instant must not create two different words for it. `daily_words.date` is
already unique, so:

```sql
INSERT INTO daily_words (word, date, word_pool_id)
VALUES (:word, :date, :pool_id)
ON CONFLICT (date) DO NOTHING
RETURNING id;
```

An empty result means another request won; re-select and use theirs. A Postgres
advisory lock keyed on the date is the alternative.

### Why this makes the pool publishable

The pool becomes public, but the **pool → date mapping is created at the moment
someone first plays that date and does not exist before then**. Reading the
repository tells you the set of possible words and nothing about which one is
today's. Nobody can know tomorrow's answer, including the maintainers.

## Community contributions

Two tracks, both ending in human review.

### Pull requests

`api/data/word-pool.json` becomes a tracked file. A CI check validates every
added entry:

- Arabic script only, no Latin characters
- A single token: no spaces
- No diacritics
- Within length bounds
- Not already in the pool
- Actually embeddable by the configured model (does not tokenize to UNK)

Merged entries are loaded by `scripts/sync_word_pool.py`. The validator builds
on the Latin-script rejection already in
`api/app/services/similarity_service.py`.

### In-app suggestions

`POST /api/v1/words/suggest`, rate-limited, writing `status = 'pending'` with
`source = 'community'`. Review happens through a CLI script or an endpoint
behind an `ADMIN_API_TOKEN`.

**Nothing is auto-approved, on either track.** One offensive or broken word
ruins the day for every player simultaneously, and there is no way to take it
back once people have started playing.

## Migration

- An Alembic revision creating `word_pool` and adding `daily_words.word_pool_id`.
- `scripts/migrate_words_to_pool.py` to backfill existing `daily_words.word`
  values into the pool with their real `times_used` and `last_used_on`.
- Existing `daily_words` rows are left alone: past challenges keep their words,
  so the archive is unaffected.

## Open questions

- Should the cooldown scale with pool size, rather than a fixed 180 days? With a
  small pool a long cooldown starves the candidate set immediately.
- Should words have a difficulty rating, so the pool can be balanced across the
  week rather than drawn uniformly?
