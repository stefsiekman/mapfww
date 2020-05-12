from typing import Dict, List

from group import Group


class CAT:

    def __init__(self, agents: int, groups: List[Group]):
        self.agents = agents
        self.groups = groups
        self.agent_map: Dict[int, Group] = dict()
        self.map_agents()

    def map_agents(self):
        """
        Create an easy access dictionary to find which agent is in which group.
        """
        self.agent_map = dict()
        for agent in range(self.agents):
            self.agent_map[agent] = next(g for g in self.groups if agent in g)

    def update(self, groups: List[Group]):
        """
        Update the CAT with new group solutions.
        """

        self.groups = groups
        self.map_agents()

    def conflicts(self, group: Group, from_time, move_from, move_to) -> bool:
        other_groups = (g for g in self.groups if g != group)
        for other_group in other_groups:
            assert other_group.solution is not None, "Groups are solved"

            if not other_group.solution.move_possible(from_time, move_from,
                                                      move_to):
                return True

        return False
