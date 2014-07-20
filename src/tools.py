from collections import namedtuple

Size = namedtuple("Size", "w h")
Coords = namedtuple("Coords", "x y")
Rect = namedtuple("Rect", "x y w h")
Quad = namedtuple("Rect", "x1 y1 x2 y2")

WINDOW_SIZE = Size(1200, 800)


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
