#
# graph.py -- Graph of vertices, edges and faces
#
# A Graph holds a set of vertices, the edges connecting them, the per-vertex
# neighbor adjacency, and the faces (loops of vertices). Subclasses decide how
# the vertices and edges are produced; computing faces from existing vertices
# and edges is general enough to live here.
#

import math
from pyglm import glm
from .face import Face


# helper
def sort_indices(index_list):
    """Rotate the index_list to make the lowest element first."""
    min_value = min(index_list)
    min_index = index_list.index(min_value)
    return index_list[min_index:] + index_list[:min_index]


class Graph:
    """
    A graph of vertices connected by edges, grouped into faces.

    Holds the vertices/edges/neighbors/faces members. Subclasses populate the
    vertices and edges (the connectivity rule varies by graph type); deriving
    the faces from vertices and edges is shared logic and lives in computeFaces().
    """

    def __init__(self, verbose=False):
        """
        Initialize an empty Graph.

        Args:
            verbose: When True, subclasses print intermediate computation to stdout.
        """
        self.verbose = verbose
        self.vertices = []      # list of vertex positions
        self.edges = []         # pairs of vertex indices connected by line segment
        self.neighbors = []     # for each vertex index: list of other vertex indices that pair as an edge
        self.faces = []         # list of vertices that form a minimal loop

    def computeFaces(self):
        """
        Compute Faces of the Graph from its vertices and edges.

        For each Vertex, find all Faces formed by Edges connecting to that Vertex.
        A Face exists when a loop of Vertices are mutually connected on a common plane.

        Each Face is stored only once with Vertices in right-handed order, lowest index first.
        """
        if len(self.vertices) < 3:
            print("Error: Need at least 3 Vertices to compute Faces.")
            self.faces = []
            return

        if len(self.edges) < 3:
            print("Error: Need at least three Edges to compute Faces. Call computeEdges() first.")
            self.faces = []
            return

        # Build adjacency list: for each vertex, list of connected Vertices
        adjacency = [set() for _ in range(len(self.vertices))]
        for i, j in self.edges:
            adjacency[i].add(j)
            adjacency[j].add(i)

        if self.verbose:
            print(f"\nVertex neighbors:")
            for i in range(len(adjacency)):
                neighbors = adjacency[i]
                print(f" {i:2} {neighbors}")
        self.neighbors = adjacency

        # Trace faces with the half-edge "next" rule. Each undirected edge is two
        # directed half-edges; every half-edge belongs to exactly one face. Walking
        # from a half-edge (u -> v), the next half-edge leaves v along the neighbor
        # that is the sharpest clockwise turn from the reverse direction (v -> u),
        # measured in v's tangent plane with v itself as the outward normal. On the
        # unit sphere this "most-clockwise-when-viewed-from-outside" rule traces the
        # minimal loop bounding each face in right-handed (counter-clockwise) order.
        face_loops = set()
        visited_half_edges = set()
        for u, v in self._directed_half_edges():
            if (u, v) in visited_half_edges:
                continue

            loop = [u]
            a, b = u, v
            while True:
                visited_half_edges.add((a, b))
                if b == u:
                    break
                loop.append(b)
                a, b = b, self._next_in_face(a, b)
                if (a, b) in visited_half_edges:
                    # Closed back on the starting half-edge (b == u handled above)
                    # or, defensively, hit an already-traced edge; stop here.
                    break

            # Orient the loop right-handed as seen from outside the sphere (its
            # polygon normal should point away from the origin), then rotate so
            # the lowest index leads. Fixing winding here makes the result
            # independent of which turn direction the trace happened to follow.
            loop = self._orient_outward(loop)
            face_loops.add(tuple(sort_indices(loop)))

        # Now that we have all of the face_loops convert to list of Face objects
        self.faces = [Face(loop) for loop in sorted(face_loops)]

        if self.verbose:
            print("\nFaces:")
            for i, face in enumerate(self.faces):
                print(f" {i:2} {face}")

    def _orient_outward(self, loop):
        """Return `loop` ordered so its winding is right-handed when viewed from
        outside the unit sphere, i.e. the polygon's area-normal points away from
        the origin. Reverses the loop in place-of-copy if it is currently inward."""
        # Newell's method gives a normal robust to non-planar / many-vertex loops.
        normal = glm.vec3(0.0, 0.0, 0.0)
        n = len(loop)
        for i in range(n):
            current = self.vertices[loop[i]]
            nxt = self.vertices[loop[(i + 1) % n]]
            normal.x += (current.y - nxt.y) * (current.z + nxt.z)
            normal.y += (current.z - nxt.z) * (current.x + nxt.x)
            normal.z += (current.x - nxt.x) * (current.y + nxt.y)

        # Centroid direction approximates the outward radial direction for a face
        # of a sphere-centered mesh.
        centroid = glm.vec3(0.0, 0.0, 0.0)
        for idx in loop:
            centroid += self.vertices[idx]
        if glm.dot(normal, centroid) < 0.0:
            return list(reversed(loop))
        return list(loop)

    def _directed_half_edges(self):
        """Yield each undirected edge as both of its directed half-edges."""
        for vertex, neighbors in enumerate(self.neighbors):
            for neighbor in neighbors:
                yield (vertex, neighbor)

    def _next_in_face(self, a, b):
        """
        Given the directed half-edge a -> b, return the next vertex c so that
        b -> c continues the face that lies to the right of a -> b.

        At b we look back toward a and choose, among b's other neighbors, the one
        reached by the smallest clockwise turn when viewed from outside the sphere
        (b is the outward normal). Picking the most-clockwise candidate keeps the
        traversal hugging a single face, producing a right-handed loop.
        """
        normal = glm.normalize(self.vertices[b])
        incoming = self._tangent_direction(b, a, normal)

        best = None
        best_angle = None
        for c in self.neighbors[b]:
            if c == a and len(self.neighbors[b]) > 1:
                # Don't immediately backtrack unless b is a dead end.
                continue
            outgoing = self._tangent_direction(b, c, normal)
            angle = self._clockwise_angle(incoming, outgoing, normal)
            if best_angle is None or angle < best_angle:
                best_angle = angle
                best = c
        return best

    def _tangent_direction(self, origin_index, target_index, normal):
        """Unit direction from origin toward target, projected into origin's
        tangent plane (the plane through origin with `normal` as its normal)."""
        delta = self.vertices[target_index] - self.vertices[origin_index]
        tangent = delta - glm.dot(delta, normal) * normal
        return glm.normalize(tangent)

    @staticmethod
    def _clockwise_angle(reference, direction, normal):
        """Angle in [0, 2pi) swept clockwise from `reference` to `direction`,
        looking down the outward `normal` (i.e. from outside the sphere).

        Clockwise-as-seen-from-outside is the negative (left-handed) sense about
        the outward normal, so we negate the cross-product term."""
        cos_a = glm.dot(reference, direction)
        # Component of `direction` along the clockwise perpendicular of `reference`.
        sin_a = glm.dot(glm.cross(reference, direction), normal)
        angle = math.atan2(-sin_a, cos_a)
        if angle < 0.0:
            angle += 2.0 * math.pi
        return angle
