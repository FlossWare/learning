# learning-ai

**Historical learning utilities being consolidated into Loom, Knowledge, Evaluation, and Strategy.**

The original package combined feedback detection, experience recording, learning extraction, and Thompson Sampling reward tracking. Those concerns now have clearer architectural homes.

## Migration map

| Former capability | Canonical destination |
|---|---|
| User feedback / correction detection | Loom interaction observations |
| Experience/task recording | Loom evidence and checkpoint/run history |
| Learning extraction | `knowledge` and Loom Knowledge APIs |
| Strategy rewards | `evaluation` + strategy implementation state |
| Thompson Sampling state | `strategy` |

The important distinction is that **Knowledge is durable understanding**, not a raw conversation or experience log. Interaction observations, evidence, and evaluation are inputs from which Knowledge may be derived.

## Status

No new architectural capabilities should be added here. Reusable implementation pieces should be migrated to their canonical destinations and this repository can then be archived as historical material.

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
