from functools import partial
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
)
from PIL.Image import Resampling

from .app import ThemeGeneratorApp
from .constants import (
    BASE_SETTINGS_PATH,
    USER_SETTINGS_PATH,
)
from .generator.preview import ThemePreviewGenerator

Image.MAX_IMAGE_PIXELS = None


def update_image_label(image_label: ttk.Label, pil_image: Image.Image) -> None:
    tk_image = ImageTk.PhotoImage(pil_image)
    image_label.config(image=tk_image)
    image_label.image = tk_image


def on_change(app: ThemeGeneratorApp, generator: ThemePreviewGenerator, *args) -> None:
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
