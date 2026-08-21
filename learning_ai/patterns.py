"""Feedback pattern matching for learning-ai.

Provides ``FeedbackPatternMatcher``, a reusable regex-based pattern
matcher that detects corrections, preferences, and confirmations in
user messages.  Zero external dependencies.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from learning_ai.types import ChatMessage, FeedbackSignal


@dataclass(frozen=True)
class FeedbackPattern:
    """A compiled feedback pattern with type and base confidence."""

    pattern: re.Pattern[str]
    feedback_type: str
    confidence: float


DEFAULT_PATTERNS: list[FeedbackPattern] = [
    # Corrections -- strongest signal
    FeedbackPattern(
        re.compile(r"\byou\s+should\s+have\b", re.IGNORECASE), "correction", 0.9
    ),
    FeedbackPattern(
        re.compile(r"\bthat'?s\s+not\s+(right|correct|what)\b", re.IGNORECASE),
        "correction",
        0.9,
    ),
    FeedbackPattern(
        re.compile(r"\bthat\s+is\s+not\s+(right|correct|what)\b", re.IGNORECASE),
        "correction",
        0.9,
    ),
    FeedbackPattern(
        re.compile(r"\bwhy\s+didn'?t\s+you\b", re.IGNORECASE), "correction", 0.85
    ),
    FeedbackPattern(
        re.compile(r"\bwhy\s+did\s+not\s+you\b", re.IGNORECASE), "correction", 0.85
    ),
    FeedbackPattern(
        re.compile(r"\binstead\s+of\b", re.IGNORECASE), "correction", 0.7
    ),
    # Preferences
    FeedbackPattern(
        re.compile(r"\balways\s+\w+", re.IGNORECASE), "preference", 0.85
    ),
    FeedbackPattern(
        re.compile(r"\bnever\s+\w+", re.IGNORECASE), "preference", 0.85
    ),
    FeedbackPattern(
        re.compile(r"\bdon'?t\s+\w+", re.IGNORECASE), "preference", 0.8
    ),
    FeedbackPattern(
        re.compile(r"\bdo\s+not\s+\w+", re.IGNORECASE), "preference", 0.8
    ),
    FeedbackPattern(
        re.compile(r"\bprefer\s+\w+\s+over\s+\w+", re.IGNORECASE), "preference", 0.9
    ),
    FeedbackPattern(
        re.compile(r"\bprefer\s+\w+", re.IGNORECASE), "preference", 0.8
    ),
    FeedbackPattern(
        re.compile(r"\bavoid\s+\w+", re.IGNORECASE), "preference", 0.75
    ),
    # Confirmations
    FeedbackPattern(
        re.compile(r"\bthat\s+worked\s+well\b", re.IGNORECASE), "confirmation", 0.8
    ),
    FeedbackPattern(
        re.compile(r"\bgood\s+job\b", re.IGNORECASE), "confirmation", 0.7
    ),
    FeedbackPattern(
        re.compile(r"\bperfect\b", re.IGNORECASE), "confirmation", 0.65
    ),
    FeedbackPattern(
        re.compile(r"\bexactly\s+what\s+I\s+wanted\b", re.IGNORECASE),
        "confirmation",
        0.85,
    ),
    FeedbackPattern(
        re.compile(r"\bthat'?s\s+(great|correct|right)\b", re.IGNORECASE),
        "confirmation",
        0.75,
    ),
    FeedbackPattern(
        re.compile(r"\bthat\s+is\s+(great|correct|right)\b", re.IGNORECASE),
        "confirmation",
        0.75,
    ),
]


class FeedbackPatternMatcher:
    """Regex-based feedback signal detector.

    Scans user messages against a configurable set of patterns and emits
    :class:`FeedbackSignal` instances for each match.

    Parameters
    ----------
    patterns:
        List of :class:`FeedbackPattern` to match against.  Defaults to
        :data:`DEFAULT_PATTERNS` which cover corrections, preferences,
        and confirmations.
    """

    def __init__(
        self,
        patterns: list[FeedbackPattern] | None = None,
    ) -> None:
        self._patterns = patterns if patterns is not None else list(DEFAULT_PATTERNS)

    @property
    def patterns(self) -> list[FeedbackPattern]:
        """The currently configured feedback patterns."""
        return list(self._patterns)

    def match(self, messages: list[ChatMessage]) -> list[FeedbackSignal]:
        """Scan *messages* for feedback signals (synchronous).

        Only user messages are inspected.  Each message emits at most one
        signal per feedback type (the first matching pattern wins).
        """
        signals: list[FeedbackSignal] = []
        for msg in messages:
            if msg.role != "user":
                continue
            seen_types: set[str] = set()
            for fp in self._patterns:
                if fp.feedback_type in seen_types:
                    continue
                if fp.pattern.search(msg.content):
                    seen_types.add(fp.feedback_type)
                    signals.append(
                        FeedbackSignal(
                            type=fp.feedback_type,
                            content=msg.content,
                            confidence=fp.confidence,
                            source_message=msg.content,
                        )
                    )
        return signals

    async def match_async(self, messages: list[ChatMessage]) -> list[FeedbackSignal]:
        """Async version of :meth:`match` for protocol compatibility."""
        return self.match(messages)
