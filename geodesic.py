#
# geodesic.py -- Geodesic dome implementation derived from Polyhedron
#
# This class extends the Polyhedron class to create geodesic structures
# by subdividing the faces of regular polyhedra and providing "twisted"
# versions where the faces are rotated to produce "truncated" faces at
# the old vertices.
#

import math
import glm
from polyhedron import Polyhedron
from arc import Arc, angle_between


class Geodesic(Polyhedron):
    """
    A class representing a geodesic dome structure.

    Inherits from Polyhedron and adds methods for subdividing faces
    and creating geodesic structures.
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
            print(f"\nTwist arcs with angle={angle}")
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
            edges = face.get_edges()
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

# Example usage
if __name__ == "__main__":
    shape_name = "tetrahedron"

    # Create a geodesic dome
    dome = Geodesic(shape_name)
    dome.orientAndAlign(verbose=True)
    dome.computeEdges(verbose=True)
    dome.computeFaces(verbose=True)

    # twist the arcs
    #twist_angle = math.pi/20.0
    twist_angle = 0.3595
    arcs = dome.computeTwistedArcs(twist_angle, verbose=True)

