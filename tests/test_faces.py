"""Tests for face computation: Graph.computeFaces() on the base Platonic solids
and the trimmed faces of a twist-truncated Geodesic.

Each face is checked for three invariants:
  * the expected number of sides,
  * right-handed winding as seen from outside the unit sphere (the polygon's
    area-normal points away from the origin),
  * the lowest vertex index leading the loop (the Face ordering contract).
"""

import math

import pytest
from pyglm import glm

from src import Polyhedron, Geodesic


def _is_outward(vertices, loop):
    """True when `loop` winds right-handed viewed from outside the sphere."""
    # Newell's method: robust area-normal for an arbitrary (possibly non-planar) loop.
    normal = glm.vec3(0.0)
    n = len(loop)
    for i in range(n):
        a = vertices[loop[i]]
        b = vertices[loop[(i + 1) % n]]
        normal.x += (a.y - b.y) * (a.z + b.z)
        normal.y += (a.z - b.z) * (a.x + b.x)
        normal.z += (a.x - b.x) * (a.y + b.y)
    centroid = glm.vec3(0.0)
    for idx in loop:
        centroid += vertices[idx]
    return glm.dot(normal, centroid) > 0.0


def _assert_faces(graph, expected_count, expected_sides):
    """Assert the face count and side-count distribution, and that every face is
    outward-wound and led by its lowest index.

    `expected_sides` is either an int (every face has that many sides) or a dict
    mapping side-count -> number of faces with that many sides, e.g. {3: 20, 5: 12}.
    """
    faces = graph.faces
    assert len(faces) == expected_count

    if isinstance(expected_sides, int):
        expected_sides = {expected_sides: expected_count}

    side_counts = {}
    for face in faces:
        loop = face.vertex_indices
        side_counts[len(loop)] = side_counts.get(len(loop), 0) + 1
        assert loop[0] == min(loop), f"face {loop} is not lowest-index-first"
        assert _is_outward(graph.vertices, loop), f"face {loop} is not outward-wound"

    assert side_counts == expected_sides


# Platonic solids exercise Graph.computeFaces() directly (Polyhedron is a Graph).
# (shape name, expected face count, sides per face)
BASE_SOLIDS = [
    ("tetrahedron", 4, 3),
    ("hexahedron", 6, 4),
    ("octahedron", 8, 3),
    ("dodecahedron", 12, 5),
    ("icosahedron", 20, 3),
    ("rhombic_dodecahedron", 12, 4),
]


@pytest.mark.parametrize("shape, count, sides", BASE_SOLIDS)
def test_platonic_solid_faces(shape, count, sides):
    _assert_faces(Polyhedron(shape), count, sides)


@pytest.mark.parametrize("shape, count, sides", BASE_SOLIDS)
def test_zero_twist_matches_base_polyhedron(shape, count, sides):
    """With no twist the base vertices are not opened, so the geodesic's faces
    match its base polyhedron exactly (same count and same shape)."""
    geodesic = Geodesic(shape)
    geodesic.setTwistAngle(0.0)
    _assert_faces(geodesic.geo_graph, count, sides)


def test_rhombic_dodecahedron_aliases():
    """The requested common misspelling and display-friendly spellings work."""
    for name in ("rombic_dodecahedron", "rhombic-dodecahedron", "rhombic dodecahedron"):
        solid = Polyhedron(name)
        assert solid.shape == "rhombic_dodecahedron"
        _assert_faces(solid, 12, 4)


@pytest.mark.parametrize("order, vertices, edges, faces", [
    (1, 14, 24, 12),
    (2, 26, 72, 48),
    (3, 98, 288, 192),
])
def test_rhombic_dodecahedron_orders(order, vertices, edges, faces):
    solid = Polyhedron("rhombic_dodecahedron", order=order)
    assert solid.order == order
    assert (len(solid.vertices), len(solid.edges)) == (vertices, edges)
    _assert_faces(solid, faces, 3 if order > 1 else 4)


@pytest.mark.parametrize("twist", [0.1, -0.1])
def test_rhombic_dodecahedron_geodesic_faces(twist):
    """Twisting opens a new face matching each base vertex's degree."""
    geodesic = Geodesic("rhombic_dodecahedron")
    geodesic.setTwistAngle(twist)
    # Eight degree-3 cube-corner vertices open triangles; the six degree-4
    # axial vertices add quads alongside the 12 original rhombic faces.
    _assert_faces(geodesic.geo_graph, 26, {3: 8, 4: 18})


@pytest.mark.parametrize("twist", [0.1, -0.1])
@pytest.mark.parametrize("order, count, sides", [
    (2, 74, {3: 48, 4: 12, 6: 8, 8: 6}),
    (3, 290, {3: 192, 4: 12, 6: 80, 8: 6}),
])
def test_higher_order_rhombic_dodecahedron_geodesic_faces(
    twist, order, count, sides
):
    geodesic = Geodesic("rhombic_dodecahedron", order=order)
    geodesic.setTwistAngle(twist)
    _assert_faces(geodesic.geo_graph, count, sides)


def test_rhombic_dodecahedron_full_twist_slider_range():
    """Topology transitions across the UI slider must not create empty faces."""
    geodesic = Geodesic("rhombic_dodecahedron")
    for step in range(201):
        twist = -math.pi / 2 + math.pi * step / 200
        geodesic.setTwistAngle(twist)
        assert all(len(face.vertex_indices) >= 3 for face in geodesic.geo_graph.faces)


# A negative twist opens the base vertices the opposite way, but by symmetry the
# face topology is identical to the matching positive twist, so both signs are
# exercised with the same expectations.
@pytest.mark.parametrize("twist", [0.1, -0.1])
def test_tetrahedron_geodesic_faces(twist):
    """A tetrahedron twisted by a small angle yields eight triangular faces.

    The four original faces survive and four new "truncated" faces open at the
    base vertices. After mid-arc vertices are trimmed every face is a triangle.
    """
    geodesic = Geodesic("tetrahedron")
    geodesic.setTwistAngle(twist)
    _assert_faces(geodesic.geo_graph, 8, 3)


@pytest.mark.parametrize("twist", [0.6534, -0.6534])
def test_icosahedron_geodesic_faces(twist):
    """A twisted icosahedron yields 32 faces: the 20 original triangular faces
    plus 12 new pentagonal "truncated" faces opening at the base vertices.
    """
    geodesic = Geodesic("icosahedron")
    geodesic.setTwistAngle(twist)
    _assert_faces(geodesic.geo_graph, 32, {3: 20, 5: 12})
