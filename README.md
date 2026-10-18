# learning

**Reusable outcome-driven learning capabilities for FlossWare.**

This repository is intended to define contracts and implementations for using observed outcomes and feedback to improve future decisions.

## Scope

- Outcome and feedback records
- Learning update contracts
- Attribution and provenance
- Pluggable learning algorithms
- Evaluation of learning behavior
- Interfaces to strategies that consume learned estimates

## Architectural boundaries

- `evaluation` judges results against intended outcomes; `learning` uses outcomes to update future behavior.
- `strategy` owns reusable decision strategies, including bandit strategies.
- `optimizer` owns reusable genetic/evolutionary optimization algorithms.
- `loom` and `loom-ai` own execution contracts and orchestration semantics.

Learning must not override security policy, authorization, budget limits, or other hard constraints. Learned recommendations remain subordinate to those constraints.

## Status

Repository scaffold. Keep algorithm implementations separate from outcome/evidence contracts where doing so enables independent reuse.
