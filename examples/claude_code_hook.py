#!/usr/bin/env python3
"""Claude Code hook: detect feedback patterns in conversation context.

Usage as a post-tool-edit hook in .claude/hooks/post-tool-edit.py:
    python3 examples/claude_code_hook.py "$CONTENT"
"""
from __future__ import annotations

import sys

FEEDBACK_KEYWORDS = [
    "you should have", "that's not right", "always use",
    "never do", "prefer", "instead of", "don't",
    "that worked well", "good job", "perfect",
]


def main():
    if len(sys.argv) < 2:
        print("Usage: claude_code_hook.py <content>")
        sys.exit(1)

    content = " ".join(sys.argv[1:]).lower()
    matches = [k for k in FEEDBACK_KEYWORDS if k in content]
    if not matches:
        sys.exit(0)

    print(f"[learning-ai] FEEDBACK DETECTED in content")
    print(f"[learning-ai] Matched patterns: {', '.join(matches)}")
    print("[learning-ai] Consider recording with SimpleLearningExtractor:")
    print("  from learning_ai import SimpleLearningExtractor")
    print("  extractor = SimpleLearningExtractor()")
    print('  exp_id = await extractor.record_experience(task=..., outcome=...)')


if __name__ == "__main__":
    main()
