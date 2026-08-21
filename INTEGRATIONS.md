# learning-ai Integrations

Install from GitHub:

```bash
pip install "git+https://github.com/FlossWare/learning-ai.git"
```

---

## Claude Code

### CLAUDE.md Snippet

```markdown
## Learning Extraction (learning-ai)

This project uses `learning-ai` for feedback detection, experience recording, and learning extraction.

- Feedback detection: `from learning_ai import detect_feedback, FeedbackPatternMatcher`
- Experience recording: `from learning_ai import record_experience, SimpleLearningExtractor`
- Learning extraction: `extractor.extract_learnings(experience_id)`
- Strategy rewards: `extractor.update_strategy(strategy, outcome, reward=0.9)`
- Use `@detect_feedback` decorator to auto-detect feedback signals in conversations
- Use `@record_experience` decorator to auto-record task outcomes
- Zero external dependencies (stdlib only)
```

### Hook Example

Create `.claude/hooks/post-tool-edit.py` to detect feedback in conversation context:

```python
#!/usr/bin/env python3
"""Post-edit hook: detect feedback patterns in recent messages."""
from __future__ import annotations

import sys

FEEDBACK_KEYWORDS = [
    "you should have", "that's not right", "always use",
    "never do", "prefer", "instead of", "don't",
]


def main():
    if len(sys.argv) < 2:
        sys.exit(0)

    content = " ".join(sys.argv[1:]).lower()
    matches = [k for k in FEEDBACK_KEYWORDS if k in content]
    if matches:
        print(f"[learning-ai] Feedback detected: {', '.join(matches)}")
        print("[learning-ai] Consider recording with SimpleLearningExtractor")


if __name__ == "__main__":
    main()
```

### Skill Example

Create `.claude/skills/extract-learnings.md`:

```markdown
---
name: extract-learnings
description: Extract learnings from a task outcome
---

Use learning-ai to record and extract learnings:

\```python
import asyncio
from learning_ai import SimpleLearningExtractor

extractor = SimpleLearningExtractor()
exp_id = asyncio.run(extractor.record_experience(
    task="<task description>",
    outcome="<outcome description>",
))
learnings = asyncio.run(extractor.extract_learnings(exp_id))
for l in learnings:
    print(f"  {l.category}: {l.content}")
\```
```

---

## OpenAI Codex

### AGENTS.md Snippet

```markdown
## Learning Extraction

Use learning-ai for feedback detection and experience recording:
- Install: `pip install "git+https://github.com/FlossWare/learning-ai.git"`
- Feedback: `FeedbackPatternMatcher().match(messages)` detects corrections/preferences/confirmations
- Experience: `SimpleLearningExtractor().record_experience(task, outcome)`
- Learnings: `extractor.extract_learnings(experience_id)` for key-phrase extraction
- Strategy: `extractor.update_strategy(strategy, outcome, reward=0.9)` for Thompson Sampling
- Decorator: `@detect_feedback(extractor=e)` for auto-detection
```

### Tool Definition

```python
from learning_ai import SimpleLearningExtractor, FeedbackPatternMatcher, ChatMessage

# Detect feedback in messages
matcher = FeedbackPatternMatcher()
signals = matcher.match([
    ChatMessage(role="user", content="You should have used the fleet"),
])
for s in signals:
    print(f"  [{s.type}] {s.content} ({s.confidence:.0%})")

# Record experience
extractor = SimpleLearningExtractor()
exp_id = await extractor.record_experience(
    task="Implement retry logic",
    outcome="Used exponential backoff",
)
learnings = await extractor.extract_learnings(exp_id)
```

---

## Cursor

### .cursorrules Snippet

```
When handling user feedback or recording task outcomes, use learning-ai:

- Import: from learning_ai import detect_feedback, record_experience, SimpleLearningExtractor
- Feedback: FeedbackPatternMatcher().match(messages) detects corrections/preferences
- Decorator: @detect_feedback(extractor=e) for auto-detection in conversation handlers
- Experience: SimpleLearningExtractor().record_experience(task, outcome)
- Learnings: extractor.extract_learnings(experience_id) for key-phrase extraction
- Strategy: extractor.update_strategy(strategy, outcome, reward=0.9)
- Zero dependencies - stdlib only
- Install: pip install "git+https://github.com/FlossWare/learning-ai.git"
```

---

## Crush

### Configuration

