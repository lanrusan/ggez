from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, order=True)
class Position:
    x: int
    y: int


class TileConversionError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Tile(Enum):
    Wall = 0
    Path = 1

    @property
    def cost(self) -> int | None:
        match self:
            case Tile.Wall:
                return None
            case Tile.Path:
                return 10

    @classmethod
    def from_int(cls, num: int) -> Tile:
        tiles = list(cls)
        if num < 0 or num >= len(tiles):
            raise TileConversionError

        return tiles[num]


class MapImportError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DistanceKind(Enum):
    MANHATTAN = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    EUCLIDEAN = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, -1), (1, -1)]


class Grid:
    def __init__(self, width: int, height: int, default_tile: Tile) -> None:
        self.width: int = width
        self.height: int = height
        self._tiles: list[Tile] = [default_tile for _ in range(width * height)]
        self.distance_kind: DistanceKind = DistanceKind.MANHATTAN

    def get_index(self, position: Position) -> int | None:
        if position.x >= self.width or position.y >= self.height:
            return None

        return position.x + position.y * self.width

    def get_tile(self, index: int) -> Tile:
        return self._tiles[index]

    def set_tile(self, index: int, tile: Tile) -> None:
        self._tiles[index] = tile

    def neighbors(self, position: Position) -> Iterator[Position]:
        neighbors = (
            self._get_neighbor(position, direction)
            for direction in self.distance_kind.value
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

    def into_str(self) -> str:
        buffer = ""

        header = f"{self.width} {self.height}\n"
        buffer += header

        data = " ".join(str(tile.value) for tile in self._tiles)
        buffer += data

        return buffer

    @staticmethod
    def from_str(grid_data: str) -> Grid:
        """This function raises an exception if the given str does not follow the proper grid format.
        The grid format is as follows: `width height`, `\\n`, `tiles`
        Where 'tiles' are the values of the given Tile enums.
        """

        try:
            buffer = grid_data.split("\n")
            header = buffer[0].split(" ")
            data = buffer[1].split(" ")

            width, height = int(header[0]), int(header[1])
            data = [Tile.from_int(int(tile)) for tile in data]
            grid = Grid(width, height, Tile.Path)
            grid._tiles = data

            return grid
        except (ValueError, TileConversionError, IndexError):
            raise MapImportError


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

        def test_into_str(self) -> None:
            grid = Grid(3, 3, Tile.Path)
            grid.set_tile(3, Tile.Wall)
            as_str = grid.into_str()
            expected = """3 3\n1 1 1 0 1 1 1 1 1"""
            self.assertEqual(as_str, expected)

        def test_from_str(self) -> None:
            as_str = """3 3\n1 1 1 0 1 1 1 1 1"""
            grid = Grid.from_str(as_str)
            expected = Grid(3, 3, Tile.Path)
            expected.set_tile(3, Tile.Wall)
            self.assertEqual(grid._tiles, expected._tiles)  # pyright: ignore [reportPrivateUsage]

        @unittest.expectedFailure
        def test_from_str_broken(self) -> None:
            as_str = """3 3\n1 1 1 0 1 1 1 1 1 123 123"""
            grid = Grid.from_str(as_str)
            expected = Grid(3, 3, Tile.Path)
            expected.set_tile(3, Tile.Wall)
            self.assertEqual(grid._tiles, expected._tiles)  # pyright: ignore [reportPrivateUsage]

    test = UnitTest()
    _ = unittest.main()
