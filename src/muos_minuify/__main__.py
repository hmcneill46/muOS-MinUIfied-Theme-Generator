from functools import partial
import json
import tkinter as tk
from tkinter import ttk

from .adapter import TkinterSettingsAdapter
from .commands import (
    select_color,
    select_bootlogo_image_path,
    select_background_image_path,
    select_alt_font_path,
    select_theme_directory_path,
    start_theme_task,
    start_bulk_theme_task,
)
from .settings import SettingsManager

from PIL import (
    ImageTk,
    Image,
    ImageDraw,
)
from PIL.Image import Resampling

from .app import ThemeGeneratorApp
from .color_utils import *
from .constants import (
    BASE_DIR,
    BASE_SETTINGS_PATH,
    USER_SETTINGS_PATH,
    MENU_LISTING_2410_X,
)
from .generator.preview import ThemePreviewGenerator

Image.MAX_IMAGE_PIXELS = None


def getAlternateMenuNameDict():
    ALT_TEXT_PATH = BASE_DIR / manager.alt_text_filename
    data = getDefaultAlternateMenuNameData()

    if ALT_TEXT_PATH.exists():
        with ALT_TEXT_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
        data = {key.lower(): value for key, value in data.items()}
        return data

    return data


def getDefaultAlternateMenuNameData():
    defaultMenuNameMap = {
        "content explorer": "Games",
        "applications": "Utilities",
        "power": "POWER",
        "sleep": "SLEEP",
        "menu": "MENU",
        "help": "HELP",
        "back": "BACK",
        "okay": "OKAY",
        "confirm": "CONFIRM",
        "launch": "LAUNCH",
        "charging...": "Charging...",
        "loading...": "Loading...",
        "rebooting...": "Rebooting...",
        "shutting down...": "Shutting Down...",
    }

    for section in MENU_LISTING_2410_X:
        if section[0].startswith("mux"):
            for n in section[1]:
                defaultMenuNameMap[n[0].lower()] = n[0]

    return defaultMenuNameMap


def update_image_label(image_label: ttk.Label, pil_image: Image.Image) -> None:
    tk_image = ImageTk.PhotoImage(pil_image)
    image_label.config(image=tk_image)
    image_label.image = tk_image
    # image_label.clear()


def remove_image_from_label(image_label: ttk.Label) -> None:
    image_label.config(image="")


def get_current_image(image_label: ttk.Label) -> Image.Image:
    # Retrieve the PhotoImage object from the label
    try:
        tk_image = image_label.image
    except:
        tk_image = None
    if tk_image is None:
        return None

    # Convert the PhotoImage object back to a PIL image
    width = tk_image.width()
    height = tk_image.height()
    pil_image = Image.new("RGB", (width, height))
    pil_image.paste(ImageTk.getimage(tk_image), (0, 0))

    return pil_image


def outline_image_with_inner_gap(
    image: Image.Image,
    outline_color: tuple[int, int, int] = (255, 0, 0),
    outline_width: int = 5,
    gap: int = 5,
):
    # Calculate the size of the new image with the outline and the gap
    new_width = image.width + 2 * (outline_width + gap)
    new_height = image.height + 2 * (outline_width + gap)

    # Create a new image with the appropriate size and background color (optional)
    outlined_image = Image.new("RGB", (new_width, new_height), (0, 0, 0))

    # Create a drawing context for the new image
    draw = ImageDraw.Draw(outlined_image)

    # Draw the outer rectangle for the red outline
    draw.rectangle(
        [0, 0, new_width - 1, new_height - 1],
        outline=outline_color,
        width=outline_width,
    )

    # Paste the original image at the centre of the new image, accounting for the outline width and gap
    outlined_image.paste(image, (outline_width + gap, outline_width + gap))

    final_image = outlined_image.resize((image.width, image.height), Image.LANCZOS)

    return final_image


def map_value(
    value: float | int,
    x_min: float | int,
    x_max: float | int,
    y_min: float | int,
    y_max: float | int,
) -> float | int:
    # Calculate the proportion of the value within the input range
    proportion = (value - x_min) / (x_max - x_min)

    # Map this proportion to the output range
    mapped_value = y_min + proportion * (y_max - y_min)

    return mapped_value


def on_change(app: ThemeGeneratorApp, generator: ThemePreviewGenerator, *args) -> None:
    # global menuNameMap
    # menuNameMap = getAlternateMenuNameDict()

    screen_width = app.manager.deviceScreenWidthVar
    screen_height = app.manager.deviceScreenHeightVar
    aspect_ratio = screen_width / screen_height

    preview_width = app.get_preview_width()
    preview_height = preview_width / aspect_ratio
    if not preview_width or not preview_height:
        return

    preview_size = (round(preview_width), round(preview_height))

    preview_theme_generator = ThemePreviewGenerator(app.manager)

    content_preview = preview_theme_generator.generate_launcher_image(
        [("A", "SELECT")]
    ).resize(preview_size, Resampling.LANCZOS)
    info_preview = preview_theme_generator.generate_launcher_image(
        [("A", "SELECT")], selected_item="info"
    ).resize(preview_size, Resampling.LANCZOS)

    update_image_label(app.image_label1, content_preview)
    update_image_label(app.image_label2, info_preview)

    if app.manager.main_menu_style_var != "Vertical":
        list_preview = preview_theme_generator.generate_launcher_image(
            [("A", "SELECT")],
            selected_item="explore",
            variant="Vertical",
        ).resize(preview_size, Resampling.LANCZOS)
        update_image_label(app.image_label3, list_preview)
    else:
        app.image_label3.config(image="")


# menuNameMap = getAlternateMenuNameDict()


def main():
    root = tk.Tk()

    commands_map = {
        "select_color": select_color,
        "select_bootlogo_image_path": select_bootlogo_image_path,
        "select_background_image_path": select_background_image_path,
        "select_alt_font_path": select_alt_font_path,
        "select_theme_directory_path": select_theme_directory_path,
        "start_theme_task": start_theme_task,
        "start_bulk_theme_task": start_bulk_theme_task,
    }

    manager = SettingsManager(BASE_SETTINGS_PATH, USER_SETTINGS_PATH)
    manager.load()

    adapter = TkinterSettingsAdapter(manager, root)
    app = ThemeGeneratorApp(
        root=root,
        title="MinUI Theme Generator",
        min_size=(1080, 500),
        settings_manager=manager,
        settings_adapter=adapter,
        commands_map=commands_map,
    )

    preview_generator = ThemePreviewGenerator(manager)

    app.set_on_change_listener(partial(on_change, app, preview_generator))
    app.build_sections_from_settings()

    app.run()


if __name__ == "__main__":
    main()
