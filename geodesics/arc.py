#
# arc.py -- Object-oriented implementation for tracking circle intersections on the UnitSphere
#

import math
from pyglm import glm


# helper
# return the angle between two vectors
def angle_between(vA, vB):
    dot = glm.dot(glm.normalize(vA), glm.normalize(vB))
    angle = math.acos(glm.clamp(dot, -1.0, 1.0))
    return angle

# helper
# return True when two points are are nearly identical
def almost_equal(pointA, pointB):
    CLOSE_ENOUGH = 0.0001
    return glm.distance(pointA, pointB) < CLOSE_ENOUGH


class Arc:
    """
    A class representing an Arc on the surface of a UnitSphere, defined by two points:
        pivot
        point (defines positive direction according to right-hand rule)

    An Arc also stores meta data about other Acs it touches:
        trimA = distance to nearest intersection with other Arcs in positive direction
        trimB = distance to nearest intersection with other Arcs in negative direction
        intersectionA = distance in positive direction to intersection from other Arc
        intersectionB = distance in negative direction to intersection from other Arc
    """

    def __init__(self, pivot, point, index=0):
        """
        Initializes an Arc.

        Args:
            pivot: point on Arc as glm.vec3, invariant under twist
            point: second point on the arc as glm.vec3 (defines positive direction)
            index: index of this Arc in a Geodesic (optional)

            Raise ValueError: If Args are not expected types.
        """
        # Validate that points are of type glm.vec3
        if not isinstance(pivot, glm.vec3):
            raise ValueError(f"pivot must be of type glm.vec3, got {type(pivot)}")
        if not isinstance(point, glm.vec3):
            raise ValueError(f"point must be of type glm.vec3, got {type(point)}")
        if not isinstance(index, int):
            raise ValueError(f"index must be of type int, got {type(index)}")

        # Normalize to UnitSphere
        self.pivot = glm.normalize(pivot)
        self.point = glm.normalize(point)

        # This Arc's index in a Geodesic
        self.index = index

        self.resetEndpoints()


    def __str__(self):
        return (f"Arc(index={self.index}, "
                f"pivot={self.pivot}, "
                f"point={self.point}, "
                f"trimA={self.trimA:.4f}, "
                f"trimB={self.trimB:.4f})")

    def resetEndpoints(self):
        # Nearest known intersection distances with other Arcs
        self.trimA = math.pi
        self.trimB = -math.pi

        # Distances to points where other Arcs interesect this one.
        self.intersectionA = 1.0
        self.intersectionB = -1.0

    def getAxis(self):
        return glm.normalize(glm.cross(self.pivot, self.point))

    def getEndPoints(self):
        axis = self.getAxis()
        Q = glm.angleAxis(self.trimA, axis)
        pointA = Q * self.pivot
        Q = glm.angleAxis(self.trimB, axis)
        pointB = Q * self.pivot
        return (pointA, pointB)

    def getIntersectionPoints(self):
        return [self.getPoint(self.intersectionA), self.getPoint(self.intersectionB)]

    def twist(self, angle):
        """
        Rotates the points about pivot by angle.
        """
        Q = glm.angleAxis(angle, self.pivot)
        self.point = glm.normalize(Q * self.point)

        # A twist invalidates endpoints and intersections
        self.resetEndpoints()


    def getProjectedDistance(self, point):
        """
        Compute the arc-distance between self.pivot to projection of point.
        """
        # project point onto the Plane of the Arc's equator
        axis = self.getAxis()
        projected_point = glm.normalize(point - glm.dot(point, axis) * axis)
        # Measure angle along the Arc.
        angle = angle_between(self.pivot, projected_point)
        other_axis = glm.normalize(glm.cross(self.pivot, projected_point))
        d = glm.dot(other_axis, axis)
        if glm.dot(other_axis, axis) < 0.0:
            angle = -angle
        # Since we're on the unit sphere radians are distance.
        return angle


    def getIntersectionAngle(self, other_arc):
        """
        Compute the small angle between two arcs.
        """
        axis = self.getAxis()
        other_axis = other_arc.getAxis()
        # We want the small angle, so make sure the dot product is positive
        dot = glm.dot(axis, other_axis)
        if dot < 0.0:
            other_axis = -other_axis
        return angle_between(axis, other_axis)


    def computeDistances(self, other_arc):
        """
        Compute the intersection distances between self and other_arc as a tuple of
        two distances around the circle starting from self.pivot.
        The distances will be sorted shortest absolute distance first.
        """

        # The intersections are computed by determining the intersection between the
        # circle planes and then projecting along that line by the radius in either
        # direction. Since this is all done on the UnitSphere the distances along the arc
        # to the intersections are equivalent to the radians between self.pivot and the
        # intersection points.
        axis = self.getAxis()
        other_axis = other_arc.getAxis()
        direction = glm.normalize(glm.cross(axis, other_axis))
        alpha = self.getProjectedDistance(direction)
        beta = self.getProjectedDistance(-direction)

        # sort distances (positive, negative)
        distances = (alpha, beta)
        if alpha < 0.0:
            distances = (beta, alpha)
        return distances


    # returns a point on the circle at angle from pivot
    # using right-hand-rule about axis=self.pivot.cross(self.point)
    def getPoint(self, angle):
        axis = self.getAxis()
        Q = glm.angleAxis(angle, axis)
        return Q * self.pivot


    # computes intersections with other_arc and reduces the endpoints as necessary
    def trimAndIntersect(self, other_arc):
        """
        # Compute self's trim_distance to nearest intersection point with other_arc.
        """
        # The intersections are computed by determining the intersection between the
        # circle planes and then projecting along that line by the radius in either
        # direction. Since this is all done on the UnitSphere the distances along the arc
        # to the intersections are equivalent to the radians between self.pivot and the
        # intersection points.
        axis = self.getAxis()
        other_axis = other_arc.getAxis()
        intersection_point = glm.normalize(glm.cross(axis, other_axis))
        alpha = self.getProjectedDistance(intersection_point)
        beta = self.getProjectedDistance(-intersection_point)

        # we want to use the shortest trim_distance
        trim_distance = alpha
        if math.fabs(beta) < math.fabs(alpha):
            trim_distance = beta
            intersection_point = -intersection_point
        if trim_distance > 0.0:
            self.trimA = trim_distance
        else:
            self.trimB = trim_distance

        # store intersection distance on other_arc
        intersection_distance = other_arc.getProjectedDistance(intersection_point)
        if intersection_distance > 0.0:
            other_arc.intersectionA = intersection_distance
        else:
            other_arc.intersectionB = intersection_distance

    def addIntersection(self, point):
        # compute distance to point
        distance = self.getProjectedDistance(point)
        # figure out if the distance is A or B
        if distance > 0.0:
            self.intersectionA = distance
        else:
            self.intersectionB = distance

