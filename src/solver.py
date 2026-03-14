from abc import ABC, abstractmethod
from dataclasses import dataclass
import heapq
from typing import override

from grid import Grid, Position


def manhattan_distance(a: Position, b: Position) -> int:
    return (abs(a.x - b.x) + abs(a.y - b.y)) * 11


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
    @override
    def solve(self, grid: Grid, start: Position, end: Position) -> SearchResult:
        open_set: list[Node] = []
        node_parents: dict[Position, Position] = {}
        g_scores: list[int] = [999999] * (grid.width * grid.height)

        visited: list[Position] = []

        heapq.heappush(open_set, Node(manhattan_distance(start, end), start))

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
            if current.cost > current_g_score + manhattan_distance(
                current.position, end
            ):
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

                path.append(start)
                path.reverse()

                return SearchResult(visited, path)

            for neighbbor in grid.neighbors(current.position):
                neighbor_index = grid.get_index(neighbbor)
                if neighbor_index is None:
                    continue

                neighbor_cost = grid.get_tile(neighbor_index).cost
                if neighbor_cost is None:
                    continue

                neighbor_g_score = current_g_score + neighbor_cost
                if neighbor_g_score < g_scores[neighbor_index]:
                    node_parents[neighbbor] = current.position
                    g_scores[neighbor_index] = neighbor_g_score

                    f_score = neighbor_g_score + manhattan_distance(neighbbor, end)
                    heapq.heappush(open_set, Node(f_score, neighbbor))

        return SearchResult(visited, None)
