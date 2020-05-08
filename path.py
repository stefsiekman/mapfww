from collections import deque

from typing import Tuple


class Path:

    def __init__(self, positions=None):
        self.positions = positions
        if positions is None:
            self.positions: deque[Tuple[int, int]] = deque()

    def last_position(self):
        return self.positions[-1]

    def add_position(self, position: Tuple[int, int]):
        self.positions.append(position)

    def prepend_position(self, position: Tuple[int, int]):
        self.positions.appendleft(position)

    def __len__(self):
        return len(self.positions)

    def __getitem__(self, item):
        return self.positions[item]

    def __iter__(self):
        for pos in self.positions:
            yield pos

    def pad_to(self, length: int):
        """
        Fill the path with the last position until it has a certain length.
        """

        last_position = self.last_position()
        while len(self) < length:
            self.add_position(last_position)
