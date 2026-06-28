"""
Physics Visual Reels — Base Renderer

Base Manim scene class that all episode scenes extend.
Sets up the vertical 9:16 canvas, navy background,
and provides helper methods for consistent rendering.

Usage:
    from render_base import PhysicsReelScene

    class GravityScene(PhysicsReelScene):
        def construct(self):
            self.setup_scene()
            # ... your animations ...
"""

from __future__ import annotations

from manim import (
    ThreeDScene, Text, MathTex, Tex,
    Dot, Arrow, Line, Circle, Ellipse,
    VGroup, SurroundingRectangle,
    FadeIn, FadeOut, Write, Transform, ReplacementTransform,
    Create, Uncreate, GrowArrow, Indicate,
    ORIGIN, UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR,
    PI, TAU, DEGREES,
    config,
)
from visual_constants import (
    BG_PRIMARY, BG_SECONDARY,
    COLOR_VELOCITY, COLOR_FORCE, COLOR_ENERGY,
    COLOR_MASS, COLOR_GRAVITY, COLOR_WAVELENGTH, COLOR_TIME,
    COLOR_WHITE, COLOR_MUTED, COLOR_GRID,
    FONT_BODY, FONT_SIZE_LABEL, FONT_SIZE_FORMULA, FONT_SIZE_THEORY_NAME,
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS,
)
from atom_anchor import AtomAnchor


# Configure Manim for vertical 9:16 video
config.pixel_width = VIDEO_WIDTH
config.pixel_height = VIDEO_HEIGHT
config.frame_rate = VIDEO_FPS
config.frame_width = 9
config.frame_height = 16
config.background_color = BG_PRIMARY


