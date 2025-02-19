from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling

from . import ThemeGenerator
from ..constants import OVERLAY_DIR
from .components.header.preview import PreviewHeaderBubbles
from ..settings import SettingsManager
from ..font import get_font_path


class ThemePreviewGenerator(ThemeGenerator):
    def __init__(
        self,
        manager: SettingsManager,
        render_factor: int = 5,
    ):
        super().__init__(manager, render_factor)

    @property
    def preview_size(self) -> tuple[int, int]:
        return (
            int(288 * 640 / self.screen_dimensions[0]),
            int(216 * 480 / self.screen_dimensions[1]),
        )

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

    def _generate_launcher_list(
        self,
        draw: ImageDraw.ImageDraw,
        selected_item: str = "explore",
    ) -> None:
        item_map = {
            "explore": "Content Explorer",
            "favourite": "Favourites",
            "history": "History",
            "apps": "Utilities",
            "info": "Information",
            "config": "Configuration",
            "reboot": "Reboot",
            "shutdown": "Shutdown",
        }

        text_padding = int(self.manager.textPaddingVar * self.render_factor)
        bubble_padding = int(self.manager.bubblePaddingVar * self.render_factor)
        screen_width = int(self.manager.deviceScreenWidthVar * self.render_factor)
        screen_height = int(self.manager.deviceScreenHeightVar * self.render_factor)

        items_per_screen = int(self.manager.itemsPerScreenVar)

        text_alignment = self.manager.global_alignment_var
        content_padding_top = int(
            self.manager.contentPaddingTopVar * self.render_factor
        )
        approx_footer_height = int(
            self.manager.approxFooterHeightVar * self.render_factor
        )
        individual_item_height = round(
            (screen_height - approx_footer_height - content_padding_top)
            / items_per_screen
        )
        max_boxart_width = int(self.manager.maxBoxArtWidth * self.render_factor)
        max_bubble_length = screen_width - max_boxart_width

        selected_font_hex = self.manager.selectedFontHexVar
        deselected_font_hex = self.manager.deselectedFontHexVar
        bubble_hex = self.manager.bubbleHexVar

        font_size = int(self.manager.font_size_var * self.render_factor)

        selected_font_path = get_font_path(
            self.manager.use_alt_font_var, self.manager.alt_font_filename
        )
        font = ImageFont.truetype(selected_font_path, font_size)

        smallestValidText_bbox = font.getbbox("_...")
        smallestValidTest_width = smallestValidText_bbox[2] - smallestValidText_bbox[0]

        for index, (app, label) in enumerate(item_map.items()):
            if index >= items_per_screen:
                break

            num_letters_cut = 0
            text_width = float("inf")
            text = label
            text_color = deselected_font_hex

            if (
                max_bubble_length
                < text_padding
                + smallestValidTest_width
                + bubble_padding
                + 5 * self.render_factor
            ):  # Make sure there won't be a bubble error
                max_bubble_length = screen_width

            if app == selected_item:
                text_color = selected_font_hex

                total_current_length = text_padding + text_width + bubble_padding
            else:
                total_current_length = text_padding + text_width

            while total_current_length > max_bubble_length:
                if num_letters_cut > 0:
                    text = label[: -(num_letters_cut + 3)]
                    text = label + "..."

                text_bbox = font.getbbox(label)
                text_width = text_bbox[2] - text_bbox[0]
                if app == selected_item:
                    total_current_length = text_padding + text_width + bubble_padding
                else:
                    total_current_length = text_padding + text_width

                num_letters_cut += 1
                if text == "...":
                    raise ValueError(
                        "'Cut bubble off at' too low\n\nPlease use a different custom 'cut bubble off' at value"
                    )

            text_x = 0
            if text_alignment == "Left":
                text_x = text_padding
            elif text_alignment == "Right":
                text_x = screen_width - text_padding - text_width
            elif text_alignment == "Centre":
                text_x = (screen_width - text_width) / 2

            rectangle_x0 = text_x - bubble_padding
            rectangle_y0 = content_padding_top + individual_item_height * index
            rectangle_x1 = rectangle_x0 + bubble_padding + text_width + bubble_padding
            rectangle_y1 = content_padding_top + individual_item_height * (index + 1)
            middle_y = (rectangle_y0 + rectangle_y1) / 2
            ascent, descent = font.getmetrics()
            text_height = ascent + descent

            # Calculate the text's y-position by centreing it vertically within the rectangle
            text_y = middle_y - (text_height / 2)

            corner_radius = individual_item_height // 2

            if app == selected_item:
                draw.rounded_rectangle(
                    [(rectangle_x0, rectangle_y0), (rectangle_x1, rectangle_y1)],
                    radius=corner_radius,
                    fill=bubble_hex,
                )
            draw.text((text_x, text_y), text, font=font, fill=text_color)

    def _generate_overlay(self, for_preview: bool = False) -> Image.Image | None:
        preview_overlay_image = None

        dimensions = self.preview_size if for_preview else self.screen_dimensions

        if self.manager.include_overlay_var and self.manager.selected_overlay_var:
            preview_overlay_path = (
                OVERLAY_DIR
                / f"{dimensions[0]}x{dimensions[1]}"
                / f"{self.manager.selected_overlay_var}.png"
            )
            if preview_overlay_path.exists():
                preview_overlay_image = Image.open(preview_overlay_path).convert("RGBA")

        return preview_overlay_image

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

        image = image.resize(self.screen_dimensions, Resampling.LANCZOS)

        if overlay_image := self._generate_overlay():
            image.alpha_composite(overlay_image, (0, 0))

        return image

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

        image = image.resize(self.screen_dimensions, Resampling.LANCZOS)

        if overlay_image := self._generate_overlay():
            image.alpha_composite(overlay_image, (0, 0))

        return image

    def generate_launcher_image(
        self,
        right_buttons: list[tuple[str, str]] = [],
        left_buttons: list[tuple[str, str]] = [("POWER", "SLEEP")],
        selected_item: str = "explore",
        variant: str | None = None,
        for_preview: bool = False,
        *args,
    ) -> Image.Image:
        dimensions = self.preview_size if for_preview else self.screen_dimensions

        image = self._generate_background()
        variant = variant or self.manager.main_menu_style_var

        if variant == "Vertical":
            draw = ImageDraw.Draw(image)
            self._generate_launcher_list(draw, selected_item)
        else:
            launcher_image = self._generate_launcher_icons(selected_item, variant)
            image.alpha_composite(launcher_image)

        header_bubbles_image = self._generate_header_bubbles(selected_item)
        image.alpha_composite(header_bubbles_image)

        footer_guides_image = self._generate_footer_guides(right_buttons, left_buttons)
        image.alpha_composite(footer_guides_image)

        image = image.resize(dimensions, Resampling.LANCZOS)

        if overlay_image := self._generate_overlay():
            image.alpha_composite(overlay_image, (0, 0))

        return image
