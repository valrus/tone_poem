import os
from collections import namedtuple
from math import sqrt

Size = namedtuple("Size", "w h")
Rect = namedtuple("Rect", "x y w h")
Quad = namedtuple("Quad", "x1 y1 x2 y2")

WINDOW_SIZE = Size(1200, 800)

ROOT_DIR = os.path.dirname(__file__)


class Coords(namedtuple("Coords", "x y")):
    def __add__(self, other):
        return Coords(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coords(self.x - other.x, self.y - other.y)

    def __rmul__(self, scalar):
        try:
            return Coords(scalar * self.x, scalar * self.y)
        except:
            raise NotImplemented


class Vect(namedtuple("Vect", "p1 p2")):
    def __abs__(self):
        return sqrt(distance_squared(*self))


def x_iterator():
    yield 'left'
    yield 'center'
    yield 'right'


def y_iterator():
    yield 'top'
    yield 'center'
    yield 'bottom'


def distance_squared(v1, v2):
    return (v2.x - v1.x) ** 2 + (v2.y - v1.y) ** 2


def sandwich(min, x, max):
    if x < min:
        return min
    elif x > max:
        return max
    else:
        return x


def group(lst, n):
    for i in range(0, len(lst), n):
        val = lst[i:i+n]
        if len(val) == n:
            yield tuple(val)


def bezier(v1, v2, steps=5):
    """Generate points along the 2nd-order Bezier curve between two vectors.
    """
    steps -= 1
    r1, r2 = v1.p1, v2.p1
    d1, d2 = (1 / steps) * (v1.p2 - v1.p1), (1 / steps) * (v2.p2 - v2.p1)
    for i in range(steps):
        yield r1 + (i / steps) * (r2 - r1)
        r1 += d1
        r2 += d2
    yield r2
