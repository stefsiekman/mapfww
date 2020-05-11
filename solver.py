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

    visited_standard_nodes = set()

    max_cost = 0

    while not open_nodes.empty():
        f, h, id, node = open_nodes.get()

        logger.debug(
            f"\n==> At node #{id} (f = {f}, h = {node.heuristic}, g = {node.cost})")

        if node.is_standard():
            pos_tuple = node.standard_hash()
            if pos_tuple in visited_standard_nodes:
                logger.debug("    skip")
                continue
            else:
                visited_standard_nodes.add(pos_tuple)

        for agent in range(node.grid.agents):
            logger.debug(f"Agent {agent} is at {node.positions[agent]}")
            logger.debug(f"        visited {node.visited_waypoints[agent]} ")

        if node.cost > max_cost:
            max_cost = node.f
            logger.info(f"\rMax cost: {f}, queue length: {node_id}",
                        end="")

        # Stop if the cost has been exceeded in case of illegal moves
        if grid.illegal_moves is not None:
            if node.f > len(grid.illegal_moves) - 1:
                logger.info("Return due to rising costs!")
                return

        if node.all_done():
            logger.debug()
            return create_solution(grid, node)

        for new_node in node.expand():
            item = (new_node.f, new_node.heuristic, node_id, new_node)

            logger.debug(f"    + #{node_id} h = {new_node.heuristic}, "
                         f"g = {new_node.cost} at {new_node.positions} with {new_node.visited_waypoints}")

            node_id += 1
            open_nodes.put(item)

        # if node_id > 1000:
        #     exit()

    logger.info("They never made it...")


def solve_od_id(grid, groups=None) -> PathSet:
    if groups is None:
        groups = [[n] for n in range(grid.agents)]

    groups_string = ", ".join([str(g) for g in groups])
    logger.debug(f"\nSolving with groups: {groups_string}")

    group_solutions = []
    for group in groups:
        logger.info(f"Running for group {group}")
        s = solve_od(grid.copy(group))
        assert s is not None
        group_solutions.append((s, group))

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
        logger.info(f"\nConflict between: {conflicts}")
        assert len(conflicts) == 2, "Only two agent groups conflict at a time"

        agent_a, agent_b = conflicts
        solution_a, group_a, solution_i_a = next(
            (s, g, i) for i, (s, g) in enumerate(group_solutions) if agent_a in g)

        agent_b = next(a for a in conflicts if a != agent_a)
        solution_b, group_b, solution_i_b = next(
            (s, g, i) for i, (s, g) in enumerate(group_solutions) if agent_b in g)

        logger.info(f"Between groups: {group_a} and {group_b}")
        logger.info(f"Can A change its path limited to {len(solution_a)}")
        logger.info(list(solution_a))

        new_solution = solve_od(grid.copy(group_a, solution_b))
        if new_solution is None:
            logger.info("No solution was found")
        else:
            logger.info(" Yes!")
            logger.info(f"Has length: {len(new_solution)}")
            logger.info(list(new_solution))
            # Recreate the solution
            group_solutions[solution_i_a] = (new_solution, group_a)
            return PathSet.merge(group_solutions)

        logger.info(f"Can B change its path limited to {len(solution_b)}")

        new_solution = solve_od(grid.copy(group_b, solution_a))
        if new_solution is None:
            logger.info("No solution was found")
        else:
            logger.info(" Yes!")
            logger.info(f"Has length: {len(new_solution)}")

        logger.info("Combining groups...")

        # Solve with combined groups
        conflict_group = []
        new_groups = []
        for group in groups:
            if any(c in group for c in conflicts):
                conflict_group.extend(group)
            else:
                new_groups.append(group)
        new_groups.append(conflict_group)
        logger.info(f"New groups: {new_groups}")
        return solve_od_id(grid, new_groups)

    return solution
