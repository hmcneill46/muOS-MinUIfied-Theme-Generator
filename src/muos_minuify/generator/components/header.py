import math
from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling

from ...color_utils import hex_to_rgba
from ...constants import GLYPHS_DIR
from ...defaults import DEFAULT_FONT_PATH
from ...settings import SettingsManager
from ...utils import get_max_length_time_string
from .scalable import Scalable


class HeaderBubbles(Scalable):
    capacity_30 = "capacity_30.png"
    capacity_image_path = GLYPHS_DIR / "capacity_30[5x].png"
    network_active = "network_active.png"
    network_image_path = GLYPHS_DIR / "network_active[5x].png"

    def __init__(
        self,
        manager: SettingsManager,
        font_path: Path = DEFAULT_FONT_PATH,
        screen_dimensions: tuple[int, int] = (640, 480),
        render_factor: int = 5,
    ):
        super().__init__(screen_dimensions, render_factor)
        self.manager = manager

        self.header_height = self.manager.headerHeightVar * self.render_factor
        self.text_height = (
            self.manager.header_text_height_var * self.render_factor * 4 / 3
        )
        self.text_bubble_height = (
            self.manager.header_text_bubble_height_var * self.render_factor
        )
        self.text_bubble_padding_block = (
            self.manager.contentPaddingTopVar * self.render_factor
        )

        self.clock_format = self.manager.clock_format_var
        self.clock_bubble_alignment = self.manager.clock_alignment_var
        self.clock_bubble_margin_left = (
            self.manager.clockHorizontalLeftPaddingVar * self.render_factor
        )
        self.clock_bubble_margin_left = (
            self.manager.clockHorizontalRightPaddingVar * self.render_factor
        )

        self.status_bubble_alignment = self.manager.header_glyph_alignment_var
        self.status_glyph_height = (
            self.manager.header_glyph_height_var * self.render_factor
        )
        self.status_bubble_height = (
            self.manager.header_glyph_bubble_height_var * self.render_factor
        )
        self.status_bubble_padding_left = (
            self.manager.header_glyph_horizontal_left_padding_var * self.render_factor
        )
        self.status_bubble_padding_right = (
            self.manager.header_glyph_horizontal_right_padding_var * self.render_factor
        )
        self.status_bubble_gap = 5 * self.render_factor
        self.status_bubble_margin_inline = (
            self.status_bubble_height - self.status_glyph_height
        ) / 2

        self.clock_x_pos = self.clock_bubble_margin_left
        self.center_y_pos = self.header_height / 2

        self.bottom_y_points = {}
        self.top_y_points = {}
        self.left_x_points = {}
        self.right_x_points = {}

        self.header_font = ImageFont.truetype(font_path, self.text_height)
        self.capacity_glyph = Image.open(self.capacity_image_path).convert("RGBA")
        self.network_glyph = Image.open(self.network_image_path).convert("RGBA")

    def with_header_configuration(
        self,
        header_height: int,
        header_text_height: int,
        header_text_bubble_height: int,
    ) -> "HeaderBubbles":
        self.header_height = header_height * self.render_factor

        if not (10 <= header_text_height <= header_height):
            raise ValueError(
                f"Header text height must be between 10 and {header_height}!"
            )
        else:
            self.text_height = header_text_height * self.render_factor * 4 / 3
            self.header_font.size = self.text_height

        if not (header_text_height <= header_text_bubble_height <= header_height):
            raise ValueError(
                f"Header text bubble height must be between {header_text_height} and {header_height}!"
            )
        else:
            self.text_bubble_height = header_text_bubble_height * self.render_factor
            self.text_bubble_padding_block = (
                (header_text_bubble_height - header_text_height)
                / 2
                * self.render_factor
            )

        self.center_y_pos = self.header_height / 2

        return self

    def with_clock_configuration(
        self,
        clock_format: Literal["12 Hour", "24 Hour"],
        clock_bubble_alignment: Literal["Left", "Centre", "Right"],
        clock_bubble_margin_left: int,
        clock_bubble_margin_right: int,
    ) -> "HeaderBubbles":
        if clock_bubble_alignment not in ["Left", "Centre", "Right"]:
            raise ValueError("Clock alignment must be 'Left', 'Centre', or 'Right'!")
        else:
            self.clock_bubble_alignment = clock_bubble_alignment

        if clock_format not in ["12 Hour", "24 Hour"]:
            raise ValueError("Clock format must be '12 Hour' or '24 Hour'!")
        else:
            self.clock_format = clock_format

        timeText = get_max_length_time_string(self.header_font, self.clock_format)
        headerBbox = self.header_font.getbbox(timeText)
        maxTimeTextWidth = headerBbox[2] - headerBbox[0]

        match self.clock_bubble_alignment:
            case "Left":
                self.clock_x_pos = clock_bubble_margin_left * self.render_factor
            case "Centre":
                self.clock_x_pos = (
                    (self.scaled_screen_dimensions[0] / 2)
                    - (
                        (
                            maxTimeTextWidth
                            + (
                                self.render_factor
                                * (clock_bubble_margin_left + clock_bubble_margin_right)
                            )
                        )
                        / 2
                    )
                    + (clock_bubble_margin_left * self.render_factor)
                )
            case "Right":
                self.clock_x_pos = self.scaled_screen_dimensions[0] - (
                    maxTimeTextWidth + (clock_bubble_margin_right * self.render_factor)
                )

        self.bottom_y_points["clock"] = self.center_y_pos - (
            self.text_bubble_height / 2
        )
        self.top_y_points["clock"] = self.center_y_pos + (self.text_bubble_height / 2)
        self.left_x_points["clock"] = self.clock_x_pos - self.text_bubble_padding_block
        self.right_x_points["clock"] = (
            self.clock_x_pos + maxTimeTextWidth + self.text_bubble_padding_block
        )

        return self

    def with_status_configuration(
        self,
        status_bubble_alignment: Literal["Left", "Centre", "Right"],
        status_glyph_height: int,
        status_bubble_height: int,
        status_bubble_padding_left: int,
        status_bubble_padding_right: int,
        status_bubble_gap: int = 5,
    ) -> "HeaderBubbles":
        if not (10 <= status_glyph_height <= self.header_height):
            raise ValueError(
                f"Header glyph height must be between 10 and {self.header_height}!"
            )
        else:
            self.status_glyph_height = status_glyph_height * self.render_factor

        if not (status_glyph_height <= status_bubble_height <= self.header_height):
            raise ValueError(
                f"Header status bubble height must be between {status_glyph_height} and {self.header_height}!"
            )
        else:
            self.status_bubble_height = status_bubble_height * self.render_factor
            self.status_bubble_margin_inline = (
                status_bubble_height - status_glyph_height
            ) // 2

        scaled_capacity_glyph = self.capacity_glyph.resize(
            (
                int(
                    self.status_glyph_height
                    * self.capacity_glyph.size[0]
                    / self.capacity_glyph.size[1]
                ),
                self.status_glyph_height,
            ),
            Resampling.LANCZOS,
        )
        scaled_network_glyph = self.network_glyph.resize(
            (
                int(
                    self.status_glyph_height
                    * self.network_glyph.size[0]
                    / self.network_glyph.size[1]
                ),
                self.status_glyph_height,
            ),
            Resampling.LANCZOS,
        )

        glyphTotalWidth = (
            scaled_capacity_glyph.size[0]
            + (status_bubble_gap * self.render_factor)
            + scaled_network_glyph.size[0]
        )

        if status_bubble_alignment not in ["Left", "Centre", "Right"]:
            raise ValueError("Status alignment must be 'Left', 'Centre', or 'Right'!")
        else:
            self.status_bubble_alignment = status_bubble_alignment

        match status_bubble_alignment:
            case "Left":
                self.status_x_pos = status_bubble_padding_left * self.render_factor
            case "Centre":
                self.status_x_pos = int(
                    (self.scaled_screen_dimensions[0] / 2)
                    - (
                        (
                            glyphTotalWidth
                            + (
                                self.render_factor
                                * (
                                    status_bubble_padding_left
                                    + status_bubble_padding_right
                                )
                            )
                        )
                        / 2
                    )
                )
            case "Right":
                self.status_x_pos = int(
                    (self.scaled_screen_dimensions[0])
                    - (
                        glyphTotalWidth
                        + (status_bubble_padding_right * self.render_factor)
                    )
                )

        self.bottom_y_points["status"] = self.center_y_pos - (
            status_bubble_height * self.render_factor / 2
        )
        self.top_y_points["status"] = self.center_y_pos + (
            status_bubble_height * self.render_factor / 2
        )
        self.left_x_points["status"] = (
            self.status_x_pos - self.status_bubble_margin_inline * self.render_factor
        )
        self.right_x_points["status"] = (
            self.status_x_pos
            + glyphTotalWidth
            + (self.status_bubble_margin_inline * self.render_factor)
        )

        return self

    def __draw_bubble(
        self,
        draw: ImageDraw.ImageDraw,
        key: str,
        accent_colour=None,
        bubble_alpha=0.133,
    ) -> None:
        if not all(
            key in d
            for d in [
                self.bottom_y_points,
                self.top_y_points,
                self.left_x_points,
                self.right_x_points,
            ]
        ):
            return

        draw.rounded_rectangle(
            [
                (self.left_x_points[key], self.bottom_y_points[key]),
                (self.right_x_points[key], self.top_y_points[key]),
            ],
            radius=math.ceil((self.top_y_points[key] - self.bottom_y_points[key]) / 2),
            fill=hex_to_rgba(accent_colour, alpha=bubble_alpha),
        )

    def _draw_clock_bubble(
        self,
        draw: ImageDraw.ImageDraw,
        accent_colour: str | None = None,
        bubble_alpha: float = 0.133,
    ) -> None:
        self.__draw_bubble(draw, "clock", accent_colour, bubble_alpha)

    def _draw_status_bubble(
        self,
        draw: ImageDraw.ImageDraw,
        accent_colour: str | None = None,
        bubble_alpha: float = 0.133,
    ) -> None:
        self.__draw_bubble(draw, "status", accent_colour, bubble_alpha)

    def _draw_joined_bubble(
        self,
        draw: ImageDraw.ImageDraw,
        accent_colour: str | None = None,
        bubble_alpha: float = 0.133,
    ) -> None:
        bottom_y = min(self.bottom_y_points.values())
        top_y = max(self.top_y_points.values())
        left_x = min(self.left_x_points.values())
        right_x = max(self.right_x_points.values())

        draw.rounded_rectangle(
            [
                (left_x, bottom_y),
                (right_x, top_y),
            ],
            radius=math.ceil((top_y - bottom_y) / 2),
            fill=hex_to_rgba(accent_colour, alpha=bubble_alpha),
        )

    def generate(
        self,
        accent_colour: str | None = None,
        bubble_alpha: float = 0.133,
        show_clock_bubble: bool = False,
        show_status_bubble: bool = False,
        join_bubbles: bool = False,
    ) -> Image.Image:
        image = Image.new("RGBA", self.scaled_screen_dimensions, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        if join_bubbles:
            self._draw_joined_bubble(draw, accent_colour, bubble_alpha)
        else:
            if show_clock_bubble:
                self._draw_clock_bubble(draw, accent_colour, bubble_alpha)

            if show_status_bubble:
                self._draw_status_bubble(draw, accent_colour, bubble_alpha)

        return image
