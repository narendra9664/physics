# Architecture

## Goal

Create a zero-cost automated pipeline for short physics concept explainer videos.

## Key Decisions

- **Two-agent system**: Topic-Idea Engine generates ranked topic batches. Script Writer Agent generates narration scripts per topic.
- **Human review stays in the loop** for accuracy — physics must be correct.
- **No subtitles** — pure animation + voiceover. Formula names and theory labels are the only text on screen.
- **Semantic color coding** — each physics concept has a permanent color (velocity=blue, force=red, etc.)
- **Motion discipline** — every animation maps to a narration step. No decorative flourishes.

## Two-Agent Loop

```text
Topic-Idea Engine (run weekly or when backlog < 10)
  Input: existing backlog, analytics, focus requests
  Output: 15 ranked topics → data/topic_backlog.csv
  Scoring: hook_potential (40%) + visual_clarity (25%) + misconception_density (20%) + evergreen (15%)

Script Writer Agent (run per topic)
  Input: topic, audience intent, length variant, avoid lists
  Output: validated script.json with beats, visual cues, source, caveat
```

## Full Orchestration

```text
01_idea_generation
  Agent: Topic-Idea Engine via Gemini API
  Output: data/topic_backlog.csv

02_script_generation
  Agent: Script Writer Agent via Gemini API
  Output: episodes/{slug}/script.json
  Validation: validate_script.py (JSON, word budget, source/caveat, hook dedup)
  Retry: up to 3 attempts if validation fails

03_voiceover
  Tool: edge-tts (en-US-DavisNeural, rate=-8%, pitch=-3Hz)
  Output: episodes/{slug}/voiceover.mp3 + timing.json

04_manim_render
  Tool: Manim CE (1080x1920, 9:16, navy background)
  Input: script.json visual cues + timing.json
  Output: silent vertical animation MP4

05_assembly
  Tool: FFmpeg
  Input: silent MP4 + voiceover MP3
  Output: final 1080x1920 MP4

06_quality_gate
  Checks: accuracy, hook, misconception correction, motion discipline, semantic colors, no subtitles
```

## Zero-Cost Components

- Python: workflow glue
- Google Gemini API (free tier): script + idea generation
- Manim Community Edition: animation engine
- FFmpeg: assembly / export
- edge-tts: voiceover
- Manual review: accuracy and quality control

## Market Research Insights (from PDF appendix)

- Visual anomaly hooks beat question hooks by ~20% in retention
- Misconception correction is the strongest save/share driver
- CTA after correction beat converts 2-3x vs generic
- Dark BG + bright accents = high-retention "cinematic physics" aesthetic
- 2.3-2.5 words/second pacing for narrated explainers
- Animation + voiceover outperforms static + text-to-speech
- Saves and shares weight more than likes for educational content distribution
