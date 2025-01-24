import math
from pathlib import Path

try:  # try to use the Rust-based package if possible
    from bidi import get_display as bidi_get_display
except ImportError:  # otherwise use the Python-based package
    from bidi.algorithm import get_display as bidi_get_display

from PIL import Image, ImageColor, ImageDraw, ImageFont

from generator.color_utils import hex_to_rgba, change_logo_color
from generator.constants import (
    BUTTON_GLYPHS_DIR,
    GLYPHS_DIR,
)
from generator.font import get_font_path
from generator.settings import SettingsManager
from generator.utils import get_max_length_time_string


class BaseThemeGenerator:
    def __init__(self, manager: SettingsManager, render_factor: int):
        self.manager = manager
        self.render_factor = render_factor

    def generate_button_glyph_image(
        self,
        buttonText: str,
        selected_font_path: Path,
        colour_hex: str,
        button_height: int = 0,
        physical_controller_layout: str = "Nintendo",
    ) -> Image.Image:
        if colour_hex.startswith("#"):
            colour_hex = colour_hex[1:]

        in_smaller_bubble_font_size = button_height * (20.1 / 40) * self.render_factor
        inSmallerBubbleFont = ImageFont.truetype(
            selected_font_path, in_smaller_bubble_font_size
        )

        single_letter_font_size = button_height * (28 / 40) * self.render_factor
        singleLetterFont = ImageFont.truetype(
            selected_font_path, single_letter_font_size
        )

        isb_text_bbox = inSmallerBubbleFont.getbbox(buttonText)
        isb_text_height = isb_text_bbox[3] - isb_text_bbox[1]
        in_smaller_bubble_text_y = (
            ((button_height * self.render_factor) / 2)
            - (isb_text_height / 2)
            - isb_text_bbox[1]
        )

        sl_text_bbox = singleLetterFont.getbbox(buttonText)
        sl_text_height = sl_text_bbox[3] - sl_text_bbox[1]
        single_letter_text_y = (
            ((button_height * self.render_factor) / 2)
            - (sl_text_height / 2)
            - sl_text_bbox[1]
        )

        horizontal_small_padding = button_height * (10 / 40)

        rendered_bubble_height = int(button_height * self.render_factor)

        if buttonText.upper() in [
            "A",
            "B",
            "X",
            "Y",
        ] and physical_controller_layout in [
            "PlayStation",
            "Xbox",
            "Universal",
        ]:
            buttonSize = (rendered_bubble_height, rendered_bubble_height)
            if physical_controller_layout == "PlayStation":
                image = (
                    Image.open(
                        BUTTON_GLYPHS_DIR / "PlayStation" / f"{buttonText.upper()}.png"
                    )
                    .convert("RGBA")
                    .resize(buttonSize, Image.LANCZOS)
                )
            elif physical_controller_layout == "Universal":
                image = (
                    Image.open(
                        BUTTON_GLYPHS_DIR / "Universal" / f"{buttonText.upper()}.png"
                    )
                    .convert("RGBA")
                    .resize(buttonSize, Image.LANCZOS)
                )
            elif physical_controller_layout == "Xbox":
                if buttonText.upper() == "A":
                    image = self.generate_button_glyph_image(
                        "B",
                        selected_font_path,
                        colour_hex,
                        button_height,
                        "Nintendo",
                    )
                elif buttonText.upper() == "B":
                    image = self.generate_button_glyph_image(
                        "A",
                        selected_font_path,
                        colour_hex,
                        button_height,
                        "Nintendo",
                    )
                elif buttonText.upper() == "X":
                    image = self.generate_button_glyph_image(
                        "Y",
                        selected_font_path,
                        colour_hex,
                        button_height,
                        "Nintendo",
                    )
                elif buttonText.upper() == "Y":
                    image = self.generate_button_glyph_image(
                        "X",
                        selected_font_path,
                        colour_hex,
                        button_height,
                        "Nintendo",
                    )

        elif len(buttonText) == 1:
            image = Image.new(
                "RGBA",
                (rendered_bubble_height, rendered_bubble_height),
                (255, 255, 255, 0),
            )
            draw = ImageDraw.Draw(image)

            circleCentreX = (rendered_bubble_height) / 2
            draw.ellipse(
                (0, 0, rendered_bubble_height, rendered_bubble_height),
                fill=f"#{colour_hex}",
            )
            singleLetterWidth = sl_text_bbox[2] - sl_text_bbox[0]
            smallerTextX = circleCentreX - (singleLetterWidth / 2)
            draw.text(
                (smallerTextX, single_letter_text_y),
                buttonText,
                font=singleLetterFont,
                fill=(*ImageColor.getrgb(f"#{colour_hex}"), int(255 * 0.593)),
            )

        else:
            ## Make the smaller bubble
            smallerTextBbox = inSmallerBubbleFont.getbbox(buttonText)
            smallerTextWidth = smallerTextBbox[2] - smallerTextBbox[0]
            smallerBubbleWidth = int(
                horizontal_small_padding
                + smallerTextWidth / self.render_factor
                + horizontal_small_padding
            )

            rendered_smallerBubbleWidth = int(smallerBubbleWidth * self.render_factor)

            image = Image.new(
                "RGBA",
                (rendered_smallerBubbleWidth, rendered_bubble_height),
                (255, 255, 255, 0),
            )
            draw = ImageDraw.Draw(image)

            draw.rounded_rectangle(
                [
                    (0, 0),  # bottom left point
                    (rendered_smallerBubbleWidth, rendered_bubble_height),
                ],  # Top right point
                radius=(math.ceil(button_height / 2)) * self.render_factor,
                fill=hex_to_rgba(colour_hex, alpha=1),
            )
            smallerTextX = horizontal_small_padding * self.render_factor
            draw.text(
                (smallerTextX, in_smaller_bubble_text_y),
                buttonText,
                font=inSmallerBubbleFont,
                fill=(*ImageColor.getrgb(f"#{colour_hex}"), int(255 * 0.593)),
            )
        return image

    def generate_header_overlay_image(
        self,
        accent_colour: str | None = None,
        bubble_alpha: float = 0.133,
        *args,
        **kwargs,
    ) -> Image.Image:
        image = Image.new(
            "RGBA",
            (
                int(self.manager.deviceScreenWidthVar) * self.render_factor,
                int(self.manager.deviceScreenHeightVar) * self.render_factor,
            ),
            (255, 255, 255, 0),
        )
        draw = ImageDraw.Draw(image)
        if accent_colour is None:
            accent_colour = self.manager.deselectedFontHexVar
        if accent_colour.startswith("#"):
            accent_colour = accent_colour[1:]

        if int(self.manager.header_text_height_var) < 10:
            raise ValueError("Header Text Height Too Small!")
        elif int(self.manager.header_text_height_var) > int(
            self.manager.headerHeightVar
        ):
            raise ValueError("Header Text Height Too Large!")
        else:
            heightOfText = int(
                int(self.manager.header_text_height_var) * self.render_factor
            )

        fontHeight = int(
            int((heightOfText * (4 / 3)) / self.render_factor) * self.render_factor
        )  ## TODO Make this not specific to BPreplay
        headerFont = ImageFont.truetype(
            get_font_path(
                self.manager.use_alt_font_var, self.manager.alt_font_filename
            ),
            fontHeight,
        )

        if (
            int(self.manager.header_text_bubble_height_var)
            - int(self.manager.header_text_height_var)
            >= 0
        ):
            headerTextPadding = int(
                (
                    int(self.manager.header_text_bubble_height_var)
                    - int(self.manager.header_text_height_var)
                )
                / 2
            )
        else:
            raise ValueError("Header Glyph Height Too Large!")

        headerMiddleY = (int(self.manager.headerHeightVar) * self.render_factor) / 2

        bottom_y_points = {}
        top_y_points = {}
        left_x_points = {}
        right_x_points = {}

        if self.manager.show_clock_bubbles_var:
            clock_left_padding = int(self.manager.clockHorizontalLeftPaddingVar)
            clock_right_padding = int(self.manager.clockHorizontalRightPaddingVar)

            timeText = get_max_length_time_string(
                headerFont,
                self.manager.clock_format_var,
            )
            maxTimeTextWidth = (
                headerFont.getbbox(timeText)[2] - headerFont.getbbox(timeText)[0]
            )

            if self.manager.clock_alignment_var == "Left":
                timeText_X = clock_left_padding * self.render_factor
            elif self.manager.clock_alignment_var == "Centre":
                timeText_X = (
                    int(
                        (int(self.manager.deviceScreenWidthVar) * self.render_factor)
                        / 2
                        - (
                            (
                                maxTimeTextWidth
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
                timeText_X = int(
                    int(self.manager.deviceScreenWidthVar) * self.render_factor
                ) - (maxTimeTextWidth + clock_right_padding * self.render_factor)
            else:
                raise ValueError("Invalid clock alignment")

            bottom_y_points["clock"] = headerMiddleY - (
                (int(self.manager.header_text_bubble_height_var) * self.render_factor)
                / 2
            )
            top_y_points["clock"] = headerMiddleY + (
                (int(self.manager.header_text_bubble_height_var) * self.render_factor)
                / 2
            )
            left_x_points["clock"] = timeText_X - (
                headerTextPadding * self.render_factor
            )
            right_x_points["clock"] = (
                timeText_X + maxTimeTextWidth + (headerTextPadding * self.render_factor)
            )

        if float(self.manager.header_glyph_height_var) < 10:
            raise ValueError("Header Glyph Height Too Small!")
        elif float(self.manager.header_glyph_height_var) > int(
            self.manager.headerHeightVar
        ):
            raise ValueError("Header Glyph Height Too Large!")
        else:
            heightOfGlyph = int(
                float(self.manager.header_glyph_height_var) * self.render_factor
            )

        if (
            int(self.manager.header_glyph_bubble_height_var)
            - int(self.manager.header_glyph_height_var)
            >= 0
        ):
            headerGlyphPadding = int(
                (
                    int(self.manager.header_glyph_bubble_height_var)
                    - int(self.manager.header_glyph_height_var)
                )
                / 2
            )
        else:
            raise ValueError("Header Glyph Height Too Large!")
        if self.manager.show_glyphs_bubbles_var:
            # Battery not charging stuff
            capacityGlyph = "capacity_30.png"
            capacity_image_path = GLYPHS_DIR / f"{capacityGlyph[:-4]}[5x].png"

            capacity_image_coloured = change_logo_color(
                capacity_image_path, accent_colour
            )
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
            glyph_left_side_padding = int(
                self.manager.header_glyph_horizontal_left_padding_var
            )
            glyph_right_side_padding = int(
                self.manager.header_glyph_horizontal_right_padding_var
            )
            glyph_between_padding = 5

            networkGlyph = "network_active"
            network_image_path = GLYPHS_DIR / f"{networkGlyph}[5x].png"

            network_image_coloured = change_logo_color(
                network_image_path, accent_colour
            )
            network_image_coloured = network_image_coloured.resize(
                (
                    int(
                        heightOfGlyph
                        * (
                            network_image_coloured.size[0]
                            / network_image_coloured.size[1]
                        )
                    ),
                    heightOfGlyph,
                ),
                Image.LANCZOS,
            )

            glyphTotalWidth = (
                capacity_image_coloured.size[0]
                + glyph_between_padding * self.render_factor
                + network_image_coloured.size[0]
            )

            if self.manager.header_glyph_alignment_var == "Left":
                current_x_pos = glyph_left_side_padding * self.render_factor
            elif self.manager.header_glyph_alignment_var == "Centre":
                current_x_pos = (
                    int(
                        (int(self.manager.deviceScreenWidthVar) * self.render_factor)
                        / 2
                        - (
                            (
                                glyphTotalWidth
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
                    - (glyph_right_side_padding * self.render_factor + glyphTotalWidth)
                )
            else:
                raise ValueError("Invalid clock alignment")

            glyphBubbleXPos = int(
                int(self.manager.deviceScreenWidthVar) * self.render_factor
            ) - (glyphTotalWidth + glyph_left_side_padding * self.render_factor)

            bottom_y_points["glyphs"] = headerMiddleY - (
                (int(self.manager.header_glyph_bubble_height_var) * self.render_factor)
                / 2
            )
            top_y_points["glyphs"] = headerMiddleY + (
                (int(self.manager.header_glyph_bubble_height_var) * self.render_factor)
                / 2
            )
            left_x_points["glyphs"] = current_x_pos - (
                headerGlyphPadding * self.render_factor
            )
            right_x_points["glyphs"] = (
                current_x_pos
                + glyphTotalWidth
                + (headerGlyphPadding * self.render_factor)
            )

        if self.manager.join_header_bubbles_var and (
            self.manager.show_glyphs_bubbles_var or self.manager.show_clock_bubbles_var
        ):
            bottom_y = min(bottom_y_points.values())
            top_y = max(top_y_points.values())
            left_x = min(left_x_points.values())
            right_x = max(right_x_points.values())

            draw.rounded_rectangle(
                [
                    (left_x, bottom_y),  # bottom left point
                    (right_x, top_y),
                ],  # Top right point
                radius=math.ceil((top_y - bottom_y) / 2),
                fill=hex_to_rgba(accent_colour, alpha=bubble_alpha),
            )
        else:
            for key in bottom_y_points.keys():
                draw.rounded_rectangle(
                    [
                        (left_x_points[key], bottom_y_points[key]),  # bottom left point
                        (right_x_points[key], top_y_points[key]),
                    ],  # Top right point
                    radius=math.ceil((top_y_points[key] - bottom_y_points[key]) / 2),
                    fill=hex_to_rgba(accent_colour, alpha=bubble_alpha),
                )

        return image

    def generate_footer_overlay_image(
        self,
        retro_rhs_buttons: list[tuple[str, str]],
        selected_font_path: Path,
        colour_hex: str,
        lhsButtons: list[tuple[str, str]] = [("POWER", "SLEEP")],
    ) -> Image.Image:
        if colour_hex.startswith("#"):
            colour_hex = colour_hex[1:]

        image = Image.new(
            "RGBA",
            (
                int(self.manager.deviceScreenWidthVar) * self.render_factor,
                int(self.manager.deviceScreenHeightVar) * self.render_factor,
            ),
            (255, 255, 255, 0),
        )
        draw = ImageDraw.Draw(image)

        real_rhs_buttons = []

        if self.manager.muos_button_swap_var == "Modern":
            for pair in retro_rhs_buttons:
                if pair[0].upper() == "A":
                    real_rhs_buttons.append(["B", pair[1]])
                elif pair[0].upper() == "B":
                    real_rhs_buttons.append(["A", pair[1]])
                elif pair[0].upper() == "X":
                    real_rhs_buttons.append(["Y", pair[1]])
                elif pair[0].upper() == "Y":
                    real_rhs_buttons.append(["X", pair[1]])
        else:
            real_rhs_buttons = retro_rhs_buttons

        if not (
            self.manager.remove_left_menu_guides_var
            and self.manager.remove_right_menu_guides_var
        ):
            required_padding_between_sides = 15  # This is the maximum space between the two sides of the menu helper guides
            lhsTotalWidth = 0
            rhsTotalWidth = int(self.manager.deviceScreenWidthVar)
            iterations = 0
            from_sides_padding = int(self.manager.VBG_Horizontal_Padding_var)
            remove_left_menu_guides_var = self.manager.remove_left_menu_guides_var
            remove_right_menu_guides_var = self.manager.remove_right_menu_guides_var
            if remove_left_menu_guides_var or remove_right_menu_guides_var:
                required_padding_between_sides = 0
            while (
                from_sides_padding
                + lhsTotalWidth
                + required_padding_between_sides
                + rhsTotalWidth
                + from_sides_padding
                > int(self.manager.deviceScreenWidthVar)
            ):
                if iterations == 0:
                    from_sides_padding = int(self.manager.VBG_Horizontal_Padding_var)
                if False:  # TODO an option for this
                    remove_left_menu_guides_var = True
                    required_padding_between_sides = 0
                from_bottom_padding = (
                    int(self.manager.VBG_Vertical_Padding_var) + iterations
                )

                individualItemHeight = round(
                    (
                        int(self.manager.deviceScreenHeightVar)
                        - int(self.manager.approxFooterHeightVar)
                        - int(self.manager.contentPaddingTopVar)
                    )
                    / int(self.manager.itemsPerScreenVar)
                )

                muosSpaceBetweenItems = 2

                footerHeight = (
                    int(self.manager.deviceScreenHeightVar)
                    - (individualItemHeight * int(self.manager.itemsPerScreenVar))
                    - int(self.manager.contentPaddingTopVar)
                    + muosSpaceBetweenItems
                )

                menu_helper_guide_height = footerHeight - (
                    from_bottom_padding * 2
                )  # Change this if overlayed

                in_smaller_bubble_font_size = (
                    menu_helper_guide_height * (20.1 / 60) * self.render_factor
                )
                inSmallerBubbleFont = ImageFont.truetype(
                    selected_font_path,
                    in_smaller_bubble_font_size,
                )

                in_bubble_font_size = (
                    menu_helper_guide_height * (24 / 60) * self.render_factor
                )
                inBubbleFont = ImageFont.truetype(
                    selected_font_path, in_bubble_font_size
                )

                single_letter_font_size = (
                    menu_helper_guide_height * (28 / 60) * self.render_factor
                )
                singleLetterFont = ImageFont.truetype(
                    selected_font_path, single_letter_font_size
                )

                horizontal_small_padding = menu_helper_guide_height * (10 / 60)
                horizontal_padding = menu_helper_guide_height * (10 / 60)
                horizontal_large_padding = menu_helper_guide_height * (
                    20 / 60
                )  # Testing here

                bottom_guide_middle_y = (
                    int(self.manager.deviceScreenHeightVar)
                    - from_bottom_padding
                    - (menu_helper_guide_height / 2)
                )

                guide_small_bubble_height = menu_helper_guide_height - (
                    horizontal_padding * 2
                )

                isb_ascent, isb_descent = inSmallerBubbleFont.getmetrics()
                isb_text_height = isb_ascent + isb_descent
                in_smaller_bubble_text_y = (
                    bottom_guide_middle_y * self.render_factor - (isb_text_height / 2)
                )

                ib_ascent, ib_descent = inBubbleFont.getmetrics()
                ib_text_height = ib_ascent + ib_descent
                in_bubble_text_y = bottom_guide_middle_y * self.render_factor - (
                    ib_text_height / 2
                )

                sl_text_bbox = singleLetterFont.getbbox("ABXY")
                sl_text_height = sl_text_bbox[3] - sl_text_bbox[1]
                single_letter_text_y = (
                    bottom_guide_middle_y * self.render_factor
                    - (sl_text_height / 2)
                    - sl_text_bbox[1]
                )

                ##TODO convert buttons at this point to lanuage of choice in their respective arrays

                combined_width = 0
                lhsTotalWidth = 0
                rhsTotalWidth = 0

                if not remove_left_menu_guides_var:
                    lhsTotalWidth += self._get_total_bubble_width(
                        lhsButtons,
                        inSmallerBubbleFont,
                        inBubbleFont,
                        horizontal_padding,
                        horizontal_large_padding,
                        horizontal_small_padding,
                        guide_small_bubble_height,
                    )
                    combined_width += lhsTotalWidth

                if not remove_right_menu_guides_var:
                    rhsTotalWidth += self._get_total_bubble_width(
                        real_rhs_buttons,
                        inSmallerBubbleFont,
                        inBubbleFont,
                        horizontal_padding,
                        horizontal_large_padding,
                        horizontal_small_padding,
                        guide_small_bubble_height,
                    )
                    combined_width += rhsTotalWidth
                iterations += 1

            if not remove_left_menu_guides_var:
                realLhsPointer = from_sides_padding * self.render_factor
                ## Make the main long bubble
                draw.rounded_rectangle(
                    [
                        (
                            realLhsPointer,
                            (bottom_guide_middle_y - menu_helper_guide_height / 2)
                            * self.render_factor,
                        ),  # bottom left point
                        (
                            realLhsPointer + (lhsTotalWidth * self.render_factor),
                            (bottom_guide_middle_y + menu_helper_guide_height / 2)
                            * self.render_factor,
                        ),
                    ],  # Top right point
                    radius=(menu_helper_guide_height / 2) * self.render_factor,
                    fill=hex_to_rgba(colour_hex, alpha=0.133),
                )
                realLhsPointer += horizontal_padding * self.render_factor
                for pair in lhsButtons:
                    button_image = self.generate_button_glyph_image(
                        pair[0],
                        selected_font_path,
                        colour_hex,
                        guide_small_bubble_height,
                        self.manager.physical_controller_layout_var,
                    )
                    button_image = change_logo_color(button_image, colour_hex)
                    image.paste(
                        button_image,
                        (
                            int(realLhsPointer),
                            int(
                                bottom_guide_middle_y * self.render_factor
                                - (button_image.size[1] / 2)
                            ),
                        ),
                        button_image,
                    )
                    realLhsPointer += (
                        (button_image.size[0])
                        + (horizontal_small_padding) * self.render_factor
                    )

                    textBbox = inBubbleFont.getbbox(pair[1])
                    textWidth = textBbox[2] - textBbox[0]
                    draw.text(
                        (realLhsPointer, in_bubble_text_y),
                        pair[1],
                        font=inBubbleFont,
                        fill=f"#{colour_hex}",
                    )
                    realLhsPointer += textWidth
                    realLhsPointer += horizontal_large_padding * self.render_factor
            if not remove_right_menu_guides_var:
                realRhsPointer = (
                    int(self.manager.deviceScreenWidthVar)
                    - from_sides_padding
                    - rhsTotalWidth
                ) * self.render_factor
                ## Make the main long bubble
                draw.rounded_rectangle(
                    [
                        (
                            realRhsPointer,
                            (bottom_guide_middle_y - menu_helper_guide_height / 2)
                            * self.render_factor,
                        ),  # bottom left point
                        (
                            realRhsPointer + (rhsTotalWidth * self.render_factor),
                            (bottom_guide_middle_y + menu_helper_guide_height / 2)
                            * self.render_factor,
                        ),
                    ],  # Top right point
                    radius=(menu_helper_guide_height / 2) * self.render_factor,
                    fill=hex_to_rgba(colour_hex, alpha=0.133),
                )
                realRhsPointer += horizontal_padding * self.render_factor
                for pair in real_rhs_buttons:
                    button_image = self.generate_button_glyph_image(
                        pair[0],
                        selected_font_path,
                        colour_hex,
                        guide_small_bubble_height,
                        self.manager.physical_controller_layout_var,
                    )
                    button_image = change_logo_color(button_image, colour_hex)

                    image.paste(
                        button_image,
                        (
                            int(realRhsPointer),
                            int(
                                bottom_guide_middle_y * self.render_factor
                                - (button_image.size[1] / 2)
                            ),
                        ),
                        button_image,
                    )
                    realRhsPointer += (
                        (button_image.size[0])
                        + (horizontal_small_padding) * self.render_factor
                    )

                    textBbox = inBubbleFont.getbbox(pair[1])
                    textWidth = textBbox[2] - textBbox[0]
                    draw.text(
                        (realRhsPointer, in_bubble_text_y),
                        pair[1],
                        font=inBubbleFont,
                        fill=f"#{colour_hex}",
                    )
                    realRhsPointer += textWidth
                    realRhsPointer += horizontal_large_padding * self.render_factor
        return image

    def generate_background_image(self) -> Image.Image:
        pass

    def generate_wall_image(self) -> Image.Image:
        pass

    def generate_static_overlay_image(
        self,
        rhsButtons: list[tuple[str, str]],
        selected_font_path: Path,
        colour_hex: str,
        lhsButtons: list[tuple[str, str]] = [("POWER", "SLEEP")],
        *args,
        **kwargs,
    ) -> Image.Image:
        if colour_hex.startswith("#"):
            colour_hex = colour_hex[1:]

        image = Image.new(
            "RGBA",
            (
                int(self.manager.deviceScreenWidthVar) * self.render_factor,
                int(self.manager.deviceScreenHeightVar) * self.render_factor,
            ),
            (255, 255, 255, 0),
        )
        draw = ImageDraw.Draw(image)

        menuHelperGuides = self.generate_footer_overlay_image(
            rhsButtons,
            selected_font_path,
            colour_hex,
            lhsButtons=lhsButtons,
        )

        image = Image.alpha_composite(image, menuHelperGuides)
        headerBubbles = self.generate_header_overlay_image(*args, **kwargs)

        image = Image.alpha_composite(image, headerBubbles)

        return image

    def generate_boot_screen_with_logo(
        self,
        bg_hex: str,
        deselected_font_hex: str,
        bubble_hex: str,
    ) -> Image.Image:
        (
            bg_hex,
            deselected_font_hex,
            bubble_hex,
        ) = [
            val[1:] if val.startswith("#") else val
            for val in [
                bg_hex,
                deselected_font_hex,
                bubble_hex,
            ]
        ]

        bg_rgb = hex_to_rgba(bg_hex)
        image = Image.new(
            "RGBA",
            (
                int(self.manager.deviceScreenWidthVar) * self.render_factor,
                int(self.manager.deviceScreenHeightVar) * self.render_factor,
            ),
            bg_rgb,
        )
        if self.manager.use_custom_bootlogo_var:
            if (
                self.manager.bootlogo_image_path
                and self.manager.bootlogo_image_path.exists()
            ):
                bootlogo_image = Image.open(self.manager.bootlogo_image_path)
                image.paste(
                    bootlogo_image.resize(
                        (
                            int(self.manager.deviceScreenWidthVar) * self.render_factor,
                            int(self.manager.deviceScreenHeightVar)
                            * self.render_factor,
                        )
                    ),
                    (0, 0),
                )
                return image
        elif background_image != None:
            image.paste(
                background_image.resize(
                    (
                        int(self.manager.deviceScreenWidthVar) * self.render_factor,
                        int(self.manager.deviceScreenHeightVar) * self.render_factor,
                    )
                ),
                (0, 0),
            )

        draw = ImageDraw.Draw(image)
        transparent_text_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw_transparent = ImageDraw.Draw(transparent_text_image)

        selected_font_path = get_font_path(
            self.manager.use_alt_font_var, self.manager.alt_font_filename
        )

        mu_font_size = 130 * self.render_factor
        mu_font = ImageFont.truetype(selected_font_path, mu_font_size)
        os_font_size = 98 * self.render_factor
        os_font = ImageFont.truetype(selected_font_path, os_font_size)

        screen_x_middle, screen_y_middle = (
            (int(self.manager.deviceScreenWidthVar) / 2) * self.render_factor,
            (int(self.manager.deviceScreenHeightVar) / 2) * self.render_factor,
        )

        from_middle_padding = 20 * self.render_factor

        muText = "mu"

        osText = "OS"

        muTextBbox = mu_font.getbbox(muText)
        osTextBbox = os_font.getbbox(osText)

        muTextWidth = muTextBbox[2] - muTextBbox[0]
        muTextHeight = muTextBbox[3] - muTextBbox[1]
        mu_y_location = screen_y_middle - muTextHeight / 2 - muTextBbox[1]
        mu_x_location = screen_x_middle - from_middle_padding - muTextWidth

        osTextWidth = osTextBbox[2] - osTextBbox[0]
        osTextHeight = osTextBbox[3] - osTextBbox[1]
        os_y_location = screen_y_middle - osTextHeight / 2 - osTextBbox[1]
        os_x_location = screen_x_middle + from_middle_padding

        bubble_x_padding = 30 * self.render_factor
        bubble_y_padding = 25 * self.render_factor
        bubble_x_mid_point = screen_x_middle + from_middle_padding + (osTextWidth / 2)
        bubble_width = bubble_x_padding + osTextWidth + bubble_x_padding
        bubble_height = bubble_y_padding + osTextHeight + bubble_y_padding
        transparency = 0

        draw_transparent.rounded_rectangle(
            [
                (
                    bubble_x_mid_point - (bubble_width / 2),
                    screen_y_middle - (bubble_height / 2),
                ),
                (
                    bubble_x_mid_point + (bubble_width / 2),
                    screen_y_middle + (bubble_height / 2),
                ),
            ],
            radius=bubble_height / 2,
            fill=f"#{bubble_hex}",
        )

        draw.text(
            (mu_x_location, mu_y_location),
            muText,
            font=mu_font,
            fill=f"#{deselected_font_hex}",
        )
        draw_transparent.text(
            (os_x_location, os_y_location),
            osText,
            font=os_font,
            fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency),
        )

        combined_image = Image.alpha_composite(image, transparent_text_image)

        return combined_image

    def generate_boot_screen_with_text(
        self,
        bg_hex: str,
        deselected_font_hex: str,
        icon_hex: str,
        display_text: str,
        icon_path: Path | None = None,
    ) -> Image.Image:
        (
            bg_hex,
            deselected_font_hex,
            icon_hex,
        ) = [
            val[1:] if val.startswith("#") else val
            for val in [
                bg_hex,
                deselected_font_hex,
                icon_hex,
            ]
        ]

        bg_rgb = hex_to_rgba(bg_hex)
        image = Image.new(
            "RGBA",
            (
                int(self.manager.deviceScreenWidthVar) * self.render_factor,
                int(self.manager.deviceScreenHeightVar) * self.render_factor,
            ),
            bg_rgb,
        )
        if background_image is not None:
            image.paste(
                background_image.resize(
                    (
                        int(self.manager.deviceScreenWidthVar) * self.render_factor,
                        int(self.manager.deviceScreenHeightVar) * self.render_factor,
                    )
                ),
                (0, 0),
            )

        draw = ImageDraw.Draw(image)

        selected_font_path = get_font_path(
            self.manager.use_alt_font_var, self.manager.alt_font_filename
        )

        screen_x_middle, screen_y_middle = (
            int((int(self.manager.deviceScreenWidthVar) / 2) * self.render_factor),
            int((int(self.manager.deviceScreenHeightVar) / 2) * self.render_factor),
        )

        from_middle_padding = 0

        if icon_path != None:
            if icon_path and icon_path.exists():
                from_middle_padding = 50 * self.render_factor

                logoColoured = change_logo_color(icon_path, icon_hex)
                logoColoured = logoColoured.resize(
                    (
                        int((logoColoured.size[0] / 5) * self.render_factor),
                        int((logoColoured.size[1] / 5) * self.render_factor),
                    ),
                    Image.LANCZOS,
                )

                logo_y_location = int(
                    screen_y_middle - logoColoured.size[1] / 2 - from_middle_padding
                )
                logo_x_location = int(screen_x_middle - logoColoured.size[0] / 2)

                image.paste(
                    logoColoured, (logo_x_location, logo_y_location), logoColoured
                )

        font_size = int(57.6 * self.render_factor)
        font = ImageFont.truetype(selected_font_path, font_size)

        displayText = display_text
        if self.manager.alternate_menu_names_var:
            displayText = bidi_get_display(
                menuNameMap.get(display_text.lower(), display_text)
            )

        textBbox = font.getbbox(displayText)

        textWidth = int(textBbox[2] - textBbox[0])
        textHeight = int(textBbox[3] - textBbox[1])
        y_location = int(
            screen_y_middle - textHeight / 2 - textBbox[1] + from_middle_padding
        )
        x_location = int(screen_x_middle - textWidth / 2)

        draw.text(
            (x_location, y_location),
            displayText,
            font=font,
            fill=f"#{deselected_font_hex}",
        )

        return image

    def generate_horizontal_menu(self) -> Image.Image:
        pass

    def generate_vertical_menu(self) -> Image.Image:
        pass

    def generate_alt_horizontal_menu(self) -> Image.Image:
        pass

    def _get_total_bubble_width(
        self,
        buttons: list[tuple[str, str]],
        internalBubbleFont: ImageFont.FreeTypeFont,
        bubbleFont: ImageFont.FreeTypeFont,
        initalPadding: float,
        largerPadding: float,
        smallerPadding: float,
        circleWidth: float,
    ) -> float:
        totalWidth = initalPadding
        for pair in buttons:
            # pair[0] might be MENU, POWER, or ABXY
            if len(pair[0]) == 1:
                totalWidth += circleWidth
            else:
                totalWidth += smallerPadding
                smallerTextBbox = internalBubbleFont.getbbox(pair[0])
                smallerTextWidth = smallerTextBbox[2] - smallerTextBbox[0]
                totalWidth += smallerTextWidth / self.render_factor
                totalWidth += smallerPadding
            totalWidth += smallerPadding
            # pair[1] might be something like INFO, FAVOURITE, REFRESH etc...
            textBbox = bubbleFont.getbbox(pair[1])
            textWidth = textBbox[2] - textBbox[0]
            totalWidth += textWidth / self.render_factor
            totalWidth += largerPadding
        return totalWidth

    def generate_theme(self):
        raise NotImplementedError(
            "Subclasses of BaseThemeGenerator must implement generate_theme"
        )
