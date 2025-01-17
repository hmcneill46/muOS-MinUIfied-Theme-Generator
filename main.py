import copy
from datetime import datetime
from functools import partial
import json
import math
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

from generator.settings import SettingsManager

try:
    from bidi import get_display as bidi_get_display
except:
    from bidi.algorithm import get_display as bidi_get_display

from PIL import (
    ImageTk,
    Image,
    ImageDraw,
    ImageFont,
    ImageColor,
)

from generator.app import ThemeGeneratorApp
from generator.config import Config
from generator.constants import (
    BASE_DIR,
    RESOURCES_DIR,
    ASSETS_DIR,
    BUTTON_GLYPHS_DIR,
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
)
from generator.font import get_font_path
from generator.utils import (
    copy_contents,
    delete_folder,
    delete_file,
    rename_file,
    ensure_folder_exists,
)

Image.MAX_IMAGE_PIXELS = None

## TODO look into centre align and left align
## TODO make header resizable

background_image = None

manager = SettingsManager(BASE_SETTINGS_PATH, USER_SETTINGS_PATH)
manager.load()

# Define constants
render_factor = 5

contentPaddingTop = 44
textMF = 0.7


def change_logo_color(input: Path | Image.Image, hex_color):
    # Load the image
    if isinstance(input, Image.Image):
        img = input
    else:
        img = Image.open(input).convert("RGBA")

    # Convert hex_color to RGBA
    r, g, b, a = hex_to_rgb(hex_color)

    # Create a new image with the same size and the specified color
    color_image = Image.new("RGBA", img.size, (r, g, b, 255))

    # Get the alpha channel from the original image
    alpha = img.split()[3]

    # Composite the color image with the alpha channel
    result_image = Image.composite(
        color_image, Image.new("RGBA", img.size, (0, 0, 0, 0)), alpha
    )

    return result_image


def generateIndividualButtonGlyph(
    buttonText,
    selected_font_path: Path,
    colour_hex,
    render_factor,
    button_height,
    physical_controller_layout,
) -> Image.Image:
    if colour_hex.startswith("#"):
        colour_hex = colour_hex[1:]

    in_smaller_bubble_font_size = button_height * (20.1 / 40) * render_factor
    inSmallerBubbleFont = ImageFont.truetype(
        selected_font_path, in_smaller_bubble_font_size
    )

    single_letter_font_size = button_height * (28 / 40) * render_factor
    singleLetterFont = ImageFont.truetype(selected_font_path, single_letter_font_size)

    isb_text_bbox = inSmallerBubbleFont.getbbox(buttonText)
    isb_text_height = isb_text_bbox[3] - isb_text_bbox[1]
    in_smaller_bubble_text_y = (
        ((button_height * render_factor) / 2) - (isb_text_height / 2) - isb_text_bbox[1]
    )

    sl_text_bbox = singleLetterFont.getbbox(buttonText)
    sl_text_height = sl_text_bbox[3] - sl_text_bbox[1]
    single_letter_text_y = (
        ((button_height * render_factor) / 2) - (sl_text_height / 2) - sl_text_bbox[1]
    )

    horizontal_small_padding = button_height * (10 / 40)

    rendered_bubble_height = int(button_height * render_factor)

    if buttonText.upper() in ["A", "B", "X", "Y"] and physical_controller_layout in [
        "PlayStation",
        "Xbox",
        "Universal",
    ]:
        buttonSize = (rendered_bubble_height, rendered_bubble_height)
        if physical_controller_layout == "PlayStation":
            image = (
                Image.open(
                    BUTTON_GLYPHS_DIR / "PlayStation" / f"{buttonText.upper()}.png"
                )
                .convert("RGBA")
                .resize(buttonSize, Image.LANCZOS)
            )
        if physical_controller_layout == "Universal":
            image = (
                Image.open(
                    BUTTON_GLYPHS_DIR / "Universal" / f"{buttonText.upper()}.png"
                )
                .convert("RGBA")
                .resize(buttonSize, Image.LANCZOS)
            )
        elif physical_controller_layout == "Xbox":
            if buttonText.upper() == "A":
                image = generateIndividualButtonGlyph(
                    "B",
                    selected_font_path,
                    colour_hex,
                    render_factor,
                    button_height,
                    "Nintendo",
                )
            elif buttonText.upper() == "B":
                image = generateIndividualButtonGlyph(
                    "A",
                    selected_font_path,
                    colour_hex,
                    render_factor,
                    button_height,
                    "Nintendo",
                )
            elif buttonText.upper() == "X":
                image = generateIndividualButtonGlyph(
                    "Y",
                    selected_font_path,
                    colour_hex,
                    render_factor,
                    button_height,
                    "Nintendo",
                )
            elif buttonText.upper() == "Y":
                image = generateIndividualButtonGlyph(
                    "X",
                    selected_font_path,
                    colour_hex,
                    render_factor,
                    button_height,
                    "Nintendo",
                )

    elif len(buttonText) == 1:
        image = Image.new(
            "RGBA", (rendered_bubble_height, rendered_bubble_height), (255, 255, 255, 0)
        )
        draw = ImageDraw.Draw(image)

        circleCentreX = (rendered_bubble_height) / 2
        draw.ellipse(
            (0, 0, rendered_bubble_height, rendered_bubble_height),
            fill=f"#{colour_hex}",
        )
        singleLetterWidth = sl_text_bbox[2] - sl_text_bbox[0]
        smallerTextX = circleCentreX - (singleLetterWidth / 2)
        draw.text(
            (smallerTextX, single_letter_text_y),
            buttonText,
            font=singleLetterFont,
            fill=(*ImageColor.getrgb(f"#{colour_hex}"), int(255 * 0.593)),
        )

    else:
        ## Make the smaller bubble
        smallerTextBbox = inSmallerBubbleFont.getbbox(buttonText)
        smallerTextWidth = smallerTextBbox[2] - smallerTextBbox[0]
        smallerBubbleWidth = int(
            horizontal_small_padding
            + smallerTextWidth / render_factor
            + horizontal_small_padding
        )

        rendered_smallerBubbleWidth = int(smallerBubbleWidth * render_factor)

        image = Image.new(
            "RGBA",
            (rendered_smallerBubbleWidth, rendered_bubble_height),
            (255, 255, 255, 0),
        )
        draw = ImageDraw.Draw(image)

        draw.rounded_rectangle(
            [
                (0, 0),  # bottom left point
                (rendered_smallerBubbleWidth, rendered_bubble_height),
            ],  # Top right point
            radius=(math.ceil(button_height / 2)) * render_factor,
            fill=hex_to_rgb(colour_hex, alpha=1),
        )
        smallerTextX = horizontal_small_padding * render_factor
        draw.text(
            (smallerTextX, in_smaller_bubble_text_y),
            buttonText,
            font=inSmallerBubbleFont,
            fill=(*ImageColor.getrgb(f"#{colour_hex}"), int(255 * 0.593)),
        )
    return image


def getTimeWithWidth(selected_font_path: Path, timeFormat, find="max"):
    TestFont = ImageFont.truetype(selected_font_path, 100)
    stringsByActualSize = {
        "0": 0,
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "7": 0,
        "8": 0,
        "9": 0,
        "AM": 0,
        "PM": 0,
    }

    # Calculate the width of each character by repeating it
    for n in stringsByActualSize.keys():
        numberMultiplier = 100
        stringsByActualSizeBbox = TestFont.getbbox(f"{str(n) * numberMultiplier}")
        stringsByActualSizeWidth = (
            stringsByActualSizeBbox[2] - stringsByActualSizeBbox[0]
        )
        stringsByActualSize[n] = stringsByActualSizeWidth

    # Sort by width to easily find min or max
    sortedStringsByActualSize = dict(
        sorted(stringsByActualSize.items(), key=lambda item: item[1])
    )

    # Set the criteria for finding the desired width based on `find` argument
    if find == "max":
        lastDigit = max(
            (s for s in sortedStringsByActualSize if any(char.isdigit() for char in s)),
            key=sortedStringsByActualSize.get,
        )
        secondLastDigit = max(
            (s for s in sortedStringsByActualSize if s.isdigit() and int(s) < 6),
            key=sortedStringsByActualSize.get,
        )
    elif find == "min":
        lastDigit = min(
            (s for s in sortedStringsByActualSize if any(char.isdigit() for char in s)),
            key=sortedStringsByActualSize.get,
        )
        secondLastDigit = min(
            (s for s in sortedStringsByActualSize if s.isdigit() and int(s) < 6),
            key=sortedStringsByActualSize.get,
        )
    else:
        raise ValueError("Invalid option for 'find'. Choose 'max' or 'min'.")

    firstDigits = None
    widthResult = 0 if find == "max" else float("inf")
    possibleFirstDigits = range(1, 13) if timeFormat == "12 Hour" else range(0, 24)

    # Adjust search logic for max or min width
    for n in possibleFirstDigits:
        currentString = str(n).zfill(2)
        digit1, digit2 = currentString[0], currentString[1]
        width1, width2 = (
            sortedStringsByActualSize[digit1],
            sortedStringsByActualSize[digit2],
        )
        currentWidth = width1 + width2

        if (find == "max" and currentWidth > widthResult) or (
            find == "min" and currentWidth < widthResult
        ):
            widthResult = currentWidth
            firstDigits = currentString

    if timeFormat == "12 Hour":
        suffex = (
            max(
                (
                    s
                    for s in sortedStringsByActualSize
                    if not any(char.isdigit() for char in s)
                ),
                key=sortedStringsByActualSize.get,
            )
            if find == "max"
            else min(
                (
                    s
                    for s in sortedStringsByActualSize
                    if not any(char.isdigit() for char in s)
                ),
                key=sortedStringsByActualSize.get,
            )
        )
        timeText = f"{firstDigits}:{secondLastDigit}{lastDigit} {suffex}"
    else:
        timeText = f"{firstDigits}:{secondLastDigit}{lastDigit}"

    return timeText


def generateHeaderBubbles(
    manager: Config, render_factor, accent_colour=None, bubble_alpha=0.133
):
    image = Image.new(
        "RGBA",
        (
            int(manager.deviceScreenWidthVar) * render_factor,
            int(manager.deviceScreenHeightVar) * render_factor,
        ),
        (255, 255, 255, 0),
    )
    draw = ImageDraw.Draw(image)
    if accent_colour == None:
        accent_colour = manager.deselectedFontHexVar
    if accent_colour.startswith("#"):
        accent_colour = accent_colour[1:]

    if int(manager.header_text_height_var) < 10:
        raise ValueError("Header Text Height Too Small!")
    elif int(manager.header_text_height_var) > int(manager.headerHeightVar):
        raise ValueError("Header Text Height Too Large!")
    else:
        heightOfText = int(int(manager.header_text_height_var) * render_factor)

    fontHeight = int(
        int((heightOfText * (4 / 3)) / render_factor) * render_factor
    )  ## TODO Make this not specific to BPreplay
    headerFont = ImageFont.truetype(
        get_font_path(manager.use_alt_font_var, manager.alt_font_filename), fontHeight
    )

    if (
        int(manager.header_text_bubble_height_var) - int(manager.header_text_height_var)
        >= 0
    ):
        headerTextPadding = int(
            (
                int(manager.header_text_bubble_height_var)
                - int(manager.header_text_height_var)
            )
            / 2
        )
    else:
        raise ValueError("Header Glyph Height Too Large!")

    headerMiddleY = (int(manager.headerHeightVar) * render_factor) / 2

    bottom_y_points = {}
    top_y_points = {}
    left_x_points = {}
    right_x_points = {}

    if manager.show_clock_bubbles_var:
        clock_left_padding = int(manager.clockHorizontalLeftPaddingVar)
        clock_right_padding = int(manager.clockHorizontalRightPaddingVar)

        timeText = getTimeWithWidth(
            get_font_path(manager.use_alt_font_var, manager.alt_font_filename),
            manager.clock_format_var,
            find="max",
        )
        maxTimeTextWidth = (
            headerFont.getbbox(timeText)[2] - headerFont.getbbox(timeText)[0]
        )

        if manager.clock_alignment_var == "Left":
            timeText_X = clock_left_padding * render_factor
        elif manager.clock_alignment_var == "Centre":
            timeText_X = (
                int(
                    (int(manager.deviceScreenWidthVar) * render_factor) / 2
                    - (
                        (
                            maxTimeTextWidth
                            + (
                                clock_right_padding * render_factor
                                + clock_left_padding * render_factor
                            )
                        )
                        / 2
                    )
                )
                + clock_left_padding * render_factor
            )
        elif manager.clock_alignment_var == "Right":
            timeText_X = int(int(manager.deviceScreenWidthVar) * render_factor) - (
                maxTimeTextWidth + clock_right_padding * render_factor
            )
        else:
            raise ValueError("Invalid clock alignment")

        bottom_y_points["clock"] = headerMiddleY - (
            (int(manager.header_text_bubble_height_var) * render_factor) / 2
        )
        top_y_points["clock"] = headerMiddleY + (
            (int(manager.header_text_bubble_height_var) * render_factor) / 2
        )
        left_x_points["clock"] = timeText_X - (headerTextPadding * render_factor)
        right_x_points["clock"] = (
            timeText_X + maxTimeTextWidth + (headerTextPadding * render_factor)
        )

    if float(manager.header_glyph_height_var) < 10:
        raise ValueError("Header Glyph Height Too Small!")
    elif float(manager.header_glyph_height_var) > int(manager.headerHeightVar):
        raise ValueError("Header Glyph Height Too Large!")
    else:
        heightOfGlyph = int(float(manager.header_glyph_height_var) * render_factor)

    if (
        int(manager.header_glyph_bubble_height_var)
        - int(manager.header_glyph_height_var)
        >= 0
    ):
        headerGlyphPadding = int(
            (
                int(manager.header_glyph_bubble_height_var)
                - int(manager.header_glyph_height_var)
            )
            / 2
        )
    else:
        raise ValueError("Header Glyph Height Too Large!")
    if manager.show_glyphs_bubbles_var:
        # Battery not charging stuff
        capacityGlyph = "capacity_30.png"
        capacity_image_path = GLYPHS_DIR / f"{capacityGlyph[:-4]}[5x].png"

        capacity_image_coloured = change_logo_color(capacity_image_path, accent_colour)
        capacity_image_coloured = capacity_image_coloured.resize(
            (
                int(
                    heightOfGlyph
                    * (
                        capacity_image_coloured.size[0]
                        / capacity_image_coloured.size[1]
                    )
                ),
                heightOfGlyph,
            ),
            Image.LANCZOS,
        )
        glyph_left_side_padding = int(manager.header_glyph_horizontal_left_padding_var)
        glyph_right_side_padding = int(
            manager.header_glyph_horizontal_right_padding_var
        )
        glyph_between_padding = 5

        networkGlyph = "network_active"
        network_image_path = GLYPHS_DIR / f"{networkGlyph}[5x].png"

        network_image_coloured = change_logo_color(network_image_path, accent_colour)
        network_image_coloured = network_image_coloured.resize(
            (
                int(
                    heightOfGlyph
                    * (network_image_coloured.size[0] / network_image_coloured.size[1])
                ),
                heightOfGlyph,
            ),
            Image.LANCZOS,
        )

        glyphTotalWidth = (
            capacity_image_coloured.size[0]
            + glyph_between_padding * render_factor
            + network_image_coloured.size[0]
        )

        if manager.header_glyph_alignment_var == "Left":
            current_x_pos = glyph_left_side_padding * render_factor
        elif manager.header_glyph_alignment_var == "Centre":
            current_x_pos = (
                int(
                    (int(manager.deviceScreenWidthVar) * render_factor) / 2
                    - (
                        (
                            glyphTotalWidth
                            + (
                                glyph_right_side_padding * render_factor
                                + glyph_left_side_padding * render_factor
                            )
                        )
                        / 2
                    )
                )
                + glyph_left_side_padding * render_factor
            )
        elif manager.header_glyph_alignment_var == "Right":
            current_x_pos = int(
                int(manager.deviceScreenWidthVar) * render_factor
                - (glyph_right_side_padding * render_factor + glyphTotalWidth)
            )
        else:
            raise ValueError("Invalid clock alignment")

        glyphBubbleXPos = int(int(manager.deviceScreenWidthVar) * render_factor) - (
            glyphTotalWidth + glyph_left_side_padding * render_factor
        )

        bottom_y_points["glyphs"] = headerMiddleY - (
            (int(manager.header_glyph_bubble_height_var) * render_factor) / 2
        )
        top_y_points["glyphs"] = headerMiddleY + (
            (int(manager.header_glyph_bubble_height_var) * render_factor) / 2
        )
        left_x_points["glyphs"] = current_x_pos - (headerGlyphPadding * render_factor)
        right_x_points["glyphs"] = (
            current_x_pos + glyphTotalWidth + (headerGlyphPadding * render_factor)
        )

    if manager.join_header_bubbles_var and (
        manager.show_glyphs_bubbles_var or manager.show_clock_bubbles_var
    ):
        bottom_y = min(bottom_y_points.values())
        top_y = max(top_y_points.values())
        left_x = min(left_x_points.values())
        right_x = max(right_x_points.values())

        draw.rounded_rectangle(
            [
                (left_x, bottom_y),  # bottom left point
                (right_x, top_y),
            ],  # Top right point
            radius=math.ceil((top_y - bottom_y) / 2),
            fill=hex_to_rgb(accent_colour, alpha=bubble_alpha),
        )
    else:
        for key in bottom_y_points.keys():
            draw.rounded_rectangle(
                [
                    (left_x_points[key], bottom_y_points[key]),  # bottom left point
                    (right_x_points[key], top_y_points[key]),
                ],  # Top right point
                radius=math.ceil((top_y_points[key] - bottom_y_points[key]) / 2),
                fill=hex_to_rgb(accent_colour, alpha=bubble_alpha),
            )

    return image


