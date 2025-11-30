# Domey

A Python module for computing vertices and arcs of geodesic spheres based on twist-truncated regular polyhedra.

## Features

- **Regular Polyhedra**: Generate vertices, edges, and faces for all five Platonic solids:
  - Tetrahedron (4 faces)
  - Hexahedron/Cube (6 faces)
  - Octahedron (8 faces)
  - Dodecahedron (12 faces)
  - Icosahedron (20 faces)

- **Automatic Normalization**: All vertices are normalized to the unit sphere

- **Standard Orientation**: Polyhedra are automatically oriented with:
  - First vertex aligned to the positive z-axis
  - Second vertex aligned to the YZ plane

- **Geodesic Structures**: Create geodesic domes by:
  - Computing arcs along polyhedron edges
  - Twisting arcs around their centers
  - Finding intersections between twisted arcs

- **Arc Computations**: Work with great circle arcs on the unit sphere, including:
  - Arc-arc intersections
  - Trimming arcs to endpoints
  - Computing distances along arcs

### Dependencies

- Python >= 3.8
- PyGLM >= 2.5.0

## Usage

```python
from geodesic import Geodesic

# Create a geodesic dome based on an icosahedron
dome = Geodesic('icosahedron')

# Orient and align the vertices
dome.orientAndAlign()

# Compute edges and faces
dome.computeEdges()
dome.computeFaces()

# Twist the arcs and compute intersections
# This creates a truncated polyhedron effect
twist_angle = 0.6534  # radians
arcs = dome.computeTwistedArcs(twist_angle, verbose=True)
```

## Module Structure

- `polyhedron.py`: Core `Polyhedron` class for regular polyhedra
- `geodesic.py`: `Geodesic` class extending `Polyhedron` for geodesic structures
- `arc.py`: `Arc` class for great circle arcs on the unit sphere
- `face.py`: `Face` class representing polygonal faces of a Polyhedron

## Mathematical Background

### Polyhedron Orientation

Polyhedra are normalized and oriented using quaternion rotations:
1. All vertices are normalized to unit length (radius = 1.0)
2. The first vertex is rotated to align with the positive z-axis
3. A second rotation around the z-axis aligns the second vertex to the YZ plane
4. Vertices are sorted by z-coordinate (descending) and then by angle in the XY plane

### Arc Intersections

Arc intersections on the unit sphere are computed by:
1. Finding the intersection of two great circle planes
2. Projecting along the intersection line to find two intersection points
3. Computing arc distances from the pivot to each intersection
4. Selecting the shortest distance for trimming

### Geodesic Construction

Geodesic structures are created by:
1. Generating arcs along each edge of a base polyhedron
2. Twisting each arc around its center by a specified angle
3. Computing intersections between neighboring twisted arcs
4. The resulting intersection points form the vertices of a truncated polyhedron

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
