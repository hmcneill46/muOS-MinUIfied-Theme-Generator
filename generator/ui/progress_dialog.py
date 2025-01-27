import tkinter as tk
from tkinter import ttk


class ProgressDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, title: str = "Generating...", max: int = 100):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x100")
        self.resizable(False, False)

        self.label = ttk.Label(self, text="")
        self.label.pack(padx=10, pady=10)

        self.progress_bar = ttk.Progressbar(
            self,
            maximum=max,
            orient="horizontal",
            mode="determinate",
        )
        self.progress_bar.pack(padx=10, pady=20, fill=tk.X)

        self.transient(parent)
        self.grab_set()
