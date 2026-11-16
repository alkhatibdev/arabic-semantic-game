# Security Policy

## Reporting a vulnerability

Please report security issues privately through
[GitHub Security Advisories](https://github.com/alkhatibdev/arabic-semantic-game/security/advisories/new)
rather than opening a public issue. You can expect an acknowledgement within a
few days.

## Known limitations

These are design characteristics of the current version, not undiscovered bugs.
They are listed here so anyone deploying this knows what they are getting.

### There is no authentication

A player is identified only by a UUID that the browser generates and stores in
`localStorage`. The API accepts that UUID at face value. Concretely:

- Anyone who knows a player's UUID can read that player's guesses, hints and
  game status, and can submit guesses as them.
- Any UUID sent to the API creates a user row on first use, so an unauthenticated
  caller can grow the `users` table. Rate limiting is the only thing bounding it.

This is acceptable for an anonymous daily puzzle with no accounts, no personal
data and nothing to steal. It would not be acceptable if accounts, profiles or
leaderboards were added. Signed anonymous sessions are on the roadmap for that
reason.

### Rate limiting requires Redis, and correct proxy configuration

`RATE_LIMIT_ENABLED=true` (the default) needs a reachable Redis. Setting it to
`false` disables limiting entirely, which is fine locally and unsafe in public.

Requests are bucketed by the IP uvicorn reports. The app does not read
`X-Forwarded-For` itself, because a client can set it freely. If you deploy
behind a proxy, set `FORWARDED_ALLOW_IPS` to that proxy's address so uvicorn
resolves the real client address — otherwise every visitor shares one bucket.
Never set it to `*`. See [docs/configuration.md](docs/configuration.md#behind-a-proxy).

### Spoiler surface

Word selection currently assigns a word to each date at seed time, so whoever
holds the seed file knows future answers. The seed file is therefore not in this
repository. Decoupling selection from dates (so the answer is drawn at play
time and nobody can know it in advance) is the first roadmap item. See
[docs/word-pool.md](docs/word-pool.md).
