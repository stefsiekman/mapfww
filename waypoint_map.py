import time
from queue import Queue
from math import factorial
from typing import Tuple, Set, Optional, Dict

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

    def heuristic(self, position, visited_waypoints: Set[Tuple[int, int]],
                  options):
        """
        Calculate the heuristic for an agent, given a current position and
        a set of waypoints that have already been visited.
        """

        key = position, frozenset(visited_waypoints)
        if key in self.cache:
            return self.cache[key]

        x, y = position

        if len(visited_waypoints) != len(self.waypoints):
            to_visit = self.waypoints - visited_waypoints
            path_lengths = self.dynamic_tsp(to_visit)
            smallest_distance = min(path_lengths[wp] +
                                    self.distance_maps[wp][y][x]
                                    for wp in
                                    self.waypoints - visited_waypoints)

        else:
            smallest_distance = self.goal_heuristics[y][x]

        self.cache[key] = smallest_distance
        return smallest_distance

    def dynamic_tsp(self, waypoints) -> Dict[Tuple[int, int], int]:
        """
        Calculates the minimal path from each way points to the goal, via all
        the other waypoints.
        """

        cache_key = tuple(sorted(waypoints))
        if cache_key in self.shared_cache:
            return self.shared_cache[cache_key]

        ordered_waypoints = list(waypoints)
        n = len(ordered_waypoints)
        all_indices = set(range(n))

        memory = {}
        queue = Queue()

        for index, wp in enumerate(ordered_waypoints):
            key = (index,), index
            wpx, wpy = wp
            queue.put(key)
            memory[key] = self.goal_heuristics[wpy][wpx], None

        while not queue.empty():
            prev_visited, prev_last_wp = queue.get()
            prev_dist, _ = memory[(prev_visited, prev_last_wp)]
            to_visit = all_indices.difference(set(prev_visited))

            for new_last_point in to_visit:
                new_visited = tuple(sorted(prev_visited + (new_last_point,)))
                xa, ya = ordered_waypoints[prev_last_wp]
                wpb = ordered_waypoints[new_last_point]
                new_dist = prev_dist + self.distance_maps[wpb][ya][xa]

                new_key = new_visited, new_last_point
                new_value = new_dist, prev_last_wp

                if new_key not in memory:
                    memory[new_key] = new_value
                    queue.put(new_key)
                else:
                    if new_dist < memory[new_key][0]:
                        memory[new_key] = new_value

        result = {}
        full_path = tuple(range(n))
        for index, wp in enumerate(ordered_waypoints):
            result[wp] = memory[(full_path, index)][0]

        self.shared_cache[cache_key] = result
        return result

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
