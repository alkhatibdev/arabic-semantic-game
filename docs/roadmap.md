# Roadmap

Two features are designed and not yet built. Both are tracked as issues; this
is the design detail behind them.

---

## 1. Date-independent word selection + community pool

Full design: **[word-pool.md](word-pool.md)**.

Short version: words are drawn from a pool at play time instead of being pinned
to dates at seed time. That makes the pool safe to publish, which in turn makes
"add a word" a contribution anyone can make. Recycling falls out of a
least-used-first draw, so the pool never runs dry.

This is the first item because the second one is less useful without it, and
because it is what lets the repository stop withholding its own data.

---

## 2. On-demand LLM hint generation

> **Status: design, not yet implemented.**

### The problem

Hints live in the `word_hints` table, authored by hand. The only authoring path
was an admin endpoint that was disabled for having no auth, and then deleted
before open-sourcing. So most words have no hints, and
`POST /game/{date}/hints/{user_id}` answers `404 No hints available`. The
feature is in the UI and mostly does not work.

### The flow

Generate a hint the first time anyone needs one, then serve that same hint to
everyone else. `HintService.provide_hint` becomes:

1. **Per-user cap.** Unchanged: a player may reveal `MAX_HINTS_PER_USER` hints
   (default 3) for a given word.
2. **Cache hit.** Ask for a hint this player has not seen. If one exists, serve
   it. **No LLM call.** This is the common path: by the second player of the
   day, every hint is already written.
3. **Cache miss, under the ceiling.** If the word has fewer than
   `MAX_GENERATED_HINTS_PER_WORD` (default 8) hints total, generate one,
   persist it with `generated_by = '<model-id>'` and
   `hint_order = max + 1`, and serve it.
4. **Ceiling reached.** Stop generating and serve from what exists. With a
   per-user cap of 3 and a per-word ceiling of 8, every player can still get
   three distinct hints. The ceiling exists purely to bound cost, not to
   restrict players.
5. **LLM unavailable**: no key, timeout, upstream rate limit. Fall back to the
   existing pool. If the pool is empty, return `503` with an Arabic message.
   Never a `500`, and never a stack trace to a player mid-game.

So the answer to "what happens when the per-word maximum is exceeded" is: it
stops generating and reuses what was already generated. Generation is a
cache-fill, not a per-request cost.

### The generator

One async **OpenAI-compatible** client, in `api/app/services/hint_generator.py`.
Pluggable by base URL rather than by provider adapter: one code path reaches
OpenAI, Groq, Together, OpenRouter, a local Ollama, or a self-hosted vLLM.

```bash
HINT_LLM_ENABLED=false                       # default false: a clone needs no key
HINT_LLM_BASE_URL=https://api.openai.com/v1  # or .../openrouter, localhost:11434/v1, ...
HINT_LLM_API_KEY=
HINT_LLM_MODEL=
HINT_LLM_TIMEOUT_SECONDS=10
MAX_GENERATED_HINTS_PER_WORD=8
MAX_HINTS_PER_USER=3
```

Default-off matters: a public clone must work out of the box for someone with
no API key and no intention of getting one.

The prompt lives in a file, not inline. It asks for Modern Standard Arabic, one
sentence, progressively more specific by `hint_order`, and receives the hints
already generated for the word so it does not repeat them.

### The safety check that matters

**A hint must never contain the answer.** An LLM that leaks the target word
destroys the day for every player who asks for a hint. Unlike a bad word
in the pool, it happens silently.

So every generated hint is validated before it is served *or persisted*:

- Strip diacritics from both the hint and the target
- Reject if the hint contains the target word
- Reject if it shares a root with the target (three or more consecutive root
  letters)
- Reject if it exceeds a length bound

On rejection: retry once, then fall back to the pool. Nothing unvalidated is
ever written to `word_hints`.

### Supporting fixes

- `user_word_hints` has only a non-unique composite index. It needs a
  uniqueness constraint, so a double-clicked hint button cannot burn two of a
  player's three slots.
- Two players hitting an empty pool simultaneously will both generate. Either
  take a per-word advisory lock, or accept the duplicate, since `set_hints` already
  deduplicates by hint text.

### Frontend

No structural change needed. `HintModal` already handles `maxHints`,
`requesting` and `error` states, and `max_hints` now comes from the API rather
than a hardcoded `3`. It needs:

- A spinner tolerant of 1-3 seconds, since a cache miss now waits on an LLM
- An Arabic message for the `503` path

---

## Smaller items

- **Signed anonymous sessions.** Closes the IDOR surface described in
  [SECURITY.md](../SECURITY.md) without introducing accounts.
- **Web component tests.** The API has unit and integration suites; the
  frontend has none.
- **i18n scaffolding.** All ~45 user-facing strings are inline Arabic literals.
  Extracting them to a strings module would make the codebase legible to
  non-Arabic-speaking contributors, and is the prerequisite for any second
  language.
- **Score-bar accessibility.** Similarity is conveyed by colour plus a number,
  with no `role="progressbar"` or `aria-valuenow`.
