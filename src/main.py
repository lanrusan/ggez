import tkinter as tk

from gg import GridGuide


def main():
    root = tk.Tk()
    root.title("Grid Guide")
    app = GridGuide(root)
    app.root.mainloop()


if __name__ == "__main__":
    main()
