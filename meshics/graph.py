#
# graph.py -- Graph of vertices, edges and faces
#
# A Graph holds a set of vertices, the edges connecting them, the per-vertex
# neighbor adjacency, and the faces (loops of vertices). Subclasses decide how
# the vertices and edges are produced; computing faces from existing vertices
# and edges is general enough to live here.
#

import math
import glm
from .face import Face


# helper
def sort_indices(index_list):
    """Rotate the index_list to make the lowest element first."""
    min_value = min(index_list)
    min_index = index_list.index(min_value)
    return index_list[min_index:] + index_list[:min_index]


class Graph:
    """
    A graph of vertices connected by edges, grouped into faces.

    Holds the vertices/edges/neighbors/faces members. Subclasses populate the
    vertices and edges (the connectivity rule varies by graph type); deriving
    the faces from vertices and edges is shared logic and lives in computeFaces().
    """

    def __init__(self, verbose=False):
        """
        Initialize an empty Graph.

        Args:
            verbose: When True, subclasses print intermediate computation to stdout.
        """
        self.verbose = verbose
        self.vertices = []      # list of vertex positions
        self.edges = []         # pairs of vertex indices connected by line segment
        self.neighbors = []     # for each vertex index: list of other vertex indices that pair as an edge
        self.faces = []         # list of vertices that form a minimal loop

    def computeFaces(self):
        """
        Compute Faces of the Graph from its vertices and edges.

        For each Vertex, find all Faces formed by Edges connecting to that Vertex.
        A Face exists when a loop of Vertices are mutually connected on a common plane.

        Each Face is stored only once with Vertices in right-handed order, lowest index first.
        """
        if len(self.vertices) < 3:
            print("Error: Need at least 3 Vertices to compute Faces.")
            self.faces = []
            return

        if len(self.edges) < 3:
            print("Error: Need at least three Edges to compute Faces. Call computeEdges() first.")
            self.faces = []
            return

        # Build adjacency list: for each vertex, list of connected Vertices
        adjacency = [set() for _ in range(len(self.vertices))]
        for i, j in self.edges:
            adjacency[i].add(j)
            adjacency[j].add(i)

        if self.verbose:
            print(f"\nVertex neighbors:")
            for i in range(len(adjacency)):
                neighbors = adjacency[i]
                print(f" {i:2} {neighbors}")
        self.neighbors = adjacency

        # Find all faces
        loop_set = set()
        for b in range(len(self.vertices)):
            # Get all vertices connected to vertex i
            neighborsB = list(self.neighbors[b])

            for a in neighborsB:
                AB = self.vertices[b] - self.vertices[a]

                num_faces_found = 0
                for c in neighborsB:
                    if c == a:
                        continue
                    BC = self.vertices[c] - self.vertices[b]

                    # ABC starts Face iff all other neighborsB are on one side of the ABC plane
                    axisABC = glm.normalize(glm.cross(AB, BC))
                    num_positive = 0
                    num_negative = 0
                    c_starts_face = True
                    for d in neighborsB:
                        if d == a or d == c:
                            continue
                        BD = self.vertices[d] - self.vertices[b]
                        if glm.dot(axisABC, BD) < 0:
                            num_negative += 1
                            if num_positive > 0:
                                c_starts_face = False
                                break
                        else:
                            num_positive += 1
                            if num_negative > 0:
                                c_starts_face = False
                                break

                    if c_starts_face:
                        loop_indices = [a, b, c]
                        d = b
                        e = c
                        DE = self.vertices[e] - self.vertices[d]
                        while e != a:
                            neighborsE = list(self.neighbors[e])
                            for f in neighborsE:
                                if f == a:
                                    e = f
                                    break
                                if f in loop_indices:
                                    continue
                                EF = self.vertices[f] - self.vertices[e]
                                axisDEF = glm.normalize(glm.cross(DE, EF))
                                dot_error = math.fabs(1.0 - math.fabs(glm.dot(axisABC, axisDEF)))
                                if math.fabs(1.0 - math.fabs(glm.dot(axisABC, axisDEF))) < 0.001:
                                    # f is on the Face plane
                                    loop_indices.append(f)
                                    e = f
                                    break

                        # rotate indices to make lowest index first
                        loop_indices = sort_indices(loop_indices)

                        # make sure loop is right-handed
                        JK = self.vertices[loop_indices[1]] - self.vertices[loop_indices[0]]
                        KL = self.vertices[loop_indices[2]] - self.vertices[loop_indices[1]]
                        axisJKL = glm.normalize(glm.cross(JK, KL))
                        if glm.dot(self.vertices[loop_indices[0]], axisJKL) < 0.0:
                            # this is a left-handed loop and we need to make it right-handed
                            # keep the first loop element where it is but reverse the order of the rest
                            loop_indices = [loop_indices[0]] + loop_indices[1:][::-1]

                        loop_set.add(tuple(loop_indices))
                        num_faces_found += 1
                        if num_faces_found == 2:
                            break;

        # Convert set to list of Face objects
        self.faces = [Face(loop) for loop in sorted(loop_set)]

        if self.verbose:
            print("\nFaces:")
            for i, face in enumerate(self.faces):
                print(f" {i:2} {face}")
