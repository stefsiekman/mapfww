import requests
import json
from time import time

from grid import Grid
from solver import solve_od, solve_od_id

URL = "https://mapfw.nl/"
headers = {
    'X-API-Token': 'secret123'
}


def load_problem(benchmark=1):
    data = {
        "algorithm": "A*+OD+ID",
        "version": "single waypoint"
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
    attempt_id, problem_id, problem = load_problem(4)

    print(f"Creating grid of {problem['width']}x{problem['height']}...")
    grid = Grid(problem["width"], problem["height"])

    print("Adding walls...")
    for y in range(problem["height"]):
        for x in range(problem["width"]):
            if problem["grid"][y][x] == 1:
                grid.add_wall(x, y)

    print("Adding agents...")
    for start, goal in zip(problem["starts"], problem["goals"]):
        grid.add_agent(tuple(start), tuple(goal))

    print("Adding waypoints...")
    for agent, waypoints in enumerate(problem["waypoints"]):
        for waypoint in waypoints:
            grid.add_waypoint(agent, waypoint[0], waypoint[1])

    print()
    print("Solving...")

    start_time = time()
    solution = solve_od_id(grid)
    time_taken = round((time() - start_time) * 1000)

    print(f"Done in {time_taken}ms")

    post_solution(attempt_id, problem_id, time_taken, solution)
