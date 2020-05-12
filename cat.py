from typing import Dict, List

from group import Group


class CAT:

    def __init__(self, agents: int, groups: List[Group]):
        self.agents = agents
        self.groups = groups
        self.agent_map: Dict[int, Group] = dict()

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

        # TODO: Implement method

        pass

    def conflicts(self, group: Group, from_time, move_from, move_to) -> bool:
        # TODO: Implement method
        return False
