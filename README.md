# Physics Visual Reels

Zero-cost automated pipeline for creating Instagram Reels that visually explain physics concepts.

## Positioning

- Audience: Students and curious non-experts
- Platform: Instagram Reels / Shorts / TikTok
- Language: English
- Voice: edge-tts (en-US-DavisNeural — deep storyteller)
- Format: faceless pure animation explainers (no subtitles)
- Text on screen: formula names, theory names, and brief labels only
- Funnel goal: build audience → route to digital product / PDF / newsletter

## Two-Agent Pipeline

```text
Topic-Idea Engine (weekly)
  → data/topic_backlog.csv (15 ranked topics per batch)
  → Script Writer Agent (per topic)
      → script.json (validated)
      → edge-tts voiceover
      → Manim visual render
      → FFmpeg assembly
      → final reel (1080×1920 MP4)
```

Both agents are powered by Google Gemini API (free tier).

## Quick Start

1. Get a free Gemini API key from https://aistudio.google.com
2. Copy `.env.example` to `.env` and add your key
3. Install dependencies: `pip install -r requirements.txt`
4. Generate topic ideas: `python src/generate_ideas.py`
5. Generate a script: `python src/generate_script.py --topic "gravity / spacetime curvature"`
6. Generate voiceover: `python src/generate_voiceover.py --episode 001-gravity-spacetime`
7. Render and assemble: `.\render_episode.ps1 001-gravity-spacetime`

## Visual Style

- Background: navy/near-black (#0A0E1A) — not pure black
- Semantic colors: velocity=blue, force=red, energy=yellow, mass=grey, gravity=purple, wavelength=green, time=cyan
- Typography: Inter (labels) + LaTeX (equations)
- Motion discipline: every animation maps to a narration step, no decorative flourishes
- Brand anchor: atom icon (nucleus + orbiting ring) in transitions

## Folder Structure

```text
configs/       content rules, quality gates, visual style definitions
docs/          architecture and planning notes
templates/     episode spec template
prompts/       system + per-call prompts for both AI agents
episodes/      one folder per reel
outputs/       rendered videos, audio, final files
src/           pipeline code (generators, validators, renderers)
assets/        fonts, logos, brand files
data/          topic backlog, used hooks/CTAs log
```

## Tech Stack (all free)

- Python: workflow glue
- Manim Community Edition: animation engine
- FFmpeg: audio/video assembly
- Google Gemini API (free tier): script + idea generation
- edge-tts: voiceover (en-US-DavisNeural)
- Pillow + imageio: fallback preview renderer

## Operating Rule

Do not overbuild. The first milestone is **10 published reels**, not a perfect automation system.
