from tkinter import Button, Canvas, Event, Frame, Tk
import tkinter as tk
from tkinter import filedialog

from grid import Grid, Position, Tile
from solver import AStar, Solver


class Viewing:
    pass


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


type Mode = Viewing | Editing | Animating | Finished


class GridGuide:
    def __init__(
        self, root: Tk, width: int = 20, height: int = 20, cell_size: int = 25
    ) -> None:
        self.root: Tk = root
        self.cell_size: int = cell_size
        self.grid: Grid = Grid(width, height, Tile.Path)
        self.mode: Mode = Editing()
        self.solver: Solver = AStar()
        self.start: Position | None=None
        self.end: Position | None=None
        self.undo_stack = []
        self.redo_stack = []
        
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
        self.canvas: Canvas = Canvas(self.root, width=width, height=height)
        self.canvas.grid(column=0, row=1)
        self._setup_canvas()
        self.canvas.bind("<Button-1>", self.start_button)
        self.canvas.bind("<Button-3>", self.end_button)
        self.canvas.bind("<B1-Motion>", self.wall_drag)

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

    def save_stat(self):
        state= (
            self.grid_tiles.copy(),
            self.start,
            self.end
        )
        self.undo_stack.append(state)
        self.redo_stack.clear()
    def restore_state(self, state):
        tiles, start, end= state
        self.grid._tiles = tiles
        self.start = start
        self.end = end
        self.draw_grid()
    def undo(self):
        if not self.undo_stack:
            return
        current = (
            self.grid._tiles.copy(),
            self.start,
            self.end
        )
        self.redo_stack.append(current)
        state = self.undo_stack.pop()
        self.restore_state(state) 

    def redo(self):
        if not self.redo_stack:
            return
        current = (
            self.grid._tiles.copy(),
            self.start,
            self.end
        )
        self.undo_stack.append(current)

        state = self.redo_stack.pop()
        self.restore_state(state)

    def cursor_location(self, x, y):
        x_pos = x // self.cell_size
        y_pos = y // self.cell_size

        return Position(x_pos, y_pos)
    
    def start_button(self, click):
        pos = self.cursor_location(click.x, click.y)
        index = self.grid.get_index(pos)

        if index is None:
            return

        self.grid.set_tile(index, Tile.Wall)
        self.draw_grid()

    def wall_drag(self, click):
        pos = self.cursor_location(click.x, click.y)
        index = self.grid.get_index(pos)

        if index is None:
            return

        self.grid.set_tile(index, Tile.Wall)
        self.draw_grid()

    def end_button(self, click):
        pos = self.cursor_location(click.x, click.y)
        index = self.grid.get_index(pos)
        if index is None:
            return
        
        tile = self.grid.get_tile(index)
        if tile == Tile.Wall:
            return
        
        if self.start is None:
            self.start = pos
        elif self.end is None:
            self.end = pos
        else:
            self.start = pos
            self.end = None
        self.draw_grid()
    def _setup_right_toolbar(self, frame: Frame) -> None:
        self.tile = Tile.Path

        def set_animating():
            self.mode = Animating([], [])
            edit_button.config(state="normal") 

        def act_mode():
            self.mode = Editing()
            edit_button.config(state="disabled")
        
        def change_tile(selection):
            if selection == "Path":
                self.tile = Tile.Path
            elif selection == "Wall":
                self.title = Tile.Wall

        solve_button = tk.Button(frame, text= "Solve", command= lambda: print("to do"))
        solve_button.grid(row=0, column=1, sticky="NSEW")
        solve_button.config(command=set_animating)

        clear_button = tk.Button(frame, text= "Clear", command= lambda: print("to do no.2"))
        clear_button.grid(row=0, column=2, sticky= "NSEW")

        edit_button = tk.Button(frame, text= "Edit",command=act_mode, state="disabled")
        edit_button.grid(row=1, column= 1, sticky= "SEW")
       
        path_and_wall_button = tk.StringVar()
        path_and_wall_button.set("Path")

        options = tk.OptionMenu(frame, path_and_wall_button, "Path", "Wall", command=change_tile)
        options.grid(row=1, column=2, sticky= "SEW")
        if path_and_wall_button.get() == "Path":
            self.tile = (Tile.Path)
        elif path_and_wall_button.get() == "Wall":
            self.tile = (Tile.Wall)
        
        undo_button  = tk.Button(frame, text="Undo", command=self.undo)
        undo_button.grid(row=2, column=1)

        redo_button = tk.Button(frame, text="Redo", command=self.redo)
        redo_button.grid(row=2, column=2, sticky= "sew")

        

    def _setup_bottom_toolbar(self, frame: Frame) -> None:
        start_button: Button = Button(frame, text="Start", command=self._start_algorithm)

        pause_button = Button(frame, text="Pause", command=self._pause_algorithm)

        stop_button: Button = Button(frame, text="Stop", command=self._stop_algorithm)

        step_button: Button = Button(frame, text="Step", command=self._step_algorithm)

        reset_button = Button(frame, text="Reset Animation", command=self._reset_animation)

        for widget in [start_button, pause_button, stop_button, step_button, reset_button]:
            widget.pack(side=tk.LEFT, padx=5, pady=5)

    def _start_algorithm(self) -> None:
        print("Start button pressed")


    def _pause_algorithm(self) -> None:
        print("Pause button pressed")


    def _stop_algorithm(self) -> None:
        print("Stop button pressed")


    def _step_algorithm(self) -> None:
        print("Step button pressed")


    def _reset_animation(self) -> None:
        print("Reset animation")
        self.mode = Editing()

    def _setup_canvas(self) -> None:
        pass
