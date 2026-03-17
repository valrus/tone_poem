import pytest

from ..map import constrain
from ..tools import Coords, Size


@pytest.fixture
def bounds() -> Size:
    return Size(12, 8)


def test_go_right_off_top(bounds: Size):
    assert constrain(
        given_point=Coords(8, 6),
        slope=2,
        bounds=bounds,
        rightward=True,
    ) == Coords(9, 8)


def test_go_right_off_right_positive_slope(bounds: Size):
    assert constrain(
        given_point=Coords(8, 6),
        slope=1 / 4,
        bounds=bounds,
        rightward=True,
    ) == Coords(12, 7)


def test_go_right_off_right_negative_slope(bounds: Size):
    assert constrain(
        given_point=Coords(8, 6),
        slope=-1,
        bounds=bounds,
        rightward=True,
    ) == Coords(12, 2)


def test_go_right_off_bottom(bounds: Size):
    assert constrain(
        given_point=Coords(8, 6),
        slope=-2,
        bounds=bounds,
        rightward=True,
    ) == Coords(11, 0)


def test_go_left_off_bottom(bounds: Size):
    assert constrain(
        given_point=Coords(8, 6),
        slope=2,
        bounds=bounds,
        rightward=False,
    ) == Coords(5, 0)


def test_go_left_off_left_positive_slope(bounds: Size):
    assert constrain(
        given_point=Coords(8, 6),
        slope=1 / 4,
        bounds=bounds,
        rightward=False,
    ) == Coords(0, 4)


def test_go_left_off_left_negative_slope(bounds: Size):
    assert constrain(
        given_point=Coords(4, 6),
        slope=-1 / 4,
        bounds=bounds,
        rightward=False,
    ) == Coords(0, 7)


def test_go_left_off_top(bounds: Size):
    assert constrain(
        given_point=Coords(8, 6),
        slope=-2,
        bounds=bounds,
        rightward=False,
    ) == Coords(7, 8)


def test_infinite_slope(bounds: Size):
    assert constrain(
        given_point=Coords(8, 6),
        slope=float("inf"),
        bounds=bounds,
        rightward=True,
    ) == Coords(8, 8)


def test_negative_infinite_slope(bounds: Size):
    assert constrain(
        given_point=Coords(8, 6),
        slope=-float("inf"),
        bounds=bounds,
        rightward=True,
    ) == Coords(8, 0)
