from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling

from ...color_utils import change_logo_color
from ...constants import HORIZONTAL_LOGOS_DIR
from ...defaults import DEFAULT_FONT_PATH
from ...settings import SettingsManager
from .scalable import Scalable


LAUNCHER_ITEMS = [
    "explore",
    "favourite",
    "history",
    "apps",
    "info",
    "config",
    "reboot",
    "shutdown",
]


class LauncherIcons(Scalable):
    def __init__(
        self,
        manager: SettingsManager,
        font_path: Path = DEFAULT_FONT_PATH,
        screen_dimensions: tuple[int, int] = (640, 480),
        render_factor: int = 5,
    ):
        super().__init__(screen_dimensions, render_factor)
        self.manager = manager

        self.selected_font_hex = self.manager.selectedFontHexVar
        self.deselected_font_hex = self.manager.deselectedFontHexVar
        self.bubble_hex = self.manager.bubbleHexVar
        self.icon_hex = self.manager.iconHexVar

        self.screen_y_center = self.scaled_screen_dimensions[1] / 2
        self.label_bubble_height = min(
            self.scaled_screen_dimensions[0] * 36.3 / 640,
            self.scaled_screen_dimensions[1] * 36.3 / 480,
        )
        self.label_bubble_padding = min(
            self.scaled_screen_dimensions[0] * 40 / 640,
            self.scaled_screen_dimensions[1] * 40 / 480,
        )
        self.small_bubble_padding = min(
            self.scaled_screen_dimensions[0] * 15 / 640,
            self.scaled_screen_dimensions[1] * 15 / 480,
        )
        self.bubble_gap = 5 * self.render_factor
        self.row_gap = min(
            self.scaled_screen_dimensions[0] * 20 / 640,
            self.scaled_screen_dimensions[1] * 20 / 480,
        )

        self.font_path = font_path
        self.font_size = min(
            self.scaled_screen_dimensions[0] * 24 / 640,
            self.scaled_screen_dimensions[1] * 24 / 480,
        )
        self.label_font = ImageFont.truetype(self.font_path, self.font_size)

        ascent, descent = self.label_font.getmetrics()
        self.text_height = ascent + descent

    def with_color_configuration(
        self,
        selected_font_hex: str,
        deselected_font_hex: str,
        bubble_hex: str,
        icon_hex: str,
    ) -> "LauncherIcons":
        self.selected_font_hex = selected_font_hex
        self.deselected_font_hex = deselected_font_hex
        self.bubble_hex = bubble_hex
        self.icon_hex = icon_hex

        return self

    def _load_and_color_icon(
        self, item: str, top_row: bool, selected: bool
    ) -> Image.Image:
        icon_path = HORIZONTAL_LOGOS_DIR / f"{item}.png"

        if top_row:
            return change_logo_color(icon_path, self.icon_hex)
        else:
            return change_logo_color(
                icon_path,
                self.selected_font_hex if selected else self.deselected_font_hex,
            )

    def _get_large_icon_size(self, icon_image: Image.Image) -> tuple[int, int]:
        return (
            int(icon_image.size[0] * self.render_factor / 5),
            int(icon_image.size[1] * self.render_factor / 5),
        )

    def _get_small_icon_size(self, icon_image: Image.Image) -> tuple[int, int]:
        min_screen_dimension = min(
            (
                self.scaled_screen_dimensions[0] / 640,
                self.scaled_screen_dimensions[1] / 480,
            )
        )

        logo_size = (
            int(icon_image.size[0] * min_screen_dimension / 5),
            int(icon_image.size[1] * min_screen_dimension / 5),
        )
        return logo_size

    def _draw_large_icon(
        self,
        image: Image.Image,
        icon_image: Image.Image,
        x: int | int,
        y: int | int,
    ) -> None:
        image.alpha_composite(icon_image, (x, y))

    def _draw_small_icon(
        self,
        image: Image.Image,
        draw: ImageDraw.ImageDraw,
        icon_image: Image.Image,
        center_x: float | int,
        center_y: float | int,
        radius: float | int,
        selected: bool = False,
        passthrough: bool = False,
    ) -> None:
        icon_x = int(center_x - (icon_image.size[0] / 2))
        icon_y = int(center_y - (icon_image.size[1] / 2))

        if selected:
            left = center_x - radius
            top = center_y - radius
            right = center_x + radius
            bottom = center_y + radius

            if passthrough:
                bubble_layer = Image.new("RGBA", image.size, 0)
                bubble_draw = ImageDraw.Draw(bubble_layer)

                bubble_draw.ellipse(
                    [(left, top), (right, bottom)],
                    fill=self.bubble_hex,
                )

                bubble_alpha = bubble_layer.getchannel("A")
                new_bubble_alpha = bubble_alpha.copy()

                icon_mask = icon_image.split()[-1]
                new_bubble_alpha.paste(
                    0,
                    box=(
                        icon_x,
                        icon_y,
                        icon_x + icon_image.size[0],
                        icon_y + icon_image.size[1],
                    ),
                    mask=icon_mask,
                )
                bubble_layer.putalpha(new_bubble_alpha)

                image.alpha_composite(bubble_layer)
                return
            else:
                draw.ellipse(
                    [(left, top), (right, bottom)],
                    fill=self.bubble_hex,
                )

        image.alpha_composite(icon_image, (icon_x, icon_y))

    def _draw_label(
        self,
        draw: ImageDraw.ImageDraw,
        center_x: float | int,
        center_y: float | int,
        label_text: str,
    ) -> None:
        bbox = self.label_font.getbbox(label_text)
        text_width = bbox[2] - bbox[0]

        text_x = center_x - (text_width / 2)
        text_y = center_y - (self.text_height / 2)

        draw.text(
            (text_x, text_y),
            label_text,
            font=self.label_font,
            fill=self.deselected_font_hex,
        )

    def _draw_selection_bubble(
        self,
        image: Image.Image,
        draw: ImageDraw.ImageDraw,
        center_x: float | int,
        center_y: float | int,
        label_text: str,
        passthrough: bool = False,
    ) -> None:
        bbox = self.label_font.getbbox(label_text)
        text_width = bbox[2] - bbox[0]

        bubble_length = text_width + self.label_bubble_padding
        bubble_left = center_x - (bubble_length / 2)
        bubble_right = center_x + (bubble_length / 2)
        bubble_top = center_y - (self.label_bubble_height / 2)
        bubble_bottom = center_y + (self.label_bubble_height / 2)

        if passthrough:
            mask = Image.new("RGBA", self.scaled_screen_dimensions, (255, 255, 255, 0))
            mask_draw = ImageDraw.Draw(mask)

            mask_draw.rounded_rectangle(
                [(bubble_left, bubble_top), (bubble_right, bubble_bottom)],
                fill=self.bubble_hex,
                radius=self.label_bubble_height / 2,
            )

            mask_draw.text(
                (center_x - (text_width / 2), center_y - (self.text_height / 2)),
                label_text,
                font=self.label_font,
                fill=(0, 0, 0, 0),
            )

            image.alpha_composite(mask, (0, 0))
        else:
            draw.rounded_rectangle(
                [(bubble_left, bubble_top), (bubble_right, bubble_bottom)],
                fill=self.bubble_hex,
                radius=self.label_bubble_height / 2,
            )

            draw.text(
                (center_x - (text_width / 2), center_y - (self.text_height / 2)),
                label_text,
                font=self.label_font,
                fill=self.selected_font_hex,
            )

    def _calculate_top_row_positions(
        self, icons: dict[str, Image.Image]
    ) -> list[float | int]:
        total_width = self.scaled_screen_dimensions[0]
        num = len(icons)
        combined_width = sum(icon.size[0] for icon in icons.values())
        spacing = (total_width - combined_width) / (num + 1)
        positions = []
        current_x = spacing

        for icon in icons.values():
            center_x = current_x + (icon.size[0] / 2)
            positions.append(center_x)
            current_x += icon.size[0] + spacing

        return positions

    def _calculate_bottom_row_positions(
        self, icons: dict[str, Image.Image]
    ) -> list[float | int]:
        total_width = self.scaled_screen_dimensions[0]
        num = len(icons)
        combined_width = sum(icon.size[0] for icon in icons.values())
        left_margin = total_width * (175 / 640)
        spacing = (
            ((total_width - (2 * left_margin) - combined_width) / (num - 1))
            if num > 1
            else 0
        )
        positions = []
        current_x = left_margin

        for icon in icons.values():
            center_x = current_x + (icon.size[0] / 2)
            positions.append(center_x)
            current_x += icon.size[0] + spacing

        return positions

    def _get_top_row_vertical_positions(
        self, icons: dict[str, Image.Image]
    ) -> tuple[int, int]:
        max_icon_height = max(icon.size[1] for icon in icons.values())
        combined_height = max_icon_height + self.label_bubble_height
        icon_y = int(self.screen_y_center - (combined_height / 2))
        bubble_center_y = int(
            self.screen_y_center
            + (combined_height / 2)
            - (self.label_bubble_height / 2)
        )

        return icon_y, bubble_center_y

    def _get_bottom_row_vertical_positions(
        self,
        top_row_combined_height: float | int,
        icons: dict[str, Image.Image],
    ) -> tuple[int, float]:
        max_icon_height = max(icon.size[1] for icon in icons.values())
        combined_height = max_icon_height + self.small_bubble_padding
        circle_radius = combined_height / 2
        bubble_center_y = int(
            self.screen_y_center
            + (top_row_combined_height / 2)
            + self.row_gap
            + circle_radius
        )

        return bubble_center_y, circle_radius

    def _draw_top_row(
        self,
        image: Image.Image,
        draw: ImageDraw.ImageDraw,
        icons: dict[str, Image.Image],
        positions: list[float | int],
        icon_y: int,
        bubble_center_y: int,
        label_map: dict[str, str],
        selected_item: str,
        passthrough: bool,
    ) -> None:
        for item, center_x in zip(icons.keys(), positions):
            icon_image = icons[item]
            icon_w, _ = icon_image.size
            icon_x = int(center_x - (icon_w / 2))
            self._draw_large_icon(image, icon_image, icon_x, icon_y)

            label = label_map.get(item, item)
            if selected_item == item:
                self._draw_selection_bubble(
                    image, draw, center_x, bubble_center_y, label, passthrough
                )
            else:
                self._draw_label(draw, center_x, bubble_center_y, label)

    def _draw_bottom_row(
        self,
        image: Image.Image,
        draw: ImageDraw.ImageDraw,
        icons: dict[str, Image.Image],
        positions: list[float | int],
        center_y: int,
        circle_radius: float | int,
        selected_item: str,
        passthrough: bool,
    ) -> None:
        for item, center_x in zip(icons.keys(), positions):
            selected = selected_item == item
            self._draw_small_icon(
                image,
                draw,
                icons[item],
                center_x,
                center_y,
                circle_radius,
                selected,
                passthrough,
            )

    def generate(
        self,
        selected_item: str,
        passthrough: bool = False,
    ) -> Image.Image:
        image = Image.new("RGBA", self.scaled_screen_dimensions, (255, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        top_label_map = {
            "explore": "Content",
            "favourite": "Favourites",
            "history": "History",
            "apps": "Utilities",
        }

        top_items = LAUNCHER_ITEMS[:4]
        top_icons = {}
        bottom_items = LAUNCHER_ITEMS[4:]
        bottom_icons = {}

        for item in top_items:
            selected = item == selected_item
            icon = self._load_and_color_icon(item, top_row=True, selected=selected)
            large_size = self._get_large_icon_size(icon)
            icon = icon.resize(large_size, Resampling.LANCZOS)
            top_icons[item] = icon

        top_positions = self._calculate_top_row_positions(top_icons)
        icon_y, bubble_center_y = self._get_top_row_vertical_positions(top_icons)

        self._draw_top_row(
            image,
            draw,
            top_icons,
            top_positions,
            icon_y,
            bubble_center_y,
            top_label_map,
            selected_item,
            passthrough,
        )

        for item in bottom_items:
            selected = item == selected_item
            icon = self._load_and_color_icon(item, top_row=False, selected=selected)
            small_size = self._get_small_icon_size(icon)
            icon = icon.resize(small_size, Resampling.LANCZOS)
            bottom_icons[item] = icon

        bottom_positions = self._calculate_bottom_row_positions(bottom_icons)

        max_top_icon_height = max(icon.size[1] for icon in top_icons.values())
        top_row_combined_height = max_top_icon_height + self.label_bubble_height
        bottom_center_y, circle_radius = self._get_bottom_row_vertical_positions(
            top_row_combined_height, bottom_icons
        )
        self._draw_bottom_row(
            image,
            draw,
            bottom_icons,
            bottom_positions,
            bottom_center_y,
            circle_radius,
            selected_item,
            passthrough,
        )

        return image