class PhysicsReelScene(ThreeDScene):
    """Base scene for all Physics Visual Reels episodes.
    
    Provides:
    - Navy/near-black background (not pure black)
    - Helper methods for labels, formulas, theory names
    - Atom anchor for brand transitions
    - Semantic color helpers
    """

    def setup_scene(self):
        """Call this at the start of construct()."""
        self.camera.background_color = BG_PRIMARY
        self.atom = AtomAnchor()
        self.atom.to_corner(DR, buff=0.4)
        self.atom.set_opacity(0)

    # ── Text helpers (allowed on screen) ──────────────

    def show_formula(self, formula_str: str, **kwargs) -> VMobject:
        """Display a LaTeX formula (e.g., 'F = ma'), with a safe non-LaTeX fallback."""
        import shutil
        has_latex = shutil.which("latex") is not None or shutil.which("pdflatex") is not None
        
        if has_latex:
            try:
                return MathTex(
                    formula_str,
                    font_size=FONT_SIZE_FORMULA,
                    color=COLOR_WHITE,
                    **kwargs,
                )
            except Exception:
                pass  # Fall back if compile fails
        
        # Non-LaTeX Fallback: Compose formulas using standard Text
        clean_formula = formula_str.strip().replace(" ", "")
        
        # 1. Einstein's Field Equations
        if "G_{\\mu\\nu}" in formula_str or "G_\\mu" in formula_str:
            eq = VGroup()
            g1 = Text("G", font="Times New Roman", font_size=FONT_SIZE_FORMULA, color=COLOR_WHITE)
            munu1 = Text("μν", font="Times New Roman", font_size=FONT_SIZE_FORMULA * 0.6, color=COLOR_WHITE).next_to(g1, DR, buff=0.01).shift(DOWN * 0.08)
            
            plus = Text(" + ", font="Times New Roman", font_size=FONT_SIZE_FORMULA, color=COLOR_WHITE).next_to(munu1, RIGHT, buff=0.1)
            
            lambda_sym = Text("Λ", font="Times New Roman", font_size=FONT_SIZE_FORMULA, color=COLOR_WHITE).next_to(plus, RIGHT, buff=0.1)
            
            g2 = Text("g", font="Times New Roman", font_size=FONT_SIZE_FORMULA, color=COLOR_WHITE).next_to(lambda_sym, RIGHT, buff=0.08)
            munu2 = Text("μν", font="Times New Roman", font_size=FONT_SIZE_FORMULA * 0.6, color=COLOR_WHITE).next_to(g2, DR, buff=0.01).shift(DOWN * 0.08)
            
            equals = Text(" = ", font="Times New Roman", font_size=FONT_SIZE_FORMULA, color=COLOR_WHITE).next_to(munu2, RIGHT, buff=0.1)
            
            # Fraction 8πG/c⁴
            num = Text("8πG", font="Times New Roman", font_size=FONT_SIZE_FORMULA * 0.8, color=COLOR_WHITE)
            denom = Text("c⁴", font="Times New Roman", font_size=FONT_SIZE_FORMULA * 0.8, color=COLOR_WHITE)
            frac_group = VGroup(num, denom)
            frac_group.arrange(DOWN, buff=0.08)
            
            width = max(num.width, denom.width) + 0.15
            line = Line(
                start=[-width/2, 0, 0],
                end=[width/2, 0, 0],
                color=COLOR_WHITE,
                stroke_width=2
            )
            line.move_to(frac_group.get_center())
            num.next_to(line, UP, buff=0.06)
            denom.next_to(line, DOWN, buff=0.06)
            
            frac = VGroup(frac_group, line)
            frac.next_to(equals, RIGHT, buff=0.1)
            
            t = Text("T", font="Times New Roman", font_size=FONT_SIZE_FORMULA, color=COLOR_WHITE).next_to(frac, RIGHT, buff=0.15)
            munu3 = Text("μν", font="Times New Roman", font_size=FONT_SIZE_FORMULA * 0.6, color=COLOR_WHITE).next_to(t, DR, buff=0.01).shift(DOWN * 0.08)
            
            eq.add(g1, munu1, plus, lambda_sym, g2, munu2, equals, frac, t, munu3)
            return eq
            
        # 2. Einstein's Mass-Energy Equivalence E = mc²
        elif "E=mc^2" in clean_formula or "E=mc" in clean_formula:
            eq = VGroup()
            e = Text("E", font="Times New Roman", font_size=FONT_SIZE_FORMULA, color=COLOR_WHITE)
            eq_sign = Text(" = ", font="Times New Roman", font_size=FONT_SIZE_FORMULA, color=COLOR_WHITE).next_to(e, RIGHT, buff=0.1)
            m = Text("m", font="Times New Roman", font_size=FONT_SIZE_FORMULA, color=COLOR_WHITE).next_to(eq_sign, RIGHT, buff=0.08)
            c = Text("c", font="Times New Roman", font_size=FONT_SIZE_FORMULA, color=COLOR_WHITE).next_to(m, RIGHT, buff=0.08)
            two = Text("2", font="Times New Roman", font_size=FONT_SIZE_FORMULA * 0.65, color=COLOR_WHITE).next_to(c, UR, buff=0.01).shift(UP * 0.12)
            eq.add(e, eq_sign, m, c, two)
            return eq
            
        # 3. Newton's second law F = ma
        elif "F=ma" in clean_formula:
            eq = VGroup()
            f = Text("F", font="Times New Roman", font_size=FONT_SIZE_FORMULA, color=COLOR_WHITE)
            eq_sign = Text(" = ", font="Times New Roman", font_size=FONT_SIZE_FORMULA, color=COLOR_WHITE).next_to(f, RIGHT, buff=0.1)
            m = Text("m", font="Times New Roman", font_size=FONT_SIZE_FORMULA, color=COLOR_WHITE).next_to(eq_sign, RIGHT, buff=0.08)
            a = Text("a", font="Times New Roman", font_size=FONT_SIZE_FORMULA, color=COLOR_WHITE).next_to(m, RIGHT, buff=0.08)
            eq.add(f, eq_sign, m, a)
            return eq

        # Generic Unicode/Text fallback
        else:
            plain_text = formula_str.replace("\\", "").replace("{", "").replace("}", "")
            return Text(plain_text, font="Times New Roman", font_size=FONT_SIZE_FORMULA, color=COLOR_WHITE, **kwargs)

    def show_theory_name(self, name: str, **kwargs) -> Text:
        """Display a theory name (e.g., 'General Relativity').
        
        Theory names use the body font (Inter) and are ALLOWED on screen.
        """
        text = Text(
            name,
            font=FONT_BODY,
            font_size=FONT_SIZE_THEORY_NAME,
            color=COLOR_WHITE,
            **kwargs,
        )
        return text

    def show_label(self, label: str, color: str = COLOR_MUTED, **kwargs) -> Text:
        """Display a brief diagram label (e.g., 'mass', 'velocity').
        
        Labels use the body font and are ALLOWED on screen.
        Keep labels to 1-2 words max.
        """
        text = Text(
            label,
            font=FONT_BODY,
            font_size=FONT_SIZE_LABEL,
            color=color,
            **kwargs,
        )
        return text

    # ── Semantic shape helpers ─────────────────────────

    def semantic_dot(self, point=ORIGIN, concept: str = "mass", radius: float = 0.1) -> Dot:
        """Create a dot colored by physics concept."""
        color_map = {
            "velocity":   COLOR_VELOCITY,
            "force":      COLOR_FORCE,
            "energy":     COLOR_ENERGY,
            "mass":       COLOR_MASS,
            "gravity":    COLOR_GRAVITY,
            "wavelength": COLOR_WAVELENGTH,
            "wave":       COLOR_WAVELENGTH,
            "time":       COLOR_TIME,
        }
        color = color_map.get(concept.lower(), COLOR_WHITE)
        return Dot(point=point, radius=radius, color=color)

    def semantic_arrow(self, start, end, concept: str = "force", **kwargs) -> Arrow:
        """Create an arrow colored by physics concept."""
        color_map = {
            "velocity":   COLOR_VELOCITY,
            "force":      COLOR_FORCE,
            "energy":     COLOR_ENERGY,
            "mass":       COLOR_MASS,
            "gravity":    COLOR_GRAVITY,
            "wavelength": COLOR_WAVELENGTH,
            "wave":       COLOR_WAVELENGTH,
            "time":       COLOR_TIME,
        }
        color = color_map.get(concept.lower(), COLOR_WHITE)
        return Arrow(start, end, color=color, **kwargs)

    # ── Atom anchor transitions ───────────────────────

    def show_atom_anchor(self, run_time: float = 0.5):
        """Fade in the atom brand anchor."""
        self.atom.set_opacity(1)
        self.play(FadeIn(self.atom, scale=0.5, run_time=run_time))

    def hide_atom_anchor(self, run_time: float = 0.5):
        """Fade out the atom brand anchor."""
        self.play(FadeOut(self.atom, scale=0.5, run_time=run_time))
        self.atom.set_opacity(0)

    def transition_with_atom(self, run_time: float = 1.0):
        """Show atom briefly during a scene transition."""
        self.show_atom_anchor(run_time=run_time * 0.3)
        self.wait(run_time * 0.4)
        self.hide_atom_anchor(run_time=run_time * 0.3)

    # ── Grid helpers ──────────────────────────────────

    def create_grid(self, rows: int = 10, cols: int = 10, cell_size: float = 0.5) -> VGroup:
        """Create a subtle background grid."""
        grid = VGroup()
        half_w = cols * cell_size / 2
        half_h = rows * cell_size / 2
        for i in range(rows + 1):
            y = -half_h + i * cell_size
            grid.add(Line(
                start=[-half_w, y, 0],
                end=[half_w, y, 0],
                color=COLOR_GRID,
                stroke_width=0.5,
                stroke_opacity=0.3,
            ))
        for j in range(cols + 1):
            x = -half_w + j * cell_size
            grid.add(Line(
                start=[x, -half_h, 0],
                end=[x, half_h, 0],
                color=COLOR_GRID,
                stroke_width=0.5,
                stroke_opacity=0.3,
            ))
        return grid
