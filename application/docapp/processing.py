"""The actual work the service does to a document.

Deliberately trivial. This course is about the cloud, not about text analysis, and every
minute a student spends on domain logic is a minute not spent on the thing being assessed.

What matters here is that the work is *slow enough to notice*. ``processing_delay_ms``
simulates work that takes real time — because a service whose handler returns instantly
cannot demonstrate queuing, saturation, or why asynchronous processing exists. The delay is
explicit and bounded rather than hidden, so students always know what they are measuring.
"""

from __future__ import annotations

import hashlib
import re
import time
from typing import Any

from .models import OPERATIONS

_WORD = re.compile(r"[A-Za-z0-9']+")
_SENTENCE = re.compile(r"(?<=[.!?])\s+")


class ProcessingError(RuntimeError):
    """The document could not be processed. The message is shown to the caller."""


def process(operation: str, data: bytes, *, delay_ms: int = 0) -> dict[str, Any]:
    """Run ``operation`` over ``data`` and return a JSON-serialisable result.

    Pure with respect to storage and state: it takes bytes and returns a dict. That is what
    makes it safe to call from a request handler in week 2 and from a queue consumer in
    week 10 without changing a line.
    """
    if operation not in OPERATIONS:
        raise ProcessingError(
            f"Unknown operation {operation!r}. Supported: {', '.join(OPERATIONS)}."
        )

    started = time.monotonic()
    if delay_ms > 0:
        # Simulated work. Sleeping rather than spinning keeps a laptop quiet and keeps the
        # free-tier CPU-seconds bill at zero, while still occupying the request for real
        # wall-clock time -- which is what a queue later relieves.
        time.sleep(delay_ms / 1000.0)

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProcessingError(
            f"Document is not valid UTF-8 text (byte {exc.start}). "
            f"This service only processes text documents."
        ) from exc

    if operation == "wordcount":
        result = _wordcount(text)
    elif operation == "checksum":
        result = _checksum(data)
    else:  # "extract"
        result = _extract(text)

    result["operation"] = operation
    result["duration_ms"] = int((time.monotonic() - started) * 1000)
    return result


def _wordcount(text: str) -> dict[str, Any]:
    words = _WORD.findall(text.lower())
    frequencies: dict[str, int] = {}
    for word in words:
        frequencies[word] = frequencies.get(word, 0) + 1
    top = sorted(frequencies.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    return {
        "words": len(words),
        "unique_words": len(frequencies),
        "characters": len(text),
        "lines": text.count("\n") + (1 if text and not text.endswith("\n") else 0),
        "top_words": [{"word": w, "count": c} for w, c in top],
    }


def _checksum(data: bytes) -> dict[str, Any]:
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def _extract(text: str) -> dict[str, Any]:
    """First few sentences. A stand-in for 'expensive extraction', nothing more.

    No AI API is used here, deliberately: it would add a credential to manage, a cost to
    model, a rate limit to hit, and a dependency on a service the course does not teach.
    """
    stripped = text.strip()
    if not stripped:
        return {"excerpt": "", "sentences_found": 0}
    sentences = [s.strip() for s in _SENTENCE.split(stripped) if s.strip()]
    excerpt = " ".join(sentences[:3])
    return {
        "excerpt": excerpt[:500],
        "sentences_found": len(sentences),
        "truncated": len(excerpt) > 500,
    }
