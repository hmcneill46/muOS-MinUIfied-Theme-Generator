from pathlib import Path

from PIL import Image

from ...color_utils import hex_to_rgba
from ...settings import SettingsManager
from .scalable import Scalable


class Background(Scalable):
    def __init__(
        self,
        manager: SettingsManager,
        screen_dimensions: tuple[int, int] = (640, 480),
        render_factor: int = 5,
    ):
        super().__init__(screen_dimensions, render_factor)
        self.manager = manager

        self.background_hex = self.manager.bgHexVar
        self.background_rgba = hex_to_rgba(self.background_hex)
        self.background_image_path = self.manager.background_image_path

    def with_background_hex(self, background_hex: str) -> "Background":
        if background_hex.startswith("#"):
            background_hex = background_hex[1:]

        self.background_rgba = hex_to_rgba(background_hex)

        return self

    def with_background_image(self, background_image_path: Path) -> "Background":
        if background_image_path and background_image_path.exists():
            self.background_image_path = background_image_path

        return self

    def generate(self, use_background_image: bool = False) -> Image.Image:
        image = Image.new("RGBA", self.scaled_screen_dimensions, self.background_rgba)

        if use_background_image and self.background_image_path:
            background_image = Image.open(self.background_image_path)
            image.paste(
                background_image.resize(self.scaled_screen_dimensions),
                (0, 0),
            )
        return image
