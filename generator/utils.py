import os
from pathlib import Path
import shutil
import sys

from PIL import ImageFont


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


def copy_contents(src: Path, dst: Path):
    if not dst.exists():
        os.makedirs(dst)

    for item in os.listdir(src):
        src_path = src / item
        dst_path = dst / item

        if src_path.is_dir():
            if not dst_path.exists():
                shutil.copytree(src_path, dst_path)
            else:
                copy_contents(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)


def ensure_folder_exists(folder_path: Path):
    if not folder_path.exists():
        try:
            os.makedirs(folder_path, exist_ok=True)
        except Exception as e:
            print(f"Error creating folder {folder_path}: {e}")


def delete_folder(folder_path: Path):
    if folder_path.exists():
        try:
            shutil.rmtree(folder_path)
        except Exception as e:
            print(f"Error deleting folder {folder_path}: {e}")
    else:
        raise FileNotFoundError(f"Folder {folder_path} does not exist")


def delete_file(file_path: Path):
    if file_path.exists():
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
    else:
        raise FileNotFoundError(f"File {file_path} does not exist")


def rename_file(src: Path, dst: Path):
    if src.exists():
        try:
            os.rename(src, dst)
        except Exception as e:
            print(f"Error renaming file {src} to {dst}: {e}")
    else:
        raise FileNotFoundError(f"File {src} does not exist")


def get_time_string_widths(time_font: ImageFont.FreeTypeFont) -> dict[str, int]:
    time_strings = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "AM", "PM"]
    time_string_widths = {}

    # Calculate the width of each character by repeating it
    for time_string in time_strings:
        time_string_bbox = time_font.getbbox(time_string * 100)
        time_string_width = time_string_bbox[2] - time_string_bbox[0]
        time_string_widths[time_string] = time_string_width

    return time_string_widths


def get_max_length_time_string(font: ImageFont.FreeTypeFont, time_format: str):
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
