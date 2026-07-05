from imgui_bundle import imgui

from .state import AppState, ORDERS, SHAPES

_TWIST_MIN, _TWIST_MAX = -1.5708, 1.5708
_BOX_WIDTH = 120
_BOX_HEIGHT = 120


def _twist_slider(state: AppState) -> None:
    """Twist slider; scrolling the mouse wheel while hovering nudges it."""
    imgui.set_next_item_width(-1)
    changed, new_twist = imgui.slider_float(
        "##twist", state.geometry.twist_angle, _TWIST_MIN, _TWIST_MAX
    )
    wheel = imgui.get_io().mouse_wheel
    if imgui.is_item_hovered() and wheel != 0.0:
        step = (_TWIST_MAX - _TWIST_MIN) / 100.0
        new_twist = min(_TWIST_MAX, max(_TWIST_MIN,
                        state.geometry.twist_angle + wheel * step))
        changed = True
    if changed:
        state.set_geometry(twist_angle=new_twist)


def draw_ui(state: AppState) -> None:
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
