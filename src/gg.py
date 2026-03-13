from tkinter import Button, Canvas, Frame, Tk
import tkinter as tk
from tkinter import filedialog

from grid import Grid, Position, Tile
from solver import AStar, Solver


class Editing:
    pass


class Animating:
    def __init__(self, visited: list[Position], path: list[Position] | None) -> None:
        self.visited: list[Position] = visited
        self.path: list[Position] | None = path
        self.current: int = 0


class Finished:
    def __init__(self, visited: list[Position], path: list[Position] | None) -> None:
        self.visited: list[Position] = visited
        self.path: list[Position] | None = path


type Mode = Editing | Animating | Finished


class GridGuide:
    def __init__(
        self, root: Tk, width: int = 20, height: int = 20, cell_size: int = 25
    ) -> None:
        self.root: Tk = root
        self.cell_size: int = cell_size
        self.grid: Grid = Grid(width, height, Tile.Path)
        self.mode: Mode = Editing()
        self.solver: Solver = AStar()

        top_toolbar_frame: Frame = Frame(self.root)
        top_toolbar_frame.grid(column=0, row=0, sticky="nw")
        self._setup_top_toolbar(top_toolbar_frame)

        right_toolbar_frame: Frame = Frame(self.root)
        right_toolbar_frame.grid(column=1, row=1, sticky="ne")
        self._setup_right_toolbar(right_toolbar_frame)

        bottom_toolbar_frame: Frame = Frame(self.root)
        bottom_toolbar_frame.grid(column=0, row=2, sticky="sw")
        self._setup_bottom_toolbar(bottom_toolbar_frame)

        width = self.grid.width * self.cell_size
        height = self.grid.height * self.cell_size
        canvas: Canvas = Canvas(self.root, width=width, height=height)
        canvas.grid(column=0, row=1)
        self._setup_canvas(canvas)

    def _setup_top_toolbar(self, frame: Frame) -> None:
        def import_file() -> None:
            file_name = filedialog.askopenfilename()
            with open(file_name) as f:
                data = f.read()
                grid = Grid.from_str(data)
                self.grid = grid

        def export_file() -> None:
            file_name = filedialog.asksaveasfilename()
            data = self.grid.into_str()
            with open(file_name, "w") as f:
                _ = f.write(data)

        import_button: Button = Button(frame, text="Import map", command=import_file)
        export_button: Button = Button(frame, text="Export map", command=export_file)

        for widget in [import_button, export_button]:
            widget.pack(side=tk.LEFT, padx=2, pady=2)

    def _setup_right_toolbar(self, frame: Frame) -> None:
        pass

    def _setup_bottom_toolbar(self, frame: Frame) -> None:
        pass

    def _setup_canvas(self, canvas: Canvas) -> None:
        pass
