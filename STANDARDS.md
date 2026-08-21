# FlossWare Engineering Standards Compliance

This package adheres to the following ADRs from [FlossWare/engineering-standards](https://github.com/FlossWare/engineering-standards):

## ADR-0001: Explicit Opt-In

Learning extraction, feedback detection, and experience recording never activate automatically.
All capabilities require explicit instantiation or decorator application by the developer.

- `SimpleLearningExtractor` must be instantiated and methods called explicitly.
- `FeedbackPatternMatcher` must be instantiated for pattern matching.
- `@detect_feedback` and `@record_experience` decorators are opt-in.
- When no extractor is configured, decorators degrade gracefully (no-op / log only).

## ADR-0006: Cross-Cutting Decorators

Convenience decorators in `learning_ai.decorators`:

- `@detect_feedback(extractor=e)` -- wraps an async conversation handler to auto-detect feedback signals.
- `@record_experience(extractor=e)` -- wraps an async task execution to auto-record outcomes and extract learnings.

## ADR-0008: Free-First

Zero external dependencies at runtime. The package uses only the Python standard library (`re`, `uuid`, `datetime`, `dataclasses`, `functools`, `logging`, `typing`, `inspect`).

Development dependencies (pytest, pytest-asyncio) are optional.

## ADR-0009: Core Principles

- **Modular**: Each concern (patterns, learning, decorators) is a separate module.
- **Composable**: Components can be used independently or combined.
- **Contracts over implementations**: Protocol types define the interfaces; any conforming object works.

## ADR-0013: Thompson Sampling Strategy Selection

`SimpleLearningExtractor.update_strategy()` implements bandit-based reward tracking compatible with Thompson Sampling model selection:

- Maintains Beta distribution parameters (alpha/beta) per strategy.
- Success (reward >= 0.5) increments alpha; failure increments beta.
- Tracks cumulative trial count and total reward.

## ADR-0017: Agent-Neutral

The package works with any agent runtime. The `LearningExtractor` Protocol is the only integration point -- any agent framework that can provide conversation messages is compatible.

No assumptions are made about the calling agent's architecture, event loop, or lifecycle.

## ADR-0020: Capability-Protocol Separation

Learning capabilities are transport-independent:

- `LearningExtractor` Protocol defines what is needed, not how it is delivered.
- No HTTP, gRPC, or other transport assumptions baked in.
- The same learning logic works whether the backend is a local mock, a database adapter, or an agent-internal store.
