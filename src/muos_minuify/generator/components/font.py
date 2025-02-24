from pathlib import Path

from ...constants import FONTS_DIR
from ...defaults import DEFAULT_FONT_PATH


class HasFont:
    BINARIES_DIR = FONTS_DIR / "Binaries"
    FONT_FILENAME = "BPreplayBold-unhinted-{font_size}.bin"

    def __init__(self, font_path: Path = DEFAULT_FONT_PATH, **kwargs):
        self.font_path = font_path

        super().__init__(**kwargs)

    def get_font_binary(self, font_size: int | float) -> Path:
        return self.BINARIES_DIR / self.FONT_FILENAME.format(font_size=round(font_size))
