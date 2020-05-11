import itertools
from queue import PriorityQueue

import logger
from grid import Grid
from pathset import PathSet


def create_solution(grid: Grid, node) -> PathSet:
    solution = PathSet(grid.agents)

    # Add the positions of all the standard nodes
    while node is not None:
        if node.is_standard():
            solution.prepend_positions(node.positions)
        node = node.parent

    return solution


def solve_od(grid) -> PathSet:
    """
    Solves the MAPFW problem for a given grid.
    :return: PathSet solution
    """

    open_nodes = PriorityQueue()
    node_id = 0
    open_nodes.put((0, 0, node_id, grid.root_node()))
    node_id += 1

    max_cost = 0

    while not open_nodes.empty():
        f, h, id, node = open_nodes.get()

        logger.debug(f"\n==> At node #{id} (h = {node.heuristic}, g = {node.cost})")
        for agent in range(node.grid.agents):
            logger.debug(f"Agent {agent} is at {node.positions[agent]}")
            logger.debug(f"        visited {node.visited_waypoints[agent]} ")

        if node.cost > max_cost:
            max_cost = node.cost
            logger.info(f"\rMax cost: {max_cost}, queue length: {node_id}", end="")

        if node.all_done():
            logger.debug()
            return create_solution(grid, node)

        for new_node in node.expand():
            item = (new_node.f, new_node.heuristic, node_id, new_node)

            logger.debug(f"    + #{node_id} h = {new_node.heuristic}, "
                  f"g = {new_node.cost} at {new_node.positions} with {new_node.visited_waypoints}")

            node_id += 1
            open_nodes.put(item)

        # if node.cost == 10:
        #     exit()


def solve_od_id(grid, groups=None) -> PathSet:
    if groups is None:
        groups = [[n] for n in range(grid.agents)]

    groups_string = ", ".join([str(g) for g in groups])
    logger.debug(f"\nSolving with groups: {groups_string}")

    group_solutions = []
    for group in groups:
        logger.debug("Running for group", group)
        group_solutions.append((solve_od(grid.copy(group)), group))

    solution = PathSet.merge(group_solutions)

    # Solve again if there are conflicts
    conflicts = solution.conflicts()
    if conflicts is not None:
        # Only one group and conflicts? No solution
        if len(groups) == 1:
            logger.debug("\nNo valid solution could be found")
            logger.debug("Last solution:")
            for s in solution:
                logger.debug(f"    {s}")
            return solution

        # Try to find another path for conflicting agents
        logger.debug("\nConflict between:", conflicts)

        assert len(conflicts) == 2, "Only two agent groups conflict at a time"

        for conflicting_agent in conflicts:
            group_index = [i for i, g in enumerate(groups)
                           if conflicting_agent in g][0]
            other_agent = list(conflicts - {conflicting_agent})[0]
            other_group_index = [i for i, g in enumerate(groups)
                                 if other_agent in g][0]

            other_grids = [grid.copy()]

            # new_solutions =

        exit()

        # Solve with combined groups
        conflict_group = []
        new_groups = []
        for group in groups:
            if any(c in group for c in conflicts):
                conflict_group.extend(group)
            else:
                new_groups.append(group)
        new_groups.append(conflict_group)
        return solve_od_id(grid, new_groups)

    return solution
