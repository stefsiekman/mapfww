from __future__ import annotations
from typing import List, Tuple, Set, Optional

from edge import Edge
from path import Path


class PathSet:

    def __init__(self, agents: int):
        self.agents = agents
        self.paths = [Path() for _ in range(agents)]

    def prepend_positions(self, positions: List[Tuple[int, int]]):
        """
        Prepend a position for each agent.
        """

        for agent, position in enumerate(positions):
            self.paths[agent].prepend_position(position)

    def move_possible(self, time: int, from_pos: Tuple[int, int],
                      to_pos: Tuple[int, int]) -> bool:
        """
        Check whether a movement from a position to another position is
        possible at a given time without conflicting with any of the paths in
        this set.
        :param time: Time since start when at start position. So t=2 would be
        the third element in the path list.
        """

        if time + 1 >= len(self):
            return True

        # Move into a position already taken
        if any(path[time + 1] == to_pos for path in self.paths):
            return False

        # Edge collisions
        if any(Edge(from_pos, to_pos).conflicts(
                Edge(path[time], path[time + 1]))
               for path in self.paths):
            return False

        return True

    def conflicts(self) -> Optional[Set[int]]:
        """
        Checks for any conflicts in the paths. When the first conflict is found
        the indices of the responsible agents are returned, else None.
        """

        step_positions = list(self)

        # Any shared positions?
        for step, positions in enumerate(step_positions):
            for agent, position in enumerate(positions):
                for other_agent, other_position in enumerate(positions):
                    if other_agent == agent:
                        continue
                    if position == other_position:
                        return {agent, other_agent}

        # Crossing edges require more that one step
        if len(self) < 2:
            return

        # Crossing edges?
        for step_before, positions in enumerate(step_positions[1:]):
            positions_before = step_positions[step_before]
            edges = [Edge(p, p_b) for p, p_b in
                     zip(positions, positions_before)]

            for agent, edge in enumerate(edges):
                for other_agent, other_edge in enumerate(edges):
                    if other_agent == agent:
                        continue
                    if edge.conflicts(other_edge):
                        return {agent, other_agent}

    def __len__(self):
        return max(len(path) for path in self.paths)

    def __iter__(self):
        """
        Convert the path set to a list of agent's list of positions at each
        time step, submittable to the benchmarking server.
        """
        for t in range(len(self)):
            yield [path[t] for path in self.paths]

    def to_json(self):
        return [list(path) for path in self.paths]

    def pad(self):
        max_length = len(self)
        for path in self.paths:
            path.pad_to(max_length)

    @staticmethod
    def merge(solutions: List[Tuple[PathSet, List[int]]]) -> PathSet:
        """
        Combine multiple solutions for groups into a single solution. This
        means correctly ordering the paths for the agent indices, as well as
        padding the paths with extra waiting at the goals on the end if
        required.
        """

        total_agents = sum(len(group) for _, group in solutions)
        combined_solution = PathSet(total_agents)

        # Collect the paths
        for solution, group in solutions:
            for index_in_solution, agent in enumerate(group):
                combined_solution.paths[agent] = \
                    solution.paths[index_in_solution].copy()

        combined_solution.pad()

        return combined_solution
