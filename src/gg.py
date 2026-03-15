from dataclasses import dataclass
from tkinter import Button, Canvas, Event, Frame, OptionMenu, StringVar, Tk, Widget
import tkinter as tk
from tkinter import filedialog
from turtle import width

from grid import Grid, Position, Tile
from solver import AStar, Solver


PATH_NODE_COLOR = "white"
WALL_NODE_COLOR = "black"
START_NODE_COLOR = "#6ae83c"
END_NODE_COLOR = "#f7ef07"


@dataclass
class View:
    pass


@dataclass
class Edit:
    pass


@dataclass
class Animate:
    visited: list[Position]
    path: list[Position] | None
    visited_index: int = 0
    path_index: int = 0


type Mode = View | Edit | Animate


class GridGuide:
    def __init__(
        self, root: Tk, width: int = 20, height: int = 20, cell_size: int = 25
    ) -> None:
        self.root: Tk = root
        self.cell_size: int = cell_size
        self.grid: Grid = Grid(width, height, Tile.Path)
        self.solver: Solver = AStar()
        self._mode: Mode = Edit()

        self.start_node: Position | None = None
        self.end_node: Position | None = None
        self.tile: Tile = Tile.Wall
        self.animation_id: str | None = None
        self.animation_speed: int = 50
        self.widgets: list[Button | OptionMenu] = []

        self.undo_stack = []
        self.redo_stack = []

        self.root.resizable(False, False)

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
        # TODO: Newtype to dict[tile_index, rect_id]
        self.rectangles: list[int] = [0] * ((self.grid.width * self.grid.height) + 1)
        self._setup_canvas()

        self.mode_changed()

        _ = self.canvas.bind("<Button-1>", self.handle_left_click)
        _ = self.canvas.bind("<B1-Motion>", self.handle_left_drag)
        _ = self.canvas.bind("<Button-3>", self.handle_right_click)
        # self.canvas.bind("<B1-Motion>", self.wall_drag)

    @property
    def mode(self) -> Mode:
        return self._mode

    @mode.setter
    def mode(self, mode: Mode):
        self._mode = mode
        self.mode_changed()

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

        self.import_button: Button = Button(
            frame, text="Import map", command=import_file
        )
        self.export_button: Button = Button(
            frame, text="Export map", command=export_file
        )

        for widget in [self.import_button, self.export_button]:
            widget.pack(side=tk.LEFT, padx=2, pady=2)
            self.widgets.append(widget)

    # def save_stat(self):
    #     state = (self.grid_tiles.copy(), self.start, self.end)
    #     self.undo_stack.append(state)
    #     self.redo_stack.clear()

    # def restore_state(self, state):
    #     tiles, start, end = state
    #     self.grid._tiles = tiles
    #     self.start = start
    #     self.end = end
    #     self.draw_grid()

    # def undo(self):
    #     if not self.undo_stack:
    #         return
    #     current = (self.grid._tiles.copy(), self.start, self.end)
    #     self.redo_stack.append(current)
    #     state = self.undo_stack.pop()
    #     self.restore_state(state)
    #
    # def redo(self):
    #     if not self.redo_stack:
    #         return
    #     current = (self.grid._tiles.copy(), self.start, self.end)
    #     self.undo_stack.append(current)
    #
    #     state = self.redo_stack.pop()
    #     self.restore_state(state)
    #

    def cursor_location(self, x: int, y: int):
        x_pos = x // self.cell_size
        y_pos = y // self.cell_size

        return Position(x_pos, y_pos)

    def paint_tile(self, event: Event):
        pos = self.cursor_location(event.x, event.y)

        if self.start_node == pos or self.end_node == pos:
            return

        index = self.grid.get_index(pos)

        if index is None:
            return

        self.grid.set_tile(index, self.tile)
        self.render_tile(index)

    def handle_left_click(self, event: Event):
        match self.mode:
            case Edit():
                self.paint_tile(event)
            case _:
                pass

    def handle_left_drag(self, event: Event):
        match self.mode:
            case Edit():
                self.paint_tile(event)
            case _:
                pass

    def handle_right_click(self, event: Event):
        match self.mode:
            case Edit():
                self.place_endpoints(event)
            case _:
                pass

    def place_endpoints(self, event: Event):
        pos = self.cursor_location(event.x, event.y)
        index = self.grid.get_index(pos)
        if index is None:
            return

        tile = self.grid.get_tile(index)
        if tile == Tile.Wall:
            return

        if self.start_node == pos:
            self.start_node = None
            self.clear_endpoint(pos)
            return

        if self.end_node == pos:
            self.end_node = None
            self.clear_endpoint(pos)
            return

        if self.start_node is None:
            self.start_node = pos
        elif self.end_node is None:
            self.end_node = pos
            _ = self.start_button.config(state="active")
        else:
            self.clear_endpoint(self.end_node)
            self.end_node = pos

        self.render_endpoints()

    def _setup_right_toolbar(self, frame: Frame) -> None:
        def set_mode(mode: Mode):
            self.mode = mode

        def change_tile(selection: StringVar):
            if selection == "Path":
                self.tile = Tile.Path
            elif selection == "Wall":
                self.tile = Tile.Wall

        def clear_all() -> None:
            self.grid.fill(Tile.Path)
            self.start_node = None
            self.end_node = None
            self.render_grid_state()

        self.clear_button: Button = tk.Button(frame, text="Clear", command=clear_all)
        self.edit_button: Button = Button(
            frame,
            text="Edit",
            command=lambda: set_mode(Edit()),
        )
        self.view_button: Button = Button(
            frame,
            text="View",
            command=lambda: set_mode(View()),
        )

        select_tile_var: StringVar = tk.StringVar()
        select_tile_var.set("Wall")

        self.select_tile_button: OptionMenu = OptionMenu(
            frame, select_tile_var, "Path", "Wall", command=change_tile
        )
        _ = self.select_tile_button.config(width=3)

        self.undo_button: Button = tk.Button(frame, text="Undo", command=lambda: ())
        self.redo_button: Button = tk.Button(frame, text="Redo", command=lambda: ())

        for i, widget in enumerate(
            [
                self.edit_button,
                self.view_button,
                self.clear_button,
                self.select_tile_button,
                self.undo_button,
                self.redo_button,
            ]
        ):
            if i % 2 == 0:
                widget.grid(row=i // 2, column=0, padx=2, pady=2)
            else:
                widget.grid(row=i // 2, column=1, padx=2, pady=2)
            self.widgets.append(widget)

    # fmt: off
    def _setup_bottom_toolbar(self, frame: Frame) -> None:
        self.start_button: Button = Button(frame, text="Start", command=self.start_animation)
        self.pause_button: Button = Button(frame, text="Pause", command=self.pause_animation)
        self.stop_button: Button = Button(frame, text="Stop", command=self.stop_animation)
        self.step_button: Button = Button(frame, text="Step", command=self.step_animation)
        self.reset_button: Button = Button(frame, text="Reset", command=self.reset_animation)

        for widget in [
            self.start_button,
            self.pause_button,
            self.stop_button,
            self.step_button,
            self.reset_button,
        ]:
            widget.pack(side=tk.LEFT, padx=2, pady=2)
            self.widgets.append(widget)


    def _setup_canvas(self) -> None:
        for r in range(self.grid.width):
            for c in range(self.grid.height):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2, outline="darkgray"
                )

                index = c + r * self.grid.width
                self.rectangles[index] = rect_id

        self.render_grid_state()

    def start_animation(self) -> None:
        self.render_grid_state()

        if self.start_node is not None and self.end_node is not None:
            result = self.solver.solve(self.grid, self.start_node, self.end_node)
            self.mode = Animate(result.visited, result.path)
            self.animate_nodes(self.mode)


    def pause_animation(self) -> None:
        raise NotImplementedError

    def stop_animation(self) -> None:
        raise NotImplementedError

    def step_animation(self) -> None:
        raise NotImplementedError

    def reset_animation(self) -> None:
        raise NotImplementedError

    def disable_buttons(self) -> None:
        for widget in self.widgets:
            _ =widget.config(state="disabled")

    def mode_changed(self) -> None:
        self.disable_buttons()

        match self.mode:
            case View():
                _ = self.edit_button.config(state="active")
                _ = self.import_button.config(state="active")
                _ = self.export_button.config(state="active")
            case Edit():
                _ = self.view_button.config(state="active")
                _ = self.clear_button.config(state="active")
                _ = self.select_tile_button.config(state="active")
                
                if self.start_node is not None and self.end_node is not None:
                    _ = self.start_button.config(state="active")

            case Animate():
                pass

    def clear_endpoint(self, position: Position) -> None:
        index = position.x + position.y * self.grid.width
        self.render_tile(index)

    def render_endpoints(self) -> None:
        match self.start_node:
            case Position(x, y):
                start_index = x + y * self.grid.width

                _ = self.canvas.itemconfig(self.rectangles[start_index], fill=START_NODE_COLOR)
            case _:
                pass

        match self.end_node:
            case Position(x, y):
                end_index = x + y * self.grid.width

                _ = self.canvas.itemconfig(self.rectangles[end_index], fill=END_NODE_COLOR)
            case _:
                pass



    def render_tile(
        self,
        index: int,
    ):
        if index in self.rectangles:
            match self.grid.get_tile(index):
                case Tile.Path:
                    color = PATH_NODE_COLOR
                case Tile.Wall:
                    color = WALL_NODE_COLOR
            _ = self.canvas.itemconfig(self.rectangles[index], fill=color)

    def render_grid_state(self):
        for r in range(self.grid.height):
            for c in range(self.grid.width):
                index = c + r * self.grid.width
                self.render_tile(index)

        self.render_endpoints()

    def animate_nodes(self, mode: Animate):
        if mode.visited_index < len(mode.visited):
            position = mode.visited[mode.visited_index]
            index = position.x + position.y * self.grid.width
            _ = self.canvas.itemconfig(self.rectangles[index], fill="#3498db")

            mode.visited_index += 1
            self.animation_id = self.root.after(
                self.animation_speed, self.animate_nodes, mode
            )
        elif mode.path is not None and mode.path_index < len(mode.path):
            position = mode.path[mode.path_index]
            index = position.x + position.y * self.grid.width
            _ = self.canvas.itemconfig(self.rectangles[index], fill="#f1c40f")

            mode.path_index += 1
            self.animation_id = self.root.after(
                self.animation_speed, self.animate_nodes, mode
            )
        else:
            self.mode = Edit()
