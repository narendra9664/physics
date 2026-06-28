"""
Physics Visual Reels — Topic Idea Generator

Automates the Topic-Idea Engine via Google Gemini API (free tier).
Generates batches of 15 ranked physics topic ideas.

Usage:
    python src/generate_ideas.py
    python src/generate_ideas.py --focus "thermodynamics"
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

# Reconfigure stdout to use UTF-8 to prevent Unicode errors on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from validate_ideas import validate_ideas, load_existing_backlog

load_dotenv(PROJECT_ROOT / ".env")


def _get_gemini_client():
    """Initialize the Gemini API client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found. Add it to your .env file.")
        sys.exit(1)

    from google import genai
    client = genai.Client(api_key=api_key)
    return client


def _load_prompt(filename: str) -> str:
    """Load a prompt template."""
    path = PROJECT_ROOT / "prompts" / filename
    return path.read_text(encoding="utf-8")


def _build_user_message(
    existing_titles: list[str],
    focus: str | None = None,
    top_performing: str | None = None,
) -> str:
    """Build the per-call user message."""
    backlog_str = "\n".join(f"- {t}" for t in existing_titles) if existing_titles else "(empty backlog)"
    focus_str = focus or "none"
    top_str = top_performing or "none yet"

    return (
        f"Existing backlog (titles only):\n{backlog_str}\n\n"
        f"Last batch date: {date.today().isoformat()}\n\n"
        f"Recent top-performing topics (from analytics):\n{top_str}\n\n"
        f"Any focus requests from the creator:\n{focus_str}"
    )


def _extract_json(text: str) -> dict | None:
    """Extract JSON from model response."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    return None


def _append_to_backlog(topics: list[dict], data_dir: Path):
    """Append validated topics to the backlog CSV."""
    backlog_file = data_dir / "topic_backlog.csv"
    file_exists = backlog_file.exists()

    fieldnames = [
        "priority", "topic", "hook_angle", "visual_approach",
        "misconception", "source_bucket", "composite_score",
        "estimated_hook_score", "estimated_visual_score",
        "estimated_misconception_score", "estimated_evergreen_score",
        "duplicate_risk", "status",
    ]

    # Read existing to determine next priority number
    next_priority = 1
    if file_exists:
        with open(backlog_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    p = int(row.get("priority", 0))
                    next_priority = max(next_priority, p + 1)
                except ValueError:
                    pass

    with open(backlog_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        for topic in topics:
            writer.writerow({
                "priority": next_priority,
                "topic": topic.get("topic", ""),
                "hook_angle": topic.get("hook_angle", ""),
                "visual_approach": topic.get("visual_approach", ""),
                "misconception": topic.get("misconception", ""),
                "source_bucket": topic.get("source_bucket", ""),
                "composite_score": topic.get("composite_score", ""),
                "estimated_hook_score": topic.get("estimated_hook_score", ""),
                "estimated_visual_score": topic.get("estimated_visual_score", ""),
                "estimated_misconception_score": topic.get("estimated_misconception_score", ""),
                "estimated_evergreen_score": topic.get("estimated_evergreen_score", ""),
                "duplicate_risk": topic.get("duplicate_risk", ""),
                "status": "backlog",
            })
            next_priority += 1


def generate_ideas(focus: str | None = None) -> list[dict]:
    """Generate a batch of topic ideas."""
    client = _get_gemini_client()
    system_prompt = _load_prompt("topic_idea_engine_system_prompt.md")
    existing_titles = load_existing_backlog(PROJECT_ROOT / "data")
    user_message = _build_user_message(existing_titles, focus=focus)

    print(f"Generating topic ideas via Gemini API...")
    print(f"Existing backlog: {len(existing_titles)} topics")
    if focus:
        print(f"Focus: {focus}")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
            config={
                "system_instruction": system_prompt,
                "temperature": 0.8,
            },
        )
    except Exception as e:
        print(f"❌ API error: {e}")
        return []

    batch = _extract_json(response.text)
    if batch is None:
        print(f"❌ Could not parse JSON from response.")
        print(f"Raw (first 500 chars): {response.text[:500]}")
        return []

    # Validate
    result = validate_ideas(batch, existing_titles)

    if result.rejected_topics:
        print(f"\nRejected {len(result.rejected_topics)} topics:")
        for topic, reason in result.rejected_topics:
            print(f"  ✗ {topic.get('topic', '?')}: {reason}")

    if result.errors:
        print(f"\nValidation errors:")
        for e in result.errors:
            print(f"  ✗ {e}")

    if result.passed_topics:
        # Append to backlog
        _append_to_backlog(result.passed_topics, PROJECT_ROOT / "data")
        print(f"\n✅ Added {len(result.passed_topics)} new topics to backlog.")
        for t in result.passed_topics:
            print(f"  • {t['topic']} (score: {t.get('composite_score', '?')})")

    return result.passed_topics


def main():
    parser = argparse.ArgumentParser(description="Generate physics topic ideas via Gemini API.")
    parser.add_argument("--focus", type=str, help="Focus area (e.g., 'thermodynamics', 'optics')")
    args = parser.parse_args()

    generate_ideas(focus=args.focus)


if __name__ == "__main__":
    main()