def generatePilImageMuOSOverlay(manager: Config, muOSpageName, render_factor):
    muOSpageNameDict = {
        "muxlaunch": "MAIN MENU",
        "muxconfig": "CONFIGURATION",
        "muxinfo": "INFORMATION",
        "muxapp": "APPLICATIONS",
        "muxplore": "ROMS",
        "muxfavourite": "FAVOURITES",
        "muxhistory": "HISTORY",
    }
    current_time = datetime.now()
    image = Image.new(
        "RGBA",
        (
            int(manager.deviceScreenWidthVar) * render_factor,
            int(manager.deviceScreenHeightVar) * render_factor,
        ),
        (255, 255, 255, 0),
    )
    draw = ImageDraw.Draw(image)
    if float(manager.header_glyph_height_var) < 10:
        raise ValueError("Header Glyph Height Too Small!")
    elif float(manager.header_glyph_height_var) > int(manager.headerHeightVar):
        raise ValueError("Header Glyph Height Too Large!")
    else:
        heightOfGlyph = int(float(manager.header_glyph_height_var) * render_factor)
    accent_colour = manager.deselectedFontHexVar
    if accent_colour.startswith("#"):
        accent_colour = accent_colour[1:]
    if "showing battery and network":
        glyphYPos = int(
            ((int(manager.headerHeightVar) * render_factor) / 2) - (heightOfGlyph / 2)
        )

        # Battery not charging stuff
        capacityGlyph = "30"
        capacity_image_path = (
            GLYPHS_DIR
            / f"{BatteryStyleOptionsDict[manager.battery_style_var]}{capacityGlyph}[5x].png"
        )

        capacity_image_coloured = change_logo_color(capacity_image_path, accent_colour)
        capacity_image_coloured = capacity_image_coloured.resize(
            (
                int(
                    heightOfGlyph
                    * (
                        capacity_image_coloured.size[0]
                        / capacity_image_coloured.size[1]
                    )
                ),
                heightOfGlyph,
            ),
            Image.LANCZOS,
        )

        capacityChargingGlyph = "30"
        capacity_charging_image_path = (
            GLYPHS_DIR
            / f"{BatteryChargingStyleOptionsDict[manager.battery_charging_style_var]}{capacityChargingGlyph}[5x].png"
        )

        capacity_charging_image_coloured = change_logo_color(
            capacity_charging_image_path, manager.batteryChargingHexVar
        )
        capacity_charging_image_coloured = capacity_charging_image_coloured.resize(
            (
                int(
                    heightOfGlyph
                    * (
                        capacity_charging_image_coloured.size[0]
                        / capacity_charging_image_coloured.size[1]
                    )
                ),
                heightOfGlyph,
            ),
            Image.LANCZOS,
        )

        networkGlyph = "network_active"
        network_image_path = GLYPHS_DIR / f"{networkGlyph}[5x].png"

        network_image_coloured = change_logo_color(network_image_path, accent_colour)
        network_image_coloured = network_image_coloured.resize(
            (
                int(
                    heightOfGlyph
                    * (network_image_coloured.size[0] / network_image_coloured.size[1])
                ),
                heightOfGlyph,
            ),
            Image.LANCZOS,
        )

        glyph_left_side_padding = int(manager.header_glyph_horizontal_left_padding_var)
        glyph_right_side_padding = int(
            manager.header_glyph_horizontal_right_padding_var
        )
        glyph_between_padding = 5

        totalGlyphWidth = (
            capacity_image_coloured.size[0]
            + glyph_between_padding * render_factor
            + network_image_coloured.size[0]
        )
        if manager.header_glyph_alignment_var == "Left":
            current_x_pos = glyph_left_side_padding * render_factor
        elif manager.header_glyph_alignment_var == "Centre":
            current_x_pos = (
                int(
                    (int(manager.deviceScreenWidthVar) * render_factor) / 2
                    - (
                        (
                            totalGlyphWidth
                            + (
                                glyph_right_side_padding * render_factor
                                + glyph_left_side_padding * render_factor
                            )
                        )
                        / 2
                    )
                )
                + glyph_left_side_padding * render_factor
            )
        elif manager.header_glyph_alignment_var == "Right":
            current_x_pos = int(
                int(manager.deviceScreenWidthVar) * render_factor
                - (glyph_right_side_padding * render_factor + totalGlyphWidth)
            )
        else:
            raise ValueError("Invalid clock alignment")

        image.paste(
            network_image_coloured, (current_x_pos, glyphYPos), network_image_coloured
        )

        current_x_pos += (
            network_image_coloured.size[0] + glyph_between_padding * render_factor
        )

        if not manager.show_charging_battery_var:
            image.paste(
                capacity_image_coloured,
                (current_x_pos, glyphYPos),
                capacity_image_coloured,
            )

        if manager.show_charging_battery_var:
            image.paste(
                capacity_charging_image_coloured,
                (current_x_pos, glyphYPos),
                capacity_charging_image_coloured,
            )

    if int(manager.header_text_height_var) < 10:
        raise ValueError("Header Text Height Too Small!")
    elif int(manager.header_text_height_var) > int(manager.headerHeightVar):
        raise ValueError("Header Text Height Too Large!")
    else:
        heightOfText = int(int(manager.header_text_height_var) * render_factor)

    fontSize = int(
        int((heightOfText * (4 / 3)) / render_factor) * render_factor
    )  ## TODO Make this not specific to BPreplay
    headerFont = ImageFont.truetype(
        get_font_path(manager.use_alt_font_var, manager.alt_font_filename),
        fontSize,
    )
    if "showing time":
        clock_left_padding = int(manager.clockHorizontalLeftPaddingVar)
        clock_right_padding = int(manager.clockHorizontalRightPaddingVar)

        if manager.clock_format_var == "12 Hour":
            timeText = current_time.strftime("%I:%M %p")
        else:
            timeText = current_time.strftime("%H:%M")

        # timeText = getTimeWithWidth(os.path.join(internal_files_dir,"Assets","Font","BPreplayBold-unhinted.otf"),manager.clock_format_var,find="max")
        # timeText = getTimeWithWidth(os.path.join(internal_files_dir,"Assets","Font","BPreplayBold-unhinted.otf"),manager.clock_format_var,find="min")

        timeTextBbox = headerFont.getbbox(timeText)
        timeTextWidth = timeTextBbox[2] - timeTextBbox[0]
        if manager.clock_alignment_var == "Left":
            timeText_X = clock_left_padding * render_factor
        elif manager.clock_alignment_var == "Centre":
            timeText_X = (
                int(
                    (int(manager.deviceScreenWidthVar) * render_factor) / 2
                    - (
                        (
                            timeTextWidth
                            + (
                                clock_right_padding * render_factor
                                + clock_left_padding * render_factor
                            )
                        )
                        / 2
                    )
                )
                + clock_left_padding * render_factor
            )
        elif manager.clock_alignment_var == "Right":
            timeText_X = int(int(manager.deviceScreenWidthVar) * render_factor) - (
                timeTextWidth + clock_right_padding * render_factor
            )
        else:
            raise ValueError("Invalid clock alignment")
        timeText_Y = (
            int(
                ((int(manager.headerHeightVar) * render_factor) / 2)
                - (heightOfText / 2)
            )
            - timeTextBbox[1]
        )
        draw.text(
            (timeText_X, timeText_Y),
            timeText,
            font=headerFont,
            fill=(*ImageColor.getrgb(f"#{accent_colour}"), 255),
        )
    if manager.show_console_name_var:
        page_title_padding = int(manager.pageTitlePaddingVar)
        pageTitle = muOSpageNameDict.get(muOSpageName, "UNKNOWN")
        pageTitleBbox = headerFont.getbbox(pageTitle)
        pageTitleWidth = pageTitleBbox[2] - pageTitleBbox[0]
        if manager.page_title_alignment_var == "Left":
            pageTitle_X = page_title_padding * render_factor
        elif manager.page_title_alignment_var == "Centre":
            pageTitle_X = int(
                (int(manager.deviceScreenWidthVar) * render_factor) / 2
                - (pageTitleWidth / 2)
            )
        elif manager.page_title_alignment_var == "Right":
            pageTitle_X = int(int(manager.deviceScreenWidthVar) * render_factor) - (
                pageTitleWidth + page_title_padding * render_factor
            )
        else:
            raise ValueError("Invalid page title alignment")
        pageTitle_Y = (
            int(
                ((int(manager.headerHeightVar) * render_factor) / 2)
                - (heightOfText / 2)
            )
            - pageTitleBbox[1]
        )
        draw.text(
            (pageTitle_X, pageTitle_Y),
            pageTitle,
            font=headerFont,
            fill=(*ImageColor.getrgb(f"#{accent_colour}"), 255),
        )

    return image


def getRealFooterHeight(manager: Config) -> int:
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
    return footerHeight


def generateMenuHelperGuides(
    retro_rhs_buttons,
    selected_font_path: Path,
    colour_hex,
    render_factor,
    manager: Config,
    lhsButtons=[["POWER", "SLEEP"]],
):
    if colour_hex.startswith("#"):
        colour_hex = colour_hex[1:]

    image = Image.new(
        "RGBA",
        (
            int(manager.deviceScreenWidthVar) * render_factor,
            int(manager.deviceScreenHeightVar) * render_factor,
        ),
        (255, 255, 255, 0),
    )
    draw = ImageDraw.Draw(image)

    real_rhs_buttons = []

    if manager.muos_button_swap_var == "Modern":
        for pair in retro_rhs_buttons:
            if pair[0].upper() == "A":
                real_rhs_buttons.append(["B", pair[1]])
            elif pair[0].upper() == "B":
                real_rhs_buttons.append(["A", pair[1]])
            elif pair[0].upper() == "X":
                real_rhs_buttons.append(["Y", pair[1]])
            elif pair[0].upper() == "Y":
                real_rhs_buttons.append(["X", pair[1]])
    else:
        real_rhs_buttons = retro_rhs_buttons

    if not (
        manager.remove_left_menu_guides_var and manager.remove_right_menu_guides_var
    ):
        required_padding_between_sides = 15  # This is the maximum space between the two sides of the menu helper guides
        lhsTotalWidth = 0
        rhsTotalWidth = int(manager.deviceScreenWidthVar)
        iterations = 0
        from_sides_padding = int(manager.VBG_Horizontal_Padding_var)
        remove_left_menu_guides_var = manager.remove_left_menu_guides_var
        remove_right_menu_guides_var = manager.remove_right_menu_guides_var
        if remove_left_menu_guides_var or remove_right_menu_guides_var:
            required_padding_between_sides = 0
        while (
            from_sides_padding
            + lhsTotalWidth
            + required_padding_between_sides
            + rhsTotalWidth
            + from_sides_padding
            > int(manager.deviceScreenWidthVar)
        ):
            if iterations == 0:
                from_sides_padding = int(manager.VBG_Horizontal_Padding_var)
            if False:  # TODO an option for this
                remove_left_menu_guides_var = True
                required_padding_between_sides = 0
            from_bottom_padding = int(manager.VBG_Vertical_Padding_var) + iterations

            individualItemHeight = round(
                (
                    int(manager.deviceScreenHeightVar)
                    - int(manager.approxFooterHeightVar)
                    - int(manager.contentPaddingTopVar)
                )
                / int(manager.itemsPerScreenVar)
            )

            muosSpaceBetweenItems = 2

            footerHeight = (
                int(manager.deviceScreenHeightVar)
                - (individualItemHeight * int(manager.itemsPerScreenVar))
                - int(manager.contentPaddingTopVar)
                + muosSpaceBetweenItems
            )

            menu_helper_guide_height = footerHeight - (
                from_bottom_padding * 2
            )  # Change this if overlayed

            in_smaller_bubble_font_size = (
                menu_helper_guide_height * (20.1 / 60) * render_factor
            )
            inSmallerBubbleFont = ImageFont.truetype(
                selected_font_path, in_smaller_bubble_font_size
            )

            in_bubble_font_size = menu_helper_guide_height * (24 / 60) * render_factor
            inBubbleFont = ImageFont.truetype(selected_font_path, in_bubble_font_size)

            single_letter_font_size = (
                menu_helper_guide_height * (28 / 60) * render_factor
            )
            singleLetterFont = ImageFont.truetype(
                selected_font_path, single_letter_font_size
            )

            horizontal_small_padding = menu_helper_guide_height * (10 / 60)
            horizontal_padding = menu_helper_guide_height * (10 / 60)
            horizontal_large_padding = menu_helper_guide_height * (
                20 / 60
            )  # Testing here

            bottom_guide_middle_y = (
                int(manager.deviceScreenHeightVar)
                - from_bottom_padding
                - (menu_helper_guide_height / 2)
            )

            guide_small_bubble_height = menu_helper_guide_height - (
                horizontal_padding * 2
            )

            isb_ascent, isb_descent = inSmallerBubbleFont.getmetrics()
            isb_text_height = isb_ascent + isb_descent
            in_smaller_bubble_text_y = bottom_guide_middle_y * render_factor - (
                isb_text_height / 2
            )

            ib_ascent, ib_descent = inBubbleFont.getmetrics()
            ib_text_height = ib_ascent + ib_descent
            in_bubble_text_y = bottom_guide_middle_y * render_factor - (
                ib_text_height / 2
            )

            sl_text_bbox = singleLetterFont.getbbox("ABXY")
            sl_text_height = sl_text_bbox[3] - sl_text_bbox[1]
            single_letter_text_y = (
                bottom_guide_middle_y * render_factor
                - (sl_text_height / 2)
                - sl_text_bbox[1]
            )

            ##TODO convert buttons at this point to lanuage of choice in their respective arrays

            combined_width = 0
            lhsTotalWidth = 0
            rhsTotalWidth = 0

            if not remove_left_menu_guides_var:
                lhsTotalWidth += getTotalBubbleWidth(
                    lhsButtons,
                    inSmallerBubbleFont,
                    inBubbleFont,
                    horizontal_padding,
                    horizontal_large_padding,
                    horizontal_small_padding,
                    guide_small_bubble_height,
                    render_factor,
                )
                combined_width += lhsTotalWidth

            if not remove_right_menu_guides_var:
                rhsTotalWidth += getTotalBubbleWidth(
                    real_rhs_buttons,
                    inSmallerBubbleFont,
                    inBubbleFont,
                    horizontal_padding,
                    horizontal_large_padding,
                    horizontal_small_padding,
                    guide_small_bubble_height,
                    render_factor,
                )
                combined_width += rhsTotalWidth
            iterations += 1

        if not remove_left_menu_guides_var:
            realLhsPointer = from_sides_padding * render_factor
            ## Make the main long bubble
            draw.rounded_rectangle(
                [
                    (
                        realLhsPointer,
                        (bottom_guide_middle_y - menu_helper_guide_height / 2)
                        * render_factor,
                    ),  # bottom left point
                    (
                        realLhsPointer + (lhsTotalWidth * render_factor),
                        (bottom_guide_middle_y + menu_helper_guide_height / 2)
                        * render_factor,
                    ),
                ],  # Top right point
                radius=(menu_helper_guide_height / 2) * render_factor,
                fill=hex_to_rgb(colour_hex, alpha=0.133),
            )
            realLhsPointer += horizontal_padding * render_factor
            for pair in lhsButtons:
                button_image = generateIndividualButtonGlyph(
                    pair[0],
                    selected_font_path,
                    colour_hex,
                    render_factor,
                    guide_small_bubble_height,
                    manager.physical_controler_layout_var,
                )
                button_image = change_logo_color(button_image, colour_hex)
                image.paste(
                    button_image,
                    (
                        int(realLhsPointer),
                        int(
                            bottom_guide_middle_y * render_factor
                            - (button_image.size[1] / 2)
                        ),
                    ),
                    button_image,
                )
                realLhsPointer += (
                    (button_image.size[0]) + (horizontal_small_padding) * render_factor
                )

                textBbox = inBubbleFont.getbbox(pair[1])
                textWidth = textBbox[2] - textBbox[0]
                draw.text(
                    (realLhsPointer, in_bubble_text_y),
                    pair[1],
                    font=inBubbleFont,
                    fill=f"#{colour_hex}",
                )
                realLhsPointer += textWidth
                realLhsPointer += horizontal_large_padding * render_factor
        if not remove_right_menu_guides_var:
            realRhsPointer = (
                int(manager.deviceScreenWidthVar) - from_sides_padding - rhsTotalWidth
            ) * render_factor
            ## Make the main long bubble
            draw.rounded_rectangle(
                [
                    (
                        realRhsPointer,
                        (bottom_guide_middle_y - menu_helper_guide_height / 2)
                        * render_factor,
                    ),  # bottom left point
                    (
                        realRhsPointer + (rhsTotalWidth * render_factor),
                        (bottom_guide_middle_y + menu_helper_guide_height / 2)
                        * render_factor,
                    ),
                ],  # Top right point
                radius=(menu_helper_guide_height / 2) * render_factor,
                fill=hex_to_rgb(colour_hex, alpha=0.133),
            )
            realRhsPointer += horizontal_padding * render_factor
            for pair in real_rhs_buttons:
                button_image = generateIndividualButtonGlyph(
                    pair[0],
                    selected_font_path,
                    colour_hex,
                    render_factor,
                    guide_small_bubble_height,
                    manager.physical_controler_layout_var,
                )
                button_image = change_logo_color(button_image, colour_hex)

                image.paste(
                    button_image,
                    (
                        int(realRhsPointer),
                        int(
                            bottom_guide_middle_y * render_factor
                            - (button_image.size[1] / 2)
                        ),
                    ),
                    button_image,
                )
                realRhsPointer += (
                    (button_image.size[0]) + (horizontal_small_padding) * render_factor
                )

                textBbox = inBubbleFont.getbbox(pair[1])
                textWidth = textBbox[2] - textBbox[0]
                draw.text(
                    (realRhsPointer, in_bubble_text_y),
                    pair[1],
                    font=inBubbleFont,
                    fill=f"#{colour_hex}",
                )
                realRhsPointer += textWidth
                realRhsPointer += horizontal_large_padding * render_factor
    return image


