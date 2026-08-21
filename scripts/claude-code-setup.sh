#!/bin/bash
# Add learning-ai integration to your CLAUDE.md
set -e

CLAUDE_MD="${CLAUDE_MD:-./CLAUDE.md}"

if [ ! -f "$CLAUDE_MD" ]; then
    echo "Creating $CLAUDE_MD"
    touch "$CLAUDE_MD"
fi

cat >> "$CLAUDE_MD" << 'EOF'

## Learning Extraction (learning-ai)

This project uses [learning-ai](https://github.com/FlossWare/learning-ai) for feedback detection, experience recording, and learning extraction.

**Install:** `pip install "git+https://github.com/FlossWare/learning-ai.git"`

**Key imports:**
```python
from learning_ai import detect_feedback, record_experience, SimpleLearningExtractor, FeedbackPatternMatcher
```

**Usage patterns:**
- Feedback: `FeedbackPatternMatcher().match(messages)` detects corrections/preferences/confirmations
- Decorator: `@detect_feedback(extractor=e)` for auto-detection in conversation handlers
- Experience: `SimpleLearningExtractor().record_experience(task, outcome)`
- Learnings: `extractor.extract_learnings(experience_id)` for key-phrase extraction
- Strategy: `extractor.update_strategy(strategy, outcome, reward=0.9)` for Thompson Sampling
- Zero external dependencies (stdlib only)
EOF

echo "Added learning-ai integration to $CLAUDE_MD"
