import itertools
from queue import PriorityQueue

from grid import Grid
from node import Node


def create_solution(grid, node):
    positions = []
    while node is not None:
        if node.is_standard():
            positions.append([list(p) for p in node.positions])
        node = node.parent

    positions.reverse()

    return [[positions[t][i] for t in range(len(positions))]
            for i in range(grid.agents)]


def solve_od(grid):
    open_nodes = PriorityQueue()
    node_id = 0
    open_nodes.put((0, node_id, grid.root_node()))
    node_id += 1

    while not open_nodes.empty():
        f, id, node = open_nodes.get()

        if node.all_done():
            return create_solution(grid, node)

        for new_node in node.expand():
            item = (new_node.f, node_id, new_node)
            node_id += 1
            open_nodes.put(item)


be = False


def paths_conflict(paths):
    global be
    if not be:
        be = True
        return [1, 2]
    return None


def solve_od_id(grid, groups=None):
    if groups is None:
        groups = [[n] for n in range(grid.agents)]

    # Create a separate grid for each agent group
    grids = []
    for group in groups:
        new_grid = Grid(grid.w, grid.h)
        new_grid.walls = grid.walls

        for agent_index in group:
            new_grid.starts.append(grid.starts[agent_index])
            new_grid.goals.append(grid.goals[agent_index])
            new_grid.heuristics.append(grid.heuristics[agent_index])
            new_grid.agents += 1

        grids.append(new_grid)

    # Convert the groups paths to a solution
    solution = [None] * grid.agents
    for group, group_grid in zip(groups, grids):
        position_lists = solve_od(group_grid)
        for agent_index, position_list in zip(group, position_lists):
            solution[agent_index] = position_list

    # Pad with positions at goal
    steps = max(len(l) for l in solution)
    for positions in solution:
        last = positions[-1]
        for _ in range(steps - len(positions)):
            positions.append(last)

    # Solve again if there are conflicts
    conflicts = paths_conflict(solution)
    if conflicts is not None:
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
