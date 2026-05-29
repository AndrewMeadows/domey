import math
from dataclasses import dataclass

import numpy as np

from geodesics import Geodesic

from .state import GeometryInputs

ARC_SAMPLES = 32  # vertices per arc polyline


@dataclass
class GeometryBuffers:
    edge_vertices: np.ndarray         # float32, shape (N, 3), GL_LINES pairs
    arc_vertices: np.ndarray          # float32, shape (M, 3), GL_LINES pairs
    intersection_points: np.ndarray   # float32, shape (P, 3), GL_POINTS
    face_triangles: np.ndarray        # float32, shape (T, 3), GL_TRIANGLES


_geodesic_cache: dict[str, Geodesic] = {}


def _get_geodesic(shape_name: str, twist: float) -> Geodesic:
    g = _geodesic_cache.get(shape_name)
    if g is None:
        g = Geodesic(shape_name)
        _geodesic_cache[shape_name] = g
    g.setTwistAngle(twist)
    return g


def _edge_vertices(g: Geodesic) -> np.ndarray:
    pairs = np.empty((len(g.edges) * 2, 3), dtype=np.float32)
    for k, (i, j) in enumerate(g.edges):
        a, b = g.vertices[i], g.vertices[j]
        pairs[2 * k] = (a.x, a.y, a.z)
        pairs[2 * k + 1] = (b.x, b.y, b.z)
    return pairs


def _arc_data_from_arcs(arcs) -> tuple[np.ndarray, np.ndarray]:
    """Returns (arc_line_pairs, intersection_points) from pre-computed arcs."""
    segments_per_arc = ARC_SAMPLES - 1
    pairs_per_arc = segments_per_arc * 2  # GL_LINES needs both endpoints per segment
    arc_verts = np.empty((len(arcs) * pairs_per_arc, 3), dtype=np.float32)
    # Each arc contributes two intersection points (one per end); duplicates
    # with the neighboring arc are accepted as harmless overdraw.
    point_verts = np.empty((len(arcs) * 2, 3), dtype=np.float32)

    for a_idx, arc in enumerate(arcs):
        start = arc.trimB
        span = arc.trimA - arc.trimB
        prev = arc.getPoint(start)
        write = a_idx * pairs_per_arc
        for s in range(1, ARC_SAMPLES):
            t = s / (ARC_SAMPLES - 1)
            curr = arc.getPoint(start + span * t)
            arc_verts[write] = (prev.x, prev.y, prev.z)
            arc_verts[write + 1] = (curr.x, curr.y, curr.z)
            write += 2
            prev = curr

        pa = arc.getPoint(arc.intersectionA)
        pb = arc.getPoint(arc.intersectionB)
        point_verts[a_idx * 2] = (pa.x, pa.y, pa.z)
        point_verts[a_idx * 2 + 1] = (pb.x, pb.y, pb.z)

    return arc_verts, point_verts


FACE_ARC_SAMPLES = 16  # samples per arc along a face boundary


def _sample_arc(arc, start: float, end: float, n: int) -> list[tuple[float, float, float]]:
    out = []
    for s in range(n):
        t = s / (n - 1)
        p = arc.getPoint(start + (end - start) * t)
        out.append((p.x, p.y, p.z))
    return out


def _face_triangles(g, arcs) -> np.ndarray:
    """Sample each face's twisted arc boundary, fan-triangulate from centroid."""
    edge_to_arc = {edge: i for i, edge in enumerate(g.edges)}
    triangles: list[tuple[float, float, float]] = []

    for face in g.faces:
        face_edges = face.getEdges()

        # Walk the face's arcs and concatenate boundary samples in order. For
        # each arc, decide orientation by comparing endpoint proximity to the
        # previous boundary point.
        boundary: list[tuple[float, float, float]] = []
        for edge in face_edges:
            arc = arcs[edge_to_arc[edge]]
            samples_fwd = _sample_arc(arc, arc.trimB, arc.trimA, FACE_ARC_SAMPLES)
            if not boundary:
                boundary.extend(samples_fwd)
                continue
            last = boundary[-1]
            d_fwd = _sq_dist(last, samples_fwd[0])
            d_rev = _sq_dist(last, samples_fwd[-1])
            chunk = samples_fwd if d_fwd < d_rev else list(reversed(samples_fwd))
            # Skip the duplicated shared endpoint.
            boundary.extend(chunk[1:])

        if len(boundary) < 3:
            continue

        # Centroid for fan triangulation, projected onto the unit sphere so
        # the fan apex sits on the same surface as the boundary samples.
        cx = sum(p[0] for p in boundary) / len(boundary)
        cy = sum(p[1] for p in boundary) / len(boundary)
        cz = sum(p[2] for p in boundary) / len(boundary)
        length = math.sqrt(cx * cx + cy * cy + cz * cz)
        if length > 0.0:
            cx, cy, cz = cx / length, cy / length, cz / length
        centroid = (cx, cy, cz)

        for k in range(len(boundary)):
            a = boundary[k]
            b = boundary[(k + 1) % len(boundary)]
            triangles.append(centroid)
            triangles.append(a)
            triangles.append(b)

    if not triangles:
        return np.empty((0, 3), dtype=np.float32)
    return np.array(triangles, dtype=np.float32)


def _sq_dist(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def build_geometry(inputs: GeometryInputs) -> GeometryBuffers:
    g = _get_geodesic(inputs.shape_name, inputs.twist_angle)
    #arcs = g.computeTwistedArcs(inputs.twist_angle)
    arc_verts, point_verts = _arc_data_from_arcs(g.arcs)
    face_tris = _face_triangles(g, g.arcs)
    return GeometryBuffers(
        edge_vertices=_edge_vertices(g),
        arc_vertices=arc_verts,
        intersection_points=point_verts,
        face_triangles=face_tris,
    )
