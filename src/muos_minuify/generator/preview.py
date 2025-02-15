from PIL import Image
from PIL.Image import Resampling

from . import ThemeGenerator
from .components.header.preview import PreviewHeaderBubbles
from ..settings import SettingsManager


class ThemePreviewGenerator(ThemeGenerator):
    def __init__(
        self,
        manager: SettingsManager,
        render_factor: int = 5,
    ):
        super().__init__(manager, render_factor)

    def _generate_header_bubbles(self, selected_item: str = "", *args) -> Image.Image:
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
            PreviewHeaderBubbles(
                manager=self.manager,
                screen_dimensions=self.screen_dimensions,
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

        accent_colour = self.manager.deselectedFontHexVar
        show_clock_bubble = self.manager.show_clock_bubbles_var
        show_status_bubble = self.manager.show_glyphs_bubbles_var
        join_bubbles = self.manager.join_header_bubbles_var
        show_page_title = self.manager.show_console_name_var
        show_charging = self.manager.show_charging_battery_var
        charging_hex = self.manager.batteryChargingHexVar

        header_bubbles_image = header_bubbles.generate(
            accent_colour=accent_colour,
            show_clock_bubble=show_clock_bubble,
            show_status_bubble=show_status_bubble,
            join_bubbles=join_bubbles,
            show_page_title=show_page_title,
            show_charging=show_charging,
            charging_hex=charging_hex,
            selected_item="launch",
        )
        return header_bubbles_image

    def generate_wall_image(
        self,
        right_buttons: list[tuple[str, str]] = [],
        left_buttons: list[tuple[str, str]] = [("POWER", "SLEEP")],
        selected_item: str = "explore",
        *args,
    ) -> Image.Image:
        image = self._generate_background()

        header_bubbles_image = self._generate_header_bubbles(selected_item)
        image.alpha_composite(header_bubbles_image, (0, 0))

        footer_guides_image = self._generate_footer_guides(right_buttons, left_buttons)
        image.alpha_composite(footer_guides_image, (0, 0))

        return image.resize(self.screen_dimensions, Resampling.LANCZOS)

    def generate_static_image(
        self,
        right_buttons: list[tuple[str, str]] = [],
        left_buttons: list[tuple[str, str]] = [("POWER", "SLEEP")],
        selected_item: str = "explore",
        *args,
    ) -> Image.Image:
        image = Image.new("RGBA", self.scaled_screen_dimensions, (0, 0, 0, 0))

        header_bubbles_image = self._generate_header_bubbles(selected_item)
        image.alpha_composite(header_bubbles_image)

        footer_guides_image = self._generate_footer_guides(right_buttons, left_buttons)
        image.alpha_composite(footer_guides_image)

        return image.resize(self.screen_dimensions, Resampling.LANCZOS)
