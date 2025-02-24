import tkinter as tk
from tkinter import ttk


class ProgressDialog(tk.Toplevel):
    def __init__(
        self, parent: tk.Tk, title: str = "Generating...", max: int | None = 100
    ):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x100")
        self.resizable(False, False)

        self.section_label = ttk.Label(self, text="")
        self.section_label.pack(padx=10, pady=(10, 0))
        self.item_label = ttk.Label(self, text="")
        self.item_label.pack(padx=10, pady=(0, 10))

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

    def update_status(
        self,
        section: str | None = None,
        item: str | None = None,
        step: int = 1,
    ) -> None:
        if section is not None:
            self.section_label.config(text=section)

        if item is not None:
            self.item_label.config(text=item)

        self.progress_bar.step(step)
