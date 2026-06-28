"""
Physics Visual Reels — Visual Constants

Single source of truth for the entire visual language.
Every renderer and scene file imports from here.
Do NOT define colors, fonts, or sizes anywhere else.
"""

from manim import ManimColor

# Backgrounds (pure black for high contrast)
# ──────────────────────────────────────────────
BG_PRIMARY = "#000000"
BG_SECONDARY = "#0A0A0A"

# ──────────────────────────────────────────────
# Semantic Physics Colors — LOCKED
# These mappings are permanent. Every scene must
# use the correct color for the correct concept.
# ──────────────────────────────────────────────
COLOR_VELOCITY   = "#5B9FFF"   # blue
COLOR_FORCE      = "#FF6B6B"   # red
COLOR_ENERGY     = "#FFD166"   # yellow
COLOR_MASS       = "#C4C4C4"   # grey
COLOR_GRAVITY    = "#BB86FC"   # purple
COLOR_WAVELENGTH = "#7CFFB2"   # green
COLOR_TIME       = "#60EFFF"   # cyan

# ──────────────────────────────────────────────
# Neutral palette
# ──────────────────────────────────────────────
COLOR_WHITE = "#F5F8FF"
COLOR_MUTED = "#6A7488"
COLOR_GRID  = "#223044"

# ──────────────────────────────────────────────
# Typography
# ──────────────────────────────────────────────
FONT_BODY = "Inter"                # geometric sans — labels, theory names
# For equations, use Manim's default MathTex (LaTeX rendering)
FONT_SIZE_LABEL       = 36        # brief diagram labels
FONT_SIZE_FORMULA     = 48        # equations like F = ma
FONT_SIZE_THEORY_NAME = 42        # "General Relativity" etc.

# ──────────────────────────────────────────────
# Atom anchor icon dimensions (Manim units)
# ──────────────────────────────────────────────
ATOM_NUCLEUS_RADIUS = 0.08
ATOM_ORBIT_RADIUS   = 0.25
ATOM_COLOR          = "#5B9FFF"

# ──────────────────────────────────────────────
# Text-on-screen rules
# ──────────────────────────────────────────────
TEXT_RULES = {
    "subtitles":          False,   # NO subtitles / captions
    "formula_names":      True,    # F = ma, E = mc², etc.
    "theory_names":       True,    # "General Relativity", "Newton's Third Law"
    "diagram_labels":     True,    # brief labels like "mass", "velocity"
    "paragraph_text":     False,   # NO bullet points or paragraphs
    "max_words_per_frame": 4,      # max simultaneous words on screen
}

# ──────────────────────────────────────────────
# Video specs
# ──────────────────────────────────────────────
VIDEO_WIDTH  = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS    = 30
VIDEO_ASPECT = "9:16"

# ──────────────────────────────────────────────
# TTS settings
# ──────────────────────────────────────────────
TTS_VOICE = "en-US-SteffanNeural"
TTS_RATE  = "-2%"
TTS_PITCH = "-1Hz"
