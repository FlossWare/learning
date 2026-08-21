"""Shared data types for the learning-ai package.

All types are plain ``dataclasses`` with no external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ChatMessage:
    """A single chat message exchanged with a language model."""

    role: str
    content: str


@dataclass
class FeedbackSignal:
    """A detected feedback signal extracted from conversation messages."""

    type: str
    content: str
    confidence: float
    source_message: str


@dataclass
class Learning:
    """A single actionable insight extracted from an experience."""

    id: str
    content: str
    category: str
    source_experience: str
    created_at: str = ""


@dataclass
class Experience:
    """A recorded task/outcome pair with optional context."""

    id: str
    task: str
    outcome: str
    context: dict = field(default_factory=dict)
    created_at: str = ""


@dataclass
class StrategyReward:
    """A reward observation for bandit-based strategy tracking."""

    strategy: str
    outcome: str
    reward: float
