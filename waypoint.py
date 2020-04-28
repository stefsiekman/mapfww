class Waypoint:

    def __init__(self, grid, agent, x, y):
        self.grid = grid
        self.x = x
        self.y = y
        self.goal_distance = grid.goal_heuristics[agent][y][x]
        self.heuristics = grid.backtrack_heuristics((x, y))

    def position(self):
        return self.x, self.y

    def heuristic(self, x, y):
        if self.heuristics[y][x] is None:
            print("Requested from None", x, y)
        return self.goal_distance + self.heuristics[y][x]