def generateMuOSBackgroundOverlay(
    rhsButtons,
    selected_font_path,
    colour_hex,
    render_factor,
    manager: Config,
    lhsButtons=[["POWER", "SLEEP"]],
):
    if colour_hex.startswith("#"):
        colour_hex = colour_hex[1:]

    image = Image.new(
        "RGBA",
        (
            int(manager.deviceScreenWidthVar) * render_factor,
            int(manager.deviceScreenHeightVar) * render_factor,
        ),
        (255, 255, 255, 0),
    )
    draw = ImageDraw.Draw(image)

    menuHelperGuides = generateMenuHelperGuides(
        rhsButtons,
        selected_font_path,
        colour_hex,
        render_factor,
        manager,
        lhsButtons=lhsButtons,
    )

    image = Image.alpha_composite(image, menuHelperGuides)
    headerBubbles = generateHeaderBubbles(manager, render_factor)

    image = Image.alpha_composite(image, headerBubbles)

    return image


def getTotalBubbleWidth(
    buttons,
    internalBubbleFont,
    bubbleFont,
    initalPadding,
    largerPadding,
    smallerPadding,
    circleWidth,
    render_factor,
):
    totalWidth = initalPadding
    for pair in buttons:
        # pair[0] might be MENU, POWER, or ABXY
        if len(pair[0]) == 1:
            totalWidth += circleWidth
        else:
            totalWidth += smallerPadding
            smallerTextBbox = internalBubbleFont.getbbox(pair[0])
            smallerTextWidth = smallerTextBbox[2] - smallerTextBbox[0]
            totalWidth += smallerTextWidth / render_factor
            totalWidth += smallerPadding
        totalWidth += smallerPadding
        # pair[1] might be something like INFO, FAVOURITE, REFRESH etc...
        textBbox = bubbleFont.getbbox(pair[1])
        textWidth = textBbox[2] - textBbox[0]
        totalWidth += textWidth / render_factor
        totalWidth += largerPadding
    return totalWidth


def generatePilImageVertical(
    progress_bar,
    workingIndex,
    muOSSystemName,
    listItems,
    textPadding,
    rectanglePadding,
    ItemsPerScreen,
    bg_hex,
    selected_font_hex,
    deselected_font_hex,
    bubble_hex,
    render_factor,
    manager: Config,
    numScreens=0,
    screenIndex=0,
    fileCounter="",
    folderName=None,
    transparent=False,
    forPreview=False,
):
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

    progress_bar["value"] += 1
    bg_rgb = hex_to_rgb(bg_hex)
    if not transparent:
        image = Image.new(
            "RGBA",
            (
                int(manager.deviceScreenWidthVar) * render_factor,
                int(manager.deviceScreenHeightVar) * render_factor,
            ),
            bg_rgb,
        )

        if background_image != None:
            image.paste(
                background_image.resize(
                    (
                        int(manager.deviceScreenWidthVar) * render_factor,
                        int(manager.deviceScreenHeightVar) * render_factor,
                    )
                ),
                (0, 0),
            )
    else:
        image = Image.new(
            "RGBA",
            (
                int(manager.deviceScreenWidthVar) * render_factor,
                int(manager.deviceScreenHeightVar) * render_factor,
            ),
            (0, 0, 0, 0),
        )

    draw = ImageDraw.Draw(image)

    boxArtDrawn = False
    boxArtWidth = 0
    if len(listItems) == 0:
        return image

    selected_font_path = get_font_path(
        manager.use_alt_font_var, manager.alt_font_filename
    )

    if muOSSystemName == "muxlaunch":
        menuHelperGuides = generateMenuHelperGuides(
            [["A", "SELECT"]],
            selected_font_path,
            manager.footerBubbleHexVar,
            render_factor,
            manager,
            lhsButtons=[["POWER", "SLEEP"]],
        )
    elif muOSSystemName == "muxconfig" or muOSSystemName == "muxinfo":
        menuHelperGuides = generateMenuHelperGuides(
            [["B", "BACK"], ["A", "SELECT"]],
            selected_font_path,
            manager.footerBubbleHexVar,
            render_factor,
            manager,
            lhsButtons=[["POWER", "SLEEP"]],
        )
    elif muOSSystemName == "muxapp":
        menuHelperGuides = generateMenuHelperGuides(
            [["B", "BACK"], ["A", "LAUNCH"]],
            selected_font_path,
            manager.footerBubbleHexVar,
            render_factor,
            manager,
            lhsButtons=[["POWER", "SLEEP"]],
        )
    elif muOSSystemName == "muxplore":
        menuHelperGuides = generateMenuHelperGuides(
            [
                ["MENU", "INFO"],
                ["Y", "FAVOURITE"],
                ["X", "REFRESH"],
                ["B", "BACK"],
                ["A", "OPEN"],
            ],
            selected_font_path,
            manager.footerBubbleHexVar,
            render_factor,
            manager,
            lhsButtons=[["POWER", "SLEEP"]],
        )
    elif muOSSystemName == "muxfavourite":
        menuHelperGuides = generateMenuHelperGuides(
            [["MENU", "INFO"], ["X", "REMOVE"], ["B", "BACK"], ["A", "OPEN"]],
            selected_font_path,
            manager.footerBubbleHexVar,
            render_factor,
            manager,
            lhsButtons=[["POWER", "SLEEP"]],
        )
    elif muOSSystemName == "muxhistory":
        menuHelperGuides = generateMenuHelperGuides(
            [
                ["MENU", "INFO"],
                ["Y", "FAVOURITE"],
                ["X", "REMOVE"],
                ["B", "BACK"],
                ["A", "OPEN"],
            ],
            selected_font_path,
            manager.footerBubbleHexVar,
            render_factor,
            manager,
            lhsButtons=[["POWER", "SLEEP"]],
        )

    if manager.show_file_counter_var == 1:
        in_bubble_font_size = 19 * render_factor
        inBubbleFont = ImageFont.truetype(selected_font_path, in_bubble_font_size)
        bbox = inBubbleFont.getbbox(fileCounter)
        text_width = bbox[2] - bbox[0]
        right_aligned_position = 620 * render_factor
        x = right_aligned_position - text_width
        y = 447 * render_factor
        draw.text((x, y), fileCounter, font=inBubbleFont, fill=f"#{bubble_hex}")

    textAlignment = None
    individualItemHeight = round(
        (
            int(manager.deviceScreenHeightVar)
            - int(manager.approxFooterHeightVar)
            - int(manager.contentPaddingTopVar)
        )
        / int(manager.itemsPerScreenVar)
    )

    if muOSSystemName.startswith("mux"):
        textAlignment = manager.global_alignment_var
    else:
        textAlignment = manager.global_alignment_var

    try:
        font_size = int(manager.font_size_var) * render_factor
    except Exception as e:
        print(e)
        font_size = int(individualItemHeight * render_factor * textMF)

    font = ImageFont.truetype(selected_font_path, font_size)

    availableHeight = (
        (individualItemHeight * int(manager.itemsPerScreenVar)) * render_factor
    ) / ItemsPerScreen

    smallestValidText_bbox = font.getbbox("_...")
    smallestValidTest_width = smallestValidText_bbox[2] - smallestValidText_bbox[0]

    for index, item in enumerate(listItems):
        noLettersCut = 0
        text_width = float("inf")
        if manager.alternate_menu_names_var and muOSSystemName.startswith("mux"):
            text = bidi_get_display(menuNameMap.get(item[0][:].lower(), item[0][:]))
        else:
            text = item[0][:]
        text_color = (
            f"#{selected_font_hex}"
            if index == workingIndex
            else f"#{deselected_font_hex}"
        )
        maxBubbleLength = int(manager.deviceScreenWidthVar) - int(
            manager.maxBoxArtWidth
        )
        if (
            maxBubbleLength * render_factor
            < textPadding * render_factor
            + smallestValidTest_width
            + rectanglePadding * render_factor
            + 5 * render_factor
        ):  # Make sure there won't be a bubble error
            maxBubbleLength = int(manager.deviceScreenWidthVar)

        if workingIndex == index:
            totalCurrentLength = (
                textPadding * render_factor
                + text_width
                + rectanglePadding * render_factor
            )
        else:
            totalCurrentLength = textPadding * render_factor + text_width
        while totalCurrentLength > (int(maxBubbleLength) * render_factor):
            if manager.alternate_menu_names_var and muOSSystemName.startswith("mux"):
                text = bidi_get_display(menuNameMap.get(item[0][:].lower(), item[0][:]))
            else:
                text = item[0][:]
            if noLettersCut > 0:
                text = text[: -(noLettersCut + 3)]
                text = text + "..."

            text_bbox = font.getbbox(text)
            text_width = text_bbox[2] - text_bbox[0]
            if workingIndex == index:
                totalCurrentLength = (
                    textPadding * render_factor
                    + text_width
                    + rectanglePadding * render_factor
                )
            else:
                totalCurrentLength = textPadding * render_factor + text_width
            noLettersCut += 1
            if text == "...":
                raise ValueError(
                    "'Cut bubble off at' too low\n\nPlease use a different custom 'cut bubble off' at value"
                )

        if textAlignment == "Left":
            text_x = textPadding * render_factor
        elif textAlignment == "Right":
            text_x = (
                int(manager.deviceScreenWidthVar) - textPadding
            ) * render_factor - text_width
        elif textAlignment == "Centre":
            text_x = (
                int(manager.deviceScreenWidthVar) * render_factor - text_width
            ) / 2
        # text_y = contentPaddingTop * render_factor + availableHeight * index

        rectangle_x0 = text_x - (rectanglePadding * render_factor)
        rectangle_y0 = contentPaddingTop * render_factor + availableHeight * index
        rectangle_x1 = (
            rectangle_x0
            + rectanglePadding * render_factor
            + text_width
            + rectanglePadding * render_factor
        )
        rectangle_y1 = contentPaddingTop * render_factor + availableHeight * (index + 1)
        middle_y = (rectangle_y0 + rectangle_y1) / 2
        ascent, descent = font.getmetrics()
        text_height = ascent + descent

        # Calculate the text's y-position by centreing it vertically within the rectangle
        text_y = middle_y - (text_height / 2)

        corner_radius = availableHeight // 2

        if workingIndex == index:
            draw.rounded_rectangle(
                [(rectangle_x0, rectangle_y0), (rectangle_x1, rectangle_y1)],
                radius=corner_radius,
                fill=f"#{bubble_hex}",
            )
        draw.text((text_x, text_y), text, font=font, fill=text_color)

    if (
        muOSSystemName == "muxdevice"
        or muOSSystemName == "muxlaunch"
        or muOSSystemName == "muxconfig"
        or muOSSystemName == "muxinfo"
        or muOSSystemName == "muxapp"
        or muOSSystemName == "muxplore"
        or muOSSystemName == "muxfavourite"
        or muOSSystemName == "muxhistory"
    ):
        image = Image.alpha_composite(image, menuHelperGuides)

    headerBubbles = generateHeaderBubbles(manager, render_factor)
    image = Image.alpha_composite(image, headerBubbles)

    if forPreview:
        muOSOverlay = generatePilImageMuOSOverlay(
            manager, muOSSystemName, render_factor
        )
        image = Image.alpha_composite(image, muOSOverlay)
    return image


