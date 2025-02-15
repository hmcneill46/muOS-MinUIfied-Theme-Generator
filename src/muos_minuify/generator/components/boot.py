from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ...color_utils import hex_to_rgba
from ...defaults import DEFAULT_FONT_PATH
from ...settings import SettingsManager
from .scalable import Scalable


class BootScreen(Scalable):
    def __init__(
        self,
        manager: SettingsManager,
        font_path: Path = DEFAULT_FONT_PATH,
        screen_dimensions: tuple[int, int] = (640, 480),
        render_factor: int = 5,
    ):
        super().__init__(screen_dimensions, render_factor)
        self.manager = manager
        self.font_path = font_path

        mu_font_size = 130 * self.render_factor
        os_font_size = 98 * self.render_factor
        self.mu_font = ImageFont.truetype(self.font_path, mu_font_size)
        self.os_font = ImageFont.truetype(self.font_path, os_font_size)

    def with_color_configuration(
        self,
        bg_hex: str,
        deselected_font_hex: str,
        bubble_hex: str,
    ) -> "BootScreen":
        self.bg_hex = bg_hex
        self.bg_rgba = hex_to_rgba(bg_hex)
        self.deselected_font_hex = deselected_font_hex
        self.bubble_hex = bubble_hex

        return self

    def with_bootlogo_image(self, bootlogo_image_path: Path) -> "BootScreen":
        if bootlogo_image_path and bootlogo_image_path.exists():
            self.bootlogo_image_path = bootlogo_image_path

        return self

    def _draw_muos_logo(self) -> Image.Image:
        image = Image.new("RGBA", self.scaled_screen_dimensions, (0, 0, 0, 0))
        mask = Image.new("RGBA", self.scaled_screen_dimensions, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        mask_draw = ImageDraw.Draw(mask)

        muText = "mu"
        osText = "OS"

        mu_bbox = self.mu_font.getbbox(muText)
        os_bbox = self.os_font.getbbox(osText)
        from_middle_spacing = 20 * self.render_factor

        screen_x_center = self.scaled_screen_dimensions[0] // 2
        screen_y_center = self.scaled_screen_dimensions[1] // 2

        mu_text_width = mu_bbox[2] - mu_bbox[0]
        os_text_width = os_bbox[2] - os_bbox[0]
        mu_text_height = mu_bbox[3] - mu_bbox[1]
        os_text_height = os_bbox[3] - os_bbox[1]

        mu_x_pos = screen_x_center - mu_text_width - from_middle_spacing
        mu_y_pos = screen_y_center - mu_text_height // 2 - mu_bbox[1]

        os_x_pos = screen_x_center + from_middle_spacing
        os_y_pos = screen_y_center - os_text_height // 2 - os_bbox[1]

        bubble_x_padding = 30 * self.render_factor
        bubble_y_padding = 25 * self.render_factor

        bubble_mid_x = screen_x_center + from_middle_spacing + (os_text_width // 2)
        bubble_width = bubble_x_padding + os_text_width + bubble_x_padding
        bubble_height = bubble_y_padding + os_text_height + bubble_y_padding

        mask_draw.rounded_rectangle(
            [
                (
                    bubble_mid_x - bubble_width // 2,
                    screen_y_center - (bubble_height / 2),
                ),
                (
                    bubble_mid_x + bubble_width // 2,
                    screen_y_center + (bubble_height / 2),
                ),
            ],
            fill=self.bubble_hex,
            radius=bubble_height / 2,
        )

        draw.text(
            (mu_x_pos, mu_y_pos),
            muText,
            font=self.mu_font,
            fill=self.deselected_font_hex,
        )
        mask_draw.text(
            (os_x_pos, os_y_pos),
            osText,
            font=self.os_font,
            fill=hex_to_rgba(self.bubble_hex, alpha=0),
        )

        combined = Image.alpha_composite(image, mask)
        return combined

    def generate_with_logo(
        self,
        use_custom_bootlogo: bool = False,
    ) -> Image.Image:
        if use_custom_bootlogo and self.bootlogo_image_path:
            bootlogo_image = Image.open(self.bootlogo_image_path).convert("RGBA")
            bootlogo_image = bootlogo_image.resize(self.scaled_screen_dimensions)
            return bootlogo_image

        return self._draw_muos_logo()
