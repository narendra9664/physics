"""
Physics Visual Reels — Atom Anchor

Reusable brand element: a small atom icon (nucleus + orbiting ring)
that appears in corners or transitions for brand recognition.
Inspired by Kurzgesagt-style warmth without building a character library.
"""

from manim import (
    VGroup, Dot, Circle, Ellipse,
    FadeIn, FadeOut, Rotate,
    PI, ORIGIN, RIGHT, UP,
    rate_functions,
)
from visual_constants import (
    ATOM_NUCLEUS_RADIUS,
    ATOM_ORBIT_RADIUS,
    ATOM_COLOR,
    COLOR_WHITE,
)


class AtomAnchor(VGroup):
    """Small atom icon for brand recognition.
    
    Usage:
        atom = AtomAnchor()
        atom.to_corner(DR, buff=0.4)  # bottom-right corner
        self.play(FadeIn(atom, scale=0.5))
    """

    def __init__(
        self,
        nucleus_radius: float = ATOM_NUCLEUS_RADIUS,
        orbit_radius: float = ATOM_ORBIT_RADIUS,
        color: str = ATOM_COLOR,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # Nucleus — a small filled dot
        self.nucleus = Dot(
            point=ORIGIN,
            radius=nucleus_radius,
            color=color,
        )
        self.nucleus.set_fill(color, opacity=1.0)

        # Orbit ring — a thin ellipse
        self.orbit = Ellipse(
            width=orbit_radius * 2,
            height=orbit_radius * 0.7,  # slightly squashed for 3D feel
            color=color,
            stroke_width=1.5,
            stroke_opacity=0.6,
        )

        # Electron — a tiny dot on the orbit path
        self.electron = Dot(
            point=self.orbit.point_from_proportion(0),
            radius=nucleus_radius * 0.5,
            color=COLOR_WHITE,
        )
        self.electron.set_fill(COLOR_WHITE, opacity=0.9)

        self.add(self.orbit, self.nucleus, self.electron)

    def animate_orbit(self, scene, run_time: float = 2.0, loops: int = 1):
        """Animate the electron orbiting the nucleus."""
        from manim import MoveAlongPath
        for _ in range(loops):
            scene.play(
                MoveAlongPath(self.electron, self.orbit, run_time=run_time),
                rate_func=rate_functions.linear,
            )

    def fade_in(self, scene, run_time: float = 0.5):
        """Fade the atom anchor into the scene."""
        scene.play(FadeIn(self, scale=0.5, run_time=run_time))

    def fade_out(self, scene, run_time: float = 0.5):
        """Fade the atom anchor out of the scene."""
        scene.play(FadeOut(self, scale=0.5, run_time=run_time))
