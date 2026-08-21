"""Tests for the learning-ai package."""

from __future__ import annotations

import pytest

from learning_ai import (
    ChatMessage,
    ExperienceStore,
    FeedbackDetector,
    FeedbackPatternMatcher,
    LearningExtractor,
    SimpleLearningExtractor,
)
from learning_ai.types import FeedbackSignal, Learning


# -- Protocol conformance ----------------------------------------------------


def test_satisfies_learning_extractor_protocol():
    """SimpleLearningExtractor satisfies the LearningExtractor protocol."""
    assert isinstance(SimpleLearningExtractor(), LearningExtractor)


def test_satisfies_feedback_detector_protocol():
    """SimpleLearningExtractor satisfies the FeedbackDetector protocol."""
    assert isinstance(SimpleLearningExtractor(), FeedbackDetector)


def test_satisfies_experience_store_protocol():
    """SimpleLearningExtractor satisfies the ExperienceStore protocol."""
    assert isinstance(SimpleLearningExtractor(), ExperienceStore)


# -- detect_feedback ---------------------------------------------------------


async def test_detect_feedback_correction():
    """Detects correction feedback from user messages."""
    extractor = SimpleLearningExtractor()
    messages = [
        ChatMessage(role="user", content="You should have used the fleet"),
    ]
    signals = await extractor.detect_feedback(messages)
    assert len(signals) >= 1
    assert any(s.type == "correction" for s in signals)


async def test_detect_feedback_preference():
    """Detects preference feedback from user messages."""
    extractor = SimpleLearningExtractor()
    messages = [
        ChatMessage(role="user", content="Always use multi-model consensus"),
    ]
    signals = await extractor.detect_feedback(messages)
    assert len(signals) >= 1
    assert any(s.type == "preference" for s in signals)


async def test_detect_feedback_confirmation():
    """Detects confirmation feedback from user messages."""
    extractor = SimpleLearningExtractor()
    messages = [
        ChatMessage(role="user", content="That worked well, good job"),
    ]
    signals = await extractor.detect_feedback(messages)
    assert len(signals) >= 1
    assert any(s.type == "confirmation" for s in signals)


async def test_detect_feedback_ignores_assistant():
    """Only user messages are scanned for feedback."""
    extractor = SimpleLearningExtractor()
    messages = [
        ChatMessage(role="assistant", content="You should have used the fleet"),
    ]
    signals = await extractor.detect_feedback(messages)
    assert len(signals) == 0


async def test_detect_feedback_no_match():
    """No signals emitted when no patterns match."""
    extractor = SimpleLearningExtractor()
    messages = [
        ChatMessage(role="user", content="The weather is nice today"),
    ]
    signals = await extractor.detect_feedback(messages)
    assert len(signals) == 0


async def test_detect_feedback_multiple_messages():
    """Multiple messages with different feedback types."""
    extractor = SimpleLearningExtractor()
    messages = [
        ChatMessage(role="user", content="You should have done X"),
        ChatMessage(role="user", content="Always use Y"),
        ChatMessage(role="user", content="That's great"),
    ]
    signals = await extractor.detect_feedback(messages)
    types = {s.type for s in signals}
    assert "correction" in types
    assert "preference" in types
    assert "confirmation" in types


async def test_detect_feedback_one_per_type_per_message():
    """Each message emits at most one signal per feedback type."""
    extractor = SimpleLearningExtractor()
    messages = [
        ChatMessage(
            role="user",
            content="You should have done X, that's not right, why didn't you do Y"
        ),
    ]
    signals = await extractor.detect_feedback(messages)
    correction_count = sum(1 for s in signals if s.type == "correction")
    assert correction_count == 1


# -- record_experience -------------------------------------------------------


async def test_record_experience_returns_uuid():
    """record_experience returns a valid UUID string."""
    extractor = SimpleLearningExtractor()
    exp_id = await extractor.record_experience(
        task="Test task", outcome="Test outcome"
    )
    assert isinstance(exp_id, str)
    assert len(exp_id) == 36  # UUID format


async def test_record_experience_stores_data():
    """Recorded experiences are accessible via .experiences property."""
    extractor = SimpleLearningExtractor()
    exp_id = await extractor.record_experience(
        task="Task A", outcome="Outcome A", context={"key": "value"}
    )
    assert exp_id in extractor.experiences
    exp = extractor.experiences[exp_id]
    assert exp["task"] == "Task A"
    assert exp["outcome"] == "Outcome A"
    assert exp["context"] == {"key": "value"}