def ContinuousFolderImageGen(
    progress_bar,
    muOSSystemName,
    listItems,
    textPadding,
    rectanglePadding,
    ItemsPerScreen,
    bg_hex,
    selected_font_hex,
    deselected_font_hex,
    bubble_hex,
    render_factor,
    outputDir: Path,
    manager: Config,
    folderName=None,
    threadNumber=0,
):
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

            image = generatePilImageVertical(
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
                render_factor,
                manager,
                fileCounter=fileCounter,
                folderName=folderName,
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


def resize_system_logos(
    system_logos_path: Path,
    output_system_logos_path: Path,
    grid_cell_size,
    grid_image_padding,
    circular_grid,
):
    system_logos = system_logos_path.glob("*.png")
    if circular_grid:
        effective_circle_diameter = grid_cell_size - (grid_image_padding * 2)
    else:
        effective_grid_size = grid_cell_size - (grid_image_padding * 2)
    for system_logo_path in system_logos:
        system_logo_image = Image.open(system_logo_path).convert("RGBA")
        if circular_grid:
            old_size = system_logo_image.size
            aspect_ratio = old_size[0] / old_size[1]
            new_height = math.sqrt(
                math.pow(effective_circle_diameter, 2) / (1 + math.pow(aspect_ratio, 2))
            )
            new_size = int(new_height * aspect_ratio), int(new_height)
        else:
            width_multiplier = effective_grid_size / system_logo_image.size[0]
            height_multiplier = effective_grid_size / system_logo_image.size[1]
            multiplier = min(width_multiplier, height_multiplier)
            new_size = (
                int(system_logo_image.size[0] * multiplier),
                int(system_logo_image.size[1] * multiplier),
            )
        system_logo_image = system_logo_image.resize(new_size, Image.LANCZOS)
        system_logo_image.save(output_system_logos_path / system_logo_path.name)


def cut_out_image(original_image, logo_image, coordinates):
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


def getHorizontalLogoSize(path_to_logo: Path, render_factor, manager: Config):
    exploreLogoColoured = change_logo_color(path_to_logo, manager.iconHexVar)
    top_logo_size = (
        int(
            (
                exploreLogoColoured.size[0]
                * render_factor
                * min(
                    int(manager.deviceScreenHeightVar) / 480,
                    int(manager.deviceScreenWidthVar) / 640,
                )
            )
            / 5
        ),
        int(
            (
                exploreLogoColoured.size[1]
                * render_factor
                * min(
                    int(manager.deviceScreenHeightVar) / 480,
                    int(manager.deviceScreenWidthVar) / 640,
                )
            )
            / 5
        ),
    )
    return top_logo_size


def generatePilImageHorizontal(
    progress_bar,
    workingIndex,
    bg_hex,
    selected_font_hex,
    deselected_font_hex,
    bubble_hex,
    icon_hex,
    render_factor,
    manager: Config,
    transparent=False,
    forPreview=False,
    generateText=True,
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

    progress_bar["value"] += 1
    bg_rgb = hex_to_rgb(bg_hex)

    # Create image

    if not transparent:
        image = Image.new(
            "RGBA",
            (
                int(manager.deviceScreenWidthVar) * render_factor,
                int(manager.deviceScreenHeightVar) * render_factor,
            ),
            bg_rgb,
        )

        if background_image != None:
            image.paste(
                background_image.resize(
                    (
                        int(manager.deviceScreenWidthVar) * render_factor,
                        int(manager.deviceScreenHeightVar) * render_factor,
                    )
                ),
                (0, 0),
            )
    else:
        image = Image.new(
            "RGBA",
            (
                int(manager.deviceScreenWidthVar) * render_factor,
                int(manager.deviceScreenHeightVar) * render_factor,
            ),
            (0, 0, 0, 0),
        )

    exploreLogoColoured = change_logo_color(
        HORIZONTAL_LOGOS_DIR / "explore.png", icon_hex
    )
    favouriteLogoColoured = change_logo_color(
        HORIZONTAL_LOGOS_DIR / "favourite.png", icon_hex
    )
    historyLogoColoured = change_logo_color(
        HORIZONTAL_LOGOS_DIR / "history.png", icon_hex
    )
    appsLogoColoured = change_logo_color(HORIZONTAL_LOGOS_DIR / "apps.png", icon_hex)

    top_logo_size = getHorizontalLogoSize(
        HORIZONTAL_LOGOS_DIR / "explore.png", render_factor, manager
    )

    exploreLogoColoured = exploreLogoColoured.resize((top_logo_size), Image.LANCZOS)
    favouriteLogoColoured = favouriteLogoColoured.resize((top_logo_size), Image.LANCZOS)
    historyLogoColoured = historyLogoColoured.resize((top_logo_size), Image.LANCZOS)
    appsLogoColoured = appsLogoColoured.resize((top_logo_size), Image.LANCZOS)

    combined_top_logos_width = (
        exploreLogoColoured.size[0]
        + favouriteLogoColoured.size[0]
        + historyLogoColoured.size[0]
        + appsLogoColoured.size[0]
    )

    icons_to_bubble_padding = (
        min(
            (int(manager.deviceScreenHeightVar) * 0) / 480,
            (int(manager.deviceScreenWidthVar) * 0) / 640,
        )
        * render_factor
    )  ## CHANGE for adjustment

    bubble_height = (
        min(
            (int(manager.deviceScreenHeightVar) * 36.3) / 480,
            (int(manager.deviceScreenWidthVar) * 36.3) / 640,
        )
        * render_factor
    )  ## CHANGE for adjustment

    screen_y_middle = (int(manager.deviceScreenHeightVar) * render_factor) / 2

    combined_top_row_height = (
        max(
            exploreLogoColoured.size[1],
            favouriteLogoColoured.size[1],
            historyLogoColoured.size[1],
            appsLogoColoured.size[1],
        )
        + icons_to_bubble_padding
        + bubble_height
    )

    top_row_icon_y = int(screen_y_middle - (combined_top_row_height / 2))

    top_row_bubble_middle = int(
        screen_y_middle + (combined_top_row_height / 2) - (bubble_height) / 2
    )

    padding_between_top_logos = (
        int(manager.deviceScreenWidthVar) * render_factor - combined_top_logos_width
    ) / (4 + 1)  # 4 logos plus 1

    explore_middle = int(padding_between_top_logos + (exploreLogoColoured.size[0]) / 2)
    favourite_middle = int(
        padding_between_top_logos
        + favouriteLogoColoured.size[0]
        + padding_between_top_logos
        + (favouriteLogoColoured.size[0]) / 2
    )
    history_middle = int(
        padding_between_top_logos
        + historyLogoColoured.size[0]
        + padding_between_top_logos
        + favouriteLogoColoured.size[0]
        + padding_between_top_logos
        + (historyLogoColoured.size[0]) / 2
    )
    apps_middle = int(
        padding_between_top_logos
        + appsLogoColoured.size[0]
        + padding_between_top_logos
        + favouriteLogoColoured.size[0]
        + padding_between_top_logos
        + historyLogoColoured.size[0]
        + padding_between_top_logos
        + (appsLogoColoured.size[0]) / 2
    )

    explore_logo_x = int(explore_middle - (exploreLogoColoured.size[0]) / 2)
    favourite_logo_x = int(favourite_middle - (favouriteLogoColoured.size[0]) / 2)
    history_logo_x = int(history_middle - (historyLogoColoured.size[0]) / 2)
    apps_logo_x = int(apps_middle - (appsLogoColoured.size[0]) / 2)

    image.paste(
        exploreLogoColoured, (explore_logo_x, top_row_icon_y), exploreLogoColoured
    )
    image.paste(
        favouriteLogoColoured, (favourite_logo_x, top_row_icon_y), favouriteLogoColoured
    )
    image.paste(
        historyLogoColoured, (history_logo_x, top_row_icon_y), historyLogoColoured
    )
    image.paste(appsLogoColoured, (apps_logo_x, top_row_icon_y), appsLogoColoured)

    draw = ImageDraw.Draw(image)
    if manager.transparent_text_var:
        transparent_text_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw_transparent = ImageDraw.Draw(transparent_text_image)
        transparency = 0

    selected_font_path = get_font_path(
        manager.use_alt_font_var, manager.alt_font_filename
    )

    menuHelperGuides = generateMenuHelperGuides(
        [["A", "SELECT"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
        lhsButtons=[["POWER", "SLEEP"]],
    )

    font_size = (
        min(
            (int(manager.deviceScreenHeightVar) * 24) / 480,
            (int(manager.deviceScreenWidthVar) * 24) / 640,
        )
        * render_factor
    )  ## CHANGE for adjustment
    font = ImageFont.truetype(selected_font_path, font_size)
    if workingIndex == 0:
        current_x_midpoint = explore_middle
    elif workingIndex == 1:
        current_x_midpoint = favourite_middle
    elif workingIndex == 2:
        current_x_midpoint = history_middle
    elif workingIndex == 3:
        current_x_midpoint = apps_middle
    else:
        current_x_midpoint = 104 + (144 * workingIndex)
    betweenBubblePadding = 5 * render_factor
    maxBubbleLength = int(
        (
            (
                (int(manager.deviceScreenWidthVar) * render_factor)
                - padding_between_top_logos
            )
            / 4
        )
        - betweenBubblePadding / 2
    )

    horizontalBubblePadding = (
        min(
            (int(manager.deviceScreenHeightVar) * 40) / 480,
            (int(manager.deviceScreenWidthVar) * 40) / 640,
        )
        * render_factor
    )  ## CHANGE for adjustment

    if manager.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("content explorer", "Content"))
    else:
        textString = "Content"
    text_bbox = font.getbbox(textString)
    text_width = text_bbox[2] - text_bbox[0]
    ascent, descent = font.getmetrics()
    text_height = ascent + descent

    text_y = top_row_bubble_middle - (text_height / 2)

    bubble_centre_x = explore_middle
    textColour = selected_font_hex if workingIndex == 0 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 0:
        if generateText:
            bubbleLength = text_width + horizontalBubblePadding
        else:
            bubbleLength = maxBubbleLength
        if manager.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int(top_row_bubble_middle - bubble_height / 2),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int(top_row_bubble_middle + bubble_height / 2),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int(top_row_bubble_middle - bubble_height / 2),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int(top_row_bubble_middle + bubble_height / 2),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
    if generateText:
        if manager.transparent_text_var and workingIndex == 0:
            draw_transparent.text(
                (text_x, text_y),
                textString,
                font=font,
                fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency),
            )
        else:
            draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    if manager.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("favourites", "Favourites"))
    else:
        textString = "Favourites"
    text_bbox = font.getbbox(textString)
    text_width = text_bbox[2] - text_bbox[0]
    bubble_centre_x = favourite_middle
    textColour = selected_font_hex if workingIndex == 1 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 1:
        if generateText:
            bubbleLength = text_width + horizontalBubblePadding
        else:
            bubbleLength = maxBubbleLength
        if manager.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int(top_row_bubble_middle - bubble_height / 2),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int(top_row_bubble_middle + bubble_height / 2),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int(top_row_bubble_middle - bubble_height / 2),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int(top_row_bubble_middle + bubble_height / 2),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
    if generateText:
        if manager.transparent_text_var and workingIndex == 1:
            draw_transparent.text(
                (text_x, text_y),
                textString,
                font=font,
                fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency),
            )
        else:
            draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    if manager.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("history", "History"))
    else:
        textString = "History"
    text_bbox = font.getbbox(textString)
    text_width = text_bbox[2] - text_bbox[0]
    bubble_centre_x = history_middle
    textColour = selected_font_hex if workingIndex == 2 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 2:
        if generateText:
            bubbleLength = text_width + horizontalBubblePadding
        else:
            bubbleLength = maxBubbleLength
        if manager.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int((top_row_bubble_middle - bubble_height / 2)),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int((top_row_bubble_middle + bubble_height / 2)),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int((top_row_bubble_middle - bubble_height / 2)),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int((top_row_bubble_middle + bubble_height / 2)),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
    if generateText:
        if manager.transparent_text_var and workingIndex == 2:
            draw_transparent.text(
                (text_x, text_y),
                textString,
                font=font,
                fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency),
            )
        else:
            draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")
    if manager.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("applications", "Utilities"))
    else:
        textString = "Utilities"
    text_bbox = font.getbbox(textString)
    text_width = text_bbox[2] - text_bbox[0]
    bubble_centre_x = apps_middle
    textColour = selected_font_hex if workingIndex == 3 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 3:
        if generateText:
            bubbleLength = text_width + horizontalBubblePadding
        else:
            bubbleLength = maxBubbleLength
        if manager.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int((top_row_bubble_middle - bubble_height / 2)),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int((top_row_bubble_middle + bubble_height / 2)),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int((top_row_bubble_middle - bubble_height / 2)),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int((top_row_bubble_middle + bubble_height / 2)),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
    if generateText:
        if manager.transparent_text_var and workingIndex == 3:
            draw_transparent.text(
                (text_x, text_y),
                textString,
                font=font,
                fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency),
            )
        else:
            draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    if workingIndex == 4:
        infoLogoColoured = change_logo_color(
            HORIZONTAL_LOGOS_DIR / "info.png", selected_font_hex
        )
    else:
        infoLogoColoured = change_logo_color(
            HORIZONTAL_LOGOS_DIR / "info.png", deselected_font_hex
        )
    if workingIndex == 5:
        configLogoColoured = change_logo_color(
            HORIZONTAL_LOGOS_DIR / "config.png", selected_font_hex
        )
    else:
        configLogoColoured = change_logo_color(
            HORIZONTAL_LOGOS_DIR / "config.png", deselected_font_hex
        )
    if workingIndex == 6:
        rebootLogoColoured = change_logo_color(
            HORIZONTAL_LOGOS_DIR / "reboot.png", selected_font_hex
        )
    else:
        rebootLogoColoured = change_logo_color(
            HORIZONTAL_LOGOS_DIR / "reboot.png", deselected_font_hex
        )
    if workingIndex == 7:
        shutdownLogoColoured = change_logo_color(
            HORIZONTAL_LOGOS_DIR / "shutdown.png", selected_font_hex
        )
    else:
        shutdownLogoColoured = change_logo_color(
            HORIZONTAL_LOGOS_DIR / "shutdown.png", deselected_font_hex
        )

    bottom_logo_size = (
        int(
            (
                infoLogoColoured.size[0]
                * render_factor
                * min(
                    int(manager.deviceScreenHeightVar) / 480,
                    int(manager.deviceScreenWidthVar) / 640,
                )
            )
            / 5
        ),
        int(
            (
                infoLogoColoured.size[1]
                * render_factor
                * min(
                    int(manager.deviceScreenHeightVar) / 480,
                    int(manager.deviceScreenWidthVar) / 640,
                )
            )
            / 5
        ),
    )

    infoLogoColoured = infoLogoColoured.resize(bottom_logo_size, Image.LANCZOS)
    configLogoColoured = configLogoColoured.resize(bottom_logo_size, Image.LANCZOS)
    rebootLogoColoured = rebootLogoColoured.resize(bottom_logo_size, Image.LANCZOS)
    shutdownLogoColoured = shutdownLogoColoured.resize(bottom_logo_size, Image.LANCZOS)

    combined_bottom_logos_width = (
        infoLogoColoured.size[0]
        + configLogoColoured.size[0]
        + rebootLogoColoured.size[0]
        + shutdownLogoColoured.size[0]
    )

    circle_padding = (
        min(
            (int(manager.deviceScreenHeightVar) * 15) / 480,
            (int(manager.deviceScreenWidthVar) * 15) / 640,
        )
        * render_factor
    )  ## CHANGE to adjust

    combined_bottom_row_height = (
        max(
            infoLogoColoured.size[1],
            configLogoColoured.size[1],
            rebootLogoColoured.size[1],
            shutdownLogoColoured.size[1],
        )
        + circle_padding * 2
    )

    circle_radius = combined_bottom_row_height / 2

    top_row_to_bottom_row_padding = (
        min(
            (int(manager.deviceScreenHeightVar) * 20) / 480,
            (int(manager.deviceScreenWidthVar) * 20) / 640,
        )
        * render_factor
    )  ## CHANGE to adjust

    bottom_row_middle_y = int(
        screen_y_middle
        + (combined_top_row_height / 2)
        + top_row_to_bottom_row_padding
        + circle_radius
    )

    padding_from_screen_bottom_logos = (
        int(manager.deviceScreenWidthVar) * (175 / 640) * render_factor
    )  ##CHANGE to adjust

    padding_between_bottom_logos = (
        int(manager.deviceScreenWidthVar) * render_factor
        - padding_from_screen_bottom_logos
        - combined_bottom_logos_width
        - padding_from_screen_bottom_logos
    ) / (4 - 1)  # 4 logos minus 1

    info_middle = int(padding_from_screen_bottom_logos + (infoLogoColoured.size[0]) / 2)
    config_middle = int(
        info_middle
        + (infoLogoColoured.size[0]) / 2
        + padding_between_bottom_logos
        + (configLogoColoured.size[0]) / 2
    )
    reboot_middle = int(
        config_middle
        + (configLogoColoured.size[0]) / 2
        + padding_between_bottom_logos
        + (rebootLogoColoured.size[0]) / 2
    )
    shutdown_middle = int(
        reboot_middle
        + (rebootLogoColoured.size[0]) / 2
        + padding_between_bottom_logos
        + (shutdownLogoColoured.size[0]) / 2
    )

    info_logo_x = int(info_middle - (infoLogoColoured.size[0]) / 2)
    config_logo_x = int(config_middle - (configLogoColoured.size[0]) / 2)
    reboot_logo_x = int(reboot_middle - (rebootLogoColoured.size[0]) / 2)
    shutdown_logo_x = int(shutdown_middle - (shutdownLogoColoured.size[0]) / 2)

    if workingIndex == 4:
        centre_x = info_middle
        if manager.transparent_text_var:
            draw_transparent.ellipse(
                (
                    int(centre_x - circle_radius),
                    int(bottom_row_middle_y - circle_radius),
                    int(centre_x + circle_radius),
                    int(bottom_row_middle_y + circle_radius),
                ),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.ellipse(
                (
                    int(centre_x - circle_radius),
                    int(bottom_row_middle_y - circle_radius),
                    int(centre_x + circle_radius),
                    int(bottom_row_middle_y + circle_radius),
                ),
                fill=f"#{bubble_hex}",
            )
    elif workingIndex == 5:
        centre_x = config_middle
        if manager.transparent_text_var:
            draw_transparent.ellipse(
                (
                    int(centre_x - circle_radius),
                    int(bottom_row_middle_y - circle_radius),
                    int(centre_x + circle_radius),
                    int(bottom_row_middle_y + circle_radius),
                ),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.ellipse(
                (
                    int(centre_x - circle_radius),
                    int(bottom_row_middle_y - circle_radius),
                    int(centre_x + circle_radius),
                    int(bottom_row_middle_y + circle_radius),
                ),
                fill=f"#{bubble_hex}",
            )
    elif workingIndex == 6:
        centre_x = reboot_middle
        if manager.transparent_text_var:
            draw_transparent.ellipse(
                (
                    int(centre_x - circle_radius),
                    int(bottom_row_middle_y - circle_radius),
                    int(centre_x + circle_radius),
                    int(bottom_row_middle_y + circle_radius),
                ),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.ellipse(
                (
                    int(centre_x - circle_radius),
                    int(bottom_row_middle_y - circle_radius),
                    int(centre_x + circle_radius),
                    int(bottom_row_middle_y + circle_radius),
                ),
                fill=f"#{bubble_hex}",
            )
    elif workingIndex == 7:
        centre_x = shutdown_middle
        if manager.transparent_text_var:
            draw_transparent.ellipse(
                (
                    int(centre_x - circle_radius),
                    int(bottom_row_middle_y - circle_radius),
                    int(centre_x + circle_radius),
                    int(bottom_row_middle_y + circle_radius),
                ),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.ellipse(
                (
                    int(centre_x - circle_radius),
                    int(bottom_row_middle_y - circle_radius),
                    int(centre_x + circle_radius),
                    int(bottom_row_middle_y + circle_radius),
                ),
                fill=f"#{bubble_hex}",
            )

    info_logo_y = int(bottom_row_middle_y - (infoLogoColoured.size[1] / 2))
    config_logo_y = int(bottom_row_middle_y - (configLogoColoured.size[1] / 2))
    reboot_logo_y = int(bottom_row_middle_y - (rebootLogoColoured.size[1] / 2))
    shutdown_logo_y = int(bottom_row_middle_y - (shutdownLogoColoured.size[1] / 2))
    if manager.transparent_text_var and workingIndex > 3:
        if workingIndex == 4:
            transparent_text_image = cut_out_image(
                transparent_text_image, infoLogoColoured, (info_logo_x, info_logo_y)
            )
            image.paste(
                configLogoColoured, (config_logo_x, config_logo_y), configLogoColoured
            )
            image.paste(
                rebootLogoColoured, (reboot_logo_x, reboot_logo_y), rebootLogoColoured
            )
            image.paste(
                shutdownLogoColoured,
                (shutdown_logo_x, shutdown_logo_y),
                shutdownLogoColoured,
            )
        elif workingIndex == 5:
            image.paste(infoLogoColoured, (info_logo_x, info_logo_y), infoLogoColoured)
            transparent_text_image = cut_out_image(
                transparent_text_image,
                configLogoColoured,
                (config_logo_x, config_logo_y),
            )
            image.paste(
                rebootLogoColoured, (reboot_logo_x, reboot_logo_y), rebootLogoColoured
            )
            image.paste(
                shutdownLogoColoured,
                (shutdown_logo_x, shutdown_logo_y),
                shutdownLogoColoured,
            )
        elif workingIndex == 6:
            image.paste(infoLogoColoured, (info_logo_x, info_logo_y), infoLogoColoured)
            image.paste(
                configLogoColoured, (config_logo_x, config_logo_y), configLogoColoured
            )
            transparent_text_image = cut_out_image(
                transparent_text_image,
                rebootLogoColoured,
                (reboot_logo_x, reboot_logo_y),
            )
            image.paste(
                shutdownLogoColoured,
                (shutdown_logo_x, shutdown_logo_y),
                shutdownLogoColoured,
            )
        elif workingIndex == 7:
            image.paste(infoLogoColoured, (info_logo_x, info_logo_y), infoLogoColoured)
            image.paste(
                configLogoColoured, (config_logo_x, config_logo_y), configLogoColoured
            )
            image.paste(
                rebootLogoColoured, (reboot_logo_x, reboot_logo_y), rebootLogoColoured
            )
            transparent_text_image = cut_out_image(
                transparent_text_image,
                shutdownLogoColoured,
                (shutdown_logo_x, shutdown_logo_y),
            )

    else:
        image.paste(infoLogoColoured, (info_logo_x, info_logo_y), infoLogoColoured)
        image.paste(
            configLogoColoured, (config_logo_x, config_logo_y), configLogoColoured
        )
        image.paste(
            rebootLogoColoured, (reboot_logo_x, reboot_logo_y), rebootLogoColoured
        )
        image.paste(
            shutdownLogoColoured,
            (shutdown_logo_x, shutdown_logo_y),
            shutdownLogoColoured,
        )

    if manager.transparent_text_var:
        image = Image.alpha_composite(image, transparent_text_image)
    image = Image.alpha_composite(image, menuHelperGuides)

    ## Show what header items will actually look like

    headerBubbles = generateHeaderBubbles(manager, render_factor)
    image = Image.alpha_composite(image, headerBubbles)

    if forPreview:
        muOSOverlay = generatePilImageMuOSOverlay(manager, "muxlaunch", render_factor)
        image = Image.alpha_composite(image, muOSOverlay)
    return image


def generatePilImageAltHorizontal(
    progress_bar,
    workingIndex,
    bg_hex,
    selected_font_hex,
    deselected_font_hex,
    bubble_hex,
    icon_hex,
    render_factor,
    manager: Config,
    transparent=False,
    forPreview=False,
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

    progress_bar["value"] += 1
    bg_rgb = hex_to_rgb(bg_hex)

    # Create image

    if not transparent:
        image = Image.new(
            "RGBA",
            (
                int(manager.deviceScreenWidthVar) * render_factor,
                int(manager.deviceScreenHeightVar) * render_factor,
            ),
            bg_rgb,
        )

        if background_image != None:
            image.paste(
                background_image.resize(
                    (
                        int(manager.deviceScreenWidthVar) * render_factor,
                        int(manager.deviceScreenHeightVar) * render_factor,
                    )
                ),
                (0, 0),
            )
    else:
        image = Image.new(
            "RGBA",
            (
                int(manager.deviceScreenWidthVar) * render_factor,
                int(manager.deviceScreenHeightVar) * render_factor,
            ),
            (0, 0, 0, 0),
        )

    top_to_bottom_row_padding = (
        min(
            (int(manager.deviceScreenHeightVar) * 30) / 480,
            (int(manager.deviceScreenWidthVar) * 30) / 640,
        )
        * render_factor
    )  ## CHANGE for adjustment

    exploreLogoColoured = change_logo_color(
        HORIZONTAL_LOGOS_DIR / "explore.png", icon_hex
    )
    favouriteLogoColoured = change_logo_color(
        HORIZONTAL_LOGOS_DIR / "favourite.png", icon_hex
    )
    historyLogoColoured = change_logo_color(
        HORIZONTAL_LOGOS_DIR / "history.png", icon_hex
    )
    appsLogoColoured = change_logo_color(HORIZONTAL_LOGOS_DIR / "apps.png", icon_hex)

    top_logo_size = (
        int(
            (
                exploreLogoColoured.size[0]
                * render_factor
                * min(
                    int(manager.deviceScreenHeightVar) / 480,
                    int(manager.deviceScreenWidthVar) / 640,
                )
            )
            / 5
        ),
        int(
            (
                exploreLogoColoured.size[1]
                * render_factor
                * min(
                    int(manager.deviceScreenHeightVar) / 480,
                    int(manager.deviceScreenWidthVar) / 640,
                )
            )
            / 5
        ),
    )

    exploreLogoColoured = exploreLogoColoured.resize((top_logo_size), Image.LANCZOS)
    favouriteLogoColoured = favouriteLogoColoured.resize((top_logo_size), Image.LANCZOS)
    historyLogoColoured = historyLogoColoured.resize((top_logo_size), Image.LANCZOS)
    appsLogoColoured = appsLogoColoured.resize((top_logo_size), Image.LANCZOS)

    combined_top_logos_width = (
        exploreLogoColoured.size[0]
        + favouriteLogoColoured.size[0]
        + historyLogoColoured.size[0]
        + appsLogoColoured.size[0]
    )

    icons_to_bubble_padding = (
        min(
            (int(manager.deviceScreenHeightVar) * 0) / 480,
            (int(manager.deviceScreenWidthVar) * 0) / 640,
        )
        * render_factor
    )  ## CHANGE for adjustment

    bubble_height = (
        min(
            (int(manager.deviceScreenHeightVar) * 36.3) / 480,
            (int(manager.deviceScreenWidthVar) * 36.3) / 640,
        )
        * render_factor
    )  ## CHANGE for adjustment

    screen_y_middle = (int(manager.deviceScreenHeightVar) * render_factor) / 2

    combined_top_row_height = (
        max(
            exploreLogoColoured.size[1],
            favouriteLogoColoured.size[1],
            historyLogoColoured.size[1],
            appsLogoColoured.size[1],
        )
        + icons_to_bubble_padding
        + bubble_height
    )

    top_row_icon_y = int(
        screen_y_middle - combined_top_row_height - (top_to_bottom_row_padding / 2)
    )

    top_row_bubble_middle = int(
        screen_y_middle - (bubble_height) / 2 - (top_to_bottom_row_padding / 2)
    )

    padding_between_top_logos = (
        int(manager.deviceScreenWidthVar) * render_factor - combined_top_logos_width
    ) / (4 + 1)  # 4 logos plus 1

    explore_middle_x = int(
        padding_between_top_logos + (exploreLogoColoured.size[0]) / 2
    )
    favourite_middle_x = int(
        padding_between_top_logos
        + favouriteLogoColoured.size[0]
        + padding_between_top_logos
        + (favouriteLogoColoured.size[0]) / 2
    )
    history_middle_x = int(
        padding_between_top_logos
        + historyLogoColoured.size[0]
        + padding_between_top_logos
        + favouriteLogoColoured.size[0]
        + padding_between_top_logos
        + (historyLogoColoured.size[0]) / 2
    )
    apps_middle_x = int(
        padding_between_top_logos
        + appsLogoColoured.size[0]
        + padding_between_top_logos
        + favouriteLogoColoured.size[0]
        + padding_between_top_logos
        + historyLogoColoured.size[0]
        + padding_between_top_logos
        + (appsLogoColoured.size[0]) / 2
    )

    explore_logo_x = int(explore_middle_x - (exploreLogoColoured.size[0]) / 2)
    favourite_logo_x = int(favourite_middle_x - (favouriteLogoColoured.size[0]) / 2)
    history_logo_x = int(history_middle_x - (historyLogoColoured.size[0]) / 2)
    apps_logo_x = int(apps_middle_x - (appsLogoColoured.size[0]) / 2)

    image.paste(
        exploreLogoColoured, (explore_logo_x, top_row_icon_y), exploreLogoColoured
    )
    image.paste(
        favouriteLogoColoured, (favourite_logo_x, top_row_icon_y), favouriteLogoColoured
    )
    image.paste(
        historyLogoColoured, (history_logo_x, top_row_icon_y), historyLogoColoured
    )
    image.paste(appsLogoColoured, (apps_logo_x, top_row_icon_y), appsLogoColoured)

    draw = ImageDraw.Draw(image)
    if manager.transparent_text_var:
        transparent_text_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw_transparent = ImageDraw.Draw(transparent_text_image)
        transparency = 0

    selected_font_path = get_font_path(
        manager.use_alt_font_var, manager.alt_font_filename
    )

    menuHelperGuides = generateMenuHelperGuides(
        [["A", "SELECT"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
        lhsButtons=[["POWER", "SLEEP"]],
    )

    font_size = (
        min(
            (int(manager.deviceScreenHeightVar) * 24) / 480,
            (int(manager.deviceScreenWidthVar) * 24) / 640,
        )
        * render_factor
    )  ## CHANGE for adjustment
    font = ImageFont.truetype(selected_font_path, font_size)
    if workingIndex == 0:
        current_x_midpoint = explore_middle_x
    elif workingIndex == 1:
        current_x_midpoint = favourite_middle_x
    elif workingIndex == 2:
        current_x_midpoint = history_middle_x
    elif workingIndex == 3:
        current_x_midpoint = apps_middle_x
    else:
        current_x_midpoint = 104 + (144 * workingIndex)

    horizontalBubblePadding = (
        min(
            (int(manager.deviceScreenHeightVar) * 40) / 480,
            (int(manager.deviceScreenWidthVar) * 40) / 640,
        )
        * render_factor
    )  ## CHANGE for adjustment

    if manager.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("content explorer", "Content"))
    else:
        textString = "Content"
    text_bbox = font.getbbox(textString)
    text_width = text_bbox[2] - text_bbox[0]
    ascent, descent = font.getmetrics()
    text_height = ascent + descent

    text_y = top_row_bubble_middle - (text_height / 2)

    bubble_centre_x = explore_middle_x
    textColour = selected_font_hex if workingIndex == 0 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 0:
        bubbleLength = text_width + horizontalBubblePadding
        if manager.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int(top_row_bubble_middle - bubble_height / 2),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int(top_row_bubble_middle + bubble_height / 2),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int(top_row_bubble_middle - bubble_height / 2),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int(top_row_bubble_middle + bubble_height / 2),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
    if manager.transparent_text_var and workingIndex == 0:
        draw_transparent.text(
            (text_x, text_y),
            textString,
            font=font,
            fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency),
        )
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    if manager.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("favourites", "Favourites"))
    else:
        textString = "Favourites"
    text_bbox = font.getbbox(textString)
    text_width = text_bbox[2] - text_bbox[0]
    bubble_centre_x = favourite_middle_x
    textColour = selected_font_hex if workingIndex == 1 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 1:
        bubbleLength = text_width + horizontalBubblePadding
        if manager.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int(top_row_bubble_middle - bubble_height / 2),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int(top_row_bubble_middle + bubble_height / 2),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int(top_row_bubble_middle - bubble_height / 2),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int(top_row_bubble_middle + bubble_height / 2),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
    if manager.transparent_text_var and workingIndex == 1:
        draw_transparent.text(
            (text_x, text_y),
            textString,
            font=font,
            fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency),
        )
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    if manager.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("history", "History"))
    else:
        textString = "History"
    text_bbox = font.getbbox(textString)
    text_width = text_bbox[2] - text_bbox[0]
    bubble_centre_x = history_middle_x
    textColour = selected_font_hex if workingIndex == 2 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 2:
        bubbleLength = text_width + horizontalBubblePadding
        if manager.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int((top_row_bubble_middle - bubble_height / 2)),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int((top_row_bubble_middle + bubble_height / 2)),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int((top_row_bubble_middle - bubble_height / 2)),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int((top_row_bubble_middle + bubble_height / 2)),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
    if manager.transparent_text_var and workingIndex == 2:
        draw_transparent.text(
            (text_x, text_y),
            textString,
            font=font,
            fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency),
        )
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")
    if manager.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("applications", "Utilities"))
    else:
        textString = "Utilities"
    text_bbox = font.getbbox(textString)
    text_width = text_bbox[2] - text_bbox[0]
    bubble_centre_x = apps_middle_x
    textColour = selected_font_hex if workingIndex == 3 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 3:
        bubbleLength = text_width + horizontalBubblePadding
        if manager.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int((top_row_bubble_middle - bubble_height / 2)),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int((top_row_bubble_middle + bubble_height / 2)),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int((top_row_bubble_middle - bubble_height / 2)),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int((top_row_bubble_middle + bubble_height / 2)),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
    if manager.transparent_text_var and workingIndex == 3:
        draw_transparent.text(
            (text_x, text_y),
            textString,
            font=font,
            fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency),
        )
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    infoLogoColoured = change_logo_color(
        HORIZONTAL_LOGOS_DIR / "alt-info.png", icon_hex
    )
    configLogoColoured = change_logo_color(
        HORIZONTAL_LOGOS_DIR / "alt-config.png", icon_hex
    )
    rebootLogoColoured = change_logo_color(
        HORIZONTAL_LOGOS_DIR / "alt-reboot.png", icon_hex
    )
    shutdownLogoColoured = change_logo_color(
        HORIZONTAL_LOGOS_DIR / "alt-shutdown.png", icon_hex
    )

    bottom_logo_size = (
        int(
            (
                infoLogoColoured.size[0]
                * render_factor
                * min(
                    int(manager.deviceScreenHeightVar) / 480,
                    int(manager.deviceScreenWidthVar) / 640,
                )
            )
            / 5
        ),
        int(
            (
                infoLogoColoured.size[1]
                * render_factor
                * min(
                    int(manager.deviceScreenHeightVar) / 480,
                    int(manager.deviceScreenWidthVar) / 640,
                )
            )
            / 5
        ),
    )

    infoLogoColoured = infoLogoColoured.resize((bottom_logo_size), Image.LANCZOS)
    configLogoColoured = configLogoColoured.resize((bottom_logo_size), Image.LANCZOS)
    rebootLogoColoured = rebootLogoColoured.resize((bottom_logo_size), Image.LANCZOS)
    shutdownLogoColoured = shutdownLogoColoured.resize(
        (bottom_logo_size), Image.LANCZOS
    )

    combined_bottom_logos_width = (
        infoLogoColoured.size[0]
        + configLogoColoured.size[0]
        + rebootLogoColoured.size[0]
        + shutdownLogoColoured.size[0]
    )

    combined_bottom_row_height = (
        max(
            infoLogoColoured.size[1],
            configLogoColoured.size[1],
            rebootLogoColoured.size[1],
            shutdownLogoColoured.size[1],
        )
        + icons_to_bubble_padding
        + bubble_height
    )

    bottom_row_icon_y = int(screen_y_middle + (top_to_bottom_row_padding / 2))

    bottom_row_bubble_middle = int(
        screen_y_middle
        + (combined_bottom_row_height)
        - (bubble_height) / 2
        + (top_to_bottom_row_padding / 2)
    )

    padding_between_bottom_logos = (
        int(manager.deviceScreenWidthVar) * render_factor - combined_bottom_logos_width
    ) / (4 + 1)  # 4 logos plus 1

    info_middle_x = int(padding_between_bottom_logos + (infoLogoColoured.size[0]) / 2)
    config_middle_x = int(
        info_middle_x
        + (infoLogoColoured.size[0]) / 2
        + padding_between_bottom_logos
        + (configLogoColoured.size[0]) / 2
    )
    reboot_middle_x = int(
        config_middle_x
        + (configLogoColoured.size[0]) / 2
        + padding_between_bottom_logos
        + (rebootLogoColoured.size[0]) / 2
    )
    shutdown_middle_x = int(
        reboot_middle_x
        + (rebootLogoColoured.size[0]) / 2
        + padding_between_bottom_logos
        + (shutdownLogoColoured.size[0]) / 2
    )

    info_logo_x = int(info_middle_x - (infoLogoColoured.size[0]) / 2)
    config_logo_x = int(config_middle_x - (configLogoColoured.size[0]) / 2)
    reboot_logo_x = int(reboot_middle_x - (rebootLogoColoured.size[0]) / 2)
    shutdown_logo_x = int(shutdown_middle_x - (shutdownLogoColoured.size[0]) / 2)

    image.paste(infoLogoColoured, (info_logo_x, bottom_row_icon_y), infoLogoColoured)
    image.paste(
        configLogoColoured, (config_logo_x, bottom_row_icon_y), configLogoColoured
    )
    image.paste(
        rebootLogoColoured, (reboot_logo_x, bottom_row_icon_y), rebootLogoColoured
    )
    image.paste(
        shutdownLogoColoured, (shutdown_logo_x, bottom_row_icon_y), shutdownLogoColoured
    )

    if workingIndex == 4:
        current_x_midpoint = info_middle_x
    elif workingIndex == 5:
        current_x_midpoint = config_middle_x
    elif workingIndex == 6:
        current_x_midpoint = reboot_middle_x
    elif workingIndex == 7:
        current_x_midpoint = shutdown_middle_x
    else:
        current_x_midpoint = 104 + (144 * workingIndex)

    if manager.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("information", "Info"))
    else:
        textString = "Info"
    text_bbox = font.getbbox(textString)
    text_width = text_bbox[2] - text_bbox[0]
    ascent, descent = font.getmetrics()
    text_height = ascent + descent

    text_y = bottom_row_bubble_middle - (text_height / 2)

    bubble_centre_x = info_middle_x
    textColour = selected_font_hex if workingIndex == 4 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 4:
        bubbleLength = text_width + horizontalBubblePadding
        if manager.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int(bottom_row_bubble_middle - bubble_height / 2),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int(bottom_row_bubble_middle + bubble_height / 2),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int(bottom_row_bubble_middle - bubble_height / 2),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int(bottom_row_bubble_middle + bubble_height / 2),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
    if manager.transparent_text_var and workingIndex == 4:
        draw_transparent.text(
            (text_x, text_y),
            textString,
            font=font,
            fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency),
        )
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    if manager.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("configuration", "Config"))
    else:
        textString = "Config"
    text_bbox = font.getbbox(textString)
    text_width = text_bbox[2] - text_bbox[0]
    bubble_centre_x = config_middle_x
    textColour = selected_font_hex if workingIndex == 5 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 5:
        bubbleLength = text_width + horizontalBubblePadding
        if manager.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int(bottom_row_bubble_middle - bubble_height / 2),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int(bottom_row_bubble_middle + bubble_height / 2),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int(bottom_row_bubble_middle - bubble_height / 2),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int(bottom_row_bubble_middle + bubble_height / 2),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
    if manager.transparent_text_var and workingIndex == 5:
        draw_transparent.text(
            (text_x, text_y),
            textString,
            font=font,
            fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency),
        )
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    if manager.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("reboot device", "Reboot"))
    else:
        textString = "Reboot"
    text_bbox = font.getbbox(textString)
    text_width = text_bbox[2] - text_bbox[0]
    bubble_centre_x = reboot_middle_x
    textColour = selected_font_hex if workingIndex == 6 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 6:
        bubbleLength = text_width + horizontalBubblePadding
        if manager.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int((bottom_row_bubble_middle - bubble_height / 2)),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int((bottom_row_bubble_middle + bubble_height / 2)),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int((bottom_row_bubble_middle - bubble_height / 2)),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int((bottom_row_bubble_middle + bubble_height / 2)),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
    if manager.transparent_text_var and workingIndex == 6:
        draw_transparent.text(
            (text_x, text_y),
            textString,
            font=font,
            fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency),
        )
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    if manager.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("shutdown device", "Shutdown"))
    else:
        textString = "Shutdown"
    text_bbox = font.getbbox(textString)
    text_width = text_bbox[2] - text_bbox[0]
    bubble_centre_x = shutdown_middle_x
    textColour = selected_font_hex if workingIndex == 7 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 7:
        bubbleLength = text_width + horizontalBubblePadding
        if manager.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int((bottom_row_bubble_middle - bubble_height / 2)),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int((bottom_row_bubble_middle + bubble_height / 2)),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
        else:
            draw.rounded_rectangle(
                [
                    (
                        (current_x_midpoint - (bubbleLength / 2)),
                        int((bottom_row_bubble_middle - bubble_height / 2)),
                    ),
                    (
                        (current_x_midpoint + (bubbleLength / 2)),
                        int((bottom_row_bubble_middle + bubble_height / 2)),
                    ),
                ],
                radius=(bubble_height / 2),
                fill=f"#{bubble_hex}",
            )
    if manager.transparent_text_var and workingIndex == 7:
        draw_transparent.text(
            (text_x, text_y),
            textString,
            font=font,
            fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency),
        )
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    if manager.transparent_text_var:
        image = Image.alpha_composite(image, transparent_text_image)
    image = Image.alpha_composite(image, menuHelperGuides)

    headerBubbles = generateHeaderBubbles(manager, render_factor)
    image = Image.alpha_composite(image, headerBubbles)

    if forPreview:
        muOSOverlay = generatePilImageMuOSOverlay(manager, "muxlaunch", render_factor)
        image = Image.alpha_composite(image, muOSOverlay)

    return image


