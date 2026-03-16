from abc import ABC, abstractmethod
from dataclasses import dataclass
import heapq
import math
from typing import Callable, override

from grid import Grid, Position


def manhattan_distance(a: Position, b: Position) -> int:
    return (abs(a.x - b.x) + abs(a.y - b.y)) * 11


def euclidean_distance(a: Position, b: Position) -> int:
    return int(math.hypot(a.x - b.x, a.y - b.y)) * 11


def octile_distance(a: Position, b: Position) -> int:
    dx = abs(a.x - b.x)
    dy = abs(a.y - b.y)

    return abs(dx - dy) * 10 + min(dx, dy) * 14


@dataclass(order=True)
class Node:
    cost: int
    position: Position


@dataclass(frozen=True)
class SearchResult:
    visited: list[Position]
    path: list[Position] | None


class Solver(ABC):
    @abstractmethod
    def solve(self, grid: Grid, start: Position, end: Position) -> SearchResult:
        raise NotImplementedError()


class AStar(Solver):
    def __init__(self, heuristic: Callable[[Position, Position], int]) -> None:
        self.heuristic: Callable[[Position, Position], int] = heuristic

    @override
    def solve(self, grid: Grid, start: Position, end: Position) -> SearchResult:
        return a_star(grid, start, end, self.heuristic)


class Dijkstra(Solver):
    @override
    def solve(self, grid: Grid, start: Position, end: Position) -> SearchResult:
        return a_star(grid, start, end, lambda start, end,: 0)


def a_star(
    grid: Grid,
    start: Position,
    end: Position,
    heuristic: Callable[[Position, Position], int],
) -> SearchResult:
    open_set: list[Node] = []
    node_parents: dict[Position, Position] = {}
    g_scores: list[int] = [999999] * (grid.width * grid.height)

    visited: list[Position] = []

    heapq.heappush(open_set, Node(heuristic(start, end), start))

    index = grid.get_index(start)
    if index is None:
        return SearchResult(visited, None)
    g_scores[index] = 0

    while open_set:
        current = heapq.heappop(open_set)

        index = grid.get_index(current.position)
        if index is None:
            continue

        current_g_score = g_scores[index]
        if current.cost > current_g_score + heuristic(current.position, end):
            continue

        visited.append(current.position)

        if current.position == end:
            path = [current.position]
            current_position = current.position

            while True:
                parent = node_parents.get(current_position)
                if parent is None:
                    break

                path.append(parent)
                current_position = parent

            path.reverse()

            return SearchResult(visited, path)

        for neigbhor in grid.neighbors(current.position):
            neighbor_index = grid.get_index(neigbhor)
            if neighbor_index is None:
                continue

            neighbor_cost = grid.get_tile(neighbor_index).cost
            if neighbor_cost is None:
                continue

            neighbor_g_score = current_g_score + neighbor_cost
            if neighbor_g_score < g_scores[neighbor_index]:
                node_parents[neigbhor] = current.position
                g_scores[neighbor_index] = neighbor_g_score

                f_score = neighbor_g_score + heuristic(neigbhor, end)
                heapq.heappush(open_set, Node(f_score, neigbhor))

    return SearchResult(visited, None)
