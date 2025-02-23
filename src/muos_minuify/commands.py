from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from pathlib import Path
import shutil
import threading
from typing import Any, Callable

import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox

from .constants import (
    DEVICE_TYPE_OPTIONS,
    SYSTEM_LOGOS_SCRIPT_PATH,
    MENU_DEFINITIONS_PATH,
    THEME_SHELL_DIR,
    PREMADE_THEMES_PATH,
)
from .settings import SettingsManager
from .ui.progress_dialog import ProgressDialog
from .utils import (
    delete_file,
    delete_folder,
    ensure_folder_exists,
    read_json,
    copy_contents,
)
from .generator import ThemeGenerator
from .generator.preview import ThemePreviewGenerator
from .scheme import SchemeRenderer


def load_premade_themes() -> list[dict[str, Any]]:
    return read_json(PREMADE_THEMES_PATH).get("themes", [])


def select_color(
    var_name: str,
    tk_variables: dict[str, tk.Variable],
    **kwargs,
) -> None:
    current_hex = tk_variables[var_name].get()
    if current_hex and not current_hex.startswith("#"):
        current_hex = f"#{current_hex}"

    try:
        chosen_tuple = colorchooser.askcolor(
            initialcolor=current_hex or "#ffffff",
            title="Choose Color",
        )
        color_code = chosen_tuple[1]
    except Exception:
        chosen_tuple = colorchooser.askcolor(title="Choose Color")
        color_code = chosen_tuple[1]

    if color_code:
        tk_variables[var_name].set(color_code)


def select_theme_directory_path(
    var_name: str,
    tk_variables: dict[str, tk.Variable],
    **kwargs,
) -> None:
    dir_path = filedialog.askdirectory()

    if dir_path:
        tk_variables[var_name].set(dir_path)


def select_background_image_path(
    var_name: str,
    tk_variables: dict[str, tk.Variable],
    **kwargs,
) -> None:
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Image Files", "*.png"),
            ("Image Files", "*.jpg"),
            ("Image Files", "*.jpeg"),
            ("Image Files", "*.webp"),
            ("Image Files", "*.gif"),
            ("Image Files", "*.bmp"),
        ],  # Only show image files
        title="Select background image file",
    )

    if file_path:
        tk_variables[var_name].set(file_path)


def select_bootlogo_image_path(
    var_name: str,
    tk_variables: dict[str, tk.Variable],
    **kwargs,
) -> None:
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Image Files", "*.png"),
            ("Image Files", "*.jpg"),
            ("Image Files", "*.jpeg"),
            ("Image Files", "*.webp"),
            ("Image Files", "*.gif"),
            ("Image Files", "*.bmp"),
        ],  # Only show image files
        title="Select bootlogo image file",
    )

    if file_path:
        tk_variables[var_name].set(file_path)


def select_alt_font_path(
    var_name: str,
    tk_variables: dict[str, tk.Variable],
    **kwargs,
) -> None:
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Font Files", "*.ttf"),
            ("Font Files", "*.otf"),
        ],  # Only show font files
        title="Select font file",
    )

    if file_path:
        tk_variables[var_name].set(file_path)


def generate_full_theme(
    manager: SettingsManager,
    output_dir: Path,
    progress_callback: Callable,
    theme_overrides: dict[str, Any] | None = None,
) -> None:
    theme_overrides = theme_overrides or {}

    temp_path = (
        output_dir
        / ".temp"
        / theme_overrides.get("theme_name_var", manager.theme_name_var)
    )
    if temp_path.exists():
        delete_folder(temp_path)
    ensure_folder_exists(temp_path)

    items_per_screen = int(manager.itemsPerScreenVar)
    original_res = manager.deviceScreenHeightVar

    if progress_callback:
        progress_callback(
            section="Generating theme...",
            item="Copying theme shell...",
        )

    copy_contents(THEME_SHELL_DIR, temp_path)

    for device in DEVICE_TYPE_OPTIONS:
        manager.load({"device_type_var": device} | theme_overrides)
        height = manager.deviceScreenHeightVar
        width = manager.deviceScreenWidthVar
        resolution = f"{width}x{height}"

        res_items_per_screen = items_per_screen * height / original_res
        manager.set_value("itemsPerScreenVar", res_items_per_screen)

        preview_generator = ThemePreviewGenerator(manager)
        renderer = SchemeRenderer(manager)
        generator = ThemeGenerator(manager, renderer=renderer)

        menu_defs = read_json(MENU_DEFINITIONS_PATH)
        defaults = menu_defs.get("default", {})

        preview_right_buttons = menu_defs.get("muxlaunch", {}).get(
            "right_guides", defaults.get("right_guides", [])
        )
        preview_left_buttons = menu_defs.get("muxlaunch", {}).get(
            "left_guides", defaults.get("left_guides", [])
        )

        if progress_callback:
            progress_callback(
                section=f"Generating theme for {resolution}...",
                item="",
            )

        generator.generate_theme(
            temp_path,
            progress_callback=progress_callback,
        )

        if progress_callback:
            progress_callback(
                section=f"Generating preview image for {resolution}...",
                item="",
            )

        preview_img = preview_generator.generate_launcher_image(
            preview_right_buttons,
            preview_left_buttons,
            "explore",
            for_preview=True,
        )
        preview_img.save(temp_path / resolution / "preview.png")
        if manager.developer_preview_var:
            dev_preview_img = preview_generator.generate_launcher_image(
                preview_right_buttons,
                preview_left_buttons,
                "explore",
            )
            dev_preview_img.save(
                temp_path / f"{manager.theme_name_var}[{resolution}].png"
            )

    opt_path = temp_path / "system_logos" / "opt"
    ensure_folder_exists(opt_path)

    shutil.copy2(SYSTEM_LOGOS_SCRIPT_PATH, opt_path / "update.sh")

    package_theme(manager.theme_name_var, temp_path, output_dir)
    delete_folder(temp_path)

    # reload user settings after generation
    manager.load()


