import json
from pathlib import Path
import re
from typing import Any

from generator.constants import MENU_LISTING_MAP


def ensure_file_exists(path: Path, default_data: dict | None = None):
    if not path.exists():
        default_data = default_data or {}
        path.write_text(
            json.dumps(
                default_data,
                indent=4,
            ),
            encoding="utf-8",
        )


def load_json(path: Path):
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error loading JSON file {path}: {e}")
        return {}


class SettingsManager:
    PATH_KEYS = (
        "theme_directory_path",
        "background_image_path",
        "bootlogo_image_path",
        "alt_font_filename",
    )

    def __init__(self, base_path: Path, user_path: Path):
        self.base_path = base_path
        self.user_path = user_path

        self.deviceScreenHeightVar = 480
        self.deviceScreenWidthVar = 640

        self.sections = []
        self.user_values: dict[str, Any] = {}
        self.merged_values: dict[str, Any] = {}

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

                final_val = self._cast_from_json(
                    user_val if user_val is not None else default_val, var_type
                )
                merged[var_name] = final_val

                if var_name == "device_type_var":
                    self._parse_screen_dimensions(final_val)

        self.merged_values = merged

    def load(self):
        ensure_file_exists(self.base_path, {"sections": []})
        ensure_file_exists(self.user_path, {})

        base_data = load_json(self.base_path)
        user_data = load_json(self.user_path)

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

                casted_user_data[var_name] = self._cast_to_json(value, var_type)

        self.user_path.write_text(
            json.dumps(casted_user_data, indent=4),
            encoding="utf-8",
        )

    def set_value(self, var_name: str, new_value):
        self.user_values[var_name] = new_value
        self.merged_values[var_name] = new_value

        if var_name == "device_type_var":
            self._parse_screen_dimensions(new_value)

    def get_value(self, var_name: str, fallback: Any = None):
        return self.merged_values.get(var_name, fallback)

    def get_menu_listing(
        self, var_name: str
    ) -> tuple[tuple[str, tuple[tuple[str, str], ...]], ...] | None:
        if version := self.get_value(var_name):
            version_number = version[5:9]
            return MENU_LISTING_MAP.get(version_number)

    def _parse_screen_dimensions(self, device_type: str):
        match = re.search(r"\[(\d+)x(\d+)\]", device_type)
        if match:
            self.deviceScreenWidthVar = int(match.group(1))
            self.deviceScreenHeightVar = int(match.group(2))
        else:
            raise ValueError(
                "Invalid device type format, cannot find screen dimensions"
            )

    def get_sections(self):
        return self.sections

    def __getattr__(self, name):
        return self.get_value(name, None)

    def _cast_from_json(self, value: Any, var_type: str) -> Any:
        if value is None:
            return None

        if var_type == "int":
            return int(value)
        elif var_type == "float":
            return float(value)
        elif var_type == "boolean":
            return bool(value)
        elif var_type == "path":
            return Path(value)
        else:
            return str(value)

    def _cast_to_json(self, value: Any, var_type: str) -> Any:
        if value is None:
            return None

        if var_type == "int":
            return int(value)
        elif var_type == "float":
            return float(value)
        elif var_type == "boolean":
            return bool(value)
        elif var_type == "path":
            return str(Path(value).resolve())
        else:
            return str(value)
