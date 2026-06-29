"""
Physics Visual Reels — Pipeline Runner

Automatically finds the next queued topic from data/topic_backlog.csv,
generates the script and voiceover, and renders/assembles it if scene.py is present.
Usage:
    python src/run_pipeline.py
    python src/run_pipeline.py --topic "quantum tunneling"
"""

import os
import sys
import csv
import argparse
import subprocess
import shutil
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Reconfigure stdout to use UTF-8 to prevent Unicode encoding errors
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")


def slugify(text: str) -> str:
    """Convert a topic title to a clean slug directory name."""
    s = text.lower().strip()
    s = s.replace(" ", "-").replace("/", "-").replace("\\", "-").replace(":", "-")
    s = s.replace("--", "-").replace("---", "-")
    return s.strip("-")


def get_next_topic() -> tuple[str, str] | None:
    """Find the next queued topic in the backlog."""
    backlog_path = PROJECT_ROOT / "data" / "topic_backlog.csv"
    if not backlog_path.exists():
        return None

    rows = []
    fieldnames = []
    with open(backlog_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    selected_topic = None
    selected_index = -1
    
    # 1. Prefer queued topics that ALREADY have a scene.py written
    for i, row in enumerate(rows):
        if row.get("status") in ["queued", "backlog"]:
            topic = row.get("topic")
            slug = slugify(topic)
            scene_file = PROJECT_ROOT / "episodes" / slug / "scene.py"
            if scene_file.exists():
                selected_topic = topic
                selected_index = i
                break

    # 2. Fall back to the first queued topic
    if selected_topic is None:
        for i, row in enumerate(rows):
            if row.get("status") in ["queued", "backlog"]:
                selected_topic = row.get("topic")
                selected_index = i
                break

    if selected_topic:
        # Mark as queued so it's locked
        rows[selected_index]["status"] = "queued"
        with open(backlog_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return selected_topic, slugify(selected_topic)

    return None


def mark_topic_status(topic: str, status: str):
    """Update status of a topic in the backlog."""
    backlog_path = PROJECT_ROOT / "data" / "topic_backlog.csv"
    if not backlog_path.exists():
        return

    rows = []
    fieldnames = []
    with open(backlog_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    for row in rows:
        if row.get("topic") == topic:
            row["status"] = status
            break

    with open(backlog_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Run the entire video automation pipeline.")
    parser.add_argument("--topic", type=str, help="Specific topic to override backlog")
    parser.add_argument("--slug", type=str, help="Override episode folder slug")
    args = parser.parse_args()

    topic = args.topic
    slug = args.slug

    # 1. Select topic
    is_backlog = False
    if not topic:
        res = get_next_topic()
        if not res:
            print("No queued or backlog topics found in data/topic_backlog.csv.")
            sys.exit(0)
        topic, slug = res
        is_backlog = True
    else:
        slug = slug or slugify(topic)

    print("=" * 60)
    print(f"STARTING PIPELINE: {topic}")
    print(f"Slug directory: episodes/{slug}")
    print("=" * 60)

    # Step A: Script/Voiceover Generation
    script_file = PROJECT_ROOT / "episodes" / slug / "script.json"
    if not script_file.exists():
        print("\n[1/4] Generating script via Gemini API...")
        res = subprocess.run([
            sys.executable, str(PROJECT_ROOT / "src" / "generate_script.py"),
            "--topic", topic,
            "--slug", slug
        ])
        if res.returncode != 0:
            print("❌ Script generation failed.")
            if is_backlog:
                mark_topic_status(topic, "backlog")
            sys.exit(1)
    else:
        print("\n[1/4] script.json already exists. Skipping script generation.")

    # Step B: Voiceover Generation
    voiceover_file = PROJECT_ROOT / "episodes" / slug / "voiceover.mp3"
    if not voiceover_file.exists():
        print("\n[2/4] Generating voiceover and timing markers...")
        res = subprocess.run([
            sys.executable, str(PROJECT_ROOT / "src" / "generate_voiceover.py"),
            "--episode", slug
        ])
        if res.returncode != 0:
            print("❌ Voiceover generation failed.")
            if is_backlog:
                mark_topic_status(topic, "backlog")
            sys.exit(1)
    else:
        print("\n[2/4] voiceover.mp3 already exists. Skipping voiceover generation.")

    # Step C: Manim Rendering
    scene_file = PROJECT_ROOT / "episodes" / slug / "scene.py"
    if not scene_file.exists():
        print(f"\n[3/4] WARNING: Scene file 'scene.py' not found at {scene_file}")
        print("Please write your Manim code for this episode and push it to render the video.")
        print("Your script and voiceover are ready. Pausing render step.")
        sys.exit(0)

    # Find the class name inside scene.py
    class_name = None
    with open(scene_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("class "):
                class_name = line.split("class ")[1].split("(")[0].strip()
                break

    if not class_name:
        print("Error: Could not find Manim class name inside scene.py")
        sys.exit(1)

    print(f"\n[3/4] Rendering Manim scene '{class_name}'...")
    res = subprocess.run([
        sys.executable, "-m", "manim", "render", "-qh", "--format", "mp4", str(scene_file)
    ])
    if res.returncode != 0:
        print("Manim render failed.")
        if is_backlog:
            mark_topic_status(topic, "backlog")
        sys.exit(1)

    # Copy silent render output
    src_mp4 = PROJECT_ROOT / "media" / "videos" / "scene" / "1920p30" / f"{class_name}.mp4"
    renders_dir = PROJECT_ROOT / "outputs" / "renders"
    renders_dir.mkdir(parents=True, exist_ok=True)
    dest_mp4 = renders_dir / f"{slug}-silent.mp4"

    if src_mp4.exists():
        shutil.copy(src_mp4, dest_mp4)
    else:
        print(f"Error: Rendered MP4 not found at {src_mp4}")
        sys.exit(1)

    # Step D: Final Assembly
    print("\n[4/4] Merging audio and video into final vertical MP4...")
    res = subprocess.run([
        sys.executable, str(PROJECT_ROOT / "src" / "assemble_final.py"),
        "--episode", slug
    ])
    if res.returncode != 0:
        print("Final assembly failed.")
        if is_backlog:
            mark_topic_status(topic, "backlog")
        sys.exit(1)

    # Step E: Telegram Upload
    # Check if Telegram chat ID is configured (either in local env or environment)
    if os.getenv("TELEGRAM_CHAT_ID"):
        print("\n[UPLOADER] Sending final reel to Telegram Bot...")
        subprocess.run([
            sys.executable, str(PROJECT_ROOT / "src" / "send_telegram.py"),
            "--episode", slug
        ])

    # Mark as rendered
    if is_backlog:
        mark_topic_status(topic, "rendered")

    print("\nPIPELINE RUN COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