if __name__ == "__main__":
    x = glm.vec3(1.0, 0.0, 0.0)
    y = glm.vec3(0.0, 1.0, 0.0)
    z = glm.vec3(0.0, 0.0, 1.0)
    xyz = glm.normalize(x + y + z)

    arcA = Arc(xyz, z)
    arcB = Arc(x, y)
    arcC = Arc(y, z)
    arcD = Arc(z, x)

    print(f"arcA:")
    print(f"  pivot={arcA.pivot}")
    print(f"  point={arcA.point}")

    # trim arcA
    arcA.trimAndIntersect(arcB)
    arcA.trimAndIntersect(arcC)
    arcA.trimAndIntersect(arcD)

    print(f"\ntrimmed arcA:")
    print(f"  endA={arcA.trimA}")
    print(f"  endB={arcA.trimB}")

    # Rotate arc by 2pi/3
    arcA.twist(2.0 * math.pi / 3.0)
    print(f"\ntwisted arcA:")
    print(f"  pivot={arcA.pivot}")
    print(f"  point={arcA.point}")

    # trim arcA
    arcA.trimAndIntersect(arcB)
    arcA.trimAndIntersect(arcC)
    arcA.trimAndIntersect(arcD)

    print(f"\ntrimmed twisted arcA:")
    print(f"  endA={arcA.trimA}")
    print(f"  endB={arcA.trimB}")
