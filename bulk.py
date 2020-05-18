"""
Class for running benchmarks in bulk on some server. Results can be obtained
from multiple sources, and the running can be stopped at any time.
"""
import os

from git import Repo


def run_bulk(name, agent_range, waypoint_range):
    pass


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

    min_agents = int(input("Min. # agents:    "))
    max_agents = int(input("Max. # agents:    "))
    min_waypoints = int(input("Min. # waypoints: "))
    max_waypoints = int(input("Max. # waypoints: "))
