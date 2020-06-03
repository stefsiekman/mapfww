from time import time
from typing import List

from mapfw import MapfwBenchmarker
from mapfw.problem import Problem

import logger
from grid import Grid
from solver import solve_od_id


def solver(problem: Problem) -> List:
    grid = Grid(problem.width, problem.height)

    parse_start_time = time()
    for y in range(problem.height):
        for x in range(problem.width):
            if problem.grid[y][x] == 1:
                grid.add_wall(x, y)

    for start, goal in zip(problem.starts, problem.goals):
        grid.add_agent(tuple(start), tuple(goal))

    for agent, waypoints in enumerate(problem.waypoints):
        for waypoint in waypoints:
            grid.add_waypoint(agent, waypoint[0], waypoint[1])

    start_time = time()
    solution = solve_od_id(grid)
    time_taken = round((time() - start_time) * 1000)

    return solution.to_json()


def run_for(id, for_real):
    api_key = open("api_key.txt", "r").read().strip()
    benchmark = MapfwBenchmarker(api_key, id,
                                 "A*+OD+ID", "opt TSP", not for_real,
                                 solver, cores=2)
    logger.start(info=benchmark.debug)
    benchmark.run()
    logger.stop()


if __name__ == "__main__":
    bid = int(input("Benchmark ID: "))
    for_real = input("For real (y/[n]): ")
    run_for(bid, for_real == 'y')
    # run_for([31, 32], False)
    # for id in [55, 27, 33, 62]:
    #     run_for(id, True)
