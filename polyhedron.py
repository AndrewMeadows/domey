#
# polyhedron.py -- Object-oriented implementation for regular polyhedron vertex computation
#
# This class encapsulates the common logic for computing vertices of regular polyhedra,
# normalizing them, and aligning them to standard orientations.
#

import math
import glm
from face import Face

# helper
def sort_indices(index_list):
    """Rotate the index_list to make the lowest element first."""
    min_value = min(index_list)
    min_index = index_list.index(min_value)
    return index_list[min_index:] + index_list[:min_index]


class Polyhedron:
    """
    A class representing a regular polyhedron shape.

    Provides methods to initialize different polyhedra and orient/align their vertices
    to a standard coordinate system where one vertex is aligned with the z-axis and
    another is aligned to the YZ plane.
    """

    VALID_SHAPES = {
        'tetrahedron',
        'cube',         # aka hexahedron
        'hexahedron',
        'octahedron',
        'dodecahedron',
        'icosahedron'
    }

    def __init__(self, shape_type=None):
        """
        Initialize a polyhedron with an optional shape type.

        Args:
            shape_type: Optional string specifying the shape ('tetrahedron', 'hexahedron',
                       'hexahedron', 'octahedron', 'dodecahedron', 'icosahedron').
                       If None, creates an empty polyhedron that must be initialized
                       manually using one of the init methods.

        Raises:
            ValueError: If shape_type is not a valid shape name.
        """
        self.vertices = []          # vertex points
        self.edges = []             # pairs of vertex indices connected by line segment
        self.connections = []       # for each vertex index: list of other vertex indices connected by edges
        self.faces = []             # faces of the polyhedron
        self.shape_name = ""

        if shape_type is not None:
            shape_type_lower = shape_type.lower()
            if shape_type_lower not in self.VALID_SHAPES:
                raise ValueError(
                    f"Invalid shape_type '{shape_type}'. "
                    f"Valid options are: {', '.join(sorted(self.VALID_SHAPES))}"
                )

            # Map shape types to their initialization methods
            shape_map = {
                'tetrahedron': self.initTetrahedron,
                'cube': self.initHexahedron,
                'hexahedron': self.initHexahedron,
                'octahedron': self.initOctahedron,
                'dodecahedron': self.initDodecahedron,
                'icosahedron': self.initIcosahedron
            }

            shape_map[shape_type_lower]()

        self.orientAndAlign()
        self.computeEdges()

    def initTetrahedron(self):
        """
        Initialize vertices for a regular tetrahedron.

        The four vertices of a regular tetrahedron centered at the origin are:
        (1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)
        """
        self.shape_name = "tetrahedron"
        self.vertices = [
            glm.vec3(1, 1, 1),
            glm.vec3(1, -1, -1),
            glm.vec3(-1, 1, -1),
            glm.vec3(-1, -1, 1)
        ]

    def initHexahedron(self):
        """
        Initialize vertices for a hexahedron (aka cube).

        The eight vertices of a hexahedron centered at the origin are:
        (+/-1, +/-1, +/-1) for all combinations of signs
        """
        self.shape_name = "hexahedron"
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

    def initOctahedron(self):
        """
        Initialize vertices for a regular octahedron.

        The 6 vertices of a regular octahedron centered at the origin are:
        (±1, 0, 0), (0, ±1, 0), (0, 0, ±1)
        """
        self.shape_name = "octahedron"
        self.vertices = [
            glm.vec3(1, 0, 0),
            glm.vec3(-1, 0, 0),
            glm.vec3(0, 1, 0),
            glm.vec3(0, -1, 0),
            glm.vec3(0, 0, 1),
            glm.vec3(0, 0, -1)
        ]

    def initDodecahedron(self):
        """
        Initialize vertices for a regular dodecahedron.

        The 20 vertices of a regular dodecahedron centered at the origin are:
        (±1, ±1, ±1) - 8 vertices of a hexahedron
        (0, ±φ, ±1/φ) - 4 vertices
        (±1/φ, 0, ±φ) - 4 vertices
        (±φ, ±1/φ, 0) - 4 vertices
        where φ = (1 + sqrt(5)) / 2 (golden ratio)
        """
        self.shape_name = "dodecahedron"

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

    def initIcosahedron(self):
        """
        Initialize vertices for a regular icosahedron.

        The 12 vertices of an icosahedron are given by:
        (0, ±1, ±a)
        (±1, ±a, 0)
        (±a, 0, ±1)
        where a = (1 + sqrt(5)) / 2 (golden ratio)
        """
        self.shape_name = "icosahedron"

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

    def orientAndAlign(self, verbose=False):
        """
        Normalize vertices and align them to a standard orientation.

        This method:
        1. Normalizes all vertices to unit length (radius = 1.0)
        2. Rotates so the first vertex aligns with the positive z-axis
        3. Rotates around the z-axis so the second vertex lies in the YZ plane

        The aligned vertices replace the original vertices.

        Args:
            verbose: If True, print detailed information about the process
        """
        if not self.vertices:
            if verbose:
                print("Error: No vertices to process. Call an init method first.")
            return

        # Normalize all vertices to unit length
        normalized_vertices = [glm.normalize(vertex) for vertex in self.vertices]

        if verbose:
            print(f"\n{self.shape_name}:")
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

            if verbose:
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
        self.sortVertices()

        if verbose:
            print("\nAligned and sorted vertices:")
            for i, vertex in enumerate(aligned_vertices):
                print(f" {i:2} ({vertex.x:8.5f}, {vertex.y:8.5f}, {vertex.z:8.5f})")


    def sortVertices(self):
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

    def computeEdges(self, verbose=False):
        """
        Compute Edges between Vertices based on distance.

        An Edge connects two Vertices if their distance is within a scalar multiple of
        a reference Edge length. The reference Edge length is the minimum distance
        from Vertex 0 to all other Vertices.
        Each Edge is stored as a tuple (i, j) where i < j.
        """
        if len(self.vertices) < 2:
            print("Error: Need at least 2 Vertices to compute edges.")
            self.edges = []
            return self.edges

        # Find minimum distance from vertex 0 to any other vertex
        v0 = self.vertices[0]
        min_dist = float('inf')
        for i in range(1, len(self.vertices)):
            dist = glm.distance(v0, self.vertices[i])
            if dist < min_dist:
                min_dist = dist

        edge_length = min_dist
        threshold = 1.4 * edge_length

        # For each Vertex, check all Vertices with higher indices
        self.edges = []
        num_edges = 0
        for i in range(len(self.vertices)):
            for j in range(i + 1, len(self.vertices)):
                dist = glm.distance(self.vertices[i], self.vertices[j])
                if dist <= threshold:
                    # Add Edge with lower index first
                    self.edges.append((i, j))
                    num_edges += 1
        if verbose:
            print("\nEdges:")
            for i in range(len(self.edges)):
                edge = self.edges[i]
                print(f" {i:2} {edge}")

    def computeFaces(self, verbose=False):
        """
        Compute faces of the polyhedron.

        For each vertex, find all faces formed by edges connecting to that vertex.
        A face exists when a loop of vertices are mutually connected on a common plane.

        Each face is stored only once with vertices in right-handed order, lowest index first.
        """
        if len(self.vertices) < 3:
            print("Error: Need at least 3 vertices to compute faces.")
            self.faces = []
            return

        if len(self.edges) < 3:
            print("Error: Need at least 3 edges to compute faces. Call computeEdges() first.")
            self.faces = []
            return

        # Build adjacency list: for each vertex, list of connected vertices
        adjacency = [set() for _ in range(len(self.vertices))]
        for i, j in self.edges:
            adjacency[i].add(j)
            adjacency[j].add(i)

        if verbose:
            print(f"\nVertex neighbors:")
            for i in range(len(adjacency)):
                neighbors = adjacency[i]
                print(f" {i:2} {neighbors}")

        # Find all faces
        loop_set = set()
        for b in range(len(self.vertices)):
            # Get all vertices connected to vertex i
            neighborsB = list(adjacency[b])

            for a in neighborsB:
                AB = self.vertices[b] - self.vertices[a]

                num_faces_found = 0
                for c in neighborsB:
                    if c == a:
                        continue
                    BC = self.vertices[c] - self.vertices[b]

                    # ABC starts Face iff all other neighborsB are on one side of the ABC plane
                    axisABC = glm.normalize(glm.cross(AB, BC))
                    num_positive = 0
                    num_negative = 0
                    c_starts_face = True
                    for d in neighborsB:
                        if d == a or d == c:
                            continue
                        BD = self.vertices[d] - self.vertices[b]
                        if glm.dot(axisABC, BD) < 0:
                            num_negative += 1
                            if num_positive > 0:
                                c_starts_face = False
                                break
                        else:
                            num_positive += 1
                            if num_negative > 0:
                                c_starts_face = False
                                break

                    if c_starts_face:
                        loop_indices = [a, b, c]
                        d = b
                        e = c
                        DE = self.vertices[e] - self.vertices[d]
                        while e != a:
                            neighborsE = list(adjacency[e])
                            for f in neighborsE:
                                if f == a:
                                    e = f
                                    break
                                if f in loop_indices:
                                    continue
                                EF = self.vertices[f] - self.vertices[e]
                                axisDEF = glm.normalize(glm.cross(DE, EF))
                                dot_error = math.fabs(1.0 - math.fabs(glm.dot(axisABC, axisDEF)))
                                if math.fabs(1.0 - math.fabs(glm.dot(axisABC, axisDEF))) < 0.001:
                                    # f is on the Face plane
                                    loop_indices.append(f)
                                    e = f
                                    break

                        # rotate indices to make lowest index first
                        loop_indices = sort_indices(loop_indices)

                        # make sure loop is right-handed
                        JK = self.vertices[loop_indices[1]] - self.vertices[loop_indices[0]]
                        KL = self.vertices[loop_indices[2]] - self.vertices[loop_indices[1]]
                        axisJKL = glm.normalize(glm.cross(JK, KL))
                        if glm.dot(self.vertices[loop_indices[0]], axisJKL) < 0.0:
                            # this is a left-handed loop and we need to make it right-handed
                            # keep the first loop element where it is but reverse the order of the rest
                            loop_indices = [loop_indices[0]] + loop_indices[1:][::-1]

                        loop_set.add(tuple(loop_indices))
                        num_faces_found += 1
                        if num_faces_found == 2:
                            break;

        # Convert set to list of Face objects
        self.faces = [Face(loop) for loop in sorted(loop_set)]

        if verbose:
            print("\nFaces:")
            for i, face in enumerate(self.faces):
                print(f" {i:2} {face}")


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

    for shape_name in shapes:
        print("=" * 60)
        print(shape_name.upper())
        print("=" * 60)
        shape = Polyhedron(shape_name)
        shape.orientAndAlign(verbose=True)
        shape.computeEdges(verbose=True)
        shape.computeFaces(verbose=True)
        print("\n")
