from __future__ import annotations
from typing import List, Optional, Tuple

import logger
from grid import Grid
from pathset import PathSet


class Group:

    def __init__(self, agents: List[int], base_grid: Grid):
        self.agents = agents
        self.solution: Optional[PathSet] = None
        self.base_grid = base_grid
        self.grid = base_grid.copy(agents)

    def solve_with(self, solver, illegal_moves=None):
        """
        If illegal moves are provided, the result is returned instead of saved.
        """

        logger.info(f"Running for group {self.agents}")
        solution = solver(self.base_grid.copy(self.agents, illegal_moves))

        if illegal_moves is not None:
            return solution
        else:
            self.solution = solution

    def find_non_conflicting_alt(self, solver, other_group: Group) -> bool:
        """
        Sees if an alternative solution can be found considering the solution
        of another group. The solution is stored if it is found.
        :return: True iff the other solution could be found
        """

        return False

    def __add__(self, other: Group) -> Group:
        """
        Create a new group instance with the agents of this group and another.
        """

        return None

    def hash(self):
        return tuple(sorted(self.agents))

    @staticmethod
    def conflicting(all_groups: List[Group]) -> \
            Optional[Tuple[Group, Group]]:
        """
        Finds the conflicting groups in a set of groups. All the groups need
        to be solved already.
        :return: First two groups to conflict, or None if there were no
                 conflicts.
        """
        return

    @staticmethod
    def combined_solution(groups: List[Group]) -> PathSet:
        """
        Combine the solutions of all the groups into a single solution.
        """

        return None
