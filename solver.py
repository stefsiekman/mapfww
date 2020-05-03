import itertools
from queue import PriorityQueue

from edge import Edge
from grid import Grid


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
    open_nodes.put((0, 0, node_id, grid.root_node()))
    node_id += 1

    max_cost = 0

    while not open_nodes.empty():
        f, h, id, node = open_nodes.get()

        # print(f"==> At node #{id} (h = {node.heuristic}, g = {node.cost})")
        # for agent in range(node.grid.agents):
        #     print(f"Agent {agent} is at {node.positions[agent]}")
        #     print(f"        visited {node.visited_waypoints[agent]} ")

        # if node.cost > max_cost:
        #     max_cost = node.cost
        #     print(f"\rMax cost: {max_cost}, queue length: {node_id}", end="")

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


def paths_conflict(paths):
    """
    Finds any conflicts in a solution, reports the agents that conflict.

    >>> paths_conflict([[[0, 0], [0, 1]], [[0, 2], [0, 3]], [[1, 1], [1, 2]]])

    >>> paths_conflict([[[0, 0], [0, 1]], [[0, 2], [0, 1]], [[1, 1], [1, 2]]])
    [0, 1]

    >>> paths_conflict([[[0, 0], [0, 1]], [[1, 2], [1, 1]], [[0, 1], [0, 0]]])
    [0, 2]
    """
    step_positions = [
        [tuple(paths[agent][step]) for agent in range(len(paths))]
        for step in range(len(paths[0]))]

    # Any shared positions?
    for step, positions in enumerate(step_positions):
        for agent, position in enumerate(positions):
            shared_position = []
            for other_agent, other_position in enumerate(positions):
                if other_agent == agent:
                    continue
                if position == other_position:
                    shared_position.append(other_agent)

            if len(shared_position) > 0:
                return [agent] + shared_position

    # Crossing edges require more that one step
    if len(paths[0]) < 2:
        return None

    # Crossing edges?
    for step_before, positions in enumerate(step_positions[1:]):
        positions_before = step_positions[step_before]
        edges = [Edge(p, p_b) for p, p_b in zip(positions, positions_before)]

        for agent, edge in enumerate(edges):
            shared_position = []
            for other_agent, other_edge in enumerate(edges):
                if other_agent == agent:
                    continue
                if edge.conflicts(other_edge):
                    shared_position.append(other_agent)
            if len(shared_position) > 0:
                return [agent] + shared_position


def solve_od_id(grid, groups=None):
    if groups is None:
        groups = [[n] for n in range(grid.agents)]

    groups_string = ", ".join([str(g) for g in groups])
    print(f"\nSolving with groups: {groups_string}")

    # Create a separate grid for each agent group
    grids = []
    for group in groups:
        new_grid = Grid(grid.w, grid.h)
        new_grid.walls = grid.walls

        for agent_index in group:
            new_grid.starts.append(grid.starts[agent_index])
            new_grid.goals.append(grid.goals[agent_index])
            new_grid.waypoints.append(grid.waypoints[agent_index])
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
    if conflicts is not None and len(groups) > 2:
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
