from __future__ import division

from math import floor
from itertools import chain, combinations

import networkx as nx

from poisson.poisson_disk import sample_poisson_uniform
from tools import Coords, Size, WINDOW_SIZE, distance_squared
from voronoi import computeDelaunayTriangulation, SiteList, Context, voronoi

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


def _secondneighbors(graph, start):
    """Generate all nodes that are distance 2 from the given one.

    (Note: this means it does not include nodes adjacent to the given one.
    """
    immediate_neighbors = set(n for n in nx.all_neighbors(graph, start))
    neighborhood = nx.ego_graph(graph, start, radius=2, center=False)
    for n in neighborhood.nodes_iter():
        if n not in immediate_neighbors:
            yield graph.node[n]


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
            self.graph.add_edges_from(chain(*[
                [(points[firstIndex], points[secondIndex]),
                 (points[secondIndex], points[firstIndex])]
                for firstIndex, secondIndex in combinations(triangle, 2)
            ]))
        self.walls, self.wall_dict = self.computeWalls()
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
                if wall is None:
                    continue
                crossings += intersect(edge, wall)
                if crossings > 1:
                    self.graph.remove_edge(*edge)
                    break

    def pointOutsideBounds(self, x, y):
        return any([x < 0, x > self.dims.w, y < 0, y > self.dims.h])

    def computeWalls(self):
        nodes = self.graph.nodes()

        # Poached from voronoi.computeVoronoiDiagram
        # http://stackoverflow.com/questions/9441007/how-can-i-get-a-dictionary-of-cells-from-this-voronoi-diagram-data
        site_list = SiteList(nodes)
        context = Context()
        voronoi(site_list, context)
        verts, abcs, edges = context.vertices, context.lines, context.edges
        walls = [None for _ in edges]
        # walls = []

        for i, v1, v2 in edges:
            if all(v != -1 and not self.pointOutsideBounds(*verts[v])
                   for v in (v1, v2)):
                # edge has a vertex at either end, easy
                walls[i] = (Coords(*verts[v1]), Coords(*verts[v2]))
                # walls.append((Coords(*verts[v1]), Coords(*verts[v2])))
                continue
            if self.pointOutsideBounds(*verts[v1]):
                v1 = -1
            elif self.pointOutsideBounds(*verts[v2]):
                v2 = -1
            # apparently v1, v2 go left to right
            # calculate an edge point using slope = -a/b
            a, b, _ = abcs[i]
            p0 = Coords(*verts[v1 if v1 != -1 else v2])
            if self.pointOutsideBounds(*p0):
                # Add a dummy wall to keep the indexing the same
                walls[i] = (p0, p0)
                continue
            # need to handle case where b is 0
            p1 = Coords(*constrain(p0, (-a / b) if b else (-a * float('inf')),
                        self.dims, rightward=(v1 != -1)))
            walls[i] = (p0, p1)
            # walls.append((p0, p1))

        wall_dict = dict()
        for site, edge_list in context.polygons.items():
            wall_dict[nodes[site]] = [walls[i] for i, _, _ in edge_list
                                      if walls[i] is not None]

        return walls, wall_dict

    def neighbors(self, node):
        return self.graph.neighbors(node)

    def _cleanup_nodes(self, nodeType):
        pass

    def add_labels(self, nodeType):
        nx.set_node_attributes(self.graph, 'label', {
            n: nodeType() for n in self.graph.nodes_iter()
        })
        self._cleanup_nodes(nodeType)

    def edge_label(self, n1, n2):
        return self.node_label(n1) - self.node_label(n2)

    def node_label(self, n):
        return self.graph.node[n]['label']

    def __getattr__(self, attrname):
        return getattr(self.graph, attrname)


class ForestMap(GraphMap):
    def _cleanup_nodes(self, nodeType):
        """Avoid ambiguous edges from any node.

        This means satisfying the following constraint:
        No node may have more than one adjacent node with the same value.
        """
        for center in nx.nodes_iter(self.graph):
            seen = set()
            for neighbor in nx.all_neighbors(self.graph, center):
                node = self.graph.node[neighbor]
                if node['label'].name in seen:
                    illegal = set(n['label'].name for n in _secondneighbors(self.graph, neighbor))
                    # Not a fan of reaching in and using to_shorthand here, but...
                    node['label'].value = [c for c in nodeType.POSSIBLE_VALUES
                                           if not c.to_shorthand() in illegal]
                else:
                    seen.add(node['label'].name)
