from pathlib import Path

from generator.defaults import DEFAULT_FONT_PATH


def get_font_path(use_alt_font: bool, alt_font_path: Path) -> Path:
    return (
        alt_font_path if use_alt_font and alt_font_path.exists() else DEFAULT_FONT_PATH
    )