async def test_record_experience_default_context():
    """Context defaults to empty dict when not provided."""
    extractor = SimpleLearningExtractor()
    exp_id = await extractor.record_experience(
        task="Task B", outcome="Outcome B"
    )
    assert extractor.experiences[exp_id]["context"] == {}


async def test_record_experience_multiple():
    """Multiple experiences can be recorded."""
    extractor = SimpleLearningExtractor()
    id1 = await extractor.record_experience(task="T1", outcome="O1")
    id2 = await extractor.record_experience(task="T2", outcome="O2")
    assert id1 != id2
    assert len(extractor.experiences) == 2


# -- extract_learnings -------------------------------------------------------


async def test_extract_learnings_key_phrases():
    """Key phrases are extracted from task and outcome text."""
    extractor = SimpleLearningExtractor()
    exp_id = await extractor.record_experience(
        task="Implement retry logic with backoff",
        outcome="Apply exponential backoff. Use jitter to spread load",
    )
    learnings = await extractor.extract_learnings(exp_id)
    assert len(learnings) >= 1
    assert all(isinstance(l, Learning) for l in learnings)
    assert all(l.source_experience == exp_id for l in learnings)


async def test_extract_learnings_summary_fallback():
    """When no key phrases found, a summary learning is generated."""
    extractor = SimpleLearningExtractor()
    exp_id = await extractor.record_experience(
        task="Simple thing", outcome="Done"
    )
    learnings = await extractor.extract_learnings(exp_id)
    assert len(learnings) >= 1
    assert any(l.category == "summary" for l in learnings)


async def test_extract_learnings_nonexistent():
    """extract_learnings returns empty list for unknown experience_id."""
    extractor = SimpleLearningExtractor()
    learnings = await extractor.extract_learnings("nonexistent-id")
    assert learnings == []


async def test_extract_learnings_deduplicates():
    """Duplicate key phrases are de-duplicated."""
    extractor = SimpleLearningExtractor()
    exp_id = await extractor.record_experience(
        task="Use retry logic. Use retry logic again",
        outcome="Applied retry logic",
    )
    learnings = await extractor.extract_learnings(exp_id)
    contents = [l.content.lower() for l in learnings]
    # No exact duplicates
    assert len(contents) == len(set(contents))


# -- update_strategy ---------------------------------------------------------


async def test_update_strategy_success():
    """Reward >= 0.5 increments alpha."""
    extractor = SimpleLearningExtractor()
    await extractor.update_strategy("greedy", "ok", reward=0.9)

    state = extractor.strategies["greedy"]
    assert state["alpha"] == 2.0  # 1.0 (prior) + 1.0
    assert state["beta"] == 1.0   # unchanged
    assert state["total_trials"] == 1


async def test_update_strategy_failure():
    """Reward < 0.5 increments beta."""
    extractor = SimpleLearningExtractor()
    await extractor.update_strategy("greedy", "bad", reward=0.2)

    state = extractor.strategies["greedy"]
    assert state["alpha"] == 1.0  # unchanged
    assert state["beta"] == 2.0   # 1.0 (prior) + 1.0
    assert state["total_trials"] == 1


async def test_update_strategy_boundary():
    """Reward exactly 0.5 is treated as success (>= 0.5)."""
    extractor = SimpleLearningExtractor()
    await extractor.update_strategy("edge", "ok", reward=0.5)

    state = extractor.strategies["edge"]
    assert state["alpha"] == 2.0  # success
    assert state["beta"] == 1.0


async def test_update_strategy_multiple():
    """Multiple strategies maintain independent state."""
    extractor = SimpleLearningExtractor()
    await extractor.update_strategy("a", "ok", reward=1.0)
    await extractor.update_strategy("b", "bad", reward=0.0)

    assert extractor.strategies["a"]["alpha"] == 2.0
    assert extractor.strategies["b"]["beta"] == 2.0


async def test_update_strategy_accumulates():
    """Multiple updates accumulate correctly."""
    extractor = SimpleLearningExtractor()
    await extractor.update_strategy("s1", "ok", reward=1.0)
    await extractor.update_strategy("s1", "bad", reward=0.0)
    await extractor.update_strategy("s1", "ok", reward=0.8)

    state = extractor.strategies["s1"]
    assert state["total_trials"] == 3
    assert state["alpha"] == 3.0  # 1.0 + 2 successes
    assert state["beta"] == 2.0   # 1.0 + 1 failure
    assert abs(state["total_reward"] - 1.8) < 1e-9


# -- FeedbackPatternMatcher --------------------------------------------------


