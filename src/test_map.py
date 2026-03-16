import unittest

from map import constrain
from tools import Coords, Size


class test_constrain(unittest.TestCase):
    def setUp(self):
        self.bounds = Size(12, 8)

    def test_go_right_off_top(self):
        self.assertEqual(
            constrain(
                given_point=(8, 6),
                slope=2,
                bounds=self.bounds,
                rightward=True,
            ),
            Coords(9, 8),
        )

    def test_go_right_off_right_positive_slope(self):
        self.assertEqual(
            constrain(
                given_point=(8, 6),
                slope=1 / 4,
                bounds=self.bounds,
                rightward=True,
            ),
            Coords(12, 7),
        )

    def test_go_right_off_right_negative_slope(self):
        self.assertEqual(
            constrain(
                given_point=(8, 6),
                slope=-1,
                bounds=self.bounds,
                rightward=True,
            ),
            Coords(12, 2),
        )

    def test_go_right_off_bottom(self):
        self.assertEqual(
            constrain(
                given_point=(8, 6),
                slope=-2,
                bounds=self.bounds,
                rightward=True,
            ),
            Coords(11, 0),
        )

    def test_go_left_off_bottom(self):
        self.assertEqual(
            constrain(
                given_point=(8, 6),
                slope=2,
                bounds=self.bounds,
                rightward=False,
            ),
            Coords(5, 0),
        )

    def test_go_left_off_left_positive_slope(self):
        self.assertEqual(
            constrain(
                given_point=(8, 6),
                slope=1 / 4,
                bounds=self.bounds,
                rightward=False,
            ),
            Coords(0, 4),
        )

    def test_go_left_off_left_negative_slope(self):
        self.assertEqual(
            constrain(
                given_point=(4, 6),
                slope=-1 / 4,
                bounds=self.bounds,
                rightward=False,
            ),
            Coords(0, 7),
        )

    def test_go_left_off_top(self):
        self.assertEqual(
            constrain(
                given_point=(8, 6),
                slope=-2,
                bounds=self.bounds,
                rightward=False,
            ),
            Coords(7, 8),
        )

    def test_infinite_slope(self):
        self.assertEqual(
            constrain(
                given_point=(8, 6),
                slope=float("inf"),
                bounds=self.bounds,
                rightward=True,
            ),
            Coords(8, 8),
        )

    def test_negative_infinite_slope(self):
        self.assertEqual(
            constrain(
                given_point=(8, 6),
                slope=-float("inf"),
                bounds=self.bounds,
                rightward=True,
            ),
            Coords(8, 0),
        )


if __name__ == "__main__":
    unittest.main()