def generatePilImageBootLogo(
    bg_hex, deselected_font_hex, bubble_hex, render_factor, manager: Config
):
    (
        bg_hex,
        deselected_font_hex,
        bubble_hex,
    ) = [
        val[1:] if val.startswith("#") else val
        for val in [
            bg_hex,
            deselected_font_hex,
            bubble_hex,
        ]
    ]

    bg_rgb = hex_to_rgb(bg_hex)
    image = Image.new(
        "RGBA",
        (
            int(manager.deviceScreenWidthVar) * render_factor,
            int(manager.deviceScreenHeightVar) * render_factor,
        ),
        bg_rgb,
    )
    if manager.use_custom_bootlogo_var:
        if manager.bootlogo_image_path and manager.bootlogo_image_path.exists():
            bootlogo_image = Image.open(manager.bootlogo_image_path)
            image.paste(
                bootlogo_image.resize(
                    (
                        int(manager.deviceScreenWidthVar) * render_factor,
                        int(manager.deviceScreenHeightVar) * render_factor,
                    )
                ),
                (0, 0),
            )
            return image
    elif background_image != None:
        image.paste(
            background_image.resize(
                (
                    int(manager.deviceScreenWidthVar) * render_factor,
                    int(manager.deviceScreenHeightVar) * render_factor,
                )
            ),
            (0, 0),
        )

    draw = ImageDraw.Draw(image)
    transparent_text_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw_transparent = ImageDraw.Draw(transparent_text_image)

    selected_font_path = get_font_path(
        manager.use_alt_font_var, manager.alt_font_filename
    )

    mu_font_size = 130 * render_factor
    mu_font = ImageFont.truetype(selected_font_path, mu_font_size)
    os_font_size = 98 * render_factor
    os_font = ImageFont.truetype(selected_font_path, os_font_size)

    screen_x_middle, screen_y_middle = (
        (int(manager.deviceScreenWidthVar) / 2) * render_factor,
        (int(manager.deviceScreenHeightVar) / 2) * render_factor,
    )

    from_middle_padding = 20 * render_factor

    muText = "mu"

    osText = "OS"

    muTextBbox = mu_font.getbbox(muText)
    osTextBbox = os_font.getbbox(osText)

    muTextWidth = muTextBbox[2] - muTextBbox[0]
    muTextHeight = muTextBbox[3] - muTextBbox[1]
    mu_y_location = screen_y_middle - muTextHeight / 2 - muTextBbox[1]
    mu_x_location = screen_x_middle - from_middle_padding - muTextWidth

    osTextWidth = osTextBbox[2] - osTextBbox[0]
    osTextHeight = osTextBbox[3] - osTextBbox[1]
    os_y_location = screen_y_middle - osTextHeight / 2 - osTextBbox[1]
    os_x_location = screen_x_middle + from_middle_padding

    bubble_x_padding = 30 * render_factor
    bubble_y_padding = 25 * render_factor
    bubble_x_mid_point = screen_x_middle + from_middle_padding + (osTextWidth / 2)
    bubble_width = bubble_x_padding + osTextWidth + bubble_x_padding
    bubble_height = bubble_y_padding + osTextHeight + bubble_y_padding
    transparency = 0

    draw_transparent.rounded_rectangle(
        [
            (
                bubble_x_mid_point - (bubble_width / 2),
                screen_y_middle - (bubble_height / 2),
            ),
            (
                bubble_x_mid_point + (bubble_width / 2),
                screen_y_middle + (bubble_height / 2),
            ),
        ],
        radius=bubble_height / 2,
        fill=f"#{bubble_hex}",
    )

    draw.text(
        (mu_x_location, mu_y_location),
        muText,
        font=mu_font,
        fill=f"#{deselected_font_hex}",
    )
    draw_transparent.text(
        (os_x_location, os_y_location),
        osText,
        font=os_font,
        fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency),
    )

    combined_image = Image.alpha_composite(image, transparent_text_image)

    return combined_image


