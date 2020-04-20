from queue import PriorityQueue, Queue

import imageio as imageio

from grid import Grid
from node import Node

from PIL import Image


def save_image(node, filename):
    pixels = [(255, 255, 255)] * (node.grid.w * node.grid.h)

    for y in range(node.grid.h):
        for x in range(node.grid.w):
            if node.grid.walls[y][x]:
                pixels[x + y * node.grid.w] = (0, 0, 0)
            elif (x, y) == node.positions[0]:
                pixels[x + y * node.grid.w] = (0, 0, 255)
            elif (x, y) == node.positions[1]:
                pixels[x + y * node.grid.w] = (128, 128, 255)
            elif (x, y) == node.grid.starts[0]:
                pixels[x + y * node.grid.w] = (0, 255, 0)
            elif (x, y) == node.grid.starts[1]:
                pixels[x + y * node.grid.w] = (128, 255, 128)
            elif (x, y) == node.grid.goals[0]:
                pixels[x + y * node.grid.w] = (255, 0, 0)
            elif (x, y) == node.grid.goals[1]:
                pixels[x + y * node.grid.w] = (255, 128, 128)

    img = Image.new("RGB", (node.grid.w, node.grid.h))
    img.putdata(pixels)
    re_img = img.resize((node.grid.w * 100, node.grid.h * 100), Image.NEAREST)
    re_img.save(filename)


def print_result(final_node: Node):
    stack = []
    current_node = final_node
    while current_node is not None:
        stack.append(current_node)
        current_node = current_node.parent

    index = 0
    filenames = []
    while len(stack) > 0:
        print_node = stack.pop()
        if not print_node.is_standard():
            continue

        index += 1
        filename = f"img/step-{index}.png"
        filenames.append(filename)
        save_image(print_node, filename)

    with imageio.get_writer("img/animation.gif", mode='I', duration=0.5) as writer:
        for filename in filenames:
            image = imageio.imread(filename)
            writer.append_data(image)


if __name__ == "__main__":
    # Figure 3 from (Standley, 2010)
    print("Creating grid...")
    grid = Grid(5, 3)
    grid.add_wall(0, 1)
    grid.add_wall(1, 1)
    grid.add_wall(3, 1)
    grid.add_wall(4, 1)

    print("Adding agents...")
    grid.add_agent((0, 0), (0, 2))
    grid.add_agent((4, 2), (4, 0))

    print()
    print("Solving...")

    open_nodes = PriorityQueue()
    node_id = 0
    open_nodes.put(
        (0, node_id, Node(grid, [(0, 0), (4, 2)], [None, None], 0, [])))
    node_id += 1

    while not open_nodes.empty():
        f, id, node = open_nodes.get()

        if node.all_done():
            print("Done")
            print_result(node)
            print("Saved images")
            break

        for new_node in node.expand():
            # print(f"Adding new node to queue: {new_node.f} {new_node}")
            item = (new_node.f, node_id, new_node)
            node_id += 1
            open_nodes.put(item)
