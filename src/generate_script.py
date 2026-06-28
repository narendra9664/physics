"""
Physics Visual Reels — Script Generator

Automates the Script Writer Agent via Google Gemini API (free tier).
Generates validated script JSON for a given physics topic.

Usage:
    python src/generate_script.py --topic "gravity / spacetime curvature"
    python src/generate_script.py --topic "angular momentum" --intent exam_prep --length 30s
    python src/generate_script.py --test   (API connectivity test)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Reconfigure stdout to use UTF-8 to prevent Unicode errors on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from validate_script import validate_script, ValidationResult

load_dotenv(PROJECT_ROOT / ".env")

MAX_RETRIES = 3


def _get_gemini_client():
    """Initialize the Gemini API client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found. Add it to your .env file.")
        print("Get a free key from https://aistudio.google.com")
        sys.exit(1)

    from google import genai
    client = genai.Client(api_key=api_key)
    return client


def _load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts directory."""
    path = PROJECT_ROOT / "prompts" / filename
    return path.read_text(encoding="utf-8")


def _load_used_items(filename: str) -> list[str]:
    """Load used hooks or CTAs from data directory."""
    path = PROJECT_ROOT / "data" / filename
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save_used_item(filename: str, item: str):
    """Append an item to the used hooks or CTAs log."""
    path = PROJECT_ROOT / "data" / filename
    items = _load_used_items(filename)
    items.append(item)
    path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def _build_user_message(topic: str, intent: str, length: str) -> str:
    """Build the per-call user message."""
    recent_hooks = _load_used_items("used_hooks.json")
    recent_ctas = _load_used_items("used_ctas.json")

    hooks_str = "\n".join(f"- {h}" for h in recent_hooks[-15:]) if recent_hooks else "(none yet)"
    ctas_str = "\n".join(f"- {c}" for c in recent_ctas[-10:]) if recent_ctas else "(none yet)"

    return (
        f"Topic: {topic}\n\n"
        f"Audience intent: {intent}\n\n"
        f"Length variant: {length}\n\n"
        f"Avoid repeating these recent hooks:\n{hooks_str}\n\n"
        f"Avoid repeating these recent CTAs:\n{ctas_str}"
    )


def _extract_json(text: str) -> dict | None:
    """Extract JSON from model response, handling markdown fences."""
    # Try direct parse first
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from code fences
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    return None


def generate_script(
    topic: str,
    intent: str = "curiosity",
    length: str = "60s",
    save_to: Path | None = None,
) -> dict | None:
    """Generate a validated script for a physics topic."""
    client = _get_gemini_client()
    system_prompt = _load_prompt("script_writer_system_prompt.md")
    user_message = _build_user_message(topic, intent, length)

    print(f"Generating script for: {topic} ({length}, {intent})")
    print(f"Using Gemini API...")

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\nAttempt {attempt}/{MAX_RETRIES}...")

        # Build messages
        if attempt == 1:
            prompt = user_message
        else:
            # Include error feedback for retry
            prompt = (
                f"{user_message}\n\n"
                f"IMPORTANT — your previous response failed validation:\n"
                f"{last_error}\n\n"
                f"Please fix these issues and return valid JSON only."
            )

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "system_instruction": system_prompt,
                    "temperature": 0.7,
                },
            )
        except Exception as e:
            print(f"API error: {e}")
            continue

        # Extract JSON
        raw_text = response.text
        script = _extract_json(raw_text)

        if script is None:
            last_error = f"Could not parse JSON from response. Raw text:\n{raw_text[:500]}"
            print(f"  JSON parse failed.")
            continue

        # Validate
        result = validate_script(script, data_dir=PROJECT_ROOT / "data")

        if result.passed:
            print(f"  ✅ Validation passed!")

            if result.warnings:
                for w in result.warnings:
                    print(f"  ⚠ {w}")



            # Save to file if path provided
            if save_to:
                save_to.parent.mkdir(parents=True, exist_ok=True)
                save_to.write_text(
                    json.dumps(script, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                print(f"  Saved to: {save_to}")

            return script
        else:
            last_error = "\n".join(result.errors)
            print(f"  ❌ Validation failed:")
            for e in result.errors:
                print(f"     ✗ {e}")

    print(f"\n❌ Failed after {MAX_RETRIES} attempts. Fix manually or try again.")
    return None


def _test_api():
    """Quick API connectivity test."""
    print("Testing Gemini API connectivity...")
    client = _get_gemini_client()
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'API connection successful' and nothing else.",
        )
        print(f"✅ {response.text.strip()}")
    except Exception as e:
        print(f"❌ API test failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate a physics reel script via Gemini API.")
    parser.add_argument("--topic", type=str, help="Physics topic to generate a script for")
    parser.add_argument("--intent", type=str, default="curiosity", choices=["exam_prep", "curiosity", "maker"])
    parser.add_argument("--length", type=str, default="60s", choices=["30s", "60s", "90s"])
    parser.add_argument("--slug", type=str, help="Episode slug (for save path). Auto-generated if not provided.")
    parser.add_argument("--test", action="store_true", help="Test API connectivity")
    args = parser.parse_args()

    if args.test:
        _test_api()
        return

    if not args.topic:
        parser.error("--topic is required (or use --test)")

    # Determine save path
    slug = args.slug or args.topic.lower().replace(" ", "-").replace("/", "-").replace("--", "-").strip("-")
    save_path = PROJECT_ROOT / "episodes" / slug / "script.json"

    script = generate_script(
        topic=args.topic,
        intent=args.intent,
        length=args.length,
        save_to=save_path,
    )

    if script:
        print(f"\nScript summary:")
        print(f"  Topic: {script.get('topic')}")
        print(f"  Beats: {len(script.get('beats', []))}")
        print(f"  Cover: {script.get('cover_text')}")
        print(f"  Source: {script.get('source')}")


if __name__ == "__main__":
    main()
