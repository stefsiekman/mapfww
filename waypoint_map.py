import time
from itertools import permutations
from math import factorial
from typing import Tuple, Set, Optional

import logger


class WaypointMap:

    def __init__(self, grid, goal: Tuple[int, int]):
        self.grid = grid
        self.waypoints = set()
        self.distance_maps = dict()
        self.goal_heuristics = grid.backtrack_heuristics(goal)
        self.cache = dict()
        self.shared_cache = dict()

    def add_waypoint(self, x, y):
        self.waypoints.add((x, y))
        self.distance_maps[(x, y)] = self.grid.backtrack_heuristics((x, y))

    def heuristic(self, position, visited_waypoints: Set[Tuple[int, int]]):
        """
        Calculate the heuristic for an agent, given a current position and
        a set of waypoints that have already been visited.
        """

        key = position, frozenset(visited_waypoints)
        if key in self.cache:
            return self.cache[key]

        x, y = position

        if len(visited_waypoints) != len(self.waypoints):
            smallest_distance = min(self.distance_from(wp, visited_waypoints) +
                                    self.distance_maps[wp][y][x]
                                    for wp in
                                    self.waypoints - visited_waypoints)
        else:
            smallest_distance = self.goal_heuristics[y][x]

        self.cache[key] = smallest_distance
        return smallest_distance

    def distance_from(self, start, excluding):
        """
        Calculates the distance from a start waypoints, via all other waypoints
        (except those in 'excluding'), to the goal position.

        This function is memoized, so it call be called frequently.
        """

        key = start, frozenset(excluding)
        if key in self.shared_cache:
            return self.shared_cache[key]

        to_visit = self.waypoints - excluding - {start}
        orderings = factorial(len(to_visit))
        logger.info(f"Solving {orderings} orderings of TSP ...")

        smallest_distance = None
        for order in permutations(to_visit):
            last_waypoint = start
            order_distance = 0

            for waypoint in order:
                lx, ly = last_waypoint
                order_distance += self.distance_maps[waypoint][ly][lx]
                last_waypoint = waypoint

            lx, ly = last_waypoint
            order_distance += self.goal_heuristics[ly][lx]

            if smallest_distance is None or order_distance < smallest_distance:
                smallest_distance = order_distance

        self.shared_cache[key] = smallest_distance
        return smallest_distance

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
