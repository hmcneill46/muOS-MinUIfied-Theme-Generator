import tkinter as tk
from tkinter import ttk
from tkinter import font
from typing import Callable


class FieldDef:
    def __init__(
        self,
        label: str,
        widget_type: str,
        variable: tk.Variable | None = None,
        options: list[str] | None = None,
        command: Callable[[], None] | None = None,
        width: int = 50,
        sticky: str = "w",
        font_style: font.Font | None = None,
        tooltip: str = "",
    ) -> None:
        self.label = label
        self.widget_type = widget_type.lower()
        self.variable = variable
        self.options = options or []
        self.command = command
        self.width = width
        self.sticky = sticky
        self.font_style = font_style
        self.tooltip = tooltip


class SectionDef:
    def __init__(
        self,
        title: str,
        fields: list[FieldDef] | None = None,
        font_style: font.Font | None = None,
    ) -> None:
        self.title = title
        self.fields = fields or []
        self.font_style = font_style


class GUIBuilder:
    def __init__(
        self,
        parent: tk.Widget,
        default_font: font.Font | None = None,
        label_style: str = "TLabel",
        spacing: int = 1,
    ) -> None:
        self.parent = parent
        self.current_row = 0
        self.default_font = default_font
        self.label_style = label_style
        self.spacing = spacing

    def build_sections(self, sections: list[SectionDef]) -> None:
        for section in sections:
            self._create_section_heading(section)

            for field in section.fields:
                self._create_field(field)

            for _ in range(self.spacing):
                self.current_row += 1

    def _create_section_heading(self, section: SectionDef) -> None:
        if section.title:
            heading = ttk.Label(
                self.parent,
                text=section.title,
                style=self.label_style,
            )

            if section.font_style:
                heading.configure(font=section.font_style)
            elif self.default_font:
                heading.configure(font=self.default_font)

            heading.grid(
                row=self.current_row,
                column=0,
                columnspan=3,
                sticky=tk.W,
                pad=(5, 5),
            )
            self.current_row += 1

    def _create_field(self, field: FieldDef) -> None:
        if field.widget_type == "heading":
            lbl = ttk.Label(
                self.parent,
                text=field.label,
                style=self.label_style,
            )

            if field.font_style:
                lbl.configure(font=field.font_style)

            lbl.grid(
                row=self.current_row,
                column=0,
                columnspan=3,
                sticky=tk.W,
                padx=(5, 5),
            )

        if field.widget_type != "label":
            lbl = ttk.Label(self.parent, text=field.label + ": ")
            lbl.grid(
                row=self.current_row,
                column=0,
                sticky=tk.W,
                padx=(0, 5),
            )

        if field.widget_type == "entry":
            entry = ttk.Entry(self.parent, width=field.width)

            if field.variable is not None:
                entry.configure(textvariable=field.variable)

            entry.grid(row=self.current_row, column=1, columnspan=1, sticky=tk.W)

            if field.tooltip:
                self._add_tooltip(entry, field.tooltip)
        elif field.widget_type == "optionmenu":
            if field.variable is None:
                field.variable = tk.StringVar(
                    value=field.options[0] if field.options else ""
                )

            om = ttk.OptionMenu(self.parent, field.variable, *field.options)
            om.config(width=field.width)
            om.grid(row=self.current_row, column=1, columnspan=2, sticky=tk.W)

            if field.tooltip:
                self._add_tooltip(om, field.tooltip)
        elif field.widget_type == "checkbutton":
            cb = ttk.Checkbutton(self.parent, text=field.label)

            if field.variable is not None:
                cb.config(variable=field.variable)

            cb.grid(
                row=self.current_row, column=0, columnspan=3, sticky=tk.W, pady=(2, 2)
            )

            if field.tooltip:
                self._add_tooltip(cb, field.tooltip)

            self.current_row += 1
            return
        elif field.widget_type == "button":
            btn = ttk.Button(self.parent, text=field.label)

            if field.command is not None:
                btn.configure(command=field.command)

            btn.grid(row=self.current_row, column=1, sticky=tk.W)

            if field.tooltip:
                self._add_tooltip(btn, field.tooltip)
        elif field.widget_type == "label":
            lbl = ttk.Label(self.parent, text=field.label)
            lbl.grid(row=self.current_row, column=0, columnspan=3, sticky=tk.W)
        else:
            err_lbl = ttk.Label(
                self.parent, text=f"Unknown widget type: {field.widget_type}"
            )
            err_lbl.grid(row=self.current_row, column=0, columnspan=3, sticky=tk.W)

        self.current_row += 1

    def _add_tooltip(self, widget: tk.Widget, text: str) -> None:
        tooltip_window = None

        def show_tooltip(event: tk.Event) -> None:
            nonlocal tooltip_window
            tooltip_window = tk.Toplevel(widget)
            tooltip_window.wm_overrideredirect(True)
            tooltip_window.wm_geometry(f"+{event.x_root + 20}+{event.y_root + 20}")

            label = ttk.Label(tooltip_window, text=text, relief=tk.SOLID, borderwidth=1)
            label.pack()

        def hide_tooltip(event: tk.Event) -> None:
            nonlocal tooltip_window
            if tooltip_window:
                tooltip_window.destroy()
                tooltip_window = None

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
