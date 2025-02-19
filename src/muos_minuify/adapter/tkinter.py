from tkinter import BooleanVar, DoubleVar, IntVar, Tk, StringVar, Variable
from typing import Any, Callable

from ..settings import SettingsManager


def create_tk_variable(var_type_str: str, default_value=None) -> Variable:
    match var_type_str:
        case "string":
            return StringVar(value=default_value)
        case "int":
            return IntVar(value=default_value)
        case "float":
            return DoubleVar(value=default_value)
        case "boolean":
            return BooleanVar(value=bool(default_value))
        case _:
            return StringVar(
                value=str(default_value) if default_value is not None else ""
            )


class TkinterSettingsAdapter:
    def __init__(self, manager: SettingsManager, master: Tk, debounce_delay: int = 300):
        self.manager = manager
        self.master = master
        self.debounce_delay = debounce_delay

        self.variables: dict[str, Variable] = {}
        self._subscribers: list[Callable[[str, Any], None]] = []

        self._debounce_after_id = None
        self._last_change: tuple[str, Any] | None = None

    def get_variable(
        self, var_name: str, var_type: str, default_value: Any | None = None
    ) -> Variable:
        if var_name not in self.variables:
            current_value = self.manager.get_value(var_name, fallback=default_value)
            tk_var = create_tk_variable(var_type, current_value)

            def on_write(*_):
                try:
                    new_val = tk_var.get()
                except Exception:
                    return

                self.manager.set_value(var_name, new_val)
                self._debounce_notify(var_name, new_val)

            tk_var.trace_add("write", on_write)
            self.variables[var_name] = tk_var

        return self.variables[var_name]

    def subscribe(self, callback: Callable[[str, Any], None]):
        self._subscribers.append(callback)

    def _notify_subscribers(self, var_name: str, new_val: Any):
        for cb in self._subscribers:
            cb(var_name, new_val)

    def _debounce_notify(self, var_name: str, new_val: Any) -> None:
        self._last_change = (var_name, new_val)

        if self._debounce_after_id is not None:
            self.master.after_cancel(self._debounce_after_id)

        self._debounce_after_id = self.master.after(
            self.debounce_delay, self._process_debounce
        )

    def _process_debounce(self):
        if self._last_change is not None:
            var_name, new_val = self._last_change
            self._notify_subscribers(var_name, new_val)

        self._debounce_after_id = None
        self._last_change = None
