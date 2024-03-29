"""
Class for running benchmarks in bulk on some server. Results can be obtained
from multiple sources, and the running can be stopped at any time.
"""
import time
from multiprocessing import Process, cpu_count, SimpleQueue, Lock
import os

from func_timeout import func_timeout, FunctionTimedOut
from git import Repo

from database import Database
from grid import Grid
from progressive import run_single


def parse_grid(grid_data) -> Grid:
    grid = Grid(grid_data["width"], grid_data["height"])

    for y in range(grid.h):
        for x in range(grid.w):
            if grid_data["walls"][y][x]:
                grid.add_wall(x, y)

    for start, goal in zip(grid_data["starts"], grid_data["goals"]):
        grid.add_agent(tuple(start), tuple(goal))

    for agent, waypoints in enumerate(grid_data["waypoints"]):
        for x, y in waypoints:
            grid.add_waypoint(agent, x, y)

    return grid


def run_single_from_data(grid_data) -> float:
    return run_single(parse_grid(grid_data))


def work(version_id, computer_id, index, size, busy_queue: SimpleQueue,
         result_queue: SimpleQueue,
         db: Database):
    time_limit = 100
    while True:
        agents, waypoints = busy_queue.get()

        start_time = time.time()
        run_id, grid_data = db.get_grid(version_id, computer_id, index,
                                        time_limit, agents, waypoints, size,
                                        20)
        overhead = time.time() - start_time

        res = None
        error = None

        try:
            res = func_timeout(time_limit, run_single_from_data,
                               args=(grid_data,))
        except FunctionTimedOut:
            pass
        except Exception as e:
            error = e

        result_queue.put((index, run_id, res, error, overhead))
        busy_queue.put((agents, waypoints))


def run_bulk(version_name, computer_name, size, agent_range, waypoint_range):
    thread_number = thread_count()
    db = Database()

    version_id = db.get_version_id(version_name)
    computer_id = db.get_computer_id(computer_name)

    busy_queue = SimpleQueue()
    result_queue = SimpleQueue()

    # Populate with all combinations within range
    for agents in range(agent_range[0], agent_range[1] + 1):
        for waypoints in range(waypoint_range[0], waypoint_range[1] + 1):
            if agents < 1:
                continue
            busy_queue.put((agents, waypoints))

    workers = [Process(target=work, args=(version_id, computer_id, i, size,
                                          busy_queue, result_queue, db))
               for i in range(thread_number)]

    for worker in workers:
        worker.start()

    runs = 0
    while True:
        thread_index, run_id, runtime, error, overhead = result_queue.get()
        start_time = time.time()
        db.complete_run(run_id, runtime)
        grid_info = db.grid_info(run_id)
        overhead += time.time() - start_time

        runs += 1

        print(f"[Process {thread_index}] Benchmark #{runs} on "
              f"{grid_info} ", end="")
        if runtime is not None:
            print(f"in {round(runtime,2)} sec", end="")
        else:
            print("timeout", end="")
        print(f" WITH ERROR: {error}" if error is not None else "", end="")

        print(f" (OH {round(overhead * 1000)} ms)")


def thread_count():
    cores = cpu_count()
    print(f"This system has {cores} cores")
    reserves = int(input("Reserve cores [1]: ") or 1)
    assert 0 <= reserves < cores, "Valid reserve count"

    using = cores - reserves
    print(f"Benchmarks will be run on {using} cores")

    return cores - reserves


def validate_repo():
    repo = Repo(os.path.dirname(os.path.realpath(__file__)))
    assert not repo.bare, "Git repo is initialized"

    if repo.is_dirty():
        return

    return repo.head.object.hexsha


if __name__ == "__main__":
    head_hex = validate_repo()
    if head_hex is None:
        print("Commit all the code changes first")
        exit()

    computer_label = input("Label this computer [iMac]: ") or "iMac"

    min_agents = int(input("Min # agents [1]: ") or 1)
    max_agents = int(input("Max # agents [10]: ") or 10)
    min_waypoints = int(input("Min # waypoints [0]: ") or 0)
    max_waypoints = int(input("Max # waypoints [10]: ") or 10)
    grid_size = int(input("Grid size [16]: ") or 16)

    run_bulk(head_hex, computer_label, grid_size,
             (min_agents, max_agents),
             (min_waypoints, max_waypoints))
