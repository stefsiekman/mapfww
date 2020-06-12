from typing import Dict, Tuple


class MST:

    def __init__(self):
        self.vertices: Dict[Tuple[int, int], int] = dict()
        self.edges = []
        self.next_vertex = 0

    def add_vertices(self, positions):
        for pos in positions:
            self.add_vertex(pos)

    def add_vertex(self, pos):
        self.vertices[pos] = self.next_vertex
        self.next_vertex += 1

    def add_edge(self, a, b, cost):
        self.edges.append(((self.vertices[a], self.vertices[b]), cost))

    def cost(self) -> int:
        self.edges.sort(key=lambda edge: edge[1])

        total_cost = 0
        groups = [[v] for v in self.vertices.values()]

        for (v1, v2), cost in self.edges:
            g1 = next(g for g in groups if v1 in g)
            g2 = next(g for g in groups if v2 in g)

            if g1 == g2:
                continue

            total_cost += cost
            g1 += g2
            groups.remove(g2)

            if len(groups) == 1:
                break

        return total_cost
