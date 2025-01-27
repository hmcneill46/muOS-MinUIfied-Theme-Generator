from datetime import datetime
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont
from PIL.Image import Resampling

from generator.color_utils import change_logo_color
from generator.constants import (
    GLYPHS_DIR,
    BatteryStyleOptionsDict,
    BatteryChargingStyleOptionsDict,
)
from generator.font import get_font_path
from generator.settings import SettingsManager
from generator.theme.base import BaseThemeGenerator


class PreviewThemeGenerator(BaseThemeGenerator):
    def __init__(self, manager: SettingsManager, render_factor: int):
        super().__init__(manager, render_factor)

    def _generate_preview_glyph(
        self, glyph_color: str, glyph_height: int, glyph_path: Path
    ) -> Image.Image:
        glyph_coloured = change_logo_color(glyph_path, glyph_color)
        glyph_scaled_height = int(
            glyph_height * (glyph_coloured.size[0] / glyph_coloured.size[1])
        )
        glyph_coloured = glyph_coloured.resize(
            (glyph_scaled_height, glyph_height), Resampling.LANCZOS
        )
        return glyph_coloured

    def _generate_battery_preview_glyph(
        self,
        glyph_color: str,
        glyph_height: int,
        charging: bool = False,
        current: int = 30,
    ) -> Image.Image:
        if 100 < current < 0 or current % 10:
            raise ValueError("Current must be a multiple of 10 between 0 and 100!")

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

        return self._generate_preview_glyph(
            self.manager.batteryChargingHexVar if charging else glyph_color,
            glyph_height,
            battery_glyph_path,
        )

    def _generate_network_preview_glyph(
        self, glyph_color: str, glyph_height: int, glyph_name: str = "network_active"
    ) -> Image.Image:
        network_glyph_path = GLYPHS_DIR / f"{glyph_name}[5x].png"

        return self._generate_preview_glyph(
            glyph_color, glyph_height, network_glyph_path
        )

    def _generate_header_preview_glyphs(
        self,
        glyph_alignment: str,
        glyph_color: str,
        glyph_gap: int,
        glyph_height: int,
        glyph_padding: tuple[int, int],
        header_height: int,
    ) -> Image.Image:
        image = self.generate_background_image(transparent=True)

        battery_glyph_image = self._generate_battery_preview_glyph(
            glyph_color,
            glyph_height,
            charging=self.manager.show_charging_battery_var,
        )
        network_glyph_image = self._generate_network_preview_glyph(
            glyph_color, glyph_height
        )

        header_glyphs_total_width = (
            battery_glyph_image.size[0] + glyph_gap + network_glyph_image.size[0]
        )

        header_glyph_x_pos = 0
        header_glyph_y_pos = int((header_height / 2) - (glyph_height / 2))

        if glyph_alignment == "Left":
            header_glyph_x_pos = glyph_padding[0]
        elif glyph_alignment == "Centre":
            header_glyph_x_pos = (
                int(
                    self.scaled_screen_dimensions[0] / 2
                    - (
                        (
                            header_glyphs_total_width
                            + glyph_padding[1]
                            + glyph_padding[0]
                        )
                        / 2
                    )
                )
                + glyph_padding[0]
            )
        elif glyph_alignment == "Right":
            header_glyph_x_pos = (
                self.scaled_screen_dimensions[0]
                - glyph_padding[1]
                - header_glyphs_total_width
            )
        else:
            raise ValueError("Invalid header glyph alignment")

        image.paste(
            network_glyph_image,
            (header_glyph_x_pos, header_glyph_y_pos),
            network_glyph_image,
        )

        header_glyph_x_pos += network_glyph_image.size[0] + glyph_gap

        image.paste(
            battery_glyph_image,
            (header_glyph_x_pos, header_glyph_y_pos),
            battery_glyph_image,
        )

        return image

    def _generate_header_preview_image(
        self, muOSpageName: str = "muxlaunch"
    ) -> Image.Image:
        muOSpageNameDict = {
            "muxlaunch": "MAIN MENU",
            "muxconfig": "CONFIGURATION",
            "muxinfo": "INFORMATION",
            "muxapp": "APPLICATIONS",
            "muxplore": "ROMS",
            "muxfavourite": "FAVOURITES",
            "muxhistory": "HISTORY",
        }
        current_time = datetime.now()
        clock_format = self.manager.clock_format_var

        accent_colour: str = self.manager.deselectedFontHexVar
        if accent_colour.startswith("#"):
            accent_colour = accent_colour[1:]

        image = self.generate_background_image(transparent=True)

        header_height = int(self.manager.headerHeightVar)

        header_glyph_height = int(self.manager.header_glyph_height_var)
        if header_height < header_glyph_height < 10:
            raise ValueError(
                f"Header Glyph Height must be between 10 and {header_height}!"
            )
        else:
            header_height *= self.render_factor
            header_glyph_height *= self.render_factor

        header_text_height = int(self.manager.header_text_height_var)
        if header_height < header_text_height < 10:
            raise ValueError(
                f"Header Text Height must be between 10 and {header_height}!"
            )
        else:
            header_text_height *= self.render_factor

        header_font_size = int(header_text_height * (4 / 3))
        header_font_path = get_font_path(
            self.manager.use_alt_font_var, self.manager.alt_font_filename
        )
        header_font = ImageFont.truetype(header_font_path, header_font_size)

        header_clock_alignment = self.manager.clock_alignment_var
        header_clock_left_padding = int(
            self.manager.clockHorizontalLeftPaddingVar * self.render_factor
        )
        header_clock_right_padding = int(
            self.manager.clockHorizontalRightPaddingVar * self.render_factor
        )

        # generate and offset battery and network glyphs
        header_glyph_left_padding = int(
            self.manager.header_glyph_horizontal_left_padding_var * self.render_factor
        )
        header_glyph_right_padding = int(
            self.manager.header_glyph_horizontal_right_padding_var * self.render_factor
        )
        header_glyph_gap = 5 * self.render_factor
        header_glyph_alignment = self.manager.header_glyph_alignment_var

        header_glyphs_image = self._generate_header_preview_glyphs(
            header_glyph_alignment,
            accent_colour,
            header_glyph_gap,
            header_glyph_height,
            (header_glyph_left_padding, header_glyph_right_padding),
            header_height,
        )

        image = Image.alpha_composite(image, header_glyphs_image)

        if clock_format == "12 Hour":
            time_text = current_time.strftime("%I:%M %p")
        else:
            time_text = current_time.strftime("%H:%M")

        time_text_bbox = header_font.getbbox(time_text)
        time_text_width = time_text_bbox[2] - time_text_bbox[0]
        if header_clock_alignment == "Left":
            header_clock_x_pos = header_clock_left_padding
        elif header_clock_alignment == "Centre":
            header_clock_x_pos = (
                int(
                    self.scaled_screen_dimensions[0] / 2
                    - (
                        (
                            time_text_width
                            + (header_clock_right_padding + header_clock_left_padding)
                        )
                        / 2
                    )
                )
                + header_clock_left_padding
            )
        elif header_clock_alignment == "Right":
            header_clock_x_pos = int(self.scaled_screen_dimensions[0]) - (
                time_text_width + header_clock_right_padding
            )
        else:
            raise ValueError("Invalid clock alignment")
        header_clock_y_pos = (
            int((header_height / 2) - (header_text_height / 2)) - time_text_bbox[1]
        )

        draw = ImageDraw.Draw(image)
        draw.text(
            (header_clock_x_pos, header_clock_y_pos),
            time_text,
            font=header_font,
            fill=(*ImageColor.getrgb(f"#{accent_colour}"), 255),
        )

        if self.manager.show_console_name_var:
            header_page_title_padding = (
                int(self.manager.pageTitlePaddingVar) * self.render_factor
            )
            header_page_title_alignment = self.manager.page_title_alignment_var

            page_title = muOSpageNameDict.get(muOSpageName, "UNKNOWN")
            page_title_bbox = header_font.getbbox(page_title)
            page_title_width = page_title_bbox[2] - page_title_bbox[0]

            if header_page_title_alignment == "Left":
                header_page_title_x_pos = header_page_title_padding
            elif header_page_title_alignment == "Centre":
                header_page_title_x_pos = int(
                    self.scaled_screen_dimensions[0] / 2 - (page_title_width / 2)
                )
            elif header_page_title_alignment == "Right":
                header_page_title_x_pos = (
                    self.scaled_screen_dimensions[0]
                    - page_title_width
                    + header_page_title_padding
                )
            else:
                raise ValueError("Invalid page title alignment")

            header_page_title_y_pos = (
                int((header_height / 2) - (header_text_height / 2)) - page_title_bbox[1]
            )
            draw.text(
                (header_page_title_x_pos, header_page_title_y_pos),
                page_title,
                font=header_font,
                fill=(*ImageColor.getrgb(f"#{accent_colour}"), 255),
            )

        return image

    def generate_header_overlay_image(
        self,
        accent_colour: str | None = None,
        bubble_alpha: float = 0.133,
        muOSpageName: str = "muxlaunch",
    ) -> Image.Image:
        image = self.generate_background_image(transparent=True)

        bubbles_image = super().generate_header_overlay_image(
            accent_colour, bubble_alpha, muOSpageName
        )
        preview_image = self._generate_header_preview_image(muOSpageName)

        image = Image.alpha_composite(image, bubbles_image)
        image = Image.alpha_composite(image, preview_image)

        return image

    def generate_static_overlay_image(
        self,
        rhsButtons: list[tuple[str, str]],
        selected_font_path: Path,
        colour_hex: str,
        lhsButtons: list[tuple[str, str]] = [("POWER", "SLEEP")],
        muOSpageName: str = "muxlaunch",
    ) -> Image.Image:
        return super().generate_static_overlay_image(
            rhsButtons,
            selected_font_path,
            colour_hex,
            lhsButtons,
            muOSpageName=muOSpageName,
        )

    def generate_theme(self):
        raise NotImplementedError("PreviewThemeGenerator only generates previews!")
