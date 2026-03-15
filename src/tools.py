import os
from dataclasses import astuple
from itertools import chain
from math import sqrt

from kivy.metrics import Metrics
from pydantic.dataclasses import dataclass

import voronoi


@dataclass(frozen=True)
class Scalable:
    @property
    def display_tuple(self):
        return (x * Metrics.dp for x in self)

    def __iter__(self):
        return iter(astuple(self))


@dataclass(frozen=True)
class Size(Scalable):
    w: int
    h: int

    @property
    def dw(self):
        return self.w * Metrics.dp

    @property
    def dh(self):
        return self.h * Metrics.dp


@dataclass(frozen=True)
class Rect(Scalable):
    x: float
    y: float
    w: float
    h: float

    @property
    def dx(self):
        return self.x * Metrics.dp

    @property
    def dy(self):
        return self.y * Metrics.dp

    @property
    def dw(self):
        return self.w * Metrics.dp

    @property
    def dh(self):
        return self.h * Metrics.dp


@dataclass(frozen=True)
class Quad(Scalable):
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def dx1(self):
        return self.x1 * Metrics.dp

    @property
    def dy1(self):
        return self.y1 * Metrics.dp

    @property
    def dx2(self):
        return self.x2 * Metrics.dp

    @property
    def dy2(self):
        return self.y2 * Metrics.dp


WINDOW_SIZE = Size(1600, 900)

ROOT_DIR = os.path.dirname(__file__)

CONFIG_INI = "config.ini"


@dataclass(frozen=True)
class Coords(Scalable):
    x: float
    y: float

    @property
    def dx(self):
        return self.x * Metrics.dp

    @property
    def dy(self):
        return self.y * Metrics.dp

    def __add__(self, other):
        return Coords(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coords(self.x - other.x, self.y - other.y)

    def __rmul__(self, scalar: int):
        return Coords(scalar * self.x, scalar * self.y)

    def __truediv__(self, dividend: float):
        return Coords(self.x / dividend, self.y / dividend)

    def __lt__(self, other: "Coords"):
        return astuple(self) < astuple(other)


@dataclass(frozen=True)
class Vect(Scalable):
    p1: float
    p2: float

    def __abs__(self):
        return sqrt(distance_squared(*self))


def x_iterator():
    yield "left"
    yield "center"
    yield "right"


def y_iterator():
    yield "top"
    yield "center"
    yield "bottom"


def distance_squared(v1, v2):
    return (v2.x - v1.x) ** 2 + (v2.y - v1.y) ** 2


def sandwich(min, x, max):
    if x < min:
        return min
    elif x > max:
        return max
    else:
        return x


def intersect(s1, s2):
    """Determine if two line segments intersect.

    s1 and s2 should be pairs of Coords.
    """
    # http://tinyurl.com/l2jcpj8
    a1, b1, a2, b2 = chain(s1, s2)
    x1, y1, x2, y2 = chain(a1, a2)
    dx1, dy1, dx2, dy2 = b1.x - x1, b1.y - y1, b2.x - x2, b2.y - y2
    vp = dx1 * dy2 - dx2 * dy1
    if vp == 0:
        return 0
    vx, vy = x2 - x1, y2 - y1
    return (
        1
        if all(
            [
                0 < (vx * dy2 - vy * dx2) / vp < 1,
                0 < (vx * dy1 - vy * dx1) / vp < 1,
            ]
        )
        else 0
    )


def sorted_pair(p1, p2):
    return (p1, p2) if p1 < p2 else (p2, p1)


def vertices_to_edges(verts):
    """Convert a list of vertices of a polygon to a list of edges of same.

    The output is in the form of a list of 4-float lists,
    suitable for passing to glsl as vec4s.
    """
    return [sorted_pair(verts[-1], verts[0])] + [
        sorted_pair(*t) for t in list(pairs(verts))
    ]


def edge_to_vec4(verts):
    """Convert 2 vertices to a 4-float list."""
    return [float(x) for x in chain.from_iterable(verts)]


def edges_to_vec4s(edges):
    return [edge_to_vec4(edge) for edge in edges]


def pairs(lst):
    """Get a list of pairs of adjacent elements in a list."""
    return zip(lst, lst[1:])


def group(lst, n):
    for i in range(0, len(lst), n):
        val = lst[i : i + n]
        if len(val) == n:
            yield tuple(val)


def bezier(v1, v2, steps=5):
    """Generate points along the 2nd-order Bezier curve between two vectors."""
    steps -= 1
    r1, r2 = v1.p1, v2.p1
    d1, d2 = (1 / steps) * (v1.p2 - v1.p1), (1 / steps) * (v2.p2 - v2.p1)
    for i in range(steps):
        yield r1 + (i / steps) * (r2 - r1)
        r1 += d1
        r2 += d2
    yield r2


def point_to_line(p0, p1, p2):
    rise = p2.y - p1.y
    run = p2.x - p1.x
    return abs(rise * p0.x - run * p0.y + p2.x * p1.y - p2.y * p1.x) / sqrt(
        rise * rise + run * run
    )


def safe_divide(numer, denom):
    if denom == 0:
        return (-1 if numer < 0 else 1) * float("inf")
    else:
        return numer / denom


@dataclass
class WallCrossing:
    wall: tuple[Coords, Coords]
    path: tuple[voronoi.Vertex, voronoi.Vertex]
