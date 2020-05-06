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

    def conflicts(self) -> Optional[Set[int]]:
        """
        Checks for any conflicts in the paths. When the first conflict is found
        the indices of the responsible agents are returned, else None.
        """

        step_positions = list(self)

        # Any shared positions?
        for step, positions in enumerate(step_positions):
            for agent, position in enumerate(positions):
                shared_position_with = set()
                for other_agent, other_position in enumerate(positions):
                    if other_agent == agent:
                        continue
                    if position == other_position:
                        shared_position_with.add(other_agent)

                if len(shared_position_with) > 0:
                    return {agent} | shared_position_with

        # Crossing edges require more that one step
        if len(self) < 2:
            return

        # Crossing edges?
        for step_before, positions in enumerate(step_positions[1:]):
            positions_before = step_positions[step_before]
            edges = [Edge(p, p_b) for p, p_b in
                     zip(positions, positions_before)]

            for agent, edge in enumerate(edges):
                shared_edge_with = set()
                for other_agent, other_edge in enumerate(edges):
                    if other_agent == agent:
                        continue
                    if edge.conflicts(other_edge):
                        shared_edge_with.add(other_agent)
                if len(shared_edge_with) > 0:
                    return {agent} | shared_edge_with

    def __len__(self):
        return max(len(path) for path in self.paths)

    def __iter__(self):
        """
        Convert the path set to a list of agent's list of positions at each
        time step, submittable to the benchmarking server.
        """
        for t in range(len(self)):
            yield [path[t] for path in self.paths]

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
                    solution.paths[index_in_solution]

        # Pad the paths
        max_length = len(combined_solution)
        for path in combined_solution.paths:
            path.pad_to(max_length)

        return combined_solution
