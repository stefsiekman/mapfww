from queue import Queue
from typing import List, Optional

from cat import CAT
from group import Group
from node import Node
from pathset import PathSet
from waypoint_map import WaypointMap


class Grid:

    def __init__(self, width, height, illegal_moves=None):
        self.w = width
        self.h = height
        self.walls = [[False for _ in range(width)] for _ in range(height)]

        self.agents = 0
        self.starts = []
        self.goals = []
        self.waypoints: List[WaypointMap] = []
        self.illegal_moves: PathSet = illegal_moves
        self.cat: Optional[CAT] = None
        self.group: Optional[Group] = None

    def add_wall(self, x, y):
        assert self.agents == 0, "Add agents after all walls are added"
        self.walls[y][x] = True

    def add_agent(self, start, goal):
        """
        Also calculates the heuristics for this agent.
        """
        self.agents += 1
        self.starts.append(start)
        self.goals.append(goal)
        self.waypoints.append(WaypointMap(self, goal))

    def add_waypoint(self, agent, x, y):
        # Ignore if on start/goal
        if (x, y) in [self.starts[agent], self.goals[agent]]:
            return

        self.waypoints[agent].add_waypoint(x, y)

    def root_node(self):
        return Node(self, self.starts[:], [None] * self.agents, 0, None, 0, [])

    def is_move_illegal(self, from_time, move_from, move_to):
        if self.illegal_moves is None:
            return False

        return not self.illegal_moves.move_possible(from_time, move_from,
                                                    move_to)

    def is_move_conflicting(self, from_time, move_from, move_to):
        if self.cat is None or self.group is None:
            return False

        return self.cat.conflicts(self.group, from_time, move_from, move_to)

    def valid_neighbours(self, position):
        """
        Neighbours of a cell that are non walls.

        >>> grid = Grid(5, 2)
        >>> grid.add_wall(1, 0)
        >>> grid.add_wall(2, 0)
        >>> grid.valid_neighbours((0,0))
        [(0, 0), (0, 1)]

        >>> grid = Grid(5, 2)
        >>> grid.add_wall(1, 0)
        >>> grid.add_wall(2, 0)
        >>> grid.valid_neighbours((3,1))
        [(2, 1), (3, 0), (3, 1), (4, 1)]
        """

        neighbours = []

        for x_offs in [-1, 0, 1]:
            for y_offs in [-1, 0, 1]:
                # Only non-diagonal
                if x_offs != 0 and y_offs != 0:
                    continue

                x = position[0] + x_offs
                y = position[1] + y_offs

                if x < 0 or x >= self.w:
                    continue
                if y < 0 or y >= self.h:
                    continue

                assert 0 <= x < self.w, "Valid X neighbour"
                assert 0 <= y < self.h, "Valid Y neighbour"

                if not self.walls[y][x]:
                    neighbours.append((x, y))

        return neighbours

    def backtrack_heuristics(self, from_pos):
        """
        Calculate the heuristics for each cell for a goal.
        """

        queue = Queue()
        visited = set()
        heuristics = [[None for _ in range(self.w)] for _ in range(self.h)]

        queue.put((from_pos, 0))

        while not queue.empty():
            position, heuristic = queue.get()
            x, y = position
            visited.add(position)

            # Is this the most efficient path?
            if heuristics[y][x] is not None and heuristic >= heuristics[y][x]:
                continue
            heuristics[y][x] = heuristic

            for neighbour in self.valid_neighbours(position):
                if neighbour not in visited:
                    queue.put((neighbour, heuristic + 1))

        return heuristics

    def heuristic(self, agent, position, visited_waypoints):
        return self.waypoints[agent].heuristic(position, visited_waypoints)

    def on_waypoint(self, agent, position):
        return self.waypoints[agent].is_waypoint(position)

    def copy(self, agents, cat: CAT, illegal_moves=None):
        """
        Create a copy of this grid with just the information for a set of
        agents.
        :param agents: List[int] agents of which to include the information
        :param illegal_moves: Optional[PathSet]
        """

        new_grid = Grid(self.w, self.h, illegal_moves)
        new_grid.walls = self.walls

        for agent_index in agents:
            new_grid.starts.append(self.starts[agent_index])
            new_grid.goals.append(self.goals[agent_index])
            new_grid.waypoints.append(self.waypoints[agent_index])
            new_grid.agents += 1

        new_grid.cat = cat

        return new_grid

    def pretty_print(self):
        for y, row in enumerate(self.walls):
            for x, tile in enumerate(row):
                char = "."
                if tile:
                    char = "#"
                if (x, y) in self.goals:
                    char = "X"
                if (x, y) in self.starts:
                    char = "O"
                if any((x, y) in [tuple(w) for w in
                                  self.waypoints[agent].waypoints]
                       for agent in range(self.agents)):
                    char = "@"
                print(char, end="")
            print()
