import multiprocessing
import sys
from typing import List

import click
from mapfw import MapfwBenchmarker
from mapfw.problem import Problem

import logger
from grid import Grid
from solver import solve_od_id


def solver(problem: Problem, options) -> List:
    grid = Grid(problem.width, problem.height)
    grid.options = options

    for y in range(problem.height):
        for x in range(problem.width):
            if problem.grid[y][x] == 1:
                grid.add_wall(x, y)

    for start, goal in zip(problem.starts, problem.goals):
        grid.add_agent(tuple(start), tuple(goal))

    for agent, waypoints in enumerate(problem.waypoints):
        for waypoint in waypoints:
            grid.add_waypoint(agent, waypoint[0], waypoint[1])

    solution = solve_od_id(grid)

    return solution.to_json()


@click.command()
@click.argument('benchmarks', required=True, nargs=-1, type=int)
@click.option('--name', '-n',
              type=str,
              help="Name of the algorithm version, can be left empty to "
                   "generate based on options.")
@click.option('--tsp', '-t', default="Dyn",
              type=click.Choice(["Dyn", "MST"], case_sensitive=False),
              help="Algorithm for calculating the TSP heuristic: "
                   "using dynamic programming, or a "
                   "minimum spanning tree approximation. (Default: Dyn)")
@click.option('--cores', '-c',
              type=click.IntRange(1, multiprocessing.cpu_count()),
              default=1,
              help="Number of cores to use concurrently, "
                   "requires more than one benchmark "
                   "or a progressive benchmark.")
@click.option('--sequential', '-s', is_flag=True,
              help="Force visiting the waypoints in sequential ordering as "
                   "received from the server.")
@click.option('--prio-conflicts', '-p', is_flag=True,
              help="Prioritize lower conflicts before a lower heuristic when "
                   "expanding nodes. With this option, the TSP method is "
                   "irrelevant.")
@click.option('--debug', '-d', is_flag=True,
              help="Run benchmark(s) as debug attempt.")
@click.option('--verbose', '-v', is_flag=True,
              help="Print and log extra information during solving.")
@click.option('--official', '-o', is_flag=True,
              help="Indicate this is an officially timed run on the "
                   "TU Delft server. Will append '(TU)' to the version.")
def main(benchmarks, name, tsp, cores, sequential, prio_conflicts, debug,
         verbose, official):
    if not name:
        name = f"pc={'T' if prio_conflicts else 'F'}," \
               f"ord={'T' if sequential else 'F'}"
        if not sequential:
            name = f"tsp={tsp}," + name
    if official:
        name += ' (TU)'

    def prepped_solver(problem: Problem) -> List:
        return solver(problem, {
            "tsp": tsp.lower(),
            "pc": prio_conflicts,
            "ord": sequential
        })

    api_key = open("api_key.txt", "r").read().strip()
    benchmark = MapfwBenchmarker(api_key, benchmarks, "A*+OD+ID", name,
                                 debug, prepped_solver, cores=cores)
    logger.start(info=debug, debug=verbose)
    benchmark.run()
    logger.stop()


if __name__ == "__main__":
    main(sys.argv[1:])
