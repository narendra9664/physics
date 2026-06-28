"""
Physics Visual Reels — Script Validator

Validates script JSON output before it enters the TTS + Manim pipeline.
Implements the 4-check validation from the Script Writer Agent prompt.

Usage:
    python src/validate_script.py --file path/to/script.json
    python src/validate_script.py --paste   (interactive paste mode)

As a library:
    from validate_script import validate_script
    result = validate_script(script_dict)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Reconfigure stdout to use UTF-8 to prevent Unicode errors on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dataclasses import dataclass, field


# Word budgets per variant per beat
WORD_BUDGETS = {
    "30s": {
        "total": (70, 80),
        "beats": {
            "hook": (5, 8),
            "problem": (12, 15),
            "explanation": (25, 30),
            "example": (15, 18),
            "cta": (10, 12),
        },
    },
    "60s": {
        "total": (140, 160),
        "beats": {
            "hook": (8, 12),
            "problem": (18, 22),
            "explanation": (40, 50),
            "example": (30, 35),
            "correction": (20, 25),
            "cta": (15, 18),
        },
    },
    "90s": {
        "total": (210, 240),
        "beats": {
            "hook": (8, 12),
            "importance": (18, 25),
            "explanation": (45, 60),
            "worked_example": (45, 55),
            "analogy": (45, 55),
            "correction": (25, 30),
            "cta": (12, 15),
        },
    },
}

OVER_BUDGET_TOLERANCE = 0.15  # 15%


@dataclass
class ValidationResult:
    """Result of validating a script."""
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def fail(self, msg: str):
        self.passed = False
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)


def _check_json_structure(script: dict, result: ValidationResult):
    """Check 1: Validate JSON structure has all required fields."""
    required_fields = ["topic", "audience_intent", "length_variant", "beats", "source", "caveat", "cta"]
    for f in required_fields:
        if f not in script:
            result.fail(f"Missing required field: '{f}'")

    if "beats" in script:
        if not isinstance(script["beats"], list) or len(script["beats"]) == 0:
            result.fail("'beats' must be a non-empty list")
        else:
            for i, beat in enumerate(script["beats"]):
                for bf in ["beat", "text", "word_count", "visual_cue"]:
                    if bf not in beat:
                        result.fail(f"Beat {i} missing field: '{bf}'")

    valid_intents = ["exam_prep", "curiosity", "maker"]
    if script.get("audience_intent") not in valid_intents:
        result.fail(f"'audience_intent' must be one of {valid_intents}, got '{script.get('audience_intent')}'")

    valid_variants = ["30s", "60s", "90s"]
    if script.get("length_variant") not in valid_variants:
        result.fail(f"'length_variant' must be one of {valid_variants}, got '{script.get('length_variant')}'")


def _check_word_budgets(script: dict, result: ValidationResult):
    """Check 2: Validate word counts per beat and total."""
    variant = script.get("length_variant")
    if variant not in WORD_BUDGETS:
        return  # Already caught in structure check

    budget = WORD_BUDGETS[variant]
    total_min, total_max = budget["total"]

    total_words = 0
    for beat in script.get("beats", []):
        beat_name = beat.get("beat", "")
        word_count = beat.get("word_count", 0)
        actual_words = len(beat.get("text", "").split())
        total_words += actual_words

        # Check declared vs actual word count
        if abs(actual_words - word_count) > 3:
            result.warn(f"Beat '{beat_name}': declared {word_count} words but text has {actual_words} words")

        # Check against budget
        if beat_name in budget["beats"]:
            bmin, bmax = budget["beats"][beat_name]
            max_allowed = bmax * (1 + OVER_BUDGET_TOLERANCE)
            if actual_words > max_allowed:
                result.fail(
                    f"Beat '{beat_name}': {actual_words} words exceeds budget "
                    f"({bmin}-{bmax}, max with 15% tolerance: {int(max_allowed)})"
                )

    if total_words < total_min * 0.85:
        result.fail(f"Total word count {total_words} is below minimum {total_min}")
    elif total_words > total_max * (1 + OVER_BUDGET_TOLERANCE):
        result.fail(f"Total word count {total_words} exceeds maximum {int(total_max * (1 + OVER_BUDGET_TOLERANCE))}")
    elif total_words < total_min or total_words > total_max:
        result.warn(f"Total word count {total_words} is outside target range ({total_min}-{total_max})")


def _check_source_caveat(script: dict, result: ValidationResult):
    """Check 3: Validate source and caveat are non-empty and not placeholders."""
    placeholders = ["", "N/A", "n/a", "NA", "none", "None", "TBD", "TODO", "placeholder"]

    source = script.get("source", "")
    if not source or source.strip() in placeholders:
        result.fail(f"'source' is empty or a placeholder ('{source}'). Must be a real, checkable reference.")

    caveat = script.get("caveat", "")
    if not caveat or caveat.strip() in placeholders:
        result.fail(f"'caveat' is empty or a placeholder ('{caveat}'). Must explain where the simplification breaks down.")


def _check_hook_cta_dedup(script: dict, result: ValidationResult, data_dir: Path | None = None):
    """Check 4: Check hooks/CTAs against rolling log for duplicates."""
    if data_dir is None:
        data_dir = Path(__file__).resolve().parent.parent / "data"

    hook_text = ""
    for beat in script.get("beats", []):
        if beat.get("beat") == "hook":
            hook_text = beat.get("text", "")
            break

    cta_text = script.get("cta", "")

    # Load used hooks
    hooks_file = data_dir / "used_hooks.json"
    if hooks_file.exists():
        try:
            used_hooks = json.loads(hooks_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            used_hooks = []

        for old_hook in used_hooks:
            similarity = _simple_similarity(hook_text.lower(), old_hook.lower())
            if similarity > 0.85:
                result.fail(f"Hook too similar to previously used hook: '{old_hook}' (similarity: {similarity:.2f})")
                break

    # Load used CTAs
    ctas_file = data_dir / "used_ctas.json"
    if ctas_file.exists():
        try:
            used_ctas = json.loads(ctas_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            used_ctas = []

        for old_cta in used_ctas:
            similarity = _simple_similarity(cta_text.lower(), old_cta.lower())
            if similarity > 0.85:
                result.fail(f"CTA too similar to previously used CTA: '{old_cta}' (similarity: {similarity:.2f})")
                break


def _simple_similarity(a: str, b: str) -> float:
    """Simple word-overlap similarity (Jaccard). Falls back if Levenshtein is not installed."""
    try:
        from Levenshtein import ratio
        return ratio(a, b)
    except ImportError:
        # Fallback: Jaccard word similarity
        words_a = set(a.split())
        words_b = set(b.split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / len(union)


def validate_script(script: dict, data_dir: Path | None = None) -> ValidationResult:
    """Run all 4 validation checks on a script dict."""
    result = ValidationResult()
    _check_json_structure(script, result)
    if result.passed:  # Only continue if structure is valid
        _check_word_budgets(script, result)
        _check_source_caveat(script, result)
        _check_hook_cta_dedup(script, result, data_dir)
    return result


def main():
    parser = argparse.ArgumentParser(description="Validate a physics reel script JSON.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", type=str, help="Path to script JSON file")
    group.add_argument("--paste", action="store_true", help="Paste JSON interactively")
    args = parser.parse_args()

    if args.paste:
        print("Paste your script JSON below (press Enter twice when done):")
        lines = []
        empty_count = 0
        while True:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
            lines.append(line)
        raw = "\n".join(lines)
    else:
        raw = Path(args.file).read_text(encoding="utf-8")

    # Check 1: Parse JSON
    try:
        script = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"FAIL — Invalid JSON: {e}")
        print("Fix the JSON and retry.")
        sys.exit(1)

    # Checks 2-4
    result = validate_script(script)

    if result.warnings:
        print("\nWARNINGS:")
        for w in result.warnings:
            print(f"  ⚠ {w}")

    if result.passed:
        print("\n✅ PASSED — Script is valid and ready for TTS + Manim.")
    else:
        print("\n❌ FAILED — Fix the following errors:")
        for e in result.errors:
            print(f"  ✗ {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
