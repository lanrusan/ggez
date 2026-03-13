from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override

from grid import Grid, Position


@dataclass(frozen=True)
class SearchResult:
    visited: list[Position]
    path: list[Position] | None


class Solver(ABC):
    @abstractmethod
    def solve(self, grid: Grid, start: Position, end: Position) -> SearchResult:
        raise NotImplementedError()


class AStar(Solver):
    @override
    def solve(self, grid: Grid, start: Position, end: Position) -> SearchResult:
        raise NotImplementedError()
