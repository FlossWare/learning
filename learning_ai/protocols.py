"""Protocol definitions for learning-ai.

Defines the structural interfaces that any backend must satisfy in order
to be used with the learning extraction components.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from learning_ai.types import ChatMessage, Experience, FeedbackSignal, Learning


@runtime_checkable
class FeedbackDetector(Protocol):
    """Protocol for detecting feedback signals in conversations."""

    async def detect_feedback(
        self, messages: list[ChatMessage]
    ) -> list[FeedbackSignal]:
        """Scan *messages* for implicit or explicit feedback signals."""
        ...


@runtime_checkable
class ExperienceStore(Protocol):
    """Protocol for recording and retrieving task experiences."""

    async def record_experience(
        self,
        task: str,
        outcome: str,
        *,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Persist a task/outcome pair and return its id."""
        ...

    async def extract_learnings(self, experience_id: str) -> list[Learning]:
        """Derive actionable learnings from a stored experience."""
        ...


@runtime_checkable
class LearningExtractor(Protocol):
    """Combined protocol for feedback detection, experience recording,
    and strategy reward tracking."""

    async def detect_feedback(
        self, messages: list[ChatMessage]
    ) -> list[FeedbackSignal]:
        """Scan *messages* for implicit or explicit feedback signals."""
        ...

    async def record_experience(
        self,
        task: str,
        outcome: str,
        *,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Persist a task/outcome pair and return its id."""
        ...

    async def extract_learnings(self, experience_id: str) -> list[Learning]:
        """Derive actionable learnings from a stored experience."""
        ...

    async def update_strategy(
        self, strategy: str, outcome: str, *, reward: float
    ) -> None:
        """Record a reward observation for bandit-based strategy state."""
        ...
