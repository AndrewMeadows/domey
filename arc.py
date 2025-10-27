#
# arc.py -- Object-oriented implementation for tracking arc intersections on the UnitSphere
#

import math
import glm


# helper
def angle_between(direction_A, direction_B):
    dot = glm.dot(direction_A, direction_B)
    angle = math.acos(glm.clamp(dot, -1.0, 1.0))
    if dot < 0.0:
        angle = -angle
    return angle

class Equator:
    """
    A class representing a GreatCircle on the UnitSphere.

    Provides a method to compute intersections between two Equators.
    """

    def __init__(self, start, end):
        """
        Initializes an Equator of the UnitSphere that passes through two points
        (start and end) on the sphere's surface.

        Args:
            start: point on the Equator as glm.vec3
            end: a different point on the Equator as glm.vec3
        """
        # Validate that points are of type glm.vec3
        if not isinstance(start, glm.vec3):
            raise ValueError(f"start must be of type glm.vec3, got {type(start)}")
        if not isinstance(end, glm.vec3):
            raise ValueError(f"end must be of type glm.vec3, got {type(end)}")

        # Normalize points to project them onto the UnitSphere
        self.start = glm.normalize(start)
        self.end = glm.normalize(end)

    def computeIntersections(self, other_equator):
        """
        Compute the intersection distances between self and other_equator as a tuple of
        two distances around the Equator starting from self.start in a counter-clockwise
        direction.
        """

        # The intersections are computed by determining the intersection between the
        # Equator planes and then projecting along that line by the radius in either
        # direction. Since this is all done on the UnitSphere the distances along the arc
        # to the intersections are equivalent to the angles between self.start and the
        # intersection points.
        normalA = glm.cross(self.start, self.end)
        normalB = glm.cross(other_equator.start, other_equator.end)
        intersection = glm.normalize(glm.cross(normalA, normalB))
        angleA = angle_between(self.start, intersection)
        angleB = angle_between(self.start, -intersection)

        # always put the angle with smaller magnitude first
        distances = (angleA, angleB)
        if math.fabs(angleB) < math.fabs(angleA):
            distances = (angleB, angleA)
        return distances

class Arc:
    """
    A class representing an Arc on the surface of a UnitSphere, defined by two points
    and the Plane that intersects the UnitSphere at its center and the Arc points.

    An Arc also store meta data about other Acs it touches.
    """

    def __init__(self, pointA, pointB, angle=0.0):
        """
        Initializes an Arc from pointA to pointB, computes its center, then twist its
        points about its center by angle.

        Args:
            pointA: first point as glm.vec3
            pointB: second point as glm.vec3
            angle: angle to twist pointsA,B about the Arc's center

            Raise ValueError: If Args are not expected types.
        """
        # Validate that points are of type glm.vec3
        if not isinstance(pointA, glm.vec3):
            raise ValueError(f"pointA must be of type glm.vec3, got {type(pointA)}")
        if not isinstance(pointB, glm.vec3):
            raise ValueError(f"pointB must be of type glm.vec3, got {type(pointB)}")
        if not isinstance(angle, float):
            raise ValueError(f"angle must be of type float, got {type(angle)}")

        # Normalize points to project them onto the UnitSphere
        self.pointA = glm.normalize(pointA)
        self.pointB = glm.normalize(pointB)

        # Compute the center of the arc (midpoint between A and B on the sphere)
        # The center lies on the great circle passing through A and B
        center = (self.pointA + self.pointB) / 2.0
        self.center = glm.normalize(center)

        if angle != 0.0:
            self.twist(angle)

        # The touches represent indices to other Arcs in a Geodesic this Arc touches
        # at pointA and pointB respectively.  We initialize them to an invalid index
        # value (-1) to indicate they haven't yet been set.
        self.touchA = -1
        self.touchB = -1

    def twist(self, angle):
        """
        Rotates the points about center by angle.
        """
        Q = glm.angleAxis(angle, self.center)
        self.pointA = glm.normalize(Q * self.pointA)
        self.pointB = glm.normalize(Q * self.pointB)
        # A twist invalidates the touches (they need to be recomputed)
        self.touchA = -1
        self.touchB = -1

    def getArcLength(self):
        """
        Compute the arc-length of this Arc.
        """
        axis = glm.normalize(glm.cross(self.pointA, self.pointB))
        return angle_between(self.pointA, self.pointB)

    def getArcDistanceToPoint(self, point):
        """
        Compute the arc-distance between self.center to projection of point.
        """
        # project point onto the Plane of the Arc's Circle
        axis = glm.normalize(glm.cross(self.pointA, self.pointB))
        point = glm.normalize(point - glm.dot(point, axis) * axis)
        # Measure arc-distance along the arc, which is equivalent to the angle between
        return angle_between(self.center, point)

    def angleBetweenArc(self, other_arc):
        """
        Compute the small angle between two arcs.
        """
        axis = glm.normalize(glm.cross(self.pointA, self.pointB))
        other_axis = glm.normalize(glm.cross(other_arc.pointA, other_arc.pointB))
        # We want the small angle, so make sure the dot product is positive
        dot = glm.dot(axis, other_axis)
        if dot < 0.0:
            other_axis = -other_axis
        return angle_between(axis, other_axis)


# Example usage
if __name__ == "__main__":
    # Create two points on the UnitSphere
    pointA = glm.vec3(1.0, 0.0, 0.0)  # Point on x-axis
    pointB = glm.vec3(0.0, 1.0, 0.0)  # Point on y-axis

    # Create an arc between these points
    arc = Arc(pointA, pointB)

    print(f"Arc created:")
    print(f"  Point_A={arc.pointA}")
    print(f"  Point_B={arc.pointB}")
    print(f"  Center={arc.center}")

    # Create an Equator with start at pointA
    equatorA = Equator(arc.pointA, arc.pointB)

    # Rotate arc by pi/2
    arc.twist(math.pi / 2)
    print(f"\nAfter rotation:")
    print(f"  Point_A={arc.pointA}")
    print(f"  Point_B={arc.pointB}")
    print(f"  Center={arc.center}")

    # Create a second Equator on rotated arc
    equatorB = Equator(arc.pointA, arc.pointB)

    # Intersections should be (+pi/4 and -3pi/4)
    intersections = equatorA.computeIntersections(equatorB)
    print(f"\nIntersections of two equators:")
    print(f"  intersection_A={intersections[0]}")
    print(f"  intersection_B={intersections[1]}")

