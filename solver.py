import itertools
from queue import PriorityQueue
from typing import Tuple

import logger
from cat import CAT
from grid import Grid
from group import Group
from node import Node
from pathset import PathSet


def create_solution(grid: Grid, node: Node) -> PathSet:
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
    open_nodes.put((0, 0, 0, node_id, grid.root_node()))
    node_id += 1

    visited_standard_nodes = set()

    max_cost = 0

    while not open_nodes.empty():
        f, _, _, id, node = open_nodes.get()
        conflicts = node.conflicts
        h = node.heuristic

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

        if node_id % 1000 == 0:
            completed_perc = round(
                (node_id - open_nodes.qsize()) / open_nodes.qsize() * 100)
            logger.info(f"\rMax cost: {f}, queue length: {open_nodes.qsize()} "
                        f"{completed_perc}%",
                        end="")

        # Stop if the cost has been exceeded in case of illegal moves
        if grid.illegal_moves is not None:
            if node.f > len(grid.illegal_moves) - 1:
                logger.info("Return due to rising costs!")
                return

        if node.all_done():
            logger.info("")
            return create_solution(grid, node)

        for new_node in node.expand():
            pc = grid.options["pc"]
            p1 = new_node.conflicts if pc else new_node.heuristic
            p2 = new_node.heuristic if pc else new_node.conflicts
            item = (new_node.f, p1, p2, node_id, new_node)

            logger.debug(f"    + #{node_id} h = {new_node.heuristic}, "
                         f"g = {new_node.cost} at {new_node.positions} with {new_node.visited_waypoints}")

            node_id += 1
            open_nodes.put(item)

    logger.info("They never made it...")


def solve_od_group(grid, group):
    return solve_od(grid.copy(group))


def solve_od_id(grid) -> PathSet:
    solved_group_conflicts = set()

    # Assign each agent to a group
    groups = [Group([n], grid) for n in range(grid.agents)]

    # Plan a path for each group
    logger.info("Planning path for each agent...")
    for group in groups:
        group.solve_with(solve_od)
    logger.info(" ... done")

    # fill conflict avoidance table with every path
    cat = CAT(grid.agents, groups)

    # until no conflicts occur
    while True:
        # Simulate execution of all paths until a conflict between two groups
        # G1 and G2 occurs
        logger.info("Simulating for conflicts ... ", "")
        conflicts = Group.conflicting(groups)
        if conflicts is None:
            logger.info("none")
            break
        group_a, group_b = conflicts
        group_combo_hash = (group_a.hash(), group_b.hash())
        resolved_conflict = False
        logger.info(f"between {group_combo_hash}")

        # if these two groups have not conflicted before
        if group_combo_hash not in solved_group_conflicts:
            solved_group_conflicts.add(group_combo_hash)

            # fill illegal move table with the current paths for G2
            # find another set of paths with the same cost for G1
            logger.info(f"Trying to find an alt for {group_a.agents}")
            resolved_conflict |= group_a.find_non_conflicting_alt(solve_od,
                                                                  group_b, cat)

            # if failed to find such a set then
            if not resolved_conflict:
                # fill illegal move table with the current paths for G1

                # find another set of paths with the same cost for G2
                logger.info(f"Trying to find an alt for {group_b.agents}")
                resolved_conflict |= group_b.find_non_conflicting_alt(solve_od,
                                                                      group_a,
                                                                      cat)

        # if failed to find an alternate set of paths for G1 and G2 then
        if not resolved_conflict:
            logger.info(f"Merging group {group_a.agents} and {group_b.agents}")
            # merge G1 and G2 into a single group
            new_group = group_a + group_b
            groups.remove(group_a)
            groups.remove(group_b)
            groups.append(new_group)

            # cooperatively plan new group
            new_group.solve_with(solve_od, cat=cat)
        else:
            logger.info("Conflict was resolved")

        # update conflict avoidance table with changes made to paths
        cat.update(groups)

    # solution ← paths of all groups combined
    solution = Group.combined_solution(groups)

    # return solution
    return solution
