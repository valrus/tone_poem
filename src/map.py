from __future__ import division

from math import floor
from itertools import chain, combinations

import networkx as nx

from poisson.poisson_disk import sample_poisson_uniform
from tools import Coords, Size, WINDOW_SIZE, distance_squared
from voronoi import computeDelaunayTriangulation, computeVoronoiDiagram

LONG_DISTANCE = 300


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


def constrain(given_point, m, bounds, rightward=True):
    """Given a line and bounds, return the point at the edge of those bounds.

    given_point should be a 2-tuple, m the slope of a line (which can be 0
    or positive or negative infinity). bounds should be an object with w and h
    attributes representing width and height.

    Returns a Coords object for the point lying on the rectangle with lower
    left corner at (0, 0) and dimensions given by bounds that intersects the
    line through given_point with slope m. There are two such points; return
    the right-most one if rightward is True and the left-most one otherwise.
    """
    x0, y0 = given_point
    up = (m > 0) if rightward else (m < 0)
    vertical_border_distance = (bounds.h - y0) if up else y0
    dx = (bounds.w - x0) if rightward else -x0
    rise = abs(m * dx)
    if rise > vertical_border_distance:
        dy = vertical_border_distance * (1 if up else -1)
        dx = dy / m if m else 0
    else:
        dy = dx * m
    return Coords(x0 + dx, y0 + dy)


class GraphMap(object):
    def __init__(self, margin=60, dims=WINDOW_SIZE):
        self.dims = Size(*dims)
        self.min_distance = sum(dims) / 18
        self.margin = margin
        points = [
            Coords(floor(x) + self.margin, floor(y) + self.margin) for x, y in
            sample_poisson_uniform(self.dims.w - self.margin * 2,
                                   self.dims.h - self.margin * 2,
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

    def pointOutsideBounds(self, x, y):
        return any([x < 0, x > self.dims.w, y < 0, y > self.dims.h])

    def computeWalls(self):
        walls = []
        verts, abcs, edges = computeVoronoiDiagram(self.graph.nodes())
        for i, v1, v2 in edges:
            if all(v != -1 and not self.pointOutsideBounds(*verts[v])
                   for v in (v1, v2)):
                # edge has a vertex at either end, easy
                walls.append((Coords(*verts[v1]), Coords(*verts[v2])))
                continue
            if self.pointOutsideBounds(*verts[v1]):
                v1 = -1
            elif self.pointOutsideBounds(*verts[v2]):
                v2 = -1
            # apparently v1, v2 go left to right
            # calculate an edge point using slope = -a/b
            a, b, __ = abcs[i]
            p0 = verts[v1 if v1 != -1 else v2]
            if self.pointOutsideBounds(*p0):
                continue
            # need to handle case where b is 0
            p1 = constrain(p0, (-a / b) if b else (-a * float('inf')),
                           self.dims, rightward=(v1 != -1))
            walls.append((p0, p1))
        return walls

    def neighbors(self, node):
        return self.graph.neighbors(node)

    def add_labels(self, nodeType):
        nx.set_node_attributes(self.graph, 'label', {
            n: nodeType() for n in self.graph.nodes_iter()
        })
        nx.set_edge_attributes(self.graph, 'label', {
            (n1, n2): self.graph.node[n1]['label'].delta(self.graph.node[n2]['label'])
            for n1, n2 in self.graph.edges()
        })

    def edge_label(self, n1, n2):
        return self.graph[n1][n2]['label']

    def node_label(self, n):
        return self.graph.node[n]['label']

    def __getattr__(self, attrname):
        return getattr(self.graph, attrname)
