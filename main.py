from queue import PriorityQueue

from grid import Grid
from node import Node

if __name__ == "__main__":
    # Figure 3 from (Standley, 2010)
    print("Creating grid...")
    grid = Grid(5, 2)
    grid.add_wall(1, 0)
    grid.add_wall(2, 0)

    print("Adding agents...")
    grid.add_agent((0, 1), (3, 1))
    grid.add_agent((1, 1), (4, 1))

    print()
    print("Solving...")

    open_nodes = PriorityQueue()
    node_id = 0
    open_nodes.put((0, node_id, Node(grid, [(0, 1), (1, 1)], [None, None], 0, [])))
    node_id += 1

    while not open_nodes.empty():
        print("\n\n=== Node from queue")
        f, id, node = open_nodes.get()

        if node.all_done():
            print("ALLL DONEEEE")
            break

        for new_node in node.expand():
            # print(f"Adding new node to queue: {new_node.f} {new_node}")
            item = (new_node.f, node_id, new_node)
            node_id += 1
            open_nodes.put(item)
