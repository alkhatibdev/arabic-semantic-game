"""Tests for the word-list loader in scripts/init_daily_words.py."""

import json
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.init_daily_words import load_challenges  # noqa: E402

START = date(2026, 1, 1)


def write(tmp_path, payload):
    p = tmp_path / "words.json"
    p.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return p


def test_plain_string_list_gets_consecutive_dates(tmp_path):
    path = write(tmp_path, ["كتاب", "بحر", "قمر"])
    out = load_challenges(path, START, shuffle=False)

    assert [c["word"] for c in out] == ["كتاب", "بحر", "قمر"]
    assert [c["date"] for c in out] == [date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3)]
    assert all(c["hints"] == [] for c in out)


def test_words_key_is_unwrapped(tmp_path):
    path = write(tmp_path, {"_comment": "ignored", "words": ["كتاب"]})
    assert load_challenges(path, START, shuffle=False)[0]["word"] == "كتاب"


def test_explicit_dates_are_respected(tmp_path):
    path = write(tmp_path, [{"word": "كتاب", "date": "2026-03-05"}])
    assert load_challenges(path, START, shuffle=False)[0]["date"] == date(2026, 3, 5)


def test_hints_are_loaded_and_blanks_dropped(tmp_path):
    path = write(tmp_path, {"words": [{"word": "بحر", "hints": ["مالح", "  ", ""]}]})
    assert load_challenges(path, START, shuffle=False)[0]["hints"] == ["مالح"]


def test_objects_without_a_date_fall_back_to_start_date(tmp_path):
    path = write(tmp_path, {"words": [{"word": "كتاب"}, {"word": "بحر"}]})
    out = load_challenges(path, START, shuffle=False)
    assert [c["date"] for c in out] == [date(2026, 1, 1), date(2026, 1, 2)]


def test_missing_file_exits_cleanly(tmp_path):
    with pytest.raises(SystemExit):
        load_challenges(tmp_path / "nope.json", START, shuffle=False)


def test_empty_list_exits_cleanly(tmp_path):
    with pytest.raises(SystemExit):
        load_challenges(write(tmp_path, []), START, shuffle=False)


def test_shipped_sample_file_is_loadable():
    """The sample must stay playable - it is the quickstart path."""
    out = load_challenges(Path("data/words.sample.json"), START, shuffle=False)
    assert len(out) == 10
    assert all(c["word"] and c["hints"] for c in out)
    # dates must be distinct, or seeding silently skips most of them
    assert len({c["date"] for c in out}) == 10
