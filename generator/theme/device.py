import math
from pathlib import Path
import re
import shutil
from typing import Any, Callable

from tkinter import ttk

from PIL import Image
from PIL.Image import Resampling

from generator.color_utils import percentage_color
from generator.constants import (
    ASSETS_DIR,
    DEVICE_TYPE_OPTIONS,
    RESOURCES_DIR,
    THEME_SHELL_DIR,
    HORIZONTAL_LOGOS_DIR,
    TEMPLATE_SCHEME_PATH,
    GLYPHS_DIR,
    OVERLAY_DIR,
    FONTS_DIR,
    MENU_LISTING_2410_X,
    BatteryStyleOptionsDict,
    BatteryChargingStyleOptionsDict,
)

from generator.font import get_font_path
from generator.utils import copy_contents, ensure_folder_exists, resize_system_logos
from generator.settings import SettingsManager
from generator.theme import BaseThemeGenerator


class DeviceThemeGenerator(BaseThemeGenerator):
    def __init__(self, manager: SettingsManager, progress_callback: Callable):
        super().__init__(manager, render_factor=5, progress_callback=progress_callback)

        self.all_resolutions = []
        for device_type in DEVICE_TYPE_OPTIONS:
            match = re.search(r"\[(\d+)x(\d+)\]", device_type)
            if match:
                self.all_resolutions.append((int(match.group(1)), int(match.group(2))))

    def generate_theme(self, threadNumber: int):
        textPadding = int(self.manager.textPaddingVar)
        rectanglePadding = int(self.manager.bubblePaddingVar)
        ItemsPerScreen = int(self.manager.itemsPerScreenVar)
        bg_hex = self.manager.bgHexVar
        selected_font_hex = self.manager.selectedFontHexVar
        deselected_font_hex = self.manager.deselectedFontHexVar
        bubble_hex = self.manager.bubbleHexVar
        icon_hex = self.manager.iconHexVar

        (
            bg_hex,
            selected_font_hex,
            deselected_font_hex,
            bubble_hex,
            icon_hex,
        ) = [
            val[1:] if val.startswith("#") else val
            for val in [
                bg_hex,
                selected_font_hex,
                deselected_font_hex,
                bubble_hex,
                icon_hex,
            ]
        ]

        selected_font_path = get_font_path(
            self.manager.use_alt_font_var, self.manager.alt_font_filename
        )
        temp_build_dir = RESOURCES_DIR / f".TempBuildTheme{threadNumber}"

        copy_contents(THEME_SHELL_DIR, temp_build_dir)

        newSchemeDir = temp_build_dir / "scheme"
        ensure_folder_exists(newSchemeDir)

        fontSize = int(self.manager.font_size_var)

        # Theme Variables that wont change
        accent_hex = deselected_font_hex
        base_hex = bg_hex
        blend_hex = percentage_color(bubble_hex, selected_font_hex, 0.5)
        muted_hex = percentage_color(bg_hex, bubble_hex, 0.25)
        counter_alignment = "Right"
        datetime_alignment = self.manager.clock_alignment_var
        header_glyph_alignment = self.manager.header_glyph_alignment_var
        datetime_left_padding = self.manager.clockHorizontalLeftPaddingVar
        datetime_right_padding = self.manager.clockHorizontalRightPaddingVar
        status_padding_left = int(self.manager.header_glyph_horizontal_left_padding_var)
        status_padding_right = int(
            self.manager.header_glyph_horizontal_right_padding_var
        )

        default_radius = "10"
        header_height = str(self.manager.headerHeightVar)
        counter_padding_top = str(self.manager.contentPaddingTopVar)
        individualItemHeight = round(
            (
                int(self.manager.deviceScreenHeightVar)
                - int(self.manager.approxFooterHeightVar)
                - int(self.manager.contentPaddingTopVar)
            )
            / int(self.manager.itemsPerScreenVar)
        )
        footerHeight = (
            int(self.manager.deviceScreenHeightVar)
            - (individualItemHeight * int(self.manager.itemsPerScreenVar))
            - int(self.manager.contentPaddingTopVar)
        )

        replacementStringMap = {
            "default": {},
            "muxlaunch": {},
            "muxnetwork": {},
            "muxassign": {},
            "muxgov": {},
            "muxsearch": {},
            "muxpicker": {},
            "muxplore": {},
            "muxfavourite": {},
            "muxhistory": {},
            "muxstorage": {},
        }

        glyph_width = 20
        glyph_to_text_pad = int(self.manager.bubblePaddingVar)
        page_title_alignment_map = {"Auto": 0, "Left": 1, "Centre": 2, "Right": 3}
        counter_alignment_map = {"Left": 0, "Centre": 1, "Right": 2}
        datetime_alignment_map = {"Auto": 0, "Left": 1, "Centre": 2, "Right": 3}
        content_alignment_map = {"Left": 0, "Centre": 1, "Right": 2}
        content_height = individualItemHeight * int(self.manager.itemsPerScreenVar)
        content_padding_left = int(self.manager.textPaddingVar) - int(
            self.manager.bubblePaddingVar
        )
        if self.manager.global_alignment_var == "Centre":
            content_padding_left = 0
        elif self.manager.global_alignment_var == "Right":
            content_padding_left = -content_padding_left

        status_alignment_map = {
            "Left": 0,
            "Right": 1,
            "Centre": 2,
            "Icons spaced evenly across header": 3,
            "icons evenly distributed with equal space around them": 4,
            "First icon aligned left last icon aligned right all other icons evenly distributed": 5,
        }

        # Set up default colours that should be the same everywhere
        replacementStringMap["default"] = {
            "accent_hex": accent_hex,
            "base_hex": base_hex,
            "blend_hex": blend_hex,
            "muted_hex": muted_hex,
            "battery_charging_hex": self.manager.batteryChargingHexVar,
            "bubble_hex": self.manager.bubbleHexVar,
            "boot_text_y_pos": int(
                int(self.manager.deviceScreenHeightVar) * (165 / 480)
            ),
            "glyph_padding_left": int(
                int(self.manager.bubblePaddingVar) + (glyph_width / 2)
            ),
            "image_overlay": self.manager.include_overlay_var,
            "footer_height": footerHeight,
            "header_text_alpha": 255 if self.manager.show_console_name_var else 0,
            "page_title_text_align": page_title_alignment_map[
                self.manager.page_title_alignment_var
            ],
            "page_title_padding": int(self.manager.pageTitlePaddingVar),
            "bar_height": 42,
            "bar_progress_width": int(self.manager.deviceScreenWidthVar) - 90,
            "bar_y_pos": self.scaled_screen_dimensions[1]
            - 30
            + self._get_footer_height(
                self.manager.itemsPerScreenVar,
                self.scaled_screen_dimensions[1],
                self.manager.contentPaddingTopVar,
                self.manager.approxFooterHeightVar,
            ),
            "bar_width": int(self.manager.deviceScreenWidthVar) - 25,
            "bar_progress_height": 16,
            "counter_alignment": counter_alignment_map[counter_alignment],
            "counter_padding_top": counter_padding_top,
            "default_radius": default_radius,
            "datetime_align": datetime_alignment_map[datetime_alignment],
            "datetime_padding_left": datetime_left_padding,
            "datetime_padding_right": datetime_right_padding,
            "status_align": status_alignment_map[header_glyph_alignment],
            "status_padding_left": status_padding_left,
            "status_padding_right": status_padding_right,
            "header_height": int(header_height),
            "content_height": content_height,
            "content_item_height": individualItemHeight - 2,
            "content_item_count": self.manager.itemsPerScreenVar,
            "background_alpha": 0,
            "selected_font_hex": self.manager.selectedFontHexVar,
            "deselected_font_hex": self.manager.deselectedFontHexVar,
            "bubble_alpha": 255,
            "bubble_padding_right": self.manager.bubblePaddingVar,
            "content_alignment": content_alignment_map[
                self.manager.global_alignment_var
            ],  # TODO make this change for the different sections
            "list_default_label_long_mode": 1,
            "content_padding_left": content_padding_left,
            "content_width": (
                int(self.manager.deviceScreenWidthVar)
                - (10 if self.manager.version_var == "muOS 2410.1 Banana" else 0)
                - 2
                * (
                    int(self.manager.textPaddingVar)
                    - int(self.manager.bubblePaddingVar)
                )
            ),
            "footer_alpha": 0,
            "footer_background_alpha": 0,
            "footer_pad_top": 0,
            "footer_pad_bottom": 0,
            "bubble_padding_left": int(
                int(self.manager.bubblePaddingVar)
                + (glyph_width / 2)
                + glyph_to_text_pad
            )
            if self.manager.show_glyphs_var
            else self.manager.bubblePaddingVar,
            "list_glyph_alpha": 255 if self.manager.show_glyphs_var else 0,
            "list_text_alpha": 255,
            "navigation_type": 0,
            "content_padding_top": int(self.manager.contentPaddingTopVar)
            - (int(header_height) + 2),
            "grid_navigation_type": 4,
            "grid_background": self.manager.bgHexVar,
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
            "grid_cell_default_background": self.manager.bgHexVar,
            "grid_cell_default_background_alpha": 0,
            "grid_cell_default_border": self.manager.bgHexVar,
            "grid_cell_default_border_alpha": 0,
            "grid_cell_default_image_alpha": 255,
            "grid_cell_default_image_recolour": self.manager.iconHexVar,
            "grid_cell_default_image_recolour_alpha": 255,
            "grid_cell_default_text": self.manager.deselectedFontHexVar,
            "grid_cell_default_text_alpha": 0,
            "grid_cell_focus_background": self.manager.deselectedFontHexVar,
            "grid_cell_focus_background_alpha": int(255 * 0.133),
            "grid_cell_focus_border": (self.manager.deselectedFontHexVar),
            "grid_cell_focus_border_alpha": 0,
            "grid_cell_focus_image_alpha": 255,
            "grid_cell_focus_image_recolour": (self.manager.iconHexVar),
            "grid_cell_focus_image_recolour_alpha": 255,
            "grid_cell_focus_text": (self.manager.selectedFontHexVar),
            "grid_cell_focus_text_alpha": 0,
        }

        missingValues = [
            k for k, v in replacementStringMap["default"].items() if v is None
        ]
        if missingValues:
            missingValuesString = ""
            for n in missingValues:
                missingValuesString += n + "\n"
            raise ValueError(f"Replacement string(s) \n{missingValuesString} not set")

        ## Overrides:

        # horizontal muxlaunch specific options - basically remove all text content and set naviagtion type
        if self.manager.main_menu_style_var != "Vertical":
            replacementStringMap["muxlaunch"] = {
                "bubble_alpha": 0,
                "list_glyph_alpha": 0,
                "list_text_alpha": 0,
                "navigation_type": 4
                if self.manager.horizontal_menu_behaviour_var == "Wrap to Row"
                else 2,
            }

        # muxnetwork Specific settings - account for status at the bottom and show footer

        if self.manager.version_var == "muOS 2410.1 Banana":
            replacementStringMap["muxnetwork"] = {
                "content_height": int(
                    (content_height / int(self.manager.itemsPerScreenVar))
                    * (int(self.manager.itemsPerScreenVar) - 2)
                ),
                "content_item_count": int(self.manager.itemsPerScreenVar) - 2,
                "footer_alpha": 255,
            }
        else:  ## muxnetwork - show the footer
            replacementStringMap["muxnetwork"]["footer_alpha"] = 255

        # muxassign - Force Glyphs on and show footer
        replacementStringMap["muxassign"] = {
            "bubble_padding_left": int(
                int(self.manager.bubblePaddingVar)
                + (glyph_width / 2)
                + glyph_to_text_pad
            ),  # for glyph support
            "list_glyph_alpha": 255,  # for glyph support
            "footer_alpha": 255,
        }

        # muxgov - same as muxassign, but hide footer
        for map in ["muxgov", "muxsearch"]:
            replacementStringMap[map] = replacementStringMap["muxassign"].copy()
            replacementStringMap[map]["footer_alpha"] = 0

        # muxpicker - Cut text off before preview image
        if self.manager.version_var != "muOS 2410.1 Banana":
            max_preview_size = int(int(self.manager.deviceScreenWidthVar) * 0.45)
            if int(self.manager.deviceScreenWidthVar) == 720:
                max_preview_size = 340

            replacementStringMap["muxpicker"]["content_width"] = (
                int(self.manager.deviceScreenWidthVar)
                - max_preview_size
                - 2
                * (
                    int(self.manager.textPaddingVar)
                    - int(self.manager.bubblePaddingVar)
                )
            )

        # muxplore - cut off text if needed for box art
        if int(self.manager.maxBoxArtWidth) > 0:
            replacementStringMap["muxplore"]["content_width"] = (
                int(self.manager.deviceScreenWidthVar)
                - int(self.manager.maxBoxArtWidth)
                - (
                    int(self.manager.textPaddingVar)
                    - int(self.manager.bubblePaddingVar)
                )
            )

            # muxfavourite - same as muxplore
            replacementStringMap["muxfavourite"] = replacementStringMap[
                "muxplore"
            ].copy()

        if int(self.manager.maxBoxArtWidth) > 0:
            replacementStringMap["muxhistory"] = replacementStringMap["muxplore"].copy()

        replacementStringMap["muxstorage"]["footer_alpha"] = 255

        if self.manager.enable_grid_view_explore_var:
            grid_total_height = (
                self.scaled_screen_dimensions[1]
                - self._get_footer_height(
                    self.manager.itemsPerScreenVar,
                    self.scaled_screen_dimensions[1],
                    self.manager.contentPaddingTopVar,
                    self.manager.approxFooterHeightVar,
                )
                - int(self.manager.headerHeightVar)
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
            grid_location_y = int(self.manager.headerHeightVar)
            grid_cell_width = grid_column_width - 2 * cell_inner_padding
            grid_cell_height = grid_row_height - 2 * cell_inner_padding
            grid_cell_size = min(grid_cell_width, grid_cell_height)

            replacementStringMap["muxplore"].update(
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

            grid_image_padding = 10

            system_logos_path = ASSETS_DIR / "System Logos" / "png [5x]"

            temp_system_icons_dir = (
                RESOURCES_DIR / f".TempBuildSystemIconsAMFile{threadNumber}"
            )
            output_system_logos_path = (
                temp_system_icons_dir
                / "run"
                / "muos"
                / "storage"
                / "info"
                / "catalogue"
                / "Folder"
                / "grid"
                / "resolutions"
                / f"{self.manager.deviceScreenWidthVar}x{self.manager.deviceScreenHeightVar}"
            )
            ensure_folder_exists(output_system_logos_path)
            resize_system_logos(
                system_logos_path,
                output_system_logos_path,
                grid_cell_size,
                grid_image_padding,
                circular_grid=False,
            )

        if not "Generating for lanuage on muxlaunch":
            horizontalLogoSize = self._get_horizontal_logo_size(
                Image.open(HORIZONTAL_LOGOS_DIR / "explore.png")
            )
            paddingBetweenLogos = (
                int(self.manager.deviceScreenWidthVar) - (horizontalLogoSize[0] * 4)
            ) / (4 + 1)

            bubble_height = min(
                (int(self.manager.deviceScreenHeightVar) * 36.3) / 480,
                (int(self.manager.deviceScreenWidthVar) * 36.3) / 640,
            )
            effective_text_padding_top = 4

            combined_height = bubble_height + horizontalLogoSize[1]
            heightAbove_logo = (
                int(self.manager.deviceScreenHeightVar) - combined_height
            ) / 2

            grid_total_width = (
                int(self.manager.deviceScreenWidthVar) - paddingBetweenLogos
            )

            grid_column_count = 4
            grid_row_count = 2

            grid_row_height = (
                heightAbove_logo + combined_height + effective_text_padding_top
            )
            grid_column_width = int(grid_total_width / grid_column_count)
            cell_inner_padding = 0
            grid_location_x = paddingBetweenLogos / 2
            grid_location_y = 0
            grid_cell_width = grid_column_width - 2 * cell_inner_padding
            grid_cell_height = grid_row_height - 2 * cell_inner_padding

            replacementStringMap["muxlaunch"] = {
                "grid_location_x": grid_location_x,
                "grid_location_y": grid_location_y,
                "grid_column_count": grid_column_count,
                "grid_row_count": grid_row_count,
                "grid_row_height": grid_row_height,
                "grid_column_width": grid_column_width,
                "grid_cell_width": grid_cell_width,
                "grid_cell_height": grid_cell_height,
                "grid_cell_radius": 0,
                "grid_cell_focus_background_alpha": 0,
                "grid_cell_default_image_alpha": 0,
                "grid_cell_default_image_recolour_alpha": 0,
                "grid_cell_default_text_alpha": 255,
                "grid_cell_focus_image_alpha": 0,
                "grid_cell_focus_image_recolour_alpha": 0,
                "grid_cell_focus_text_alpha": 255,
            }

        for fileName in replacementStringMap.keys():
            shutil.copy2(TEMPLATE_SCHEME_PATH, newSchemeDir / f"{fileName}.txt")
            self.replace_scheme_options(newSchemeDir, fileName, replacementStringMap)

        ensure_folder_exists(temp_build_dir / "image" / "wall")

        if self.manager.include_overlay_var:
            shutil.copy2(
                OVERLAY_DIR
                / f"{self.manager.deviceScreenWidthVar}x{self.manager.deviceScreenHeightVar}"
                / f"{self.manager.selected_overlay_var}.png",
                temp_build_dir / "image" / "overlay.png",
            )

        ## GLYPH STUFF
        ensure_folder_exists(temp_build_dir / "glyph" / "footer")
        ensure_folder_exists(temp_build_dir / "glyph" / "header")

        muosSpaceBetweenItems = 2
        footerHeight = (
            int(self.manager.deviceScreenHeightVar)
            - (individualItemHeight * int(self.manager.itemsPerScreenVar))
            - int(self.manager.contentPaddingTopVar)
            + muosSpaceBetweenItems
        )
        button_height = int(
            (footerHeight - (int(self.manager.VBG_Vertical_Padding_var) * 2)) * (2 / 3)
        )  # Change this if overlayed
        in_bubble_font_size = round(button_height * (24 / 40))

        buttonsToGenerate = ["A", "B", "C", "MENU", "POWER", "X", "Y", "Z"]
        for button in buttonsToGenerate:
            button_image = self.generate_button_glyph_image(
                button,
                selected_font_path,
                accent_hex,
                button_height,
                self.manager.physical_controller_layout_var,
            )
            button_image = button_image.resize(
                (
                    int(button_image.size[0] / self.render_factor),
                    int(button_image.size[1] / self.render_factor),
                ),
                Resampling.LANCZOS,
            )
            button_image.save(
                temp_build_dir / "glyph" / "footer" / f"{button.lower()}.png",
                format="PNG",
            )
        capacities = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        networkGlyphNames = ["network_active", "network_normal"]
        if float(self.manager.header_glyph_height_var) < 10:
            raise ValueError("Header Glyph Height Too Small!")
        elif float(self.manager.header_glyph_height_var) > int(
            self.manager.headerHeightVar
        ):
            raise ValueError("Header Glyph Height Too Large!")
        else:
            heightOfGlyph = int(float(self.manager.header_glyph_height_var))

        for capacity in capacities:
            try:
                capacity_image_path = (
                    GLYPHS_DIR
                    / f"{BatteryStyleOptionsDict[self.manager.battery_style_var]}{capacity}[5x].png"
                )
            except:
                raise Exception("Battery Style not found")
            capacity_image = Image.open(capacity_image_path)
            capacity_image = capacity_image.resize(
                (
                    int(
                        heightOfGlyph
                        * (capacity_image.size[0] / capacity_image.size[1])
                    ),
                    heightOfGlyph,
                ),
                Resampling.LANCZOS,
            )
            capacity_image.save(
                temp_build_dir / "glyph" / "header" / f"capacity_{capacity}.png",
                format="PNG",
            )

            try:
                capacity_charging_image_path = (
                    GLYPHS_DIR
                    / f"{BatteryChargingStyleOptionsDict[self.manager.battery_charging_style_var]}{capacity}[5x].png"
                )
            except:
                raise Exception("Battery Charging Style not found")
            capacity_charging_image = Image.open(capacity_charging_image_path)
            capacity_charging_image = capacity_charging_image.resize(
                (
                    int(
                        heightOfGlyph
                        * (
                            capacity_charging_image.size[0]
                            / capacity_charging_image.size[1]
                        )
                    ),
                    heightOfGlyph,
                ),
                Resampling.LANCZOS,
            )
            capacity_charging_image.save(
                temp_build_dir
                / "glyph"
                / "header"
                / f"capacity_charging_{capacity}.png",
                format="PNG",
            )

        for networkGlyph in networkGlyphNames:
            input_image_path = GLYPHS_DIR / f"{networkGlyph}[5x].png"
            image = Image.open(input_image_path)
            image = image.resize(
                (int(heightOfGlyph * (image.size[0] / image.size[1])), heightOfGlyph),
                Resampling.LANCZOS,
            )
            image.save(
                temp_build_dir / "glyph" / "header" / f"{networkGlyph}.png",
                format="PNG",
            )

        ## FONT STUFF
        font_path = temp_build_dir / "font"
        font_panel_path = font_path / "panel"
        font_footer_path = font_path / "footer"
        font_header_path = font_path / "header"
        font_binary_path = FONTS_DIR / "Binaries"

        ensure_folder_exists(font_panel_path)
        ensure_folder_exists(temp_build_dir / "font" / "footer")
        ensure_folder_exists(temp_build_dir / "font" / "header")

        shutil.copy2(
            font_binary_path / f"BPreplayBold-unhinted-{int(fontSize)}.bin",
            font_panel_path / "default.bin",
        )
        muxarchive_font_size_640 = 17
        muxarchive_font_size = math.floor(
            muxarchive_font_size_640 * (int(self.manager.deviceScreenWidthVar) / 640)
        )
        if fontSize > muxarchive_font_size:
            shutil.copy2(
                font_binary_path
                / f"BPreplayBold-unhinted-{int(muxarchive_font_size)}.bin",
                font_panel_path / "muxarchive.bin",
            )

        muxpicker_font_size_640 = 18
        muxpicker_font_size = math.floor(
            muxpicker_font_size_640 * (int(self.manager.deviceScreenWidthVar) / 640)
        )
        if fontSize > muxpicker_font_size:
            shutil.copy2(
                font_binary_path
                / f"BPreplayBold-unhinted-{int(muxpicker_font_size)}.bin",
                font_panel_path / "muxpicker.bin",
            )

        shutil.copy2(
            font_binary_path / f"BPreplayBold-unhinted-{int(20)}.bin",
            font_path / "default.bin",
        )

        ## FOOTER FONT STUFF
        shutil.copy2(
            font_binary_path / f"BPreplayBold-unhinted-{in_bubble_font_size}.bin",
            font_footer_path / "default.bin",
        )

        ## HEADER FONT STUFF
        headerFontSize = int(
            int(
                (
                    int(int(self.manager.header_text_height_var) * self.render_factor)
                    * (4 / 3)
                )
                / self.render_factor
            )
        )
        shutil.copy2(
            font_binary_path / f"BPreplayBold-unhinted-{headerFontSize}.bin",
            font_header_path / "default.bin",
        )

        res_code = f"{self.screen_dimensions[0]}x{self.screen_dimensions[1]}"

        ## IMAGE STUFF
        temp_image_dir = temp_build_dir / "image"
        self.update_progress(f"Generating boot screen ({res_code})...")
        bootlogoimage = self.generate_boot_screen_with_logo(
            self.manager.bgHexVar,
            self.manager.deselectedFontHexVar,
            self.manager.bubbleHexVar,
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        bootlogoimage.save(
            temp_image_dir / "bootlogo.bmp",
            format="BMP",
        )

        self.update_progress(
            f"Generating boot screen with charging text ({res_code})..."
        )
        chargingimage = self.generate_boot_screen_with_text(
            self.manager.bgHexVar,
            self.manager.deselectedFontHexVar,
            self.manager.iconHexVar,
            "CHARGING...",
            icon_path=ASSETS_DIR / "ChargingLogo[5x].png",
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        chargingimage.save(
            temp_image_dir / "wall" / "muxcharge.png",
            format="PNG",
        )

        self.update_progress(
            f"Generating boot screen with loading text ({res_code})..."
        )
        loadingimage = self.generate_boot_screen_with_text(
            self.manager.bgHexVar,
            self.manager.deselectedFontHexVar,
            self.manager.iconHexVar,
            "LOADING...",
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        loadingimage.save(
            temp_image_dir / "wall" / "muxstart.png",
            format="PNG",
        )

        self.update_progress(
            f"Generating boot screen with shutdown text ({res_code})..."
        )
        shutdownimage = self.generate_boot_screen_with_text(
            self.manager.bgHexVar,
            self.manager.deselectedFontHexVar,
            self.manager.iconHexVar,
            "SHUTTING DOWN...",
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        shutdownimage.save(
            temp_image_dir / "shutdown.png",
            format="PNG",
        )

        self.update_progress(f"Generating boot screen with reboot text ({res_code})...")
        rebootimage = self.generate_boot_screen_with_text(
            self.manager.bgHexVar,
            self.manager.deselectedFontHexVar,
            self.manager.iconHexVar,
            "Rebooting...",
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        rebootimage.save(
            temp_image_dir / "reboot.png",
            format="PNG",
        )

        self.update_progress(f"Generating default background ({res_code})...")
        defaultimage = self.generate_background_image(self.manager.bgHexVar).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        defaultimage.save(
            temp_image_dir / "wall" / "default.png",
            format="PNG",
        )

        # TODO If implimented it would be great to only set these once as a default.png type thing, and then make it work in every menu

        visualbuttonoverlay_B_BACK_A_SELECT = self.generate_static_overlay_image(
            [["B", "BACK"], ["A", "SELECT"]],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )

        self.update_progress(f"Generating muxconfig overlays ({res_code})...")
        if self.manager.version_var == "muOS 2410.1 Banana":
            muxconfig_items = [
                "general",
                "theme",
                "network",
                "service",
                "clock",
                "language",
            ]
        else:
            muxconfig_items = [
                "general",
                "custom",
                "network",
                "service",
                "clock",
                "language",
                "storage",
            ]
        ensure_folder_exists(temp_image_dir / "static" / "muxconfig")
        for item in muxconfig_items:
            visualbuttonoverlay_B_BACK_A_SELECT.save(
                temp_image_dir / "static" / "muxconfig" / f"{item}.png",
                format="PNG",
            )

        self.update_progress(f"Generating muxcustom overlays ({res_code})...")
        if self.manager.version_var == "muOS 2410.1 Banana":
            muxcustom_items = []
        else:
            muxcustom_items = ["theme", "catalogue", "config"]
        ensure_folder_exists(temp_image_dir / "static" / "muxcustom")
        for item in muxcustom_items:
            visualbuttonoverlay_B_BACK_A_SELECT.save(
                temp_image_dir / "static" / "muxcustom" / f"{item}.png",
                format="PNG",
            )

        self.update_progress(f"Generating muxinfo overlays ({res_code})...")
        if self.manager.version_var == "muOS 2410.1 Banana":
            muxinfo_items = ["tracker", "tester", "system", "credit"]
        else:
            muxinfo_items = ["tracker", "tester", "system", "credit"]
        ensure_folder_exists(temp_image_dir / "static" / "muxinfo")
        for item in muxinfo_items:
            visualbuttonoverlay_B_BACK_A_SELECT.save(
                temp_image_dir / "static" / "muxinfo" / f"{item}.png",
                format="PNG",
            )

        self.update_progress(f"Generating muxoption overlays ({res_code})...")
        if self.manager.version_var == "muOS 2410.1 Banana":
            muxoption_items = ["core", "governor"]
        else:
            muxoption_items = ["search", "core", "governor"]
        ensure_folder_exists(temp_image_dir / "static" / "muxoption")
        for item in muxoption_items:
            visualbuttonoverlay_B_BACK_A_SELECT.save(
                temp_image_dir / "static" / "muxoption" / f"{item}.png",
                format="PNG",
            )

        visualbuttonoverlay_A_SELECT = self.generate_static_overlay_image(
            [["A", "SELECT"]],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )

        self.update_progress(f"Generating muxlaunch overlays ({res_code})...")
        if self.manager.version_var == "muOS 2410.1 Banana":
            muxlaunch_items = [
                "explore",
                "favourite",
                "history",
                "apps",
                "info",
                "config",
                "reboot",
                "shutdown",
            ]
        else:
            muxlaunch_items = [
                "explore",
                "favourite",
                "history",
                "apps",
                "info",
                "config",
                "reboot",
                "shutdown",
            ]
        ensure_folder_exists(temp_image_dir / "static" / "muxlaunch")
        for item in muxlaunch_items:
            visualbuttonoverlay_A_SELECT.save(
                temp_image_dir / "static" / "muxlaunch" / f"{item}.png",
                format="PNG",
            )

        visualbuttonoverlay_B_BACK = self.generate_static_overlay_image(
            [["B", "BACK"]],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        visualbuttonoverlay_B_SAVE = self.generate_static_overlay_image(
            [["B", "SAVE"]],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )

        self.update_progress(f"Generating muxtweakgen overlays ({res_code})...")
        if self.manager.version_var == "muOS 2410.1 Banana":
            muxtweakgen_items = [
                "hidden",
                "bgm",
                "sound",
                "startup",
                "colour",
                "brightness",
                "hdmi",
                "power",
                "interface",
                "advanced",
            ]
        else:
            muxtweakgen_items = [
                "hidden",
                "bgm",
                "sound",
                "startup",
                "colour",
                "brightness",
                "hdmi",
                "power",
                "interface",
                "advanced",
            ]
        ensure_folder_exists(temp_image_dir / "static" / "muxtweakgen")
        for item in muxtweakgen_items:
            visualbuttonoverlay_B_SAVE.save(
                temp_image_dir / "static" / "muxtweakgen" / f"{item}.png",
                format="PNG",
            )

        self.update_progress(f"Generating muxhdmi overlays ({res_code})...")
        if self.manager.version_var == "muOS 2410.1 Banana":
            muxhdmi_items = []
        else:
            muxhdmi_items = [
                "enable",
                "resolution",
                "space",
                "depth",
                "range",
                "scan",
                "audio",
            ]
        ensure_folder_exists(temp_image_dir / "static" / "muxhdmi")
        for item in muxhdmi_items:
            visualbuttonoverlay_B_SAVE.save(
                temp_image_dir / "static" / "muxhdmi" / f"{item}.png",
                format="PNG",
            )

        self.update_progress(f"Generating muxpower overlays ({res_code})...")
        if self.manager.version_var == "muOS 2410.1 Banana":
            muxpower_items = ["shutdown", "battery", "idle_display", "idle_sleep"]
        else:
            muxpower_items = ["shutdown", "battery", "idle_display", "idle_sleep"]
        ensure_folder_exists(temp_image_dir / "static" / "muxpower")
        for item in muxpower_items:
            visualbuttonoverlay_B_SAVE.save(
                temp_image_dir / "static" / "muxpower" / f"{item}.png",
                format="PNG",
            )

        self.update_progress(f"Generating muxvisual overlays ({res_code})...")
        if self.manager.version_var == "muOS 2410.1 Banana":
            muxvisual_items = [
                "battery",
                "network",
                "bluetooth",
                "clock",
                "boxart",
                "boxartalign",
                "name",
                "dash",
                "friendlyfolder",
                "thetitleformat",
                "titleincluderootdrive",
                "folderitemcount",
                "counterfolder",
                "counterfile",
                "backgroundanimation",
            ]
        else:
            muxvisual_items = [
                "battery",
                "network",
                "bluetooth",
                "clock",
                "boxart",
                "boxartalign",
                "name",
                "dash",
                "friendlyfolder",
                "thetitleformat",
                "titleincluderootdrive",
                "folderitemcount",
                "folderempty",
                "counterfolder",
                "counterfile",
                "backgroundanimation",
                "launchsplash",
                "blackfade",
            ]
        ensure_folder_exists(temp_image_dir / "static" / "muxvisual")
        for item in muxvisual_items:
            visualbuttonoverlay_B_SAVE.save(
                temp_image_dir / "static" / "muxvisual" / f"{item}.png",
                format="PNG",
            )

        self.update_progress(f"Generating muxtweakadv overlays ({res_code})...")
        if self.manager.version_var == "muOS 2410.1 Banana":
            muxtweakadv_items = [
                "accelerate",
                "swap",
                "thermal",
                "font",
                "volume",
                "brightness",
                "offset",
                "lock",
                "led",
                "theme",
                "retrowait",
                "usbfunction",
                "state",
                "verbose",
                "rumble",
                "hdmi",
                "storage",
            ]
        else:
            muxtweakadv_items = [
                "accelerate",
                "swap",
                "thermal",
                "font",
                "volume",
                "brightness",
                "offset",
                "lock",
                "led",
                "theme",
                "retrowait",
                "usbfunction",
                "state",
                "verbose",
                "rumble",
                "userinit",
                "dpadswap",
                "overdrive",
                "swapfile",
                "cardmode",
            ]
        ensure_folder_exists(temp_image_dir / "static" / "muxtweakadv")
        for item in muxtweakadv_items:
            visualbuttonoverlay_B_SAVE.save(
                temp_image_dir / "static" / "muxtweakadv" / f"{item}.png",
                format="PNG",
            )

        self.update_progress(f"Generating muxwebserv overlays ({res_code})...")
        if self.manager.version_var == "muOS 2410.1 Banana":
            muxwebserv_items = [
                "shell",
                "browser",
                "terminal",
                "sync",
                "resilio",
                "ntp",
            ]
        else:
            muxwebserv_items = [
                "sshd",
                "sftpgo",
                "ttyd",
                "syncthing",
                "rslsync",
                "ntp",
                "tailscaled",
            ]
        ensure_folder_exists(temp_image_dir / "static" / "muxwebserv")
        for item in muxwebserv_items:
            visualbuttonoverlay_B_SAVE.save(
                temp_image_dir / "static" / "muxwebserv" / f"{item}.png",
                format="PNG",
            )

        self.update_progress(f"Generating muxrtc overlays ({res_code})...")
        if self.manager.version_var == "muOS 2410.1 Banana":
            muxrtc_items = [
                "year",
                "month",
                "day",
                "hour",
                "minute",
                "notation",
                "timezone",
            ]
        else:
            muxrtc_items = [
                "year",
                "month",
                "day",
                "hour",
                "minute",
                "notation",
                "timezone",
            ]
        ensure_folder_exists(temp_image_dir / "static" / "muxrtc")
        for item in muxrtc_items:
            visualbuttonoverlay_B_SAVE.save(
                temp_image_dir / "static" / "muxrtc" / f"{item}.png",
                format="PNG",
            )

        self.update_progress(f"Generating muxsysinfo overlays ({res_code})...")
        if self.manager.version_var == "muOS 2410.1 Banana":
            muxsysinfo_items = [
                "version",
                "device",
                "kernel",
                "uptime",
                "cpu",
                "speed",
                "governor",
                "memory",
                "temp",
                "service",
                "capacity",
                "voltage",
            ]
        else:
            muxsysinfo_items = [
                "version",
                "device",
                "kernel",
                "uptime",
                "cpu",
                "speed",
                "governor",
                "memory",
                "temp",
                "service",
                "capacity",
                "voltage",
            ]
        ensure_folder_exists(temp_image_dir / "static" / "muxsysinfo")
        for item in muxsysinfo_items:
            visualbuttonoverlay_B_BACK.save(
                temp_image_dir / "static" / "muxsysinfo" / f"{item}.png",
                format="PNG",
            )

        # TODO REMOVE THIS AS IT DOESNT ALLOW BACKGROUND REPLACEMENT (When Alternative is avaliable)
        # TODO wifi would be cool to have footers for once its possible

        background = self.generate_background_image(bg_hex)

        self.update_progress(f"Generating muxapp and muxtask overlays ({res_code})...")
        visualbuttonoverlay_muxapp = self.generate_static_overlay_image(
            [["B", "BACK"], ["A", "LAUNCH"]],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        )
        altered_background = Image.alpha_composite(
            background, visualbuttonoverlay_muxapp
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        altered_background.save(
            temp_image_dir / "wall" / "muxapp.png",
            format="PNG",
        )
        altered_background.save(
            temp_image_dir / "wall" / "muxtask.png",
            format="PNG",
        )

        self.update_progress(f"Generating muxplore overlays ({res_code})...")
        visualbuttonoverlay_muxplore = self.generate_static_overlay_image(
            [
                ["MENU", "INFO"],
                ["Y", "FAVOURITE"],
                ["X", "REFRESH"],
                ["B", "BACK"],
                ["A", "OPEN"],
            ],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        )
        altered_background = Image.alpha_composite(
            background, visualbuttonoverlay_muxplore
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        altered_background.save(
            temp_image_dir / "wall" / "muxplore.png",
            format="PNG",
        )

        self.update_progress(f"Generating muxfavourite overlays ({res_code})...")
        visualbuttonoverlay_muxfavourite = self.generate_static_overlay_image(
            [["MENU", "INFO"], ["X", "REMOVE"], ["B", "BACK"], ["A", "OPEN"]],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        )
        altered_background = Image.alpha_composite(
            background, visualbuttonoverlay_muxfavourite
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        altered_background.save(
            temp_image_dir / "wall" / "muxfavourite.png",
            format="PNG",
        )

        self.update_progress(f"Generating muxhistory overlays ({res_code})...")
        visualbuttonoverlay_muxhistory = self.generate_static_overlay_image(
            [
                ["MENU", "INFO"],
                ["Y", "FAVOURITE"],
                ["X", "REMOVE"],
                ["B", "BACK"],
                ["A", "OPEN"],
            ],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        )
        altered_background = Image.alpha_composite(
            background, visualbuttonoverlay_muxhistory
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        altered_background.save(
            temp_image_dir / "wall" / "muxhistory.png",
            format="PNG",
        )

        self.update_progress(f"Generating muxtimezone overlays ({res_code})...")
        visualbuttonoverlay_muxtimezone = self.generate_static_overlay_image(
            [["A", "SELECT"]],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        )
        altered_background = Image.alpha_composite(
            background, visualbuttonoverlay_muxtimezone
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        altered_background.save(
            temp_image_dir / "wall" / "muxtimezone.png",
            format="PNG",
        )

        self.update_progress(f"Generating muxpicker overlays ({res_code})...")
        visualbuttonoverlay_muxpicker = self.generate_static_overlay_image(
            [["Y", "SAVE"], ["B", "BACK"], ["A", "SELECT"]],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        )
        altered_background = Image.alpha_composite(
            background, visualbuttonoverlay_muxpicker
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        altered_background.save(
            temp_image_dir / "wall" / "muxpicker.png",
            format="PNG",
        )

        self.update_progress(f"Generating muxlanguage overlays ({res_code})...")
        visualbuttonoverlay_muxlanguage = self.generate_static_overlay_image(
            [["B", "BACK"], ["A", "SELECT"]],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        )
        altered_background = Image.alpha_composite(
            background, visualbuttonoverlay_muxlanguage
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        altered_background.save(
            temp_image_dir / "wall" / "muxlanguage.png",
            format="PNG",
        )

        self.update_progress(f"Generating muxarchive overlays ({res_code})...")
        visualbuttonoverlay_muxarchive = self.generate_static_overlay_image(
            [["B", "BACK"]],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        )
        altered_background = Image.alpha_composite(
            background, visualbuttonoverlay_muxarchive
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        altered_background.save(
            temp_image_dir / "wall" / "muxarchive.png",
            format="PNG",
        )

        self.update_progress(f"Generating muxnetprofile overlays ({res_code})...")
        visualbuttonoverlay_muxnetprofile = self.generate_static_overlay_image(
            [["Y", "REMOVE"], ["X", "SAVE"], ["B", "BACK"], ["A", "LOAD"]],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        )
        altered_background = Image.alpha_composite(
            background, visualbuttonoverlay_muxnetprofile
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        altered_background.save(
            temp_image_dir / "wall" / "muxnetprofile.png",
            format="PNG",
        )

        self.update_progress(f"Generating muxnetscan overlays ({res_code})...")
        visualbuttonoverlay_muxnetscan = self.generate_static_overlay_image(
            [["X", "RESCAN"], ["B", "BACK"], ["A", "USE"]],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        )
        altered_background = Image.alpha_composite(
            background, visualbuttonoverlay_muxnetscan
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        altered_background.save(
            temp_image_dir / "wall" / "muxnetscan.png",
            format="PNG",
        )

        self.update_progress(f"Generating muxgov overlays ({res_code})...")
        visualbuttonoverlay_muxgov = self.generate_static_overlay_image(
            [
                ["Y", "RECURSIVE"],
                ["X", "DIRECTORY"],
                ["A", "INDIVIDUAL"],
                ["B", "BACK"],
            ],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        )
        altered_background = Image.alpha_composite(
            background, visualbuttonoverlay_muxgov
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        altered_background.save(
            temp_image_dir / "wall" / "muxgov.png",
            format="PNG",
        )

        self.update_progress(f"Generating muxsearch overlays ({res_code})...")
        visualbuttonoverlay_muxsearch = self.generate_static_overlay_image(
            [["X", "CLEAR"], ["B", "BACK"], ["A", "SELECT"]],
            selected_font_path,
            self.manager.footerBubbleHexVar,
            lhsButtons=[["POWER", "SLEEP"]],
        )
        altered_background = Image.alpha_composite(
            background, visualbuttonoverlay_muxsearch
        ).resize(
            self.screen_dimensions,
            Resampling.LANCZOS,
        )
        altered_background.save(
            temp_image_dir / "wall" / "muxsearch.png",
            format="PNG",
        )

        # itemsList = []
        # if self.manager.version_var[0:9] == "muOS 2410":
        #     workingMenus = MENU_LISTING_2410_X

        # else:
        #     raise ValueError("You Haven't Selected a muOS Version")

        # workingMenus = [
        #     [
        #         "muxlaunch",
        #         [
        #             ["Content Explorer", "explore"],
        #             ["Favourites", "favourite"],
        #             ["History", "history"],
        #             ["Applications", "apps"],
        #             ["Information", "info"],
        #             ["Configuration", "config"],
        #             ["Reboot Device", "reboot"],
        #             ["Shutdown Device", "shutdown"],
        #         ],
        #     ]
        # ]

        # for index, menu in enumerate(workingMenus):
        #     itemsList.append([])
        #     for item in menu[1]:
        #         (itemsList[index].append([item[0], "Menu", item[1]]),)

        # preview_theme_generator = PreviewThemeGenerator(self.manager, self.render_factor)
        # for index, menu in enumerate(workingMenus):
        #     if menu[0] == "muxdevice":
        #         ContinuousFolderImageGen(
        #             progress_bar,
        #             menu[0],
        #             itemsList[index],
        #             textPadding,
        #             rectanglePadding,
        #             ItemsPerScreen,
        #             bg_hex,
        #             selected_font_hex,
        #             deselected_font_hex,
        #             bubble_hex,
        #             self.render_factor,
        #             temp_image_dir / "static",
        #             self.manager,
        #             threadNumber=threadNumber,
        #         )
        #     elif menu[0] == "muxlaunch":
        #         if self.manager.main_menu_style_var == "Horizontal":
        #             HorizontalMenuGen(
        #                 progress_bar,
        #                 menu[0],
        #                 itemsList[index],
        #                 bg_hex,
        #                 selected_font_hex,
        #                 deselected_font_hex,
        #                 bubble_hex,
        #                 icon_hex,
        #                 self.render_factor,
        #                 temp_image_dir / "static",
        #                 variant="Horizontal",
        #                 self.manager=self.manager,
        #                 threadNumber=threadNumber,
        #             )
        #         elif self.manager.main_menu_style_var == "Alt-Horizontal":
        #             HorizontalMenuGen(
        #                 progress_bar,
        #                 menu[0],
        #                 itemsList[index],
        #                 bg_hex,
        #                 selected_font_hex,
        #                 deselected_font_hex,
        #                 bubble_hex,
        #                 icon_hex,
        #                 self.render_factor,
        #                 temp_image_dir / "static",
        #                 variant="Alt-Horizontal",
        #                 self.manager=self.manager,
        #                 threadNumber=threadNumber,
        #             )

        #     else:
        #         ContinuousFolderImageGen(
        #             progress_bar,
        #             menu[0],
        #             itemsList[index],
        #             textPadding,
        #             rectanglePadding,
        #             ItemsPerScreen,
        #             bg_hex,
        #             selected_font_hex,
        #             deselected_font_hex,
        #             bubble_hex,
        #             self.render_factor,
        #             temp_image_dir / "static",
        #             self.manager,
        #             threadNumber=threadNumber,
        #         )
        # fakeprogressbar = {"value": 0}
        # fakeprogressbar["maximum"] = 1
        # if self.manager.main_menu_style_var == "Horizontal":
        #     previewImage = preview_theme_generator.generate_horizontal_menu_image(
        #         fakeprogressbar,
        #         0,
        #         self.manager.bgHexVar,
        #         self.manager.selectedFontHexVar,
        #         self.manager.deselectedFontHexVar,
        #         self.manager.bubbleHexVar,
        #         self.manager.iconHexVar,
        #         transparent=False,
        #     )
        # elif self.manager.main_menu_style_var == "Alt-Horizontal":
        #     previewImage = theme_generator.generate_alt_horizontal_menu(
        #         fakeprogressbar,
        #         0,
        #         self.manager.bgHexVar,
        #         self.manager.selectedFontHexVar,
        #         self.manager.deselectedFontHexVar,
        #         self.manager.bubbleHexVar,
        #         self.manager.iconHexVar,
        #         transparent=False,
        #     )
        # elif self.manager.main_menu_style_var == "Vertical":
        #     previewImage = preview_theme_generator.generate_vertical_menu_image(
        #         fakeprogressbar,
        #         0,
        #         "muxlaunch",
        #         itemsList[index][0 : int(self.manager.itemsPerScreenVar)],
        #         int(self.manager.textPaddingVar),
        #         int(self.manager.bubblePaddingVar),
        #         int(self.manager.itemsPerScreenVar),
        #         self.manager.bgHexVar,
        #         self.manager.selectedFontHexVar,
        #         self.manager.deselectedFontHexVar,
        #         self.manager.bubbleHexVar,
        #         transparent=False,
        #     )
        # preview_size = (
        #     int(0.45 * int(self.manager.deviceScreenWidthVar)),
        #     int(0.45 * int(self.manager.deviceScreenHeightVar)),
        # )
        # if (
        #     int(self.manager.deviceScreenWidthVar) == 720
        #     and int(self.manager.deviceScreenHeightVar) == 720
        # ):
        #     preview_size = (340, 340)
        # smallPreviewImage = previewImage.resize(preview_size, Resampling.LANCZOS)
        # smallPreviewImage.save(temp_build_dir / "preview.png")
        # if self.manager.developer_preview_var:
        #     developerPreviewImage = previewImage.resize(
        #         (int(self.manager.deviceScreenWidthVar), int(self.manager.deviceScreenHeightVar)),
        #         Resampling.LANCZOS,
        #     )
        #     developerPreviewImage.save(
        #         RESOURCES_DIR
        #         / f"TempPreview{threadNumber}[{self.manager.deviceScreenWidthVar}x{self.manager.deviceScreenHeightVar}].png",
        #     )

    def replace_scheme_options(
        self, newSchemeDir: Path, fileName: str, replacementStringMap: dict[str, Any]
    ) -> None:
        file_path = newSchemeDir / f"{fileName}.txt"
        replacements = {
            stringToBeReplaced: replacementStringMap[fileName].get(
                stringToBeReplaced, defaultValue
            )
            for stringToBeReplaced, defaultValue in replacementStringMap[
                "default"
            ].items()
        }

        with file_path.open("rb") as file:
            file_contents = file.read()

        # Replace the occurrences of the search_string with replace_string in binary data
        new_contents = file_contents.decode().format(**replacements)

        # Write the new content back to the file in binary mode
        with file_path.open("wb") as file:
            file.write(new_contents.encode())
