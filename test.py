from pathlib import Path
import random

from PIL import Image

from src.muos_minuify.utils import (
    delete_folder,
    read_json,
    ensure_folder_exists,
)
from src.muos_minuify.scheme import SchemeRenderer
from src.muos_minuify.settings import SettingsManager
from src.muos_minuify.generator import ThemeGenerator
from src.muos_minuify.generator.preview import ThemePreviewGenerator

TEST_PATH = Path("test_images")

DEVICES = [
    "Other [640x480]",
    "RG CubeXX [720x720]",
    "RG34XX [720x480]",
    "576p [720x576]",
    "HD [1280x720]",
    "Full HD [1920x1080]",
]

BUTTONS = [
    "A",
    "B",
    "X",
    "Y",
    "L1",
    "R1",
    "L2",
    "R2",
    "L3",
    "R3",
    "SELECT",
    "START",
    "MENU",
    "POWER",
    "VOL+",
    "VOL-",
    "RESET",
]

EFFECTS = [
    "SLEEP",
    "BACK",
    "LAUNCH",
    "INFO",
    "REMOVE",
    "OPEN",
    "SELECT",
    "RECURSIVE",
    "DIRECTORY",
    "INDIVIDUAL",
    "FAVOURITE",
    "SAVE",
    "LOAD",
    "RESCAN",
    "USE",
    "REFRESH",
    "CLEAR",
    "LAUNCH",
]

COLOR_SCHEMES = [
    {  # catppuccin latte sapphire
        "bgHexVar": "#eff1f5",
        "selectedFontHexVar": "#209fb5",
        "deselectedFontHexVar": "#4c4f69",
        "footerBubbleHexVar": "#209fb5",
        "iconHexVar": "#209fb5",
        "batteryChargingHexVar": "#40a02b",
    },
    {  # catppuccin frappe mauve
        "bgHexVar": "#303446",
        "selectedFontHexVar": "#ca9ee6",
        "deselectedFontHexVar": "#c6d0f5",
        "footerBubbleHexVar": "#ca9ee6",
        "iconHexVar": "#ca9ee6",
        "batteryChargingHexVar": "#a6d189",
    },
    {  # catppuccin macchiato yellow
        "bgHexVar": "#24273a",
        "selectedFontHexVar": "#eed49f",
        "deselectedFontHexVar": "#cad3f5",
        "footerBubbleHexVar": "#eed49f",
        "iconHexVar": "#eed49f",
        "batteryChargingHexVar": "#a6da95",
    },
    {  # catppuccin mocha red
        "bgHexVar": "#1e1e2e",
        "selectedFontHexVar": "#f38ba8",
        "deselectedFontHexVar": "#cdd6f4",
        "footerBubbleHexVar": "#f38ba8",
        "iconHexVar": "#f38ba8",
        "batteryChargingHexVar": "#a6e3a1",
    },
]

THEMES = {
    "latte": {
        "bgHexVar": "#eff1f5",
        "deselectedFontHexVar": "#4c4f69",
        "batteryChargingHexVar": "#40a02b",
        "colors": {
            "rosewater": "#dc8a78",
            "flamingo": "#dd7878",
            "pink": "#ea76cb",
            "mauve": "#8839ef",
            "red": "#d20f39",
            "maroon": "#e64553",
            "peach": "#fe640b",
            "yellow": "#df8e1d",
            "green": "#40a02b",
            "teal": "#179299",
            "sky": "#04a5e5",
            "sapphire": "#209fb5",
            "blue": "#1e66f5",
            "lavender": "#7287fd",
        },
    },
    "frappe": {
        "bgHexVar": "#303446",
        "deselectedFontHexVar": "#4c4f69",
        "batteryChargingHexVar": "#a6d189",
        "colors": {
            "rosewater": "#f2d5cf",
            "flamingo": "#eebebe",
            "pink": "#f4b8e4",
            "mauve": "#ca9ee6",
            "red": "#e78284",
            "maroon": "#ea999c",
            "peach": "#ef9f76",
            "yellow": "#e5c890",
            "green": "#a6d189",
            "teal": "#81c8be",
            "sky": "#99d1db",
            "sapphire": "#85c1dc",
            "blue": "#8caaee",
            "lavender": "#babbf1",
        },
    },
    "macchiato": {
        "bgHexVar": "#24273a",
        "deselectedFontHexVar": "#cad3f5",
        "batteryChargingHexVar": "#a6da95",
        "colors": {
            "rosewater": "#f4dbd6",
            "flamingo": "#f0c6c6",
            "pink": "#f5bde6",
            "mauve": "#c6a0f6",
            "red": "#ed8796",
            "maroon": "#ee99a0",
            "peach": "#f5a97f",
            "yellow": "#eed49f",
            "green": "#a6da95",
            "teal": "#8bd5ca",
            "sky": "#91d7e3",
            "sapphire": "#7dc4e4",
            "blue": "#8aadf4",
            "lavender": "#b7bdf8",
        },
    },
    "mocha": {
        "bgHexVar": "#1e1e2e",
        "deselectedFontHexVar": "#cdd6f4",
        "batteryChargingHexVar": "#a6e3a1",
        "colors": {
            "rosewater": "#f5e0dc",
            "flamingo": "#f2cdcd",
            "pink": "#f5c2e7",
            "mauve": "#cba6f7",
            "red": "#f38ba8",
            "maroon": "#eba0ac",
            "peach": "#fab387",
            "yellow": "#f9e2af",
            "green": "#a6e3a1",
            "teal": "#94e2d5",
            "sky": "#89dceb",
            "sapphire": "#74c7ec",
            "blue": "#89b4fa",
            "lavender": "#bdbefe",
        },
    },
}


