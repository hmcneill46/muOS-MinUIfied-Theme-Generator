import platform
import tkinter as tk
from tkinter import font, ttk
from typing import Any, Callable

from .adapter import TkinterSettingsAdapter
from .settings import SettingsManager


class ThemeGeneratorApp:
    def __init__(
        self,
        root: tk.Tk,
        title: str,
        min_size: tuple[int, int],
        settings_manager: SettingsManager,
        settings_adapter: TkinterSettingsAdapter,
        commands_map: dict[str, Callable],
    ):
        self.root = root
        self.manager = settings_manager
        self.adapter = settings_adapter
        self.commands_map = commands_map
        self.on_change_settings = None

        self.tk_variables: dict[str, tk.Variable] = {}
        self._current_row = 0

        self.title_font = font.Font(family="Helvetica", size=20, weight="bold")
        self.subtitle_font = font.Font(family="Helvetica", size=14, weight="bold")

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

        self.root.protocol("WM_DELETE_WINDOW", self.on_app_close)

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

        self.scrollable_frame.grid_columnconfigure(0, weight=0)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

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

    def get_preview_width(self) -> int:
        return self.right_pane.winfo_width()

    def build_sections_from_settings(self) -> None:
        for section_data in self.manager.get_sections():
            if section_title := section_data.get("title", ""):
                heading_label = ttk.Label(
                    self.scrollable_frame,
                    text=section_title,
                    font=self.title_font,
                )
                heading_label.grid(
                    row=self._current_row,
                    column=0,
                    columnspan=2,
                    sticky=tk.W,
                    padx=(10, 5),
                    pady=(10, 5),
                )
                self._current_row += 1

            for field_info in section_data.get("fields", []):
                widget_type = field_info.get("widget_type", "label")
                var_name = field_info.get("var_name", "")
                default_value = field_info.get("default_value", None)
                var_type_str = field_info.get("var_type", "string")
                label_text = field_info.get("label", "")
                options = field_info.get("options", [])
                command_name = field_info.get("command", None)

                self._create_widget_for_field(
                    widget_type=widget_type,
                    var_name=var_name,
                    label_text=label_text,
                    var_type_str=var_type_str,
                    default_value=default_value,
                    options=options,
                    command_name=command_name,
                )

        if self.on_change_settings:
            self.on_change_settings()

    def _create_widget_for_field(
        self,
        widget_type: str,
        var_name: str,
        label_text: str,
        var_type_str: str,
        default_value: Any,
        options: list[str],
        command_name: str | None,
    ) -> None:
        if widget_type in ("label", "optionmenu", "entry") and label_text:
            lbl = ttk.Label(self.scrollable_frame, text=label_text)
            lbl.grid(
                row=self._current_row,
                column=0,
                sticky=tk.W,
                padx=(10, 5),
                pady=(2, 2),
            )

        tk_var = self.adapter.get_variable(var_name, var_type_str, default_value)

        if widget_type == "entry":
            entry = ttk.Entry(self.scrollable_frame, textvariable=tk_var)
            entry.grid(
                row=self._current_row,
                column=1,
                sticky=tk.EW,
                padx=(10, 10),
                pady=(2, 2),
            )

            self._current_row += 1
        elif widget_type == "optionmenu":
            om = ttk.OptionMenu(
                self.scrollable_frame,
                tk_var,
                tk_var.get(),
                *options,
            )
            om.grid(
                row=self._current_row,
                column=1,
                sticky=tk.EW,
                padx=(10, 10),
                pady=(2, 2),
            )

            self._current_row += 1
        elif widget_type == "checkbox":
            cb = ttk.Checkbutton(
                self.scrollable_frame,
                text=label_text,
                variable=tk_var,
            )
            cb.grid(
                row=self._current_row,
                column=0,
                columnspan=2,
                sticky=tk.W,
                padx=(10, 10),
                pady=(2, 2),
            )

            self._current_row += 1
        elif widget_type == "button":
            btn = ttk.Button(self.scrollable_frame, text=label_text)

            if command_name and command_name in self.commands_map:

                def callback():
                    self.commands_map[command_name](
                        self.manager, var_name, self.adapter.variables
                    )

                btn.configure(command=callback)

            btn.grid(
                row=self._current_row,
                column=1,
                columnspan=2,
                sticky=tk.E,
                padx=(10, 10),
                pady=(2, 2),
            )

            self._current_row += 1
        elif widget_type == "label":
            self._current_row += 1
        else:
            lbl = ttk.Label(
                self.scrollable_frame, text=f"Unknown widget type: {widget_type}"
            )
            lbl.grid(
                row=self._current_row,
                column=0,
                columnspan=2,
                sticky=tk.W,
                padx=(10, 10),
                pady=(2, 2),
            )

            self._current_row += 1

    def set_on_change_listener(self, callback: Callable[[], None]):
        self.on_change_settings = callback
        self.adapter.subscribe(self._on_var_change)

    def _on_var_change(self, var_name: str, value: Any):
        if self.on_change_settings:
            self.on_change_settings()

    def _on_resize(self, event: tk.Event) -> None:
        if self.resize_event_id is not None:
            self.root.after_cancel(self.resize_event_id)
        self.resize_event_id = self.root.after(100, self.on_resize_complete)

    def on_resize_complete(self) -> None:
        if self.on_change_settings:
            self.on_change_settings()

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

    def on_app_close(self):
        self.manager.save_user_values()
        self.root.destroy()

    def add_change_listener(self, on_change_settings: Callable):
        self.on_change_settings = on_change_settings

    def run(self) -> None:
        self.root.mainloop()
