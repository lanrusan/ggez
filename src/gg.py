from enum import Enum
import tkinter as tk

from grid import Grid, Tile


class Mode(Enum):
    Editing = 0
    Animating = 1
    Finished = 2


class GridGuide:
    def __init__(
        self, root: tk.Tk, width: int = 20, height: int = 20, grid_scale: int = 25
    ) -> None:
        self.root: tk.Tk = root
        self.grid_scale: int = grid_scale
        self.grid: Grid = Grid(width, height, Tile.Path)
        self.mode: Mode = Mode.Editing

        self.setup_ui()

    def setup_ui(self):
        width = self.grid.width * self.grid_scale
        height = self.grid.height * self.grid_scale
        self.canvas: tk.Canvas = tk.Canvas(self.root, width=width, height=height)
