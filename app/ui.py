from imgui_bundle import imgui

from .state import AppState, ORDERS, SHAPES
from .colors import ARC_COLORS, FACE_COLORS

_TWIST_MIN, _TWIST_MAX = -1.5708, 1.5708
_TWIST_WHEEL_STEPS = 100 # coarse tuning
_TWIST_KEY_STEPS = 1000  # fine tuning
_BOX_WIDTH = 120
_BOX_HEIGHT = 120


def _arc_part_number(group):
    """Format an arc group using its compact, human-readable part number."""
    intersections = []
    for distance, arc_id, angle in zip(
        group.intersection_distances,
        group.intersection_arcs,
        group.intersection_angles,
    ):
        percentage = 100.0 * distance / group.arc_length
        intersections.append(
            f"{percentage:.6f}-{arc_id or '—'}-{angle:.6f}"
        )

    # The current geometry normally has two intersections. Keep the format
    # stable if a degenerate or future arc group has fewer than two.
    missing = "—-—-—"
    while len(intersections) < 2:
        intersections.append(missing)

    return (
        f"{group.count} {group.id}=0.0-{group.start_endpoint_arc or '—'}--"
        f"{intersections[0]}--{intersections[1]}--"
        f"100.0-{group.end_endpoint_arc or '—'}=({group.arc_length:.6f})"
    )


def _draw_arcs_window(geodesic) -> None:
    imgui.set_next_window_pos(imgui.ImVec2(360, 10), imgui.Cond_.first_use_ever.value)
    imgui.set_next_window_size(imgui.ImVec2(650, 420), imgui.Cond_.first_use_ever.value)
    imgui.begin("Geometry")
    if imgui.begin_tab_bar("geometry_tabs"):
        if imgui.begin_tab_item_simple("Arcs"):
            imgui.text("part number")
            imgui.separator()
            for group_index, group in enumerate(geodesic.getArcGroups()):
                color = ARC_COLORS[min(group_index, len(ARC_COLORS) - 1)]
                imgui.text_colored(imgui.ImVec4(*color, 1.0), _arc_part_number(group))
            imgui.end_tab_item()
        if imgui.begin_tab_item_simple("Faces"):
            imgui.text("part number (count)")
            imgui.separator()
            for group in geodesic.getFaceGroups():
                parts = ".".join(f"{radians:.6f}" for radians in group.parts)
                color = FACE_COLORS[group.id % len(FACE_COLORS)]
                imgui.text_colored(imgui.ImVec4(*color, 1.0),
                                   f"{group.count} {group.id}={group.face_type}:{parts}")
            imgui.end_tab_item()
        imgui.end_tab_bar()
    imgui.end()


def _twist_slider(state: AppState) -> None:
    """Adjust twist coarsely with the wheel and finely with Up/Down."""
    imgui.set_next_item_width(-1)
    changed, new_twist = imgui.slider_float(
        "##twist", state.geometry.twist_angle, _TWIST_MIN, _TWIST_MAX
    )
    wheel = imgui.get_io().mouse_wheel
    if imgui.is_item_hovered():
        delta = wheel * ((_TWIST_MAX - _TWIST_MIN) / _TWIST_WHEEL_STEPS)
        delta += imgui.is_key_pressed(imgui.Key.up_arrow) * (
            (_TWIST_MAX - _TWIST_MIN) / _TWIST_KEY_STEPS
        )
        delta -= imgui.is_key_pressed(imgui.Key.down_arrow) * (
            (_TWIST_MAX - _TWIST_MIN) / _TWIST_KEY_STEPS
        )
        if delta != 0.0:
            new_twist = min(_TWIST_MAX, max(_TWIST_MIN,
                            state.geometry.twist_angle + delta))
            changed = True
    if changed:
        state.set_geometry(twist_angle=new_twist)


def draw_ui(state: AppState, geodesic=None) -> None:
    imgui.set_next_window_pos(imgui.ImVec2(10, 10), imgui.Cond_.first_use_ever.value)
    imgui.set_next_window_size(imgui.ImVec2(340, 260), imgui.Cond_.first_use_ever.value)
    imgui.begin("Geodesic")

    current = state.geometry.shape_name
    if imgui.begin_combo("shape", current):
        for name in SHAPES:
            selected = name == current
            if imgui.selectable(name, selected)[0]:
                state.set_geometry(shape_name=name)
            if selected:
                imgui.set_item_default_focus()
        imgui.end_combo()

    current_order = state.geometry.order
    if imgui.begin_combo("order", str(current_order)):
        for value in ORDERS:
            selected = value == current_order
            if imgui.selectable(str(value), selected)[0]:
                state.set_geometry(order=value)
            if selected:
                imgui.set_item_default_focus()
        imgui.end_combo()

    imgui.separator()

    # Two side-by-side boxes: polyhedron on the left, geodesic on the right. The
    # geodesic box also holds the twist slider.
    box_size = imgui.ImVec2(_BOX_WIDTH, _BOX_HEIGHT + 28)

    imgui.begin_child("polyhedron_box", box_size, True)
    imgui.push_id("polyhedron_box")
    _, state.display.polyhedron.enabled = imgui.checkbox(
        "polyhedron", state.display.polyhedron.enabled
    )
    imgui.separator()
    _, state.display.polyhedron.show_vertices = imgui.checkbox(
        "vertices", state.display.polyhedron.show_vertices
    )
    _, state.display.polyhedron.show_edges = imgui.checkbox(
        "edges", state.display.polyhedron.show_edges
    )
    _, state.display.polyhedron.show_faces = imgui.checkbox(
        "faces", state.display.polyhedron.show_faces
    )
    imgui.pop_id()
    imgui.end_child()
    imgui.same_line()

    imgui.begin_child("geodesic_box", box_size, True)
    imgui.push_id("geodesic_box")
    _, state.display.geodesic.enabled = imgui.checkbox(
        "geodesic", state.display.geodesic.enabled
    )
    imgui.text("twist")
    _twist_slider(state)
    imgui.separator()
    _, state.display.geodesic.show_vertices = imgui.checkbox(
        "vertices", state.display.geodesic.show_vertices
    )
    _, state.display.geodesic.show_edges = imgui.checkbox(
        "edges", state.display.geodesic.show_edges
    )
    _, state.display.geodesic.show_faces = imgui.checkbox(
        "faces", state.display.geodesic.show_faces
    )
    imgui.pop_id()
    imgui.end_child()

    imgui.end()
    if geodesic is not None:
        _draw_arcs_window(geodesic)
