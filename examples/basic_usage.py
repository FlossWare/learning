#!/usr/bin/env python3
"""Basic learning-ai usage: feedback detection, experience recording, learning extraction."""
from __future__ import annotations

import asyncio

from learning_ai import (
    ChatMessage,
    FeedbackPatternMatcher,
    SimpleLearningExtractor,
)


async def main():
    # 1. Detect feedback signals
    matcher = FeedbackPatternMatcher()
    messages = [
        ChatMessage(role="user", content="You should have used the fleet for that"),
        ChatMessage(role="assistant", content="I'll use the fleet next time"),
        ChatMessage(role="user", content="Always use multi-model consensus"),
        ChatMessage(role="user", content="That worked well, good job"),
    ]

    signals = matcher.match(messages)
    print("Feedback Detection:")
    for s in signals:
        print(f"  [{s.type}] {s.content} (confidence={s.confidence:.0%})")

    # 2. Record experiences and extract learnings
    extractor = SimpleLearningExtractor()

    exp_id = await extractor.record_experience(
        task="Implement retry logic with exponential backoff",
        outcome="Used jitter to avoid thundering herd. Apply backoff pattern",
    )
    print(f"\nExperience recorded: {exp_id}")

    learnings = await extractor.extract_learnings(exp_id)
    print(f"Learnings extracted: {len(learnings)}")
    for l in learnings:
        print(f"  {l.category}: {l.content}")

    # 3. Strategy reward tracking (Thompson Sampling)
    await extractor.update_strategy("greedy", "success", reward=0.9)
    await extractor.update_strategy("exploratory", "failure", reward=0.2)
    await extractor.update_strategy("greedy", "success", reward=0.8)

    print(f"\nStrategy state:")
    for name, state in extractor.strategies.items():
        print(f"  {name}: alpha={state['alpha']}, beta={state['beta']}, "
              f"trials={state['total_trials']}")


if __name__ == "__main__":
    asyncio.run(main())
