from pathlib import Path

import moderngl
import numpy as np

from .scene import GeometryBuffers, build_geometry
from .state import GeometryInputs

_SHADERS = Path(__file__).parent / "shaders"
_INITIAL_RESERVE = 4096 * 3 * 4  # 4096 vec3 floats; grows on demand


def _read(name: str) -> str:
    return (_SHADERS / name).read_text()


class _GLBuffer:
    """A growing VBO+VAO pair bound to a given program."""

    def __init__(self, ctx: moderngl.Context, prog: moderngl.Program) -> None:
        self.ctx = ctx
        self.vbo = ctx.buffer(reserve=_INITIAL_RESERVE, dynamic=True)
        self.vao = ctx.vertex_array(prog, [(self.vbo, "3f", "in_position")])
        self.vertex_count = 0

    def upload(self, data: np.ndarray) -> None:
        data = np.ascontiguousarray(data, dtype=np.float32)
        if data.nbytes > self.vbo.size:
            self.vbo.orphan(size=data.nbytes)
        self.vbo.write(data.tobytes())
        self.vertex_count = data.shape[0]

    def render(self, mode: int) -> None:
        if self.vertex_count > 0:
            self.vao.render(mode, vertices=self.vertex_count)


class Renderer:
    def __init__(self, ctx: moderngl.Context) -> None:
        self.ctx = ctx

        self.line_prog = ctx.program(
            vertex_shader=_read("line.vert"),
            fragment_shader=_read("line.frag"),
        )
        self._line_mvp = self.line_prog["u_mvp"]
        self._line_color = self.line_prog["u_color"]

        self.point_prog = ctx.program(
            vertex_shader=_read("point.vert"),
            fragment_shader=_read("point.frag"),
        )
        self._point_mvp = self.point_prog["u_mvp"]
        self._point_color = self.point_prog["u_color"]
        self._point_size = self.point_prog["u_point_size"]

        self.tri_prog = ctx.program(
            vertex_shader=_read("tri.vert"),
            fragment_shader=_read("tri.frag"),
        )
        self._tri_mvp = self.tri_prog["u_mvp"]
        self._tri_color = self.tri_prog["u_color"]

        self._edges = _GLBuffer(ctx, self.line_prog)
        self._arcs = _GLBuffer(ctx, self.line_prog)
        self._points = _GLBuffer(ctx, self.point_prog)
        self._faces = _GLBuffer(ctx, self.tri_prog)

        self._cached_inputs: GeometryInputs | None = None

    def ensure_geometry(self, inputs: GeometryInputs) -> None:
        if inputs == self._cached_inputs:
            return
        buffers = build_geometry(inputs)
        self._edges.upload(buffers.edge_vertices)
        self._arcs.upload(buffers.arc_vertices)
        self._points.upload(buffers.intersection_points)
        self._faces.upload(buffers.face_triangles)
        self._cached_inputs = inputs

    def draw(
        self,
        mvp_bytes: bytes,
        show_edges: bool,
        show_arcs: bool,
        show_intersections: bool,
        show_faces: bool,
    ) -> None:
        ctx = self.ctx
        ctx.enable(moderngl.DEPTH_TEST)
        ctx.enable(moderngl.PROGRAM_POINT_SIZE)
        ctx.clear(0.08, 0.09, 0.11, 1.0)

        if show_faces:
            # Translucent fills: blend with depth-test on but writes off so
            # face fragments don't occlude lines/points drawn later.
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
            ctx.depth_mask = False
            self._tri_mvp.write(mvp_bytes)
            self._tri_color.value = (0.30, 0.55, 0.90, 0.35)
            self._faces.render(moderngl.TRIANGLES)
            ctx.depth_mask = True
            ctx.disable(moderngl.BLEND)

        if show_edges or show_arcs:
            self._line_mvp.write(mvp_bytes)
            if show_edges:
                self._line_color.value = (0.40, 0.42, 0.48)
                self._edges.render(moderngl.LINES)
            if show_arcs:
                self._line_color.value = (0.95, 0.78, 0.30)
                self._arcs.render(moderngl.LINES)

        if show_intersections:
            self._point_mvp.write(mvp_bytes)
            self._point_color.value = (0.30, 0.85, 0.95)
            self._point_size.value = 9.0
            self._points.render(moderngl.POINTS)
