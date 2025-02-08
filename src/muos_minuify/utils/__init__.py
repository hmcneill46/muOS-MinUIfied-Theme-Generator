import json
import logging
import math
import os
from pathlib import Path
import shutil
import sys
from typing import Any, Literal

from PIL import Image, ImageFont
from PIL.Image import Resampling

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)


class FileOperationError(Exception):
    pass


class FolderOperationError(Exception):
    pass


def find_base_dirs() -> tuple[Path, Path]:
    frozen: bool = getattr(sys, "frozen", False)
    mei_pass: str = getattr(sys, "_MEIPASS", "")
    executable: str = getattr(sys, "executable", "")

    if frozen and mei_pass:
        # The application is running as a bundle
        BASE_DIR = Path(executable).parent
        RESOURCES_DIR = Path(mei_pass)  # type: ignore[attr-defined]
    else:
        # the application is running in a normal Python environment
        BASE_DIR = Path()
        RESOURCES_DIR = BASE_DIR

    return BASE_DIR, RESOURCES_DIR


def copy_contents(src: str | Path, dst: str | Path, overwrite: bool = False) -> None:
    src = Path(src).resolve()
    dst = Path(dst).resolve()

    if not src.is_dir():
        raise NotADirectoryError(f"Source path {src} is not a directory")

    dst.mkdir(parents=True, exist_ok=True)

    for item in src.iterdir():
        dst_path = dst / item.name

        if item.is_dir():
            copy_contents(item, dst_path, overwrite=overwrite)
        else:
            if not dst_path.exists() or overwrite:
                try:
                    shutil.copy2(item, dst_path)
                except Exception as e:
                    LOGGER.error(f"Error copying {item} to {dst_path}: {e}")
                    raise FileOperationError from e


def ensure_file_exists(file_path: str | Path, default_data: dict | None = None):
    file_path = Path(file_path).resolve()

    if not file_path.exists():
        try:
            if default_data is not None:
                file_data = json.dumps(default_data, indent=4)
                file_path.write_text(file_data, encoding="utf-8")
            else:
                file_path.touch()
        except Exception as e:
            LOGGER.error(f"Error creating file {file_path}: {e}")
            raise FileOperationError from e


def ensure_folder_exists(folder_path: str | Path):
    folder_path = Path(folder_path).resolve()

    if not folder_path.exists():
        try:
            os.makedirs(folder_path, exist_ok=True)
        except Exception as e:
            LOGGER.error(f"Error creating folder {folder_path}: {e}")
            raise FolderOperationError from e


def delete_folder(folder_path: str | Path):
    folder_path = Path(folder_path).resolve()

    if folder_path.exists():
        try:
            shutil.rmtree(folder_path)
        except Exception as e:
            LOGGER.error(f"Error deleting folder {folder_path}: {e}")
            raise FolderOperationError from e
    else:
        LOGGER.warning(f"Folder {folder_path} does not exist")
        raise FileNotFoundError(f"Folder {folder_path} does not exist")


def delete_file(file_path: str | Path):
    file_path = Path(file_path).resolve()

    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            LOGGER.error(f"Error deleting file {file_path}: {e}")
    else:
        LOGGER.warning(f"File {file_path} does not exist")
        raise FileNotFoundError(f"File {file_path} does not exist")


def rename_file(src: str | Path, dst: str | Path):
    src = Path(src).resolve()
    dst = Path(dst).resolve()

    if src.exists():
        try:
            src.rename(dst)
        except Exception as e:
            LOGGER.info(f"Error renaming file {src} to {dst}: {e}")
            raise FileOperationError from e
    else:
        LOGGER.warning(f"File {src} does not exist")
        raise FileNotFoundError(f"File {src} does not exist")


def read_file(file_path: str | Path) -> str:
    file_path = Path(file_path).resolve()

    if file_path.exists():
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception as e:
            LOGGER.error(f"Error reading file {file_path}: {e}")
            raise FileOperationError from e
    else:
        LOGGER.warning(f"File {file_path} does not exist")
        raise FileNotFoundError(f"File {file_path} does not exist")


