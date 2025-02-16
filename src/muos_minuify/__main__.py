import copy
from functools import partial
import json
import math
from typing import Any, Callable
import numpy as np
from pathlib import Path
import queue
import re
import shutil
import threading
import tkinter as tk
from tkinter import (
    filedialog,
    messagebox,
    ttk,
    colorchooser,
)
import traceback

from .adapter import TkinterSettingsAdapter
from .settings import SettingsManager
from .theme import DeviceThemeGenerator, PreviewThemeGenerator

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
    DEVICE_TYPE_OPTIONS,
    RESOURCES_DIR,
    ASSETS_DIR,
    GLYPHS_DIR,
    HORIZONTAL_LOGOS_DIR,
    THEME_SHELL_DIR,
    TEMPLATE_SCHEME_PATH,
    OVERLAY_DIR,
    FONTS_DIR,
    BASE_SETTINGS_PATH,
    USER_SETTINGS_PATH,
    BatteryStyleOptionsDict,
    BatteryChargingStyleOptionsDict,
    MENU_LISTING_2410_X,
)
from .font import get_font_path
from .utils import (
    copy_contents,
    delete_folder,
    delete_file,
    rename_file,
    ensure_folder_exists,
)
from .utils.math import round_to_nearest_odd
from .ui.progress_dialog import ProgressDialog
from .generator.preview import ThemePreviewGenerator

Image.MAX_IMAGE_PIXELS = None

## TODO look into centre align and left align
## TODO make header resizable

background_image = None
preview_overlay_image = None

# Define constants
render_factor = 5

contentPaddingTop = 44
textMF = 0.7


def ContinuousFolderImageGen(
    progress_bar: ttk.Progressbar,
    muOSSystemName: str,
    listItems: list[str],
    textPadding: int,
    rectanglePadding: int,
    ItemsPerScreen: int,
    bg_hex: str,
    selected_font_hex: str,
    deselected_font_hex: str,
    bubble_hex: str,
    render_factor: int,
    outputDir: Path,
    manager: SettingsManager,
    folderName: Path | None = None,
    threadNumber: int = 0,
) -> None:
    (
        bg_hex,
        selected_font_hex,
        deselected_font_hex,
        bubble_hex,
    ) = [
        val[1:] if val.startswith("#") else val
        for val in [
            bg_hex,
            selected_font_hex,
            deselected_font_hex,
            bubble_hex,
        ]
    ]

    theme_generator = DeviceThemeGenerator(manager)
    totalItems = len(listItems)
    for workingIndex, workingItem in enumerate(listItems):
        if workingItem[1] == "Directory" or workingItem[1] == "Menu":
            # Load the base image
            midIndexOfList = int((ItemsPerScreen - 1) / 2)
            if totalItems > ItemsPerScreen:
                if workingIndex < midIndexOfList:
                    startIndex = 0
                    focusIndex = workingIndex
                elif workingIndex > (totalItems - ItemsPerScreen) + midIndexOfList:
                    startIndex = totalItems - ItemsPerScreen
                    focusIndex = ItemsPerScreen - (totalItems - (workingIndex + 1)) - 1
                else:
                    startIndex = workingIndex - midIndexOfList
                    focusIndex = midIndexOfList
                endIndex = min(startIndex + ItemsPerScreen, totalItems)
            else:
                startIndex = 0
                endIndex = totalItems
                focusIndex = workingIndex
            fileCounter = str(workingIndex + 1) + " / " + str(totalItems)

            image = theme_generator.generate_vertical_menu_image(
                progress_bar,
                focusIndex,
                muOSSystemName,
                listItems[startIndex:endIndex],
                textPadding,
                rectanglePadding,
                ItemsPerScreen,
                bg_hex,
                selected_font_hex,
                deselected_font_hex,
                bubble_hex,
                fileCounter=fileCounter,
                transparent=True,
            )
            image = image.resize(
                (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
                Image.LANCZOS,
            )
            if workingItem[1] == "File":
                directory = outputDir / muOSSystemName / "box"
                ensure_folder_exists(directory)
                image.save(directory / f"{workingItem[2]}.png")
            elif workingItem[1] == "Directory":
                directory = outputDir / muOSSystemName / "Folder" / "box"
                ensure_folder_exists(directory)
                image.save(directory / f"{workingItem[2]}.png")


def cut_out_image(
    original_image: Image.Image, logo_image: Image.Image, coordinates: tuple[int, int]
) -> Image.Image:
    x, y = coordinates

    # Ensure the images are in RGBA mode
    original_image = original_image.convert("RGBA")
    logo_image = logo_image.convert("RGBA")

    # Convert the images to NumPy arrays
    original_array = np.array(original_image)
    logo_array = np.array(logo_image)

    # Get the dimensions of the original and logo images
    original_height, original_width = original_array.shape[:2]
    logo_height, logo_width = logo_array.shape[:2]

    # Create a mask where the logo is not transparent
    logo_mask = logo_array[:, :, 3] > 0  # The alpha channel indicates transparency

    # Ensure the coordinates are within the bounds of the original image
    x_end = min(x + logo_width, original_width)
    y_end = min(y + logo_height, original_height)

    # Adjust the logo mask and arrays to fit within the bounds of the original image
    logo_mask = logo_mask[: y_end - y, : x_end - x]
    logo_alpha = logo_array[: y_end - y, : x_end - x, 3] / 255.0

    # Cut out the region of the original image where the logo is not transparent
    original_array[y:y_end, x:x_end, 3] = np.where(
        logo_mask,
        original_array[y:y_end, x:x_end, 3] * (1 - logo_alpha),
        original_array[y:y_end, x:x_end, 3],
    )

    # Convert the modified NumPy array back to a Pillow image
    edited_image = Image.fromarray(original_array.astype("uint8"), "RGBA")

    # Return the edited image
    return edited_image


def HorizontalMenuGen(
    progress_bar: ttk.Progressbar,
    muOSSystemName: str,
    listItems: list[str],
    bg_hex: str,
    selected_font_hex: str,
    deselected_font_hex: str,
    bubble_hex: str,
    icon_hex: str,
    render_factor: int,
    outputDir: Path,
    variant: str,
    manager: SettingsManager,
    threadNumber: int = 0,
):
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

    startIndex = 0
    endIndex = 8
    theme_generator = DeviceThemeGenerator(manager)
    for workingIndex in range(startIndex, endIndex):
        workingItem = listItems[workingIndex]
        if variant == "Horizontal":
            image = theme_generator.generate_horizontal_menu_image(
                progress_bar,
                workingIndex,
                bg_hex,
                selected_font_hex,
                deselected_font_hex,
                bubble_hex,
                icon_hex,
                transparent=True,
            )
        elif variant == "Alt-Horizontal":
            image = theme_generator.generate_alt_horizontal_menu_image(
                progress_bar,
                workingIndex,
                bg_hex,
                selected_font_hex,
                deselected_font_hex,
                bubble_hex,
                icon_hex,
                transparent=True,
            )
        else:
            raise ValueError("Something went wrong with your Main Menu Style")
        image = image.resize(
            (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
            Image.LANCZOS,
        )

        if workingItem[1] == "File":
            directory = outputDir / muOSSystemName / "box"
            ensure_folder_exists(directory)
            image.save(directory / f"{workingItem[0]}.png")
        elif workingItem[1] == "Directory":
            directory = outputDir / muOSSystemName / "Folder" / "box"
            ensure_folder_exists(directory)
            image.save(directory / f"{workingItem[0]}.png")
        elif workingItem[1] == "Menu":
            directory = outputDir / muOSSystemName
            ensure_folder_exists(directory)
            image.save(directory / f"{workingItem[2]}.png")


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


def select_color(
    manager: SettingsManager, var_name: str, tk_variables: dict[str, tk.Variable]
) -> None:
    """Opens a color picker and sets the selected color to the given entry."""
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
        manager.set_value(var_name, color_code.lstrip("#"))
        tk_variables[var_name].set(color_code)


def select_theme_directory_path(
    manager: SettingsManager, var_name: str, tk_variables: dict[str, tk.Variable]
) -> None:
    dir_path = filedialog.askdirectory()

    if dir_path:
        manager.set_value(var_name, dir_path)
        tk_variables[var_name].set(dir_path)


def select_background_image_path(
    manager: SettingsManager, var_name: str, tk_variables: dict[str, tk.Variable]
) -> None:
    # File dialog to select a file, with specific types of files allowed
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Image Files", "*.png"),
            ("Image Files", "*.jpg"),
            ("Image Files", "*.jpeg"),
            ("Image Files", "*.webp"),
            ("Image Files", "*.gif"),
            ("Image Files", "*.bmp"),
        ],  # Only show .png files
        title="Select background image file",
    )

    if file_path:
        manager.set_value(var_name, file_path)
        tk_variables[var_name].set(file_path)


