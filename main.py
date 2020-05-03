from time import time

from mapfw import MapfwBenchmarker

from grid import Grid
from solver import solve_od_id

if __name__ == "__main__":
    benchmark = MapfwBenchmarker("secret123", 13,
                                 "A*+OD+ID", "mult. waypoints, prio")

    for problem in benchmark:
        print(f"Creating grid of {problem.width}x{problem.height}...")
        grid = Grid(problem.width, problem.height)

        parse_start_time = time()
        print("Adding walls...")
        for y in range(problem.height):
            for x in range(problem.width):
                if problem.grid[y][x] == 1:
                    grid.add_wall(x, y)

        print("Adding agents...")
        for start, goal in zip(problem.starts, problem.goals):
            grid.add_agent(tuple(start), tuple(goal))

        print("Adding waypoints...")
        for agent, waypoints in enumerate(problem.waypoints):
            for waypoint in waypoints:
                grid.add_waypoint(agent, waypoint[0], waypoint[1])

        grid.pretty_print()

        print(f"\nParsing done in "
              f"{round((time() - parse_start_time) * 1000, 2)} ms")

        print()
        print("Solving...")

        start_time = time()
        solution = solve_od_id(grid)
        time_taken = round((time() - start_time) * 1000)

        print(f"Done in {time_taken}ms")

        problem.add_solution(solution)
