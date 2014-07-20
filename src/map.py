from __future__ import division

from math import floor
from itertools import chain, combinations

import networkx as nx

from poisson.poisson_disk import sample_poisson_uniform
from tools import Coords, Size, WINDOW_SIZE, distance_squared, sandwich
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


def constrain(given_point, bounds, m, rightward=True):
    x0, y0 = given_point
    if rightward:
        # second point is to the right
        if m > 0:
            # up and to the right
            vertical_border_distance = bounds.h - y0
            if abs(m * (bounds.w - x0)) > vertical_border_distance:
                # closest border is up
                dy = vertical_border_distance
                dx = dy / m if m else 0
            else:
                # closest border is right
                dx = bounds.w - x0
                dy = dx * m
        else:
            # down and to the right
            vertical_border_distance = y0
            if abs(m * (bounds.w - x0)) > vertical_border_distance:
                # closest border is down
                dy = -vertical_border_distance
                dx = dy / m if m else 0
            else:
                # closest border is right
                dx = bounds.w - x0
                dy = dx * m
    else:
        # second point is to the left
        if m < 0:
            # up and to the left
            vertical_border_distance = abs(bounds.h - y0)
            if abs(m * x0) > vertical_border_distance:
                # closest border is up
                dy = vertical_border_distance
                dx = -dy / m if m else 0
            else:
                # closest border is left
                dx = -x0
                dy = dx * m
        else:
            # down and to the left
            vertical_border_distance = y0
            if abs(m * x0) > vertical_border_distance:
                # closest border is down
                dy = -vertical_border_distance
                dx = dy / m if m else 0
            else:
                # closest border is left
                dx = -x0
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
                print("easy:", verts[v1], verts[v2])
                walls.append((Coords(*verts[v1]), Coords(*verts[v2])))
                continue
            if self.pointOutsideBounds(*verts[v1]):
                v1 = -1
            elif self.pointOutsideBounds(*verts[v2]):
                v2 = -1
            # apparently v1, v2 go left to right
            # calculate an edge point using slope = -a/b
            a, b, __ = abcs[i]
            m = -a / b if b else 0
            p0 = verts[v1 if v1 != -1 else v2]
            if self.pointOutsideBounds(*p0):
                continue
            p1 = constrain(p0, self.dims, -a/b, rightward=(v1 != -1))
            if any([self.pointOutsideBounds(*p) for p in (p0, p1)]):
                print(p0, m)
            walls.append((p0, p1))
        return walls

    def __getattr__(self, attrname):
        return getattr(self.graph, attrname)
