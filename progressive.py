import itertools
import random
import signal
import time
from typing import List, Dict

import solver
from grid import Grid


def generate_grid(agents: int, waypoints: int, size: int) -> Grid:
    grid = Grid(size, size)
    tiles = [(x, y) for y in range(size) for x in range(size)]

    # 20% walls
    for _ in range(size * size // 5):
        tile = random.choice(tiles)
        tiles.remove(tile)
        grid.add_wall(tile[0], tile[1])

    # Agents
    for agent in range(agents):
        start = random.choice(tiles)
        tiles.remove(start)
        goal = random.choice(tiles)
        tiles.remove(goal)
        grid.add_agent(start, goal)

        # Waypoints
        for _ in range(waypoints):
            waypoint = random.choice(tiles)
            tiles.remove(waypoint)
            grid.add_waypoint(agent, waypoint[0], waypoint[1])

    return grid


def run_single(grid: Grid):
    start_time = time.time()
    solver.solve_od_id(grid)
    return time.time() - start_time


def run_progressive(timeout: int, count: int, waypoints: int, size: int):
    agents = 1
    results = []

    while True:
        print(f"==> {agents} agents")
        benchmarks = [generate_grid(agents, waypoints, size)
                      for _ in range(count)]
        print("    Generated grids")

        times = []
        print("    Benchmarking ", end="")
        for benchmark in benchmarks:
            signal.alarm(timeout)
            try:
                time = run_single(benchmark)
                signal.alarm(0)
                times.append(time)
            except Exception as e:
                pass

            print(".", end="")
        print(" done")
        results.append(times)

        print(
            f"    Finished: {len(times)} ({round(len(times) / count * 100)}%)")

        if len(times) == 0:
            break

        agents += 1

    return results


def write_table(name: str, columns: Dict[str, List]):
    label = time.strftime("%Y%m%d_%H%M%S")
    with open(f"reports/report_{label}_{name}.csv", "w") as file:
        # Headers
        file.write(";".join(str(k) for k in columns.keys()))
        file.write("\n")

        # Contents
        for i in range(max(len(columns[k]) for k in columns.keys())):
            file.write(";".join(str(columns[k][i]).replace(".", ",")
                                if i < len(columns[k]) else ""
                                for k in columns.keys()))
            file.write("\n")


def write_reports(times: List[List[float]]):
    write_table("finished", {
        "agents": [i + 1 for i, _ in enumerate(times)],
        "finished": [len(t) for t in times],
    })

    instance_times = list(itertools.chain.from_iterable(times))
    write_table("instances", {
        "instance": list(range(1, len(instance_times) + 1)),
        "time": sorted(instance_times),
    })

    time_data = {
        "instance": list(range(1, max(len(t) for t in times) + 1))
    }
    for i, time_list in enumerate(times):
        agents = i + 1
        time_data[f"{agents} agents"] = sorted(time_list)
    write_table("time", time_data)


def handler(signum, frame):
    raise Exception("Time is over")


if __name__ == "__main__":
    signal.signal(signal.SIGALRM, handler)
    write_reports(run_progressive(1, 5, 3, 8))
