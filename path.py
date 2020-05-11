from __future__ import annotations
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

    def copy(self) -> Path:
        return Path(self.positions.copy())

    def unpadded(self) -> Path:
        """
        Remove all the duplicate positions at the end of a path.
        :return: Path copy of itself, less the duplicates
        """
        new_path = self.copy()

        while len(new_path.positions) > 1:
            last = new_path.positions[-1]
            before_last = new_path.positions[-2]

            if last == before_last:
                new_path.positions.pop()
            else:
                break

        return new_path
