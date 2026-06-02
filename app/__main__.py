import sys
from pathlib import Path

# Make the top-level domey modules (polyhedron.py, geodesic.py, ...) importable.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import moderngl_window as mglw
from imgui_bundle import imgui
from moderngl_window.integrations.imgui_bundle import ModernglWindowRenderer

from .camera import orbit, view_proj, zoom
from .renderer import Renderer
from .state import AppState
from .ui import draw_ui


class GeodesicViewer(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "domey viewer"
    window_size = (1024, 768)
    resizable = True
    aspect_ratio = None
    samples = 4

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        imgui.create_context()
        self.imgui = ModernglWindowRenderer(self.wnd)
        self.state = AppState()
        self.renderer = Renderer(self.ctx)
        self._right_dragging = False

    def on_render(self, time: float, frame_time: float) -> None:
        self.renderer.ensure_geometry(self.state.geometry)

        aspect = self.wnd.viewport_width / max(1, self.wnd.viewport_height)
        mvp = view_proj(self.state.camera, aspect)

        self.renderer.draw(
            mvp_bytes=bytes(mvp.to_bytes()),
            geodesic=self.state.display.geodesic,
            polyhedron=self.state.display.polyhedron,
        )

        imgui.new_frame()
        draw_ui(self.state)
        imgui.render()
        self.imgui.render(imgui.get_draw_data())

    # --- input forwarding ---

    def on_resize(self, width: int, height: int) -> None:
        self.imgui.resize(width, height)

    def on_key_event(self, key, action, modifiers) -> None:
        self.imgui.key_event(key, action, modifiers)

    def on_mouse_position_event(self, x: int, y: int, dx: int, dy: int) -> None:
        self.imgui.mouse_position_event(x, y, dx, dy)

    def on_mouse_drag_event(self, x: int, y: int, dx: int, dy: int) -> None:
        self.imgui.mouse_drag_event(x, y, dx, dy)
        if self._right_dragging and not imgui.get_io().want_capture_mouse:
            orbit(self.state.camera, dx, dy)

    def on_mouse_scroll_event(self, x_offset: float, y_offset: float) -> None:
        self.imgui.mouse_scroll_event(x_offset, y_offset)
        if not imgui.get_io().want_capture_mouse:
            zoom(self.state.camera, y_offset)

    def on_mouse_press_event(self, x: int, y: int, button: int) -> None:
        self.imgui.mouse_press_event(x, y, button)
        if button == self.wnd.mouse.right:
            self._right_dragging = True

    def on_mouse_release_event(self, x: int, y: int, button: int) -> None:
        self.imgui.mouse_release_event(x, y, button)
        if button == self.wnd.mouse.right:
            self._right_dragging = False

    def on_unicode_char_entered(self, char: str) -> None:
        self.imgui.unicode_char_entered(char)


def main() -> None:
    mglw.run_window_config(GeodesicViewer)


if __name__ == "__main__":
    main()
