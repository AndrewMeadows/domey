import math
from dataclasses import dataclass

import numpy as np
from pyglm import glm

from geodesics import Geodesic

from .state import GeometryInputs

ARC_SAMPLES = 24          # samples along each edge arc (>= 2)
FACE_SUBDIVISIONS = 3     # recursive splits per face triangle; 0 = flat

# Radial layering for the geodesic, drawn just outside the unit sphere so that
# faces occlude the inner polyhedron, arcs stay visible above the faces, and
# vertices stay visible above everything on the near-facing side.
GEO_FACE_RADIUS = 1.001
GEO_ARC_RADIUS = 1.003
GEO_VERTEX_RADIUS = 1.006


@dataclass
class ObjectBuffers:
    """One renderable object's three element buffers."""
    edges: np.ndarray       # float32, (E, 3), GL_LINES pairs
    faces: np.ndarray       # float32, (T, 3), GL_TRIANGLES
    vertices: np.ndarray    # float32, (V, 3), GL_POINTS


@dataclass
class GeometryBuffers:
    geodesic: ObjectBuffers
    polyhedron: ObjectBuffers


_geodesic_cache: dict[tuple[str, int], Geodesic] = {}


def _get_geodesic(shape_name: str, twist: float, order: int) -> Geodesic:
    # Order changes the base polyhedron, which is built in Geodesic.__init__, so
    # cache per (shape, order) rather than rebuilding the same one each frame.
    key = (shape_name, order)
    g = _geodesic_cache.get(key)
    if g is None:
        g = Geodesic(shape_name, order)
        _geodesic_cache[key] = g
    g.setTwistAngle(twist)
    return g


def _slerp(a: glm.vec3, b: glm.vec3, t: float) -> glm.vec3:
    """Spherical interpolation between two unit vectors; result is on the sphere."""
    dot = max(-1.0, min(1.0, glm.dot(a, b)))
    omega = math.acos(dot)
    if omega < 1e-6:
        # Nearly coincident: linear blend is safe and avoids divide-by-zero.
        return glm.normalize(a + t * (b - a))
    sin_omega = math.sin(omega)
    wa = math.sin((1.0 - t) * omega) / sin_omega
    wb = math.sin(t * omega) / sin_omega
    return glm.normalize(wa * a + wb * b)


def _arc_edges(graph, radius: float) -> np.ndarray:
    """Each graph edge sampled as a great-circle arc at `radius`, as GL_LINES pairs."""
    verts = graph.vertices
    edges = graph.edges
    segments_per_edge = ARC_SAMPLES - 1
    pairs = np.empty((len(edges) * segments_per_edge * 2, 3), dtype=np.float32)

    write = 0
    for i, j in edges:
        a = glm.normalize(verts[i])
        b = glm.normalize(verts[j])
        prev = a * radius
        for s in range(1, ARC_SAMPLES):
            t = s / (ARC_SAMPLES - 1)
            curr = _slerp(a, b, t) * radius
            pairs[write] = (prev.x, prev.y, prev.z)
            pairs[write + 1] = (curr.x, curr.y, curr.z)
            write += 2
            prev = curr

    return pairs


def _straight_edges(graph) -> np.ndarray:
    """Each graph edge as a straight chord between its vertices, as GL_LINES pairs."""
    verts = graph.vertices
    edges = graph.edges
    pairs = np.empty((len(edges) * 2, 3), dtype=np.float32)
    for k, (i, j) in enumerate(edges):
        a, b = verts[i], verts[j]
        pairs[2 * k] = (a.x, a.y, a.z)
        pairs[2 * k + 1] = (b.x, b.y, b.z)
    return pairs


def _subdivide_spherical(a, b, c, depth, out):
    """Recursively split triangle (a, b, c) into 4, projecting midpoints onto the
    unit sphere so the patch curves to match the sphere surface. Emits the leaf
    triangles (as glm.vec3) into `out`."""
    if depth == 0:
        out.append(a)
        out.append(b)
        out.append(c)
        return
    ab = glm.normalize(a + b)
    bc = glm.normalize(b + c)
    ca = glm.normalize(c + a)
    _subdivide_spherical(a, ab, ca, depth - 1, out)
    _subdivide_spherical(ab, b, bc, depth - 1, out)
    _subdivide_spherical(ca, bc, c, depth - 1, out)
    _subdivide_spherical(ab, bc, ca, depth - 1, out)


def _spherical_faces(graph, radius: float) -> np.ndarray:
    """Triangulate each face as a fan from its (sphere-projected) centroid, then
    subdivide every triangle onto a sphere of the given radius for a smooth,
    opaque surface."""
    verts = graph.vertices
    leaves: list[glm.vec3] = []

    for face in graph.faces:
        loop = [glm.normalize(verts[idx]) for idx in face.vertex_indices]
        if len(loop) < 3:
            continue

        centroid = glm.vec3(0.0)
        for p in loop:
            centroid += p
        centroid = glm.normalize(centroid)

        n = len(loop)
        for k in range(n):
            _subdivide_spherical(centroid, loop[k], loop[(k + 1) % n], FACE_SUBDIVISIONS, leaves)

    return _points_to_array(leaves, radius)


def _flat_faces(graph) -> np.ndarray:
    """Triangulate each face as a flat fan from its planar centroid, keeping the
    vertices at their true positions so the faces are the polyhedron's own planes."""
    verts = graph.vertices
    tris: list[glm.vec3] = []

    for face in graph.faces:
        loop = [verts[idx] for idx in face.vertex_indices]
        if len(loop) < 3:
            continue

        centroid = glm.vec3(0.0)
        for p in loop:
            centroid += p
        centroid = centroid / len(loop)

        n = len(loop)
        for k in range(n):
            tris.append(centroid)
            tris.append(loop[k])
            tris.append(loop[(k + 1) % n])

    return _points_to_array(tris, radius=None)


def _vertex_points(graph, radius: float) -> np.ndarray:
    """The graph's vertices as GL_POINTS at the given radius (radius None keeps
    them at their true positions)."""
    return _points_to_array([glm.normalize(v) for v in graph.vertices], radius)


def _points_to_array(points, radius) -> np.ndarray:
    """Pack glm.vec3 points into an (N, 3) float32 array, optionally scaling each
    (already-normalized) point to `radius`."""
    if not points:
        return np.empty((0, 3), dtype=np.float32)
    out = np.empty((len(points), 3), dtype=np.float32)
    for idx, p in enumerate(points):
        if radius is not None:
            p = p * radius
        out[idx] = (p.x, p.y, p.z)
    return out


def build_geometry(inputs: GeometryInputs) -> GeometryBuffers:
    g = _get_geodesic(inputs.shape_name, inputs.twist_angle, inputs.order)
    graph = g.geo_graph
    polyhedron = g.getPolyhedron()

    geodesic = ObjectBuffers(
        edges=_arc_edges(graph, GEO_ARC_RADIUS),
        faces=_spherical_faces(graph, GEO_FACE_RADIUS),
        vertices=_vertex_points(graph, GEO_VERTEX_RADIUS),
    )
    poly = ObjectBuffers(
        edges=_straight_edges(polyhedron),
        faces=_flat_faces(polyhedron),
        vertices=_vertex_points(polyhedron, radius=None),
    )
    return GeometryBuffers(geodesic=geodesic, polyhedron=poly)
