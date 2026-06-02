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

        self.tri_prog = ctx.program(
            vertex_shader=_read("tri.vert"),
            fragment_shader=_read("tri.frag"),
        )
        self._tri_mvp = self.tri_prog["u_mvp"]
        self._tri_color = self.tri_prog["u_color"]

        self.point_prog = ctx.program(
            vertex_shader=_read("point.vert"),
            fragment_shader=_read("point.frag"),
        )
        self._point_mvp = self.point_prog["u_mvp"]
        self._point_color = self.point_prog["u_color"]
        self._point_size = self.point_prog["u_point_size"]

        # One buffer set per object (geodesic, polyhedron); each has edges,
        # faces and vertices.
        self._geo_edges = _GLBuffer(ctx, self.line_prog)
        self._geo_faces = _GLBuffer(ctx, self.tri_prog)
        self._geo_points = _GLBuffer(ctx, self.point_prog)
        self._poly_edges = _GLBuffer(ctx, self.line_prog)
        self._poly_faces = _GLBuffer(ctx, self.tri_prog)
        self._poly_points = _GLBuffer(ctx, self.point_prog)

        self._cached_inputs: GeometryInputs | None = None

    def ensure_geometry(self, inputs: GeometryInputs) -> None:
        if inputs == self._cached_inputs:
            return
        buffers = build_geometry(inputs)
        self._geo_edges.upload(buffers.geodesic.edges)
        self._geo_faces.upload(buffers.geodesic.faces)
        self._geo_points.upload(buffers.geodesic.vertices)
        self._poly_edges.upload(buffers.polyhedron.edges)
        self._poly_faces.upload(buffers.polyhedron.faces)
        self._poly_points.upload(buffers.polyhedron.vertices)
        self._cached_inputs = inputs

    # Per-object colors so the two objects stay distinguishable when both show.
    _GEO_FACE = (0.30, 0.55, 0.90, 1.0)
    _GEO_EDGE = (0.95, 0.78, 0.30)
    _GEO_POINT = (0.30, 0.85, 0.95)
    _POLY_FACE = (0.55, 0.50, 0.40, 1.0)
    _POLY_EDGE = (0.55, 0.57, 0.62)
    _POLY_POINT = (0.95, 0.55, 0.45)

    def draw(self, mvp_bytes: bytes, geodesic, polyhedron) -> None:
        """Render the enabled objects. `geodesic` and `polyhedron` are
        ObjectDisplay-like flags (enabled / show_vertices / show_edges / show_faces)."""
        ctx = self.ctx
        ctx.enable(moderngl.DEPTH_TEST)
        ctx.enable(moderngl.PROGRAM_POINT_SIZE)
        ctx.clear(0.08, 0.09, 0.11, 1.0)

        # (flags, faces, edges, points, face_color, edge_color, point_color)
        objects = []
        if geodesic.enabled:
            objects.append((geodesic, self._geo_faces, self._geo_edges, self._geo_points,
                            self._GEO_FACE, self._GEO_EDGE, self._GEO_POINT))
        if polyhedron.enabled:
            objects.append((polyhedron, self._poly_faces, self._poly_edges, self._poly_points,
                            self._POLY_FACE, self._POLY_EDGE, self._POLY_POINT))

        # Opaque faces first (depth writes on) so edges and vertices drawn after
        # are depth-tested against the surfaces and hidden on the far side.
        self._tri_mvp.write(mvp_bytes)
        for flags, faces, _e, _p, face_color, _ec, _pc in objects:
            if flags.show_faces:
                self._tri_color.value = face_color
                faces.render(moderngl.TRIANGLES)

        self._line_mvp.write(mvp_bytes)
        for flags, _f, edges, _p, _fc, edge_color, _pc in objects:
            if flags.show_edges:
                self._line_color.value = edge_color
                edges.render(moderngl.LINES)

        self._point_mvp.write(mvp_bytes)
        self._point_size.value = 9.0
        for flags, _f, _e, points, _fc, _ec, point_color in objects:
            if flags.show_vertices:
                self._point_color.value = point_color
                points.render(moderngl.POINTS)
