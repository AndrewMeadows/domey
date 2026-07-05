#
# polyhedron.py -- Regular polyhedron as a special case of Graph
#
# Polyhedron picks the vertices of one of the five regular (Platonic) solids,
# then derives the edges/neighbors/faces from them. Graph (see graph.py) is the
# plain data container holding those members; Polyhedron supplies both the
# vertex-generating logic for each solid and the topology computation.
#

import math
from pyglm import glm
from .graph import Graph


class Polyhedron(Graph):
    """
    A regular polyhedron: a Graph whose vertices come from a Platonic solid.

    Provides methods to initialize the vertices of each of the five regular
    polyhedra.
    """

    VALID_SHAPES = {
        'tetrahedron',
        'cube',         # aka hexahedron
        'hexahedron',
        'octahedron',
        'dodecahedron',
        'icosahedron'
    }

    def __init__(self, shape=None, order=1, verbose=False):
        """
        Initialize a polyhedron with an optional shape type.

        Args:
            shape: Optional string specifying the shape ('tetrahedron', 'hexahedron',
                   'hexahedron', 'octahedron', 'dodecahedron', 'icosahedron').
                   If None, creates an empty polyhedron that must be initialized
                   manually using one of the init methods.

        Raises:
            ValueError: If shape is invalid.
        """
        # Start with an empty Graph; this polyhedron supplies its own vertices.
        super().__init__(verbose=verbose)
        self.shape = ""

        if shape is not None:
            shape_name_lower = shape.lower()
            if shape_name_lower not in self.VALID_SHAPES:
                raise ValueError(
                    f"Invalid shape '{shape}'. "
                    f"Valid options are: {', '.join(sorted(self.VALID_SHAPES))}"
                )
            self.shape =  shape_name_lower
            self._rebuildGraph(order)


    def _initTetrahedron(self):
        """
        Initialize vertices for a regular tetrahedron.

        The four vertices of a regular tetrahedron centered at the origin are:
        (1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)
        """
        self.shape = "tetrahedron"
        self.vertices = [
            glm.vec3(1, 1, 1),
            glm.vec3(1, -1, -1),
            glm.vec3(-1, 1, -1),
            glm.vec3(-1, -1, 1)
        ]

    def _initHexahedron(self):
        """
        Initialize vertices for a hexahedron (aka cube).

        The eight vertices of a hexahedron centered at the origin are:
        (+/-1, +/-1, +/-1) for all combinations of signs
        """
        self.shape = "hexahedron"
        self.vertices = [
            glm.vec3(1, 1, 1),
            glm.vec3(1, 1, -1),
            glm.vec3(1, -1, 1),
            glm.vec3(1, -1, -1),
            glm.vec3(-1, 1, 1),
            glm.vec3(-1, 1, -1),
            glm.vec3(-1, -1, 1),
            glm.vec3(-1, -1, -1)
        ]

    def _initOctahedron(self):
        """
        Initialize vertices for a regular octahedron.

        The 6 vertices of a regular octahedron centered at the origin are:
        (±1, 0, 0), (0, ±1, 0), (0, 0, ±1)
        """
        self.shape = "octahedron"
        self.vertices = [
            glm.vec3(1, 0, 0),
            glm.vec3(-1, 0, 0),
            glm.vec3(0, 1, 0),
            glm.vec3(0, -1, 0),
            glm.vec3(0, 0, 1),
            glm.vec3(0, 0, -1)
        ]

    def _initDodecahedron(self):
        """
        Initialize vertices for a regular dodecahedron.

        The 20 vertices of a regular dodecahedron centered at the origin are:
        (±1, ±1, ±1) - 8 vertices of a hexahedron
        (0, ±φ, ±1/φ) - 4 vertices
        (±1/φ, 0, ±φ) - 4 vertices
        (±φ, ±1/φ, 0) - 4 vertices
        where φ = (1 + sqrt(5)) / 2 (golden ratio)
        """
        self.shape = "dodecahedron"

        # Calculate φ = (1 + sqrt(5)) / 2 (golden ratio)
        phi = (1 + math.sqrt(5)) / 2
        inv_phi = 1 / phi

        self.vertices = []

        # (±1, ±1, ±1) - 8 vertices of a hexahedron
        self.vertices.extend([
            glm.vec3(1, 1, 1),
            glm.vec3(1, 1, -1),
            glm.vec3(1, -1, 1),
            glm.vec3(1, -1, -1),
            glm.vec3(-1, 1, 1),
            glm.vec3(-1, 1, -1),
            glm.vec3(-1, -1, 1),
            glm.vec3(-1, -1, -1)
        ])

        # (0, ±φ, ±1/φ) - 4 vertices
        self.vertices.extend([
            glm.vec3(0, phi, inv_phi),
            glm.vec3(0, phi, -inv_phi),
            glm.vec3(0, -phi, inv_phi),
            glm.vec3(0, -phi, -inv_phi)
        ])

        # (±1/φ, 0, ±φ) - 4 vertices
        self.vertices.extend([
            glm.vec3(inv_phi, 0, phi),
            glm.vec3(inv_phi, 0, -phi),
            glm.vec3(-inv_phi, 0, phi),
            glm.vec3(-inv_phi, 0, -phi)
        ])

        # (±φ, ±1/φ, 0) - 4 vertices
        self.vertices.extend([
            glm.vec3(phi, inv_phi, 0),
            glm.vec3(phi, -inv_phi, 0),
            glm.vec3(-phi, inv_phi, 0),
            glm.vec3(-phi, -inv_phi, 0)
        ])

    def _initIcosahedron(self):
        """
        Initialize vertices for a regular icosahedron.

        The 12 vertices of an icosahedron are given by:
        (0, ±1, ±a)
        (±1, ±a, 0)
        (±a, 0, ±1)
        where a = (1 + sqrt(5)) / 2 (golden ratio)
        """
        self.shape = "icosahedron"

        # Calculate a = (1 + sqrt(5)) / 2
        a = (1 + math.sqrt(5)) / 2

        self.vertices = []

        # (0, ±1, ±a)
        self.vertices.extend([
            glm.vec3(0, 1, a),
            glm.vec3(0, 1, -a),
            glm.vec3(0, -1, a),
            glm.vec3(0, -1, -a)
        ])

        # (±1, ±a, 0)
        self.vertices.extend([
            glm.vec3(1, a, 0),
            glm.vec3(1, -a, 0),
            glm.vec3(-1, a, 0),
            glm.vec3(-1, -a, 0)
        ])

        # (±a, 0, ±1)
        self.vertices.extend([
            glm.vec3(a, 0, 1),
            glm.vec3(a, 0, -1),
            glm.vec3(-a, 0, 1),
            glm.vec3(-a, 0, -1)
        ])

    def _computeTopology(self):
        """Orient the vertices and derive edges, neighbors, and faces."""
        self._orientAndAlign()
        self._computeEdges()
        self.computeFaces()

    def _rebuildGraph(self, order):
        # Map shape types to their initialization methods
        shape_map = {
            'tetrahedron': self._initTetrahedron,
            'cube': self._initHexahedron,
            'hexahedron': self._initHexahedron,
            'octahedron': self._initOctahedron,
            'dodecahedron': self._initDodecahedron,
            'icosahedron': self._initIcosahedron
        }
        shape_map[self.shape]()
        self._computeTopology()

        # we only support frequencies 1, 2, and 3
        MAX_ORDER = 3
        MIN_ORDER = 1
        if order > 1:
            order = min(order, MAX_ORDER)
            i = order
            if self.shape == "hexahedron" or self.shape == "dodecahedron":
                # for some shapes: add a vertex in the center of each face
                #
                #   o---------------o         o---------------o
                #   |               |         |               |
                #   |               |         |               |
                #   |               |         |               |
                #   |               |  --->   |       o       |
                #   |               |         |               |
                #   |               |         |               |
                #   |               |         |               |
                #   o---------------o         o---------------o
                #
                for face in self.faces:
                    new_vertex = glm.vec3(0, 0, 0)
                    for index in face.vertex_indices:
                        new_vertex += self.vertices[index]
                    self.vertices.append(glm.normalize(new_vertex))
                # now all faces are triangles
                self._computeTopology()
                i -= 1
            elif self.shape == "tetrahedron":
                # add a vertex in the center of each edge, and one at the center
                #    o---------------o       o-------o-------o
                #     \             /         \             /
                #      \           /           \     o     /
                #       \         /             \         /
                #        \       /     ---->     o       o
                #         \     /                 \     /
                #          \   /                   \   /
                #           \ /                     \ /
                #            o                       o
                #
                # adjacent faces share edges; track processed edges so each shared
                # edge contributes only one midpoint vertex
                for edge in self.edges:
                    self.vertices.append(glm.normalize(self.vertices[edge[0]] + self.vertices[edge[1]]))
                for face in self.faces:
                    face_center = glm.vec3(0, 0, 0)
                    for index in face.vertex_indices:
                        face_center += self.vertices[index]
                    self.vertices.append(glm.normalize(face_center))

                self._computeTopology()
                i -= 1

            if i == 2:
                # add a vertex in the center of each edge
                #    o---------------o       o-------o-------o
                #     \             /         \             /
                #      \           /           \           /
                #       \         /             \         /
                #        \       /     ---->     o       o
                #         \     /                 \     /
                #          \   /                   \   /
                #           \ /                     \ /
                #            o                       o
                #
                for edge in self.edges:
                    self.vertices.append(glm.normalize(self.vertices[edge[0]] + self.vertices[edge[1]]))
                self._computeTopology()
            elif i == 3:
                # divide each arc by three, then add one vertex in the center
                #    o-----------------o       o-----o-----o-----o
                #     \               /         \               /
                #      \             /           \             /
                #       \           /             o     o     o
                #        \         /               \         /
                #         \       /     ---->       \       /
                #          \     /                   o     o
                #           \   /                     \   /
                #            \ /                       \ /
                #             o                         o
                #
                # compute the points at 1/3 and 2/3 along the arc from A to B and
                # append both to new_vertices

                # util function for dividing edge into thirds
                # along the arc from A to B rather than
                # along the straight line from A to B
                def compute_two_points(point_A, point_B):
                    axis = glm.cross(point_A, point_B)
                    axis_length = glm.length(axis)
                    # angle is the sweep to move point_A to point_B
                    angle = math.asin(axis_length)
                    # we want new points that are one-third of angle
                    delta_angle = angle/3.0
                    # the coefficients of the quaternion use sines of half of delta_angle
                    c = math.cos(delta_angle/2.0)
                    s = math.sin(delta_angle/2.0)   # the w-component scales with c
                    axis *= s / axis_length         # the xyz components scale with s*normalized_axis
                    dQ = glm.quat(c, axis.x, axis.y, axis.z)
                    # rotate point_A from the left toward B, point_B from the right toward A
                    return (dQ * point_A, point_B * dQ)

                for edge in self.edges:
                    points = compute_two_points(self.vertices[edge[0]], self.vertices[edge[1]])
                    for point in points:
                        self.vertices.append(point)
                for face in self.faces:
                    face_center = glm.vec3(0, 0, 0)
                    for index in face.vertex_indices:
                        face_center += self.vertices[index]
                    self.vertices.append(glm.normalize(face_center))
                self._computeTopology()
        else:
            order = MIN_ORDER
        self.order = order


    def _orientAndAlign(self):
        """
        Normalize vertices and align them to a standard orientation.

        This method:
        1. Normalizes all vertices to unit length (radius = 1.0)
        2. Rotates so the first vertex aligns with the positive z-axis
        3. Rotates around the z-axis so the second vertex lies in the YZ plane

        The aligned vertices replace the original vertices.
        """
        if not self.vertices:
            if self.verbose:
                print("Error: No vertices to process. Provide vertices first.")
            return

        # Normalize all vertices to unit length
        normalized_vertices = [glm.normalize(vertex) for vertex in self.vertices]

        if self.verbose:
            print(f"\nVertices:")
            for i, vertex in enumerate(normalized_vertices):
                print(f" {i:2} ({vertex.x:8.5f}, {vertex.y:8.5f}, {vertex.z:8.5f})")

        # Check if any vertex is already aligned with z-axis
        z_axis = glm.vec3(0, 0, 1)
        tolerance = 1e-6

        z_aligned = False
        for vertex in normalized_vertices:
            cross_mag = glm.length(glm.cross(vertex, z_axis))
            if cross_mag < tolerance:
                z_aligned = True
                break

        if not z_aligned:
            # Compute quaternion Q that rotates normalized_vertices[0] to z-axis
            v0 = normalized_vertices[0]
            target = glm.vec3(0, 0, 1)  # positive z-axis

            # Compute rotation quaternion from v0 to target
            cross_product = glm.cross(v0, target)
            dot_product = glm.dot(v0, target)

            # Compute angle and normalized axis
            angle = math.acos(dot_product)
            axis = glm.normalize(cross_product)

            # Create quaternion from angle and axis
            Q = glm.angleAxis(angle, axis)

            # Apply rotation Q to all normalized vertices
            rotated_vertices = [Q * vertex for vertex in normalized_vertices]

            if self.verbose:
                print("\nRotated vertices:")
                for i, vertex in enumerate(rotated_vertices):
                    print(f" {i:2} ({vertex.x:8.5f}, {vertex.y:8.5f}, {vertex.z:8.5f})")

            # Check if v1 needs rotation to align with YZ plane
            v1 = rotated_vertices[1]
            threshold = 1.0e-4

            if abs(v1.x) > threshold:
                # Compute quaternion Q2 that rotates rotated_vertices[1] to align with y-axis
                # Project v1 onto xy plane (remove z component)
                v1_xy = glm.vec3(v1.x, v1.y, 0)
                v1_xy_normalized = glm.normalize(v1_xy)
                y_target = glm.vec3(0, 1, 0)  # positive y-axis

                # Compute rotation quaternion from v1_xy to y_target
                cross_product2 = glm.cross(v1_xy_normalized, y_target)
                dot_product2 = glm.dot(v1_xy_normalized, y_target)

                # Compute angle and normalized axis
                angle2 = math.acos(dot_product2)
                axis2 = glm.normalize(cross_product2)

                # Create quaternion from angle and axis
                Q2 = glm.angleAxis(angle2, axis2)

                # Apply rotation Q2 to all rotated vertices
                aligned_vertices = [Q2 * vertex for vertex in rotated_vertices]
            else:
                aligned_vertices = rotated_vertices

        else:
            aligned_vertices = normalized_vertices

        # Replace original vertices with aligned vertices, then sort
        self.vertices = aligned_vertices
        self._sortVertices()

        if self.verbose:
            print("\nAligned and sorted vertices:")
            for i, vertex in enumerate(aligned_vertices):
                print(f" {i:2} ({vertex.x:8.5f}, {vertex.y:8.5f}, {vertex.z:8.5f})")


    def _sortVertices(self):
        """
        Sort vertices using two criteria:
        1. Z-component (descending - more positive values first)
        2. Angle in XY plane relative to x-axis (range [0, 2π])

        The angle is computed using atan2(y, x) and normalized to [0, 2π].
        """
        def sort_key(vertex):
            # Primary sort: z-component, descending (negate for descending order)
            z = -vertex.z

            # Secondary sort: angle in XY plane [0, 2π]
            angle = math.atan2(vertex.y, vertex.x)
            # Normalize to [0, 2π] range
            if angle < 0:
                angle += 2 * math.pi

            return (z, angle)

        self.vertices.sort(key=sort_key)

    def _computeEdges(self):
        """
        Compute Edges between Vertices based on distance.

        An Edge connects two Vertices if their distance is within a scalar multiple of
        a reference Edge length. The reference Edge length is the minimum distance
        from Vertex 0 to all other Vertices.
        Each Edge is stored as a tuple (i, j) where i < j.
        """
        if len(self.vertices) < 2:
            print("Error: Need at least two Vertices to compute Edges.")
            self.edges = []
            return self.edges

        # Find minimum distance from vertex 0 to any other
        v0 = self.vertices[0]
        min_dist = float('inf')
        for i in range(1, len(self.vertices)):
            dist = glm.distance(v0, self.vertices[i])
            if dist < min_dist:
                min_dist = dist

        NEIGHBOR_PROXIMITY_FACTOR = 1.395
        neighbor_threshold = NEIGHBOR_PROXIMITY_FACTOR * min_dist

        # For each Vertex, check all Vertices with higher indices
        self.edges = []
        num_edges = 0
        for i in range(len(self.vertices)):
            for j in range(i + 1, len(self.vertices)):
                dist = glm.distance(self.vertices[i], self.vertices[j])
                if dist <= neighbor_threshold:
                    # Add Edge with lower index first
                    self.edges.append((i, j))
                    num_edges += 1
        if self.verbose:
            print("\nEdges:")
            for i in range(len(self.edges)):
                edge = self.edges[i]
                print(f" {i:2} {edge}")


# Example usage
if __name__ == "__main__":
    # Test all five Platonic solids using the new constructor API
    shapes = [
        "tetrahedron",
        "hexahedron",
        "octahedron",
        "dodecahedron",
        "icosahedron"
    ]

    for shape in shapes:
        print("=" * 60)
        print(shape.upper())
        print("=" * 60)
        shape = Polyhedron(shape, verbose=True)
        print("\n")