def package_theme(theme_name: str, temp_path: Path, theme_path: Path) -> None:
    shutil.make_archive(
        str(theme_path / "MinUIfied AM System Icons"), "zip", temp_path / "system_logos"
    )
    delete_folder(temp_path / "system_logos")

    for file in temp_path.iterdir():
        if file.is_file() and file.name.endswith(".png"):
            shutil.copy2(file, theme_path / file.name)
            delete_file(file)

    shutil.make_archive(str(theme_path / theme_name), "zip", temp_path)


def start_theme_task(manager: SettingsManager, root: tk.Tk, **kwargs) -> None:
    dialog = ProgressDialog(root, title=f"Generating theme...", max=None)

    def on_progress(
        section: str | None = None, item: str | None = None, step: int = 1
    ) -> None:
        def _update():
            dialog.update_status(section, item, step)

        root.after(0, _update)

    def worker():
        try:
            manager.save_user_values()

            output_dir = Path(manager.theme_directory_path)
            ensure_folder_exists(output_dir)

            generate_full_theme(manager, output_dir, progress_callback=on_progress)

            on_progress(section="Theme generation complete.", item="")
            root.after(0, dialog.destroy)
            root.after(
                0,
                lambda: messagebox.showinfo("Success", "Theme generated successfully!"),
            )
        except Exception as e:
            print(e)
            root.after(0, dialog.destroy)
            root.after(
                0,
                partial(
                    messagebox.showerror,
                    "Error",
                    str(e)
                    if manager.advanced_error_var
                    else "An error occurred while generating the theme.",
                ),
            )

    threading.Thread(target=worker, daemon=True).start()


def start_bulk_theme_task(manager: SettingsManager, root: tk.Tk, **kwargs) -> None:
    if not (themes := load_premade_themes()):
        messagebox.showinfo("Info", "No premade themes found.")
        return

    dialog = ProgressDialog(root, title=f"Generating {len(themes)} themes...", max=None)
    manager.save_user_values()
    show_errors = manager.advanced_error_var

    def on_progress(
        section: str | None = None, item: str | None = None, step: int = 1
    ) -> None:
        def _update():
            try:
                if dialog.winfo_exists():
                    dialog.update_status(section, item, step)
            except tk.TclError:
                pass

        root.after(0, _update)

    def bulk_worker():
        max_workers = 2
        futures = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for theme in themes:
                futures.append(executor.submit(worker, theme))

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(e)
                    root.after(
                        0,
                        partial(
                            messagebox.showerror,
                            "Error",
                            str(e)
                            if show_errors
                            else "An error occurred while generating the theme.",
                        ),
                    )

        root.after(0, dialog.destroy)
        root.after(
            0,
            partial(
                messagebox.showinfo,
                "Success",
                "All themes generated successfully!",
            ),
        )

    def worker(theme_overrides: dict[str, Any]):
        try:
            manager = SettingsManager()
            manager.load()

            output_dir = Path(manager.theme_directory_path)
            ensure_folder_exists(output_dir)

            generate_full_theme(
                manager,
                output_dir,
                progress_callback=on_progress,
                theme_overrides=theme_overrides,
            )

            on_progress(
                section=f"Finished generating {manager.theme_name_var}", item=""
            )
        except Exception as e:
            print(e)
            root.after(
                0,
                partial(
                    messagebox.showerror,
                    "Error",
                    str(e)
                    if show_errors
                    else "An error occurred while generating the theme.",
                ),
            )

    threading.Thread(target=bulk_worker, daemon=True).start()
