"""
Physics Visual Reels — edge-tts Voices List

Queries edge-tts for all available English voices and prints them.
Usage:
    python src/list_voices.py
"""

import asyncio
import sys

# Reconfigure stdout to use UTF-8 to prevent Unicode errors on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import edge_tts
except ImportError:
    print("edge-tts is not installed. Run: pip install edge-tts")
    sys.exit(1)


async def main():
    voices = await edge_tts.list_voices()
    
    # Filter for English (locale starts with 'en-')
    english_voices = [v for v in voices if v["Locale"].lower().startswith("en-")]
    
    # Sort by Locale, then Name
    english_voices.sort(key=lambda x: (x["Locale"], x["ShortName"]))
    
    print(f"{'Voice ID':<35} | {'Gender':<8} | {'Region/Locale':<13} | {'Personalities'}")
    print("-" * 90)
    for v in english_voices:
        personalities = ", ".join(v.get("VoicePersonalities", [])) if v.get("VoicePersonalities") else "General"
        print(f"{v['ShortName']:<35} | {v['Gender']:<8} | {v['Locale']:<13} | {personalities}")


if __name__ == "__main__":
    asyncio.run(main())
