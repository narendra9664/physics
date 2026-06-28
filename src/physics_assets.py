"""
Physics Visual Reels — Reusable 3D Physics Assets

Contains premium, lightweight 3D vector-drawn models (Planets, Suns, Black Holes)
for use in physics explainer videos. These render quickly and look highly mathematical.
"""

from manim import *
import numpy as np

# Semantics and neutrals (imported locally to avoid circular dependencies)
from visual_constants import COLOR_MASS, COLOR_VELOCITY, COLOR_FORCE, COLOR_WHITE, COLOR_MUTED

class Planet3D(VGroup):
    """A wireframe 3D planet with longitudinal and latitudinal grid rings.
    
    Creates a beautiful vector globe effect when rotated.
    """
    def __init__(self, radius: float = 0.5, color: str = COLOR_VELOCITY, num_rings: int = 4, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.color = color

        # 1. Base solid core (slightly translucent)
        self.core = Sphere(radius=radius, color=color)
        self.core.set_opacity(0.15)
        self.add(self.core)

        # 2. Longitudinal rings (vertical loops rotated around Z-axis)
        self.longitudes = VGroup()
        for i in range(num_rings):
            angle = i * (180 / num_rings) * DEGREES
            ring = Circle(radius=radius, color=color)
            ring.set_stroke(width=1.5, opacity=0.6)
            ring.rotate(angle, axis=UP)
            self.longitudes.add(ring)
        self.add(self.longitudes)

        # 3. Latitudinal rings (horizontal loops at different heights)
        self.latitudes = VGroup()
        lat_count = num_rings - 1
        for i in range(1, lat_count + 1):
            h = radius * np.cos(i * PI / (lat_count + 1))
            r_lat = radius * np.sin(i * PI / (lat_count + 1))
            ring = Circle(radius=r_lat, color=color)
            ring.set_stroke(width=1.2, opacity=0.45)
            ring.move_to([0, 0, h])
            self.latitudes.add(ring)
        self.add(self.latitudes)

    def rotate_globe(self, scene, run_time: float = 4.0, axis=OUT, rate_func=linear):
        """Play a smooth globe rotation animation."""
        scene.play(
            Rotate(self.longitudes, angle=PI, axis=axis, run_time=run_time, rate_func=rate_func),
            Rotate(self.latitudes, angle=PI, axis=axis, run_time=run_time, rate_func=rate_func),
        )


class Sun3D(VGroup):
    """A glowing star core with surrounding orbit flare loops."""
    def __init__(self, radius: float = 0.65, color: str = "#FFD166", **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.color = color

        # Inner solid core
        self.core = Sphere(radius=radius, color=color)
        self.core.set_opacity(0.85)
        self.add(self.core)

        # Subtle corona glow circles
        self.corona = VGroup()
        for offset in [1.1, 1.25, 1.4]:
            ring = Circle(radius=radius * offset, color=color)
            ring.set_stroke(width=1.0, opacity=0.25)
            # Tilt corona rings slightly to look 3D
            ring.rotate(30 * DEGREES, axis=RIGHT)
            ring.rotate(45 * DEGREES, axis=UP)
            self.corona.add(ring)
        self.add(self.corona)

    def pulsate(self, scene, run_time: float = 2.0, scale_factor: float = 1.08):
        """Simulate a glowing star pulsation."""
        scene.play(
            self.corona.animate.scale(scale_factor),
            run_time=run_time * 0.5,
            rate_func=rate_functions.ease_in_out_sine
        )
        scene.play(
            self.corona.animate.scale(1.0 / scale_factor),
            run_time=run_time * 0.5,
            rate_func=rate_functions.ease_in_out_sine
        )


class BlackHole3D(VGroup):
    """A black hole asset with a pitch-black core and a glowing accretion disk."""
    def __init__(self, radius: float = 0.5, accretion_color: str = "#FF6B6B", **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        
        # 1. Event horizon (solid pitch-black sphere)
        self.singularity = Sphere(radius=radius, color="#000000")
        self.singularity.set_opacity(1.0)
        self.add(self.singularity)

        # 2. Shadow border
        self.shadow = Circle(radius=radius * 1.05, color=COLOR_WHITE)
        self.shadow.set_stroke(width=2.5, opacity=0.8)
        self.add(self.shadow)

        # 3. Accretion Disk (multiple rings squashed and rotated)
        self.disk = VGroup()
        for i in range(5):
            r_offset = radius * (1.5 + i * 0.4)
            ring = Ellipse(width=r_offset * 2, height=r_offset * 0.4, color=accretion_color)
            ring.set_stroke(width=2.0 - i * 0.3, opacity=0.9 - i * 0.15)
            # Tilt accretion disk
            ring.rotate(25 * DEGREES, axis=RIGHT)
            self.disk.add(ring)
        self.add(self.disk)

    def rotate_disk(self, scene, run_time: float = 3.0):
        """Rotate the accretion disk around the black hole."""
        scene.play(
            Rotate(self.disk, angle=PI / 2, axis=OUT, run_time=run_time, rate_func=linear)
        )
