"""In-memory learning extractor for learning-ai.

Implements the :class:`~learning_ai.protocols.LearningExtractor`
protocol via structural subtyping.  All state is held in plain dicts
and lists -- no external dependencies.

Classes
-------
SimpleLearningExtractor -- pattern-based feedback detection, in-memory
    experience recording, key-phrase learning extraction, and strategy
    reward tracking for Thompson Sampling bandits.
"""

from __future__ import annotations

import asyncio
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from learning_ai.patterns import FeedbackPatternMatcher
from learning_ai.types import ChatMessage, FeedbackSignal, Learning

_KEY_PHRASE_RE = re.compile(
    r"\b(use|apply|avoid|prefer|try|implement|fix|handle|check|test|run|ensure)\s+"
    r"([\w\s]{2,30}?)(?:\.|,|;|$)",
    re.IGNORECASE,
)


def _extract_key_phrases(text: str) -> list[str]:
    """Return de-duplicated key phrases from *text*."""
    seen: set[str] = set()
    phrases: list[str] = []
    for match in _KEY_PHRASE_RE.finditer(text):
        phrase = match.group(0).strip().rstrip(".,;")
        lower = phrase.lower()
        if lower not in seen:
            seen.add(lower)
            phrases.append(phrase)
    return phrases


class SimpleLearningExtractor:
    """In-memory learning extractor with feedback detection and experience recording.

    Satisfies :class:`~learning_ai.protocols.LearningExtractor` via
    structural subtyping -- no inheritance required.

    Stores experiences, feedback signals, and strategy rewards in plain
    Python data structures.  Suitable for testing and single-process
    deployments.
    """

    def __init__(self) -> None:
        self._matcher = FeedbackPatternMatcher()
        self._experiences: dict[str, dict[str, Any]] = {}
        self._strategies: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def detect_feedback(
        self, messages: list[ChatMessage]
    ) -> list[FeedbackSignal]:
        """Scan *messages* for implicit or explicit feedback signals.

        Only user messages are inspected.  Each message is tested against
        every compiled pattern; the first match per (message, type) pair
        is emitted.
        """
        return self._matcher.match(messages)

    async def record_experience(
        self,
        task: str,
        outcome: str,
        *,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Persist a task/outcome pair and return its UUID."""
        experience_id = str(uuid.uuid4())
        async with self._lock:
            self._experiences[experience_id] = {
                "task": task,
                "outcome": outcome,
                "context": context or {},
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        return experience_id

    async def extract_learnings(self, experience_id: str) -> list[Learning]:
        """Derive actionable learnings from a stored experience.

        Key phrases are extracted from both the task description and the
        outcome text.  Each phrase becomes a separate :class:`Learning`.
        """
        experience = self._experiences.get(experience_id)
        if experience is None:
            return []

        combined = f"{experience['task']}. {experience['outcome']}"
        phrases = _extract_key_phrases(combined)

        learnings: list[Learning] = []
        now = datetime.now(timezone.utc).isoformat()
        for phrase in phrases:
            learnings.append(
                Learning(
                    id=str(uuid.uuid4()),
                    content=phrase,
                    category="key_phrase",
                    source_experience=experience_id,
                    created_at=now,
                )
            )

        if not learnings:
            learnings.append(
                Learning(
                    id=str(uuid.uuid4()),
                    content=f"Task: {experience['task']} -> {experience['outcome']}",
                    category="summary",
                    source_experience=experience_id,
                    created_at=now,
                )
            )

        return learnings

    async def update_strategy(
        self, strategy: str, outcome: str, *, reward: float
    ) -> None:
        """Record a reward observation for Thompson Sampling bandit state.

        Maintains cumulative trial count and total reward, plus Beta
        distribution parameters (alpha/beta) updated as:
        - success (reward >= 0.5): alpha += 1
        - failure (reward < 0.5):  beta  += 1
        """
        _ = outcome
        async with self._lock:
            state = self._strategies.setdefault(
                strategy,
                {"total_trials": 0, "total_reward": 0.0, "alpha": 1.0, "beta": 1.0},
            )
            state["total_trials"] += 1
            state["total_reward"] += reward
            if reward >= 0.5:
                state["alpha"] += 1.0
            else:
                state["beta"] += 1.0

    @property
    def experiences(self) -> dict[str, dict[str, Any]]:
        """All recorded experiences (read-only copy)."""
        return dict(self._experiences)

    @property
    def strategies(self) -> dict[str, dict[str, Any]]:
        """All strategy bandit states (read-only copy)."""
        return dict(self._strategies)
