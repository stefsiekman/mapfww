import json
from math import factorial
from pprint import PrettyPrinter
from queue import Queue
from random import randint


def DP_TSP(distances_array):
    n = len(distances_array)
    all_points_set = set(range(n))

    # memo keys: tuple(sorted_points_in_path, last_point_in_path)
    # memo values: tuple(cost_thus_far, next_to_last_point_in_path)
    memo = {((0,), 0): (0, None)}
    queue = Queue()
    queue.put(((0,), 0))

    iterations = 0

    while not queue.empty():
        prev_visited, prev_last_point = queue.get()
        prev_dist, _ = memo[(prev_visited, prev_last_point)]
        to_visit = all_points_set.difference(set(prev_visited))
        
        iterations += 1

        for new_last_point in to_visit:
            new_visited = tuple(sorted(list(prev_visited) + [new_last_point]))
            new_dist = (prev_dist + distances_array[prev_last_point][
                new_last_point])

            if (new_visited, new_last_point) not in memo:
                memo[(new_visited, new_last_point)] = (
                    new_dist, prev_last_point)
                queue.put((new_visited, new_last_point))
            else:
                if new_dist < memo[(new_visited, new_last_point)][0]:
                    memo[(new_visited, new_last_point)] = (
                        new_dist, prev_last_point)

    pp = PrettyPrinter(indent=4)
    pp.pprint(memo)

    print(f"Solved in {iterations} iterations ({n}! = {factorial(n)})")

    full_path = tuple(range(n))
    for end in range(1, n):
        print(f"Ending at {end}")
        print(f"Path: {full_path}")
        print(F"Cost: {memo[full_path, end][0]}")



def gen_array(size):
    return [[randint(1, 10) for _ in range(size)] for _ in range(size)]


if __name__ == "__main__":
    DP_TSP(gen_array(4))
