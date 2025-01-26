from tkinter import BooleanVar, DoubleVar, IntVar, StringVar, Variable
from typing import Any, Callable

from generator.settings import SettingsManager


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
    def __init__(self, manager: SettingsManager):
        self.manager = manager
        self.variables: dict[str, Variable] = {}
        self._subscribers: list[Callable[[str, Any], None]] = []

    def get_variable(
        self, var_name: str, var_type: str, default_value: Any | None = None
    ) -> Variable:
        if var_name not in self.variables:
            current_value = self.manager.get_value(var_name, fallback=default_value)
            tk_var = create_tk_variable(var_type, current_value)

            def on_write(*_):
                new_val = tk_var.get()
                self.manager.set_value(var_name, new_val)
                self._notify_subscribers(var_name, new_val)

            tk_var.trace_add("write", on_write)
            self.variables[var_name] = tk_var

        return self.variables[var_name]

    def subscribe(self, callback: Callable[[str, Any], None]):
        self._subscribers.append(callback)

    def _notify_subscribers(self, var_name: str, new_val: Any):
        for cb in self._subscribers:
            cb(var_name, new_val)
