from datetime import datetime
from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw
from PIL.Image import Resampling

from . import HeaderBubbles
from ....color_utils import change_logo_color
from ....constants import (
    GLYPHS_DIR,
    BatteryChargingStyleOptionsDict,
    BatteryStyleOptionsDict,
)
from ....defaults import DEFAULT_FONT_PATH
from ....settings import SettingsManager


class PreviewHeaderBubbles(HeaderBubbles):
    PAGE_TITLE_MAP = {
        "launch": "MAIN MENU",
        "explore": "CONTENT",
        "favourite": "FAVOURITES",
        "history": "HISTORY",
        "apps": "APPLICATIONS",
        "info": "INFORMATION",
        "config": "CONFIGURATION",
    }

    def __init__(
        self,
        manager: SettingsManager,
        font_path: Path = DEFAULT_FONT_PATH,
        screen_dimensions: tuple[int, int] = (640, 480),
        render_factor: int = 5,
    ):
        super().__init__(manager, font_path, screen_dimensions, render_factor)

        self.clock_format = self.manager.clock_format_var

        ascent, descent = self.header_font.getmetrics()
        self.header_text_height = ascent + descent

    def _draw_clock_text(
        self, draw: ImageDraw.ImageDraw, accent_colour: str | None = None
    ) -> None:
        current_time = datetime.now()
        time_text = (
            current_time.strftime("%I:%M %p")
            if self.clock_format == "12 Hour"
            else current_time.strftime("%H:%M")
        )

        left = self.left_x_points.get("clock", 0)
        right = self.right_x_points.get("clock", 0)
        top = self.top_y_points.get("clock", 0)
        bottom = self.bottom_y_points.get("clock", 0)

        bubble_width = right - left
        bubble_height = top - bottom

        text_bbox = self.header_font.getbbox(time_text)
        text_width = text_bbox[2] - text_bbox[0]

        x = left + (bubble_width - text_width) // 2
        y = bottom + (bubble_height - self.header_text_height) // 2

        draw.text(
            (x, y),
            time_text,
            font=self.header_font,
            fill=accent_colour,
        )

    def _draw_clock_bubble(
        self,
        draw: ImageDraw.ImageDraw,
        accent_colour: str | None = None,
        bubble_alpha: float = 0.133,
    ) -> None:
        super()._draw_clock_bubble(draw, accent_colour, bubble_alpha)
        self._draw_clock_text(draw, accent_colour)

    def _draw_page_title(
        self,
        draw: ImageDraw.ImageDraw,
        selected_item: str,
    ) -> None:
        page_title = self.PAGE_TITLE_MAP.get(selected_item, "UNKNOWN")

        text_bbox = self.header_font.getbbox(page_title)
        text_width = text_bbox[2] - text_bbox[0]

        match self.page_title_alignment:
            case "Left":
                page_title_x_pos = self.page_title_margin_inline
            case "Centre":
                page_title_x_pos = (self.scaled_screen_dimensions[0] / 2) - (
                    text_width / 2
                )
            case "Right":
                page_title_x_pos = (
                    self.scaled_screen_dimensions[0]
                    - text_width
                    - self.page_title_margin_inline
                )
            case _:
                raise ValueError(
                    "Page title alignment must be 'Left', 'Centre', or 'Right'!"
                )

        page_title_y_pos = int((self.header_height / 2) - (self.header_text_height / 2))

        draw.text(
            (page_title_x_pos, page_title_y_pos),
            page_title,
            font=self.header_font,
            fill=self.manager.deselectedFontHexVar,
        )

    def __generate_glyph(
        self, color_hex: str, height: int, glyph_path: Path
    ) -> Image.Image:
        glyph_coloured = change_logo_color(glyph_path, color_hex)
        original_width, original_height = glyph_coloured.size
        scaled_width = int(height * original_width / original_height)
        glyph_coloured = glyph_coloured.resize(
            (scaled_width, height), Resampling.LANCZOS
        )

        return glyph_coloured

    def _generate_network_glyph(
        self,
        color_hex: str,
        height: int,
        glyph_name: str = "network_active",
    ) -> Image.Image:
        network_glyph_path = GLYPHS_DIR / f"{glyph_name}[5x].png"
        return self.__generate_glyph(color_hex, height, network_glyph_path)

    def _generate_battery_glyph(
        self,
        color_hex: str,
        height: int,
        charging: bool = False,
        current: int = 30,
    ) -> Image.Image:
        if current < 0 or current > 100 or current % 10 != 0:
            raise ValueError("Current battery percentage must be a multiple of 10")

        color_hex = self.manager.batteryChargingHexVar if charging else color_hex
        battery_style_option_dict = (
            BatteryChargingStyleOptionsDict if charging else BatteryStyleOptionsDict
        )
        battery_style_option = (
            self.manager.battery_charging_style_var
            if charging
            else self.manager.battery_style_var
        )

        battery_glyph_path = (
            GLYPHS_DIR
            / f"{battery_style_option_dict[battery_style_option]}{current}[5x].png"
        )

        return self.__generate_glyph(color_hex, height, battery_glyph_path)

    def _draw_network_glyph(self, image: Image.Image) -> None:
        color_hex = self.manager.deselectedFontHexVar
        network_glyph = self._generate_network_glyph(
            color_hex, self.status_glyph_height
        )

        bubble_top = self.top_y_points.get("status", 0)
        bubble_bottom = self.bottom_y_points.get("status", 0)

        x = int(self.status_x_pos)
        y = int(
            bubble_bottom
            + ((bubble_top - bubble_bottom) - self.status_glyph_height) / 2
        )

        image.paste(network_glyph, (x, y), network_glyph)

    def _draw_battery_glyph(
        self,
        image: Image.Image,
        show_charging: bool,
        charging_hex: str,
    ) -> None:
        color_hex = self.manager.deselectedFontHexVar
        battery_glyph = self._generate_battery_glyph(
            charging_hex if show_charging else color_hex,
            self.status_glyph_height,
            charging=show_charging,
            current=30,
        )
        network_glyph = self._generate_network_glyph(
            color_hex, self.status_glyph_height
        )

        bubble_top = self.top_y_points.get("status", 0)
        bubble_bottom = self.bottom_y_points.get("status", 0)

        x = int(self.status_x_pos + network_glyph.size[0] + self.status_bubble_gap)
        y = int(
            bubble_bottom
            + ((bubble_top - bubble_bottom) - self.status_glyph_height) / 2
        )

        image.paste(battery_glyph, (x, y), battery_glyph)

    def _draw_status_glyphs(
        self,
        image: Image.Image,
        show_charging: bool,
        charging_hex: str,
    ) -> None:
        self._draw_network_glyph(image)
        self._draw_battery_glyph(image, show_charging, charging_hex)

    def _draw_status_bubble(
        self,
        image: Image.Image,
        draw: ImageDraw.ImageDraw,
        accent_colour: str | None = None,
        bubble_alpha: float = 0.133,
    ) -> None:
        super()._draw_status_bubble(image, draw, accent_colour, bubble_alpha)
        self._draw_status_glyphs(image, self.show_charging, self.charging_hex)

    def with_header_configuration(
        self,
        header_height: int,
        header_text_height: int,
        header_text_bubble_height: int,
    ) -> "PreviewHeaderBubbles":
        return super().with_header_configuration(
            header_height,
            header_text_height,
            header_text_bubble_height,
        )

    def with_clock_configuration(
        self,
        clock_format: Literal["12 Hour", "24 Hour"],
        clock_bubble_alignment: Literal["Left", "Centre", "Right"],
        clock_bubble_margin_left: int,
        clock_bubble_margin_right: int,
    ) -> "PreviewHeaderBubbles":
        return super().with_clock_configuration(
            clock_format,
            clock_bubble_alignment,
            clock_bubble_margin_left,
            clock_bubble_margin_right,
        )

    def with_status_configuration(
        self,
        status_bubble_alignment: Literal["Left", "Centre", "Right"],
        status_glyph_height: int,
        status_bubble_height: int,
        status_bubble_padding_left: int,
        status_bubble_padding_right: int,
        status_bubble_gap: int = 5,
    ) -> "PreviewHeaderBubbles":
        return super().with_status_configuration(
            status_bubble_alignment,
            status_glyph_height,
            status_bubble_height,
            status_bubble_padding_left,
            status_bubble_padding_right,
            status_bubble_gap,
        )

    def generate(
        self,
        accent_colour: str | None = None,
        bubble_alpha: float = 0.133,
        show_clock_bubble: bool = False,
        show_status_bubble: bool = False,
        join_bubbles: bool = False,
        show_page_title: bool = False,
        show_charging: bool = False,
        charging_hex: str = "#FFFFFF",
        selected_item: str = "explore",
    ) -> Image.Image:
        self.show_charging = show_charging
        self.charging_hex = charging_hex

        image = super().generate(
            accent_colour,
            bubble_alpha,
            show_clock_bubble,
            show_status_bubble,
            join_bubbles,
        )
        draw = ImageDraw.Draw(image)

        if show_page_title:
            self._draw_page_title(draw, selected_item)

        return image
