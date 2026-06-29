"""
Physics Visual Reels — Telegram Video Uploader

Uploads the final compiled video to a Telegram Chat/Channel via Bot API.
Usage:
    python src/send_telegram.py --episode 001-gravity-spacetime
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

try:
    import requests
except ImportError:
    print("requests is not installed. Run: pip install requests")
    sys.exit(1)


def send_video_to_telegram(video_path: Path, caption: str = "") -> bool:
    """Send a video file to a Telegram chat/channel using the Bot API."""
    # Bot Token fallback to user-provided token
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "8846840890:AAGn88S1uY5IpMH010h379XQvEJVIQ2IaVk")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not chat_id:
        print("ERROR: TELEGRAM_CHAT_ID is not configured.")
        print("To send videos to Telegram, please add TELEGRAM_CHAT_ID to your .env file or GitHub Secrets.")
        return False

    if not video_path.exists():
        print(f"ERROR: Video file not found at {video_path}")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    
    print(f"Uploading {video_path.name} to Telegram (Chat ID: {chat_id})...")

    # Open video file and send multipart form post
    with open(video_path, "rb") as video_file:
        files = {"video": video_file}
        data = {
            "chat_id": chat_id,
            "caption": caption[:1024]  # Telegram caption limit is 1024 chars
        }
        
        try:
            response = requests.post(url, files=files, data=data, timeout=120)
            result = response.json()
            
            if response.status_code == 200 and result.get("ok"):
                print("✅ Video successfully sent to Telegram!")
                return True
            else:
                print(f"❌ Telegram API Error: {result.get('description', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Network or connection error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Upload an episode to Telegram.")
    parser.add_argument("--episode", type=str, required=True, help="Episode slug folder name")
    args = parser.parse_args()

    # Locate final video and script details
    video_path = PROJECT_ROOT / "outputs" / "final" / f"{args.episode}-final.mp4"
    script_path = PROJECT_ROOT / "episodes" / args.episode / "script.json"

    # Extract caption from script if available
    caption = ""
    if script_path.exists():
        try:
            script_data = json.loads(script_path.read_text(encoding="utf-8"))
            caption = script_data.get("caption", "")
        except Exception:
            pass

    if not caption:
        caption = f"New Physics Visual Reels Episode: {args.episode}"

    success = send_video_to_telegram(video_path, caption)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
