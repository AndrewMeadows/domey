#
# polyhedron.py -- Object-oriented implementation for regular polyhedron vertex computation
#
# This class encapsulates the common logic for computing vertices of regular polyhedra,
# normalizing them, and aligning them to standard orientations.
#

import math
import glm


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
        self.computeConnectivity()

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
            print(f"\nAll normalized {self.shape_name} vertices:")
            for i, vertex in enumerate(normalized_vertices):
                print(f"Vertex {i:2}: ({vertex.x:8.5f}, {vertex.y:8.5f}, {vertex.z:8.5f})")

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

            if verbose:
                print(f"\nQuaternion Q: ({Q.w:8.5f}, {Q.x:8.5f}, {Q.y:8.5f}, {Q.z:8.5f})")

            # Apply rotation Q to all normalized vertices
            rotated_vertices = [Q * vertex for vertex in normalized_vertices]

            if verbose:
                print("\nRotated vertices:")
                for i, vertex in enumerate(rotated_vertices):
                    print(f"Vertex {i:2}: ({vertex.x:8.5f}, {vertex.y:8.5f}, {vertex.z:8.5f})")

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

                if verbose:
                    print(f"\nQuaternion Q2: ({Q2.w:8.5f}, {Q2.x:8.5f}, {Q2.y:8.5f}, {Q2.z:8.5f})")

                # Apply rotation Q2 to all rotated vertices
                aligned_vertices = [Q2 * vertex for vertex in rotated_vertices]

                if verbose:
                    print("\nAligned vertices:")
                    for i, vertex in enumerate(aligned_vertices):
                        print(f"Vertex {i:2}: ({vertex.x:8.5f}, {vertex.y:8.5f}, {vertex.z:8.5f})")
            else:
                if verbose:
                    print(f"\nVertex 1 x-component ({v1.x:.6f}) is already close to YZ plane - no rotation needed.")
                aligned_vertices = rotated_vertices

                if verbose:
                    print("\nAligned vertices (same as rotated vertices):")
                    for i, vertex in enumerate(aligned_vertices):
                        print(f"Vertex {i:2}: ({vertex.x:8.5f}, {vertex.y:8.5f}, {vertex.z:8.5f})")
        else:
            if verbose:
                print("\nOne of the vertices is already aligned with the z-axis - no rotation needed.")
            aligned_vertices = normalized_vertices

            if verbose:
                print("\nAligned vertices (same as normalized vertices):")
                for i, vertex in enumerate(aligned_vertices):
                    print(f"Vertex {i:2}: ({vertex.x:8.5f}, {vertex.y:8.5f}, {vertex.z:8.5f})")

        # Replace original vertices with aligned vertices
        self.vertices = aligned_vertices

    def computeConnectivity(self, verbose=False):
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
        if verbose:
            print(f"\nMinDistance={min_dist}")

        edge_length = min_dist
        threshold = 1.4 * edge_length

        # For each Vertex its Connections is a list of Edges (by index) that share the Vertex.
        # We initialize the all of Connections here and fill them as Edges are found.
        self.connections = []
        for vertex in self.vertices:
            self.connections.append([])

        # For each Vertex, check all Vertices with higher indices
        self.edges = []
        num_edges = 0
        for i in range(len(self.vertices)):
            for j in range(i + 1, len(self.vertices)):
                dist = glm.distance(self.vertices[i], self.vertices[j])
                if dist <= threshold:
                    # Add Edge with lower index first
                    self.edges.append((i, j))
                    # Add Edge index to connections
                    self.connections[i].append(num_edges)
                    self.connections[j].append(num_edges)
                    num_edges += 1
        if verbose:
            print("Edges:")
            for edge in self.edges:
                print(f"{edge}")


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
        shape.computeConnectivity(verbose=True)
        print("\n")
