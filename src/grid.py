from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, order=True)
class Position:
    x: int
    y: int


class Tile(Enum):
    Path = 0
    Wall = 1


class Grid:
    def __init__(self, width: int, height: int, default_tile: Tile) -> None:
        self.width: int = width
        self.height: int = height
        self._tiles: list[Tile] = [default_tile for _ in range(width * height)]

    def get_tile(self, index: int) -> Tile:
        return self._tiles[index]