def select_bootlogo_image_path(
    manager: SettingsManager, var_name: str, tk_variables: dict[str, tk.Variable]
) -> None:
    # File dialog to select a file, with specific types of files allowed
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Image Files", "*.png"),
            ("Image Files", "*.jpg"),
            ("Image Files", "*.jpeg"),
            ("Image Files", "*.webp"),
            ("Image Files", "*.gif"),
            ("Image Files", "*.bmp"),
        ],  # Only show .png files
        title="Select bootlogo image file",
    )

    if file_path:
        manager.set_value(var_name, file_path)
        tk_variables[var_name].set(file_path)


def select_alt_font_path(
    manager: SettingsManager, var_name: str, tk_variables: dict[str, tk.Variable]
) -> None:
    # File dialog to select a file, with specific types of files allowed
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Font Files", "*.ttf"),
            ("Font Files", "*.otf"),
        ],  # Only show font files
        title="Select font file",
    )

    if file_path:
        manager.set_value(var_name, file_path)
        tk_variables[var_name].set(file_path)


def generate_theme(
    manager: SettingsManager,
    threadNumber: int,
    resolutions: list[tuple[int, int]],
    assumed_res: tuple[int, int],
    progress_callback: Callable,
) -> None:
    temp_build_dir = RESOURCES_DIR / f".TempBuildTheme{threadNumber}"
    temp_system_icons_dir = RESOURCES_DIR / f".TempBuildSystemIconsAMFile{threadNumber}"
    assumed_res_dir = temp_build_dir / f"{assumed_res[0]}x{assumed_res[1]}"

    # try:

    if threadNumber != -1:
        themeName = manager.theme_name_var + f" {manager.main_menu_style_var}"
    else:
        themeName = manager.theme_name_var

    assumed_items_per_screen = int(manager.itemsPerScreenVar)
    height_items_per_screen_map = {}
    for width, height in resolutions:
        height_items_per_screen_map[height] = round_to_nearest_odd(
            assumed_items_per_screen * (height / assumed_res[1])
        )

    for width, height in resolutions:
        temp_res_dir = temp_build_dir / f"{width}x{height}"
        scale_factor = width / assumed_res[0]

        scaled_clock_left_padding = int(
            int(manager.clockHorizontalLeftPaddingVar) * scale_factor
        )
        scaled_clock_right_padding = int(
            int(manager.clockHorizontalRightPaddingVar) * scale_factor
        )
        scaled_glyph_left_padding = int(
            int(manager.header_glyph_horizontal_left_padding_var) * scale_factor
        )
        scaled_glyph_right_padding = int(
            int(manager.header_glyph_horizontal_right_padding_var) * scale_factor
        )
        scaled_page_title_padding = int(int(manager.pageTitlePaddingVar) * scale_factor)

        res_values = {
            "deviceScreenWidthVar": width,
            "deviceScreenHeightVar": height,
        }

        if height != assumed_res[1]:
            res_values["itemsPerScreenVar"] = height_items_per_screen_map[height]

            if manager.clock_alignment_var == "Centre":
                res_values["clockHorizontalLeftPaddingVar"] = scaled_clock_left_padding
                res_values["clockHorizontalRightPaddingVar"] = (
                    scaled_clock_right_padding
                )

            if manager.header_glyph_alignment_var == "Centre":
                res_values["header_glyph_horizontal_left_padding_var"] = (
                    scaled_glyph_left_padding
                )
                res_values["header_glyph_horizontal_right_padding_var"] = (
                    scaled_glyph_right_padding
                )
            if manager.page_title_alignment_var == "Centre":
                res_values["pageTitlePaddingVar"] = scaled_page_title_padding

        res_manager = SettingsManager()
        res_manager.load(res_values)

        res_generator = DeviceThemeGenerator(res_manager, progress_callback)
        res_generator.generate_theme(threadNumber)

        try:
            for target in ["font", "glyph", "image", "scheme"]:
                shutil.move(temp_build_dir / target, temp_res_dir / target)
        except Exception as e:
            print(e)
            pass

        if manager.enable_grid_view_explore_var:
            theme_dir = manager.theme_directory_path

            ensure_folder_exists(temp_system_icons_dir / "opt")
            shutil.copy2(
                ASSETS_DIR / "AM - Scripts" / "System Logo Load" / "update.sh",
                temp_system_icons_dir / "opt" / "update.sh",
            )
    if manager.enable_grid_view_explore_var:
        theme_dir = manager.theme_directory_path

        shutil.make_archive(
            str(theme_dir / "MinUIfied AM System Icons"),
            "zip",
            str(temp_system_icons_dir),
        )
        delete_folder(temp_system_icons_dir)

    for target in ["font", "glyph", "image", "scheme"]:
        shutil.move(assumed_res_dir / target, temp_build_dir / target)

    delete_folder(assumed_res_dir)

    theme_dir = manager.theme_directory_path

    shutil.make_archive(str(theme_dir / themeName), "zip", temp_build_dir)

    if manager.developer_preview_var:
        ensure_folder_exists(theme_dir)
        for width, height in resolutions:
            thread_and_res = f"{threadNumber}[{width}x{height}].png"
            theme_and_res = f"{themeName}[{width}x{height}].png"
            temp_preview_path = RESOURCES_DIR / f"TempPreview{thread_and_res}"
            theme_preview_path = theme_dir / theme_and_res
            preview_path = theme_dir / "preview" / f"TempPreview{thread_and_res}"

            delete_file(temp_preview_path)
            rename_file(temp_preview_path, theme_preview_path)
            delete_file(temp_preview_path)
            delete_file(preview_path)

    delete_folder(temp_build_dir)
    if threadNumber == -1:
        messagebox.showinfo("Success", "Theme generated successfully.")

    # except Exception as e:
    #     print(e)
    #     loading_window.destroy()
    #     theme_dir = manager.theme_directory_path

    #     if manager.advanced_error_var:
    #         tb_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    #         messagebox.showerror(
    #             "Error", f"An unexpected error occurred: {e}\n{tb_str}"
    #         )
    #     else:
    #         messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    #     delete_folder(temp_build_dir)
    #     if manager.developer_preview_var:
    #         for width, height in resolutions:
    #             thread_and_res = f"{threadNumber}[{width}x{height}].png"
    #             temp_preview_path = RESOURCES_DIR / f"TempPreview{thread_and_res}"
    #             preview_path = theme_dir / "preview" / f"TempPreview{thread_and_res}"

    #             delete_file(temp_preview_path)
    #             delete_file(preview_path)


