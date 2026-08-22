"""Colors shared by the 3-D renderer and the ImGui overlays."""

# The order is the order of the unique arc groups shown in the Arcs window.
ARC_COLORS = (
    (0.95, 0.78, 0.30),  # existing default
    (0.35, 0.85, 0.45),  # green
    (0.90, 0.35, 0.75),  # magenta
    (0.95, 0.50, 0.15),  # orange
    (0.20, 0.75, 0.90),  # cyan
    (0.55, 0.35, 0.90),  # violet
    (0.75, 0.90, 0.25),  # lime
    (0.95, 0.35, 0.40),  # coral
    (0.25, 0.55, 0.95),  # blue
    (0.80, 0.45, 0.90),  # lavender
)

# Face colors deliberately use a separate warm/earthy palette so face groups
# remain distinguishable from the arc colors in both the UI and the renderer.
FACE_COLORS = (
    (0.95, 0.35, 0.25),
    (0.95, 0.60, 0.20),
    (0.80, 0.35, 0.15),
    (0.70, 0.25, 0.35),
    (0.60, 0.40, 0.20),
    (0.90, 0.45, 0.55),
    (0.75, 0.55, 0.25),
    (0.55, 0.30, 0.20),
    (0.85, 0.25, 0.60),
    (0.65, 0.45, 0.35),
    (0.95, 0.70, 0.35),
    (0.50, 0.25, 0.40),
    (0.80, 0.50, 0.40),
    (0.70, 0.30, 0.55),
    (0.90, 0.40, 0.30),
    (0.60, 0.55, 0.30),
    (0.75, 0.40, 0.25),
)
