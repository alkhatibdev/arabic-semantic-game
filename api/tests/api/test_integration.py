"""
End-to-end API tests against a real PostgreSQL database.

Skipped unless RUN_INTEGRATION_TESTS=1 and DATABASE_URL points at a database
you are happy to have migrated and written to. CI provides both; locally:

    docker run -d --name pg -e POSTGRES_PASSWORD=postgres -p 55432:5432 postgres:16-alpine
    RUN_INTEGRATION_TESTS=1 \
    DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:55432/postgres \
    pytest tests/api

The embedding model is replaced with a deterministic fake, so these run in
seconds and need no model download.
"""

import os
import uuid
from datetime import date, timedelta

import httpx
import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="set RUN_INTEGRATION_TESTS=1 and DATABASE_URL to run",
)

TODAY = date.today()
WORD_TODAY = "باب"


@pytest.fixture(scope="module")
def seeded_db(fake_model_module):
    """Rebuild the schema from scratch and seed ten past days ending today."""
    import asyncio
    import pathlib

    import sqlalchemy as sa

    from alembic import command
    from alembic.config import Config
    from app.core.config import settings
    from scripts.init_daily_words import load_challenges, seed

    # Drop the schema outright rather than `alembic downgrade base`: one of the
    # existing downgrades re-creates a unique constraint on word_hints that
    # seeded data can violate, so a downgrade is not a reliable reset.
    sync_url = settings.DATABASE_URL.replace("+asyncpg", "")
    engine = sa.create_engine(sync_url)
    with engine.begin() as conn:
        conn.execute(sa.text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
    engine.dispose()

    command.upgrade(Config("alembic.ini"), "head")

    challenges = load_challenges(
        pathlib.Path("data/words.sample.json"),
        TODAY - timedelta(days=9),
        shuffle=False,
    )

    async def _seed() -> None:
        from app.db.session import engine as app_engine

        await seed(challenges, dry_run=False)
        # The pooled connections are bound to this throwaway loop; leaving them
        # in the pool makes the first real test fail with a cross-loop error.
        await app_engine.dispose()

    asyncio.run(_seed())
    return challenges


@pytest.fixture(autouse=True)
async def _fresh_pool():
    """
    Drop pooled connections between tests.

    app/db/session.py builds one global engine at import, pytest-asyncio gives
    each test its own event loop, and an asyncpg connection cannot be reused
    across loops.
    """
    yield
    from app.db.session import engine

    await engine.dispose()


@pytest.fixture
async def client(seeded_db):
    from app.main import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def player():
    return str(uuid.uuid4())


async def test_today_challenge_is_available(client):
    r = await client.get("/api/v1/challenges/today")
    assert r.status_code == 200
    assert r.json()["has_challenge"] is True
    assert r.json()["game_number"] == 10


async def test_future_challenge_is_refused(client):
    assert (await client.get("/api/v1/challenges/2099-01-01")).status_code == 403


async def test_malformed_date_is_rejected(client):
    assert (await client.get("/api/v1/challenges/not-a-date")).status_code == 400


async def test_new_player_state(client, player):
    r = await client.get(f"/api/v1/game/{TODAY}/state/{player}")
    assert r.status_code == 200
    body = r.json()
    assert body["max_hints"] == 3
    assert body["hints"] == []
    # The answer must not leak before the player has won or given up.
    assert body["game_status"]["target_word"] is None


async def test_guess_is_scored_and_idempotent(client, player):
    payload = {"user_id": player, "challenge_date": TODAY.isoformat(), "word": "شجرة"}

    first = await client.post("/api/v1/game/guess", json=payload)
    assert first.status_code == 200
    assert first.json()["is_given_up"] is False
    assert first.json()["is_correct"] is False

    # Guessing the same word again must not create a second attempt.
    second = await client.post("/api/v1/game/guess", json=payload)
    assert second.json()["id"] == first.json()["id"]

    status = await client.get(f"/api/v1/game/{TODAY}/status/{player}")
    assert status.json()["attempts"] == 1


async def test_latin_input_scores_zero(client, player):
    r = await client.post(
        "/api/v1/game/guess",
        json={"user_id": player, "challenge_date": TODAY.isoformat(), "word": "hello"},
    )
    assert r.json()["similarity_score"] == 0.0


async def test_empty_guess_is_rejected(client, player):
    r = await client.post(
        "/api/v1/game/guess",
        json={"user_id": player, "challenge_date": TODAY.isoformat(), "word": "   "},
    )
    assert r.status_code == 400


async def test_oversized_guess_is_rejected(client, player):
    """
    A guess longer than MAX_GUESS_LENGTH must be refused by validation.

    `word` was an unbounded string, so a multi-megabyte value reached the
    embedding model and the database. guessed_word is also part of a btree
    unique index, which Postgres caps at ~2704 bytes per entry, so a long
    incompressible guess raised an unhandled database error rather than a 4xx.
    """
    from app.core.config import MAX_GUESS_LENGTH

    r = await client.post(
        "/api/v1/game/guess",
        json={
            "user_id": player,
            "challenge_date": TODAY.isoformat(),
            "word": "ك" * (MAX_GUESS_LENGTH + 1),
        },
    )
    assert r.status_code == 422

    # A word at the limit is still perfectly playable.
    ok = await client.post(
        "/api/v1/game/guess",
        json={
            "user_id": player,
            "challenge_date": TODAY.isoformat(),
            "word": "ك" * MAX_GUESS_LENGTH,
        },
    )
    assert ok.status_code == 200


async def test_hint_allowance_is_enforced(client, player):
    for _ in range(3):
        r = await client.post(f"/api/v1/game/{TODAY}/hints/{player}")
        assert r.status_code == 200
        assert r.json()["hint_text"]

    assert (await client.post(f"/api/v1/game/{TODAY}/hints/{player}")).status_code == 403

    revealed = await client.get(f"/api/v1/game/{TODAY}/hints/{player}")
    assert len(revealed.json()) == 3


async def test_hints_are_per_player(client, player):
    await client.post(f"/api/v1/game/{TODAY}/hints/{player}")
    other = str(uuid.uuid4())
    assert (await client.get(f"/api/v1/game/{TODAY}/hints/{other}")).json() == []


async def test_giveup_is_distinguishable_from_a_win(client, player):
    r = await client.post(
        "/api/v1/game/giveup",
        json={"user_id": player, "challenge_date": TODAY.isoformat()},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["is_correct"] is True
    # The flag the frontend needs to render "you gave up" rather than "you won".
    assert body["is_given_up"] is True
    assert body["word"] == WORD_TODAY

    state = await client.get(f"/api/v1/game/{TODAY}/state/{player}")
    assert state.json()["game_status"]["target_word"] == WORD_TODAY


async def test_attempt_numbers_are_chronological(client, player):
    for word in ("شجرة", "قمر", "بحر"):
        await client.post(
            "/api/v1/game/guess",
            json={"user_id": player, "challenge_date": TODAY.isoformat(), "word": word},
        )

    r = await client.get(f"/api/v1/game/{TODAY}/guesses/{player}")
    numbers = [g["attempt_number"] for g in r.json()]
    assert numbers == list(range(1, len(numbers) + 1))


async def test_status_for_unseeded_date_is_404(client, player):
    assert (await client.get(f"/api/v1/game/1999-01-01/status/{player}")).status_code == 404


async def test_hints_are_numbered_sequentially(client, player):
    """
    Every hint for a word needs a distinct 1-based order.

    They were all created with hint_order=0, which collapsed the UI's 1⃣2⃣3⃣
    numbering to a generic icon and gave the hint list duplicate React keys.
    """
    for _ in range(3):
        await client.post(f"/api/v1/game/{TODAY}/hints/{player}")

    revealed = await client.get(f"/api/v1/game/{TODAY}/hints/{player}")
    orders = sorted(h["hint_order"] for h in revealed.json())
    assert orders == [1, 2, 3]