def generate_themes(themes: list[Any]) -> None:
    if themes:
        barrier = threading.Barrier(
            len(themes) + 1
        )  # Create a barrier for all threads + the main thread

        for threadNumber, theme in enumerate(themes):
            thread_config = copy.deepcopy(Config())
            save_settings(thread_config)
            thread_manager.apply_theme(theme)

            loading_window = tk.Toplevel(root)
            loading_window.title(f"Generating {thread_manager.theme_name_entry}...")
            loading_window.geometry("600x100")

            progress_bar = ttk.Progressbar(
                loading_window, orient="horizontal", length=500, mode="determinate"
            )
            progress_bar.pack(pady=20)

            # Start a thread for each theme generation
            match = re.search(r"\[(\d+)x(\d+)\]", thread_manager.device_type_var)
            assumed_res = (640, 480)
            if match:
                assumed_res = (int(match.group(1)), int(match.group(2)))
            else:
                raise ValueError(
                    "Invalid device type format, cannot find screen dimensions"
                )
            all_resolutions = []
            for device_type in deviceTypeOptions:
                match = re.search(r"\[(\d+)x(\d+)\]", device_type)
                if match:
                    all_resolutions.append((int(match.group(1)), int(match.group(2))))
            threading.Thread(
                target=generate_theme,
                args=(
                    progress_bar,
                    loading_window,
                    threadNumber,
                    thread_config,
                    barrier,
                    all_resolutions,
                    assumed_res,
                ),
            ).start()

        # Wait for all threads to finish
        barrier.wait()
        messagebox.showinfo("Success", "Themes generated successfully.")


