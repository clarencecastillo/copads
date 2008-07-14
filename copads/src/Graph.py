"""
File containing classes for use in graph algorithms.

Copyright (c) Maurice H.T. Ling <mauriceling@acm.org>
Date created: 17th August 2005
"""

from Matrix import Matrix
from PriorityDictionary import PriorityDictionary
from CopadsExceptions import VertexNotFoundError, NotAdjacencyGraphMatrixError
from CopadsExceptions import GraphEdgeSizeMismatchError, GraphParameterError
from CopadsExceptions import FunctionParameterTypeError


class Graph:
    graph = {}
    
    def __init__(self, **kwarg):
        """
        Initialization method. It can accept the following keyword parameters:
        
        adjacency (Matrix - list of list) - an adjacency matrix, with vertices 
            as the first row - row count is 1 more than column count
        digraph (boolean) - state whether the input values is to construct a 
            graph (True for directional graph). Default = False.
        edges (list of 2-element tuples) - defines a list of edges where each 
            tuple is (<source>, <destination>). Uses digraph parameter.
        graph (dictionary of dictionary) - graph as 
            {<source> : <destination dictionary>} 
            where
            <destination dictionary> ::= {<destination> : <attribute>}.
        vertices (list) - list of vertices (nodes).
        """
        if not kwarg.has_key('digraph'): kwarg['digraph'] = False
        if kwarg.has_key('graph'): 
            self.graph = kwarg['graph']
        elif kwarg.has_key('vertices'): 
            self.makeGraphFromVertices(kwarg['vertices'])
        elif kwarg.has_key('edges'): 
            if kwarg['digraph'] == True:
                self.makeGraphFromEdges1(kwarg['edges'])
            else: self.makeGraphFromEdges2(kwarg['edges'])
        elif kwarg.has_key('adjacency'): 
            self.makeGraphFromAdjacency(kwarg['adjacency'])
        else: self.graph = {}
        
    def makeGraphFromAdjacency(self, adj):
        """
        Constructs a graph from an adjacency (adj) matrix, which is given
        as a list of list (rows). 
        The first row of the matrix contains a list of the vertices; hence,
        there will be n+1 rows and n-columns in the given matrix.
        """
        vertices = adj.pop(0)
        for l in adj:
            if len(l) != len(vertices): raise GraphEdgeSizeMismatchError
        ends = {}
        for row in range(len(adj)):
            for col in range(len(adj[row])):
                if adj[row][col] > 0: ends[vertices[col]] = adj[row][col]
            self.graph[vertices[row]] = ends
            ends = {}
    
    def makeGraphFromVertices(self, vertices):
        """
        Initialize a list of nodes (vertices) without edges.
        """
        if type(vertices) != list: raise GraphParameterError('Vertices must \
                                    be a list')
        for vertex in vertices: self.graph[vertex] = {}
    
    def makeGraphFromEdges1(self, edges):
        """
        Constructs a directional graph from edges (a list of tuple).
        Each tuple contains 2 vertices. 
        For example, P -> Q is written as ('P', 'Q')."""
        if type(edges) != list: raise GraphParameterError('Edges must be a \
                                list of tuples')
        from Set import Set
        from Matrix import Matrix
        vertices = list(Set([x[0] for x in edges] + [x[1] for x in edges]))
        adj = Matrix(len(vertices))
        adj = adj.m
        for e in edges:
            row = vertices.index(e[0])
            col = vertices.index(e[1])
            # fill values into lower triangular matrix
            adj[row][col] = adj[row][col] + 1
        adj.insert(0, vertices)
        self.makeGraphFromAdjacency(adj)
        
    def makeGraphFromEdges2(self, edges):
        """
        Constructs an un-directional graph from edges (a list of tuple).
        Each tuple contains 2 vertices.
        An un-directional graph is implemented as a directional graph where
        each edges runs both directions.
        """
        if type(edges) != list: raise GraphParameterError('Edges must be a \
                                list of tuples')
        from Set import Set
        from Matrix import Matrix
        vertices = list(Set([x[0] for x in edges] + [x[1] for x in edges]))
        adj = Matrix(len(vertices))
        adj = adj.m
        for e in edges:
            row = vertices.index(e[0])
            col = vertices.index(e[1])
            # fill values into lower triangular matrix
            adj[row][col] = adj[row][col] + 1
            # repeat on the upper triangular matrix for undirectional graph
            adj[col][row] = adj[col][row] + 1
        adj.insert(0, vertices)
        self.makeGraphFromAdjacency(adj)
        
    def isVertices(self, vlist):
        """
        Checks whether each element in vlist is a vertex (node) of
        the graph. It returns a dictionary of 
        <element of vlist> : <True | False>
        """
        result = {}
        from Set import Set
        vlist = list(Set(vlist))
        for v in vlist:
            if self.graph.has_key(v): result[v] = True
            else: result[v] = False
        return result

    def Dijkstra(self, start,end=None):
        """
        Find shortest paths from the start vertex to all vertices nearer than 
        or equal to the end.
        
        Dijkstra's algorithm is only guaranteed to work correctly when all 
        edge lengths are positive. This code does not verify this property 
        for all edges (only the edges seen before the end vertex is reached), 
        but will correctly compute shortest paths even for some graphs with 
        negative edges, and will raise an exception if it discovers that a 
        negative edge has caused it to make a mistake.
        """
    
        D = {}    # dictionary of final distances
        P = {}    # dictionary of predecessors
        Q = PriorityDictionary()   # est.dist. of non-final vert.
        Q[start] = 0
        
        for v in Q:
            D[v] = Q[v]
            if v == end: break
            
            for w in self.graph[v]:
                vwLength = D[v] + self.graph[v][w]
                if w in D:
                    if vwLength < D[w]:
                        raise ValueError, \
      "Dijkstra: found better path to already-final vertex"
                elif w not in Q or vwLength < Q[w]:
                    Q[w] = vwLength
                    P[w] = v
        
        return (D,P)
                
    def shortestPath(self,start,end):
        """
        Find a single shortest path from the given start vertex
        to the given end vertex. The output is a list of the vertices 
        in order along the shortest path.
        """
    
        D,P = self.Dijkstra(start,end)
        Path = []
        while 1:
            Path.append(end)
            if end == start: break
            end = P[end]
        Path.reverse()
        return Path
       
    def RandomGraph(self, nodes, edges, maxweight = 100.0):
        """
        Generates a graph of random edges.
        
        nodes (list or integer) - list of nodes or number of nodes in the 
            random graph
        edges (integer) - number of edges to generate in the random graph
        maxweight (float) - maximum weight of each edge
        """
        import random
        nodes_size = 0
        if type(nodes) == int:
            adjacency = [range(nodes)]
            nodes_size = nodes
            for node in range(nodes):
                adjacency.append([0 for x in range(nodes)])
        elif type(nodes) == list:
            adjacency = nodes
            nodes_size = len(nodes)
            for node in range(nodes_size):
                adjacency.append([0 for x in range(nodes_size)])
        else: raise FunctionParameterTypeError('nodes can only be a list \
                or integer')
        count = 0
        while count <= edges:
            edge = (int(random.uniform(0, nodes_size)) + 1, 
                    int(random.uniform(0, nodes_size)),
                    int(random.uniform(0, 1) * maxweight))
            if adjacency[edge[0]][edge[1]] == 0:
                adjacency[edge[0]][edge[1]] = edge[2]
                count = count + 1
        self.makeGraphFromAdjacency(adjacency)