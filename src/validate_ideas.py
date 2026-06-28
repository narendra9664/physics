"""
Physics Visual Reels — Topic Idea Validator

Validates topic idea batch JSON from the Topic-Idea Engine.
Checks for duplicates against existing backlog, verifies composite scores,
and ensures source bucket diversity.

Usage:
    from validate_ideas import validate_ideas
    result = validate_ideas(batch_dict, existing_backlog)
"""

from __future__ import annotations

import json
import csv
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class IdeaValidationResult:
    """Result of validating a topic idea batch."""
    passed_topics: list[dict] = field(default_factory=list)
    rejected_topics: list[tuple[dict, str]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0 and len(self.passed_topics) > 0


def _similarity(a: str, b: str) -> float:
    """String similarity between two topic titles."""
    try:
        from Levenshtein import ratio
        return ratio(a.lower().strip(), b.lower().strip())
    except ImportError:
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        if not words_a or not words_b:
            return 0.0
        return len(words_a & words_b) / len(words_a | words_b)


def _verify_composite(topic: dict) -> float | None:
    """Verify composite_score = 0.4*hook + 0.25*visual + 0.2*misconception + 0.15*evergreen."""
    try:
        hook = float(topic.get("estimated_hook_score", 0))
        visual = float(topic.get("estimated_visual_score", 0))
        misconception = float(topic.get("estimated_misconception_score", 0))
        evergreen = float(topic.get("estimated_evergreen_score", 0))
        expected = round(0.4 * hook + 0.25 * visual + 0.2 * misconception + 0.15 * evergreen, 1)
        return expected
    except (TypeError, ValueError):
        return None


def validate_ideas(
    batch: dict,
    existing_titles: list[str] | None = None,
    similarity_threshold: float = 0.85,
) -> IdeaValidationResult:
    """Validate a topic idea batch."""
    result = IdeaValidationResult()

    if not isinstance(batch, dict):
        result.errors.append("Batch must be a JSON object")
        return result

    topics = batch.get("topics", [])
    if not isinstance(topics, list) or len(topics) == 0:
        result.errors.append("'topics' must be a non-empty list")
        return result

    if existing_titles is None:
        existing_titles = []

    # Track source buckets for diversity check
    source_buckets_seen = set()
    accepted_titles = list(existing_titles)

    for topic in topics:
        title = topic.get("topic", "")

        # Check required fields
        required = ["topic", "hook_angle", "visual_approach", "misconception", "source_bucket"]
        missing = [f for f in required if not topic.get(f)]
        if missing:
            result.rejected_topics.append((topic, f"Missing fields: {missing}"))
            continue

        # Check for duplicates against existing backlog
        is_dup = False
        for existing in accepted_titles:
            sim = _similarity(title, existing)
            if sim > similarity_threshold:
                result.rejected_topics.append(
                    (topic, f"Too similar to existing topic '{existing}' (similarity: {sim:.2f})")
                )
                is_dup = True
                break

        if is_dup:
            continue

        # Verify composite score
        expected_score = _verify_composite(topic)
        if expected_score is not None:
            declared = topic.get("composite_score")
            try:
                declared_float = float(declared)
                if abs(declared_float - expected_score) > 0.2:
                    topic["composite_score"] = expected_score  # Correct it
            except (TypeError, ValueError):
                topic["composite_score"] = expected_score

        source_buckets_seen.add(topic.get("source_bucket", ""))
        accepted_titles.append(title)
        result.passed_topics.append(topic)

    # Check source bucket diversity
    if len(source_buckets_seen) < 3:
        result.errors.append(
            f"Only {len(source_buckets_seen)} source buckets represented "
            f"({source_buckets_seen}). Need at least 3."
        )

    # Re-sort by corrected composite score
    result.passed_topics.sort(
        key=lambda t: float(t.get("composite_score", 0)),
        reverse=True,
    )

    return result


def load_existing_backlog(data_dir: Path | None = None) -> list[str]:
    """Load existing topic titles from the backlog CSV."""
    if data_dir is None:
        data_dir = Path(__file__).resolve().parent.parent / "data"

    backlog_file = data_dir / "topic_backlog.csv"
    if not backlog_file.exists():
        return []

    titles = []
    with open(backlog_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("topic", "").strip()
            if title:
                titles.append(title)
    return titles
