from .utils import find_base_dirs


BASE_DIR, RESOURCES_DIR = find_base_dirs()

ASSETS_DIR = BASE_DIR / "Assets"
FONTS_DIR = ASSETS_DIR / "Font"
GLYPHS_DIR = ASSETS_DIR / "glyphs"
HORIZONTAL_LOGOS_DIR = ASSETS_DIR / "Horizontal Logos"
BUTTON_GLYPHS_DIR = ASSETS_DIR / "Button Glyphs"
OVERLAY_DIR = ASSETS_DIR / "Overlays"
TEMPLATE_SCHEME_DIR = BASE_DIR / "Template Scheme"
TEMPLATE_SCHEME_FILENAME = "template.txt"
TEMPLATE_SCHEME_PATH = TEMPLATE_SCHEME_DIR / TEMPLATE_SCHEME_FILENAME
THEME_SHELL_DIR = BASE_DIR / "Theme Shell"
SYSTEM_LOGOS_DIR = ASSETS_DIR / "System Logos" / "png [5x]"

CONFIG_FILENAME = "MinUIThemeGeneratorConfig.json"
CONFIG_PATH = BASE_DIR / CONFIG_FILENAME

PREMADE_THEMES_FILENAME = "PremadeThemes.json"
PREMADE_THEMES_PATH = BASE_DIR / PREMADE_THEMES_FILENAME

BASE_SETTINGS_PATH = ASSETS_DIR / "base_settings.json"
MENU_DEFINITIONS_PATH = ASSETS_DIR / "menu_definitions.json"
USER_SETTINGS_PATH = BASE_DIR / "settings.json"
LEGACY_SETTINGS_PATH = BASE_DIR / "MinUIThemeGeneratorConfig.json"

BatteryStyleOptionsDict = {
    "Default": "capacity_",
    "Percentage": "percentage_capacity_",
    "Alt Percentage": "alt_percentage_capacity_",
}
BatteryChargingStyleOptionsDict = {
    "Default": "capacity_",
    "Percentage": "percentage_capacity_",
    "Percentage Lightning": "percentage_capacity_charging_",
    "Alt Percentage": "alt_percentage_capacity_",
    "Alt Percentage Lightning": "alt_percentage_capacity_charging_",
    "Lightning 1": "capacity_charging_",
    "Lightning 2": "alt1_capacity_charging_",
    "Lightning 3": "alt2_capacity_charging_",
}

DEVICE_TYPE_OPTIONS = [
    "Other [640x480]",
    "RG CubeXX [720x720]",
    "RG34XX [720x480]",
    "576p [720x576]",
    "HD [1280x720]",
    "Full HD [1920x1080]",
]

MENU_LISTING_2410_X: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    (
        "muxapp",
        (
            ("Archive Manager", "Archive Manager"),
            ("Dingux Commander", "Dingux Commander"),
            ("Flip Clock", "Flip Clock"),
            ("GMU Music Player", "GMU Music Player"),
            ("Moonlight", "Moonlight"),
            ("PortMaster", "PortMaster"),
            ("PPSSPP", "PPSSPP"),
            ("RetroArch", "RetroArch"),
            ("Simple Terminal", "Simple Terminal"),
            ("Task Toolkit", "Task Toolkit"),
        ),
    ),
    (
        "muxconfig",
        (
            ("General Settings", "general"),
            ("Theme Picker", "theme"),
            ("Wi-Fi Settings", "network"),
            ("Web Services", "service"),
            ("Date and Time", "clock"),
            ("Device Type", "device"),
        ),
    ),
    (
        "muxdevice",
        (
            ("RG35XX - H", "rg35xx-h"),
            ("RG35XX - Plus", "rg35xx-plus"),
            ("RG35XX - SP", "rg35xx-sp"),
            ("RG35XX - 2024", "rg35xx-2024"),
        ),
    ),
    (
        "muxinfo",
        (
            ("Input Tester", "tester"),
            ("System Details", "system"),
            ("Supporters", "credit"),
        ),
    ),
    (
        "muxlaunch",
        (
            ("Content Explorer", "explore"),
            ("Favourites", "favourite"),
            ("History", "history"),
            ("Applications", "apps"),
            ("Information", "info"),
            ("Configuration", "config"),
            ("Reboot Device", "reboot"),
            ("Shutdown Device", "shutdown"),
        ),
    ),
)

MENU_LISTING_MAP: dict[str, tuple[tuple[str, tuple[tuple[str, str], ...]], ...]] = {
    "2410": MENU_LISTING_2410_X,
}
