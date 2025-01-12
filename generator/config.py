import json
from pathlib import Path

from ..generator import defaults
from .constants import CONFIG_PATH, PREMADE_THEMES_PATH


class Config:  # TODO delete unneeded variables
    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self.deviceScreenHeightVar = 480
        self.deviceScreenWidthVar = 640
        self.textPaddingVar = 40
        self.header_glyph_horizontal_left_padding_var = 10
        self.header_glyph_horizontal_right_padding_var = 10
        self.header_glyph_height_var = 20
        self.header_glyph_bubble_height_var = 35
        self.header_text_bubble_height_var = 35
        self.header_text_height_var = 20
        self.clockHorizontalLeftPaddingVar = 10
        self.clockHorizontalRightPaddingVar = 10
        self.pageTitlePaddingVar = 10
        self.text_padding_entry = 40
        self.VBG_Vertical_Padding_entry = 15
        self.VBG_Horizontal_Padding_entry = 15
        self.bubblePaddingVar = 20
        self.rectangle_padding_entry = 20
        self.itemsPerScreenVar = 7
        self.items_per_screen_entry = 7
        self.approxFooterHeightVar = 80
        self.contentPaddingTopVar = 44
        self.headerHeightVar = 44
        self.content_padding_top_entry = 44
        self.font_size_var = 24
        self.custom_font_size_entry = "24"
        self.bgHexVar = "000000"
        self.background_hex_entry = "000000"
        self.selectedFontHexVar = "000000"
        self.selected_font_hex_entry = "000000"
        self.deselectedFontHexVar = "ffffff"
        self.deselected_font_hex_entry = "ffffff"
        self.bubbleHexVar = "ffffff"
        self.bubble_hex_entry = "ffffff"
        self.iconHexVar = "ffffff"
        self.batteryChargingHexVar = "2eb774"
        self.icon_hex_entry = "ffffff"
        self.include_overlay_var = False
        self.show_glyphs_var = False
        self.show_clock_bubbles_var = False
        self.show_glyphs_bubbles_var = False
        self.join_header_bubbles_var = False
        self.enable_game_switcher_var = False
        self.enable_grid_view_explore_var = False
        self.alternate_menu_names_var = False
        self.remove_right_menu_guides_var = False
        self.remove_left_menu_guides_var = False
        self.boxArtPaddingVar = 0
        self.folderBoxArtPaddingVar = 0
        self.box_art_directory_path = ""
        self.maxBoxArtWidth = 0
        self.roms_directory_path = ""
        self.application_directory_path = ""
        self.previewConsoleNameVar = "Nintendo Game Boy"
        self.show_hidden_files_var = False
        self.override_folder_box_art_padding_var = False
        self.page_by_page_var = False
        self.transparent_text_var = False
        self.version_var = "muOS 2410.3 AW BANANA"
        self.device_type_var = "Other [640x480]"
        self.global_alignment_var = "Left"
        self.selected_overlay_var = "muOS Default CRT Overlay"
        self.physical_controler_layout_var = "Nintendo"
        self.muos_button_swap_var = "Retro"
        self.main_menu_style_var = "Horizontal"
        self.horizontal_menu_behaviour_var = "Wrap to Row"
        self.battery_charging_style_var = "Default"
        self.battery_style_var = "Default"
        self.clock_format_var = "24 Hour"
        self.clock_alignment_var = "Left"
        self.header_glyph_alignment_var = "Right"
        self.page_title_alignment_var = "Centre"
        self.am_theme_directory_path = ""
        self.theme_directory_path = ""
        self.catalogue_directory_path = ""
        self.name_json_path = ""
        self.background_image_path = ""
        self.bootlogo_image_path = ""
        self.alt_font_filename = defaults.DEFAULT_FONT_FILENAME
        self.alt_text_filename = defaults.DEFAULT_ALT_TEXT_FILENAME
        self.use_alt_font_var = False
        self.use_custom_background_var = False
        self.use_custom_bootlogo_var = False
        self.theme_name_entry = "MinUIfied - Default Theme"
        self.amThemeName = "MinUIfied - Default AM Theme"
        self.am_ignore_theme_var = False
        self.am_ignore_cd_var = False
        self.advanced_error_var = False
        self.developer_preview_var = False
        self.show_file_counter_var = False
        self.show_console_name_var = False
        self.show_charging_battery_var = False
        self.load_config()

    def load_config(self):
        if self.config_path.exists():
            with self.config_path.open("r") as file:
                config_data = json.load(file)
                self.__dict__.update(config_data)
        else:
            self.save_config()

    def save_config(self):
        with self.config_path.open("w") as file:
            json.dump(self.__dict__, file, indent=4)

    def load_premade_themes(self, themes_path=PREMADE_THEMES_PATH):
        themes = []

        if themes_path.exists():
            with themes_path.open("r") as file:
                themes_data = json.load(file)
                themes = themes_data.get("themes", [])

        return themes

    def apply_theme(self, theme):
        # Update the Config object with all key-value pairs from the theme
        self.__dict__.update(theme)
        self.save_config()


global_config = Config()