def read_json(file_path: str | Path) -> dict[str, Any]:
    file_text = read_file(file_path)

    try:
        return json.loads(file_text)
    except Exception as e:
        LOGGER.error(f"Error parsing JSON from file {file_path}: {e}")
        raise FileOperationError from e


def write_file(file_path: str | Path, content: str):
    file_path = Path(file_path).resolve()

    try:
        file_path.write_text(content, encoding="utf-8")
    except Exception as e:
        LOGGER.error(f"Error writing to file {file_path}: {e}")
        raise FileOperationError from e


def write_json(file_path: str | Path, content: dict[str, Any]):
    content_json = json.dumps(content, indent=4)
    write_file(file_path, content_json)


def get_time_string_widths(time_font: ImageFont.FreeTypeFont) -> dict[str, int]:
    time_strings = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "AM", "PM"]
    time_string_widths = {}

    # Calculate the width of each character by repeating it
    for time_string in time_strings:
        time_string_bbox = time_font.getbbox(time_string * 100)
        time_string_width = time_string_bbox[2] - time_string_bbox[0]
        time_string_widths[time_string] = time_string_width

    return time_string_widths


def get_max_length_time_string(
    font: ImageFont.FreeTypeFont,
    time_format: Literal["12 Hour", "24 Hour"],
) -> str:
    time_string_sizes = get_time_string_widths(font)

    last_digit = max(
        (s for s in time_string_sizes if any(char.isdigit() for char in s)),
        key=lambda s: time_string_sizes[s],
    )
    second_last_digit = max(
        (s for s in time_string_sizes if s.isdigit() and int(s) < 6),
        key=lambda s: time_string_sizes[s],
    )

    firstDigits = None
    widthResult = 0
    hour_values = range(1, 13) if time_format == "12 Hour" else range(0, 24)

    for hour in hour_values:
        hour_string = str(hour).zfill(2)
        digit1, digit2 = hour_string[:]
        width1, width2 = (time_string_sizes[digit1], time_string_sizes[digit2])
        hour_width = width1 + width2

        if hour_width > widthResult:
            widthResult = hour_width
            firstDigits = hour_string

    if time_format == "12 Hour":
        am_or_pm = max(
            (s for s in time_string_sizes if not any(char.isdigit() for char in s)),
            key=lambda s: time_string_sizes[s],
        )
        timeText = f"{firstDigits}:{second_last_digit}{last_digit} {am_or_pm}"
    else:
        timeText = f"{firstDigits}:{second_last_digit}{last_digit}"

    return timeText


def resize_system_logos(
    system_logos_path: Path,
    output_system_logos_path: Path,
    grid_cell_size: int,
    grid_image_padding: int,
    circular_grid: bool,
) -> None:
    system_logos = system_logos_path.glob("*.png")
    if circular_grid:
        effective_circle_diameter = grid_cell_size - (grid_image_padding * 2)
    else:
        effective_grid_size = grid_cell_size - (grid_image_padding * 2)
    for system_logo_path in system_logos:
        system_logo_image = Image.open(system_logo_path).convert("RGBA")
        if circular_grid:
            old_size = system_logo_image.size
            aspect_ratio = old_size[0] / old_size[1]
            new_height = math.sqrt(
                math.pow(effective_circle_diameter, 2) / (1 + math.pow(aspect_ratio, 2))
            )
            new_size = int(new_height * aspect_ratio), int(new_height)
        else:
            width_multiplier = effective_grid_size / system_logo_image.size[0]
            height_multiplier = effective_grid_size / system_logo_image.size[1]
            multiplier = min(width_multiplier, height_multiplier)
            new_size = (
                int(system_logo_image.size[0] * multiplier),
                int(system_logo_image.size[1] * multiplier),
            )
        system_logo_image = system_logo_image.resize(new_size, Resampling.LANCZOS)
        system_logo_image.save(output_system_logos_path / system_logo_path.name)
