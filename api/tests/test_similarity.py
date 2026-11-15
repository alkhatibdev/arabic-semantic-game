"""Tests for the similarity scoring service."""

import pytest

from app.services.similarity_service import similarity_service


@pytest.mark.parametrize(
    "word,expected",
    [
        ("كتاب", False),
        ("بحر", False),
        ("book", True),
        ("كتابbook", True),
        ("Kitab", True),
        ("", False),
        ("123", False),
    ],
)
def test_contains_english_chars(word, expected):
    assert similarity_service.contains_english_chars(word) is expected


def test_scale_similarity_endpoints():
    # Cosine -1 floors at 0, +1 tops out at 100.
    assert similarity_service.scale_similarity(-1.0) == pytest.approx(0.0)
    assert similarity_service.scale_similarity(1.0) == pytest.approx(100.0)
    # Orthogonal lands at 25, not 50: the curve is deliberately back-loaded.
    assert similarity_service.scale_similarity(0.0) == pytest.approx(25.0)


def test_scale_similarity_is_monotonic():
    scores = [similarity_service.scale_similarity(c / 10) for c in range(-10, 11)]
    assert scores == sorted(scores)


def test_identical_words_score_100(fake_model):
    score, cos = similarity_service.calculate_similarity("كتاب", "كتاب")
    assert cos == pytest.approx(1.0, abs=1e-6)
    assert score == pytest.approx(100.0, abs=1e-4)


def test_latin_input_short_circuits_without_encoding(fake_model):
    score, cos = similarity_service.calculate_similarity("كتاب", "book")
    assert (score, cos) == (0.0, 0.0)
    # The model must not be consulted for out-of-domain input.
    assert fake_model.encode_calls == []


async def test_calculate_similarity_async_matches_sync(fake_model):
    sync = similarity_service.calculate_similarity("كتاب", "قلم")
    asyn = await similarity_service.calculate_similarity_async("كتاب", "قلم")
    assert sync == asyn