def generatePilImageBootScreen(
    bg_hex,
    deselected_font_hex,
    icon_hex,
    display_text,
    render_factor,
    manager: Config,
    icon_path: Path | None = None,
):
    (
        bg_hex,
        deselected_font_hex,
        icon_hex,
    ) = [
        val[1:] if val.startswith("#") else val
        for val in [
            bg_hex,
            deselected_font_hex,
            icon_hex,
        ]
    ]

    bg_rgb = hex_to_rgb(bg_hex)
    image = Image.new(
        "RGBA",
        (
            int(manager.deviceScreenWidthVar) * render_factor,
            int(manager.deviceScreenHeightVar) * render_factor,
        ),
        bg_rgb,
    )
    if background_image != None:
        image.paste(
            background_image.resize(
                (
                    int(manager.deviceScreenWidthVar) * render_factor,
                    int(manager.deviceScreenHeightVar) * render_factor,
                )
            ),
            (0, 0),
        )

    draw = ImageDraw.Draw(image)

    selected_font_path = get_font_path(
        manager.use_alt_font_var, manager.alt_font_filename
    )

    screen_x_middle, screen_y_middle = (
        int((int(manager.deviceScreenWidthVar) / 2) * render_factor),
        int((int(manager.deviceScreenHeightVar) / 2) * render_factor),
    )

    from_middle_padding = 0

    if icon_path != None:
        if icon_path and icon_path.exists():
            from_middle_padding = 50 * render_factor

            logoColoured = change_logo_color(icon_path, icon_hex)
            logoColoured = logoColoured.resize(
                (
                    int((logoColoured.size[0] / 5) * render_factor),
                    int((logoColoured.size[1] / 5) * render_factor),
                ),
                Image.LANCZOS,
            )

            logo_y_location = int(
                screen_y_middle - logoColoured.size[1] / 2 - from_middle_padding
            )
            logo_x_location = int(screen_x_middle - logoColoured.size[0] / 2)

            image.paste(logoColoured, (logo_x_location, logo_y_location), logoColoured)

    font_size = int(57.6 * render_factor)
    font = ImageFont.truetype(selected_font_path, font_size)

    displayText = display_text
    if manager.alternate_menu_names_var:
        displayText = bidi_get_display(
            menuNameMap.get(display_text.lower(), display_text)
        )

    textBbox = font.getbbox(displayText)

    textWidth = int(textBbox[2] - textBbox[0])
    textHeight = int(textBbox[3] - textBbox[1])
    y_location = int(
        screen_y_middle - textHeight / 2 - textBbox[1] + from_middle_padding
    )
    x_location = int(screen_x_middle - textWidth / 2)

    draw.text(
        (x_location, y_location), displayText, font=font, fill=f"#{deselected_font_hex}"
    )

    return image


