from __future__ import division

from math import floor
from itertools import chain, combinations

import networkx as nx

from poisson.poisson_disk import sample_poisson_uniform
from tools import Coords, Size, WINDOW_SIZE
from voronoi import computeDelaunayTriangulation, computeVoronoiDiagram

LONG_DISTANCE = 100000


def distance_squared(v1, v2):
    return (v2.x - v1.x) ** 2 + (v2.y - v1.y) ** 2


def intersect(s1, s2):
    # http://tinyurl.com/l2jcpj8
    a1, b1, a2, b2 = chain(s1, s2)
    x1, y1, x2, y2 = chain(a1, a2)
    dx1, dy1, dx2, dy2 = b1.x - x1, b1.y - y1, b2.x - x2, b2.y - y2
    vp = dx1 * dy2 - dx2 * dy1
    if vp == 0:
        return 0
    vx, vy = x2 - x1, y2 - y1
    return 1 if all([0 < (vx * dy2 - vy * dx2) / vp < 1,
                     0 < (vx * dy1 - vy * dx1) / vp < 1]) else 0


class GraphMap(object):
    def __init__(self, dims=WINDOW_SIZE):
        self.dims = Size(*dims)
        self.min_distance = sum(dims) / 15
        points = [
            Coords(floor(x), floor(y)) for x, y in
            sample_poisson_uniform(self.dims.w, self.dims.h,
                                   # Average divided by 5 seems reasonable
                                   self.min_distance,
                                   # Sample points for Poisson, arbitrary
                                   30)
        ]
        self.graph = nx.Graph()
        self.graph.add_nodes_from(points)
        for triangle in computeDelaunayTriangulation(points):
            self.graph.add_edges_from([
                (points[firstIndex], points[secondIndex])
                for firstIndex, secondIndex in combinations(triangle, 2)
            ])
        self.walls = self.computeWalls()
        self.removeMultiWallEdges()
        dist_squared = self.min_distance ** 2
        for e in self.graph.edges():
            if distance_squared(*e) > 2 * dist_squared:
                self.graph.remove_edge(*e)
                if not nx.is_connected(self.graph):
                    self.graph.add_edge(*e)

    def removeMultiWallEdges(self):
        for edge in self.graph.edges():
            crossings = 0
            for wall in self.walls:
                crossings += intersect(edge, wall)
                if crossings > 1:
                    self.graph.remove_edge(*edge)
                    break

    def computeWalls(self):
        walls = []
        verts, abcs, edges = computeVoronoiDiagram(self.graph.nodes())
        for i, v1, v2 in edges:
            if all(v != -1 for v in (v1, v2)):
                # edge has a vertex at either end, easy
                walls.append((Coords(*verts[v1]), Coords(*verts[v2])))
            else:
                # apparently v1, v2 go left to right
                # compute a point "at infinity" by using slope = -a/b
                a, b, __ = abcs[i]
                if v1 != -1:
                    x0, y0 = verts[v1]
                    # this can trigger divide by 0, account for that!
                    walls.append((
                        Coords(x0, y0),
                        Coords(x0 + (LONG_DISTANCE if b else 0),
                               y0 - (a * LONG_DISTANCE) / (b or 1))
                    ))
                else:
                    x0, y0 = verts[v2]
                    walls.append((
                        Coords(x0 - (LONG_DISTANCE if b else 0),
                               y0 + (a * LONG_DISTANCE) / (b or 1)),
                        Coords(x0, y0)
                    ))
                continue
        return walls

    def __getattr__(self, attrname):
        return getattr(self.graph, attrname)
