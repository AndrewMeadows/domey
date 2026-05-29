#
# geodesic.py -- Geodesic dome built on top of a Polyhedron
#
# A Geodesic owns a base Polyhedron (self.polyhedron) and creates geodesic
# spheres from it by twisting the arcs of the geodesic faces to open new
# "truncated" faces at the base Vertices.
#

import math
import glm
from .polyhedron import Polyhedron
from .arc import Arc, angle_between

RAD_TO_DEG = 180.0 / math.pi

class Geodesic:
    """
    A class representing a geodesic sphere based on a regular polyhedron.

    Holds a base Polyhedron in self.polyhedron and adds methods for twisting
    arcs to produce "twisted and truncated" structures.
    """

    def __init__(self, shape_type=None, verbose=False):
        """
        Initialize a geodesic dome with an optional base shape type.

        Args:
            shape_type: Optional string specifying the base polyhedron shape
                       ('tetrahedron', 'hexahedron', 'octahedron',
                        'dodecahedron', 'icosahedron').
        """
        self.verbose = verbose
        self.polyhedron = Polyhedron(shape_type, verbose)
        self.setTwistAngle(0.0)

    def getPolyhedron(self):
        """Return the base Polyhedron this geodesic was built from."""
        return self.polyhedron


    def setTwistAngle(self, angle):
        self.twistAngle = angle
        self.computeTwistedArcs()
        self._computeGeoVertices()
        self._computeArcSegments()
        self._computeGeoFaces()

    def computeTwistedArcs(self):
        """
        For each Edge define an Arc, twist it about its center, and compute its intersection
        with neighboring twisted Arcs.
        """
        # For each Edge create: (a) an Arc and (b) an empty list for storing
        # "neighbor" Arcs by index.  A "neighbor" is any other Arc that shares
        # an endpoint.
        polyhedron = self.polyhedron
        arcs = []
        arc_index = 0
        if self.verbose:
            print(f"\nTwist arcs with angle={self.twistAngle:.4} ({self.twistAngle * RAD_TO_DEG:.4} degrees)")
        for edge in polyhedron.edges:
            i = edge[0]
            j = edge[1]
            center = glm.normalize(polyhedron.vertices[i] + polyhedron.vertices[j])
            arcs.append(Arc(center, polyhedron.vertices[i], arc_index))
            if self.verbose:
                arc_length = angle_between(polyhedron.vertices[i], polyhedron.vertices[j])
            arc_index = arc_index + 1

        # Twist all the Arcs and build a list of resulting Equators.
        if self.twistAngle != 0.0:
            for arc in arcs:
                arc.twist(self.twistAngle)

        # For each Polyhedron Face trim and intersect each Arc against its neighbors
        for face in polyhedron.faces:
            edges = face.getEdges()
            # Find the indices of the Face edges
            edge_indices = []
            for edge in edges:
                for i in range(len(polyhedron.edges)):
                    if edge == polyhedron.edges[i]:
                        edge_indices.append(i)

            # Trim and intersect each Arc against its face-neighbor in right-hand direction
            for i in range(1, len(edge_indices)):
                j = edge_indices[i - 1]
                k = edge_indices[i]
                arcs[j].trimAndIntersect(arcs[k])
            j = edge_indices[-1]
            k = edge_indices[0]
            arcs[j].trimAndIntersect(arcs[k])

        if self.verbose:
            print("\nTwisted arcs:")
            for i in range(len(arcs)):
                arc = arcs[i]
                trims = (arc.trimA, arc.trimB)
                intersections = (arc.intersectionA, arc.intersectionB)
                arc_length = arc.trimA - arc.trimB
                relative_intersections = (arc.intersectionA / arc_length, arc.intersectionB / arc_length)
                print(f" {i:2} l={arc_length} d={trims} i={intersections} ri={relative_intersections}")

        self.arcs = arcs

    def _computeGeoVertices(self):
        self.geoVertices = []
        self.faceSegments = []
        for arc in self.arcs:
            [pointA, pointB] = arc.getEndPoints()
            self.geoVertices.append(pointA)
            self.geoVertices.append(pointB)
        return 0

    def _computeArcSegments(self):
        self.faceSegments = []
        #for arc in self.arcs:
        #    [pointA, pointB] = arc.getEndPoints()
        #    [pointC, pointD] = arc.getIntersectionPoints()
        #    # BOOKMARK: compute indices of points by searching for the points in self.geoVertices
        #    #self.faceSegments.append(

    def _computeGeoFaces(self):
        # compute the line segments
        #for arc in self.arcs[]:
        # BOOKMARK

        # for each planar face on the base Polyhedron there will be a curved Geodesic face
        self.faceGeoFaces = []


        # for each vertex on the base Polyhedron there will be a curved Geodesic face
        self.vertexGeoFaces = []
        if self.twistAngle != 0.0:
            # TODO: compute the vertex-faces
            self.vertexGeoFaces = []

    def computeIntersectionAngle(self, arcs):
        """
        Computes the small angle between two adjacent arcs.
        """
        angle = 0.0
        polyhedron = self.polyhedron
        if len(polyhedron.faces) > 0:
            face = polyhedron.faces[0]
            edges = face.getEdges()

            # Find the indices of the Face edges
            edge_indices = []
            for edge in edges:
                for i in range(len(polyhedron.edges)):
                    if edge == polyhedron.edges[i]:
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
        dome = Geodesic(shape_name, verbose)

        # Twist the arcs
        dome.setTwistAngle(angles[i])
        intersection_angle = dome.computeIntersectionAngle(arcs)

        print(f"\nintersection_angle={intersection_angle:.4} ({intersection_angle * RAD_TO_DEG:.4} degrees)")

