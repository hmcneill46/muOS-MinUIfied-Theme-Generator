from typing import Callable

from PIL import Image

from ..settings import SettingsManager
from .components import Background, HeaderBubbles


class BaseThemeGenerator:
    def __init__(
        self,
        manager: SettingsManager,
        render_factor: int = 1,
        on_progress: Callable | None = None,
    ):
        self.manager = manager
        self.render_factor = render_factor
        self.on_progress = on_progress

    @property
    def screen_dimensions(self) -> tuple[int, int]:
        return (
            int(self.manager.deviceScreenWidthVar),
            int(self.manager.deviceScreenHeightVar),
        )

    @property
    def scaled_screen_dimensions(self) -> tuple[int, int]:
        return (
            self.screen_dimensions[0] * self.render_factor,
            self.screen_dimensions[1] * self.render_factor,
        )

    def _generate_background(self) -> Image.Image:
        bg_hex = self.manager.bgHexVar
        use_background_image = self.manager.use_custom_background_var
        background_image_path = self.manager.background_image_path

        background = Background().with_background_hex(bg_hex)
        if use_background_image and background_image_path:
            background = background.with_background_image(background_image_path)

        background_image = background.generate(self.scaled_screen_dimensions)
        return background_image

    def _generate_header_bubbles(self) -> Image.Image:
        header_height = self.manager.headerHeightVar
        text_height = self.manager.header_text_height_var
        text_bubble_height = self.manager.header_text_bubble_height_var

        clock_format = self.manager.clock_format_var
        clock_bubble_alignment = self.manager.clock_alignment_var
        clock_bubble_margin_left = self.manager.clockHorizontalLeftPaddingVar
        clock_bubble_margin_right = self.manager.clockHorizontalRightPaddingVar

        status_bubble_alignment = self.manager.header_glyph_alignment_var
        status_glyph_height = self.manager.header_glyph_height_var
        status_bubble_height = self.manager.header_glyph_bubble_height_var
        status_bubble_padding_left = (
            self.manager.header_glyph_horizontal_left_padding_var
        )
        status_bubble_padding_right = (
            self.manager.header_glyph_horizontal_right_padding_var
        )

        header_bubbles = (
            HeaderBubbles(
                screen_dimensions=self.scaled_screen_dimensions,
                render_factor=self.render_factor,
            )
            .with_header_configuration(header_height, text_height, text_bubble_height)
            .with_clock_configuration(
                clock_format,
                clock_bubble_alignment,
                clock_bubble_margin_left,
                clock_bubble_margin_right,
            )
            .with_status_configuration(
                status_bubble_alignment,
                status_glyph_height,
                status_bubble_height,
                status_bubble_padding_left,
                status_bubble_padding_right,
            )
        )

        accent_colour = "#ff0000"
        show_clock_bubble = self.manager.show_clock_bubbles_var
        show_status_bubble = self.manager.show_glyphs_bubbles_var
        join_bubbles = self.manager.join_header_bubbles_var

        header_bubbles_image = header_bubbles.generate(
            accent_colour=accent_colour,
            show_clock_bubble=show_clock_bubble,
            show_status_bubble=show_status_bubble,
            join_bubbles=join_bubbles,
        )
        return header_bubbles_image

    def generate_wall_image(self) -> Image.Image:
        background_image = self._generate_background()

        header_bubbles_image = self._generate_header_bubbles()
        background_image.paste(header_bubbles_image, (0, 0), header_bubbles_image)

        return background_image

    def generate_static_image(self) -> Image.Image:
        image = Image.new("RGBA", self.screen_dimensions, (0, 0, 0, 0))

        header_bubbles_image = self._generate_header_bubbles()
        image.alpha_composite(header_bubbles_image)

        return image

    def generate_theme(self):
        pass
