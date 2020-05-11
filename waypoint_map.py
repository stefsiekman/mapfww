from itertools import permutations
from typing import Tuple, Set, Optional


class WaypointMap:

    def __init__(self, grid, goal: Tuple[int, int]):
        self.grid = grid
        self.waypoints = set()
        self.distance_maps = dict()
        self.goal_heuristics = grid.backtrack_heuristics(goal)

    def add_waypoint(self, x, y):
        self.waypoints.add((x, y))
        self.distance_maps[(x, y)] = self.grid.backtrack_heuristics((x, y))

    def heuristic(self, position, visited_waypoints: Set[Tuple[int, int]]):
        """
        Calculate the heuristic for an agent, given a current position and
        a set of waypoints that have already been visited.
        """

        smallest_distance = None
        for order in permutations(self.waypoints - visited_waypoints):
            last_waypoint = position
            order_distance = 0

            for waypoint in order:
                lx, ly = last_waypoint
                assert waypoint in self.distance_maps, \
                    f"{waypoint} should be in distance maps"
                order_distance += self.distance_maps[waypoint][ly][lx]
                last_waypoint = waypoint

            lx, ly = last_waypoint
            order_distance += self.goal_heuristics[ly][lx]

            if smallest_distance is None or order_distance < smallest_distance:
                smallest_distance = order_distance

        return smallest_distance

    def furthest_waypoint(self, position, excluding: Set[Tuple[int, int]]):
        if self.are_all(excluding):
            return None

        x, y = position
        return max(self.waypoints - excluding,
                   key=lambda wp: self.distance_maps[wp][y][x])

    def is_waypoint(self, position):
        return position in self.waypoints

    def are_all(self, waypoints: Set[Tuple[int, int]]):
        """
        Test whether the set of waypoints are all the waypoints there are in
        this map.

        >>> from grid import Grid
        >>> grid = Grid(5, 5)
        >>> grid.add_agent((0, 0), (4, 4))
        >>> grid.add_waypoint(0, 4, 0)
        >>> grid.add_waypoint(0, 0, 4)
        >>> m = WaypointMap(grid, (4, 4))
        >>> m.add_waypoint(4, 0)
        >>> m.add_waypoint(0, 4)
        >>> m.are_all(set())
        False

        >>> m.are_all({(0, 4)})
        False

        >>> m.are_all({(4, 0)})
        False

        >>> m.are_all({(0, 4), (4, 0)})
        True
        """

        return all(wp in waypoints for wp in self.waypoints)
