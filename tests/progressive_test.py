import unittest
import progressive


class TestProgressive(unittest.TestCase):

    def test_disconnected(self):
        tiles = {(0, 0), (0, 1), (3, 3)}
        res = progressive.find_disconnected(tiles)
        assert res == {(3, 3)}, f"Got {res}"

    def test_find_groups(self):
        tiles = {(0, 0), (0, 1), (3, 3)}
        res = progressive.find_groups(tiles)
        ans = {frozenset({(0, 0), (0, 1)}), frozenset({(3, 3)})}
        assert res == ans, f"Got {res}"

    def test_group_of(self):
        tiles = {(0, 0), (0, 1), (3, 3)}
        res = progressive.group_of(tiles, (0, 0))
        assert res == {(0, 0), (0, 1)}, f"Got {res}"

    def test_neighbours(self):
        tiles = {(0, 0), (0, 1), (3, 3)}
        res = progressive.neighbours(tiles, (0, 0))
        assert res == {(0, 0), (0, 1)}, f"Got {res}"
