#
# geodesic.py -- Geodesic dome built on top of a Polyhedron
#
# A Geodesic owns a base Polyhedron (self.polyhedron) and creates geodesic
# spheres from it by twisting the arcs of the geodesic faces to open new
# "truncated" faces at the base Vertices.
#

import math
from pyglm import glm
from meshics.graph import Graph, sort_indices
from meshics.face import Face
from .polyhedron import Polyhedron
from .arc import Arc, angle_between

RAD_TO_DEG = 180.0 / math.pi

def find_nearest_index(vertices, point):
    """
    returns index of vertex closest to point
    """
    index = 0
    nearest_distance = glm.distance(vertices[0], point)
    for i in range(len(vertices)):
        distance = glm.distance(vertices[i], point)
        if distance < nearest_distance:
            nearest_distance = distance
            index = i
    return index

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
        self.arcs = []
        self.geo_graph = Graph(verbose)
        self.polyhedron = Polyhedron(shape_type, verbose)
        self.geo_vertices = []
        self.arc_segments = []
        self.setTwistAngle(0.0)

    def getPolyhedron(self):
        """Return the base Polyhedron this geodesic was built from."""
        return self.polyhedron


    def setTwistAngle(self, angle):
        self.twist_angle = angle
        if self.twist_angle == 0.0:
            self.arcs = []
            self.geo_graph = Graph(self.verbose)
            self.geo_vertices = []
            self.arc_segments = []
        else:
            self._computeTwistedArcs()
            self._computeGeoVertices()
            self._computeArcSegments()
            self._computeGeoGraph()

    def _computeTwistedArcs(self):
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
            print(f"\nTwist arcs with angle={self.twist_angle:.4} ({self.twist_angle * RAD_TO_DEG:.4} degrees)")
        for edge in polyhedron.edges:
            i = edge[0]
            j = edge[1]
            center = glm.normalize(polyhedron.vertices[i] + polyhedron.vertices[j])
            arcs.append(Arc(center, polyhedron.vertices[i], arc_index))
            arc_index = arc_index + 1

        # Twist all the Arcs and build a list of resulting Equators.
        if self.twist_angle != 0.0:
            for arc in arcs:
                arc.twist(self.twist_angle)

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
        self.geo_vertices = []
        for arc in self.arcs:
            [point_A, point_B] = arc.getEndPoints()
            self.geo_vertices.append(point_A)
            self.geo_vertices.append(point_B)


    def _computeArcSegments(self):
        self.arc_segments = []
        for arc in self.arcs:
            # get the points along the arc
            #
            # A-----C------D------B
            #
            [point_A, point_B] = arc.getEndPoints()
            [point_C, point_D] = arc.getIntersectionPoints()
            dist_AC = glm.distance(point_A, point_C)
            dist_AD = glm.distance(point_A, point_D)
            if dist_AD < dist_AC:
                point_C, point_D = point_D, point_C

            # find the indices
            indexA = find_nearest_index(self.geo_vertices, point_A)
            indexB = find_nearest_index(self.geo_vertices, point_B)
            indexC = find_nearest_index(self.geo_vertices, point_C)
            indexD = find_nearest_index(self.geo_vertices, point_D)

            # append the segments
            self.arc_segments.append(sorted((indexA, indexC)))
            self.arc_segments.append(sorted((indexC, indexD)))
            self.arc_segments.append(sorted((indexD, indexB)))

        self.arc_segments.sort()

    def _computeGeoGraph(self):
        """
        Computes faces of twist-truncated geodesic
        """
        self.geo_graph.vertices = self.geo_vertices
        self.geo_graph.edges = self.arc_segments
        self.geo_graph.computeFaces()

        # Graph.computeFaces() uses adjacency of vertices on the known edges to determine
        # the "faces", however this will produce some faces with "unnecessary" vertices
        # when projected to the surface of the unit sphere.
        #
        # If it has only necessary vertices it looks something like this:
        #
        # (a)-----(b)
        #  |     .'
        #  |   .'
        #  | .'
        # (c)
        #
        # Whereas a face with unnecessary vertices has an extra vertex in each arc:
        #
        # (a)---(b)----(c)      (f)---(a)----(b)
        #  |          .'         |          .'
        #  |        .'           |        .'
        # (f)    (d)            (e)    (c)
        #  |   .'                |   .'
        #  | .'                  | .'
        # (e)                   (d)
        #
        # We want to identify the vertices in the middle of arcs and trim them out
        # leaving just the corners, while maintaining their cyclic order.
        #
        faces = self.geo_graph.faces
        trimmed_faces = []
        for face in faces:
            indices = list(face.vertex_indices)
            if len(indices) == 3:
                # trivial case: a triangle has no mid-arc vertices to remove
                trimmed_faces.append(face)
                continue

            # The axis of the great-circle arc through two points is their cross
            # product. axes[i] is the arc from indices[i] to its successor, taken
            # cyclically so axes[-1] wraps from the last vertex back to the first.
            n = len(indices)
            axes = []
            for i in range(n):
                point_a = self.geo_graph.vertices[indices[i]]
                point_b = self.geo_graph.vertices[indices[(i + 1) % n]]
                axes.append(glm.normalize(glm.cross(point_a, point_b)))

            # Vertex indices[i] is "unnecessary" (a mid-arc point) when the arc
            # arriving at it (axes[i-1]) and the arc leaving it (axes[i]) lie on the
            # same great circle, i.e. their axes are parallel or anti-parallel. The
            # adjacency is cyclic, so indices[0]'s arriving arc is axes[-1].
            new_indices = []
            for i in range(n):
                arriving = axes[(i - 1) % n]
                leaving = axes[i]
                parallel = abs(1.0 - abs(glm.dot(arriving, leaving))) < 0.01
                if not parallel:
                    new_indices.append(indices[i])
            # Trimming can drop the leading vertex; restore the Face invariant
            # that the lowest index leads (cyclic order is preserved).
            trimmed_faces.append(Face(sort_indices(new_indices)))

        self.geo_graph.faces = trimmed_faces


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

## Example usage
#if __name__ == "__main__":
#    shapes = [
#        "tetrahedron",
#        "hexahedron",
#        "octahedron",
#        "dodecahedron",
#        "icosahedron"
#    ]
#
#    # Corresponding twist angles which produce intersections
#    # at points 1/3 the length of the arcs
#    angles = [
#        0.3598,
#        0.3103,
#        0.5485,
#        0.2908,
#        0.6534
#    ]
#
#    verbose = False
#
#    for i in range(len(shapes)):
#        shape_name = shapes[i]
#
#        # Create a geodesic dome
#        dome = Geodesic(shape_name, verbose)
#
#        # Twist the arcs
#        dome.setTwistAngle(angles[i])
#        intersection_angle = dome.computeIntersectionAngle(arcs)
#
#        print(f"\nintersection_angle={intersection_angle:.4} ({intersection_angle * RAD_TO_DEG:.4} degrees)")

