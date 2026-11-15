"""
Seed the daily_words table from a word list.

The word list is deliberately NOT hardcoded here. A public repo that contains the
answer for every upcoming date is a spoiler for the whole game, so the list is
loaded from a JSON file chosen by --file / WORD_SEED_FILE. The sample file that
ships with the repo exists only so a fresh clone is playable.

Accepted file shapes:

    {"words": ["كتاب", "بحر"]}                              # dated from --start-date
    ["كتاب", "بحر"]                                          # same
    [{"word": "كتاب", "date": "2026-11-15"}]                 # explicit dates
    [{"word": "كتاب", "hints": ["يُقرأ", "له صفحات"]}]        # optional hints

Usage:
    python scripts/init_daily_words.py
    python scripts/init_daily_words.py --file data/my-words.json --start-date 2026-12-01
    python scripts/init_daily_words.py --dry-run
"""

import argparse
import asyncio
import json
import logging
import random
import sys
from datetime import date as date_type
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings  # noqa: E402
from app.core.logging import configure_logging  # noqa: E402
from app.crud.daily_word import daily_word as crud_daily_word  # noqa: E402
from app.db.session import AsyncSessionLocal  # noqa: E402
from app.schemas.word_hint import WordHintsRequest  # noqa: E402
from app.services.hint_service import hint_service  # noqa: E402

logger = logging.getLogger("seed")


def load_challenges(path: Path, start_date: date_type, shuffle: bool) -> list[dict]:
    """Read a word-list file and return [{"word", "date", "hints"}, ...]."""
    if not path.exists():
        raise SystemExit(f"Word list not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    entries = raw.get("words", []) if isinstance(raw, dict) else raw

    if not entries:
        raise SystemExit(f"No words found in {path}")

    # Object shape: each entry may carry an explicit date and/or hints.
    if isinstance(entries[0], dict):
        objects = [e for e in entries if str(e.get("word", "")).strip()]
        if shuffle:
            random.shuffle(objects)
        return [
            {
                "word": e["word"].strip(),
                "date": (
                    date_type.fromisoformat(e["date"])
                    if e.get("date")
                    else start_date + timedelta(days=offset)
                ),
                "hints": [h.strip() for h in e.get("hints", []) if h.strip()],
            }
            for offset, e in enumerate(objects)
        ]

    # Plain string list: assign consecutive dates from start_date.
    words = [w.strip() for w in entries if isinstance(w, str) and w.strip()]
    if shuffle:
        random.shuffle(words)

    return [
        {"word": word, "date": start_date + timedelta(days=offset), "hints": []}
        for offset, word in enumerate(words)
    ]


async def seed(challenges: list[dict], dry_run: bool) -> None:
    """Insert each challenge, skipping dates that already have a word."""
    created = skipped = hinted = 0

    async with AsyncSessionLocal() as db:
        try:
            for challenge in challenges:
                existing = await crud_daily_word.get_by_date(db, challenge["date"])
                if existing:
                    logger.debug("%s already seeded, skipping", challenge["date"])
                    skipped += 1
                    continue

                if not dry_run:
                    await crud_daily_word.create_daily_word(
                        db=db, word=challenge["word"], challenge_date=challenge["date"]
                    )
                created += 1

                if challenge["hints"]:
                    if not dry_run:
                        await hint_service.set_hints(
                            db=db,
                            request=WordHintsRequest(
                                word=challenge["word"], hints=challenge["hints"]
                            ),
                        )
                    hinted += 1

            if dry_run:
                await db.rollback()
                logger.info(
                    "Dry run: would create %d word(s) (%d with hints), skip %d",
                    created,
                    hinted,
                    skipped,
                )
            else:
                await db.commit()
                logger.info(
                    "Created %d daily word(s) (%d with hints), skipped %d",
                    created,
                    hinted,
                    skipped,
                )
        except Exception:
            await db.rollback()
            logger.exception("Seeding failed, rolled back")
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file",
        default=settings.WORD_SEED_FILE,
        help="JSON word list (default: WORD_SEED_FILE setting)",
    )
    parser.add_argument(
        "--start-date",
        default=date_type.today().isoformat(),
        help="First challenge date for undated lists (default: today)",
    )
    parser.add_argument(
        "--shuffle",
        action="store_true",
        help="Shuffle an undated list before assigning dates",
    )
    parser.add_argument("--dry-run", action="store_true", help="Report without writing")
    args = parser.parse_args()

    configure_logging()

    challenges = load_challenges(
        Path(args.file),
        date_type.fromisoformat(args.start_date),
        args.shuffle,
    )
    logger.info("Loaded %d word(s) from %s", len(challenges), args.file)
    asyncio.run(seed(challenges, args.dry_run))


if __name__ == "__main__":
    main()
