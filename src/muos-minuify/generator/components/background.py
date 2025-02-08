from pathlib import Path

from PIL import Image

from ...color_utils import hex_to_rgba
from ...settings import DEFAULT_SETTINGS


class Background:
    def __init__(self):
        self.background_hex = DEFAULT_SETTINGS["bgHexVar"]
        self.background_rgba = hex_to_rgba(self.background_hex)
        self.background_image_path = DEFAULT_SETTINGS["background_image_path"]

    def with_background_hex(self, background_hex: str) -> "Background":
        if background_hex.startswith("#"):
            background_hex = background_hex[1:]

        self.background_rgba = hex_to_rgba(background_hex)

        return self

    def with_background_image(self, background_image_path: Path) -> "Background":
        if background_image_path and background_image_path.exists():
            self.background_image_path = background_image_path

        return self

    def generate(self, screen_dimensions: tuple[int, int] = (640, 480)) -> Image.Image:
        image = Image.new("RGBA", screen_dimensions, self.background_rgba)

        if self.background_image_path:
            background_image = Image.open(self.background_image_path)
            image.paste(
                background_image.resize(screen_dimensions),
                (0, 0),
            )
        return image
