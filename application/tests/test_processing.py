"""The domain logic. Small, but wrong answers here would be invisible in every lab."""

from __future__ import annotations

import hashlib

import pytest

from docapp.processing import ProcessingError, process

TEXT = b"One two two three three three.\nFour four four four!\n"


def test_wordcount_counts_and_ranks():
    result = process("wordcount", TEXT)
    assert result["words"] == 10
    assert result["unique_words"] == 4
    assert result["top_words"][0] == {"word": "four", "count": 4}


def test_checksum_matches_hashlib():
    result = process("checksum", TEXT)
    assert result["sha256"] == hashlib.sha256(TEXT).hexdigest()
    assert result["bytes"] == len(TEXT)


def test_extract_returns_leading_sentences():
    result = process("extract", b"First one. Second one. Third one. Fourth one.")
    assert result["sentences_found"] == 4
    assert result["excerpt"].startswith("First one.")
    assert "Fourth" not in result["excerpt"]


def test_unknown_operation_is_rejected_by_name():
    with pytest.raises(ProcessingError) as exc:
        process("transmogrify", TEXT)
    assert "transmogrify" in str(exc.value)


def test_non_utf8_input_fails_with_a_useful_message():
    with pytest.raises(ProcessingError) as exc:
        process("wordcount", b"\xff\xfe\x00binary")
    assert "UTF-8" in str(exc.value)


def test_delay_is_actually_observed():
    """The simulated delay must be real, or Labs 4 and 5 measure nothing."""
    result = process("checksum", TEXT, delay_ms=60)
    assert result["duration_ms"] >= 55  # allow for clock granularity