def test_matcher_default_patterns():
    """Default patterns detect all three feedback types."""
    matcher = FeedbackPatternMatcher()
    assert len(matcher.patterns) > 0


def test_matcher_match_correction():
    """Matcher detects correction patterns."""
    matcher = FeedbackPatternMatcher()
    signals = matcher.match([
        ChatMessage(role="user", content="That's not correct"),
    ])
    assert any(s.type == "correction" for s in signals)


def test_matcher_match_preference():
    """Matcher detects preference patterns."""
    matcher = FeedbackPatternMatcher()
    signals = matcher.match([
        ChatMessage(role="user", content="Never use that approach"),
    ])
    assert any(s.type == "preference" for s in signals)


def test_matcher_match_confirmation():
    """Matcher detects confirmation patterns."""
    matcher = FeedbackPatternMatcher()
    signals = matcher.match([
        ChatMessage(role="user", content="Exactly what I wanted"),
    ])
    assert any(s.type == "confirmation" for s in signals)


def test_matcher_custom_patterns():
    """Matcher accepts custom patterns."""
    import re

    from learning_ai.patterns import FeedbackPattern

    custom = [
        FeedbackPattern(
            re.compile(r"\bcustom\b", re.IGNORECASE), "custom_type", 0.95
        ),
    ]
    matcher = FeedbackPatternMatcher(patterns=custom)
    signals = matcher.match([
        ChatMessage(role="user", content="This is a custom pattern"),
    ])
    assert len(signals) == 1
    assert signals[0].type == "custom_type"
    assert signals[0].confidence == 0.95


async def test_matcher_async_version():
    """Async match_async returns same results as sync match."""
    matcher = FeedbackPatternMatcher()
    messages = [
        ChatMessage(role="user", content="Always do X"),
    ]
    sync_result = matcher.match(messages)
    async_result = await matcher.match_async(messages)
    assert len(sync_result) == len(async_result)
    assert sync_result[0].type == async_result[0].type


def test_matcher_empty_messages():
    """Empty message list returns no signals."""
    matcher = FeedbackPatternMatcher()
    assert matcher.match([]) == []


def test_matcher_prefer_over():
    """'prefer X over Y' pattern is detected."""
    matcher = FeedbackPatternMatcher()
    signals = matcher.match([
        ChatMessage(role="user", content="I prefer Python over JavaScript"),
    ])
    assert any(s.type == "preference" for s in signals)


# -- Decorators ---------------------------------------------------------------


async def test_detect_feedback_decorator():
    """@detect_feedback decorator attaches signals to result."""
    from learning_ai import detect_feedback

    extractor = SimpleLearningExtractor()

    class Result:
        pass

    @detect_feedback(extractor=extractor)
    async def handler(messages):
        return Result()

    messages = [
        ChatMessage(role="user", content="You should have done X"),
    ]
    result = await handler(messages=messages)
    assert hasattr(result, "_feedback_signals")
    assert len(result._feedback_signals) >= 1


async def test_detect_feedback_decorator_no_feedback():
    """@detect_feedback decorator works when no feedback detected."""
    from learning_ai import detect_feedback

    @detect_feedback()
    async def handler(messages):
        return "result"

    messages = [
        ChatMessage(role="user", content="Hello world"),
    ]
    result = await handler(messages=messages)
    assert result == "result"


async def test_record_experience_decorator():
    """@record_experience decorator records and extracts learnings."""
    from learning_ai import record_experience

    extractor = SimpleLearningExtractor()

    class Result:
        pass

    @record_experience(extractor=extractor)
    async def process(task="test task"):
        return Result()

    result = await process(task="Implement retry with backoff")
    assert hasattr(result, "_experience_id")
    assert hasattr(result, "_learnings")
    assert len(extractor.experiences) == 1


async def test_record_experience_decorator_primitive_result():
    """@record_experience handles primitive return values gracefully."""
    from learning_ai import record_experience

    extractor = SimpleLearningExtractor()

    @record_experience(extractor=extractor)
    async def process(task="test"):
        return 42

    result = await process(task="Simple task")
    assert result == 42
    assert len(extractor.experiences) == 1


# -- __init__ exports --------------------------------------------------------


def test_version():
    """Package version is set."""
    import learning_ai

    assert learning_ai.__version__ == "0.1"


def test_all_exports():
    """__all__ lists all public symbols."""
    import learning_ai

    assert len(learning_ai.__all__) == 14
    for name in learning_ai.__all__:
        assert hasattr(learning_ai, name), f"Missing export: {name}"
