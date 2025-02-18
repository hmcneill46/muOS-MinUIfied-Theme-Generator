from datetime import datetime, UTC
import math
from pathlib import Path

from .color_utils import percentage_color
from .constants import RESOURCES_DIR, THEME_SHELL_DIR, TEMPLATE_SCHEME_PATH
from .defaults import DEFAULT_FONT_PATH
from .settings import SettingsManager
from .utils import copy_contents, ensure_folder_exists


class SchemeRenderer:
    def __init__(
        self,
        manager: SettingsManager,
        font_path: Path = DEFAULT_FONT_PATH,
        screen_dimensions: tuple[int, int] = (640, 480),
    ):
        self.manager = manager
        self.font_path = font_path
        self.screen_dimensions = screen_dimensions

        self.textPadding = int(self.manager.textPaddingVar)
        self.rectanglePadding = int(self.manager.bubblePaddingVar)
        self.ItemsPerScreen = int(self.manager.itemsPerScreenVar)

        self.bg_hex = self.manager.bgHexVar.strip("#")
        self.selected_font_hex = self.manager.selectedFontHexVar.strip("#")
        self.deselected_font_hex = self.manager.deselectedFontHexVar.strip("#")
        self.bubble_hex = self.manager.bubbleHexVar.strip("#")
        self.icon_hex = self.manager.iconHexVar.strip("#")

        self.fontSize = int(self.manager.font_size_var)

        self.accent_hex = self.deselected_font_hex
        self.base_hex = self.bg_hex
        self.blend_hex = percentage_color(self.bubble_hex, self.selected_font_hex, 0.5)
        self.muted_hex = percentage_color(self.bg_hex, self.bubble_hex, 0.25)
        self.counter_alignment = "Right"
        self.datetime_alignment = self.manager.clock_alignment_var
        self.header_glyph_alignment = self.manager.header_glyph_alignment_var
        self.datetime_left_padding = self.manager.clockHorizontalLeftPaddingVar
        self.datetime_right_padding = int(self.manager.clockHorizontalRightPaddingVar)
        self.status_padding_left = int(
            self.manager.header_glyph_horizontal_left_padding_var
        )
        self.status_padding_right = int(
            self.manager.header_glyph_horizontal_right_padding_var
        )

        self.default_radius = 10
        self.header_height = int(self.manager.headerHeightVar)
        self.counter_padding_top = int(self.manager.contentPaddingTopVar)
        self.individualItemHeight = round(
            (
                int(self.manager.deviceScreenHeightVar)
                - int(self.manager.approxFooterHeightVar)
                - self.counter_padding_top
            )
            / int(self.manager.itemsPerScreenVar)
        )
        self.footerHeight = (
            int(self.manager.deviceScreenHeightVar)
            - (self.individualItemHeight * self.ItemsPerScreen)
            - self.counter_padding_top
        )

        self.glyph_width = 20
        self.glyph_to_text_pad = self.rectanglePadding

        self.page_title_alignment_map = {"Auto": 0, "Left": 1, "Centre": 2, "Right": 3}
        self.counter_alignment_map = {"Left": 0, "Centre": 1, "Right": 2}
        self.datetime_alignment_map = {"Auto": 0, "Left": 1, "Centre": 2, "Right": 3}
        self.content_alignment_map = {"Left": 0, "Centre": 1, "Right": 3}

        self.content_height = self.individualItemHeight * self.ItemsPerScreen
        self.content_padding_left = self.textPadding - self.rectanglePadding

        if self.manager.global_alignment_var == "Centre":
            self.content_padding_left = 0
        elif self.manager.global_alignment_var == "Right":
            self.content_padding_left = -self.content_padding_left

        self.status_alignment_map = {
            "Left": 0,
            "Right": 1,
            "Centre": 2,
            "Icons spaced evenly accross header": 3,
            "Icons evenly distributed with equal space around them": 4,
            "First icon aligned left, last icon align right, all other icons evenly distributed": 5,
        }

        self.replacementStringMap = {
            "default": self._get_default_map(),
            "muxlaunch": self._get_muxlaunch_map(),
            "muxnetwork": self._get_muxnetwork_map(),
            "muxassign": self._get_muxassign_map(),
            "muxgov": self._get_muxgov_map(),
            "muxsearch": self._get_muxsearch_map(),
            "muxpicker": self._get_muxpicker_map(),
            "muxplore": self._get_muxplore_map(),
            "muxfavourite": self._get_muxfavourite_map(),
            "muxhistory": self._get_muxhistory_map(),
            "muxstorage": self._get_muxstorage_map(),
        }

    def _get_muxlaunch_map(self) -> dict[str, int]:
        map = {}

        if self.manager.main_menu_style_var != "Vertical":
            wrap = self.manager.horizontal_menu_behaviour_var == "Wrap to Row"
            map = {
                "bubble_alpha": 0,
                "list_glyph_alpha": 0,
                "list_text_alpha": 0,
                "navigation_type": 4 if wrap else 2,
            }

        return map

    def _get_muxnetwork_map(self) -> dict[str, int]:
        map = {}

        if self.manager.version_var == "muOS 2410.1 Banana":
            map.update(
                {
                    "content_height": int(
                        (self.content_height / self.ItemsPerScreen)
                        * (self.ItemsPerScreen - 2)
                    ),
                    "content_item_count": self.ItemsPerScreen - 2,
                }
            )

        return map

    def _get_muxassign_map(self) -> dict[str, int]:
        map = {
            "bubble_padding_left": int(
                self.rectanglePadding + (self.glyph_width / 2) + self.glyph_to_text_pad
            ),
            "list_glyph_alpha": 255,
        }

        return map

    def _get_muxgov_map(self) -> dict[str, int]:
        map = self._get_muxassign_map()

        return map

    def _get_muxsearch_map(self) -> dict[str, int]:
        map = self._get_muxassign_map()

        return map

    def _get_muxpicker_map(self) -> dict[str, int]:
        map = {}

        if self.manager.version_var != "muOS 2410.1 Banana":
            max_preview_size = int(self.manager.deviceScreenWidthVar * 0.45)
            if int(self.manager.deviceScreenWidthVar) == 720:
                max_preview_size = 340

            map["content_width"] = (
                int(self.manager.deviceScreenWidthVar)
                - max_preview_size
                - 2 * (self.textPadding - self.rectanglePadding)
            )

        return map

    def _get_muxplore_map(self) -> dict[str, int]:
        map = {}

        if int(self.manager.maxBoxArtWidth) > 0:
            map["content_width"] = (
                int(self.manager.deviceScreenWidthVar)
                - int(self.manager.maxBoxArtWidth)
                - (self.textPadding - self.rectanglePadding)
            )

        if self.manager.enable_grid_view_explore_var:
            grid_total_height = (
                self.screen_dimensions[1] - self.footerHeight - self.header_height
            )
            grid_total_width = int(self.manager.deviceScreenWidthVar)
            min_cell_size = min(
                160, int(grid_total_height / 2), int(grid_total_width / 4)
            )  # 160 is the minimum size for a grid cell (excluding padding)

            diff_aspect_ratios = {}
            target_aspect_ratio = grid_total_width / grid_total_height
            columns = 0
            rows = 0

            while True:
                columns += 1
                rows = 0

                if grid_total_width / columns < min_cell_size:
                    break

                while True:
                    rows += 1

                    if grid_total_height / rows < min_cell_size:
                        break

                    if columns * rows >= 8:
                        aspect_ratio = columns / rows
                        diff_aspect_ratio = abs(aspect_ratio - target_aspect_ratio)

                        diff_aspect_ratios[diff_aspect_ratio] = (columns, rows)

            closest_aspect_ratio = diff_aspect_ratios[min(diff_aspect_ratios.keys())]
            grid_column_count, grid_row_count = closest_aspect_ratio

            grid_row_height = int(grid_total_height / grid_row_count)
            grid_column_width = int(grid_total_width / grid_column_count)
            cell_inner_padding = 5
            grid_location_x = 0
            grid_location_y = self.header_height
            grid_cell_width = grid_column_width - 2 * cell_inner_padding
            grid_cell_height = grid_row_height - 2 * cell_inner_padding
            grid_cell_size = min(grid_cell_width, grid_cell_height)

            map.update(
                {
                    "grid_location_x": grid_location_x,
                    "grid_location_y": grid_location_y,
                    "grid_column_count": grid_column_count,
                    "grid_row_count": grid_row_count,
                    "grid_row_height": grid_row_height,
                    "grid_column_width": grid_column_width,
                    "grid_cell_width": grid_cell_size,
                    "grid_cell_height": grid_cell_size,
                    "grid_cell_radius": math.ceil(grid_cell_size / 2.0),
                }
            )

        return map

    def _get_muxfavourite_map(self) -> dict[str, int]:
        return self._get_muxplore_map()

    def _get_muxhistory_map(self) -> dict[str, int]:
        return self._get_muxplore_map()

    def _get_muxstorage_map(self) -> dict[str, int]:
        map = {}

        return map

    def _get_default_map(self) -> dict[str, str | int]:
        map = {
            "accent_hex": self.accent_hex,
            "base_hex": self.base_hex,
            "blend_hex": self.blend_hex,
            "muted_hex": self.muted_hex,
            "battery_charging_hex": self.manager.batteryChargingHexVar.strip("#"),
            "bubble_hex": self.bubble_hex,
            "boot_text_y_pos": int(
                int(self.manager.deviceScreenHeightVar) * (165 / 480)
            ),
            "glyph_padding_left": int(self.rectanglePadding + (self.glyph_width / 2)),
            "image_overlay": self.manager.include_overlay_var,
            "footer_height": self.footerHeight,
            "header_text_alpha": 255 if self.manager.show_console_name_var else 0,
            "page_title_text_align": self.page_title_alignment_map[
                self.manager.page_title_alignment_var
            ],
            "page_title_padding": int(self.manager.pageTitlePaddingVar),
            "bar_height": 42,
            "bar_progress_width": int(self.manager.deviceScreenWidthVar) - 90,
            "bar_y_pos": self.screen_dimensions[1] - 30 + self.footerHeight,
            "bar_width": int(self.manager.deviceScreenWidthVar) - 25,
            "bar_progress_height": 16,
            "counter_alignment": self.counter_alignment_map[self.counter_alignment],
            "counter_padding_top": self.counter_padding_top,
            "default_radius": self.default_radius,
            "datetime_align": self.datetime_alignment_map[self.datetime_alignment],
            "datetime_padding_left": self.datetime_left_padding,
            "datetime_padding_right": self.datetime_right_padding,
            "status_align": self.status_alignment_map[self.header_glyph_alignment],
            "status_padding_left": self.status_padding_left,
            "status_padding_right": self.status_padding_right,
            "header_height": int(self.header_height),
            "content_height": self.content_height,
            "content_item_height": self.individualItemHeight - 2,
            "content_item_count": self.ItemsPerScreen,
            "background_alpha": 0,
            "selected_font_hex": self.selected_font_hex,
            "deselected_font_hex": self.deselected_font_hex,
            "bubble_alpha": 255,
            "bubble_padding_right": self.rectanglePadding,
            "content_alignment": self.content_alignment_map[
                self.manager.global_alignment_var
            ],  # TODO make this change for the different sections
            "list_default_label_long_mode": 1,
            "content_padding_left": self.content_padding_left,
            "content_width": (
                int(self.manager.deviceScreenWidthVar)
                - (10 if self.manager.version_var == "muOS 2410.1 Banana" else 0)
                - 2 * (self.textPadding - self.rectanglePadding)
            ),
            "footer_alpha": 0,
            "footer_background_alpha": 0,
            "footer_pad_top": 0,
            "footer_pad_bottom": 0,
            "bubble_padding_left": int(
                self.rectanglePadding + (self.glyph_width / 2) + self.glyph_to_text_pad
            )
            if self.manager.show_glyphs_var
            else self.rectanglePadding,
            "list_glyph_alpha": 255 if self.manager.show_glyphs_var else 0,
            "list_text_alpha": 255,
            "navigation_type": 0,
            "content_padding_top": self.counter_padding_top
            - (int(self.header_height) + 2),
            "grid_navigation_type": 4,
            "grid_background": self.bg_hex,
            "grid_background_alpha": 0,
            "grid_location_x": 0,
            "grid_location_y": 0,
            "grid_column_count": 0,
            "grid_row_count": 0,
            "grid_row_height": 0,
            "grid_column_width": 0,
            "grid_cell_width": 200,
            "grid_cell_height": 200,
            "grid_cell_radius": 10,
            "grid_cell_border_width": 0,
            "grid_cell_image_padding_top": 0,
            "grid_cell_text_padding_bottom": 0,
            "grid_cell_text_padding_side": 0,
            "grid_cell_text_line_spacing": 0,
            "grid_cell_default_background": self.bg_hex,
            "grid_cell_default_background_alpha": 0,
            "grid_cell_default_border": self.bg_hex,
            "grid_cell_default_border_alpha": 0,
            "grid_cell_default_image_alpha": 255,
            "grid_cell_default_image_recolour": self.icon_hex,
            "grid_cell_default_image_recolour_alpha": 255,
            "grid_cell_default_text": self.deselected_font_hex,
            "grid_cell_default_text_alpha": 0,
            "grid_cell_focus_background": self.selected_font_hex,
            "grid_cell_focus_background_alpha": int(255 * 0.133),
            "grid_cell_focus_border": self.deselected_font_hex,
            "grid_cell_focus_border_alpha": 0,
            "grid_cell_focus_image_alpha": 255,
            "grid_cell_focus_image_recolour": self.icon_hex,
            "grid_cell_focus_image_recolour_alpha": 255,
            "grid_cell_focus_text": self.selected_font_hex,
            "grid_cell_focus_text_alpha": 0,
        }

        missingValues = [k for k, v in map.items() if v is None]
        if missingValues:
            missingValuesString = ""
            for n in missingValues:
                missingValuesString += n + "\n"
            raise ValueError(f"Replacement string(s) \n{missingValuesString} not set")

        return map

    def render(self, item: str) -> str | None:
        template = TEMPLATE_SCHEME_PATH.read_text()

        default_contents = self.replacementStringMap["default"]
        scheme_contents = self.replacementStringMap.get(item, {})

        scheme_contents = default_contents | scheme_contents

        return template.format(**scheme_contents)
