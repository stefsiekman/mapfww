from typing import Set, Tuple, List, Optional

from edge import Edge


class Node:

    def __init__(self, grid, positions, moves, cost, taken_edges, parent=None,
                 visited_waypoints=None, heuristic_waypoints=None):
        self.grid = grid
        self.positions = positions
        self.moves = moves
        self.cost = cost
        self.taken_edges = taken_edges
        self.parent = parent

        # Goal waypoint for each agent to visit for the heuristic
        self.heuristic_waypoints = heuristic_waypoints
        if self.heuristic_waypoints is None:
            self.heuristic_waypoints:\
                List[Optional[Tuple[int, int]]] = [None] * grid.agents

        # Copy or create waypoints list
        self.visited_waypoints: Set[Tuple[int, int]] = visited_waypoints
        if self.visited_waypoints is None:
            self.visited_waypoints = [set() for _ in range(grid.agents)]

        # Set a new goal for each agent, if required
        for agent, goal_waypoint in enumerate(self.heuristic_waypoints):
            if goal_waypoint is not None:
                continue

            # Set to the furthest waypoint
            self.heuristic_waypoints[agent] = \
                self.grid.waypoints[agent].furthest_waypoint(
                    self.positions[agent], self.visited_waypoints[agent])

        # Make node standard
        if None not in moves:
            self.moves = [None] * len(self.positions)
            self.positions = moves
            self.taken_edges = []

        self.post_moves = [move if move is not None else pos
                           for pos, move in zip(self.positions, self.moves)]

        self.heuristic = sum(grid.heuristic(agent, self.post_moves[agent],
                                            self.heuristic_waypoints[agent])
                             for agent in range(len(positions)))

        self.f = self.cost + self.heuristic

    def augmented(self):
        pass

    def expand(self):
        agent = self.moves.index(None)
        position = self.positions[agent]

        if self.agent_done(agent) and position not in self.moves:
            new_moves = self.moves[:]
            new_moves[agent] = position
            return [Node(self.grid, self.positions, new_moves, self.cost,
                         self.taken_edges, self, self.visited_waypoints)]

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

            new_moves = self.moves[:]
            new_moves[agent] = neighbour
            new_taken_edges = self.taken_edges[:]
            new_taken_edges.append(move_edge)

            # Check if this means a new waypoint is now visited for this agent
            new_visited_waypoints = self.visited_waypoints
            new_heuristic_waypoints = self.heuristic_waypoints[:]
            if self.grid.on_waypoint(agent, neighbour):
                new_visited_waypoints = [ws.copy() for ws in
                                         new_visited_waypoints]
                new_visited_waypoints[agent].add(neighbour)
                new_heuristic_waypoints[agent] = None

            new_node = Node(self.grid, self.positions, new_moves,
                            self.cost + 1, new_taken_edges, self,
                            new_visited_waypoints, new_heuristic_waypoints)
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
