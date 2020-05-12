from __future__ import annotations
from typing import List, Optional, Tuple

import logger
from pathset import PathSet


class Group:

    def __init__(self, agents: List[int], base_grid):
        self.agents = agents
        self.solution: Optional[PathSet] = None
        self.base_grid = base_grid

    def solve_with(self, solver, illegal_moves=None, cat=None):
        """
        If illegal moves are provided, the result is returned instead of saved.
        """

        logger.info(f"Running for group {self.agents}")

        grid = self.base_grid.copy(self.agents, illegal_moves)
        grid.group = self
        grid.cat = cat
        solution = solver(grid)

        if illegal_moves is not None:
            return solution
        else:
            self.solution = solution

    def find_non_conflicting_alt(self, solver, other_group: Group,
                                 cat) -> bool:
        """
        Sees if an alternative solution can be found considering the solution
        of another group. The solution is stored if it is found.
        :return: True iff the other solution could be found
        """

        assert other_group.solution is not None, "Other groups is solved"

        # Is there an equal other solution?
        grid = self.base_grid.copy(self.agents, other_group.solution)
        grid.group = self
        grid.cat = cat
        alternative_solution = solver(grid)
        if alternative_solution is None:
            return False

        self.solution = alternative_solution

        return True

    def __add__(self, other: Group) -> Group:
        """
        Create a new group instance with the agents of this group and another.
        """

        return Group(sorted(self.agents + other.agents), self.base_grid)

    def __contains__(self, item: int):
        return item in self.agents

    def hash(self):
        return tuple(sorted(self.agents))

    @staticmethod
    def conflicting(groups: List[Group]) -> Optional[Tuple[Group, Group]]:
        """
        Finds the conflicting groups in a set of groups. All the groups need
        to be solved already.
        :return: First two groups to conflict, or None if there were no
                 conflicts.
        """

        assert all(g.solution is not None for g in groups), "Groups are solved"

        # See if there are conflicts
        conflicts = Group.combined_solution(groups).conflicts()
        if conflicts is None:
            return None

        # Find appropriate groups
        conflicting_a, conflicting_b = conflicts
        conflicting_groups = tuple(g for g in groups if
                                   conflicting_a in g.agents or
                                   conflicting_b in g.agents)

        assert len(conflicting_groups), "No duplicate agents in groups"

        return conflicting_groups[0:2]

    @staticmethod
    def combined_solution(groups: List[Group]) -> PathSet:
        """
        Combine the solutions of all the groups into a single solution.
        """

        assert all(g.solution is not None for g in groups), "Groups are solved"

        return PathSet.merge([(g.solution, g.agents) for g in groups])
