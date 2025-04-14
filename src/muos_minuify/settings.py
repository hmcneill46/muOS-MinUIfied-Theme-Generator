from pathlib import Path
import re
from typing import Any

from .constants import (
    BASE_SETTINGS_PATH,
    USER_SETTINGS_PATH,
    LEGACY_SETTINGS_PATH,
)
from .utils import ensure_file_exists, read_json, write_json


class SettingsManager:
    def __init__(
        self,
        base_path: Path = BASE_SETTINGS_PATH,
        user_path: Path = USER_SETTINGS_PATH,
    ):
        self.base_path = base_path
        self.user_path = user_path

        self.sections = []
        self.default_values: dict[str, tuple[Any, str]] = self._load_defaults(base_path)
        self.user_values: dict[str, Any] = {}
        self.merged_values: dict[str, Any] = {}

    def _load_defaults(
        self,
        defaults_path: Path = BASE_SETTINGS_PATH,
    ) -> dict[str, tuple[Any, str]]:
        ensure_file_exists(defaults_path, {"sections": []})
        base_data = read_json(defaults_path)
        defaults = {}

        for section in base_data.get("sections", []):
            for field in section.get("fields", []):
                if (
                    (var_name := field.get("var_name"))
                    and (var_type := field.get("var_type", "string"))
                    and not field.get("command")
                ):
                    if "hex" in var_name.lower():
                        pass
                    defaults[var_name] = (
                        SettingsManager._cast_from_json(
                            field.get("default_value", None), var_type
                        ),
                        var_type,
                    )

        return defaults

    def _merge_values(self):
        merged = {}

        for section in self.sections:
            for field in section.get("fields", []):
                if (
                    not (var_name := field.get("var_name"))
                    or field.get("widget_type") == "button"
                ):
                    continue

                default_val = field.get("default_value", None)
                var_type = field.get("var_type", "string")
                user_val = self.user_values.get(var_name, None)

                final_val = SettingsManager._cast_from_json(
                    user_val if user_val is not None else default_val, var_type
                )
                merged[var_name] = final_val

                if var_name == "device_type_var":
                    width, height = self._parse_screen_dimensions(final_val)
                    merged["deviceScreenWidthVar"] = width
                    merged["deviceScreenHeightVar"] = height

        self.merged_values = merged

    def _get_var_type(self, var_name: str) -> str:
        for section in self.sections:
            for field in section.get("fields", []):
                if field.get("var_name") == var_name:
                    return field.get("var_type", "string")

        return "string"

    def load(self, override_values: dict[str, Any] | None = None):
        ensure_file_exists(self.base_path, {"sections": []})
        base_data = read_json(self.base_path)
        user_data = {}

        if not self.user_path.exists() and not LEGACY_SETTINGS_PATH.exists():
            ensure_file_exists(self.user_path, {})
        elif self.user_path.exists():
            user_data = read_json(self.user_path)
        else:
            legacy_data = read_json(LEGACY_SETTINGS_PATH)
            for key, value in legacy_data.items():
                if "hex" in key.lower():
                    pass
                if key in self.default_values and value != self.default_values[key][0]:
                    user_data[key] = SettingsManager._cast_from_json(
                        *self.default_values[key]
                    )

        if override_values:
            user_data.update(override_values)

        self.sections = base_data.get("sections", [])
        self.user_values = user_data

        self._merge_values()

    def save_user_values(self):
        casted_user_data = {}
        for section in self.sections:
            for field in section.get("fields", []):
                if (
                    not (var_name := field.get("var_name"))
                    or var_name not in self.user_values
                ):
                    continue

                var_type = field.get("var_type", "string")
                value = self.user_values[var_name]

                casted_user_data[var_name] = SettingsManager._cast_to_json(
                    value, var_type
                )

        write_json(self.user_path, casted_user_data)

    def set_value(self, var_name: str, new_value: Any) -> None:
        default_value = self.default_values.get(var_name, None)
        old_value = self.merged_values.get(var_name, None)
        var_type = self._get_var_type(var_name)

        new_value = SettingsManager._parse_value(
            new_value, old_value, default_value, var_type
        )

        self.user_values[var_name] = new_value
        self.merged_values[var_name] = new_value

        if var_name in "device_type_var":
            width, height = self._parse_screen_dimensions(new_value)
            self.user_values["deviceScreenWidthVar"] = width
            self.merged_values["deviceScreenWidthVar"] = width
            self.user_values["deviceScreenHeightVar"] = height
            self.merged_values["deviceScreenHeightVar"] = height

    def set_values(self, values: dict[str, Any]) -> None:
        for var_name, new_value in values.items():
            self.set_value(var_name, new_value)

    def get_value(self, var_name: str, fallback: Any = None):
        return self.merged_values.get(var_name, fallback)

    def _parse_screen_dimensions(self, device_type: str) -> tuple[int, int]:
        match = re.search(r"\[(\d+)x(\d+)\]", device_type)
        if match:
            return int(match.group(1)), int(match.group(2))
        else:
            raise ValueError(
                "Invalid device type format, cannot find screen dimensions"
            )

    @staticmethod
    def _parse_value(
        new_value: Any,
        old_value: Any | None = None,
        default_value: Any | None = None,
        var_type: str = "string",
    ) -> Any:
        parsed_value = new_value

        if var_type == "color":
            parsed_value = SettingsManager._parse_color_hex(
                new_value, old_value, default_value
            )
        if var_type == "int":
            parsed_value = SettingsManager._parse_integer(
                new_value, old_value, default_value
            )
        if var_type == "path":
            parsed_value = SettingsManager._parse_path(
                new_value, old_value, default_value
            )

        return parsed_value

    @staticmethod
    def _parse_color_hex(
        color_hex: str,
        old_color_hex: str | None = None,
        default_color_hex: str | None = "#000000",
    ) -> str:
        hex_pattern = r"^#?([0-9a-f]{6}){1}$"

        if color_match := re.fullmatch(hex_pattern, color_hex, re.IGNORECASE):
            return f"#{color_match.group(1)}".lower()
        elif old_color_hex and (
            old_color_match := re.fullmatch(hex_pattern, old_color_hex, re.IGNORECASE)
        ):
            return f"#{old_color_match.group(1)}".lower()
        elif default_color_match := re.fullmatch(
            hex_pattern, str(default_color_hex), re.IGNORECASE
        ):
            return f"#{default_color_match.group(1)}".lower()

        return "#000000"

    @staticmethod
    def _parse_integer(
        value: str | int,
        old_value: str | int | None = None,
        default_value: str | int | None = 0,
    ) -> int:
        if value and str(value).isdigit():
            return int(value)
        elif old_value and str(old_value).isdigit():
            return int(old_value)
        elif str(default_value).isdigit():
            return int(default_value) if default_value is not None else 0

        return 0

    @staticmethod
    def _parse_path(
        value: str | Path,
        old_value: str | Path | None = None,
        default_value: str | Path | None = None,
    ) -> Path | None:
        if isinstance(value, str):
            if value and (path := Path(value)):
                return path.resolve()
            else:
                return None
        elif isinstance(old_value, Path) and old_value and (path := Path(old_value)):
            return path.resolve()
        elif (
            isinstance(default_value, Path)
            and default_value
            and (path := Path(default_value))
        ):
            return path.resolve()

        return None

    def get_sections(self):
        return self.sections

    def __getattr__(self, name: str) -> Any:
        return self.get_value(name)

    @staticmethod
    def _cast_from_json(value: Any, var_type: str) -> Any:
        if value is None:
            return None

        if var_type == "int":
            return SettingsManager._parse_integer(value)
        elif var_type == "float":
            return float(value)
        elif var_type == "boolean":
            return bool(value)
        elif var_type == "path":
            return (
                parsed_path
                if (parsed_path := SettingsManager._parse_path(value))
                else None
            )
        elif var_type == "color":
            return SettingsManager._parse_color_hex(f"#{value.strip('#')}")
        else:
            return str(value)

    @staticmethod
    def _cast_to_json(value: Any, var_type: str) -> Any:
        if value is None:
            return None

        if var_type == "int":
            return SettingsManager._parse_integer(value)
        elif var_type == "float":
            return float(value)
        elif var_type == "boolean":
            return bool(value)
        elif var_type == "path":
            return (
                str(parsed_path)
                if (parsed_path := SettingsManager._parse_path(value))
                else ""
            )
        elif var_type == "color":
            return SettingsManager._parse_color_hex(f"#{value.strip('#')}")
        else:
            return str(value)