def generatePilImageDefaultScreen(bg_hex, render_factor, manager: Config):
    if bg_hex.startswith("#"):
        bg_hex = bg_hex[1:]

    bg_rgb = hex_to_rgb(bg_hex)
    image = Image.new(
        "RGBA",
        (
            int(manager.deviceScreenWidthVar) * render_factor,
            int(manager.deviceScreenHeightVar) * render_factor,
        ),
        bg_rgb,
    )
    if background_image != None:
        image.paste(
            background_image.resize(
                (
                    int(manager.deviceScreenWidthVar) * render_factor,
                    int(manager.deviceScreenHeightVar) * render_factor,
                )
            ),
            (0, 0),
        )
    return image


def HorizontalMenuGen(
    progress_bar,
    muOSSystemName,
    listItems,
    bg_hex,
    selected_font_hex,
    deselected_font_hex,
    bubble_hex,
    icon_hex,
    render_factor,
    outputDir: Path,
    variant,
    manager: Config,
    threadNumber=0,
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
    for workingIndex in range(startIndex, endIndex):
        workingItem = listItems[workingIndex]
        if variant == "Horizontal":
            image = generatePilImageHorizontal(
                progress_bar,
                workingIndex,
                bg_hex,
                selected_font_hex,
                deselected_font_hex,
                bubble_hex,
                icon_hex,
                render_factor,
                manager,
                transparent=True,
            )
        elif variant == "Alt-Horizontal":
            image = generatePilImageAltHorizontal(
                progress_bar,
                workingIndex,
                bg_hex,
                selected_font_hex,
                deselected_font_hex,
                bubble_hex,
                icon_hex,
                render_factor,
                manager,
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

    for section in menus2405_2:
        if section[0].startswith("mux"):
            for n in section[1]:
                defaultMenuNameMap[n[0].lower()] = n[0]

    return defaultMenuNameMap


def select_color(manager, var_name, tk_variables):
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


def select_theme_directory_path(manager, var_name, tk_variables):
    dir_path = filedialog.askdirectory()

    if dir_path:
        manager.set_value(var_name, dir_path)
        tk_variables[var_name].set(dir_path)


def select_background_image_path(manager, var_name, tk_variables):
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


def select_bootlogo_image_path(manager, var_name, tk_variables):
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


def select_alt_font_path(manager, var_name, tk_variables):
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


# INFO FOR BELOW LIST
#        FOLDER NAME      DISPLAYED NAME     FILE NAME

menus2405 = [
    [
        "muxapps",
        [
            ["Archive Manager", "archive"],
            ["Backup Manager", "backup"],
            ["Portmaster", "portmaster"],
            ["Retroarch", "retroarch"],
            ["Dingux Commander", "dingux"],
            ["Gmu Music Player", "gmu"],
        ],
    ],
    [
        "muxconfig",
        [
            ["General Settings", "general"],
            ["Theme Picker", "theme"],
            ["Wi-Fi Settings", "network"],
            ["Web Services", "service"],
            ["Date and Time", "clock"],
            ["Device Type", "device"],
            ["System Refresh", "refresh"],
        ],
    ],
    [
        "muxdevice",
        [
            ["RG35XX - H", "rg35xx-h"],
            ["RG35XX - Plus", "rg35xx-plus"],
            ["RG35XX - 2024", "rg35xx-2024"],
        ],
    ],
    [
        "muxinfo",
        [
            ["Input Tester", "tester"],
            ["System Details", "system"],
            ["Supporters", "credit"],
        ],
    ],
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
    ],
]

menus2405_1 = [
    [
        "muxapp",
        [
            ["Archive Manager", "Archive Manager"],
            ["Dingux Commander", "Dingux Commander"],
            ["GMU Music Player", "GMU Music Player"],
            ["PortMaster", "PortMaster"],
            ["RetroArch", "RetroArch"],
            ["Simple Terminal", "Simple Terminal"],
            ["Task Toolkit", "Task Toolkit"],
        ],
    ],
    [
        "muxconfig",
        [
            ["General Settings", "general"],
            ["Theme Picker", "theme"],
            ["Wi-Fi Settings", "network"],
            ["Web Services", "service"],
            ["Date and Time", "clock"],
            ["Device Type", "device"],
        ],
    ],
    [
        "muxdevice",
        [
            ["RG35XX - H", "rg35xx-h"],
            ["RG35XX - Plus", "rg35xx-plus"],
            ["RG35XX - SP", "rg35xx-sp"],
            ["RG35XX - 2024", "rg35xx-2024"],
        ],
    ],
    [
        "muxinfo",
        [
            ["Input Tester", "tester"],
            ["System Details", "system"],
            ["Supporters", "credit"],
        ],
    ],
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
    ],
]
menus2405_2 = [
    [
        "muxapp",
        [
            ["Archive Manager", "Archive Manager"],
            ["Dingux Commander", "Dingux Commander"],
            ["Flip Clock", "Flip Clock"],
            ["GMU Music Player", "GMU Music Player"],
            ["Moonlight", "Moonlight"],
            ["PortMaster", "PortMaster"],
            ["PPSSPP", "PPSSPP"],
            ["RetroArch", "RetroArch"],
            ["Simple Terminal", "Simple Terminal"],
            ["Task Toolkit", "Task Toolkit"],
        ],
    ],
    [
        "muxconfig",
        [
            ["General Settings", "general"],
            ["Theme Picker", "theme"],
            ["Wi-Fi Settings", "network"],
            ["Web Services", "service"],
            ["Date and Time", "clock"],
            ["Device Type", "device"],
        ],
    ],
    [
        "muxdevice",
        [
            ["RG35XX - H", "rg35xx-h"],
            ["RG35XX - Plus", "rg35xx-plus"],
            ["RG35XX - SP", "rg35xx-sp"],
            ["RG35XX - 2024", "rg35xx-2024"],
        ],
    ],
    [
        "muxinfo",
        [
            ["Input Tester", "tester"],
            ["System Details", "system"],
            ["Supporters", "credit"],
        ],
    ],
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
    ],
]
menus2405_3 = [
    [
        "muxapp",
        [
            ["Archive Manager", "Archive Manager"],
            ["Dingux Commander", "Dingux Commander"],
            ["Flip Clock", "Flip Clock"],
            ["GMU Music Player", "GMU Music Player"],
            ["Moonlight", "Moonlight"],
            ["PortMaster", "PortMaster"],
            ["PPSSPP", "PPSSPP"],
            ["RetroArch", "RetroArch"],
            ["Simple Terminal", "Simple Terminal"],
            ["Task Toolkit", "Task Toolkit"],
        ],
    ],
    [
        "muxconfig",
        [
            ["General Settings", "general"],
            ["Theme Picker", "theme"],
            ["Wi-Fi Settings", "network"],
            ["Web Services", "service"],
            ["Date and Time", "clock"],
            ["Device Type", "device"],
        ],
    ],
    [
        "muxdevice",
        [
            ["RG35XX - H", "rg35xx-h"],
            ["RG35XX - Plus", "rg35xx-plus"],
            ["RG35XX - SP", "rg35xx-sp"],
            ["RG35XX - 2024", "rg35xx-2024"],
        ],
    ],
    [
        "muxinfo",
        [
            ["Input Tester", "tester"],
            ["System Details", "system"],
            ["Supporters", "credit"],
        ],
    ],
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
    ],
]


def hex_to_rgb(hex_color: str, alpha=1.0):
    # Convert hex to RGB
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return (rgb[0], rgb[1], rgb[2], int(alpha * 255))


def rgb_to_hex(rgb_color):
    # Convert RGB to hex
    return "{:02x}{:02x}{:02x}".format(*rgb_color)


def interpolate_color_component(c1, c2, factor):
    # Interpolate a single color component
    return int(c1 + (c2 - c1) * factor)


def percentage_color(hex1, hex2, percentage):
    # Convert hex colors to RGB
    rgb1 = hex_to_rgb(hex1)
    rgb2 = hex_to_rgb(hex2)

    # Calculate the interpolated color for each component
    interp_rgb = tuple(
        interpolate_color_component(c1, c2, percentage) for c1, c2 in zip(rgb1, rgb2)
    )

    # Convert interpolated RGB back to hex
    return rgb_to_hex(interp_rgb)


