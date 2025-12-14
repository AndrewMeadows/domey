#
# face.py -- Face class for representing polygonal faces of polyhedra
#
# This class stores vertex indices that form a polygonal face of a polyhedron.
#

class Face:
    """
    A class representing a polygonal face of a polyhedron.

    Stores a list of vertex indices that define the face. The indices reference
    vertices in a Polyhedron's vertex list.
    """

    def __init__(self, vertex_indices):
        """
        Initialize a face with a list of vertex indices.

        Args:
            vertex_indices: List or tuple of vertex indices that form the face
        """
        self.vertex_indices = list(vertex_indices)

    def __repr__(self):
        """String representation of the face."""
        return f"Face({self.vertex_indices})"

    def __str__(self):
        """Human-readable string representation."""
        indices_str = ", ".join(str(idx) for idx in self.vertex_indices)
        return f"({indices_str})"

    def numVertices(self):
        """
        Return the number of vertices in this face.

        Returns:
            The number of vertices
        """
        return len(self.vertex_indices)

    def containsVertex(self, vertex_index):
        """
        Check if the face contains a given vertex index.

        Args:
            vertex_index: The vertex index to check

        Returns:
            True if the vertex is part of this face, False otherwise
        """
        return vertex_index in self.vertex_indices

    def containsEdge(self, edge):
        """
        Check if the face contains a given edge.

        Args:
            edge: A tuple (i, j) representing an edge between vertices i and j

        Returns:
            True if the edge is part of this face, False otherwise
        """
        i, j = edge
        return i in self.vertex_indices and j in self.vertex_indices

    def getEdges(self):
        """
        Returns:
            Array of Edges (pairs of indices into a Polyhedron's vertex list) in right-hand order.
        """
        edges = []
        for i in range(len(self.vertex_indices) - 1):
            a = self.vertex_indices[i]
            b = self.vertex_indices[i+1]
            # the indices in an "Edge" are always sorted small to high
            if a < b:
                edge = (a, b)
            else:
                edge = (b, a)
            edges.append(edge)

        a = self.vertex_indices[-1]
        b = self.vertex_indices[0]
        if a < b:
            edge = (a, b)
        else:
            edge = (b, a)
        edges.append(edge)

        return edges