```python
# crush.config.py
from learning_ai import SimpleLearningExtractor, FeedbackPatternMatcher, ChatMessage

extractor = SimpleLearningExtractor()
matcher = FeedbackPatternMatcher()

def detect_user_feedback(messages: list[dict]) -> list[dict]:
    """Detect feedback signals in user messages."""
    chat_msgs = [ChatMessage(role=m["role"], content=m["content"]) for m in messages]
    signals = matcher.match(chat_msgs)
    return [{"type": s.type, "confidence": s.confidence, "content": s.content} for s in signals]

async def record_task(task: str, outcome: str) -> str:
    """Record a task outcome and extract learnings."""
    exp_id = await extractor.record_experience(task=task, outcome=outcome)
    learnings = await extractor.extract_learnings(exp_id)
    return exp_id
```

---

## Generic Python Agent

### Feedback Detection

```python
from learning_ai import FeedbackPatternMatcher, ChatMessage

matcher = FeedbackPatternMatcher()
messages = [
    ChatMessage(role="user", content="You should have used the fleet for that"),
    ChatMessage(role="assistant", content="I'll use the fleet next time"),
    ChatMessage(role="user", content="Always use multi-model consensus"),
    ChatMessage(role="user", content="That worked well, good job"),
]

signals = matcher.match(messages)
for s in signals:
    print(f"  [{s.type}] {s.content} (confidence={s.confidence:.0%})")
# Output:
#   [correction] You should have used the fleet for that (confidence=90%)
#   [preference] Always use multi-model consensus (confidence=85%)
#   [confirmation] That worked well, good job (confidence=80%)
```

### Experience Recording

```python
import asyncio
from learning_ai import SimpleLearningExtractor

async def main():
    extractor = SimpleLearningExtractor()

    # Record experiences
    exp_id = await extractor.record_experience(
        task="Implement retry logic with exponential backoff",
        outcome="Used jitter to avoid thundering herd. Apply backoff pattern",
    )

    # Extract learnings
    learnings = await extractor.extract_learnings(exp_id)
    for l in learnings:
        print(f"  {l.category}: {l.content}")
    # Output:
    #   key_phrase: Implement retry logic
    #   key_phrase: Apply backoff pattern

    # Track strategy rewards (Thompson Sampling)
    await extractor.update_strategy("greedy", "success", reward=0.9)
    await extractor.update_strategy("exploratory", "failure", reward=0.2)
    print(f"Strategies: {extractor.strategies}")

asyncio.run(main())
```

### Decorator Pattern

```python
from learning_ai import detect_feedback, record_experience, SimpleLearningExtractor

extractor = SimpleLearningExtractor()

@detect_feedback(extractor=extractor)
async def handle_conversation(messages, *, model="default"):
    """Feedback signals are auto-detected from the messages argument."""
    return await backend.chat(messages, model=model)

@record_experience(extractor=extractor)
async def execute_task(task="default task"):
    """Task outcome is auto-recorded with learning extraction."""
    return await backend.process(task)
```

---

## Cross-Package Integration

### learning-ai + evaluation-ai

Record evaluation outcomes as learnings:

```python
from learning_ai import record_experience, SimpleLearningExtractor
from evaluation_ai import adversarial_verify

extractor = SimpleLearningExtractor()

@record_experience(extractor=extractor)
@adversarial_verify(backend=eval_backend, available_models=models)
async def verified_and_recorded(task="analyze code", *, model="default"):
    return await backend.chat([{"role": "user", "content": task}], model=model)
```

### learning-ai + consensus-ai

Record consensus decisions:

```python
from learning_ai import detect_feedback, SimpleLearningExtractor
from consensus_ai import with_consensus

extractor = SimpleLearningExtractor()

@detect_feedback(extractor=extractor)
@with_consensus(strategy="majority_vote", models=["m1", "m2", "m3"])
async def consensus_with_feedback(messages, *, model="default"):
    return await backend.chat(messages, model=model)
```

### Full Stack: All Packages

```python
from learning_ai import detect_feedback, record_experience, SimpleLearningExtractor
from evaluation_ai import adversarial_verify
from consensus_ai import with_consensus
from structured_output_ai import structured_output
from resilience_ai import with_retry, with_circuit_breaker
from observability_ai import track_execution

extractor = SimpleLearningExtractor()

@record_experience(extractor=extractor)     # record outcome
@detect_feedback(extractor=extractor)       # detect feedback
@structured_output(schema=SCHEMA)           # parse into typed object
@track_execution(telemetry=t)               # track timing and cost
@adversarial_verify(backend=eval_b)         # verify correctness
@with_consensus(models=models)              # multi-model vote
@with_retry(max_attempts=3)                 # retry on failure
@with_circuit_breaker(provider="llm")       # circuit break per provider
async def production_query(messages, *, task="query", model="default"):
    return await backend.chat(messages, model=model)
```
