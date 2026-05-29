"""
geodessy - A Python module for computing vertices and segments of multi-frequency geodesic shapes.

This module provides tools for working with regular polyhedra and geodesic structures
based on various fundamental polyhedra points.
"""

from .polyhedron import Polyhedron
from .geodesic import Geodesic
from .arc import Arc, angle_between

__version__ = "0.1.0"
__all__ = ["Polyhedron", "Geodesic", "Arc", "angle_between"]
