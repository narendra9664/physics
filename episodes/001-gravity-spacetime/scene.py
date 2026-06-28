"""
Physics Visual Reels — Episode 001: Gravity & Spacetime Curvature

A premium 3D math-aesthetic composition inspired by @beyond.the.math,
synchronized with the SteffanNeural voiceover (55.3s total).
Fixes all text overlaps by using temporary labels and HUD-safe spacing.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from manim import *
from render_base import PhysicsReelScene
from visual_constants import (
    COLOR_GRID, COLOR_MASS, COLOR_GRAVITY, COLOR_VELOCITY, COLOR_FORCE,
    COLOR_WHITE, COLOR_MUTED, FONT_BODY
)

class GravitySpacetimeScene(PhysicsReelScene):
    def construct(self):
        # Setup camera and background specs
        self.setup_scene()
        
        # Start in flat 2D orthographic camera view
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)

        # 3D Spacetime Funnel Warp Function
        def spacetime_warp_3d(p):
            x, y, z = p
            r = np.linalg.norm([x, y])
            if r < 0.1:
                return np.array([x, y, -2.2])
            # Dip in the Z direction based on distance from center
            dip = -2.2 / (1.0 + (r / 1.3)**2)
            return np.array([x, y, dip])

        # =========================================================================
        # BEAT 1: HOOK (0.0s - 6.0s)
        # "You aren't standing still right now. You're constantly falling, even on solid ground."
        # =========================================================================
        
        # Draw a stylized Earth and a person standing on it
        earth_circle = Circle(radius=2.0, color=COLOR_VELOCITY).set_fill(COLOR_VELOCITY, opacity=0.15)
        earth_circle.move_to(DOWN * 1.5)
        
        person_dot = Dot(point=earth_circle.get_top(), radius=0.12, color=COLOR_WHITE)
        person_label = self.show_label("you", color=COLOR_WHITE).next_to(person_dot, UP, buff=0.15)
        
        self.add_fixed_in_frame_mobjects(person_label)
        self.play(FadeIn(earth_circle), FadeIn(person_dot), FadeIn(person_label), run_time=1.0)
        self.wait(1.0)

        # Animate "falling" (dropping the person towards the center)
        self.play(
            person_dot.animate.move_to(earth_circle.get_center()),
            FadeOut(person_label),
            rate_func=rate_functions.ease_in_quad,
            run_time=1.2
        )
        self.wait(0.2)

        # Clear and prepare flat spacetime grid
        self.play(FadeOut(person_dot), FadeOut(earth_circle), run_time=0.4)
        
        flat_grid = self.create_discretized_grid(rows=14, cols=10, cell_size=0.6)
        self.play(Create(flat_grid, run_time=1.0))
        self.wait(0.2)


        # =========================================================================
        # BEAT 2: PROBLEM (6.0s - 12.5s)
        # "We usually think gravity is a mysterious force pulling things down. But what if there's no 'pull' at all?"
        # =========================================================================
        
        # Central mass (Sun) and orbital body (Earth)
        sun_dot = Dot(point=ORIGIN, radius=0.45, color=COLOR_MASS)
        sun_label = self.show_label("Sun", color=COLOR_MASS).next_to(sun_dot, UP, buff=0.25)
        
        earth_dot = Dot(point=DOWN * 2.2, radius=0.15, color=COLOR_VELOCITY)
        earth_label = self.show_label("Earth", color=COLOR_VELOCITY).next_to(earth_dot, RIGHT, buff=0.2)
        
        self.play(
            FadeIn(sun_dot), FadeIn(sun_label),
            FadeIn(earth_dot), FadeIn(earth_label),
            run_time=1.0
        )
        self.wait(0.5)

        # Pull force arrow
        pull_arrow = self.semantic_arrow(start=earth_dot.get_center(), end=sun_dot.get_center(), concept="force")
        pull_label = self.show_label("pull force", color=COLOR_FORCE).next_to(pull_arrow, LEFT, buff=0.2)
        
        self.play(GrowArrow(pull_arrow), FadeIn(pull_label), run_time=0.8)
        self.wait(0.8)

        # Red cross over force arrow
        cross_line1 = Line(start=pull_arrow.get_center() + [-0.5, -0.5, 0], end=pull_arrow.get_center() + [0.5, 0.5, 0], color=COLOR_FORCE, stroke_width=6)
        cross_line2 = Line(start=pull_arrow.get_center() + [-0.5, 0.5, 0], end=pull_arrow.get_center() + [0.5, -0.5, 0], color=COLOR_FORCE, stroke_width=6)
        
        self.play(Create(cross_line1), Create(cross_line2), run_time=0.6)
        self.wait(0.6)

        # Clear pull force elements and labels to avoid clutter
        self.play(
            FadeOut(pull_arrow), FadeOut(pull_label),
            FadeOut(cross_line1), FadeOut(cross_line2),
            FadeOut(sun_label), FadeOut(earth_label),
            run_time=0.6
        )
        self.wait(0.2)


        # =========================================================================
        # BEAT 3: EXPLANATION (12.5s - 25.6s)
        # "Massive objects, like planets or stars, don't just sit in space. They actually bend and warp..."
        # =========================================================================
        
        # HUD Theory Label
        theory_label = self.show_theory_name("General Relativity")
        theory_label.to_edge(UP, buff=0.8)
        self.add_fixed_in_frame_mobjects(theory_label)
        self.play(Write(theory_label, run_time=1.2))
        
        # 3D Sun Sphere
        sun_3d = Sphere(radius=0.55, color=COLOR_MASS)
        sun_3d.move_to([0, 0, -0.45])

        # Warp grid in 3D and tilt camera
        warped_grid = flat_grid.copy().apply_function(spacetime_warp_3d)

        self.move_camera(
            phi=68 * DEGREES,
            theta=-35 * DEGREES,
            added_anims=[
                FadeOut(sun_dot),
                FadeIn(sun_3d, scale=0.5),
                Transform(flat_grid, warped_grid),
            ],
            run_time=2.2
        )
        self.wait(1.0)

        # Highlight spacetime fabric
        fabric_label = self.show_label("warped spacetime", color=COLOR_GRAVITY)
        fabric_label.to_edge(DL, buff=0.8)
        self.add_fixed_in_frame_mobjects(fabric_label)
        
        self.play(FadeIn(fabric_label, shift=RIGHT * 0.2), run_time=0.8)
        self.wait(1.5)

        # Passing object showing curved spacetime path
        passing_object = Dot(radius=0.12, color=COLOR_VELOCITY)
        
        # 3D curved trajectory near gravity well
        x_vals = np.linspace(-4, 4, 80)
        points_3d = []
        for x in x_vals:
            y = 1.2 + 0.125 * x**2
            p_flat = np.array([x, y, 0])
            p_warped = spacetime_warp_3d(p_flat)
            points_3d.append(p_warped)

        geodesic_path = VMobject()
        geodesic_path.set_points_as_corners(points_3d)
        geodesic_path.make_smooth()

        self.play(FadeIn(passing_object))
        self.play(
            MoveAlongPath(passing_object, geodesic_path, rate_func=rate_functions.ease_in_out_sine),
            run_time=3.5
        )
        
        # Clean Beat 3 labels and passing object
        self.play(
            FadeOut(passing_object),
            FadeOut(fabric_label),
            run_time=0.6
        )
        self.wait(0.5)


        # =========================================================================
        # BEAT 4: EXAMPLE (25.6s - 38.0s)
        # "So, Earth doesn't orbit the Sun because the Sun 'pulls' it. Instead, Earth is simply following..."
        # =========================================================================
        
        # 3D Orbit path for Earth at funnel depth
        orbit_radius = 2.2
        orbit_z = -2.2 / (1.0 + (orbit_radius / 1.3)**2)
        
        orbit_circle = Circle(radius=orbit_radius, color=COLOR_MUTED)
        orbit_circle.set_stroke(width=1.5, opacity=0.45)
        orbit_circle.move_to([0, 0, orbit_z])
        self.play(Create(orbit_circle), run_time=1.0)

        # Animate Earth orbiting Sun
        orbiting_earth = Dot(point=orbit_circle.point_from_proportion(0), radius=0.15, color=COLOR_VELOCITY)
        self.play(FadeIn(orbiting_earth))

        # Satisfying ambient camera rotation during orbit
        self.begin_ambient_camera_rotation(rate=0.08)

        self.play(
            MoveAlongPath(orbiting_earth, orbit_circle),
            run_time=4.5,
            rate_func=rate_functions.linear
        )
        self.play(
            MoveAlongPath(orbiting_earth, orbit_circle),
            run_time=3.5,
            rate_func=rate_functions.linear
        )

        self.stop_ambient_camera_rotation()
        self.wait(0.4)

        # Fade out Beat 4 elements
        self.play(
            FadeOut(orbiting_earth), FadeOut(orbit_circle),
            FadeOut(sun_3d), FadeOut(flat_grid), FadeOut(theory_label),
            run_time=0.8
        )
        self.wait(0.5)


        # =========================================================================
        # BEAT 5: CORRECTION (38.0s - 49.3s)
        # "So, gravity isn't a mysterious pulling force. You're just following the path..."
        # =========================================================================
        
        # Reset camera back to flat 2D
        self.move_camera(phi=0, theta=-90 * DEGREES, run_time=1.0)

        correction_title = self.show_label("Spacetime Geometry", color=COLOR_GRAVITY)
        correction_title.to_edge(UP, buff=0.8)
        self.add_fixed_in_frame_mobjects(correction_title)
        self.play(FadeIn(correction_title))

        # Show flat grid line warping to a curve as a mass moves past
        measuring_line = Line(start=[-3.5, -1, 0], end=[3.5, -1, 0], color=COLOR_MUTED)
        self.play(Create(measuring_line), run_time=0.8)
        
        mass_pass = Dot(point=[-4, 0, 0], radius=0.3, color=COLOR_MASS)
        self.play(FadeIn(mass_pass))
        
        # Curved line deformation
        curved_line = VMobject()
        curved_points = [
            np.array([x, -1.0 - 0.7 / (1.0 + (x / 1.2)**2), 0])
            for x in np.linspace(-3.5, 3.5, 60)
        ]
        curved_line.set_points_as_corners(curved_points)
        curved_line.set_color(COLOR_GRAVITY)
        curved_line.set_stroke(width=2.5)

        self.play(
            mass_pass.animate.move_to([4, 0, 0]),
            Transform(measuring_line, curved_line),
            run_time=2.2,
            rate_func=rate_functions.ease_in_out_sine
        )
        self.wait(0.5)

        # Clear elements
        self.play(
            FadeOut(mass_pass), FadeOut(measuring_line), FadeOut(correction_title),
            run_time=0.6
        )

        # HUD Einstein Field Equations
        einstein_eq = self.show_formula(r"G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}")
        einstein_eq.move_to(UP * 1.5)
        
        eq_label = self.show_label("Einstein Field Equations", color=COLOR_MUTED)
        eq_label.next_to(einstein_eq, DOWN, buff=0.35)
        
        self.add_fixed_in_frame_mobjects(einstein_eq, eq_label)
        self.play(Write(einstein_eq), FadeIn(eq_label, shift=DOWN * 0.1), run_time=2.0)
        self.wait(1.5)

        self.play(FadeOut(einstein_eq), FadeOut(eq_label), run_time=0.6)
        self.wait(0.2)

        self.transition_with_atom(run_time=1.1)


        # =========================================================================
        # BEAT 6: CTA (49.3s - 55.3s)
        # "Send this to someone who loves mind-bending ideas and wants to see..."
        # =========================================================================
        
        cta_text = self.show_theory_name("Share The Loop")
        cta_text.move_to(UP * 1.5)
        
        cta_sub = self.show_label("Send to a friend who loves physics", color=COLOR_MUTED)
        cta_sub.scale(0.85)
        cta_sub.next_to(cta_text, DOWN, buff=0.3)

        self.add_fixed_in_frame_mobjects(cta_text, cta_sub)
        self.play(FadeIn(cta_text, shift=UP * 0.2), FadeIn(cta_sub, shift=UP * 0.2), run_time=1.2)
        self.wait(0.4)

        brand_atom = self.atom
        brand_atom.move_to(DOWN * 1.5)
        self.add_fixed_in_frame_mobjects(brand_atom)
        
        self.play(brand_atom.animate.set_opacity(1.0).scale(2.5), run_time=1.0)
        brand_atom.animate_orbit(self, run_time=1.5, loops=2)
        self.wait(0.8)

        # Clear final
        self.play(FadeOut(cta_text), FadeOut(cta_sub), FadeOut(brand_atom), run_time=0.8)
        self.wait(0.4)


    # Discretized grid helper for curving lines smoothly
    def create_discretized_grid(self, rows=14, cols=10, cell_size=0.6, color=COLOR_GRID) -> VGroup:
        grid = VGroup()
        half_w = cols * cell_size / 2
        half_h = rows * cell_size / 2
        
        # Horizontal lines
        for i in range(rows + 1):
            y = -half_h + i * cell_size
            line = VMobject()
            points = [np.array([x, y, 0]) for x in np.linspace(-half_w, half_w, 60)]
            line.set_points_as_corners(points)
            line.set_color(color)
            line.set_stroke(width=1.2, opacity=0.35)
            grid.add(line)
            
        # Vertical lines
        for j in range(cols + 1):
            x = -half_w + j * cell_size
            line = VMobject()
            points = [np.array([x, y, 0]) for y in np.linspace(-half_h, half_h, 60)]
            line.set_points_as_corners(points)
            line.set_color(color)
            line.set_stroke(width=1.2, opacity=0.35)
            grid.add(line)
            
        return grid
