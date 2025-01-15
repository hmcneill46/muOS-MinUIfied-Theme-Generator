import tkinter as tk


class GridHelper:
    def __init__(self, root: tk.Frame):
        self.root = root
        self.row: int = 0
        self.column: int = 0

    def add(
        self,
        widget: tk.Widget,
        colspan: int = 1,
        rowspan: int = 1,
        next_row: bool = False,
        **kwargs,
    ):
        widget.grid(
            row=self.row,
            column=self.column,
            columnspan=colspan,
            rowspan=rowspan,
            **kwargs,
        )
        if next_row:
            self.row += 1
            self.column = 0
        else:
            self.column += colspan
