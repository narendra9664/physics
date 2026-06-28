"""
Physics Visual Reels — Final Assembly

Combines silent Manim render with voiceover audio using FFmpeg.
Output: final 1080x1920 MP4 with audio.

Usage:
    python src/assemble_final.py --episode 001-gravity-spacetime
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Reconfigure stdout to use UTF-8 to prevent Unicode errors on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def assemble(episode_slug: str) -> bool:
    """Assemble final video from silent render + voiceover."""
    episode_dir = PROJECT_ROOT / "episodes" / episode_slug
    outputs_dir = PROJECT_ROOT / "outputs"

    # Find inputs
    silent_video = outputs_dir / "renders" / f"{episode_slug}-silent.mp4"
    voiceover = episode_dir / "voiceover.mp3"
    final_output = outputs_dir / "final" / f"{episode_slug}-final.mp4"

    if not silent_video.exists():
        print(f"❌ Silent render not found: {silent_video}")
        print("Run the Manim render first.")
        return False

    if not voiceover.exists():
        print(f"❌ Voiceover not found: {voiceover}")
        print("Run generate_voiceover.py first.")
        return False

    final_output.parent.mkdir(parents=True, exist_ok=True)

    print(f"Assembling final video for: {episode_slug}")
    print(f"  Video: {silent_video}")
    print(f"  Audio: {voiceover}")
    print(f"  Output: {final_output}")

    # FFmpeg command:
    # - Take video from the silent render
    # - Take audio from the voiceover
    # - If video is longer than audio, pad audio with silence
    # - If audio is longer than video, use the shorter duration
    cmd = [
        "ffmpeg", "-y",
        "-i", str(silent_video),
        "-i", str(voiceover),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-map", "0:v:0",
        "-map", "1:a:0",
        str(final_output),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Final video saved: {final_output}")
            _log_used_elements(episode_slug)
            return True
        else:
            print(f"❌ FFmpeg failed:")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found. Install FFmpeg and add it to PATH.")
        return False


def _log_used_elements(episode_slug: str):
    """Save the hook and CTA of the assembled episode to the rolling logs."""
    episode_dir = PROJECT_ROOT / "episodes" / episode_slug
    script_file = episode_dir / "script.json"
    if not script_file.exists():
        return

    try:
        script = json.loads(script_file.read_text(encoding="utf-8"))
    except Exception:
        return

    data_dir = PROJECT_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # 1. Log hook
    hook_text = ""
    for beat in script.get("beats", []):
        if beat.get("beat") == "hook":
            hook_text = beat.get("text", "").strip()
            break

    if hook_text:
        hooks_file = data_dir / "used_hooks.json"
        try:
            used_hooks = json.loads(hooks_file.read_text(encoding="utf-8")) if hooks_file.exists() else []
        except Exception:
            used_hooks = []
        if hook_text not in used_hooks:
            used_hooks.append(hook_text)
            hooks_file.write_text(json.dumps(used_hooks, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"Logged hook as used: '{hook_text}'")

    # 2. Log CTA
    cta_text = script.get("cta", "").strip()
    if cta_text:
        ctas_file = data_dir / "used_ctas.json"
        try:
            used_ctas = json.loads(ctas_file.read_text(encoding="utf-8")) if ctas_file.exists() else []
        except Exception:
            used_ctas = []
        if cta_text not in used_ctas:
            used_ctas.append(cta_text)
            ctas_file.write_text(json.dumps(used_ctas, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"Logged CTA as used: '{cta_text}'")


def main():
    parser = argparse.ArgumentParser(description="Assemble final physics reel video.")
    parser.add_argument("--episode", type=str, required=True, help="Episode slug")
    args = parser.parse_args()

    assemble(args.episode)


if __name__ == "__main__":
    main()
