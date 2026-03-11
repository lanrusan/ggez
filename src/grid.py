from collections.abc import Iterable, Iterator
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

    def get_index(self, position: Position) -> int | None:
        if position.x >= self.width or position.y >= self.height:
            return None

        return position.x + position.y * self.width

    def get_tile(self, index: int) -> Tile:
        return self._tiles[index]

    def set_tile(self, tile: Tile, index: int) -> None:
        self._tiles[index] = tile

    def neighbors(self, position: Position) -> Iterator[Position]:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        neighbors = (
            self._get_neighbor(position, direction) for direction in directions
        )
        iter = (neighbor for neighbor in neighbors if isinstance(neighbor, Position))
        return iter

    def _get_neighbor(
        self, position: Position, directions: tuple[int, int]
    ) -> Position | None:
        x = position.x + directions[0]
        y = position.y + directions[1]

        if x < 0 or y < 0:
            return None

        if x >= self.width or y >= self.height:
            return None

        return Position(x, y)


if __name__ == "__main__":
    import unittest

    class UnitTest(unittest.TestCase):
        def test_neighbor(self) -> None:
            grid = Grid(20, 20, Tile.Path)
            position = Position(10, 10)
            neighbors = grid.neighbors(position)
            self.assertEqual(next(neighbors), Position(10, 11))
            self.assertEqual(next(neighbors), Position(10, 9))
            self.assertEqual(next(neighbors), Position(11, 10))
            self.assertEqual(next(neighbors), Position(9, 10))

        def test_neighbor_out_of_bounds(self) -> None:
            grid = Grid(5, 5, Tile.Path)
            position = Position(10, 10)
            neighbors = list(grid.neighbors(position))
            self.assertEqual(len(neighbors), 0)

        def test_neighbor_some_in_bound(self) -> None:
            grid = Grid(5, 5, Tile.Path)
            position = Position(5, 4)
            neighbors = list(grid.neighbors(position))
            self.assertEqual(len(neighbors), 1)
            self.assertEqual(neighbors[0], Position(4, 4))

    test = UnitTest()
    _ = unittest.main()
