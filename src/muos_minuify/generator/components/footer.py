import math
from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling

from ...color_utils import hex_to_rgba, change_logo_color
from ...constants import BUTTON_GLYPHS_DIR
from ...defaults import DEFAULT_FONT_PATH
from ...settings import SettingsManager
from .scalable import Scalable


class FooterGuides(Scalable):
    def __init__(
        self,
        manager: SettingsManager,
        font_path: Path = DEFAULT_FONT_PATH,
        screen_dimensions: tuple[int, int] = (640, 480),
        render_factor: int = 5,
    ):
        super().__init__(screen_dimensions, render_factor)
        self.font_path = font_path
        self.manager = manager

        self.footer_ideal_height = self.manager.approxFooterHeightVar
        self.footer_height = self.footer_ideal_height
        self.footer_margin_block = self.manager.VBG_Vertical_Padding_var
        self.footer_margin_inline = self.manager.VBG_Horizontal_Padding_var
        self.footer_bubble_height = self.footer_height - self.footer_margin_block * 2
        self.footer_bubble_padding = self.footer_bubble_height * (10 / 60)
        self.footer_bubble_button_padding = self.footer_bubble_height * (10 / 60)
        self.footer_bubble_effect_padding_right = self.footer_bubble_height * (20 / 60)
        self.footer_bubble_button_width = self.footer_bubble_height - (
            self.footer_bubble_padding * 2
        )

        self.center_y_pos = self.screen_dimensions[1] - (self.footer_height / 2)

        self.content_item_height = 0
        self.content_padding_top = self.manager.contentPaddingTopVar
        self.content_gap = 2

        self.items_per_screen = self.manager.itemsPerScreenVar
        self.control_scheme = self.manager.muos_button_swap_var
        self.button_layout = self.manager.physical_controller_layout_var
        self.right_buttons = []
        self.left_buttons = [("POWER", "SLEEP")]

        self.left_guide_width = 0
        self.right_guide_width = self.screen_dimensions[0]

        button_font_size = self.footer_bubble_height * (20.1 / 60)
        effect_font_size = self.footer_bubble_height * (24 / 60)
        single_letter_font_size = self.footer_bubble_button_width * (28 / 40)
        word_font_size = self.footer_bubble_button_width * (20.1 / 40)

        self.button_font = ImageFont.truetype(self.font_path, button_font_size)
        self.effect_font = ImageFont.truetype(self.font_path, effect_font_size)
        self.single_letter_font = ImageFont.truetype(
            self.font_path, single_letter_font_size
        )
        self.word_font = ImageFont.truetype(self.font_path, word_font_size)

        ib_ascent, ib_descent = self.button_font.getmetrics()
        ib_text_height = ib_ascent + ib_descent
        self.footer_bubble_button_y = self.center_y_pos - (ib_text_height / 2)

        self.with_footer_configuration(
            self.items_per_screen,
            self.content_padding_top,
            self.footer_ideal_height,
            self.footer_margin_block,
            self.footer_margin_inline,
        )
        self.with_button_configuration(
            self.right_buttons,
            self.left_buttons,
            self.control_scheme,
            self.button_layout,
        )

    def _get_total_bubble_width(
        self,
        buttons: list[tuple[str, str]],
        button_font: ImageFont.FreeTypeFont,
        effect_font: ImageFont.FreeTypeFont,
        bubble_padding: float,
        effect_padding_right: float,
        button_padding_inline: float,
        circleWidth: float,
    ) -> float:
        total_width = bubble_padding

        for button, effect in buttons:
            if len(button) == 1:
                total_width += circleWidth
            else:
                button_bbox = button_font.getbbox(button)
                total_width += (
                    button_padding_inline
                    + (button_bbox[2] - button_bbox[0])
                    + button_padding_inline
                )

            effect_bbox = effect_font.getbbox(effect)
            total_width += (
                button_padding_inline
                + (effect_bbox[2] - effect_bbox[0])
                + effect_padding_right
            )

        return total_width

    def with_footer_configuration(
        self,
        items_per_screen: int,
        content_padding_top: int,
        footer_ideal_height: int,
        footer_margin_block: int,
        footer_margin_inline: int,
    ) -> "FooterGuides":
        self.footer_margin_block = footer_margin_block * self.render_factor

        iterations = 0
        self.left_guide_width = 0
        self.right_guide_width = self.scaled_screen_dimensions[0]

        while (
            80
            + (self.footer_margin_inline * 2)
            + self.left_guide_width
            + self.right_guide_width
        ) > self.scaled_screen_dimensions[0]:
            footer_margin_block += iterations * self.render_factor

            self.content_item_height = (
                self.scaled_screen_dimensions[1]
                - self.render_factor * (footer_ideal_height + content_padding_top)
            ) / items_per_screen
            self.footer_height = (
                self.scaled_screen_dimensions[1]
                - (content_padding_top * self.render_factor)
                - (self.content_item_height * items_per_screen)
                + (self.content_gap * self.render_factor)
            )

            self.footer_bubble_height = self.footer_height - (
                2 * footer_margin_block * self.render_factor
            )

            self.footer_bubble_padding = self.footer_bubble_height * (10 / 60)
            self.footer_bubble_button_padding = self.footer_bubble_height * (10 / 60)
            self.footer_bubble_effect_padding_right = self.footer_bubble_height * (
                20 / 60
            )
            self.footer_margin_inline = footer_margin_inline * self.render_factor

            self.footer_bubble_button_width = self.footer_bubble_height - (
                self.footer_bubble_padding * 2
            )

            button_font_size = self.footer_bubble_height * (20.1 / 60)
            effect_font_size = self.footer_bubble_height * (24 / 60)
            single_letter_font_size = self.footer_bubble_button_width * (28 / 40)
            word_font_size = self.footer_bubble_button_width * (20.1 / 40)

            self.button_font = ImageFont.truetype(self.font_path, button_font_size)
            self.effect_font = ImageFont.truetype(self.font_path, effect_font_size)
            self.single_letter_font = ImageFont.truetype(
                self.font_path, single_letter_font_size
            )
            self.word_font = ImageFont.truetype(self.font_path, word_font_size)

            self.center_y_pos = (
                self.scaled_screen_dimensions[1]
                - self.footer_margin_block
                - (self.footer_bubble_height / 2)
            )

            ib_ascent, ib_descent = self.button_font.getmetrics()
            ib_text_height = ib_ascent + ib_descent
            self.footer_bubble_button_y = self.center_y_pos - (ib_text_height / 2)

            self.left_guide_width = self._get_total_bubble_width(
                self.left_buttons,
                self.word_font,
                self.effect_font,
                self.footer_bubble_padding,
                self.footer_bubble_effect_padding_right,
                self.footer_bubble_button_padding,
                self.footer_bubble_button_width,
            )

            self.right_guide_width = self._get_total_bubble_width(
                self.right_buttons,
                self.word_font,
                self.effect_font,
                self.footer_bubble_padding,
                self.footer_bubble_effect_padding_right,
                self.footer_bubble_button_padding,
                self.footer_bubble_button_width,
            )

            iterations += 1

        return self

    def with_button_configuration(
        self,
        right_buttons: list[tuple[str, str]],
        left_buttons: list[tuple[str, str]] = [("POWER", "SLEEP")],
        control_scheme: Literal["Modern", "Retro"] = "Modern",
        button_layout: Literal[
            "Nintendo", "Xbox", "PlayStation", "Universal"
        ] = "Nintendo",
    ) -> "FooterGuides":
        self.right_buttons = right_buttons
        self.left_buttons = left_buttons
        self.control_scheme = control_scheme
        self.button_layout = button_layout

        if self.control_scheme == "Modern":
            modern_buttons = []
            for button, effect in right_buttons:
                match button.upper():
                    case "A":
                        modern_buttons.append(("B", effect))
                    case "B":
                        modern_buttons.append(("A", effect))
                    case "X":
                        modern_buttons.append(("Y", effect))
                    case "Y":
                        modern_buttons.append(("X", effect))
            self.right_buttons = modern_buttons

        return self

    def _generate_button_glyph(self, button_text: str, colour_hex: str) -> Image.Image:
        rendered_bubble_height = int(self.footer_bubble_button_width)
        buttonSize = (rendered_bubble_height, rendered_bubble_height)

        if button_text.upper() in [
            "A",
            "B",
            "X",
            "Y",
        ] and self.button_layout in [
            "PlayStation",
            "Xbox",
            "Universal",
        ]:
            if self.button_layout == "PlayStation":
                image = (
                    Image.open(
                        BUTTON_GLYPHS_DIR / "PlayStation" / f"{button_text.upper()}.png"
                    )
                    .convert("RGBA")
                    .resize(buttonSize, Resampling.LANCZOS)
                )
            elif self.button_layout == "Universal":
                image = (
                    Image.open(
                        BUTTON_GLYPHS_DIR / "Universal" / f"{button_text.upper()}.png"
                    )
                    .convert("RGBA")
                    .resize(buttonSize, Resampling.LANCZOS)
                )
            elif self.button_layout == "Xbox":
                if button_text.upper() == "A":
                    image = self._generate_button_glyph("B", colour_hex)
                elif button_text.upper() == "B":
                    image = self._generate_button_glyph("A", colour_hex)
                elif button_text.upper() == "X":
                    image = self._generate_button_glyph("Y", colour_hex)
                elif button_text.upper() == "Y":
                    image = self._generate_button_glyph("X", colour_hex)

        elif len(button_text) == 1:
            sl_text_bbox = self.single_letter_font.getbbox(button_text)
            sl_text_height = sl_text_bbox[3] - sl_text_bbox[1]
            single_letter_text_y = (
                (self.footer_bubble_button_width / 2)
                - (sl_text_height / 2)
                - sl_text_bbox[1]
            )

            image = Image.new(
                "RGBA",
                buttonSize,
                (0, 0, 0, 0),
            )
            draw = ImageDraw.Draw(image)

            circleCentreX = (rendered_bubble_height) / 2
            draw.ellipse(
                (0, 0, rendered_bubble_height, rendered_bubble_height),
                fill="#FFFFFF",
            )

            singleLetterWidth = sl_text_bbox[2] - sl_text_bbox[0]
            smallerTextX = circleCentreX - (singleLetterWidth / 2)

            text_mask = Image.new("L", image.size, 0)
            mask_draw = ImageDraw.Draw(text_mask)
            mask_draw.text(
                (smallerTextX, single_letter_text_y),
                button_text,
                font=self.single_letter_font,
                fill=255,
            )

            existing_alpha = image.getchannel("A")
            new_alpha = Image.new("L", image.size, 0)

            existing_alpha_pixels = existing_alpha.load()
            new_alpha_pixels = new_alpha.load()

            for y in range(int(rendered_bubble_height)):
                for x in range(int(rendered_bubble_height)):
                    new_alpha_pixels[x, y] = max(
                        existing_alpha_pixels[x, y] - text_mask.getpixel((x, y)), 0
                    )

            image.putalpha(new_alpha)
        else:
            isb_text_bbox = self.word_font.getbbox(button_text)
            isb_text_height = isb_text_bbox[3] - isb_text_bbox[1]
            in_smaller_bubble_text_y = (
                (self.footer_bubble_button_width / 2)
                - (isb_text_height / 2)
                - isb_text_bbox[1]
            )

            horizontal_small_padding = self.footer_bubble_button_width * (10 / 40)

            ## Make the smaller bubble
            smallerTextBbox = self.word_font.getbbox(button_text)
            smallerTextWidth = smallerTextBbox[2] - smallerTextBbox[0]
            smallerBubbleWidth = (
                horizontal_small_padding + smallerTextWidth + horizontal_small_padding
            )

            rendered_smallerBubbleWidth = int(smallerBubbleWidth)

            image = Image.new(
                "RGBA",
                (rendered_smallerBubbleWidth, rendered_bubble_height),
                (0, 0, 0, 0),
            )
            draw = ImageDraw.Draw(image)

            draw.rounded_rectangle(
                [
                    (0, 0),  # bottom left point
                    (rendered_smallerBubbleWidth, rendered_bubble_height),
                ],  # Top right point
                radius=(math.ceil(rendered_bubble_height) / 2),
                fill=hex_to_rgba("#FFFFFF"),
            )

            smallerTextX = horizontal_small_padding

            text_mask = Image.new("L", image.size, 0)
            mask_draw = ImageDraw.Draw(text_mask)
            mask_draw.text(
                (smallerTextX, in_smaller_bubble_text_y),
                button_text,
                font=self.word_font,
                fill=255,
            )

            existing_alpha = image.getchannel("A")
            new_alpha = Image.new("L", image.size, 0)

            existing_alpha_pixels = existing_alpha.load()
            new_alpha_pixels = new_alpha.load()

            for y in range(int(rendered_bubble_height)):
                for x in range(int(rendered_smallerBubbleWidth)):
                    new_alpha_pixels[x, y] = max(
                        existing_alpha_pixels[x, y] - text_mask.getpixel((x, y)), 0
                    )

            image.putalpha(new_alpha)

        return image

    def __generate_guide(
        self,
        buttons: list[tuple[str, str]],
        guide_width: int | float,
        bubble_x_pos: int | float,
        colour_hex: str,
    ) -> Image.Image:
        image = Image.new("RGBA", self.scaled_screen_dimensions, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        draw.rounded_rectangle(
            [
                (
                    bubble_x_pos,
                    (self.center_y_pos - self.footer_bubble_height / 2),
                ),
                (
                    bubble_x_pos + guide_width,
                    (self.center_y_pos + self.footer_bubble_height / 2),
                ),
            ],
            radius=(self.footer_bubble_height / 2),
            fill=hex_to_rgba(colour_hex, alpha=0.133),
        )
        bubble_x_pos += self.footer_bubble_padding

        for button, effect in buttons:
            button_image = self._generate_button_glyph(
                button,
                colour_hex,
            )

            button_image = change_logo_color(button_image, colour_hex)

            image.alpha_composite(
                button_image,
                (
                    int(bubble_x_pos),
                    int(self.center_y_pos - (button_image.size[1] / 2)),
                ),
            )

            bubble_x_pos += button_image.size[0] + self.footer_bubble_button_padding

            text_bbox = self.effect_font.getbbox(effect)
            draw.text(
                (bubble_x_pos, self.footer_bubble_button_y),
                effect,
                font=self.effect_font,
                fill=hex_to_rgba(colour_hex, alpha=1),
            )
            bubble_x_pos += (text_bbox[2] - text_bbox[0]) + (
                self.footer_bubble_effect_padding_right
            )

        return image

    def _generate_left_guide(self, colour_hex: str) -> Image.Image:
        left_x_pos = self.footer_margin_inline

        return self.__generate_guide(
            self.left_buttons, self.left_guide_width, left_x_pos, colour_hex
        )

    def _generate_right_guide(self, colour_hex: str) -> Image.Image:
        right_x_pos = (
            self.scaled_screen_dimensions[0]
            - self.footer_margin_inline
            - self.right_guide_width
        )

        return self.__generate_guide(
            self.right_buttons, self.right_guide_width, right_x_pos, colour_hex
        )

    def generate(
        self,
        colour_hex: str,
        show_left_guide: bool = True,
        show_right_guide: bool = True,
    ) -> Image.Image:
        image = Image.new("RGBA", self.scaled_screen_dimensions, (0, 0, 0, 0))

        if show_left_guide:
            left_guide_image = self._generate_left_guide(colour_hex)
            image.alpha_composite(left_guide_image)

        if show_right_guide:
            right_guide_image = self._generate_right_guide(colour_hex)
            image.alpha_composite(right_guide_image)

        return image
