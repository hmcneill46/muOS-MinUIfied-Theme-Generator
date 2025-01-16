from pathlib import Path
import platform
import tkinter as tk
from tkinter import ttk
from typing import Callable

from .config import Config
from .constants import VARIABLE_DEFINITIONS


def create_gui_variables() -> dict[str, tk.Variable]:
    variables = {}
    for definition in VARIABLE_DEFINITIONS:
        var_name = definition["name"]
        var_type = definition["type"]
        default_value = definition.get("default", None)
        variables[var_name] = var_type(value=default_value)

    return variables


def load_from_config(variables: dict[str, tk.Variable], config: Config):
    for definition in VARIABLE_DEFINITIONS:
        var_name = definition["name"]
        config_attr = definition["config_attr"]

        if hasattr(config, config_attr):
            config_value = getattr(config, config_attr)

            if isinstance(config_value, Path):
                config_value = str(config_value)

            variables[var_name].set(config_value)


def save_to_config(variables: dict[str, tk.Variable], config: Config):
    for definition in VARIABLE_DEFINITIONS:
        var_name = definition["name"]
        config_attr = definition["config_attr"]

        if hasattr(config, config_attr):
            current_value = variables[var_name].get()
            setattr(config, config_attr, current_value)

    config.save_config()


def bind_traces(
    variables: dict[str, tk.Variable], config: Config, on_change: Callable[[], None]
):
    def trace_callback(*args):
        save_to_config(variables, config)
        on_change()

    for definition in VARIABLE_DEFINITIONS:
        if definition.get("trace_save", False):
            var_name = definition["name"]
            variable = variables[var_name]
            variable.trace_add("write", trace_callback)


class ThemeGeneratorApp:
    def __init__(self, title: str, min_size: tuple[int, int]):
        self.root = tk.Tk()

        screen_height = self.root.winfo_screenheight()
        window_height = int(min(screen_height * 0.9, 1720))

        self.root.title(title)
        self.root.minsize(*min_size)
        self.root.geometry(f"1280x{window_height}")

        self.resize_event_id: str | None = None

        self.paned_window: ttk.PanedWindow | None = None
        self.left_pane: ttk.Frame | None = None
        self.right_pane: ttk.Frame | None = None
        self.canvas: tk.Canvas | None = None
        self.scrollbar: ttk.Scrollbar | None = None
        self.scrollable_frame: ttk.Frame | None = None

        self.image_label1: ttk.Label | None = None
        self.image_label2: ttk.Label | None = None
        self.image_label3: ttk.Label | None = None
        self.image_label4: ttk.Label | None = None
        self.image_label5: ttk.Label | None = None

        self._build_paned_window()
        self._build_left_pane()
        self._build_right_pane()

        if not self.paned_window:
            raise Exception("Failed to create paned window")

        self.paned_window.add(self.left_pane, weight=2)
        self.paned_window.add(self.right_pane, weight=1)

        self._bind_events()

    def _build_paned_window(self) -> None:
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

    def _build_left_pane(self) -> None:
        self.left_pane = ttk.Frame(self.paned_window)

        self.canvas = tk.Canvas(self.left_pane)
        self.scrollbar = ttk.Scrollbar(
            self.left_pane, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.scrollable_frame = ttk.Frame(self.canvas)

        if not all((self.canvas, self.scrollbar, self.scrollable_frame)):
            raise Exception("Failed to create left pane")

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox(tk.ALL),
            ),
        )

    def _build_right_pane(self):
        self.right_pane = ttk.Frame(self.paned_window, width=240)

        self.image_label1 = ttk.Label(self.right_pane, text="Preview #1")
        self.image_label2 = ttk.Label(self.right_pane, text="Preview #2")
        self.image_label3 = ttk.Label(self.right_pane, text="Preview #3")
        self.image_label4 = ttk.Label(self.right_pane, text="Preview #4")
        self.image_label5 = ttk.Label(self.right_pane, text="Preview #5")

        self.image_label1.pack()
        self.image_label2.pack()
        self.image_label3.pack()
        self.image_label4.pack()
        self.image_label5.pack()

    def _bind_events(self) -> None:
        self.root.bind("<Configure>", self._on_resize)
        self.paned_window.bind("<Configure>", self._on_resize)

        if platform.system() == "Darwin":
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_mac)
            self.canvas.bind_all("<Shift-MouseWheel>", self._on_shiftmousewheel_mac)
        else:
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_win_linux)
            self.canvas.bind_all("<Shift-MouseWheel>", self._on_mousewheel_win_linux)
            self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _on_resize(self, event: tk.Event) -> None:
        if self.resize_event_id is not None:
            self.root.after_cancel(self.resize_event_id)
        self.resize_event_id = self.root.after(100, self.on_resize_complete)

    def on_resize_complete(self) -> None:
        pass

    def _on_mousewheel_win_linux(self, event: tk.Event) -> None:
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def _on_shiftmousewheel_win_linux(self, event: tk.Event) -> None:
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def _on_mousewheel_mac(self, event: tk.Event) -> None:
        self.canvas.yview_scroll(-1 * int(event.delta), "units")

    def _on_shiftmousewheel_mac(self, event: tk.Event) -> None:
        self.canvas.yview_scroll(-1 * int(event.delta), "units")

    def _on_mousewheel_linux(self, event: tk.Event) -> None:
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    app = ThemeGeneratorApp("muOS Theme Generator", (1280, 720))
    app.run()
