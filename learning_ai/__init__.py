"""learning-ai -- Feedback detection, experience recording, and learning extraction for LLM agents.

Public API
----------
Types:
    ChatMessage, FeedbackSignal, Learning, Experience, StrategyReward

Protocols:
    FeedbackDetector, ExperienceStore, LearningExtractor

Learning:
    SimpleLearningExtractor

Patterns:
    FeedbackPatternMatcher, FeedbackPattern, DEFAULT_PATTERNS

Decorators (ADR-0006):
    detect_feedback, record_experience
"""

from __future__ import annotations

from learning_ai.decorators import detect_feedback, record_experience
from learning_ai.learning import SimpleLearningExtractor
from learning_ai.patterns import DEFAULT_PATTERNS, FeedbackPattern, FeedbackPatternMatcher
from learning_ai.protocols import ExperienceStore, FeedbackDetector, LearningExtractor
from learning_ai.types import (
    ChatMessage,
    Experience,
    FeedbackSignal,
    Learning,
    StrategyReward,
)

__all__ = [
    "ChatMessage",
    "DEFAULT_PATTERNS",
    "Experience",
    "ExperienceStore",
    "FeedbackDetector",
    "FeedbackPattern",
    "FeedbackPatternMatcher",
    "FeedbackSignal",
    "Learning",
    "LearningExtractor",
    "SimpleLearningExtractor",
    "StrategyReward",
    "detect_feedback",
    "record_experience",
]

__version__ = "0.1"