def color_test(manager: SettingsManager, generator: ThemeGenerator) -> None:
    left_buttons = [
        ("POWER", "SLEEP"),
    ]
    right_buttons = [
        ("A", "SELECT"),
        ("B", "BACK"),
    ]

    for theme_name, theme_def in THEMES.items():
        for key, value in theme_def.items():
            if key == "colors":
                continue

            manager.set_value(key, value)

        colors = theme_def["colors"]
        for base_name, base_color in colors.items():
            manager.set_value("selectedFontHexVar", base_color)
            manager.set_value("iconHexVar", base_color)

            for footer_name, footer_color in colors.items():
                manager.set_value("footerBubbleHexVar", footer_color)

                wall_img = generator.generate_wall_image(right_buttons, left_buttons)
                wall_img.save(
                    TEST_PATH / f"wall_test-{theme_name}-{base_name}-{footer_name}.png"
                )


def random_test(
    manager: SettingsManager,
    generator: ThemeGenerator,
    num_generations: int,
    max_left_buttons: int,
    max_right_buttons: int,
) -> None:
    for i in range(num_generations):
        manager.set_value("device_type_var", random.choice(DEVICES))

        left_buttons = [
            (random.choice(BUTTONS), random.choice(EFFECTS))
            for _ in range(random.randint(1, max_left_buttons))
        ]
        right_buttons = [
            (random.choice(BUTTONS), random.choice(EFFECTS))
            for _ in range(random.randint(1, max_right_buttons))
        ]

        wall_img = generator.generate_wall_image(right_buttons, left_buttons)
        wall_img.save(
            TEST_PATH
            / f"wall_test-{manager.deviceScreenWidthVar}x{manager.deviceScreenHeightVar}-{i}.png"
        )


def single_test(
    manager: SettingsManager, generator: ThemeGenerator, renderer: SchemeRenderer
) -> None:
    defs_path = Path("Assets/menu_definitions.json")
    menu_defs = read_json(defs_path)
    defaults = menu_defs.get("default", {})

    resolution = f"{manager.deviceScreenWidthVar}x{manager.deviceScreenHeightVar}"

    res_path = TEST_PATH / resolution
    scheme_path = res_path / "scheme"
    image_path = res_path / "image"
    wall_path = image_path / "wall"
    static_path = image_path / "static"
    ensure_folder_exists(res_path)
    ensure_folder_exists(scheme_path)
    ensure_folder_exists(image_path)
    ensure_folder_exists(wall_path)
    ensure_folder_exists(static_path)

    preview_generator = ThemePreviewGenerator(manager)
    preview_right_buttons = menu_defs.get("muxlaunch", {}).get(
        "right_guides", menu_defs["default"].get("right_guides", [])
    )
    preview_left_buttons = menu_defs.get("muxlaunch", {}).get(
        "left_guides", menu_defs["default"].get("left_guides", [])
    )
    preview_generator.generate_launcher_image(
        preview_right_buttons, preview_left_buttons, "explore"
    ).save(res_path / "preview.png")

    for name, menu_def in menu_defs.items():
        if (name[:3] == "mux" or name == "default") and (
            rendered_scheme := renderer.render(name)
        ):
            with (scheme_path / f"{name}.txt").open("w") as f:
                f.write(rendered_scheme)

        if name == "bootlogo":
            boot_image = generator.generate_boot_logo_image()
            boot_image.save(image_path / f"{name}.bmp")
            continue
        elif name == "default":
            background_image = generator.generate_background_image()
            background_image.save(wall_path / "default.png")
            continue

        if not menu_def:
            continue
        elif caption_text := menu_def.get("caption_text"):
            icon_path = menu_def.get("icon_path")
            boot_image = generator.generate_boot_text_image(
                caption_text, Path(icon_path) if icon_path else None
            )
            boot_image.save(
                (wall_path if name[:3] == "mux" else image_path) / f"{name}.png"
            )
            continue

        def_right_buttons = menu_def.get(
            "right_guides", defaults.get("right_guides", [])
        )
        def_left_buttons = menu_def.get("left_guides", defaults.get("left_guides", []))

        if len(menu_items := menu_def.get("menu_items", [])) > 1:
            menu_path = static_path / name
            ensure_folder_exists(menu_path)

            for item, item_def in menu_items.items():
                right_buttons = item_def.get("right_guides", def_right_buttons)
                left_buttons = item_def.get("left_guides", def_left_buttons)

                static_img = (
                    generator.generate_launcher_image(right_buttons, left_buttons, item)
                    if name == "muxlaunch"
                    else generator.generate_static_image(right_buttons, left_buttons)
                )
                static_img.save(menu_path / f"{item}.png")
        else:
            wall_img = generator.generate_wall_image(
                def_right_buttons, def_left_buttons
            )
            wall_img.save(wall_path / f"{name}.png")


def full_test(
    manager: SettingsManager, generator: ThemeGenerator, renderer: SchemeRenderer
) -> None:
    for device in DEVICES:
        manager.set_value("device_type_var", device)
        single_test(manager, generator, renderer)


if __name__ == "__main__":
    manager = SettingsManager()
    manager.load()

    generator = ThemeGenerator(manager)
    renderer = SchemeRenderer(manager)

    delete_folder(TEST_PATH)
    ensure_folder_exists(TEST_PATH)

    # single_test(manager, generator, renderer)
    print(renderer.render("muxsearch"))
