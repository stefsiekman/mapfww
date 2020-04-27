from edge import Edge


class Node:

    def __init__(self, grid, positions, moves, cost, taken_edges, parent=None):
        self.grid = grid
        self.positions = positions
        self.moves = moves
        self.cost = cost
        self.taken_edges = taken_edges
        self.parent = parent

        # Make node standard
        if None not in moves:
            self.moves = [None] * len(self.positions)
            self.positions = moves
            self.taken_edges = []

        self.post_moves = [move if move is not None else pos
                           for pos, move in zip(self.positions, self.moves)]

        self.heuristic = sum(grid.heuristic(agent, self.post_moves[agent])
                             for agent in range(len(positions)))

        self.f = self.cost + self.heuristic

    def augmented(self):
        pass

    def expand(self):
        agent = self.moves.index(None)
        position = self.positions[agent]

        if self.grid.goals[agent] == position:
            new_moves = self.moves[:]
            new_moves[agent] = position
            return [Node(self.grid, self.positions, new_moves, self.cost,
                         self.taken_edges, self)]

        new_nodes = []

        for neighbour in self.grid.valid_neighbours(position):
            # Check if cell is occupied by moved agent
            if neighbour in self.moves:
                continue

            # Check for crossing edges
            move_edge = Edge(position, neighbour)
            if any(move_edge.conflicts(edge) for edge in self.taken_edges):
                continue

            new_moves = self.moves[:]
            new_moves[agent] = neighbour
            new_taken_edges = self.taken_edges[:]
            new_taken_edges.append(move_edge)
            new_node = Node(self.grid, self.positions, new_moves,
                            self.cost + 1, new_taken_edges, self)
            new_nodes.append(new_node)

        return new_nodes

    def is_standard(self):
        return all(move is None for move in self.moves)

    def all_done(self):
        return all(pos == goal
                   for pos, goal in zip(self.positions, self.grid.goals))

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
