class Edge:

    def __init__(self, a, b):
        points = sorted([a, b], key=lambda k: [k[1], k[0]])
        self.a = points[0]
        self.b = points[1]

    def conflicts(self, other):
        if self.a == other.a and self.b == other.b:
            return True

        return False

    def __str__(self):
        return f"Edge({self.a}, {self.b})"
