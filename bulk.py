"""
Class for running benchmarks in bulk on some server. Results can be obtained
from multiple sources, and the running can be stopped at any time.
"""
from multiprocessing import Queue, Process, cpu_count, SimpleQueue
import os
import time
from queue import Queue
from random import randint

from func_timeout import func_timeout, FunctionTimedOut
from git import Repo

from progressive import save_generate_grid, run_single


def work(index, size, busy_queue: Queue, result_queue: Queue):
    while True:
        agents, waypoints = busy_queue.get(block=True)

        grid = save_generate_grid(agents, waypoints, size)
        res = None

        try:
            res = func_timeout(10, run_single, args=(grid,))
        except FunctionTimedOut:
            pass

        result_queue.put((index, agents, waypoints, size, res))
        busy_queue.put((agents, waypoints))


def run_bulk(name, size, agent_range, waypoint_range):
    thread_number = thread_count()

    busy_queue = Queue()
    result_queue = SimpleQueue()

    # Populate with all combinations within range
    for agents in range(agent_range[0], agent_range[1] + 1):
        for waypoints in range(waypoint_range[0], waypoint_range[1] + 1):
            if agents < 1:
                continue
            busy_queue.put((agents, waypoints))

    workers = [Process(target=work, args=(i, size, busy_queue, result_queue))
               for i in range(thread_number)]

    for worker in workers:
        worker.start()

    result_file = "runs.csv"
    if not os.path.exists(result_file):
        with open(result_file, "w") as file:
            file.write("Version,Thread,Agents,Waypoints,Size,Time\n")

    runs = 0
    with open(result_file, "a") as file:
        while True:
            res = result_queue.get()
            res_time = res[4] if res[4] is not None else ""
            file.write(f"{name},{res[0]},{res[1]},{res[2]},{res[3]},{res[4]}\n")
            file.flush()
            runs += 1
            print(f"\rRan {runs} benchmarks", end="", flush=True)


def thread_count():
    cores = cpu_count()
    print(f"This system has {cores} cores")
    inp = input("Reserve cores [0]: ")
    reserves = int(inp) if inp is not "" else 0
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

    min_agents = int(input("Min # agents: "))
    max_agents = int(input("Max # agents: "))
    min_waypoints = int(input("Min # waypoints: "))
    max_waypoints = int(input("Max # waypoints: "))
    grid_size = int(input("Grid size: "))

    run_bulk(head_hex, grid_size,
             (min_agents, max_agents),
             (min_waypoints, max_waypoints))
