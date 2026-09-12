# learning-ai

**Historical learning utilities consolidated into Loom, Knowledge, Evaluation, and Strategy.**

The original package combined feedback detection, experience recording, learning extraction, and Thompson Sampling reward tracking. Those concerns now have clearer architectural homes.

## Migration map

| Former capability | Canonical destination |
|---|---|
| User feedback / correction detection | `evaluation` (`evaluation_ai/feedback.py`) |
| Experience/task recording | Loom evidence and checkpoint/run history + `storage` |
| Learning extraction | `knowledge` and Loom Knowledge APIs |
| Strategy rewards | `strategy` |
| Thompson Sampling state | `strategy` |

The important distinction is that **Knowledge is durable understanding**, not a raw conversation or experience log. Interaction observations, evidence, and evaluation are inputs from which Knowledge may be derived.

## Status

**Retirement candidate.** The reusable conversation-feedback matcher has been extracted to `evaluation`. The remaining historical classes intentionally have not been ported because their responsibilities are already owned by canonical Loom capabilities.

No new architectural capabilities should be added here. Preserve this repository only as historical source and archive it when convenient.

Loom's interaction loop is:

```text
human interaction
      ↓
observation
      ↓
Intent / execution / evaluation
      ↓
Knowledge derivation
      ↓
future interpretation and decisions
```

## License

MIT
