from typing import Set, Tuple, List, Optional

from edge import Edge


class Node:

    def __init__(self, grid, positions, moves, cost, goal_waits, conflicts,
                 taken_edges, parent=None, visited_waypoints=None,
                 new_heuristic=None):
        self.grid = grid
        self.positions = positions
        self.moves = moves
        self.cost = cost
        self.goal_waits: List[int] = goal_waits or [0] * grid.agents
        self.conflicts = conflicts
        self.taken_edges = taken_edges
        self.parent = parent

        # Copy or create waypoints list
        self.visited_waypoints: List[Set[Tuple[int, int]]] = visited_waypoints
        if self.visited_waypoints is None:
            self.visited_waypoints = [set() for _ in range(grid.agents)]

        # Make node standard
        if None not in moves:
            self.moves = [None] * len(self.positions)
            self.positions = moves
            self.taken_edges = []

        self.post_moves = [move if move is not None else pos
                           for pos, move in zip(self.positions, self.moves)]

        if new_heuristic is None:
            self.heuristic = sum(grid.heuristic(agent, self.post_moves[agent],
                                                self.visited_waypoints[agent])
                                 for agent in range(len(positions)))
        else:
            self.heuristic = new_heuristic

        self.f = self.cost + self.heuristic

    def standard_hash(self):
        """
        Hash (tuple) to uniquely identify this node, given it's treated as
        standard. So takes the positions and visited waypoints into account.
        """

        return tuple(self.positions), tuple(
            tuple(sorted(x + y * self.grid.w for x, y in waypoints)) for
            waypoints in self.visited_waypoints)

    def augmented(self):
        pass

    def expand(self):
        agent = self.moves.index(None)
        position = self.positions[agent]

        new_nodes = []

        for neighbour in self.grid.valid_neighbours(position):
            # Check if cell is occupied by moved agent
            if neighbour in self.moves:
                continue

            # Check for crossing edges
            move_edge = Edge(position, neighbour)
            if any(move_edge.conflicts(edge) for edge in self.taken_edges):
                continue

            # Check for illegal moves, if given
            if self.grid.is_move_illegal(self.cost, position, neighbour):
                continue

            # Check for new conflicts with other groups
            new_conflicts = self.conflicts
            if self.grid.is_move_conflicting(self.cost, position, neighbour):
                new_conflicts += 1

            new_moves = self.moves[:]
            new_moves[agent] = neighbour
            new_taken_edges = self.taken_edges[:]
            new_taken_edges.append(move_edge)

            # Check if this means a new waypoint is now visited for this agent
            new_visited_waypoints = self.visited_waypoints
            if self.grid.on_waypoint(agent, neighbour):
                new_visited_waypoints = [ws.copy() for ws in
                                         new_visited_waypoints]
                new_visited_waypoints[agent].add(neighbour)

            # Agents can wait at goal for no cost, unless they will move again
            # in the future, so we need to keep track of this 'credit'
            additional_cost = 1
            new_goal_waits = self.goal_waits
            if self.agent_done(agent):
                additional_cost = 0
                new_goal_waits = self.goal_waits[:]
                new_goal_waits[agent] += 1
            elif self.goal_waits[agent]:
                additional_cost = self.goal_waits[agent] + 1
                new_goal_waits = self.goal_waits[:]
                new_goal_waits[agent] = 0

            # Calculate the new heuristic by looking at the difference for
            # only this agent
            h_before = self.grid.heuristic(agent, position,
                                           self.visited_waypoints[agent])
            h_after = self.grid.heuristic(agent, neighbour,
                                          new_visited_waypoints[agent])
            h_difference = h_after - h_before
            new_heuristic = self.heuristic + h_difference

            new_node = Node(self.grid, self.positions, new_moves,
                            self.cost + additional_cost, new_goal_waits,
                            new_conflicts, new_taken_edges, self,
                            new_visited_waypoints, new_heuristic)
            new_nodes.append(new_node)

        return new_nodes

    def is_standard(self):
        return all(move is None for move in self.moves)

    def all_done(self):
        return all(self.agent_done(agent) for agent in range(self.grid.agents))

    def agent_done(self, agent):
        return self.positions[agent] == self.grid.goals[agent] and \
               self.grid.waypoints[agent].are_all(
                   self.visited_waypoints[agent])

    def pretty_print(self):
        vertical_border = "+" + ("-" * (self.grid.w)) + "+"
        print(vertical_border)
        for y in range(self.grid.h):
            print("|", end="")
            for x in range(self.grid.w):
                if self.grid.walls[y][x]:
                    print("#", end="")
                elif (x, y) in self.positions:
                    print(self.positions.index((x, y)) + 1, end="")
                else:
                    print(".", end="")
            print("|")
        print(vertical_border)
