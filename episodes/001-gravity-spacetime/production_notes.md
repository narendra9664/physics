# Production Notes — 001 Gravity / Spacetime Curvature

## Status

Awaiting script generation.

## Topic

Gravity / spacetime curvature — how mass warps space and creates what we experience as "falling."

## Visual Plan

- Show a flat 2D grid (spacetime fabric)
- Place a mass on it — grid warps/curves
- Smaller objects follow curved paths (geodesics) near the mass
- Formula: show Einstein field equations or E = mc² briefly
- Theory name: "General Relativity" fades in
- Semantic colors: mass = grey (#C4C4C4), gravity = purple (#BB86FC), velocity = blue (#5B9FFF)
- Atom anchor appears during scene transitions

## Pipeline Steps

1. [ ] Generate script via `python src/generate_script.py --topic "gravity / spacetime curvature"`
2. [ ] Review script.json for accuracy
3. [ ] Generate voiceover via `python src/generate_voiceover.py --episode 001-gravity-spacetime`
4. [ ] Write Manim scene (scene.py)
5. [ ] Render silent video
6. [ ] Assemble final video via `python src/assemble_final.py --episode 001-gravity-spacetime`
7. [ ] Quality gate review
