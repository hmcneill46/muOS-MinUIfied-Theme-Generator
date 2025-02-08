import tkinter as tk
from tkinter import ttk


class ProgressDialog(tk.Toplevel):
    def __init__(
        self, parent: tk.Tk, title: str = "Generating...", max: int | None = 100
    ):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x100")
        self.resizable(False, False)

        self.label = ttk.Label(self, text="")
        self.label.pack(padx=10, pady=10)

        self.progress_bar = ttk.Progressbar(
            self,
            orient="horizontal",
        )
        if max is not None:
            self.progress_bar.config(maximum=max, mode="determinate")
        else:
            self.progress_bar.config(mode="indeterminate")

        self.progress_bar.pack(padx=10, pady=20, fill=tk.X)

        self.transient(parent)
        self.grab_set()
