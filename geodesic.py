#
# geodesic.py -- Geodesic dome implementation derived from Polyhedron
#
# This class extends the Polyhedron class to create geodesic spheres
# based on the five regular polyhedra and providing "twisted" versions
# where the base faces are rotated to introduce "truncated" faces at the
# base vertices.
#

import math
import glm
from polyhedron import Polyhedron
from arc import Arc, angle_between

RAD_TO_DEG = 180.0 / math.pi

class Geodesic(Polyhedron):
    """
    A class representing a geodesic sphere based on a regular polyhedron.

    Inherits from Polyhedron and adds methods for twisting arcs to produce
    "twisted and truncated" structures.
    """

    def __init__(self, shape_type=None):
        """
        Initialize a geodesic dome with an optional base shape type.

        Args:
            shape_type: Optional string specifying the base polyhedron shape
                       ('tetrahedron', 'hexahedron', 'octahedron',
                        'dodecahedron', 'icosahedron').
        """
        super().__init__(shape_type)


    def computeTwistedArcs(self, angle, verbose=False):
        """
        For each Edge define an Arc, twist it about its center, and compute its intersection
        with neighboring twisted Arcs.
        """
        # For each Edge create: (a) an Arc and (b) an empty list for storing
        # "neighbor" Arcs by index.  A "neighbor" is any other Arc that shares
        # an endpoint.
        arcs = []
        arc_index = 0
        if verbose:
            print(f"\nTwist arcs with angle={angle:.4} ({angle * RAD_TO_DEG:.4} degrees)")
        for edge in self.edges:
            i = edge[0]
            j = edge[1]
            center = glm.normalize(self.vertices[i] + self.vertices[j])
            arcs.append(Arc(center, self.vertices[i], arc_index))
            if verbose:
                arc_length = angle_between(self.vertices[i], self.vertices[j])
            arc_index = arc_index + 1

        # Twist all the Arcs and build a list of resulting Equators.
        if angle != 0.0:
            for arc in arcs:
                arc.twist(angle)

        # For each Face trim and intersect each Arc against its neighbors
        for face in self.faces:
            edges = face.getEdges()
            # Find the indices of the Face edges
            edge_indices = []
            for edge in edges:
                for i in range(len(self.edges)):
                    if edge == self.edges[i]:
                        edge_indices.append(i)

            # Trim and intersect each Arc against its face-neighbor in right-hand direction
            for i in range(1, len(edge_indices)):
                j = edge_indices[i - 1]
                k = edge_indices[i]
                arcs[j].trimAndIntersect(arcs[k])
            j = edge_indices[-1]
            k = edge_indices[0]
            arcs[j].trimAndIntersect(arcs[k])

        if verbose:
            print("\nTwisted arcs:")
            for i in range(len(arcs)):
                arc = arcs[i]
                trims = (arc.trimA, arc.trimB)
                intersections = (arc.intersectionA, arc.intersectionB)
                arc_length = arc.trimA - arc.trimB
                relative_intersections = (arc.intersectionA / arc_length, arc.intersectionB / arc_length)
                print(f" {i:2} l={arc_length} d={trims} i={intersections} ri={relative_intersections}")

        return arcs


    def computeIntersectionAngle(self, arcs):
        """
        Computes the small angle between two adjacent arcs.
        """
        angle = 0.0
        if len(self.faces) > 0:
            face = self.faces[0]
            edges = face.getEdges()

            # Find the indices of the Face edges
            edge_indices = []
            for edge in edges:
                for i in range(len(self.edges)):
                    if edge == self.edges[i]:
                        edge_indices.append(i)
            arcA = arcs[edge_indices[0]]
            arcB = arcs[edge_indices[1]]
            angle = arcA.getIntersectionAngle(arcB)
        return angle


# Example usage
if __name__ == "__main__":
    shapes = [
        "tetrahedron",
        "hexahedron",
        "octahedron",
        "dodecahedron",
        "icosahedron"
    ]

    # Corresponding twist angles which produce intersections
    # at points 1/3 the length of the arcs
    angles = [
        0.3598,
        0.3103,
        0.5485,
        0.2908,
        0.6534
    ]

    verbose = False

    for i in range(len(shapes)):
        shape_name = shapes[i]

        # Create a geodesic dome
        dome = Geodesic(shape_name)
        dome.orientAndAlign(verbose)
        dome.computeEdges(verbose)
        dome.computeFaces(verbose)

        # Twist the arcs
        twist_angle = angles[i]
        arcs = dome.computeTwistedArcs(twist_angle, verbose=True)
        intersection_angle = dome.computeIntersectionAngle(arcs)

        print(f"\nintersection_angle={intersection_angle:.4} ({intersection_angle * RAD_TO_DEG:.4} degrees)")

