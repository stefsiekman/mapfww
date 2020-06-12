import unittest

from grid import Grid
from waypoint_map import WaypointMap


class WaypointMapTest(unittest.TestCase):

    @staticmethod
    def example_map():
        grid = Grid(6, 6)
        grid.add_agent((0, 0), (3, 3))

        waypoints = [(2, 0), (1, 5), (5, 2), (1, 2)]
        for x, y in waypoints:
            grid.add_waypoint(0, x, y)

        map = WaypointMap(grid, (3, 3))
        for x, y in waypoints:
            map.add_waypoint(x, y)

        return map

    def test_mst_tsp(self):
        map = WaypointMapTest.example_map()
        self.assertEqual(11, map.heuristic_mst((0, 0), {(1, 5)}))

    def test_mst_tsp_all(self):
        map = WaypointMapTest.example_map()
        self.assertEqual(14, map.heuristic_mst((0, 0), set()))


if __name__ == '__main__':
    unittest.main()