def FillTempThemeFolder(
    progress_bar: ttk.Progressbar, threadNumber: int, manager: SettingsManager
) -> None:
    textPadding = int(manager.textPaddingVar)
    rectanglePadding = int(manager.bubblePaddingVar)
    ItemsPerScreen = int(manager.itemsPerScreenVar)
    bg_hex = manager.bgHexVar
    selected_font_hex = manager.selectedFontHexVar
    deselected_font_hex = manager.deselectedFontHexVar
    bubble_hex = manager.bubbleHexVar
    icon_hex = manager.iconHexVar

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
        manager.use_alt_font_var, manager.alt_font_filename
    )
    temp_build_dir = RESOURCES_DIR / f".TempBuildTheme{threadNumber}"

    copy_contents(THEME_SHELL_DIR, temp_build_dir)

    newSchemeDir = temp_build_dir / "scheme"
    ensure_folder_exists(newSchemeDir)

    fontSize = int(manager.font_size_var)

    # Theme Variables that wont change
    accent_hex = deselected_font_hex
    base_hex = bg_hex
    blend_hex = percentage_color(bubble_hex, selected_font_hex, 0.5)
    muted_hex = percentage_color(bg_hex, bubble_hex, 0.25)
    counter_alignment = "Right"
    datetime_alignment = manager.clock_alignment_var
    header_glyph_alignment = manager.header_glyph_alignment_var
    datetime_left_padding = manager.clockHorizontalLeftPaddingVar
    datetime_right_padding = manager.clockHorizontalRightPaddingVar
    status_padding_left = int(manager.header_glyph_horizontal_left_padding_var)
    status_padding_right = int(manager.header_glyph_horizontal_right_padding_var)

    default_radius = "10"
    header_height = str(manager.headerHeightVar)
    counter_padding_top = str(manager.contentPaddingTopVar)
    individualItemHeight = round(
        (
            int(manager.deviceScreenHeightVar)
            - int(manager.approxFooterHeightVar)
            - int(manager.contentPaddingTopVar)
        )
        / int(manager.itemsPerScreenVar)
    )
    footerHeight = (
        int(manager.deviceScreenHeightVar)
        - (individualItemHeight * int(manager.itemsPerScreenVar))
        - int(manager.contentPaddingTopVar)
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
    glyph_to_text_pad = int(manager.bubblePaddingVar)
    page_title_alignment_map = {"Auto": 0, "Left": 1, "Centre": 2, "Right": 3}
    counter_alignment_map = {"Left": 0, "Centre": 1, "Right": 2}
    datetime_alignment_map = {"Auto": 0, "Left": 1, "Centre": 2, "Right": 3}
    content_alignment_map = {"Left": 0, "Centre": 1, "Right": 2}
    content_height = individualItemHeight * int(manager.itemsPerScreenVar)
    content_padding_left = int(manager.textPaddingVar) - int(manager.bubblePaddingVar)
    if manager.global_alignment_var == "Centre":
        content_padding_left = 0
    elif manager.global_alignment_var == "Right":
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
        "battery_charging_hex": manager.batteryChargingHexVar,
        "bubble_hex": manager.bubbleHexVar,
        "boot_text_y_pos": int(int(manager.deviceScreenHeightVar) * (165 / 480)),
        "glyph_padding_left": int(int(manager.bubblePaddingVar) + (glyph_width / 2)),
        "image_overlay": manager.include_overlay_var,
        "footer_height": footerHeight,
        "header_text_alpha": 255 if manager.show_console_name_var else 0,
        "page_title_text_align": page_title_alignment_map[
            manager.page_title_alignment_var
        ],
        "page_title_padding": int(manager.pageTitlePaddingVar),
        "bar_height": 42,
        "bar_progress_width": int(manager.deviceScreenWidthVar) - 90,
        "bar_y_pos": int(manager.deviceScreenHeightVar)
        - (30 + getRealFooterHeight(manager)),
        "bar_width": int(manager.deviceScreenWidthVar) - 25,
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
        "content_item_count": manager.itemsPerScreenVar,
        "background_alpha": 0,
        "selected_font_hex": manager.selectedFontHexVar,
        "deselected_font_hex": manager.deselectedFontHexVar,
        "bubble_alpha": 255,
        "bubble_padding_right": manager.bubblePaddingVar,
        "content_alignment": content_alignment_map[
            manager.global_alignment_var
        ],  # TODO make this change for the different sections
        "list_default_label_long_mode": 1,
        "content_padding_left": content_padding_left,
        "content_width": (
            int(manager.deviceScreenWidthVar)
            - (10 if manager.version_var == "muOS 2410.1 Banana" else 0)
            - 2 * (int(manager.textPaddingVar) - int(manager.bubblePaddingVar))
        ),
        "footer_alpha": 0,
        "footer_background_alpha": 0,
        "footer_pad_top": 0,
        "footer_pad_bottom": 0,
        "bubble_padding_left": int(
            int(manager.bubblePaddingVar) + (glyph_width / 2) + glyph_to_text_pad
        )
        if manager.show_glyphs_var
        else manager.bubblePaddingVar,
        "list_glyph_alpha": 255 if manager.show_glyphs_var else 0,
        "list_text_alpha": 255,
        "navigation_type": 0,
        "content_padding_top": int(contentPaddingTop) - (int(header_height) + 2),
        "grid_navigation_type": 4,
        "grid_background": manager.bgHexVar,
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
        "grid_cell_default_background": manager.bgHexVar,
        "grid_cell_default_background_alpha": 0,
        "grid_cell_default_border": manager.bgHexVar,
        "grid_cell_default_border_alpha": 0,
        "grid_cell_default_image_alpha": 255,
        "grid_cell_default_image_recolour": manager.iconHexVar,
        "grid_cell_default_image_recolour_alpha": 255,
        "grid_cell_default_text": manager.deselectedFontHexVar,
        "grid_cell_default_text_alpha": 0,
        "grid_cell_focus_background": manager.deselectedFontHexVar,
        "grid_cell_focus_background_alpha": int(255 * 0.133),
        "grid_cell_focus_border": (manager.deselectedFontHexVar),
        "grid_cell_focus_border_alpha": 0,
        "grid_cell_focus_image_alpha": 255,
        "grid_cell_focus_image_recolour": (manager.iconHexVar),
        "grid_cell_focus_image_recolour_alpha": 255,
        "grid_cell_focus_text": (manager.selectedFontHexVar),
        "grid_cell_focus_text_alpha": 0,
    }

    missingValues = [k for k, v in replacementStringMap["default"].items() if v is None]
    if missingValues:
        missingValuesString = ""
        for n in missingValues:
            missingValuesString += n + "\n"
        raise ValueError(f"Replacement string(s) \n{missingValuesString} not set")

    ## Overrides:

    # horizontal muxlaunch specific options - basically remove all text content and set naviagtion type
    if manager.main_menu_style_var != "Vertical":
        replacementStringMap["muxlaunch"] = {
            "bubble_alpha": 0,
            "list_glyph_alpha": 0,
            "list_text_alpha": 0,
            "navigation_type": 4
            if manager.horizontal_menu_behaviour_var == "Wrap to Row"
            else 2,
        }

    # muxnetwork Specific settings - account for status at the bottom and show footer

    if manager.version_var == "muOS 2410.1 Banana":
        replacementStringMap["muxnetwork"] = {
            "content_height": int(
                (content_height / int(manager.itemsPerScreenVar))
                * (int(manager.itemsPerScreenVar) - 2)
            ),
            "content_item_count": int(manager.itemsPerScreenVar) - 2,
            "footer_alpha": 255,
        }
    else:  ## muxnetwork - show the footer
        replacementStringMap["muxnetwork"]["footer_alpha"] = 255

    # muxassign - Force Glyphs on and show footer
    replacementStringMap["muxassign"] = {
        "bubble_padding_left": int(
            int(manager.bubblePaddingVar) + (glyph_width / 2) + glyph_to_text_pad
        ),  # for glyph support
        "list_glyph_alpha": 255,  # for glyph support
        "footer_alpha": 255,
    }

    # muxgov - same as muxassign, but hide footer
    for map in ["muxgov", "muxsearch"]:
        replacementStringMap[map] = replacementStringMap["muxassign"].copy()
        replacementStringMap[map]["footer_alpha"] = 0

    # muxpicker - Cut text off before preview image
    if manager.version_var != "muOS 2410.1 Banana":
        max_preview_size = int(int(manager.deviceScreenWidthVar) * 0.45)
        if int(manager.deviceScreenWidthVar) == 720:
            max_preview_size = 340

        replacementStringMap["muxpicker"]["content_width"] = (
            int(manager.deviceScreenWidthVar)
            - max_preview_size
            - 2 * (int(manager.textPaddingVar) - int(manager.bubblePaddingVar))
        )

    # muxplore - cut off text if needed for box art
    if int(manager.maxBoxArtWidth) > 0:
        replacementStringMap["muxplore"]["content_width"] = (
            int(manager.deviceScreenWidthVar)
            - int(manager.maxBoxArtWidth)
            - (int(manager.textPaddingVar) - int(manager.bubblePaddingVar))
        )

        # muxfavourite - same as muxplore
        replacementStringMap["muxfavourite"] = replacementStringMap["muxplore"].copy()

    if int(manager.maxBoxArtWidth) > 0:
        replacementStringMap["muxhistory"] = replacementStringMap["muxplore"].copy()

    replacementStringMap["muxstorage"]["footer_alpha"] = 255

    if manager.enable_grid_view_explore_var:
        grid_total_height = (
            int(manager.deviceScreenHeightVar)
            - getRealFooterHeight(manager)
            - int(manager.headerHeightVar)
        )
        grid_total_width = int(manager.deviceScreenWidthVar)
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
        grid_location_y = int(manager.headerHeightVar)
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
            / f"{manager.deviceScreenWidthVar}x{manager.deviceScreenHeightVar}"
        )
        ensure_folder_exists(output_system_logos_path)
        resize_system_logos(
            system_logos_path,
            output_system_logos_path,
            grid_cell_size,
            grid_image_padding,
            circular_grid=False,
        )

    theme_generator = DeviceThemeGenerator(manager)
    if not "Generating for lanuage on muxlaunch":
        horizontalLogoSize = theme_generator._get_horizontal_logo_size(
            HORIZONTAL_LOGOS_DIR / "explore.png"
        )
        paddingBetweenLogos = (
            int(manager.deviceScreenWidthVar) - (horizontalLogoSize[0] * 4)
        ) / (4 + 1)

        bubble_height = min(
            (int(manager.deviceScreenHeightVar) * 36.3) / 480,
            (int(manager.deviceScreenWidthVar) * 36.3) / 640,
        )
        effective_text_padding_top = 4

        combined_height = bubble_height + horizontalLogoSize[1]
        heightAbove_logo = (int(manager.deviceScreenHeightVar) - combined_height) / 2

        grid_total_width = int(manager.deviceScreenWidthVar) - paddingBetweenLogos

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
        replace_scheme_options(newSchemeDir, fileName, replacementStringMap)

    ensure_folder_exists(temp_build_dir / "image" / "wall")

    if manager.include_overlay_var:
        shutil.copy2(
            OVERLAY_DIR
            / f"{manager.deviceScreenWidthVar}x{manager.deviceScreenHeightVar}"
            / f"{manager.selected_overlay_var}.png",
            temp_build_dir / "image" / "overlay.png",
        )

    ## GLYPH STUFF
    ensure_folder_exists(temp_build_dir / "glyph" / "footer")
    ensure_folder_exists(temp_build_dir / "glyph" / "header")

    muosSpaceBetweenItems = 2
    footerHeight = (
        int(manager.deviceScreenHeightVar)
        - (individualItemHeight * int(manager.itemsPerScreenVar))
        - int(manager.contentPaddingTopVar)
        + muosSpaceBetweenItems
    )
    button_height = int(
        (footerHeight - (int(manager.VBG_Vertical_Padding_var) * 2)) * (2 / 3)
    )  # Change this if overlayed
    in_bubble_font_size = round(button_height * (24 / 40))

    buttonsToGenerate = ["A", "B", "C", "MENU", "X", "Y", "Z"]
    theme_generator = DeviceThemeGenerator(manager)
    for button in buttonsToGenerate:
        button_image = theme_generator.generate_button_glyph_image(
            button,
            selected_font_path,
            accent_hex,
            button_height,
            manager.physical_controller_layout_var,
            render_factor,
        )
        button_image = button_image.resize(
            (
                int(button_image.size[0] / render_factor),
                int(button_image.size[1] / render_factor),
            ),
            Image.LANCZOS,
        )
        button_image.save(
            temp_build_dir / "glyph" / "footer" / f"{button.lower()}.png",
            format="PNG",
        )
    capacities = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    networkGlyphNames = ["network_active", "network_normal"]
    if float(manager.header_glyph_height_var) < 10:
        raise ValueError("Header Glyph Height Too Small!")
    elif float(manager.header_glyph_height_var) > int(manager.headerHeightVar):
        raise ValueError("Header Glyph Height Too Large!")
    else:
        heightOfGlyph = int(float(manager.header_glyph_height_var))

    for capacity in capacities:
        try:
            capacity_image_path = (
                GLYPHS_DIR
                / f"{BatteryStyleOptionsDict[manager.battery_style_var]}{capacity}[5x].png"
            )
        except:
            raise Exception("Battery Style not found")
        capacity_image = Image.open(capacity_image_path)
        capacity_image = capacity_image.resize(
            (
                int(heightOfGlyph * (capacity_image.size[0] / capacity_image.size[1])),
                heightOfGlyph,
            ),
            Image.LANCZOS,
        )
        capacity_image.save(
            temp_build_dir / "glyph" / "header" / f"capacity_{capacity}.png",
            format="PNG",
        )

        try:
            capacity_charging_image_path = (
                GLYPHS_DIR
                / f"{BatteryChargingStyleOptionsDict[manager.battery_charging_style_var]}{capacity}[5x].png"
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
            Image.LANCZOS,
        )
        capacity_charging_image.save(
            temp_build_dir / "glyph" / "header" / f"capacity_charging_{capacity}.png",
            format="PNG",
        )

    for networkGlyph in networkGlyphNames:
        input_image_path = GLYPHS_DIR / f"{networkGlyph}[5x].png"
        image = Image.open(input_image_path)
        image = image.resize(
            (int(heightOfGlyph * (image.size[0] / image.size[1])), heightOfGlyph),
            Image.LANCZOS,
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
        muxarchive_font_size_640 * (int(manager.deviceScreenWidthVar) / 640)
    )
    if fontSize > muxarchive_font_size:
        shutil.copy2(
            font_binary_path / f"BPreplayBold-unhinted-{int(muxarchive_font_size)}.bin",
            font_panel_path / "muxarchive.bin",
        )

    muxpicker_font_size_640 = 18
    muxpicker_font_size = math.floor(
        muxpicker_font_size_640 * (int(manager.deviceScreenWidthVar) / 640)
    )
    if fontSize > muxpicker_font_size:
        shutil.copy2(
            font_binary_path / f"BPreplayBold-unhinted-{int(muxpicker_font_size)}.bin",
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
            (int(int(manager.header_text_height_var) * render_factor) * (4 / 3))
            / render_factor
        )
    )
    shutil.copy2(
        font_binary_path / f"BPreplayBold-unhinted-{headerFontSize}.bin",
        font_header_path / "default.bin",
    )

    ## IMAGE STUFF
    temp_image_dir = temp_build_dir / "image"
    bootlogoimage = theme_generator.generate_boot_screen_with_logo(
        manager.bgHexVar,
        manager.deselectedFontHexVar,
        manager.bubbleHexVar,
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    bootlogoimage.save(
        temp_image_dir / "bootlogo.bmp",
        format="BMP",
    )
    progress_bar["value"] += 1

    chargingimage = theme_generator.generate_boot_screen_with_text(
        manager.bgHexVar,
        manager.deselectedFontHexVar,
        manager.iconHexVar,
        "CHARGING...",
        icon_path=ASSETS_DIR / "ChargingLogo[5x].png",
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    chargingimage.save(
        temp_image_dir / "wall" / "muxcharge.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    loadingimage = theme_generator.generate_boot_screen_with_text(
        manager.bgHexVar,
        manager.deselectedFontHexVar,
        manager.iconHexVar,
        "LOADING...",
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    loadingimage.save(
        temp_image_dir / "wall" / "muxstart.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    shutdownimage = theme_generator.generate_boot_screen_with_text(
        manager.bgHexVar,
        manager.deselectedFontHexVar,
        manager.iconHexVar,
        "Shutting Down...",
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    shutdownimage.save(
        temp_image_dir / "shutdown.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    rebootimage = theme_generator.generate_boot_screen_with_text(
        manager.bgHexVar,
        manager.deselectedFontHexVar,
        manager.iconHexVar,
        "REBOOTING...",
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    rebootimage.save(
        temp_image_dir / "reboot.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    defaultimage = theme_generator.generate_background_image(manager.bgHexVar).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    defaultimage.save(
        temp_image_dir / "wall" / "default.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    # TODO If implimented it would be great to only set these once as a default.png type thing, and then make it work in every menu

    visualbuttonoverlay_B_BACK_A_SELECT = theme_generator.generate_static_overlay_image(
        [["B", "BACK"], ["A", "SELECT"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )

    if manager.version_var == "muOS 2410.1 Banana":
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

    if manager.version_var == "muOS 2410.1 Banana":
        muxcustom_items = []
    else:
        muxcustom_items = ["theme", "catalogue", "config"]
    ensure_folder_exists(temp_image_dir / "static" / "muxcustom")
    for item in muxcustom_items:
        visualbuttonoverlay_B_BACK_A_SELECT.save(
            temp_image_dir / "static" / "muxcustom" / f"{item}.png",
            format="PNG",
        )

    if manager.version_var == "muOS 2410.1 Banana":
        muxinfo_items = ["tracker", "tester", "system", "credit"]
    else:
        muxinfo_items = ["tracker", "tester", "system", "credit"]
    ensure_folder_exists(temp_image_dir / "static" / "muxinfo")
    for item in muxinfo_items:
        visualbuttonoverlay_B_BACK_A_SELECT.save(
            temp_image_dir / "static" / "muxinfo" / f"{item}.png",
            format="PNG",
        )

    if manager.version_var == "muOS 2410.1 Banana":
        muxoption_items = ["core", "governor"]
    else:
        muxoption_items = ["search", "core", "governor"]
    ensure_folder_exists(temp_image_dir / "static" / "muxoption")
    for item in muxoption_items:
        visualbuttonoverlay_B_BACK_A_SELECT.save(
            temp_image_dir / "static" / "muxoption" / f"{item}.png",
            format="PNG",
        )
    progress_bar["value"] += 1

    visualbuttonoverlay_A_SELECT = theme_generator.generate_static_overlay_image(
        [["A", "SELECT"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )

    if manager.version_var == "muOS 2410.1 Banana":
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
    progress_bar["value"] += 1

    visualbuttonoverlay_B_BACK = theme_generator.generate_static_overlay_image(
        [["B", "BACK"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    visualbuttonoverlay_B_SAVE = theme_generator.generate_static_overlay_image(
        [["B", "SAVE"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )

    if manager.version_var == "muOS 2410.1 Banana":
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

    if manager.version_var == "muOS 2410.1 Banana":
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

    if manager.version_var == "muOS 2410.1 Banana":
        muxpower_items = ["shutdown", "battery", "idle_display", "idle_sleep"]
    else:
        muxpower_items = ["shutdown", "battery", "idle_display", "idle_sleep"]
    ensure_folder_exists(temp_image_dir / "static" / "muxpower")
    for item in muxpower_items:
        visualbuttonoverlay_B_SAVE.save(
            temp_image_dir / "static" / "muxpower" / f"{item}.png",
            format="PNG",
        )

    if manager.version_var == "muOS 2410.1 Banana":
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

    if manager.version_var == "muOS 2410.1 Banana":
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

    if manager.version_var == "muOS 2410.1 Banana":
        muxwebserv_items = ["shell", "browser", "terminal", "sync", "resilio", "ntp"]
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

    if manager.version_var == "muOS 2410.1 Banana":
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

    if manager.version_var == "muOS 2410.1 Banana":
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
    progress_bar["value"] += 1

    # TODO REMOVE THIS AS IT DOESNT ALLOW BACKGROUND REPLACEMENT (When Alternative is avaliable)
    # TODO wifi would be cool to have footers for once its possible

    background = theme_generator.generate_background_image(bg_hex)

    visualbuttonoverlay_muxapp = theme_generator.generate_static_overlay_image(
        [["B", "BACK"], ["A", "LAUNCH"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    altered_background = Image.alpha_composite(background, visualbuttonoverlay_muxapp)
    altered_background.save(
        temp_image_dir / "wall" / "muxapp.png",
        format="PNG",
    )
    altered_background.save(
        temp_image_dir / "wall" / "muxtask.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    visualbuttonoverlay_muxplore = theme_generator.generate_static_overlay_image(
        [
            ["MENU", "INFO"],
            ["Y", "FAVOURITE"],
            ["X", "REFRESH"],
            ["B", "BACK"],
            ["A", "OPEN"],
        ],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    altered_background = Image.alpha_composite(background, visualbuttonoverlay_muxplore)
    altered_background.save(
        temp_image_dir / "wall" / "muxplore.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    visualbuttonoverlay_muxfavourite = theme_generator.generate_static_overlay_image(
        [["MENU", "INFO"], ["X", "REMOVE"], ["B", "BACK"], ["A", "OPEN"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    altered_background = Image.alpha_composite(
        background, visualbuttonoverlay_muxfavourite
    )
    altered_background.save(
        temp_image_dir / "wall" / "muxfavourite.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    visualbuttonoverlay_muxhistory = theme_generator.generate_static_overlay_image(
        [
            ["MENU", "INFO"],
            ["Y", "FAVOURITE"],
            ["X", "REMOVE"],
            ["B", "BACK"],
            ["A", "OPEN"],
        ],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    altered_background = Image.alpha_composite(
        background, visualbuttonoverlay_muxhistory
    )
    altered_background.save(
        temp_image_dir / "wall" / "muxhistory.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    visualbuttonoverlay_muxtimezone = theme_generator.generate_static_overlay_image(
        [["A", "SELECT"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    altered_background = Image.alpha_composite(
        background, visualbuttonoverlay_muxtimezone
    )
    altered_background.save(
        temp_image_dir / "wall" / "muxtimezone.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    visualbuttonoverlay_muxpicker = theme_generator.generate_static_overlay_image(
        [["Y", "SAVE"], ["B", "BACK"], ["A", "SELECT"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    altered_background = Image.alpha_composite(
        background, visualbuttonoverlay_muxpicker
    )
    altered_background.save(
        temp_image_dir / "wall" / "muxpicker.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    visualbuttonoverlay_muxlanguage = theme_generator.generate_static_overlay_image(
        [["B", "BACK"], ["A", "SELECT"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    altered_background = Image.alpha_composite(
        background, visualbuttonoverlay_muxlanguage
    )
    altered_background.save(
        temp_image_dir / "wall" / "muxlanguage.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    visualbuttonoverlay_muxarchive = theme_generator.generate_static_overlay_image(
        [["B", "BACK"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    altered_background = Image.alpha_composite(
        background, visualbuttonoverlay_muxarchive
    )
    altered_background.save(
        temp_image_dir / "wall" / "muxarchive.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    visualbuttonoverlay_muxnetprofile = theme_generator.generate_static_overlay_image(
        [["Y", "REMOVE"], ["X", "SAVE"], ["B", "BACK"], ["A", "LOAD"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    altered_background = Image.alpha_composite(
        background, visualbuttonoverlay_muxnetprofile
    )
    altered_background.save(
        temp_image_dir / "wall" / "muxnetprofile.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    visualbuttonoverlay_muxnetscan = theme_generator.generate_static_overlay_image(
        [["X", "RESCAN"], ["B", "BACK"], ["A", "USE"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    altered_background = Image.alpha_composite(
        background, visualbuttonoverlay_muxnetscan
    )
    altered_background.save(
        temp_image_dir / "wall" / "muxnetscan.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    visualbuttonoverlay_muxgov = theme_generator.generate_static_overlay_image(
        [["Y", "RECURSIVE"], ["X", "DIRECTORY"], ["A", "INDIVIDUAL"], ["B", "BACK"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    altered_background = Image.alpha_composite(background, visualbuttonoverlay_muxgov)
    altered_background.save(
        temp_image_dir / "wall" / "muxgov.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    visualbuttonoverlay_muxsearch = theme_generator.generate_static_overlay_image(
        [["X", "CLEAR"], ["B", "BACK"], ["A", "SELECT"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    altered_background = Image.alpha_composite(
        background, visualbuttonoverlay_muxsearch
    )
    altered_background.save(
        temp_image_dir / "wall" / "muxsearch.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    itemsList = []
    if manager.version_var[0:9] == "muOS 2410":
        workingMenus = MENU_LISTING_2410_X

    else:
        raise ValueError("You Haven't Selected a muOS Version")

    workingMenus = [
        [
            "muxlaunch",
            [
                ["Content Explorer", "explore"],
                ["Favourites", "favourite"],
                ["History", "history"],
                ["Applications", "apps"],
                ["Information", "info"],
                ["Configuration", "config"],
                ["Reboot Device", "reboot"],
                ["Shutdown Device", "shutdown"],
            ],
        ]
    ]

    for index, menu in enumerate(workingMenus):
        itemsList.append([])
        for item in menu[1]:
            (itemsList[index].append([item[0], "Menu", item[1]]),)

    preview_theme_generator = PreviewThemeGenerator(manager, render_factor)
    for index, menu in enumerate(workingMenus):
        if menu[0] == "muxdevice":
            ContinuousFolderImageGen(
                progress_bar,
                menu[0],
                itemsList[index],
                textPadding,
                rectanglePadding,
                ItemsPerScreen,
                bg_hex,
                selected_font_hex,
                deselected_font_hex,
                bubble_hex,
                render_factor,
                temp_image_dir / "static",
                manager,
                threadNumber=threadNumber,
            )
        elif menu[0] == "muxlaunch":
            if manager.main_menu_style_var == "Horizontal":
                HorizontalMenuGen(
                    progress_bar,
                    menu[0],
                    itemsList[index],
                    bg_hex,
                    selected_font_hex,
                    deselected_font_hex,
                    bubble_hex,
                    icon_hex,
                    render_factor,
                    temp_image_dir / "static",
                    variant="Horizontal",
                    manager=manager,
                    threadNumber=threadNumber,
                )
            elif manager.main_menu_style_var == "Alt-Horizontal":
                HorizontalMenuGen(
                    progress_bar,
                    menu[0],
                    itemsList[index],
                    bg_hex,
                    selected_font_hex,
                    deselected_font_hex,
                    bubble_hex,
                    icon_hex,
                    render_factor,
                    temp_image_dir / "static",
                    variant="Alt-Horizontal",
                    manager=manager,
                    threadNumber=threadNumber,
                )

        else:
            ContinuousFolderImageGen(
                progress_bar,
                menu[0],
                itemsList[index],
                textPadding,
                rectanglePadding,
                ItemsPerScreen,
                bg_hex,
                selected_font_hex,
                deselected_font_hex,
                bubble_hex,
                render_factor,
                temp_image_dir / "static",
                manager,
                threadNumber=threadNumber,
            )
    fakeprogressbar = {"value": 0}
    fakeprogressbar["maximum"] = 1
    if manager.main_menu_style_var == "Horizontal":
        previewImage = preview_theme_generator.generate_horizontal_menu_image(
            fakeprogressbar,
            0,
            manager.bgHexVar,
            manager.selectedFontHexVar,
            manager.deselectedFontHexVar,
            manager.bubbleHexVar,
            manager.iconHexVar,
            transparent=False,
        )
    elif manager.main_menu_style_var == "Alt-Horizontal":
        previewImage = theme_generator.generate_alt_horizontal_menu(
            fakeprogressbar,
            0,
            manager.bgHexVar,
            manager.selectedFontHexVar,
            manager.deselectedFontHexVar,
            manager.bubbleHexVar,
            manager.iconHexVar,
            transparent=False,
        )
    elif manager.main_menu_style_var == "Vertical":
        previewImage = preview_theme_generator.generate_vertical_menu_image(
            fakeprogressbar,
            0,
            "muxlaunch",
            itemsList[index][0 : int(manager.itemsPerScreenVar)],
            int(manager.textPaddingVar),
            int(manager.bubblePaddingVar),
            int(manager.itemsPerScreenVar),
            manager.bgHexVar,
            manager.selectedFontHexVar,
            manager.deselectedFontHexVar,
            manager.bubbleHexVar,
            transparent=False,
        )
    preview_size = (
        int(0.45 * int(manager.deviceScreenWidthVar)),
        int(0.45 * int(manager.deviceScreenHeightVar)),
    )
    if (
        int(manager.deviceScreenWidthVar) == 720
        and int(manager.deviceScreenHeightVar) == 720
    ):
        preview_size = (340, 340)
    smallPreviewImage = previewImage.resize(preview_size, Image.LANCZOS)
    smallPreviewImage.save(temp_build_dir / "preview.png")
    if manager.developer_preview_var:
        developerPreviewImage = previewImage.resize(
            (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
            Image.LANCZOS,
        )
        developerPreviewImage.save(
            RESOURCES_DIR
            / f"TempPreview{threadNumber}[{manager.deviceScreenWidthVar}x{manager.deviceScreenHeightVar}].png",
        )


def start_theme_task(manager: SettingsManager, *args) -> None:
    dialog = ProgressDialog(
        root, title=f"Generating {manager.theme_name_var}...", max=None
    )

    all_resolutions = []
    for device_type in DEVICE_TYPE_OPTIONS:
        match = re.search(r"\[(\d+)x(\d+)\]", device_type)
        if match:
            all_resolutions.append((int(match.group(1)), int(match.group(2))))

    match = re.search(r"\[(\d+)x(\d+)\]", manager.device_type_var)
    assumed_res = [640, 480]
    if match:
        assumed_res = (int(match.group(1)), int(match.group(2)))
    else:
        raise ValueError("Invalid device type format, cannot find screen dimensions")

    def on_progress(message: str = "", step: int = 1):
        def _update():
            dialog.label["text"] = message
            dialog.progress_bar["value"] += step

        root.after(0, _update)

    def worker():
        try:
            manager.save_user_values()

            generate_theme(
                manager,
                -1,
                all_resolutions,
                assumed_res,
                progress_callback=on_progress,
            )

            root.after(0, dialog.destroy)
            root.after(
                0,
                lambda: messagebox.showinfo("Success", "Theme generated successfully!"),
            )
        except Exception as e:
            root.after(0, dialog.destroy)
            raise e

    threading.Thread(target=worker, daemon=True).start()


def start_bulk_theme_task() -> None:
    # Create a new Toplevel window for the loading bar
    themes = manager.load_premade_themes()

    threading.Thread(target=generate_themes, args=(themes,)).start()


# subtitle_font = font.Font(family="Helvetica", size=14, weight="bold")
# title_font = font.Font(family="Helvetica", size=20, weight="bold")


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
    global background_image
    global preview_overlay_image

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

    # if app.manager.include_overlay_var and app.manager.selected_overlay_var:
    #     preview_overlay_path = (
    #         OVERLAY_DIR
    #         / f"{screen_width}x{screen_height}"
    #         / f"{app.manager.selected_overlay_var}.png"
    #     )
    #     if preview_overlay_path.exists():
    #         preview_overlay_image = Image.open(preview_overlay_path)
    #     else:
    #         preview_overlay_image = None
    # else:
    #     preview_overlay_path = None

    # if (
    #     app.manager.use_custom_background_var
    #     and app.manager.background_image_path
    #     and app.manager.background_image_path.exists()
    # ):
    #     background_image = Image.open(app.manager.background_image_path)
    # else:
    #     background_image = None

    # previewApplicationList = []
    # if app.manager.version_var[0:9] == "muOS 2410":
    #     index = None
    #     for i, n in enumerate(MENU_LISTING_2410_X):
    #         if n[0] == "muxapp":
    #             index = i
    #             break
    #     if index is not None:
    #         previewApplicationList = [
    #             [x[0], "menu", x[0]] for x in MENU_LISTING_2410_X[index][1]
    #         ]

    # previewItemList = [
    #     ["Content Explorer", "Menu", "explore"],
    #     ["Favourites", "Menu", "favourite"],
    #     ["History", "Menu", "history"],
    #     ["Applications", "Menu", "apps"],
    #     ["Information", "Menu", "info"],
    #     ["Configuration", "Menu", "config"],
    #     ["Reboot Device", "Menu", "reboot"],
    #     ["Shutdown Device", "Menu", "shutdown"],
    # ]

    # if app.manager.include_overlay_var and app.manager.selected_overlay_var != "":
    #     preview_overlay_resized = preview_overlay_image.resize(
    #         image1.size, Image.LANCZOS
    #     )
    #     image1.paste(preview_overlay_resized, (0, 0), preview_overlay_resized)
    #     image2.paste(preview_overlay_resized, (0, 0), preview_overlay_resized)
    #     if app.manager.main_menu_style_var != "Vertical":
    #         image3.paste(preview_overlay_resized, (0, 0), preview_overlay_resized)

    update_image_label(app.image_label1, content_preview)
    update_image_label(app.image_label2, info_preview)

    # if app.manager.main_menu_style_var != "Vertical":
    #     update_image_label(app.image_label3, image3)
    # else:
    #     remove_image_from_label(app.image_label3)


# menuNameMap = getAlternateMenuNameDict()

root = tk.Tk()


def main():
    manager = SettingsManager(BASE_SETTINGS_PATH, USER_SETTINGS_PATH)
    manager.load()

    adapter = TkinterSettingsAdapter(manager)

    commands_map = {
        "select_color": select_color,
        "select_bootlogo_image_path": select_bootlogo_image_path,
        "select_background_image_path": select_background_image_path,
        "select_alt_font_path": select_alt_font_path,
        "select_theme_directory_path": select_theme_directory_path,
        "start_theme_task": start_theme_task,
    }

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
