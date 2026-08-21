#!/usr/bin/env python3
"""Verify learning-ai installation and run a quick smoke test."""
import sys


def main():
    try:
        from learning_ai import (
            ChatMessage,
            DEFAULT_PATTERNS,
            Experience,
            ExperienceStore,
            FeedbackDetector,
            FeedbackPattern,
            FeedbackPatternMatcher,
            FeedbackSignal,
            Learning,
            LearningExtractor,
            SimpleLearningExtractor,
            StrategyReward,
            detect_feedback,
            record_experience,
        )
    except ImportError as e:
        print(f"FAIL: Could not import learning_ai: {e}")
        print("Install: pip install 'git+https://github.com/FlossWare/learning-ai.git'")
        sys.exit(1)

    import learning_ai

    print(f"learning-ai v{learning_ai.__version__} installed successfully")
    print(f"Exports: {len(learning_ai.__all__)} public symbols")

    # Smoke test: pattern matching
    matcher = FeedbackPatternMatcher()
    signals = matcher.match([
        ChatMessage(role="user", content="You should have used the fleet"),
    ])
    print(f"Smoke test: FeedbackPatternMatcher matched {len(signals)} signal(s)")

    # Smoke test: extractor
    extractor = SimpleLearningExtractor()
    print(f"Smoke test: SimpleLearningExtractor created: {extractor}")

    # Smoke test: decorators are callable
    assert callable(detect_feedback), "detect_feedback must be callable"
    assert callable(record_experience), "record_experience must be callable"
    print("Smoke test: decorators are callable")

    # Smoke test: protocols
    assert isinstance(extractor, LearningExtractor), "extractor must satisfy LearningExtractor"
    assert isinstance(extractor, FeedbackDetector), "extractor must satisfy FeedbackDetector"
    print("Smoke test: protocols satisfied")

    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
