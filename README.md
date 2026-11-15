<div align="center">

<img src="web/public/og-image.png" alt="Arabic Semantic Game" width="640">

# Arabic Semantic Game · تحدي التشابه والتقارب

**An open-source Arabic word game exploring semantic similarity and sentence embeddings.**

Guess the secret word. Every guess is scored by how close its meaning is to the target, not by matching letters.

Powered by an Arabic sentence-embedding model, the game explores how machines represent and compare meaning in Arabic. A guess like `طبيب` (doctor) can score well against `مستشفى` (hospital), even though the two words share no letters.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![API: FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](api/)
[![Web: Next.js](https://img.shields.io/badge/Web-Next.js%2016-black.svg)](web/)

</div>

---

## What is this?

Arabic Semantic Game is a Semantle-style daily word puzzle built specifically for Arabic.

Everyone gets the same secret word each day. Players submit guesses and receive a similarity score indicating how close each word is to the target in meaning. The game also includes hints and an archive of previous puzzles.

Unlike traditional word games that rely on spelling, letter positions, or shared characters, this game uses **semantic similarity**. Two words can be closely related even when their written forms are completely different.

The project is also an exploration of Arabic NLP: taking sentence embeddings and applying them to an interactive, accessible experience for Arabic speakers.

## See it in action

<table>
<tr>
<td width="50%"><img src="docs/images/screenshot-light.png" alt="Arabic Semantic Game in light mode"></td>
<td width="50%"><img src="docs/images/screenshot-dark.png" alt="Arabic Semantic Game in dark mode"></td>
</tr>
</table>

For example, against the target `كتاب` (book):

| Guess | Meaning | Similarity |
|---|---|---:|
| `قراءة` | Reading | 71.8% |
| `مكتبة` | Library | 70.6% |
| `سيارة` | Car | 37.5% |

The scores come from semantic relationships, not shared letters.

## How semantic scoring works

Each guess is converted into a numerical vector using the Arabic sentence-embedding model:

[`silma-ai/silma-embedding-matryoshka-v0.1`](https://huggingface.co/silma-ai/silma-embedding-matryoshka-v0.1)

The backend compares the guess vector with the target word vector using cosine similarity.

The resulting similarity is transformed into a 0–100 score displayed in the game.

This allows the game to recognize relationships between words based on their contextual meaning rather than their spelling.

The scoring implementation and transformation are documented in [docs/scoring.md](docs/scoring.md).

## Technology stack

| Component | Technology |
|---|---|
| Backend API | Python, FastAPI |
| Semantic embeddings | Sentence Transformers, Silma Embedding |
| Database | PostgreSQL |
| Caching and rate limiting | Redis |
| Frontend | Next.js 16, React |
| Styling | Tailwind CSS v4 |
| Language support | Arabic, RTL layout |
| Deployment | Docker Compose |

## Repository layout

This is a monorepo containing two independently deployable services:

| Path | Description |
|---|---|
| [`api/`](api/) | FastAPI backend: embeddings, scoring, game state, and hints. PostgreSQL + Redis. |
| [`web/`](web/) | Next.js frontend: App Router, Tailwind v4, RTL Arabic, light/dark themes. |
| [`docs/`](docs/) | Architecture, API reference, scoring, configuration, and roadmap. |

## Quickstart

### With Docker (recommended)

```bash
git clone https://github.com/alkhatibdev/arabic-semantic-game.git
cd arabic-semantic-game
docker compose up --build
```

Then seed a few words and open the game:

```bash
docker compose exec api python scripts/init_daily_words.py
```

- Game: http://localhost:3000
- API documentation: http://localhost:8000/docs

The first start downloads the embedding model (approximately 500 MB) and takes a few minutes. Subsequent starts reuse the cached model.

<details>
<summary>Port already in use?</summary>

If you already run PostgreSQL or Redis locally, the containers cannot bind those ports. Override them:

```bash
POSTGRES_PORT=55432 REDIS_PORT=56379 docker compose up --build
```

Only the host-side ports change. Services still communicate using their default ports inside the Docker Compose network.

</details>

### Without Docker

You will need **Python 3.10+**, **Node.js 20+**, **PostgreSQL 14+**, and **Redis**.

<details>
<summary>Backend</summary>

```bash
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

cp .env.example .env
# Set DATABASE_URL in .env

alembic upgrade head
python scripts/init_daily_words.py
uvicorn app.main:app --reload
```

Redis must be running, or set `RATE_LIMIT_ENABLED=false` in `.env`.

</details>

<details>
<summary>Frontend</summary>

```bash
cd web
npm install
cp .env.example .env.local
npm run dev
```

`NEXT_PUBLIC_API_URL` defaults to `http://localhost:8000`.

</details>

## Configuration

Both services read environment variables from their respective env files.

Full reference: [docs/configuration.md](docs/configuration.md).

**`api/.env`**

The only required value is `DATABASE_URL`.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | None | **Required.** PostgreSQL connection string, e.g. `postgresql+asyncpg://user:pass@host:5432/db` |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | JSON array of allowed frontend origins |
| `ML_MODEL_NAME` | `silma-ai/silma-embedding-matryoshka-v0.1` | Sentence-transformers model |
| `WORD_SEED_FILE` | `data/words.sample.json` | Word list used by the seed script |
| `MAX_HINTS_PER_USER` | `3` | Hints a player may reveal per word |
| `RATE_LIMIT_ENABLED` | `true` | Whether Redis-based rate limiting is enabled |
| `RATE_LIMIT_STORAGE_URI` | `redis://localhost:6379` | Redis connection URI |
| `SENTRY_DSN` | Empty | Error tracking; disabled when unset |

**`web/.env.local`**

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend base URL |
| `NEXT_PUBLIC_SITE_URL` | `http://localhost:3000` | Canonical and Open Graph URLs |
| `NEXT_PUBLIC_GA_MEASUREMENT_ID` | Empty | Google Analytics; disabled when unset |

## Arabic word data

The daily word list is deliberately excluded from this repository.

In the current implementation, each word is assigned to a date during seeding. Publishing the complete word list would therefore expose future answers.

Instead, `api/data/words.sample.json` contains ten sample words, each with three hints, allowing a fresh installation to run a complete game.

A planned improvement is to move word selection from seed time to play time. This would allow the word pool to become public and enable the community to contribute words without exposing upcoming answers.

Design: [docs/word-pool.md](docs/word-pool.md).

## Security model and known limitations

**There is no authentication.**

Players are anonymous UUIDs generated in the browser, and the API trusts these identifiers. Anyone with a player's UUID can read and modify that player's game state.

For an anonymous daily puzzle without user accounts or personal data, this is a documented trade-off in the current version, not a claim of production-grade identity security.

Other known limitations and security considerations are documented in [SECURITY.md](SECURITY.md).

## Roadmap

- [ ] **Date-independent word selection and community word pool:** Select the answer at play time, allowing the word pool to become public. ([Design](docs/word-pool.md))
- [ ] **On-demand LLM hint generation:** Generate hints when first requested, with per-word limits and shared caching. ([Design](docs/roadmap.md))
- [ ] Signed anonymous sessions to address the current player-ID trust model.
- [ ] Component tests for the web application.
- [ ] Internationalization scaffolding; Arabic strings are currently inline.

## Contributing

Contributions are welcome! This project is an opportunity to explore Arabic NLP and build something useful for the Arabic-speaking community.

Some particularly useful contributions include:

- **Words:** Suggesting suitable Arabic words for future puzzles.
- **Hints:** Writing clear, indirect hints that help players discover the target.
- **Testing:** Improving backend and frontend test coverage.
- **Documentation:** Improving technical documentation and Arabic-language explanations.
- **Screenshots and feedback:** Reporting usability issues and suggesting improvements.

Start with [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Credits and licensing

The project code is licensed under the MIT License. See [LICENSE](LICENSE).

Third-party components:

| Component | Usage | License |
|---|---|---|
| [Silma Embedding Matryoshka v0.1](https://huggingface.co/silma-ai/silma-embedding-matryoshka-v0.1) | Arabic semantic embeddings; fine-tuned from AraBERT | Apache-2.0 |
| [Tajawal](https://fonts.google.com/specimen/Tajawal) | Arabic typeface | SIL OFL 1.1 |
| [Heroicons](https://heroicons.com) | Sun and moon icons | MIT |
| [Bootstrap Icons](https://icons.getbootstrap.com) | Flame icon | MIT |

The Arabic word list is curated by hand for this project.

**Inspired by:** [Semantle](https://semantle.com) by David Turner.

This project is an independent implementation. No Semantle code is used; the scoring, API, and user interface are original.