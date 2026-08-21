# learning-ai

Feedback detection, experience recording, key-phrase extraction, and strategy reward tracking for LLM agents.

Part of the [FlossWare](https://github.com/FlossWare) AI component ecosystem.

## Features

- **Feedback Detection** -- regex-based pattern matching for corrections, preferences, and confirmations in user messages
- **Experience Recording** -- in-memory task/outcome persistence with UUID tracking
- **Learning Extraction** -- key-phrase extraction from experiences for actionable insights
- **Strategy Rewards** -- Thompson Sampling bandit state tracking (alpha/beta) for model selection
- **Decorators** -- `@detect_feedback` and `@record_experience` for cross-cutting concerns
- **Zero Dependencies** -- stdlib only, no external packages required
- **Protocol-Based** -- `typing.Protocol` with `@runtime_checkable` for structural subtyping

## Install

```bash
pip install "git+https://github.com/FlossWare/learning-ai.git"
```

## Quick Start

```python
import asyncio
from learning_ai import SimpleLearningExtractor, ChatMessage

async def main():
    extractor = SimpleLearningExtractor()

    # Detect feedback in conversation
    messages = [
        ChatMessage(role="user", content="You should have used the fleet for that"),
        ChatMessage(role="assistant", content="I'll use the fleet next time"),
        ChatMessage(role="user", content="Always use multi-model consensus"),
    ]
    signals = await extractor.detect_feedback(messages)
    for s in signals:
        print(f"  [{s.type}] {s.content} (confidence={s.confidence:.0%})")

    # Record an experience
    exp_id = await extractor.record_experience(
        task="Implement retry logic",
        outcome="Used exponential backoff with jitter",
    )

    # Extract learnings
    learnings = await extractor.extract_learnings(exp_id)
    for l in learnings:
        print(f"  Learning: {l.content} ({l.category})")

    # Track strategy rewards (Thompson Sampling)
    await extractor.update_strategy("greedy", "success", reward=0.9)
    await extractor.update_strategy("exploratory", "failure", reward=0.2)

asyncio.run(main())
```

## Decorators

```python
from learning_ai import detect_feedback, record_experience, SimpleLearningExtractor

extractor = SimpleLearningExtractor()

@detect_feedback(extractor=extractor)
async def handle_conversation(messages, *, model="default"):
    return await backend.chat(messages, model=model)

@record_experience(extractor=extractor)
async def execute_task(task="default task"):
    return await backend.process(task)
```

## Pattern Matching

```python
from learning_ai import FeedbackPatternMatcher, ChatMessage

matcher = FeedbackPatternMatcher()
signals = matcher.match([
    ChatMessage(role="user", content="That's not correct, prefer X over Y"),
])
# signals: [FeedbackSignal(type="correction", ...), FeedbackSignal(type="preference", ...)]
```

## Standards

See [STANDARDS.md](STANDARDS.md) for ADR compliance details.

## License

MIT -- see [LICENSE](LICENSE).
