import itertools
from queue import PriorityQueue

from edge import Edge
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

        # print(f"==> At node #{id} (h = {node.heuristic}, g = {node.cost})")
        # for agent in range(node.grid.agents):
        #     print(f"Agent {agent} is at {node.positions[agent]}")
        #     print(f"        visited {node.visited_waypoints[agent]} ")

        if node.cost > max_cost:
            max_cost = node.cost
            print(f"\rMax cost: {max_cost}, queue length: {node_id}", end="")

        if node.all_done():
            return create_solution(grid, node)

        for new_node in node.expand():
            item = (new_node.f, new_node.heuristic, node_id, new_node)

            # print(f"    + #{node_id} h = {new_node.heuristic}, "
            #       f"g = {new_node.cost}")

            node_id += 1
            open_nodes.put(item)

        # if node_id > 100:
        #     exit()


def solve_od_id(grid, groups=None) -> PathSet:
    if groups is None:
        groups = [[n] for n in range(grid.agents)]

    groups_string = ", ".join([str(g) for g in groups])
    print(f"\nSolving with groups: {groups_string}")

    solution = PathSet.merge([(solve_od(grid.copy(group)), group)
                              for group in groups])

    # Solve again if there are conflicts
    conflicts = solution.conflicts()
    if conflicts is not None:
        if len(groups) == 1:
            print("\nNo valid solution could be found")
            print("Last solution:")
            for s in solution:
                print(f"    {s}")
            return solution

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
