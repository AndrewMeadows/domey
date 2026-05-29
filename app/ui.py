from imgui_bundle import imgui

from .state import AppState, SHAPES


def draw_ui(state: AppState) -> None:
    imgui.set_next_window_pos(imgui.ImVec2(10, 10), imgui.Cond_.first_use_ever.value)
    imgui.set_next_window_size(imgui.ImVec2(280, 220), imgui.Cond_.first_use_ever.value)
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

    changed, new_twist = imgui.slider_float(
        "twist", state.geometry.twist_angle, -1.5708, 1.5708
    )
    if changed:
        state.set_geometry(twist_angle=new_twist)

    imgui.separator()
    _, state.display.show_base_polyhedron = imgui.checkbox(
        "base edges", state.display.show_base_polyhedron
    )
    _, state.display.show_arcs = imgui.checkbox(
        "twisted arcs", state.display.show_arcs
    )
    _, state.display.show_intersections = imgui.checkbox(
        "intersections", state.display.show_intersections
    )
    _, state.display.show_faces = imgui.checkbox(
        "face fills", state.display.show_faces
    )

    imgui.end()