def round_to_nearest_odd(number):
    high_odd = (number // 2) * 2 + 1
    low_odd = high_odd - 2
    return (
        int(high_odd)
        if abs(number - high_odd) < abs(number - low_odd)
        else int(low_odd)
    )


def generate_theme(
    progress_bar,
    loading_window,
    threadNumber,
    manager: Config,
    barrier,
    resolutions,
    assumed_res,
):
    temp_build_dir = RESOURCES_DIR / f".TempBuildTheme{threadNumber}"
    temp_system_icons_dir = RESOURCES_DIR / f".TempBuildSystemIconsAMFile{threadNumber}"
    assumed_res_dir = temp_build_dir / f"{assumed_res[0]}x{assumed_res[1]}"

    try:
        progress_bar["value"] = 0
        if (
            manager.main_menu_style_var == "Alt-Horizontal"
            or manager.main_menu_style_var == "Horizontal"
        ):
            progress_bar["maximum"] = 28 * len(resolutions)
        elif manager.main_menu_style_var == "Vertical":
            progress_bar["maximum"] = 20 * len(resolutions)
        else:
            raise ValueError("Something went wrong with your Main Menu Style")

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

            res_config = copy.deepcopy(manager)
            res_manager.deviceScreenWidthVar = width
            res_manager.deviceScreenHeightVar = height
            if height != assumed_res[1]:
                res_manager.itemsPerScreenVar = height_items_per_screen_map[height]
                res_manager.itemsPerScreenVar = height_items_per_screen_map[height]
                if res_manager.clock_alignment_var == "Centre":
                    res_manager.clockHorizontalLeftPaddingVar = str(
                        int(
                            int(res_manager.clockHorizontalLeftPaddingVar)
                            * (width / assumed_res[0])
                        )
                    )
                    res_manager.clockHorizontalRightPaddingVar = str(
                        int(
                            int(res_manager.clockHorizontalRightPaddingVar)
                            * (width / assumed_res[0])
                        )
                    )
                if res_manager.header_glyph_alignment_var == "Centre":
                    res_manager.header_glyph_horizontal_left_padding_var = str(
                        int(
                            int(res_manager.header_glyph_horizontal_left_padding_var)
                            * (width / assumed_res[0])
                        )
                    )
                    res_manager.header_glyph_horizontal_right_padding_var = str(
                        int(
                            int(res_manager.header_glyph_horizontal_right_padding_var)
                            * (width / assumed_res[0])
                        )
                    )
                if res_manager.page_title_alignment_var == "Centre":
                    res_manager.pageTitlePaddingVar = str(
                        int(
                            int(res_manager.pageTitlePaddingVar)
                            * (width / assumed_res[0])
                        )
                    )
                    res_manager.pageTitlePaddingVar = str(
                        int(
                            int(res_manager.pageTitlePaddingVar)
                            * (width / assumed_res[0])
                        )
                    )
            FillTempThemeFolder(progress_bar, threadNumber, manager=res_config)

            try:
                for target in ["font", "glyph", "image", "scheme", "preview.png"]:
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

        for target in ["font", "glyph", "image", "scheme", "preview.png"]:
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
        loading_window.destroy()
        barrier.wait()
    except Exception as e:
        print(e)
        loading_window.destroy()
        theme_dir = manager.theme_directory_path

        if manager.advanced_error_var:
            tb_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            messagebox.showerror(
                "Error", f"An unexpected error occurred: {e}\n{tb_str}"
            )
        else:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

        delete_folder(temp_build_dir)
        if manager.developer_preview_var:
            for width, height in resolutions:
                thread_and_res = f"{threadNumber}[{width}x{height}].png"
                temp_preview_path = RESOURCES_DIR / f"TempPreview{thread_and_res}"
                preview_path = theme_dir / "preview" / f"TempPreview{thread_and_res}"

                delete_file(temp_preview_path)
                delete_file(preview_path)


def generate_themes(themes):
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
            assumed_res = [640, 480]
            if match:
                assumed_res = [int(match.group(1)), int(match.group(2))]
            else:
                raise ValueError(
                    "Invalid device type format, cannot find screen dimensions"
                )
            all_resolutions = []
            for device_type in deviceTypeOptions:
                match = re.search(r"\[(\d+)x(\d+)\]", device_type)
                if match:
                    all_resolutions.append([int(match.group(1)), int(match.group(2))])
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


def FillTempThemeFolder(progress_bar, threadNumber, manager: Config):
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
    if not "Generating for lanuage on muxlaunch":
        horizontalLogoSize = getHorizontalLogoSize(
            HORIZONTAL_LOGOS_DIR / "explore.png", 1, manager
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
    for button in buttonsToGenerate:
        button_image = generateIndividualButtonGlyph(
            button,
            selected_font_path,
            accent_hex,
            render_factor,
            button_height,
            manager.physical_controler_layout_var,
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
    bootlogoimage = generatePilImageBootLogo(
        manager.bgHexVar,
        manager.deselectedFontHexVar,
        manager.bubbleHexVar,
        render_factor,
        manager,
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    bootlogoimage.save(
        temp_image_dir / "bootlogo.bmp",
        format="BMP",
    )
    progress_bar["value"] += 1

    chargingimage = generatePilImageBootScreen(
        manager.bgHexVar,
        manager.deselectedFontHexVar,
        manager.iconHexVar,
        "CHARGING...",
        render_factor,
        manager,
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

    loadingimage = generatePilImageBootScreen(
        manager.bgHexVar,
        manager.deselectedFontHexVar,
        manager.iconHexVar,
        "LOADING...",
        render_factor,
        manager,
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    loadingimage.save(
        temp_image_dir / "wall" / "muxstart.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    shutdownimage = generatePilImageBootScreen(
        manager.bgHexVar,
        manager.deselectedFontHexVar,
        manager.iconHexVar,
        "Shutting Down...",
        render_factor,
        manager,
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    shutdownimage.save(
        temp_image_dir / "shutdown.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    rebootimage = generatePilImageBootScreen(
        manager.bgHexVar,
        manager.deselectedFontHexVar,
        manager.iconHexVar,
        "Rebooting...",
        render_factor,
        manager,
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    rebootimage.save(
        temp_image_dir / "reboot.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    defaultimage = generatePilImageDefaultScreen(
        manager.bgHexVar, render_factor, manager
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    defaultimage.save(
        temp_image_dir / "wall" / "default.png",
        format="PNG",
    )
    progress_bar["value"] += 1

    # TODO If implimented it would be great to only set these once as a default.png type thing, and then make it work in every menu

    visualbuttonoverlay_B_BACK_A_SELECT = generateMuOSBackgroundOverlay(
        [["B", "BACK"], ["A", "SELECT"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
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

    visualbuttonoverlay_A_SELECT = generateMuOSBackgroundOverlay(
        [["A", "SELECT"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
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

    visualbuttonoverlay_B_BACK = generateMuOSBackgroundOverlay(
        [["B", "BACK"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
        lhsButtons=[["POWER", "SLEEP"]],
    ).resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )
    visualbuttonoverlay_B_SAVE = generateMuOSBackgroundOverlay(
        [["B", "SAVE"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
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

    bg_rgb = hex_to_rgb(bg_hex)
    background = Image.new(
        "RGBA",
        (
            int(manager.deviceScreenWidthVar) * render_factor,
            int(manager.deviceScreenHeightVar) * render_factor,
        ),
        bg_rgb,
    )
    if background_image is not None:
        background.paste(
            background_image.resize(
                (
                    int(manager.deviceScreenWidthVar) * render_factor,
                    int(manager.deviceScreenHeightVar) * render_factor,
                )
            ),
            (0, 0),
        )
    background = background.resize(
        (int(manager.deviceScreenWidthVar), int(manager.deviceScreenHeightVar)),
        Image.LANCZOS,
    )

    visualbuttonoverlay_muxapp = generateMuOSBackgroundOverlay(
        [["B", "BACK"], ["A", "LAUNCH"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
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

    visualbuttonoverlay_muxplore = generateMuOSBackgroundOverlay(
        [
            ["MENU", "INFO"],
            ["Y", "FAVOURITE"],
            ["X", "REFRESH"],
            ["B", "BACK"],
            ["A", "OPEN"],
        ],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
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

    visualbuttonoverlay_muxfavourite = generateMuOSBackgroundOverlay(
        [["MENU", "INFO"], ["X", "REMOVE"], ["B", "BACK"], ["A", "OPEN"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
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

    visualbuttonoverlay_muxhistory = generateMuOSBackgroundOverlay(
        [
            ["MENU", "INFO"],
            ["Y", "FAVOURITE"],
            ["X", "REMOVE"],
            ["B", "BACK"],
            ["A", "OPEN"],
        ],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
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

    visualbuttonoverlay_muxtimezone = generateMuOSBackgroundOverlay(
        [["A", "SELECT"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
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

    visualbuttonoverlay_muxpicker = generateMuOSBackgroundOverlay(
        [["Y", "SAVE"], ["B", "BACK"], ["A", "SELECT"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
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

    visualbuttonoverlay_muxlanguage = generateMuOSBackgroundOverlay(
        [["B", "BACK"], ["A", "SELECT"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
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

    visualbuttonoverlay_muxarchive = generateMuOSBackgroundOverlay(
        [["B", "BACK"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
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

    visualbuttonoverlay_muxnetprofile = generateMuOSBackgroundOverlay(
        [["Y", "REMOVE"], ["X", "SAVE"], ["B", "BACK"], ["A", "LOAD"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
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

    visualbuttonoverlay_muxnetscan = generateMuOSBackgroundOverlay(
        [["X", "RESCAN"], ["B", "BACK"], ["A", "USE"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
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

    visualbuttonoverlay_muxgov = generateMuOSBackgroundOverlay(
        [["Y", "RECURSIVE"], ["X", "DIRECTORY"], ["A", "INDIVIDUAL"], ["B", "BACK"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
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

    visualbuttonoverlay_muxsearch = generateMuOSBackgroundOverlay(
        [["X", "CLEAR"], ["B", "BACK"], ["A", "SELECT"]],
        selected_font_path,
        manager.footerBubbleHexVar,
        render_factor,
        manager,
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
        workingMenus = menus2405_3

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
        previewImage = generatePilImageHorizontal(
            fakeprogressbar,
            0,
            manager.bgHexVar,
            manager.selectedFontHexVar,
            manager.deselectedFontHexVar,
            manager.bubbleHexVar,
            manager.iconHexVar,
            render_factor,
            manager,
            transparent=False,
            forPreview=True,
        )
    elif manager.main_menu_style_var == "Alt-Horizontal":
        previewImage = generatePilImageAltHorizontal(
            fakeprogressbar,
            0,
            manager.bgHexVar,
            manager.selectedFontHexVar,
            manager.deselectedFontHexVar,
            manager.bubbleHexVar,
            manager.iconHexVar,
            render_factor,
            manager,
            transparent=False,
            forPreview=True,
        )
    elif manager.main_menu_style_var == "Vertical":
        previewImage = generatePilImageVertical(
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
            render_factor,
            manager,
            transparent=False,
            forPreview=True,
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


def start_theme_task():
    barrier = threading.Barrier(2)
    # Create a new Toplevel window for the loading bar
    loading_window = tk.Toplevel(root)
    loading_window.title("Generating...")
    loading_window.geometry("300x100")

    # Create a Progressbar widget in the loading window
    progress_bar = ttk.Progressbar(
        loading_window, orient="horizontal", length=280, mode="determinate"
    )
    progress_bar.pack(pady=20)

    match = re.search(r"\[(\d+)x(\d+)\]", manager.device_type_var)
    assumed_res = [640, 480]
    if match:
        assumed_res = [int(match.group(1)), int(match.group(2))]
    else:
        raise ValueError("Invalid device type format, cannot find screen dimensions")
    all_resolutions = []
    for device_type in deviceTypeOptions:
        match = re.search(r"\[(\d+)x(\d+)\]", device_type)
        if match:
            all_resolutions.append([int(match.group(1)), int(match.group(2))])

    input_queue = queue.Queue()
    output_queue = queue.Queue()

    # Start the long-running task in a separate thread
    threading.Thread(
        target=generate_theme,
        args=(
            progress_bar,
            loading_window,
            -1,
            manager,
            barrier,
            all_resolutions,
            assumed_res,
        ),
    ).start()


def start_bulk_theme_task():
    # Create a new Toplevel window for the loading bar
    themes = manager.load_premade_themes()

    threading.Thread(target=generate_themes, args=(themes,)).start()


# subtitle_font = font.Font(family="Helvetica", size=14, weight="bold")
# title_font = font.Font(family="Helvetica", size=20, weight="bold")


def update_image_label(image_label, pil_image):
    tk_image = ImageTk.PhotoImage(pil_image)
    image_label.config(image=tk_image)
    image_label.image = tk_image
    # image_label.clear()


def remove_image_from_label(image_label):
    image_label.config(image="")


def get_current_image(image_label):
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
    image, outline_color=(255, 0, 0), outline_width=5, gap=5
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


valid_params = True


def map_value(value, x_min, x_max, y_min, y_max):
    # Calculate the proportion of the value within the input range
    proportion = (value - x_min) / (x_max - x_min)

    # Map this proportion to the output range
    mapped_value = y_min + proportion * (y_max - y_min)

    return mapped_value


def on_change(app, *args):
    # global menuNameMap
    # menuNameMap = getAlternateMenuNameDict()
    try:
        preview_overlay_image = Image.open(
            OVERLAY_DIR
            / f"{manager.deviceScreenWidthVar}x{manager.deviceScreenHeightVar}"
            / f"{manager.selected_overlay_var}.png",
        ).convert("RGBA")
    except:
        pass
    global contentPaddingTop
    try:
        contentPaddingTop = int(manager.contentPaddingTopVar)
    except:
        contentPaddingTop = 40

    global background_image

    if (
        manager.use_custom_background_var
        and manager.background_image_path
        and manager.background_image_path.exists()
    ):
        background_image = Image.open(manager.background_image_path)
    else:
        background_image = None

    global menus2405
    global menus2405_1  ## NOT GLOBALS AHH SORRY HACKY SHOULD REMOVE
    global menus2405_2
    global menus2405_3

    previewApplicationList = []
    if manager.version_var[0:9] == "muOS 2410":
        index = None
        for i, n in enumerate(menus2405_3):
            if n[0] == "muxapp":
                index = i
                break
        if index != None:
            previewApplicationList = [
                [x[0], "menu", x[0]] for x in menus2405_3[index][1]
            ]

    global valid_params

    fakeprogressbar = {"value": 0}
    fakeprogressbar["maximum"] = 1

    previewRenderFactor = 1
    current_image_size = [640, 480]
    if get_current_image(app.image_label1) is not None:
        current_image_size = get_current_image(app.image_label1).size
    preview_size = [current_image_size[0] / 2, current_image_size[1] / 2]
    if app.right_pane.winfo_width() > 100:
        previewRenderFactor = (
            math.ceil(app.right_pane.winfo_width() / current_image_size[1]) + 1
        )  # Affectively anti aliasing in the preview

        preview_size = [
            int(app.right_pane.winfo_width()),
            int(
                app.right_pane.winfo_width()
                * (current_image_size[1] / current_image_size[0])
            ),
        ]
    try:
        if int(manager.deviceScreenHeightVar) < 240:
            raise ValueError("Device Screen Height must be at least 240")
        if int(manager.deviceScreenWidthVar) < 320:
            raise ValueError("Device Screen Width must be at least 320")
        if int(manager.deviceScreenHeightVar) > 4320:
            raise ValueError("Device Screen Height must be at most 4320")
        if int(manager.deviceScreenWidthVar) > 7680:
            raise ValueError("Device Screen Width must be at most 7680")

        if app.right_pane.winfo_width() < 100:
            preview_size = [
                int(int(manager.deviceScreenWidthVar) / 2),
                int(int(manager.deviceScreenHeightVar) / 2),
            ]
        else:
            previewRenderFactor = (
                math.ceil(
                    app.right_pane.winfo_width() / int(manager.deviceScreenWidthVar)
                )
                + 1
            )  # Affectively anti aliasing in the preview

            preview_size = [
                int(app.right_pane.winfo_width()),
                int(
                    app.right_pane.winfo_width()
                    * (
                        int(manager.deviceScreenHeightVar)
                        / int(manager.deviceScreenWidthVar)
                    )
                ),
            ]
        # preview_size = [int(640/2),int(480/2)]

        # This function will run whenever any traced variable changes

        previewItemList = [
            ["Content Explorer", "Menu", "explore"],
            ["Favourites", "Menu", "favourite"],
            ["History", "Menu", "history"],
            ["Applications", "Menu", "apps"],
            ["Information", "Menu", "info"],
            ["Configuration", "Menu", "config"],
            ["Reboot Device", "Menu", "reboot"],
            ["Shutdown Device", "Menu", "shutdown"],
        ]

        if manager.main_menu_style_var == "Horizontal":
            image1 = generatePilImageHorizontal(
                fakeprogressbar,
                0,
                manager.bgHexVar,
                manager.selectedFontHexVar,
                manager.deselectedFontHexVar,
                manager.bubbleHexVar,
                manager.iconHexVar,
                previewRenderFactor,
                manager,
                transparent=False,
                forPreview=True,
            ).resize(preview_size, Image.LANCZOS)
        elif manager.main_menu_style_var == "Alt-Horizontal":
            image1 = generatePilImageAltHorizontal(
                fakeprogressbar,
                0,
                manager.bgHexVar,
                manager.selectedFontHexVar,
                manager.deselectedFontHexVar,
                manager.bubbleHexVar,
                manager.iconHexVar,
                previewRenderFactor,
                manager,
                transparent=False,
                forPreview=True,
            ).resize(preview_size, Image.LANCZOS)
        elif manager.main_menu_style_var == "Vertical":
            image1 = generatePilImageVertical(
                fakeprogressbar,
                0,
                "muxlaunch",
                previewItemList[0 : int(manager.itemsPerScreenVar)],
                int(manager.textPaddingVar),
                int(manager.bubblePaddingVar),
                int(manager.itemsPerScreenVar),
                manager.bgHexVar,
                manager.selectedFontHexVar,
                manager.deselectedFontHexVar,
                manager.bubbleHexVar,
                previewRenderFactor,
                manager,
                transparent=False,
                forPreview=True,
            ).resize(preview_size, Image.LANCZOS)

        image2 = generatePilImageVertical(
            fakeprogressbar,
            0,
            "muxapp",
            previewApplicationList[0 : int(manager.itemsPerScreenVar)],
            int(manager.textPaddingVar),
            int(manager.bubblePaddingVar),
            int(manager.itemsPerScreenVar),
            manager.bgHexVar,
            manager.selectedFontHexVar,
            manager.deselectedFontHexVar,
            manager.bubbleHexVar,
            previewRenderFactor,
            manager,
            fileCounter=f"1 / {manager.itemsPerScreenVar}",
            transparent=False,
            forPreview=True,
        ).resize(preview_size, Image.LANCZOS)

        if manager.main_menu_style_var == "Horizontal":
            image3 = generatePilImageHorizontal(
                fakeprogressbar,
                4,
                manager.bgHexVar,
                manager.selectedFontHexVar,
                manager.deselectedFontHexVar,
                manager.bubbleHexVar,
                manager.iconHexVar,
                previewRenderFactor,
                manager,
                transparent=False,
                forPreview=True,
            ).resize(preview_size, Image.LANCZOS)

        elif manager.main_menu_style_var == "Alt-Horizontal":
            image3 = generatePilImageAltHorizontal(
                fakeprogressbar,
                4,
                manager.bgHexVar,
                manager.selectedFontHexVar,
                manager.deselectedFontHexVar,
                manager.bubbleHexVar,
                manager.iconHexVar,
                previewRenderFactor,
                manager,
                transparent=False,
                forPreview=True,
            ).resize(preview_size, Image.LANCZOS)

        if manager.include_overlay_var and manager.selected_overlay_var != "":
            preview_overlay_resized = preview_overlay_image.resize(
                image1.size, Image.LANCZOS
            )
            image1.paste(preview_overlay_resized, (0, 0), preview_overlay_resized)
            image2.paste(preview_overlay_resized, (0, 0), preview_overlay_resized)
            if manager.main_menu_style_var != "Vertical":
                image3.paste(preview_overlay_resized, (0, 0), preview_overlay_resized)

        update_image_label(app.image_label1, image1)
        update_image_label(app.image_label2, image2)
        if manager.main_menu_style_var != "Vertical":
            update_image_label(app.image_label3, image3)
        else:
            remove_image_from_label(app.image_label3)
        valid_params = True
    except Exception:
        traceback.print_exc()
        if (
            get_current_image(app.image_label1) != None
            and get_current_image(app.image_label2) != None
            and get_current_image(app.image_label3)
        ):
            if valid_params:
                redOutlineImage1 = outline_image_with_inner_gap(
                    get_current_image(app.image_label1)
                ).resize(preview_size, Image.LANCZOS)
                redOutlineImage2 = outline_image_with_inner_gap(
                    get_current_image(app.image_label2)
                ).resize(preview_size, Image.LANCZOS)
                if manager.main_menu_style_var != "Vertical":
                    redOutlineImage3 = outline_image_with_inner_gap(
                        get_current_image(app.image_label3)
                    ).resize(preview_size, Image.LANCZOS)
                update_image_label(app.image_label1, redOutlineImage1)
                update_image_label(app.image_label2, redOutlineImage2)
                if manager.main_menu_style_var != "Vertical":
                    update_image_label(app.image_label3, redOutlineImage3)
                valid_params = False
        else:
            raise


# menuNameMap = getAlternateMenuNameDict()


def replace_scheme_options(newSchemeDir, fileName, replacementStringMap):
    file_path = newSchemeDir / f"{fileName}.txt"
    replacements = {
        stringToBeReplaced: replacementStringMap[fileName].get(
            stringToBeReplaced, defaultValue
        )
        for stringToBeReplaced, defaultValue in replacementStringMap["default"].items()
    }

    with file_path.open("rb") as file:
        file_contents = file.read()

    # Replace the occurrences of the search_string with replace_string in binary data
    new_contents = file_contents.decode().format(**replacements)

    # Write the new content back to the file in binary mode
    with file_path.open("wb") as file:
        file.write(new_contents.encode())


def main():
    commands_map = {
        "select_color": select_color,
        "select_bootlogo_image_path": select_bootlogo_image_path,
        "select_background_image_path": select_background_image_path,
        "select_alt_font_path": select_alt_font_path,
        "select_theme_directory_path": select_theme_directory_path,
    }

    app = ThemeGeneratorApp(
        title="MinUI Theme Generator",
        min_size=(1080, 500),
        settings_manager=manager,
        commands_map=commands_map,
    )
    app.build_sections_from_settings(partial(on_change, app))

    app.run()


if __name__ == "__main__":
    main()
