"""
Physics Visual Reels — Voiceover Generator

Generates voiceover audio from a script JSON using edge-tts.
Voice: en-US-DavisNeural (deep, gravelly storyteller)

Usage:
    python src/generate_voiceover.py --episode 001-gravity-spacetime
    python src/generate_voiceover.py --test
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Reconfigure stdout to use UTF-8 to prevent Unicode errors on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import edge_tts
except ImportError:
    print("edge-tts not installed. Run: pip install edge-tts")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from visual_constants import TTS_VOICE, TTS_RATE, TTS_PITCH

# TTS Configuration
VOICE = TTS_VOICE
RATE = TTS_RATE
PITCH = TTS_PITCH


async def _generate_audio(text: str, output_path: Path, timing_path: Path | None = None):
    """Generate audio and optionally save word-level timing."""
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)

    # Collect subtitle/timing data
    timing_data = []

    if timing_path:
        # Use SubMaker approach for timing
        sub_maker = edge_tts.SubMaker()
        with open(output_path, "wb") as audio_file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_file.write(chunk["data"])
                elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                    timing_data.append({
                        "type": chunk["type"],
                        "text": chunk["text"],
                        "offset": chunk["offset"],
                        "duration": chunk["duration"],
                    })

        # Save timing data
        timing_path.write_text(
            json.dumps(timing_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    else:
        await communicate.save(str(output_path))


def generate_voiceover(episode_slug: str) -> bool:
    """Generate voiceover for an episode from its script.json."""
    episode_dir = PROJECT_ROOT / "episodes" / episode_slug
    script_file = episode_dir / "script.json"

    if not script_file.exists():
        print(f"❌ Script not found: {script_file}")
        print(f"Run generate_script.py first.")
        return False

    script = json.loads(script_file.read_text(encoding="utf-8"))

    # Extract narration text from beats
    narration_parts = []
    for beat in script.get("beats", []):
        text = beat.get("text", "").strip()
        if text:
            narration_parts.append(text)

    if not narration_parts:
        print("❌ No narration text found in script beats.")
        return False

    full_narration = " ".join(narration_parts)
    print(f"Generating voiceover for: {episode_slug}")
    print(f"Voice: {VOICE} (rate={RATE}, pitch={PITCH})")
    print(f"Text length: {len(full_narration.split())} words")

    output_path = episode_dir / "voiceover.mp3"
    timing_path = episode_dir / "timing.json"

    try:
        asyncio.run(_generate_audio(full_narration, output_path, timing_path))
        print(f"✅ Voiceover saved to: {output_path}")
        if timing_path.exists():
            print(f"✅ Timing data saved to: {timing_path}")
        return True
    except Exception as e:
        print(f"❌ TTS generation failed: {e}")
        return False


async def _test_tts():
    """Quick test to verify edge-tts works."""
    print(f"Testing edge-tts with voice: {VOICE}")
    test_text = "Gravity is not a force pulling you down. It is the curvature of spacetime."
    test_path = PROJECT_ROOT / "outputs" / "audio" / "tts_test.mp3"
    test_path.parent.mkdir(parents=True, exist_ok=True)

    communicate = edge_tts.Communicate(test_text, VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(str(test_path))
    print(f"✅ Test audio saved to: {test_path}")
    print(f"Listen to it and verify the deep storyteller tone.")


def main():
    parser = argparse.ArgumentParser(description="Generate voiceover for a physics reel.")
    parser.add_argument("--episode", type=str, help="Episode slug (e.g., 001-gravity-spacetime)")
    parser.add_argument("--test", action="store_true", help="Test TTS with a sample sentence")
    args = parser.parse_args()

    if args.test:
        asyncio.run(_test_tts())
        return

    if not args.episode:
        parser.error("--episode is required (or use --test)")

    generate_voiceover(args.episode)


if __name__ == "__main__":
    main()
