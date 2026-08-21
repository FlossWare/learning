"""Convenience decorators for learning-ai (ADR-0006).

Provides ``@detect_feedback`` and ``@record_experience`` decorators
that wrap async functions with cross-cutting learning extraction
concerns.  Both are explicit opt-in (ADR-0001) -- nothing activates
unless a developer deliberately applies a decorator.

Zero external dependencies -- uses only the standard library.
"""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable, TypeVar

from learning_ai.learning import SimpleLearningExtractor
from learning_ai.patterns import FeedbackPatternMatcher
from learning_ai.types import ChatMessage

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def detect_feedback(
    *,
    extractor: SimpleLearningExtractor | None = None,
    matcher: FeedbackPatternMatcher | None = None,
    messages_arg: str = "messages",
    on_feedback: str = "log",
) -> Callable[[F], F]:
    """Decorator that wraps an async conversation handler to auto-detect feedback.

    The decorated function must accept a *messages* keyword argument
    (or a positional argument named per *messages_arg*) containing a
    ``list[ChatMessage]``.

    Parameters
    ----------
    extractor:
        A :class:`SimpleLearningExtractor` instance.  When provided,
        detected signals are stored via the extractor.  When ``None``,
        a :class:`FeedbackPatternMatcher` is used for detection only.
    matcher:
        A :class:`FeedbackPatternMatcher` for pattern matching.  When
        ``None`` and no *extractor* is provided, defaults to a new
        matcher with default patterns.
    messages_arg:
        Name of the keyword argument containing the message list
        (default ``"messages"``).
    on_feedback:
        Action when feedback is detected:
        ``"log"`` (default) -- log the feedback signals;
        ``"raise"`` -- raise ``RuntimeError``.

    Returns
    -------
    The original function's return value.  A ``_feedback_signals``
    attribute is attached when possible.
    """
    active_matcher = matcher or (
        extractor._matcher if extractor else FeedbackPatternMatcher()
    )

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            messages: list[ChatMessage] | None = kwargs.get(messages_arg)
            if messages is None:
                import inspect

                sig = inspect.signature(fn)
                params = list(sig.parameters.keys())
                if messages_arg in params:
                    idx = params.index(messages_arg)
                    if idx < len(args):
                        messages = args[idx]

            signals = []
            if messages:
                signals = active_matcher.match(messages)
                if signals:
                    summary = "; ".join(
                        f"{s.type}({s.confidence:.0%})" for s in signals
                    )
                    msg = f"Feedback detected in {fn.__name__!r}: {summary}"
                    if on_feedback == "raise":
                        raise RuntimeError(msg)
                    logger.info(msg)

            result = await fn(*args, **kwargs)

            try:
                result._feedback_signals = signals  # type: ignore[union-attr]
            except (AttributeError, TypeError):
                pass

            return result

        return wrapper  # type: ignore[return-value]

    return decorator


def record_experience(
    *,
    extractor: SimpleLearningExtractor,
    task_arg: str = "task",
    extract_learnings: bool = True,
    on_error: str = "log",
) -> Callable[[F], F]:
    """Decorator that wraps an async task execution to auto-record outcomes.

    The decorated function's return value (converted to ``str``) is
    recorded as the outcome of the task.

    Parameters
    ----------
    extractor:
        A :class:`SimpleLearningExtractor` instance for recording.
    task_arg:
        Name of the keyword argument containing the task description
        (default ``"task"``).  If not found, the function name is used.
    extract_learnings:
        Whether to extract learnings from the recorded experience
        (default ``True``).
    on_error:
        Action when recording fails:
        ``"log"`` (default) -- log the error;
        ``"raise"`` -- re-raise the exception.

    Returns
    -------
    The original function's return value.  ``_experience_id`` and
    ``_learnings`` attributes are attached when possible.
    """

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            task_desc = kwargs.get(task_arg, fn.__name__)

            result = await fn(*args, **kwargs)

            try:
                experience_id = await extractor.record_experience(
                    task=str(task_desc),
                    outcome=str(result),
                )

                learnings = []
                if extract_learnings:
                    learnings = await extractor.extract_learnings(experience_id)

                try:
                    result._experience_id = experience_id  # type: ignore[union-attr]
                    result._learnings = learnings  # type: ignore[union-attr]
                except (AttributeError, TypeError):
                    pass

            except Exception as exc:
                if on_error == "raise":
                    raise
                logger.warning(
                    "Failed to record experience for %r: %s", fn.__name__, exc
                )

            return result

        return wrapper  # type: ignore[return-value]

    return decorator
