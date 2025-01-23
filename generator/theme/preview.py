from datetime import datetime
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont

from generator.color_utils import change_logo_color
from generator.constants import GLYPHS_DIR, BatteryStyleOptionsDict, BatteryChargingStyleOptionsDict
from generator.font import get_font_path
from generator.settings import SettingsManager
from generator.theme.base import BaseThemeGenerator


class PreviewThemeGenerator(BaseThemeGenerator):
    def __init__(self, manager: SettingsManager, render_factor: int):
        super().__init__(manager, render_factor)

    def generate_header_overlay_image(
        self,
        accent_colour: str | None = None,
        bubble_alpha: float = 0.133,
        muOSpageName: str = "muxlaunch",
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
        image = Image.new(
            "RGBA",
            (
                int(self.manager.deviceScreenWidthVar) * self.render_factor,
                int(self.manager.deviceScreenHeightVar) * self.render_factor,
            ),
            (255, 255, 255, 0),
        )
        draw = ImageDraw.Draw(image)
        if float(self.manager.header_glyph_height_var) < 10:
            raise ValueError("Header Glyph Height Too Small!")
        elif float(self.manager.header_glyph_height_var) > int(self.manager.headerHeightVar):
            raise ValueError("Header Glyph Height Too Large!")
        else:
            heightOfGlyph = int(float(self.manager.header_glyph_height_var) * self.render_factor)
        accent_colour = self.manager.deselectedFontHexVar
        if accent_colour.startswith("#"):
            accent_colour = accent_colour[1:]
        if "showing battery and network":
            glyphYPos = int(
                ((int(self.manager.headerHeightVar) * self.render_factor) / 2) - (heightOfGlyph / 2)
            )

            # Battery not charging stuff
            capacityGlyph = "30"
            capacity_image_path = (
                GLYPHS_DIR
                / f"{BatteryStyleOptionsDict[self.manager.battery_style_var]}{capacityGlyph}[5x].png"
            )

            capacity_image_coloured = change_logo_color(capacity_image_path, accent_colour)
            capacity_image_coloured = capacity_image_coloured.resize(
                (
                    int(
                        heightOfGlyph
                        * (
                            capacity_image_coloured.size[0]
                            / capacity_image_coloured.size[1]
                        )
                    ),
                    heightOfGlyph,
                ),
                Image.LANCZOS,
            )

            capacityChargingGlyph = "30"
            capacity_charging_image_path = (
                GLYPHS_DIR
                / f"{BatteryChargingStyleOptionsDict[self.manager.battery_charging_style_var]}{capacityChargingGlyph}[5x].png"
            )

            capacity_charging_image_coloured = change_logo_color(
                capacity_charging_image_path, self.manager.batteryChargingHexVar
            )
            capacity_charging_image_coloured = capacity_charging_image_coloured.resize(
                (
                    int(
                        heightOfGlyph
                        * (
                            capacity_charging_image_coloured.size[0]
                            / capacity_charging_image_coloured.size[1]
                        )
                    ),
                    heightOfGlyph,
                ),
                Image.LANCZOS,
            )

            networkGlyph = "network_active"
            network_image_path = GLYPHS_DIR / f"{networkGlyph}[5x].png"

            network_image_coloured = change_logo_color(network_image_path, accent_colour)
            network_image_coloured = network_image_coloured.resize(
                (
                    int(
                        heightOfGlyph
                        * (network_image_coloured.size[0] / network_image_coloured.size[1])
                    ),
                    heightOfGlyph,
                ),
                Image.LANCZOS,
            )

            glyph_left_side_padding = int(self.manager.header_glyph_horizontal_left_padding_var)
            glyph_right_side_padding = int(
                self.manager.header_glyph_horizontal_right_padding_var
            )
            glyph_between_padding = 5

            totalGlyphWidth = (
                capacity_image_coloured.size[0]
                + glyph_between_padding * self.render_factor
                + network_image_coloured.size[0]
            )
            if self.manager.header_glyph_alignment_var == "Left":
                current_x_pos = glyph_left_side_padding * self.render_factor
            elif self.manager.header_glyph_alignment_var == "Centre":
                current_x_pos = (
                    int(
                        (int(self.manager.deviceScreenWidthVar) * self.render_factor) / 2
                        - (
                            (
                                totalGlyphWidth
                                + (
                                    glyph_right_side_padding * self.render_factor
                                    + glyph_left_side_padding * self.render_factor
                                )
                            )
                            / 2
                        )
                    )
                    + glyph_left_side_padding * self.render_factor
                )
            elif self.manager.header_glyph_alignment_var == "Right":
                current_x_pos = int(
                    int(self.manager.deviceScreenWidthVar) * self.render_factor
                    - (glyph_right_side_padding * self.render_factor + totalGlyphWidth)
                )
            else:
                raise ValueError("Invalid clock alignment")

            image.paste(
                network_image_coloured, (current_x_pos, glyphYPos), network_image_coloured
            )

            current_x_pos += (
                network_image_coloured.size[0] + glyph_between_padding * self.render_factor
            )

            if not self.manager.show_charging_battery_var:
                image.paste(
                    capacity_image_coloured,
                    (current_x_pos, glyphYPos),
                    capacity_image_coloured,
                )

            if self.manager.show_charging_battery_var:
                image.paste(
                    capacity_charging_image_coloured,
                    (current_x_pos, glyphYPos),
                    capacity_charging_image_coloured,
                )

        if int(self.manager.header_text_height_var) < 10:
            raise ValueError("Header Text Height Too Small!")
        elif int(self.manager.header_text_height_var) > int(self.manager.headerHeightVar):
            raise ValueError("Header Text Height Too Large!")
        else:
            heightOfText = int(int(self.manager.header_text_height_var) * self.render_factor)

        fontSize = int(
            int((heightOfText * (4 / 3)) / self.render_factor) * self.render_factor
        )  ## TODO Make this not specific to BPreplay
        headerFont = ImageFont.truetype(
            get_font_path(self.manager.use_alt_font_var, self.manager.alt_font_filename),
            fontSize,
        )
        if "showing time":
            clock_left_padding = int(self.manager.clockHorizontalLeftPaddingVar)
            clock_right_padding = int(self.manager.clockHorizontalRightPaddingVar)

            if self.manager.clock_format_var == "12 Hour":
                timeText = current_time.strftime("%I:%M %p")
            else:
                timeText = current_time.strftime("%H:%M")

            timeTextBbox = headerFont.getbbox(timeText)
            timeTextWidth = timeTextBbox[2] - timeTextBbox[0]
            if self.manager.clock_alignment_var == "Left":
                timeText_X = clock_left_padding * self.render_factor
            elif self.manager.clock_alignment_var == "Centre":
                timeText_X = (
                    int(
                        (int(self.manager.deviceScreenWidthVar) * self.render_factor) / 2
                        - (
                            (
                                timeTextWidth
                                + (
                                    clock_right_padding * self.render_factor
                                    + clock_left_padding * self.render_factor
                                )
                            )
                            / 2
                        )
                    )
                    + clock_left_padding * self.render_factor
                )
            elif self.manager.clock_alignment_var == "Right":
                timeText_X = int(int(self.manager.deviceScreenWidthVar) * self.render_factor) - (
                    timeTextWidth + clock_right_padding * self.render_factor
                )
            else:
                raise ValueError("Invalid clock alignment")
            timeText_Y = (
                int(
                    ((int(self.manager.headerHeightVar) * self.render_factor) / 2)
                    - (heightOfText / 2)
                )
                - timeTextBbox[1]
            )
            draw.text(
                (timeText_X, timeText_Y),
                timeText,
                font=headerFont,
                fill=(*ImageColor.getrgb(f"#{accent_colour}"), 255),
            )
        if self.manager.show_console_name_var:
            page_title_padding = int(self.manager.pageTitlePaddingVar)
            pageTitle = muOSpageNameDict.get(muOSpageName, "UNKNOWN")
            pageTitleBbox = headerFont.getbbox(pageTitle)
            pageTitleWidth = pageTitleBbox[2] - pageTitleBbox[0]
            if self.manager.page_title_alignment_var == "Left":
                pageTitle_X = page_title_padding * self.render_factor
            elif self.manager.page_title_alignment_var == "Centre":
                pageTitle_X = int(
                    (int(self.manager.deviceScreenWidthVar) * self.render_factor) / 2
                    - (pageTitleWidth / 2)
                )
            elif self.manager.page_title_alignment_var == "Right":
                pageTitle_X = int(int(self.manager.deviceScreenWidthVar) * self.render_factor) - (
                    pageTitleWidth + page_title_padding * self.render_factor
                )
            else:
                raise ValueError("Invalid page title alignment")
            pageTitle_Y = (
                int(
                    ((int(self.manager.headerHeightVar) * self.render_factor) / 2)
                    - (heightOfText / 2)
                )
                - pageTitleBbox[1]
            )
            draw.text(
                (pageTitle_X, pageTitle_Y),
                pageTitle,
                font=headerFont,
                fill=(*ImageColor.getrgb(f"#{accent_colour}"), 255),
            )

        return image

    def generate_static_overlay_image(
        self,
        rhsButtons: list[tuple[str, str]],
        selected_font_path: Path,
        colour_hex: str,
        lhsButtons: list[tuple[str, str]] = [("POWER", "SLEEP")],
        muOSpageName: str = "muxlaunch",
    ) -> Image.Image:
        return self.generate_static_overlay_image(rhsButtons,selected_font_path, colour_hex,lhsButtons,muOSpageName=muOSpageName)

    def generate_theme(self):
        raise NotImplementedError("PreviewThemeGenerator only generates previews!")
