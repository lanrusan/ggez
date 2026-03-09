from abc import ABC
from dataclasses import dataclass

from grid import Grid, Position


@dataclass(frozen=True)
class SearchResult:
    visited: list[Position]
    path: list[Position] | None


class Solver(ABC):
    def solve(self, grid: Grid, start: Position, end: Position) -> SearchResult:
        raise NotImplementedError()
