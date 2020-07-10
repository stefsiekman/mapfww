import unittest
from random import randint

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

    def test_ordered_1(self):
        map = WaypointMapTest.example_map()
        self.assertEqual(10, map.heuristic((3,1), {(2,0),(1,5)}, {
            "ord": True
        }))

    def test_ordered_2(self):
        map = WaypointMapTest.example_map()
        self.assertEqual(6, map.heuristic((3,1), {(2,0),(1,5),(5,2)}, {
            "ord": True
        }))

    def test_ordered_3(self):
        map = WaypointMapTest.example_map()
        self.assertEqual(2, map.heuristic((3,1), {(2,0),(1,5),(5,2),(1,2)}, {
            "ord": True
        }))

    def test_ordered_4(self):
        map = WaypointMapTest.example_map()
        self.assertEqual(20, map.heuristic((3,1), {(2,0)}, {
            "ord": True
        }))

    def test_ordered_5(self):
        map = WaypointMapTest.example_map()
        self.assertEqual(22, map.heuristic((3,1), set(), {
            "ord": True
        }))

    def test_mst_tsp(self):
        map = WaypointMapTest.example_map()
        self.assertEqual(11, map.heuristic_mst((0, 0), {(1, 5)}))

    def test_mst_tsp_all(self):
        map = WaypointMapTest.example_map()
        self.assertEqual(14, map.heuristic_mst((0, 0), set()))

    def test_smaller(self):
        map = WaypointMapTest.example_map()
        self.assertLessEqual(map.heuristic_mst((0, 0), set()),
                             map.heuristic_tsp((0, 0), set()))

    def test_smaller_random(self):
        for n in range(1000):
            size = randint(5, 16)
            grid = Grid(size, size)
            start = (randint(0, size - 1), randint(0, size - 1))
            pos = (randint(0, size - 1), randint(0, size - 1))
            goal = (randint(0, size - 1), randint(0, size - 1))
            grid.add_agent(start, goal)

            waypoints = [(randint(0, size - 1), randint(0, size - 1))
                         for _ in range(randint(0, 10))]
            waypoints = [w for w in waypoints
                         if w != start and w != goal and w != pos]
            for x, y in waypoints:
                grid.add_waypoint(0, x, y)

            map = WaypointMap(grid, goal)
            for x, y in waypoints:
                map.add_waypoint(x, y)

            mst = map.heuristic_mst(pos, set())
            tsp = map.heuristic_tsp(pos, set())

            if mst > tsp:
                print(f"Failed test #{n}")
                print(f"  Size      = {size}")
                print(f"  Start     = {start}")
                print(f"  Position  = {pos}")
                print(f"  Goal      = {goal}")
                print(f"  Waypoints = {waypoints}")
                print(f"  TSP       = {tsp}")
                print(f"  MST       = {mst}")

            self.assertLessEqual(mst, tsp)

    def test_mst_map1(self):
        grid = Grid(6, 6)
        grid.add_agent((5, 1), (4, 0))

        waypoints = [(0, 3), (3, 1), (0, 5)]
        for x, y in waypoints:
            grid.add_waypoint(0, x, y)

        map = WaypointMap(grid, (4, 0))
        for x, y in waypoints:
            map.add_waypoint(x, y)

        map = WaypointMapTest.example_map()
        self.assertEqual(13, map.heuristic_mst((5, 1), set()))


if __name__ == '__main__':
    unittest.main()
