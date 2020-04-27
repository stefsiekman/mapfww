import requests
import json
from time import time

from queue import PriorityQueue, Queue

from grid import Grid
from node import Node

URL = "https://mapfw.nl/"
headers = {
    'X-API-Token': 'secret123'
}


def load_problem(benchmark=1):
    data = {
        "algorithm": "CBS",
        "version": "0"
    }
    r = requests.post(f"{URL}api/benchmarks/{benchmark}/problems",
                      headers=headers, json=data)

    problem_id = r.json()["problems"][0]["id"]
    problem = json.loads(r.json()["problems"][0]["problem"])
    attempt_id = r.json()["attempt"]

    problem["width"] = int(problem["width"])
    problem["height"] = int(problem["height"])

    return attempt_id, problem_id, problem


def post_solution(attempt_id, problem_id, time, solution):
    data = {
        "solutions": [
            {
                "problem": problem_id,
                "time": time,
                "solution": solution
            }
        ]
    }
    requests.post(f"{URL}api/attempts/{attempt_id}/solutions",
                  headers=headers, json=data)
    print("Submitted response:", problem_id)


if __name__ == "__main__":
    attempt_id, problem_id, problem = load_problem()
    start_time = time()

    print(f"Creating grid of {problem['width']}x{problem['height']}...")
    grid = Grid(problem["width"], problem["height"])

    print("Adding walls...")
    walls = 0
    for y in range(problem["height"]):
        for x in range(problem["width"]):
            if problem["grid"][y][x] == 1:
                grid.add_wall(x, y)
                walls += 1
    print(f"    added {walls} walls")

    print("Adding agents...")
    for start, goal in zip(problem["starts"], problem["goals"]):
        print(f"    from {start}  \tto {goal}")
        grid.add_agent(tuple(start), tuple(goal))

    print()
    print("Solving...")

    open_nodes = PriorityQueue()
    node_id = 0
    open_nodes.put((0, node_id, grid.root_node()))
    node_id += 1

    final_node: Node = None

    while not open_nodes.empty():
        f, id, node = open_nodes.get()

        if node.all_done():
            final_node = node
            break

        for new_node in node.expand():
            # print(f"Adding new node to queue: {new_node.f} {new_node}")
            item = (new_node.f, node_id, new_node)
            node_id += 1
            open_nodes.put(item)

    time_taken = round((time() - start_time) * 1000)
    print(f"Done in {time_taken}ms, with {node_id} nodes")

    positions = []
    while final_node is not None:
        if final_node.is_standard():
            positions.append([list(p) for p in final_node.positions])
        final_node = final_node.parent

    positions.reverse()

    solution = [[positions[t][i] for t in range(len(positions))]
                for i in range(grid.agents)]

    post_solution(attempt_id, problem_id, time_taken, solution)
