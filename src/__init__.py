"""
domey - A Python module for computing vertices and segments of multi-frequency geodesic shapes.

Combines the mesh building blocks (faces, graphs) with the geodesic tools
(regular polyhedra, arcs, geodesics) into a single package.
"""

from .face import Face
from .graph import Graph
from .polyhedron import Polyhedron
from .geodesic import Geodesic
from .arc import Arc, angle_between

__version__ = "0.1.0"
__all__ = ["Face", "Graph", "Polyhedron", "Geodesic", "Arc", "angle_between"]
