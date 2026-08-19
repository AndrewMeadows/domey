from pathlib import Path

import moderngl
import numpy as np

from .scene import GeometryBuffers, build_geometry
from .state import GeometryInputs
from .colors import ARC_COLORS, FACE_COLORS

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
        self._geo_edge_groups = [_GLBuffer(ctx, self.line_prog)
                                 for _ in ARC_COLORS]
        self._geo_face_groups = [_GLBuffer(ctx, self.tri_prog)
                                 for _ in FACE_COLORS]
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
        for buffer, data in zip(self._geo_edge_groups, buffers.geodesic.edge_groups):
            buffer.upload(data)
        # Face-group count and identities can change with twist/topology. Clear
        # every unused buffer as well as uploading current groups; otherwise
        # old triangles remain drawable after a group disappears.
        empty_faces = np.empty((0, 3), dtype=np.float32)
        for index, buffer in enumerate(self._geo_face_groups):
            data = (buffers.geodesic.face_groups[index]
                    if index < len(buffers.geodesic.face_groups)
                    else empty_faces)
            buffer.upload(data)
        self._geo_points.upload(buffers.geodesic.vertices)
        self._poly_edges.upload(buffers.polyhedron.edges)
        self._poly_faces.upload(buffers.polyhedron.faces)
        self._poly_points.upload(buffers.polyhedron.vertices)
        self._cached_inputs = inputs

    # Per-object colors so the two objects stay distinguishable when both show.
    # The geodesic is the outer surface: translucent (_GEO_FACE) when the
    # polyhedron is enabled so it stays visible inside, but fully opaque
    # (_GEO_FACE_OPAQUE) when the geodesic is shown on its own.
    _GEO_FACE = (0.30, 0.55, 0.90, 0.65)
    _GEO_FACE_OPAQUE = (0.30, 0.55, 0.90, 1.0)
    _GEO_EDGE = ARC_COLORS[0]
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
            # Translucent only when there's a polyhedron behind it to reveal.
            geo_face = self._GEO_FACE if polyhedron.enabled else self._GEO_FACE_OPAQUE
            objects.append((geodesic, self._geo_face_groups, self._geo_edges, self._geo_points,
                            geo_face, self._GEO_EDGE, self._GEO_POINT))
        if polyhedron.enabled:
            objects.append((polyhedron, (self._poly_faces,), self._poly_edges, self._poly_points,
                            self._POLY_FACE, self._POLY_EDGE, self._POLY_POINT))

        # Faces in two passes so a translucent object (the geodesic) blends over
        # whatever is behind it, revealing the opaque polyhedron nested inside.
        # Cull back faces throughout: both objects are wound CCW as seen from
        # outside the sphere, so away-facing triangles never draw and can't blend
        # over the near side of a translucent shell.
        self._tri_mvp.write(mvp_bytes)
        ctx.enable(moderngl.CULL_FACE)

        # 1) Opaque faces first, depth writes on, so later geometry is correctly
        #    occluded and translucent faces have something to blend against.
        for flags, faces, _e, _p, face_color, _ec, _pc in objects:
            if flags.show_faces and face_color[3] >= 1.0:
                for face_index, face_buffer in enumerate(faces):
                    color = (FACE_COLORS[face_index] + (face_color[3],)
                             if faces is self._geo_face_groups else face_color)
                    self._tri_color.value = color
                    face_buffer.render(moderngl.TRIANGLES)

        # 2) Translucent faces last, with blending on and depth writes off so the
        #    surface doesn't occlude itself or hide the inner object; depth test
        #    still keeps faces behind the opaque geometry from showing through.
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        ctx.depth_mask = False
        for flags, faces, _e, _p, face_color, _ec, _pc in objects:
            if flags.show_faces and face_color[3] < 1.0:
                for face_index, face_buffer in enumerate(faces):
                    color = (FACE_COLORS[face_index] + (face_color[3],)
                             if faces is self._geo_face_groups else face_color)
                    self._tri_color.value = color
                    face_buffer.render(moderngl.TRIANGLES)
        ctx.depth_mask = True
        ctx.disable(moderngl.BLEND)
        ctx.disable(moderngl.CULL_FACE)

        self._line_mvp.write(mvp_bytes)
        for flags, _f, edges, _p, _fc, edge_color, _pc in objects:
            if flags.show_edges:
                if edges is self._geo_edges:
                    for color, group_edges in zip(ARC_COLORS, self._geo_edge_groups):
                        self._line_color.value = color
                        group_edges.render(moderngl.LINES)
                else:
                    self._line_color.value = edge_color
                    edges.render(moderngl.LINES)

        self._point_mvp.write(mvp_bytes)
        self._point_size.value = 9.0
        for flags, _f, _e, points, _fc, _ec, point_color in objects:
            if flags.show_vertices:
                self._point_color.value = point_color
                points.render(moderngl.POINTS)
