#
# geodesic.py -- Geodesic dome implementation derived from Polyhedron
#
# This class extends the Polyhedron class to create geodesic structures
# by subdividing the faces of regular polyhedra and providing "twisted"
# versions where the faces are rotated to produce "truncated" faces at
# the old vertices.
#

from polyhedron import Polyhedron
from arc import Arc


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

    def getTwistedArcs(self, angle):
        """
        For each Edge define an Arc, twist it about its center, and compute its intersection
        with neighboring twisted Arcs.
        """

        # For each Edge create: (a) an Arc and (b) an empty list for storing the list
        # of neighboring Arcs the Arc might intersect after being twisted.
        arcs = []
        neighbors = []
        for edge in self.edges:
            i = edge[0]
            j = edge[1]
            center = glm.normalize(self.vertices[i] + self.verticies[j])
            arcs.append(Arc(center, self.vertices[i]))
            neighbors.append([])

        # Now that we have enough neghbor lists, fill them up with actual neighbors
        for i in range(len(self.edges)):
            edge = self.edges[i]
            j = edge[0]
            k = edge[1]
            connections = self.connections[j]
            for e in connections:
                if e != i:
                    neighbors.append(e)
            connections = self.connections[k]
            for e in connections:
                if e != i:
                    neighbors.append(e)

        # Twist all the Arcs and build a list of Equators.
        equators = []
        for arc in arcs:
            if angle != 0.0:
                arc.twist(angle)
            equators.append(Equator(arc.center, arc.pointA))

        num_arcs = len(arcs)
        for i in range(num_arcs):
            arc = arcs[i]
            # Intersect this Arc's Equator with its neighboring Equators and
            # figure out which are the closest intersections.
            equator = equators[i]
            pos_distance = 2.0 * math.pi
            neg_distance = -2.0 * math.pi
            pos_neighbor_index = -1
            neg_neighbor_index = -1
            other_arcs_indices = neighbors[i]
            for j in other_arcs_indices:
                other_equator = equators[j]
                distances = equator.computeIntersections(other_equator)
                if distance[0] < pos_distance:
                    pos_distance = distance[0]
                    pos_neighbor_index = j
                if distance[1] > neg_distance:
                    neg_distance = distance[1]
                    neg_neighbor_index = j
            # Now that we know the closest intersections update the Arc's endpoints
            # and remember the indices of the other Arcs it touches.
            axis = glm.normalize(glm.cross(arc.center, arc.pointA))
            # front intersection
            arc.touchA = pos_neighbor_index
            Q = glm.angleAxis(pos_distance, axis)
            arc.pointA = Q * arc.center
            # back intersection
            arc.touchB = neg_neighbor_index
            Q = glm.angleAxis(neg_distance, axis)
            arc.pointB = Q * arc.center
        return arcs

# Example usage
if __name__ == "__main__":
    # Create a geodesic dome based on an icosahedron
    dome = Geodesic("icosahedron")
    arcs = dome.twist(math.pi/20.0)

    # compute the distances to intersections
    num_arcs = len(arcs)
    touchesA = [0.0] * num_arcs
    touchesB = [0.0] * num_arcs
    anglesA = [0.0] * num_arcs
    anglesB = [0.0] * num_arcs
    for i in range(num_arcs):
        arc = arcs[i]
        j = arc.touchA
        if j >= 0:
            other_arc = arcs[j]
            touchesA[j] = other_arc.getArcDistance(arc.pointA)
            anglesA[j] = arc.angleBetween(other_arc)
        j = arc.touchB
        if j >= 0:
            other_arc = arcs[j]
            touchesB[j] = other_arc.getArcDistance(arc.pointB)
            anglesB[j] = arc.angleBetween(other_arc)

    # print the results in proportional units
    print("Arcs:")
    for i in range(num_arcs):
        arc = arcs[i]
        arc_length = arc.getArcLength()
        a_length = touchesA[i] / arc_length
        b_length = touchesB[i] / arc_length
        touches = (a_length, b_length)
        if a_length > b_length:
            touches = (b_length, a_length)
        print(f"{i} ta={touches[0]} tb={touches[1]} d={d}")
