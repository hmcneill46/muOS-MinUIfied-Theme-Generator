# -*- coding: utf-8 -*-
from PIL import ImageTk,Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageColor, ImageChops
try:
    from bidi import get_display as bidi_get_display
except:
    from bidi.algorithm import get_display as bidi_get_display
import os
import sys
import math
import tkinter as tk
from tkinter import font, PanedWindow, Scrollbar,filedialog, simpledialog, messagebox, ttk, colorchooser
import shutil
import re
import traceback
import platform
import threading
import queue
import time
import json
import subprocess
import shutil
import numpy as np
import copy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime


Image.MAX_IMAGE_PIXELS = None

TargetMuOSVersion = "2502.0"

## TODO look into centre align and left align
## TODO make header resizable

if getattr(sys, 'frozen', False):
    # The application is running as a bundle
    internal_files_dir = sys._MEIPASS
    script_dir = os.path.dirname(sys.executable)
else:
    # The application is running in a normal Python environment
    internal_files_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir = os.path.dirname(os.path.abspath(__file__))

#HI
# Default values for parameters
class Config: # TODO delete unneeded variables
    def __init__(self, config_file=os.path.join(script_dir,'MinUIThemeGeneratorConfig.json')):
        self.config_file = config_file
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
        self.footerBubbleHexVar = "ffffff"
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
        self.alt_font_path = ""
        self.alt_text_path = "AlternativeMenuNames.json"
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
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                config_data = json.load(file)
                self.__dict__.update(config_data)
        else:
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.__dict__, file, indent=4)
    
    def load_premade_themes(self, themes_file='PremadeThemes.json'):
        if os.path.exists(themes_file):
            with open(themes_file, 'r') as file:
                themes_data = json.load(file)
                return themes_data['themes']
        return []

    def apply_theme(self, theme):
        # Update the Config object with all key-value pairs from the theme
        self.__dict__.update(theme)
        self.save_config()

global_config = Config()

background_image = None

# Define constants
render_factor = 5

contentPaddingTop = 44
textMF = 0.7


def change_logo_color(input, hex_color):
    # Load the image
    if isinstance(input, Image.Image):
        img = input
    else:
        img = Image.open(input).convert("RGBA")
    
    # Convert hex_color to RGBA
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Create a new image with the same size and the specified color
    color_image = Image.new("RGBA", img.size, (r, g, b, 255))
    
    # Get the alpha channel from the original image
    alpha = img.split()[3]
    
    # Composite the color image with the alpha channel
    result_image = Image.composite(color_image, Image.new("RGBA", img.size, (0, 0, 0, 0)), alpha)
    
    return result_image

def generateIndividualButtonGlyph(buttonText,selected_font_path,colour_hex,render_factor, button_height, physical_controller_layout):
    in_smaller_bubble_font_size = button_height*(20.1/40)*render_factor
    inSmallerBubbleFont = ImageFont.truetype(selected_font_path, in_smaller_bubble_font_size)

    single_letter_font_size = button_height*(28/40)*render_factor
    singleLetterFont = ImageFont.truetype(selected_font_path, single_letter_font_size)

    isb_text_bbox = inSmallerBubbleFont.getbbox(buttonText)
    isb_text_height = isb_text_bbox[3]-isb_text_bbox[1]
    in_smaller_bubble_text_y = ((button_height*render_factor)/2) - (isb_text_height / 2)-isb_text_bbox[1]

    sl_text_bbox = singleLetterFont.getbbox(buttonText)
    sl_text_height = sl_text_bbox[3]-sl_text_bbox[1]
    single_letter_text_y = ((button_height*render_factor)/2) - (sl_text_height / 2)-sl_text_bbox[1]

    horizontal_small_padding = button_height*(10/40)

    rendered_bubble_height = int(button_height*render_factor)

    if buttonText.upper() in ["A", "B", "X", "Y"] and physical_controller_layout in ["PlayStation", "Xbox", "Universal"]:
        buttonSize = (rendered_bubble_height, rendered_bubble_height)
        if physical_controller_layout == "PlayStation":
            image = Image.open(os.path.join(internal_files_dir, "Assets", "Button Glyphs", "PlayStation",f"{buttonText.upper()}.png")).convert("RGBA").resize(buttonSize, Image.LANCZOS)
        if physical_controller_layout == "Universal":
            image = Image.open(os.path.join(internal_files_dir, "Assets", "Button Glyphs", "Universal",f"{buttonText.upper()}.png")).convert("RGBA").resize(buttonSize, Image.LANCZOS)
        elif physical_controller_layout == "Xbox":
            if buttonText.upper() == "A":
                image = generateIndividualButtonGlyph("B", selected_font_path, colour_hex, render_factor, button_height, "Nintendo")
            elif buttonText.upper() == "B":
                image = generateIndividualButtonGlyph("A", selected_font_path, colour_hex, render_factor, button_height, "Nintendo")
            elif buttonText.upper() == "X":
                image = generateIndividualButtonGlyph("Y", selected_font_path, colour_hex, render_factor, button_height, "Nintendo")
            elif buttonText.upper() == "Y":
                image = generateIndividualButtonGlyph("X", selected_font_path, colour_hex, render_factor, button_height, "Nintendo")



    elif len(buttonText) == 1:
        image = Image.new("RGBA", (rendered_bubble_height, rendered_bubble_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        circleCentreX = ((rendered_bubble_height)/2)
        draw.ellipse((0, 0,rendered_bubble_height, rendered_bubble_height),fill=f"#{colour_hex}")
        singleLetterWidth = sl_text_bbox[2]-sl_text_bbox[0]
        smallerTextX = circleCentreX-(singleLetterWidth/2)
        draw.text(( smallerTextX,single_letter_text_y), buttonText, font=singleLetterFont, fill=(*ImageColor.getrgb(f"#{colour_hex}"), int(255*0.593)))

    else:
        ## Make the smaller bubble
        smallerTextBbox = inSmallerBubbleFont.getbbox(buttonText)
        smallerTextWidth = smallerTextBbox[2]-smallerTextBbox[0]
        smallerBubbleWidth = int(horizontal_small_padding+smallerTextWidth/render_factor+horizontal_small_padding)

        rendered_smallerBubbleWidth = int(smallerBubbleWidth*render_factor)

        image = Image.new("RGBA", (rendered_smallerBubbleWidth, rendered_bubble_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        draw.rounded_rectangle([(0,0), #bottom left point
                        (rendered_smallerBubbleWidth,rendered_bubble_height)], # Top right point
                        radius=(math.ceil(button_height/2))*render_factor,
                        fill = hex_to_rgb(colour_hex,alpha=1)
                        )
        smallerTextX = horizontal_small_padding*render_factor
        draw.text((smallerTextX,in_smaller_bubble_text_y),buttonText,font=inSmallerBubbleFont,fill=(*ImageColor.getrgb(f"#{colour_hex}"), int(255*0.593)))
    return(image)

def getTimeWithWidth(selected_font_path, timeFormat, find="max"):
    TestFont = ImageFont.truetype(selected_font_path, 100)
    stringsByActualSize = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "AM": 0, "PM": 0}
    
    # Calculate the width of each character by repeating it
    for n in stringsByActualSize.keys():
        numberMultiplier = 100
        stringsByActualSizeBbox = TestFont.getbbox(f"{str(n) * numberMultiplier}")
        stringsByActualSizeWidth = stringsByActualSizeBbox[2] - stringsByActualSizeBbox[0]
        stringsByActualSize[n] = stringsByActualSizeWidth
    
    # Sort by width to easily find min or max
    sortedStringsByActualSize = dict(sorted(stringsByActualSize.items(), key=lambda item: item[1]))
    
    # Set the criteria for finding the desired width based on `find` argument
    if find == "max":
        lastDigit = max((s for s in sortedStringsByActualSize if any(char.isdigit() for char in s)), key=sortedStringsByActualSize.get)
        secondLastDigit = max((s for s in sortedStringsByActualSize if s.isdigit() and int(s) < 6), key=sortedStringsByActualSize.get)
    elif find == "min":
        lastDigit = min((s for s in sortedStringsByActualSize if any(char.isdigit() for char in s)), key=sortedStringsByActualSize.get)
        secondLastDigit = min((s for s in sortedStringsByActualSize if s.isdigit() and int(s) < 6), key=sortedStringsByActualSize.get)
    else:
        raise ValueError("Invalid option for 'find'. Choose 'max' or 'min'.")

    firstDigits = None
    widthResult = 0 if find == "max" else float('inf')
    possibleFirstDigits = range(1, 13) if timeFormat == "12 Hour" else range(0, 24)
    
    # Adjust search logic for max or min width
    for n in possibleFirstDigits:
        currentString = str(n).zfill(2)
        digit1, digit2 = currentString[0], currentString[1]
        width1, width2 = sortedStringsByActualSize[digit1], sortedStringsByActualSize[digit2]
        currentWidth = width1 + width2
        
        if (find == "max" and currentWidth > widthResult) or (find == "min" and currentWidth < widthResult):
            widthResult = currentWidth
            firstDigits = currentString

    if timeFormat == "12 Hour":
        suffex = max((s for s in sortedStringsByActualSize if not any(char.isdigit() for char in s)), key=sortedStringsByActualSize.get) if find == "max" else \
                 min((s for s in sortedStringsByActualSize if not any(char.isdigit() for char in s)), key=sortedStringsByActualSize.get)
        timeText = f"{firstDigits}:{secondLastDigit}{lastDigit} {suffex}"
    else:
        timeText = f"{firstDigits}:{secondLastDigit}{lastDigit}"
    
    return timeText


def generateHeaderBubbles(config:Config,render_factor,accent_colour=None,bubble_alpha=0.133):
    image = Image.new("RGBA", (int(config.deviceScreenWidthVar)*render_factor, int(config.deviceScreenHeightVar)*render_factor), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    if accent_colour == None:
        accent_colour = config.deselectedFontHexVar

    if int(config.header_text_height_var) < 10:
        raise ValueError("Header Text Height Too Small!")
    elif int(config.header_text_height_var) > int(config.headerHeightVar):
        raise ValueError("Header Text Height Too Large!")
    else:
        heightOfText = int(int(config.header_text_height_var)*render_factor)

    fontHeight = int(int((heightOfText*(4/3))/render_factor)*render_factor) ## TODO Make this not specific to BPreplay
    headerFont = ImageFont.truetype(os.path.join(internal_files_dir,"Assets","Font","BPreplayBold-unhinted.otf"),fontHeight)
    
    if int(config.header_text_bubble_height_var) - int(config.header_text_height_var) >= 0:
        headerTextPadding = int((int(config.header_text_bubble_height_var)-int(config.header_text_height_var))/2)
    else:
        raise ValueError("Header Glyph Height Too Large!")

    headerMiddleY = ((int(config.headerHeightVar)*render_factor)/2)

    bottom_y_points = {}
    top_y_points = {}
    left_x_points = {}
    right_x_points = {}


    if config.show_clock_bubbles_var:
        clock_left_padding = int(config.clockHorizontalLeftPaddingVar)
        clock_right_padding = int(config.clockHorizontalRightPaddingVar)

        timeText = getTimeWithWidth(os.path.join(internal_files_dir,"Assets","Font","BPreplayBold-unhinted.otf"),config.clock_format_var,find="max")
        maxTimeTextWidth = headerFont.getbbox(timeText)[2] - headerFont.getbbox(timeText)[0]

        if config.clock_alignment_var == "Left":
            timeText_X = clock_left_padding*render_factor
        elif config.clock_alignment_var == "Centre":
            timeText_X = int((int(config.deviceScreenWidthVar)*render_factor)/2-((maxTimeTextWidth+(clock_right_padding*render_factor+clock_left_padding*render_factor))/2))+clock_left_padding*render_factor
        elif config.clock_alignment_var == "Right":
            timeText_X = int(int(config.deviceScreenWidthVar)*render_factor) - (maxTimeTextWidth + clock_right_padding*render_factor)
        else:
            raise ValueError("Invalid clock alignment")

        bottom_y_points["clock"] = headerMiddleY-((int(config.header_text_bubble_height_var)*render_factor)/2)
        top_y_points["clock"] = headerMiddleY+((int(config.header_text_bubble_height_var)*render_factor)/2)
        left_x_points["clock"] = timeText_X-(headerTextPadding*render_factor)
        right_x_points["clock"] = timeText_X+maxTimeTextWidth+(headerTextPadding*render_factor)

    if float(config.header_glyph_height_var) < 10:
        raise ValueError("Header Glyph Height Too Small!")
    elif float(config.header_glyph_height_var) > int(config.headerHeightVar):
        raise ValueError("Header Glyph Height Too Large!")
    else:
        heightOfGlyph = int(float(config.header_glyph_height_var)*render_factor)

    if int(config.header_glyph_bubble_height_var) - int(config.header_glyph_height_var) >= 0:
        headerGlyphPadding = int((int(config.header_glyph_bubble_height_var)-int(config.header_glyph_height_var))/2)
    else:
        raise ValueError("Header Glyph Height Too Large!")
    if config.show_glyphs_bubbles_var:

        #Battery not charging stuff
        capacityGlyph = "capacity_30.png"
        capacity_image_path = os.path.join(internal_files_dir,"Assets","glyphs",f"{capacityGlyph[:-4]}[5x].png")
        
        capacity_image_coloured = change_logo_color(capacity_image_path,accent_colour)
        capacity_image_coloured = capacity_image_coloured.resize((int(heightOfGlyph*(capacity_image_coloured.size[0]/capacity_image_coloured.size[1])),heightOfGlyph), Image.LANCZOS)
        glyph_left_side_padding = int(config.header_glyph_horizontal_left_padding_var)
        glyph_right_side_padding = int(config.header_glyph_horizontal_right_padding_var)
        glyph_between_padding = 5

        networkGlyph = "network_active"
        network_image_path = os.path.join(internal_files_dir,"Assets","glyphs",f"{networkGlyph}[5x].png")
        network_image_coloured = change_logo_color(network_image_path,accent_colour)
        network_image_coloured = network_image_coloured.resize((int(heightOfGlyph*(network_image_coloured.size[0]/network_image_coloured.size[1])),heightOfGlyph), Image.LANCZOS)

        glyphTotalWidth = (capacity_image_coloured.size[0] + glyph_between_padding*render_factor + network_image_coloured.size[0])
        

        if config.header_glyph_alignment_var == "Left":
            current_x_pos = glyph_left_side_padding*render_factor
        elif config.header_glyph_alignment_var == "Centre":
            current_x_pos = int((int(config.deviceScreenWidthVar)*render_factor)/2-((glyphTotalWidth+(glyph_right_side_padding*render_factor+glyph_left_side_padding*render_factor))/2))+glyph_left_side_padding*render_factor
        elif config.header_glyph_alignment_var == "Right":
            current_x_pos = int(int(config.deviceScreenWidthVar)*render_factor - (glyph_right_side_padding*render_factor + glyphTotalWidth))
        else:
            raise ValueError("Invalid clock alignment")

        glyphBubbleXPos = int(int(config.deviceScreenWidthVar)*render_factor) - (glyphTotalWidth + glyph_left_side_padding*render_factor)

        bottom_y_points["glyphs"] = headerMiddleY-((int(config.header_glyph_bubble_height_var)*render_factor)/2)
        top_y_points["glyphs"] = headerMiddleY+((int(config.header_glyph_bubble_height_var)*render_factor)/2)
        left_x_points["glyphs"] = current_x_pos-(headerGlyphPadding*render_factor)
        right_x_points["glyphs"] = current_x_pos+glyphTotalWidth+(headerGlyphPadding*render_factor)

    if config.join_header_bubbles_var and (config.show_glyphs_bubbles_var or config.show_clock_bubbles_var):
        bottom_y = min(bottom_y_points.values())
        top_y = max(top_y_points.values())
        left_x = min(left_x_points.values())
        right_x = max(right_x_points.values())

        draw.rounded_rectangle([(left_x,bottom_y), #bottom left point
                                (right_x,top_y)], # Top right point
                                radius=math.ceil((top_y-bottom_y)/2),
                                fill = hex_to_rgb(accent_colour,alpha=bubble_alpha)
                                )
    else:
        for key in bottom_y_points.keys():
            draw.rounded_rectangle([(left_x_points[key],bottom_y_points[key]), #bottom left point
                                    (right_x_points[key],top_y_points[key])], # Top right point
                                    radius=math.ceil((top_y_points[key]-bottom_y_points[key])/2),
                                    fill = hex_to_rgb(accent_colour,alpha=bubble_alpha)
                                    )
        
    return(image)


def generatePilImageMuOSOverlay(config:Config,muOSpageName,render_factor):
    muOSpageNameDict = {"muxlaunch":"MAIN MENU",
                        "muxconfig":"CONFIGURATION",
                        "muxinfo":"INFORMATION",
                        "muxapp":"APPLICATIONS",
                        "muxplore":"ROMS",
                        "muxcollect":"COLLECTIONS",
                        "muxhistory":"HISTORY"}
    current_time = datetime.now()
    image = Image.new("RGBA", (int(config.deviceScreenWidthVar)*render_factor, int(config.deviceScreenHeightVar)*render_factor), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    if float(config.header_glyph_height_var) < 10:
        raise ValueError("Header Glyph Height Too Small!")
    elif float(config.header_glyph_height_var) > int(config.headerHeightVar):
        raise ValueError("Header Glyph Height Too Large!")
    else:
        heightOfGlyph = int(float(config.header_glyph_height_var)*render_factor)
    accent_colour = config.deselectedFontHexVar
    if "showing battery and network":
        glyphYPos = int(((int(config.headerHeightVar)*render_factor)/2)-(heightOfGlyph/2))

        #Battery not charging stuff
        capacityGlyph = "30"
        capacity_image_path = os.path.join(internal_files_dir,"Assets","glyphs",f"{BatteryStyleOptionsDict[config.battery_style_var]}{capacityGlyph}[5x].png")
        
        capacity_image_coloured = change_logo_color(capacity_image_path,accent_colour)
        capacity_image_coloured = capacity_image_coloured.resize((int(heightOfGlyph*(capacity_image_coloured.size[0]/capacity_image_coloured.size[1])),heightOfGlyph), Image.LANCZOS)

        capacityChargingGlyph = "30"
        capacity_charging_image_path = os.path.join(internal_files_dir,"Assets","glyphs",f"{BatteryChargingStyleOptionsDict[config.battery_charging_style_var]}{capacityChargingGlyph}[5x].png")
        capacity_charging_image_coloured = change_logo_color(capacity_charging_image_path,config.batteryChargingHexVar)
        capacity_charging_image_coloured = capacity_charging_image_coloured.resize((int(heightOfGlyph*(capacity_charging_image_coloured.size[0]/capacity_charging_image_coloured.size[1])),heightOfGlyph), Image.LANCZOS)

        networkGlyph = "network_active"
        network_image_path = os.path.join(internal_files_dir,"Assets","glyphs",f"{networkGlyph}[5x].png")
        network_image_coloured = change_logo_color(network_image_path,accent_colour)
        network_image_coloured = network_image_coloured.resize((int(heightOfGlyph*(network_image_coloured.size[0]/network_image_coloured.size[1])),heightOfGlyph), Image.LANCZOS)


        glyph_left_side_padding = int(config.header_glyph_horizontal_left_padding_var)
        glyph_right_side_padding = int(config.header_glyph_horizontal_right_padding_var)
        glyph_between_padding = 5

        totalGlyphWidth = (capacity_image_coloured.size[0] + glyph_between_padding*render_factor + network_image_coloured.size[0])
        if config.header_glyph_alignment_var == "Left":
            current_x_pos = glyph_left_side_padding*render_factor
        elif config.header_glyph_alignment_var == "Centre":
            current_x_pos = int((int(config.deviceScreenWidthVar)*render_factor)/2-((totalGlyphWidth+(glyph_right_side_padding*render_factor+glyph_left_side_padding*render_factor))/2))+glyph_left_side_padding*render_factor
        elif config.header_glyph_alignment_var == "Right":
            current_x_pos = int(int(config.deviceScreenWidthVar)*render_factor - (glyph_right_side_padding*render_factor + totalGlyphWidth))
        else:
            raise ValueError("Invalid clock alignment")
        
        image.paste(network_image_coloured,(current_x_pos,glyphYPos),network_image_coloured)

        current_x_pos += network_image_coloured.size[0] + glyph_between_padding*render_factor

        if not config.show_charging_battery_var:
            image.paste(capacity_image_coloured,(current_x_pos,glyphYPos),capacity_image_coloured)

        if config.show_charging_battery_var:
            image.paste(capacity_charging_image_coloured,(current_x_pos,glyphYPos),capacity_charging_image_coloured)

        

        
    if int(config.header_text_height_var) < 10:
        raise ValueError("Header Text Height Too Small!")
    elif int(config.header_text_height_var) > int(config.headerHeightVar):
        raise ValueError("Header Text Height Too Large!")
    else:
        heightOfText = int(int(config.header_text_height_var)*render_factor)


    fontSize = int(int((heightOfText*(4/3))/render_factor)*render_factor) ## TODO Make this not specific to BPreplay
    headerFont = ImageFont.truetype(os.path.join(internal_files_dir,"Assets","Font","BPreplayBold-unhinted.otf"),fontSize)
    if "showing time":
        clock_left_padding = int(config.clockHorizontalLeftPaddingVar)
        clock_right_padding = int(config.clockHorizontalRightPaddingVar)
        
        if config.clock_format_var == "12 Hour":
            timeText = current_time.strftime("%I:%M %p")
        else:
            timeText = current_time.strftime("%H:%M")
        
        #timeText = getTimeWithWidth(os.path.join(internal_files_dir,"Assets","Font","BPreplayBold-unhinted.otf"),config.clock_format_var,find="max")
        #timeText = getTimeWithWidth(os.path.join(internal_files_dir,"Assets","Font","BPreplayBold-unhinted.otf"),config.clock_format_var,find="min")

        timeTextBbox = headerFont.getbbox(timeText)
        timeTextWidth = timeTextBbox[2] - timeTextBbox[0]
        if config.clock_alignment_var == "Left":
            timeText_X = clock_left_padding*render_factor
        elif config.clock_alignment_var == "Centre":
            timeText_X = int((int(config.deviceScreenWidthVar)*render_factor)/2-((timeTextWidth+(clock_right_padding*render_factor+clock_left_padding*render_factor))/2))+clock_left_padding*render_factor
        elif config.clock_alignment_var == "Right":
            timeText_X = int(int(config.deviceScreenWidthVar)*render_factor) - (timeTextWidth + clock_right_padding*render_factor)
        else:
            raise ValueError("Invalid clock alignment")
        timeText_Y = int(((int(config.headerHeightVar)*render_factor)/2)-(heightOfText/2))-timeTextBbox[1]
        draw.text((timeText_X,timeText_Y),timeText,font=headerFont,fill=(*ImageColor.getrgb(f"#{accent_colour}"), 255))
    if config.show_console_name_var:
        page_title_padding = int(config.pageTitlePaddingVar)
        pageTitle = muOSpageNameDict.get(muOSpageName, "UNKNOWN")
        pageTitleBbox = headerFont.getbbox(pageTitle)
        pageTitleWidth = pageTitleBbox[2] - pageTitleBbox[0]
        if config.page_title_alignment_var == "Left":
            pageTitle_X = page_title_padding*render_factor
        elif config.page_title_alignment_var == "Centre":
            pageTitle_X = int((int(config.deviceScreenWidthVar)*render_factor)/2-(pageTitleWidth/2))
        elif config.page_title_alignment_var == "Right":
            pageTitle_X = int(int(config.deviceScreenWidthVar)*render_factor) - (pageTitleWidth + page_title_padding*render_factor)
        else:
            raise ValueError("Invalid page title alignment")
        pageTitle_Y = int(((int(config.headerHeightVar)*render_factor)/2)-(heightOfText/2))-pageTitleBbox[1]
        draw.text((pageTitle_X,pageTitle_Y),pageTitle,font=headerFont,fill=(*ImageColor.getrgb(f"#{accent_colour}"), 255))

    return(image)


def generateGameSwitcherOverlay(config: Config, render_factor, gameNameForPreview=None, generatingForPreview=False):
    overlay = Image.new("RGBA", (int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    if os.path.exists(os.path.join(internal_files_dir, "Assets", "Game Screenshots", f"{gameNameForPreview}.png")):
        screenshot = Image.open(os.path.join(internal_files_dir, "Assets", "Game Screenshots", f"{gameNameForPreview}.png")).convert("RGBA").resize((int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor), Image.LANCZOS)
    else:
        screenshot = Image.new("RGBA", (int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor), (255, 255, 255, 0))
    
    bottom_bar_height_over_footer_percent = 0.1
    bottom_bar_height_over_footer = int((int(config.deviceScreenHeightVar) * bottom_bar_height_over_footer_percent) * render_factor)
    bottom_bar_total_height = int(getRealFooterHeight(config) * render_factor) + bottom_bar_height_over_footer

    # Draw a rectangle at the bottom of the screen here
    draw.rectangle([(0, (int(config.deviceScreenHeightVar) * render_factor) - bottom_bar_total_height),  # bottom left point
                    (int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor)],  # Top right point
                   fill=hex_to_rgb(config.bgHexVar, alpha=0.866))
    if not "dont Draw upper rectangle for testing":
        # Draw a rectangle at the bottom of the screen here
        draw.rectangle([(0, (int(config.deviceScreenHeightVar) * render_factor) - (bottom_bar_total_height)),  # top left point
                        (int(config.deviceScreenWidthVar) * render_factor, (int(config.deviceScreenHeightVar) * render_factor)-(bottom_bar_total_height-bottom_bar_height_over_footer))],  # Top right point
                    fill=hex_to_rgb("ff0000", alpha=0.866))

    menuHelperGuide = generateMenuHelperGuides([["A", "OKAY"], ["B", "BACK"]], os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf"), config.deselectedFontHexVar, render_factor, config)
    overlay = Image.alpha_composite(overlay, menuHelperGuide)

    headerBubbles = generateHeaderBubbles(config, render_factor,accent_colour=config.bgHexVar,bubble_alpha=0.866)
    overlay = Image.alpha_composite(overlay, headerBubbles)
    

        
    if generatingForPreview:
        screenshot = Image.alpha_composite(screenshot, overlay)

        fontSize = bottom_bar_height_over_footer * 0.55
        fontSize = int(fontSize/render_factor)
        fontSize = fontSize*render_factor
        bottomBarFont = ImageFont.truetype(os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf"), fontSize)
        bottomBarText = gameNameForPreview

        # Generate other overlays first
        muOSOverlay = generatePilImageMuOSOverlay(config, "Recently Played", render_factor)
        screenshot = Image.alpha_composite(screenshot, muOSOverlay)
        drawScreenshot = ImageDraw.Draw(screenshot)

        # Now, draw the game name text on the final composite overlay
        bottomBarTextBbox = bottomBarFont.getbbox(bottomBarText)
        bottomBarTextWidth = bottomBarTextBbox[2] - bottomBarTextBbox[0]
        bottomBarText_X = int((int(config.deviceScreenWidthVar) * render_factor) / 2 - (bottomBarTextWidth / 2))
        bottomBarText_Y = (int(config.deviceScreenHeightVar) * render_factor) - (bottom_bar_total_height-(bottom_bar_height_over_footer/2))
        bottomBarText_Y = bottomBarText_Y - (bottomBarTextBbox[1] + bottomBarTextBbox[3]) / 2
        drawScreenshot.text((bottomBarText_X, bottomBarText_Y), bottomBarText, font=bottomBarFont, fill=(*ImageColor.getrgb(f"#{config.deselectedFontHexVar}"), 255))


        # Final composite with screenshot
        return screenshot
    if "showing game screenshot":
        screenshot = Image.alpha_composite(screenshot, overlay)
        return screenshot
    


    return overlay

def getRealFooterHeight(config:Config) -> int:
    individualItemHeight = round((int(config.deviceScreenHeightVar)-int(config.approxFooterHeightVar)-int(config.contentPaddingTopVar))/int(config.itemsPerScreenVar))
    footerHeight = int(config.deviceScreenHeightVar)-(individualItemHeight*int(config.itemsPerScreenVar))-int(config.contentPaddingTopVar)
    return(footerHeight)

def generateMenuHelperGuides(retro_rhs_buttons,selected_font_path,colour_hex,render_factor,config:Config,lhsButtons=[["POWER","SLEEP"]]):
    image = Image.new("RGBA", (int(config.deviceScreenWidthVar)*render_factor, int(config.deviceScreenHeightVar)*render_factor), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    real_rhs_buttons = []
    
    if config.muos_button_swap_var == "Modern":
        for pair in retro_rhs_buttons:
            if pair[0].upper() == "A":
                real_rhs_buttons.append(["B",pair[1]])
            elif pair[0].upper() == "B":
                real_rhs_buttons.append(["A",pair[1]])
            elif pair[0].upper() == "X":
                real_rhs_buttons.append(["Y",pair[1]])
            elif pair[0].upper() == "Y":
                real_rhs_buttons.append(["X",pair[1]])
    else:
        real_rhs_buttons = retro_rhs_buttons

    if not( config.remove_left_menu_guides_var and config.remove_right_menu_guides_var):
        required_padding_between_sides=15 # This is the maximum space between the two sides of the menu helper guides
        lhsTotalWidth = 0
        rhsTotalWidth = int(config.deviceScreenWidthVar)
        iterations = 0
        from_sides_padding = int(config.VBG_Horizontal_Padding_entry)
        remove_left_menu_guides_var = config.remove_left_menu_guides_var
        remove_right_menu_guides_var = config.remove_right_menu_guides_var
        if remove_left_menu_guides_var or remove_right_menu_guides_var:
            required_padding_between_sides = 0
        while from_sides_padding+lhsTotalWidth+required_padding_between_sides+rhsTotalWidth+from_sides_padding>int(config.deviceScreenWidthVar):
            if iterations==0:
                from_sides_padding = int(config.VBG_Horizontal_Padding_entry)
            if False: # TODO an option for this
                remove_left_menu_guides_var = True
                required_padding_between_sides = 0
            from_bottom_padding = int(config.VBG_Vertical_Padding_entry)+iterations

            individualItemHeight = round((int(config.deviceScreenHeightVar)-int(config.approxFooterHeightVar)-int(config.contentPaddingTopVar))/int(config.itemsPerScreenVar))

            muosSpaceBetweenItems = 2

            footerHeight = int(config.deviceScreenHeightVar)-(individualItemHeight*int(config.itemsPerScreenVar))-int(config.contentPaddingTopVar)+muosSpaceBetweenItems

            menu_helper_guide_height = footerHeight-(from_bottom_padding*2) # Change this if overlayed

            in_smaller_bubble_font_size = menu_helper_guide_height*(20.1/60)*render_factor
            inSmallerBubbleFont = ImageFont.truetype(selected_font_path, in_smaller_bubble_font_size)

            in_bubble_font_size = menu_helper_guide_height*(24/60)*render_factor
            inBubbleFont = ImageFont.truetype(selected_font_path, in_bubble_font_size)

            single_letter_font_size = menu_helper_guide_height*(28/60)*render_factor
            singleLetterFont = ImageFont.truetype(selected_font_path, single_letter_font_size)

            horizontal_small_padding = menu_helper_guide_height*(10/60)
            horizontal_padding = menu_helper_guide_height*(10/60)
            horizontal_large_padding = menu_helper_guide_height*(20/60) # Testing here
            
            bottom_guide_middle_y = int(config.deviceScreenHeightVar)-from_bottom_padding-(menu_helper_guide_height/2)

            guide_small_bubble_height = menu_helper_guide_height-(horizontal_padding*2)

            isb_ascent, isb_descent = inSmallerBubbleFont.getmetrics()
            isb_text_height = isb_ascent + isb_descent
            in_smaller_bubble_text_y = bottom_guide_middle_y*render_factor - (isb_text_height / 2)

            ib_ascent, ib_descent = inBubbleFont.getmetrics()
            ib_text_height = ib_ascent + ib_descent
            in_bubble_text_y = bottom_guide_middle_y*render_factor - (ib_text_height / 2)

            sl_text_bbox = singleLetterFont.getbbox("ABXY")
            sl_text_height = sl_text_bbox[3]-sl_text_bbox[1]
            single_letter_text_y = bottom_guide_middle_y*render_factor - (sl_text_height / 2)-sl_text_bbox[1]

            ##TODO convert buttons at this point to lanuage of choice in their respective arrays

            combined_width = 0
            lhsTotalWidth=0
            rhsTotalWidth=0

            if not remove_left_menu_guides_var:
                lhsTotalWidth += getTotalBubbleWidth(lhsButtons,inSmallerBubbleFont,inBubbleFont,horizontal_padding,horizontal_large_padding,horizontal_small_padding,guide_small_bubble_height,render_factor)
                combined_width += lhsTotalWidth

            if not remove_right_menu_guides_var:
                rhsTotalWidth += getTotalBubbleWidth(real_rhs_buttons,inSmallerBubbleFont,inBubbleFont,horizontal_padding,horizontal_large_padding,horizontal_small_padding,guide_small_bubble_height,render_factor)
                combined_width += rhsTotalWidth
            iterations +=1

        if not remove_left_menu_guides_var:
            realLhsPointer = from_sides_padding*render_factor
            ## Make the main long bubble
            draw.rounded_rectangle([(realLhsPointer,(bottom_guide_middle_y-menu_helper_guide_height/2)*render_factor), #bottom left point
                                    (realLhsPointer+(lhsTotalWidth*render_factor),(bottom_guide_middle_y+menu_helper_guide_height/2)*render_factor)], # Top right point
                                    radius=(menu_helper_guide_height/2)*render_factor,
                                    fill = hex_to_rgb(colour_hex,alpha=0.133)
                                    )
            realLhsPointer+=horizontal_padding*render_factor
            for pair in lhsButtons:
                button_image = generateIndividualButtonGlyph(pair[0],selected_font_path,colour_hex,render_factor, guide_small_bubble_height, config.physical_controler_layout_var)
                button_image = change_logo_color(button_image, colour_hex)
                image.paste(button_image,(int(realLhsPointer),int(bottom_guide_middle_y*render_factor-(button_image.size[1]/2))),button_image)
                realLhsPointer+=(button_image.size[0])+(horizontal_small_padding)*render_factor

                textBbox = inBubbleFont.getbbox(pair[1])
                textWidth = textBbox[2]-textBbox[0]
                draw.text((realLhsPointer,in_bubble_text_y),pair[1],font=inBubbleFont,fill=f"#{colour_hex}")
                realLhsPointer+=textWidth
                realLhsPointer += horizontal_large_padding*render_factor
        if not remove_right_menu_guides_var:
            realRhsPointer = (int(config.deviceScreenWidthVar)-from_sides_padding-rhsTotalWidth)*render_factor
            ## Make the main long bubble
            draw.rounded_rectangle([(realRhsPointer,(bottom_guide_middle_y-menu_helper_guide_height/2)*render_factor), #bottom left point
                                    (realRhsPointer+(rhsTotalWidth*render_factor),(bottom_guide_middle_y+menu_helper_guide_height/2)*render_factor)], # Top right point
                                    radius=(menu_helper_guide_height/2)*render_factor,
                                    fill = hex_to_rgb(colour_hex,alpha=0.133)
                                    )
            realRhsPointer+=horizontal_padding*render_factor
            for pair in real_rhs_buttons:
                
                button_image = generateIndividualButtonGlyph(pair[0],selected_font_path,colour_hex,render_factor, guide_small_bubble_height, config.physical_controler_layout_var)
                button_image = change_logo_color(button_image, colour_hex)
                    
                image.paste(button_image,(int(realRhsPointer),int(bottom_guide_middle_y*render_factor-(button_image.size[1]/2))),button_image)
                realRhsPointer+=(button_image.size[0])+(horizontal_small_padding)*render_factor

                textBbox = inBubbleFont.getbbox(pair[1])
                textWidth = textBbox[2]-textBbox[0]
                draw.text((realRhsPointer,in_bubble_text_y),pair[1],font=inBubbleFont,fill=f"#{colour_hex}")
                realRhsPointer+=textWidth
                realRhsPointer += horizontal_large_padding*render_factor
    return(image)

def generateMuOSBackgroundOverlay(rhsButtons,selected_font_path,colour_hex,render_factor,config:Config,lhsButtons=[["POWER","SLEEP"]]):
    image = Image.new("RGBA", (int(config.deviceScreenWidthVar)*render_factor, int(config.deviceScreenHeightVar)*render_factor), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    menuHelperGuides = generateMenuHelperGuides(rhsButtons,selected_font_path,colour_hex,render_factor,config,lhsButtons=lhsButtons)

    image = Image.alpha_composite(image,menuHelperGuides)
    headerBubbles = generateHeaderBubbles(config,render_factor)

    image = Image.alpha_composite(image,headerBubbles)

    return(image)

def getTotalBubbleWidth(buttons,internalBubbleFont,bubbleFont,initalPadding,largerPadding,smallerPadding,circleWidth,render_factor):
    totalWidth = initalPadding
    for pair in buttons:
        #pair[0] might be MENU, POWER, or ABXY
        if len(pair[0]) == 1:
            totalWidth+=circleWidth
        else:
            totalWidth+=smallerPadding
            smallerTextBbox = internalBubbleFont.getbbox(pair[0])
            smallerTextWidth = smallerTextBbox[2]-smallerTextBbox[0]
            totalWidth+=(smallerTextWidth/render_factor)
            totalWidth+=smallerPadding
        totalWidth+=smallerPadding
        #pair[1] might be something like INFO, COLLECT, REFRESH etc...
        textBbox = bubbleFont.getbbox(pair[1])
        textWidth = textBbox[2]-textBbox[0]
        totalWidth += (textWidth/render_factor)
        totalWidth+=largerPadding
    return(totalWidth)


def generatePilImageVertical(progress_bar,workingIndex, muOSSystemName,listItems,textPadding, rectanglePadding, ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor,config:Config,numScreens=0,screenIndex=0,fileCounter="",folderName = None,transparent=False, forPreview=False):
    progress_bar['value'] +=1
    bg_rgb = hex_to_rgb(bg_hex)
    if not transparent:
        image = Image.new("RGBA", (int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor), bg_rgb)

        if background_image != None:
            image.paste(background_image.resize((int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor)), (0,0))
    else:
        image = Image.new("RGBA", (int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor), (0,0,0,0))

    draw = ImageDraw.Draw(image)   

    boxArtDrawn = False
    boxArtWidth = 0
    if len(listItems) == 0:
        return(image)
    if not config.use_alt_font_var:
        selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    else:
        if os.path.exists(config.alt_font_path):
            selected_font_path = config.alt_font_path
        else:
            selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")

    if muOSSystemName == "muxlaunch":
        menuHelperGuides = generateMenuHelperGuides([["A", "SELECT"]],selected_font_path,config.footerBubbleHexVar,render_factor,config,lhsButtons=[["POWER","SLEEP"]])
    elif muOSSystemName == "muxconfig" or muOSSystemName == "muxinfo":
        menuHelperGuides = generateMenuHelperGuides([["B", "BACK"],["A", "SELECT"]],selected_font_path,config.footerBubbleHexVar,render_factor,config,lhsButtons=[["POWER","SLEEP"]])
    elif muOSSystemName == "muxapp":
        menuHelperGuides = generateMenuHelperGuides([["B", "BACK"],["A", "LAUNCH"]],selected_font_path,config.footerBubbleHexVar,render_factor,config,lhsButtons=[["POWER","SLEEP"]])
    elif muOSSystemName == "muxplore":
        menuHelperGuides = generateMenuHelperGuides([["MENU", "INFO"],["Y", "COLLECT"],["X", "REFRESH"],["B", "BACK"],["A", "OPEN"]],selected_font_path,config.footerBubbleHexVar,render_factor,config,lhsButtons=[["POWER","SLEEP"]])
    elif muOSSystemName == "muxcollect":
        menuHelperGuides = generateMenuHelperGuides([["MENU", "INFO"],["X", "REMOVE"],["B", "BACK"],["A", "OPEN"]],selected_font_path,config.footerBubbleHexVar,render_factor,config,lhsButtons=[["POWER","SLEEP"]])
    elif muOSSystemName == "muxhistory":
        menuHelperGuides = generateMenuHelperGuides([["MENU", "INFO"],["Y", "COLLECT"],["X", "REMOVE"],["B", "BACK"],["A", "OPEN"]],selected_font_path,config.footerBubbleHexVar,render_factor,config,lhsButtons=[["POWER","SLEEP"]])

    if config.show_file_counter_var == 1:
        in_bubble_font_size = 19*render_factor
        inBubbleFont = ImageFont.truetype(selected_font_path, in_bubble_font_size)
        bbox = inBubbleFont.getbbox(fileCounter)
        text_width = bbox[2] - bbox[0]
        right_aligned_position = 620 * render_factor
        x = right_aligned_position - text_width
        y = 447 * render_factor
        draw.text(( x, y ), fileCounter, font=inBubbleFont, fill=f"#{bubble_hex}")    
    

    textAlignment = None
    individualItemHeight = round((int(config.deviceScreenHeightVar)-int(config.approxFooterHeightVar)-int(config.contentPaddingTopVar))/int(config.itemsPerScreenVar))

    if muOSSystemName.startswith("mux"):
        textAlignment = config.global_alignment_var
    else:
        textAlignment = config.global_alignment_var

    try:
        font_size = int(config.custom_font_size_entry) * render_factor
    except:
        font_size = int(individualItemHeight * render_factor * textMF)
    
    font = ImageFont.truetype(selected_font_path, font_size)
    

    availableHeight = ((individualItemHeight*int(config.itemsPerScreenVar)) * render_factor) / ItemsPerScreen

    smallestValidText_bbox = font.getbbox("_...")
    smallestValidTest_width = smallestValidText_bbox[2] - smallestValidText_bbox[0]

    for index, item in enumerate(listItems):
        noLettersCut = 0
        text_width = float('inf')
        if config.alternate_menu_names_var and muOSSystemName.startswith("mux"):
            text = bidi_get_display(menuNameMap.get(item[0][:].lower(),item[0][:]))
        else:
            text = item[0][:]
        text_color = f"#{selected_font_hex}" if index == workingIndex else f"#{deselected_font_hex}"
        maxBubbleLength = int(config.deviceScreenWidthVar)-int(config.maxBoxArtWidth)
        if maxBubbleLength*render_factor < textPadding*render_factor+smallestValidTest_width+rectanglePadding*render_factor+5*render_factor: #Make sure there won't be a bubble error
            maxBubbleLength = int(config.deviceScreenWidthVar)

        if workingIndex == index:
            totalCurrentLength = (textPadding * render_factor + text_width + rectanglePadding * render_factor)
        else:
            totalCurrentLength = (textPadding * render_factor + text_width)
        while totalCurrentLength > (int(maxBubbleLength)*render_factor):
            if config.alternate_menu_names_var and muOSSystemName.startswith("mux"):
                text = bidi_get_display(menuNameMap.get(item[0][:].lower(),item[0][:]))
            else:
                text = item[0][:]
            if noLettersCut>0:
                text = text[:-(noLettersCut+3)]
                text = text+"..."
            
            text_bbox = font.getbbox(text)
            text_width = text_bbox[2] - text_bbox[0]
            if workingIndex == index:
                totalCurrentLength = (textPadding * render_factor + text_width + rectanglePadding * render_factor)
            else:
                totalCurrentLength = (textPadding * render_factor + text_width)
            noLettersCut +=1
            if text  == "...":
                raise ValueError("'Cut bubble off at' too low\n\nPlease use a different custom 'cut bubble off' at value")
        
        if textAlignment == "Left":
            text_x = textPadding * render_factor
        elif textAlignment == "Right":
            text_x = (int(config.deviceScreenWidthVar)-textPadding) * render_factor-text_width
        elif textAlignment == "Centre":
            text_x = ((int(config.deviceScreenWidthVar)* render_factor-text_width)/2) 
        #text_y = contentPaddingTop * render_factor + availableHeight * index

        
        rectangle_x0 = text_x - (rectanglePadding * render_factor)
        rectangle_y0 = contentPaddingTop * render_factor + availableHeight * index
        rectangle_x1 = rectangle_x0 + rectanglePadding * render_factor + text_width + rectanglePadding * render_factor
        rectangle_y1 = contentPaddingTop * render_factor + availableHeight * (index+1)
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
                fill=f"#{bubble_hex}"
            )   
        draw.text((text_x, text_y), text, font=font, fill=text_color)
            
    
    if (muOSSystemName == "muxdevice" or muOSSystemName == "muxlaunch" or muOSSystemName == "muxconfig" or muOSSystemName == "muxinfo" or muOSSystemName == "muxapp" or muOSSystemName == "muxplore" or muOSSystemName == "muxcollect" or muOSSystemName == "muxhistory"):
        image = Image.alpha_composite(image, menuHelperGuides)
    
    headerBubbles = generateHeaderBubbles(config,render_factor)
    image = Image.alpha_composite(image, headerBubbles)

    if forPreview:
        muOSOverlay = generatePilImageMuOSOverlay(config,muOSSystemName,render_factor)
        image = Image.alpha_composite(image, muOSOverlay)
    return(image)


def ContinuousFolderImageGen(progress_bar,muOSSystemName, listItems, textPadding, rectanglePadding, ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, outputDir,config:Config, folderName = None, threadNumber = 0):
    totalItems = len(listItems)
    for workingIndex, workingItem in enumerate(listItems):
        
        if workingItem[1] == "Directory" or workingItem[1] == "Menu":

            # Load the base image
            midIndexOfList = int((ItemsPerScreen-1)/2)
            if totalItems > ItemsPerScreen:
                if workingIndex < midIndexOfList:
                    startIndex = 0
                    focusIndex = workingIndex
                elif workingIndex > (totalItems- ItemsPerScreen)+midIndexOfList:
                    startIndex = totalItems - ItemsPerScreen
                    focusIndex = ItemsPerScreen-(totalItems-(workingIndex+1))-1
                else:
                    startIndex = workingIndex-midIndexOfList
                    focusIndex = midIndexOfList
                endIndex = min(startIndex+ItemsPerScreen,totalItems)
            else:
                startIndex = 0
                endIndex = totalItems
                focusIndex= workingIndex
            fileCounter = str(workingIndex + 1) + " / " + str(totalItems)

            image = generatePilImageVertical(progress_bar,
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
                                             config,
                                             fileCounter=fileCounter,
                                             folderName = folderName,transparent=True)
            image = image.resize((int(config.deviceScreenWidthVar), int(config.deviceScreenHeightVar)), Image.LANCZOS)
            if workingItem[1] == "File":
                directory = os.path.dirname(f"{outputDir}/{muOSSystemName}/box/{workingItem[2]}.png")
                if not os.path.exists(directory):
                    os.makedirs(directory)
                image.save(f"{outputDir}/{muOSSystemName}/box/{workingItem[2]}.png")
            elif workingItem[1] == "Directory":
                directory = os.path.dirname(f"{outputDir}/Folder/box/{workingItem[2]}.png")
                if not os.path.exists(directory):
                    os.makedirs(directory)
                image.save(f"{outputDir}/Folder/box/{workingItem[2]}.png")

def resize_system_logos(system_logos_path, output_system_logos_path,grid_cell_size,grid_image_padding,circular_grid):
    system_logos = os.listdir(system_logos_path)
    if circular_grid:
        effective_circle_diameter = grid_cell_size-(grid_image_padding*2)
    else:
        effective_grid_size = grid_cell_size-(grid_image_padding*2)
    for system_logo in system_logos:
        if system_logo.endswith(".png"):
            system_logo_path = os.path.join(system_logos_path, system_logo)
            system_logo_image = Image.open(system_logo_path).convert("RGBA")
            if circular_grid:
                old_size = system_logo_image.size
                aspect_ratio = old_size[0]/old_size[1]
                new_height = math.sqrt(math.pow(effective_circle_diameter,2)/(1+math.pow(aspect_ratio,2)))
                new_size = int(new_height*aspect_ratio),int(new_height)
            else:
                width_multiplier = effective_grid_size/system_logo_image.size[0]
                height_multiplier = effective_grid_size/system_logo_image.size[1]
                multiplier = min(width_multiplier,height_multiplier)
                new_size = int(system_logo_image.size[0]*multiplier),int(system_logo_image.size[1]*multiplier)
            system_logo_image = system_logo_image.resize(new_size, Image.LANCZOS)
            system_logo_image.save(os.path.join(output_system_logos_path, system_logo)) 

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
    logo_mask = logo_mask[:y_end-y, :x_end-x]
    logo_alpha = logo_array[:y_end-y, :x_end-x, 3] / 255.0
    
    # Cut out the region of the original image where the logo is not transparent
    original_array[y:y_end, x:x_end, 3] = np.where(logo_mask, 
                                                   original_array[y:y_end, x:x_end, 3] * (1 - logo_alpha), 
                                                   original_array[y:y_end, x:x_end, 3])
    
    # Convert the modified NumPy array back to a Pillow image
    edited_image = Image.fromarray(original_array.astype('uint8'), 'RGBA')
    
    # Return the edited image
    return edited_image

def getHorizontalLogoSize(path_to_logo, render_factor, config:Config):
    exploreLogoColoured = change_logo_color(path_to_logo,config.iconHexVar)
    top_logo_size = (int((exploreLogoColoured.size[0]*render_factor*min(int(config.deviceScreenHeightVar)/480,int(config.deviceScreenWidthVar)/640))/5),
                     int((exploreLogoColoured.size[1]*render_factor*min(int(config.deviceScreenHeightVar)/480,int(config.deviceScreenWidthVar)/640))/5))
    return(top_logo_size)
    

def generatePilImageHorizontal(progress_bar,workingIndex, bg_hex, selected_font_hex,deselected_font_hex, bubble_hex,icon_hex,render_factor,config:Config,transparent=False,forPreview=False, generateText = True):
    progress_bar['value']+=1
    bg_rgb = hex_to_rgb(bg_hex)

    # Create image

    if not transparent:
        image = Image.new("RGBA", (int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor), bg_rgb)

        if background_image != None:
            image.paste(background_image.resize((int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor)), (0,0))
    else:
        image = Image.new("RGBA", (int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor), (0,0,0,0))


    

    exploreLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "explore.png"),icon_hex)
    collectionLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "collection.png"),icon_hex)
    historyLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "history.png"),icon_hex)
    appsLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "apps.png"),icon_hex)
   
    top_logo_size = getHorizontalLogoSize(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "explore.png"), render_factor, config)
    
    exploreLogoColoured = exploreLogoColoured.resize((top_logo_size), Image.LANCZOS)
    collectionLogoColoured = collectionLogoColoured.resize((top_logo_size), Image.LANCZOS)
    historyLogoColoured = historyLogoColoured.resize((top_logo_size), Image.LANCZOS)
    appsLogoColoured = appsLogoColoured.resize((top_logo_size), Image.LANCZOS)
    
    combined_top_logos_width = exploreLogoColoured.size[0]+collectionLogoColoured.size[0]+historyLogoColoured.size[0]+appsLogoColoured.size[0]

    icons_to_bubble_padding = min((int(config.deviceScreenHeightVar)*0)/480,(int(config.deviceScreenWidthVar)*0)/640)*render_factor ## CHANGE for adjustment

    bubble_height = min((int(config.deviceScreenHeightVar)*36.3)/480,(int(config.deviceScreenWidthVar)*36.3)/640)*render_factor ## CHANGE for adjustment

    screen_y_middle = (int(config.deviceScreenHeightVar)*render_factor)/2

    combined_top_row_height = max(exploreLogoColoured.size[1],collectionLogoColoured.size[1],historyLogoColoured.size[1],appsLogoColoured.size[1])+icons_to_bubble_padding+bubble_height

    top_row_icon_y = int(screen_y_middle-(combined_top_row_height/2))

    top_row_bubble_middle = int(screen_y_middle+(combined_top_row_height/2)-(bubble_height)/2)

    padding_between_top_logos = (int(config.deviceScreenWidthVar)*render_factor-combined_top_logos_width)/(4+1) # 4 logos plus 1

    explore_middle = int(padding_between_top_logos+(exploreLogoColoured.size[0])/2)
    collection_middle = int(padding_between_top_logos+collectionLogoColoured.size[0]+padding_between_top_logos+(collectionLogoColoured.size[0])/2)
    history_middle = int(padding_between_top_logos+historyLogoColoured.size[0]+padding_between_top_logos+collectionLogoColoured.size[0]+padding_between_top_logos+(historyLogoColoured.size[0])/2)
    apps_middle = int(padding_between_top_logos+appsLogoColoured.size[0]+padding_between_top_logos+collectionLogoColoured.size[0]+padding_between_top_logos+historyLogoColoured.size[0]+padding_between_top_logos+(appsLogoColoured.size[0])/2)

    explore_logo_x = int(explore_middle-(exploreLogoColoured.size[0])/2)
    collection_logo_x = int(collection_middle-(collectionLogoColoured.size[0])/2)
    history_logo_x = int(history_middle-(historyLogoColoured.size[0])/2)
    apps_logo_x = int(apps_middle-(appsLogoColoured.size[0])/2)

    image.paste(exploreLogoColoured,(explore_logo_x,top_row_icon_y),exploreLogoColoured)
    image.paste(collectionLogoColoured,(collection_logo_x,top_row_icon_y),collectionLogoColoured)
    image.paste(historyLogoColoured,(history_logo_x,top_row_icon_y),historyLogoColoured)
    image.paste(appsLogoColoured,(apps_logo_x,top_row_icon_y),appsLogoColoured)

    draw = ImageDraw.Draw(image)
    if config.transparent_text_var:
        transparent_text_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw_transparent = ImageDraw.Draw(transparent_text_image)
        transparency = 0

    if not config.use_alt_font_var:
        selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    else:
        if os.path.exists(config.alt_font_path):
            selected_font_path = config.alt_font_path
        else:
            selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    menuHelperGuides = generateMenuHelperGuides([["A", "SELECT"]],selected_font_path,config.footerBubbleHexVar,render_factor,config,lhsButtons=[["POWER","SLEEP"]])
    
    

    font_size = min((int(config.deviceScreenHeightVar)*24)/480,(int(config.deviceScreenWidthVar)*24)/640) * render_factor  ## CHANGE for adjustment
    font = ImageFont.truetype(selected_font_path, font_size)
    if workingIndex == 0:
        current_x_midpoint = explore_middle
    elif workingIndex == 1:
        current_x_midpoint = collection_middle
    elif workingIndex == 2:
        current_x_midpoint = history_middle
    elif workingIndex == 3:
        current_x_midpoint = apps_middle
    else:
        current_x_midpoint = 104+(144*workingIndex)
    betweenBubblePadding=5*render_factor
    maxBubbleLength = int((((int(config.deviceScreenWidthVar)*render_factor)-padding_between_top_logos)/4)-betweenBubblePadding/2)

    

    horizontalBubblePadding = min((int(config.deviceScreenHeightVar)*40)/480,(int(config.deviceScreenWidthVar)*40)/640)*render_factor  ## CHANGE for adjustment
    
    if config.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("content explorer", "Content"))
    else:
        textString = "Content"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    ascent, descent = font.getmetrics()
    text_height = ascent + descent

    text_y = top_row_bubble_middle - (text_height / 2)


    bubble_centre_x =  explore_middle
    textColour = selected_font_hex if workingIndex == 0 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 0 :
        if generateText:
            bubbleLength = text_width+horizontalBubblePadding
        else:
            bubbleLength = maxBubbleLength
        if config.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int(top_row_bubble_middle-bubble_height/2)), ((current_x_midpoint+(bubbleLength/2)), int(top_row_bubble_middle+bubble_height/2))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
        else:
            draw.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int(top_row_bubble_middle-bubble_height/2)), ((current_x_midpoint+(bubbleLength/2)), int(top_row_bubble_middle+bubble_height/2))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
    if generateText:
        if config.transparent_text_var and workingIndex == 0:
            draw_transparent.text((text_x, text_y), textString, font=font, fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency))
        else:
            draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")
    
    if config.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("collections", "Collections"))
    else:
        textString = "Collections"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    bubble_centre_x =  collection_middle
    textColour = selected_font_hex if workingIndex == 1 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 1 :
        if generateText:
            bubbleLength = text_width+horizontalBubblePadding
        else:
            bubbleLength = maxBubbleLength
        if config.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int(top_row_bubble_middle-bubble_height/2)), ((current_x_midpoint+(bubbleLength/2)), int(top_row_bubble_middle+bubble_height/2))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
        else:
            draw.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int(top_row_bubble_middle-bubble_height/2)), ((current_x_midpoint+(bubbleLength/2)), int(top_row_bubble_middle+bubble_height/2))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
    if generateText:
        if config.transparent_text_var and workingIndex == 1:
            draw_transparent.text((text_x, text_y), textString, font=font, fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency))
        else:
            draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    if config.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("history", "History"))
    else:
        textString = "History"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    bubble_centre_x =  history_middle
    textColour = selected_font_hex if workingIndex == 2 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 2 :
        if generateText:
            bubbleLength = text_width+horizontalBubblePadding
        else:
            bubbleLength = maxBubbleLength
        if config.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int((top_row_bubble_middle-bubble_height/2))), ((current_x_midpoint+(bubbleLength/2)), int((top_row_bubble_middle+bubble_height/2)))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
        else:
            draw.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int((top_row_bubble_middle-bubble_height/2))), ((current_x_midpoint+(bubbleLength/2)), int((top_row_bubble_middle+bubble_height/2)))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
    if generateText:
        if config.transparent_text_var and workingIndex == 2:
            draw_transparent.text((text_x, text_y), textString, font=font, fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency))
        else:
            draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")
    if config.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("applications", "Utilities"))
    else:
        textString = "Utilities"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    bubble_centre_x =  apps_middle
    textColour = selected_font_hex if workingIndex == 3 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 3 :
        if generateText:
            bubbleLength = text_width+horizontalBubblePadding
        else:
            bubbleLength = maxBubbleLength
        if config.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int((top_row_bubble_middle-bubble_height/2))), ((current_x_midpoint+(bubbleLength/2)), int((top_row_bubble_middle+bubble_height/2)))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
        else:
            draw.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int((top_row_bubble_middle-bubble_height/2))), ((current_x_midpoint+(bubbleLength/2)), int((top_row_bubble_middle+bubble_height/2)))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
    if generateText:
        if config.transparent_text_var and workingIndex == 3:
            draw_transparent.text((text_x, text_y), textString, font=font, fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency))
        else:
            draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    

    if workingIndex == 4:
        infoLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "info.png"),selected_font_hex)
    else:
        infoLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "info.png"),deselected_font_hex)
    if workingIndex == 5:
        configLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "config.png"),selected_font_hex)
    else:
        configLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "config.png"),deselected_font_hex)
    if workingIndex == 6:
        rebootLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "reboot.png"),selected_font_hex)
    else:
        rebootLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "reboot.png"),deselected_font_hex)
    if workingIndex == 7:
        shutdownLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "shutdown.png"),selected_font_hex)
    else:
        shutdownLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "shutdown.png"),deselected_font_hex)
    
    bottom_logo_size = (int((infoLogoColoured.size[0]*render_factor*min(int(config.deviceScreenHeightVar)/480,int(config.deviceScreenWidthVar)/640))/5),
                     int((infoLogoColoured.size[1]*render_factor*min(int(config.deviceScreenHeightVar)/480,int(config.deviceScreenWidthVar)/640))/5))
    
    infoLogoColoured = infoLogoColoured.resize(bottom_logo_size, Image.LANCZOS)
    configLogoColoured = configLogoColoured.resize(bottom_logo_size, Image.LANCZOS)
    rebootLogoColoured = rebootLogoColoured.resize(bottom_logo_size, Image.LANCZOS)
    shutdownLogoColoured = shutdownLogoColoured.resize(bottom_logo_size, Image.LANCZOS)


    combined_bottom_logos_width = infoLogoColoured.size[0]+configLogoColoured.size[0]+rebootLogoColoured.size[0]+shutdownLogoColoured.size[0]

    circle_padding = min((int(config.deviceScreenHeightVar)*15)/480,(int(config.deviceScreenWidthVar)*15)/640)*render_factor ## CHANGE to adjust 

    combined_bottom_row_height = max(infoLogoColoured.size[1],configLogoColoured.size[1],rebootLogoColoured.size[1],shutdownLogoColoured.size[1])+circle_padding*2

    circle_radius = combined_bottom_row_height/2

    top_row_to_bottom_row_padding = min((int(config.deviceScreenHeightVar)*20)/480,(int(config.deviceScreenWidthVar)*20)/640)*render_factor ## CHANGE to adjust

    bottom_row_middle_y =  int(screen_y_middle+(combined_top_row_height/2)+top_row_to_bottom_row_padding+circle_radius)


    padding_from_screen_bottom_logos = int(config.deviceScreenWidthVar)*(175/640)*render_factor ##CHANGE to adjust

    padding_between_bottom_logos = (int(config.deviceScreenWidthVar)*render_factor-padding_from_screen_bottom_logos-combined_bottom_logos_width-padding_from_screen_bottom_logos)/(4-1) # 4 logos minus 1

    info_middle = int(padding_from_screen_bottom_logos+(infoLogoColoured.size[0])/2)
    config_middle = int(info_middle+(infoLogoColoured.size[0])/2+padding_between_bottom_logos+(configLogoColoured.size[0])/2)
    reboot_middle = int(config_middle+(configLogoColoured.size[0])/2+padding_between_bottom_logos+(rebootLogoColoured.size[0])/2)
    shutdown_middle = int(reboot_middle+(rebootLogoColoured.size[0])/2+padding_between_bottom_logos+(shutdownLogoColoured.size[0])/2)

    info_logo_x = int(info_middle-(infoLogoColoured.size[0])/2)
    config_logo_x = int(config_middle-(configLogoColoured.size[0])/2)
    reboot_logo_x = int(reboot_middle-(rebootLogoColoured.size[0])/2)
    shutdown_logo_x = int(shutdown_middle-(shutdownLogoColoured.size[0])/2)

    
    

    if workingIndex == 4:
        centre_x = info_middle
        if config.transparent_text_var:
            draw_transparent.ellipse((int(centre_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(centre_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
        else:
            draw.ellipse((int(centre_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(centre_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
    elif workingIndex == 5:
        centre_x = config_middle
        if config.transparent_text_var:
            draw_transparent.ellipse((int(centre_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(centre_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
        else:
            draw.ellipse((int(centre_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(centre_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
    elif workingIndex == 6:
        centre_x = reboot_middle
        if config.transparent_text_var:
            draw_transparent.ellipse((int(centre_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(centre_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
        else:
            draw.ellipse((int(centre_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(centre_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
    elif workingIndex == 7:
        centre_x = shutdown_middle
        if config.transparent_text_var:
            draw_transparent.ellipse((int(centre_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(centre_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
        else:
            draw.ellipse((int(centre_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(centre_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")

    info_logo_y = int(bottom_row_middle_y-(infoLogoColoured.size[1]/2))
    config_logo_y = int(bottom_row_middle_y-(configLogoColoured.size[1]/2))
    reboot_logo_y = int(bottom_row_middle_y-(rebootLogoColoured.size[1]/2))
    shutdown_logo_y = int(bottom_row_middle_y-(shutdownLogoColoured.size[1]/2))
    if config.transparent_text_var and workingIndex >3:
        if workingIndex == 4:
            transparent_text_image = cut_out_image(transparent_text_image,infoLogoColoured,(info_logo_x,info_logo_y))
            image.paste(configLogoColoured,(config_logo_x,config_logo_y),configLogoColoured)
            image.paste(rebootLogoColoured,(reboot_logo_x,reboot_logo_y),rebootLogoColoured)
            image.paste(shutdownLogoColoured,(shutdown_logo_x,shutdown_logo_y),shutdownLogoColoured)
        elif workingIndex == 5:
            image.paste(infoLogoColoured,(info_logo_x,info_logo_y),infoLogoColoured)
            transparent_text_image = cut_out_image(transparent_text_image,configLogoColoured,(config_logo_x,config_logo_y))
            image.paste(rebootLogoColoured,(reboot_logo_x,reboot_logo_y),rebootLogoColoured)
            image.paste(shutdownLogoColoured,(shutdown_logo_x,shutdown_logo_y),shutdownLogoColoured)
        elif workingIndex == 6:
            image.paste(infoLogoColoured,(info_logo_x,info_logo_y),infoLogoColoured)
            image.paste(configLogoColoured,(config_logo_x,config_logo_y),configLogoColoured)
            transparent_text_image = cut_out_image(transparent_text_image,rebootLogoColoured,(reboot_logo_x,reboot_logo_y))
            image.paste(shutdownLogoColoured,(shutdown_logo_x,shutdown_logo_y),shutdownLogoColoured)
        elif workingIndex == 7:
            image.paste(infoLogoColoured,(info_logo_x,info_logo_y),infoLogoColoured)
            image.paste(configLogoColoured,(config_logo_x,config_logo_y),configLogoColoured)
            image.paste(rebootLogoColoured,(reboot_logo_x,reboot_logo_y),rebootLogoColoured)
            transparent_text_image = cut_out_image(transparent_text_image,shutdownLogoColoured,(shutdown_logo_x,shutdown_logo_y))
        
    else:
        image.paste(infoLogoColoured,(info_logo_x,info_logo_y),infoLogoColoured)
        image.paste(configLogoColoured,(config_logo_x,config_logo_y),configLogoColoured)
        image.paste(rebootLogoColoured,(reboot_logo_x,reboot_logo_y),rebootLogoColoured)
        image.paste(shutdownLogoColoured,(shutdown_logo_x,shutdown_logo_y),shutdownLogoColoured)

    if config.transparent_text_var:
        image = Image.alpha_composite(image, transparent_text_image)
    image = Image.alpha_composite(image, menuHelperGuides)

    ## Show what header items will actually look like

    headerBubbles = generateHeaderBubbles(config,render_factor)
    image = Image.alpha_composite(image, headerBubbles)
    
    if forPreview:
        muOSOverlay = generatePilImageMuOSOverlay(config,"muxlaunch",render_factor)
        image = Image.alpha_composite(image, muOSOverlay)
    return(image)

def generatePilImageAltHorizontal(progress_bar,workingIndex, bg_hex, selected_font_hex,deselected_font_hex, bubble_hex,icon_hex,render_factor,config:Config,transparent=False,forPreview=False):
    progress_bar['value']+=1
    bg_rgb = hex_to_rgb(bg_hex)

    # Create image

    if not transparent:
        image = Image.new("RGBA", (int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor), bg_rgb)

        if background_image != None:
            image.paste(background_image.resize((int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor)), (0,0))
    else:
        image = Image.new("RGBA", (int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor), (0,0,0,0))


    top_to_bottom_row_padding = min((int(config.deviceScreenHeightVar)*30)/480,(int(config.deviceScreenWidthVar)*30)/640) * render_factor  ## CHANGE for adjustment
    

    exploreLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "explore.png"),icon_hex)
    collectionLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "collection.png"),icon_hex)
    historyLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "history.png"),icon_hex)
    appsLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "apps.png"),icon_hex)
   
    top_logo_size = (int((exploreLogoColoured.size[0]*render_factor*min(int(config.deviceScreenHeightVar)/480,int(config.deviceScreenWidthVar)/640))/5),
                     int((exploreLogoColoured.size[1]*render_factor*min(int(config.deviceScreenHeightVar)/480,int(config.deviceScreenWidthVar)/640))/5))
    
    exploreLogoColoured = exploreLogoColoured.resize((top_logo_size), Image.LANCZOS)
    collectionLogoColoured = collectionLogoColoured.resize((top_logo_size), Image.LANCZOS)
    historyLogoColoured = historyLogoColoured.resize((top_logo_size), Image.LANCZOS)
    appsLogoColoured = appsLogoColoured.resize((top_logo_size), Image.LANCZOS)
    
    combined_top_logos_width = exploreLogoColoured.size[0]+collectionLogoColoured.size[0]+historyLogoColoured.size[0]+appsLogoColoured.size[0]

    icons_to_bubble_padding = min((int(config.deviceScreenHeightVar)*0)/480,(int(config.deviceScreenWidthVar)*0)/640)*render_factor ## CHANGE for adjustment

    bubble_height = min((int(config.deviceScreenHeightVar)*36.3)/480,(int(config.deviceScreenWidthVar)*36.3)/640)*render_factor ## CHANGE for adjustment

    screen_y_middle = (int(config.deviceScreenHeightVar)*render_factor)/2

    combined_top_row_height = max(exploreLogoColoured.size[1],collectionLogoColoured.size[1],historyLogoColoured.size[1],appsLogoColoured.size[1])+icons_to_bubble_padding+bubble_height

    top_row_icon_y = int(screen_y_middle-combined_top_row_height-(top_to_bottom_row_padding/2))

    top_row_bubble_middle = int(screen_y_middle-(bubble_height)/2-(top_to_bottom_row_padding/2))

    padding_between_top_logos = (int(config.deviceScreenWidthVar)*render_factor-combined_top_logos_width)/(4+1) # 4 logos plus 1

    explore_middle_x = int(padding_between_top_logos+(exploreLogoColoured.size[0])/2)
    collection_middle_x = int(padding_between_top_logos+collectionLogoColoured.size[0]+padding_between_top_logos+(collectionLogoColoured.size[0])/2)
    history_middle_x = int(padding_between_top_logos+historyLogoColoured.size[0]+padding_between_top_logos+collectionLogoColoured.size[0]+padding_between_top_logos+(historyLogoColoured.size[0])/2)
    apps_middle_x = int(padding_between_top_logos+appsLogoColoured.size[0]+padding_between_top_logos+collectionLogoColoured.size[0]+padding_between_top_logos+historyLogoColoured.size[0]+padding_between_top_logos+(appsLogoColoured.size[0])/2)

    explore_logo_x = int(explore_middle_x-(exploreLogoColoured.size[0])/2)
    collection_logo_x = int(collection_middle_x-(collectionLogoColoured.size[0])/2)
    history_logo_x = int(history_middle_x-(historyLogoColoured.size[0])/2)
    apps_logo_x = int(apps_middle_x-(appsLogoColoured.size[0])/2)

    image.paste(exploreLogoColoured,(explore_logo_x,top_row_icon_y),exploreLogoColoured)
    image.paste(collectionLogoColoured,(collection_logo_x,top_row_icon_y),collectionLogoColoured)
    image.paste(historyLogoColoured,(history_logo_x,top_row_icon_y),historyLogoColoured)
    image.paste(appsLogoColoured,(apps_logo_x,top_row_icon_y),appsLogoColoured)

    draw = ImageDraw.Draw(image)
    if config.transparent_text_var:
        transparent_text_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw_transparent = ImageDraw.Draw(transparent_text_image)
        transparency = 0

    if not config.use_alt_font_var:
        selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    else:
        if os.path.exists(config.alt_font_path):
            selected_font_path = config.alt_font_path
        else:
            selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    menuHelperGuides = generateMenuHelperGuides([["A", "SELECT"]],selected_font_path,config.footerBubbleHexVar,render_factor,config,lhsButtons=[["POWER","SLEEP"]])
    

    font_size = min((int(config.deviceScreenHeightVar)*24)/480,(int(config.deviceScreenWidthVar)*24)/640) * render_factor  ## CHANGE for adjustment
    font = ImageFont.truetype(selected_font_path, font_size)
    if workingIndex == 0:
        current_x_midpoint = explore_middle_x
    elif workingIndex == 1:
        current_x_midpoint = collection_middle_x
    elif workingIndex == 2:
        current_x_midpoint = history_middle_x
    elif workingIndex == 3:
        current_x_midpoint = apps_middle_x
    else:
        current_x_midpoint = 104+(144*workingIndex)

    

    horizontalBubblePadding = min((int(config.deviceScreenHeightVar)*40)/480,(int(config.deviceScreenWidthVar)*40)/640)*render_factor  ## CHANGE for adjustment
    
    if config.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("content explorer", "Content"))
    else:
        textString = "Content"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    ascent, descent = font.getmetrics()
    text_height = ascent + descent

    text_y = top_row_bubble_middle - (text_height / 2)


    bubble_centre_x =  explore_middle_x
    textColour = selected_font_hex if workingIndex == 0 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 0 :
        bubbleLength = text_width+horizontalBubblePadding
        if config.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int(top_row_bubble_middle-bubble_height/2)), ((current_x_midpoint+(bubbleLength/2)), int(top_row_bubble_middle+bubble_height/2))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
        else:
            draw.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int(top_row_bubble_middle-bubble_height/2)), ((current_x_midpoint+(bubbleLength/2)), int(top_row_bubble_middle+bubble_height/2))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
    if config.transparent_text_var and workingIndex == 0:
        draw_transparent.text((text_x, text_y), textString, font=font, fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency))
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")
    
    if config.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("collections", "Collections"))
    else:
        textString = "Collections"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    bubble_centre_x =  collection_middle_x
    textColour = selected_font_hex if workingIndex == 1 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 1 :
        bubbleLength = text_width+horizontalBubblePadding
        if config.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int(top_row_bubble_middle-bubble_height/2)), ((current_x_midpoint+(bubbleLength/2)), int(top_row_bubble_middle+bubble_height/2))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
        else:
            draw.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int(top_row_bubble_middle-bubble_height/2)), ((current_x_midpoint+(bubbleLength/2)), int(top_row_bubble_middle+bubble_height/2))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
    if config.transparent_text_var and workingIndex == 1:
        draw_transparent.text((text_x, text_y), textString, font=font, fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency))
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    if config.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("history", "History"))
    else:
        textString = "History"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    bubble_centre_x =  history_middle_x
    textColour = selected_font_hex if workingIndex == 2 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 2 :
        bubbleLength = text_width+horizontalBubblePadding
        if config.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int((top_row_bubble_middle-bubble_height/2))), ((current_x_midpoint+(bubbleLength/2)), int((top_row_bubble_middle+bubble_height/2)))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
        else:
            draw.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int((top_row_bubble_middle-bubble_height/2))), ((current_x_midpoint+(bubbleLength/2)), int((top_row_bubble_middle+bubble_height/2)))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
    if config.transparent_text_var and workingIndex == 2:
        draw_transparent.text((text_x, text_y), textString, font=font, fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency))
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")
    if config.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("applications", "Utilities"))
    else:
        textString = "Utilities"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    bubble_centre_x =  apps_middle_x
    textColour = selected_font_hex if workingIndex == 3 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 3 :
        bubbleLength = text_width+horizontalBubblePadding
        if config.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int((top_row_bubble_middle-bubble_height/2))), ((current_x_midpoint+(bubbleLength/2)), int((top_row_bubble_middle+bubble_height/2)))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
        else:
            draw.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int((top_row_bubble_middle-bubble_height/2))), ((current_x_midpoint+(bubbleLength/2)), int((top_row_bubble_middle+bubble_height/2)))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
    if config.transparent_text_var and workingIndex == 3:
        draw_transparent.text((text_x, text_y), textString, font=font, fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency))
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    

    infoLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "alt-info.png"),icon_hex)
    configLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "alt-config.png"),icon_hex)
    rebootLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "alt-reboot.png"),icon_hex)
    shutdownLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "alt-shutdown.png"),icon_hex)
   
    bottom_logo_size = (int((infoLogoColoured.size[0]*render_factor*min(int(config.deviceScreenHeightVar)/480,int(config.deviceScreenWidthVar)/640))/5),
                     int((infoLogoColoured.size[1]*render_factor*min(int(config.deviceScreenHeightVar)/480,int(config.deviceScreenWidthVar)/640))/5))
    
    infoLogoColoured = infoLogoColoured.resize((bottom_logo_size), Image.LANCZOS)
    configLogoColoured = configLogoColoured.resize((bottom_logo_size), Image.LANCZOS)
    rebootLogoColoured = rebootLogoColoured.resize((bottom_logo_size), Image.LANCZOS)
    shutdownLogoColoured = shutdownLogoColoured.resize((bottom_logo_size), Image.LANCZOS)
    
    combined_bottom_logos_width = infoLogoColoured.size[0]+configLogoColoured.size[0]+rebootLogoColoured.size[0]+shutdownLogoColoured.size[0]

    combined_bottom_row_height = max(infoLogoColoured.size[1],configLogoColoured.size[1],rebootLogoColoured.size[1],shutdownLogoColoured.size[1])+icons_to_bubble_padding+bubble_height

    bottom_row_icon_y = int(screen_y_middle+(top_to_bottom_row_padding/2))

    bottom_row_bubble_middle = int(screen_y_middle+(combined_bottom_row_height)-(bubble_height)/2+(top_to_bottom_row_padding/2))

    padding_between_bottom_logos = (int(config.deviceScreenWidthVar)*render_factor-combined_bottom_logos_width)/(4+1) # 4 logos plus 1

    info_middle_x = int(padding_between_bottom_logos+(infoLogoColoured.size[0])/2)
    config_middle_x = int(info_middle_x+(infoLogoColoured.size[0])/2+padding_between_bottom_logos+(configLogoColoured.size[0])/2)
    reboot_middle_x = int(config_middle_x+(configLogoColoured.size[0])/2+padding_between_bottom_logos+(rebootLogoColoured.size[0])/2)
    shutdown_middle_x = int(reboot_middle_x+(rebootLogoColoured.size[0])/2+padding_between_bottom_logos+(shutdownLogoColoured.size[0])/2)

    info_logo_x = int(info_middle_x-(infoLogoColoured.size[0])/2)
    config_logo_x = int(config_middle_x-(configLogoColoured.size[0])/2)
    reboot_logo_x = int(reboot_middle_x-(rebootLogoColoured.size[0])/2)
    shutdown_logo_x = int(shutdown_middle_x-(shutdownLogoColoured.size[0])/2)

    image.paste(infoLogoColoured,(info_logo_x,bottom_row_icon_y),infoLogoColoured)
    image.paste(configLogoColoured,(config_logo_x,bottom_row_icon_y),configLogoColoured)
    image.paste(rebootLogoColoured,(reboot_logo_x,bottom_row_icon_y),rebootLogoColoured)
    image.paste(shutdownLogoColoured,(shutdown_logo_x,bottom_row_icon_y),shutdownLogoColoured)
    

    if workingIndex == 4:
        current_x_midpoint = info_middle_x
    elif workingIndex == 5:
        current_x_midpoint = config_middle_x
    elif workingIndex == 6:
        current_x_midpoint = reboot_middle_x
    elif workingIndex == 7:
        current_x_midpoint = shutdown_middle_x
    else:
        current_x_midpoint = 104+(144*workingIndex)

    if config.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("information", "Info"))
    else:
        textString = "Info"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    ascent, descent = font.getmetrics()
    text_height = ascent + descent

    text_y = bottom_row_bubble_middle - (text_height / 2)


    bubble_centre_x =  info_middle_x
    textColour = selected_font_hex if workingIndex == 4 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 4 :
        bubbleLength = text_width+horizontalBubblePadding
        if config.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int(bottom_row_bubble_middle-bubble_height/2)), ((current_x_midpoint+(bubbleLength/2)), int(bottom_row_bubble_middle+bubble_height/2))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
        else:
            draw.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int(bottom_row_bubble_middle-bubble_height/2)), ((current_x_midpoint+(bubbleLength/2)), int(bottom_row_bubble_middle+bubble_height/2))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
    if config.transparent_text_var and workingIndex == 4:
        draw_transparent.text((text_x, text_y), textString, font=font, fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency))
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")
    
    if config.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("configuration", "Config"))
    else:
        textString = "Config"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    bubble_centre_x =  config_middle_x
    textColour = selected_font_hex if workingIndex == 5 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 5 :
        bubbleLength = text_width+horizontalBubblePadding
        if config.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int(bottom_row_bubble_middle-bubble_height/2)), ((current_x_midpoint+(bubbleLength/2)), int(bottom_row_bubble_middle+bubble_height/2))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
        else:
            draw.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int(bottom_row_bubble_middle-bubble_height/2)), ((current_x_midpoint+(bubbleLength/2)), int(bottom_row_bubble_middle+bubble_height/2))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
    if config.transparent_text_var and workingIndex == 5:
        draw_transparent.text((text_x, text_y), textString, font=font, fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency))
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")



    if config.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("reboot device", "Reboot"))
    else:
        textString = "Reboot"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    bubble_centre_x =  reboot_middle_x
    textColour = selected_font_hex if workingIndex == 6 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 6 :
        bubbleLength = text_width+horizontalBubblePadding
        if config.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int((bottom_row_bubble_middle-bubble_height/2))), ((current_x_midpoint+(bubbleLength/2)), int((bottom_row_bubble_middle+bubble_height/2)))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
        else:
            draw.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int((bottom_row_bubble_middle-bubble_height/2))), ((current_x_midpoint+(bubbleLength/2)), int((bottom_row_bubble_middle+bubble_height/2)))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
    if config.transparent_text_var and workingIndex == 6:
        draw_transparent.text((text_x, text_y), textString, font=font, fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency))
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")



    if config.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("shutdown device", "Shutdown"))
    else:
        textString = "Shutdown"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    bubble_centre_x =  shutdown_middle_x
    textColour = selected_font_hex if workingIndex == 7 else deselected_font_hex
    text_x = bubble_centre_x - (text_width / 2)
    if workingIndex == 7 :
        bubbleLength = text_width+horizontalBubblePadding
        if config.transparent_text_var:
            draw_transparent.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int((bottom_row_bubble_middle-bubble_height/2))), ((current_x_midpoint+(bubbleLength/2)), int((bottom_row_bubble_middle+bubble_height/2)))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
        else:
            draw.rounded_rectangle(
                [((current_x_midpoint-(bubbleLength/2)), int((bottom_row_bubble_middle-bubble_height/2))), ((current_x_midpoint+(bubbleLength/2)), int((bottom_row_bubble_middle+bubble_height/2)))],
                radius=(bubble_height/2),
                fill=f"#{bubble_hex}"
            )
    if config.transparent_text_var and workingIndex == 7:
        draw_transparent.text((text_x, text_y), textString, font=font, fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency))
    else:
        draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    if config.transparent_text_var:
        image = Image.alpha_composite(image, transparent_text_image)
    image = Image.alpha_composite(image, menuHelperGuides)

    headerBubbles = generateHeaderBubbles(config,render_factor)
    image = Image.alpha_composite(image, headerBubbles)

    if forPreview:
        muOSOverlay = generatePilImageMuOSOverlay(config,"muxlaunch",render_factor)
        image = Image.alpha_composite(image, muOSOverlay)
    
    return(image)


def generatePilImageBootLogo(bg_hex,deselected_font_hex,bubble_hex,render_factor,config:Config):
    bg_rgb = hex_to_rgb(bg_hex)
    image = Image.new("RGBA", (int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor), bg_rgb)
    if config.use_custom_bootlogo_var:
        if os.path.exists(config.bootlogo_image_path):
            bootlogo_image = Image.open(config.bootlogo_image_path)
            image.paste(bootlogo_image.resize((int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor)), (0,0))
            return image
    elif background_image != None:
        image.paste(background_image.resize((int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor)), (0,0))

    draw = ImageDraw.Draw(image)
    transparent_text_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw_transparent = ImageDraw.Draw(transparent_text_image)

    if not config.use_alt_font_var:
        selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    else:
        if os.path.exists(config.alt_font_path):
            selected_font_path = config.alt_font_path
        else:
            selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")

    mu_font_size = 130 * render_factor
    mu_font = ImageFont.truetype(selected_font_path, mu_font_size)
    os_font_size = 98 * render_factor
    os_font = ImageFont.truetype(selected_font_path, os_font_size)

    screen_x_middle, screen_y_middle = (int(config.deviceScreenWidthVar)/2)*render_factor,(int(config.deviceScreenHeightVar)/2)*render_factor

    from_middle_padding = 20*render_factor

    muText = "mu"

    osText = "OS"

    muTextBbox = mu_font.getbbox(muText)
    osTextBbox = os_font.getbbox(osText)

    muTextWidth = muTextBbox[2] - muTextBbox[0]
    muTextHeight = muTextBbox[3]-muTextBbox[1]
    mu_y_location = screen_y_middle-muTextHeight/2-muTextBbox[1]
    mu_x_location = screen_x_middle - from_middle_padding - muTextWidth

    osTextWidth = osTextBbox[2] - osTextBbox[0]
    osTextHeight = osTextBbox[3] - osTextBbox[1]
    os_y_location = screen_y_middle - osTextHeight / 2-osTextBbox[1]
    os_x_location = screen_x_middle + from_middle_padding

    bubble_x_padding = 30 * render_factor
    bubble_y_padding = 25 * render_factor
    bubble_x_mid_point = screen_x_middle + from_middle_padding + (osTextWidth / 2)
    bubble_width = bubble_x_padding + osTextWidth + bubble_x_padding
    bubble_height = bubble_y_padding + osTextHeight + bubble_y_padding
    transparency = 0
    
    draw_transparent.rounded_rectangle(
        [(bubble_x_mid_point-(bubble_width/2), screen_y_middle-(bubble_height/2)), (bubble_x_mid_point+(bubble_width/2), screen_y_middle+(bubble_height/2))],
        radius=bubble_height/2,
        fill=f"#{bubble_hex}"
    )

    draw.text((mu_x_location,mu_y_location), muText,font=mu_font, fill=f"#{deselected_font_hex}")
    draw_transparent.text((os_x_location,os_y_location),osText,font=os_font,fill=(*ImageColor.getrgb(f"#{bubble_hex}"), transparency))
    
    combined_image = Image.alpha_composite(image, transparent_text_image)

    return combined_image

def generatePilImageBootScreen(bg_hex,deselected_font_hex,icon_hex,display_text,render_factor,config:Config,icon_path=None):
    bg_rgb = hex_to_rgb(bg_hex)
    image = Image.new("RGBA", (int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor), bg_rgb)
    if background_image != None:
        image.paste(background_image.resize((int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor)), (0,0))
    
    draw = ImageDraw.Draw(image)

    if not config.use_alt_font_var:
        selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    else:
        if os.path.exists(config.alt_font_path):
            selected_font_path = config.alt_font_path
        else:
            selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    
    screen_x_middle, screen_y_middle = int((int(config.deviceScreenWidthVar)/2)*render_factor),int((int(config.deviceScreenHeightVar)/2)*render_factor)

    from_middle_padding = 0
    
    if icon_path != None:
        if os.path.exists(icon_path):
            from_middle_padding = 50*render_factor

            logoColoured = change_logo_color(icon_path,icon_hex)
            logoColoured = logoColoured.resize((int((logoColoured.size[0]/5)*render_factor),int((logoColoured.size[1]/5)*render_factor)), Image.LANCZOS)
            
            logo_y_location = int(screen_y_middle-logoColoured.size[1]/2-from_middle_padding)
            logo_x_location = int(screen_x_middle-logoColoured.size[0]/2)

            image.paste(logoColoured,(logo_x_location,logo_y_location),logoColoured)
            
    font_size = int(57.6 * render_factor)
    font = ImageFont.truetype(selected_font_path, font_size)

    displayText = display_text
    if config.alternate_menu_names_var:
        displayText = bidi_get_display(menuNameMap.get(display_text.lower(), display_text))

    

    textBbox = font.getbbox(displayText)

    textWidth = int(textBbox[2] - textBbox[0])
    textHeight = int(textBbox[3]-textBbox[1])
    y_location = int(screen_y_middle-textHeight/2-textBbox[1]+from_middle_padding)
    x_location = int(screen_x_middle - textWidth/2)

    draw.text((x_location,y_location), displayText, font=font, fill=f"#{deselected_font_hex}")

    
    return (image)

def generatePilImageDefaultScreen(bg_hex,render_factor,config:Config):
    bg_rgb = hex_to_rgb(bg_hex)
    image = Image.new("RGBA", (int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor), bg_rgb)
    if background_image != None:
        image.paste(background_image.resize((int(config.deviceScreenWidthVar) * render_factor, int(config.deviceScreenHeightVar) * render_factor)), (0,0))
    return (image)

def HorizontalMenuGen(progress_bar,muOSSystemName, listItems, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex,icon_hex, render_factor, outputDir,variant, config:Config, threadNumber = 0):
    startIndex = 0
    endIndex = 8
    for workingIndex in range(startIndex, endIndex):
        workingItem = listItems[workingIndex]
        #image.save(os.path.join(script_dir,"Images for testing horizontal",f"{workingIndex}.png"))
        if variant == "Horizontal":
            image = generatePilImageHorizontal(progress_bar,workingIndex,bg_hex, selected_font_hex,deselected_font_hex,bubble_hex,icon_hex,render_factor,config,transparent=True)
        elif variant == "Alt-Horizontal":
           image = generatePilImageAltHorizontal(progress_bar,workingIndex,bg_hex, selected_font_hex,deselected_font_hex,bubble_hex,icon_hex,render_factor,config,transparent=True)
        else:
            raise ValueError("Something went wrong with your Main Menu Style")
        image = image.resize((int(config.deviceScreenWidthVar), int(config.deviceScreenHeightVar)), Image.LANCZOS)
        if workingItem[1] == "File":
            directory = os.path.dirname(f"{outputDir}/{muOSSystemName}/box/{workingItem[0]}.png")
            if not os.path.exists(directory):
                os.makedirs(directory)
            image.save(f"{outputDir}/{muOSSystemName}/box/{workingItem[0]}.png")
        elif workingItem[1] == "Directory":
            directory = os.path.dirname(f"{outputDir}/Folder/box/{workingItem[0]}.png")
            if not os.path.exists(directory):
                os.makedirs(directory)
            image.save(f"{outputDir}/Folder/box/{workingItem[0]}.png")
        elif workingItem[1] == "Menu":
            directory = os.path.dirname(f"{outputDir}/{muOSSystemName}/{workingItem[2]}.png")
            if not os.path.exists(directory):
                os.makedirs(directory)
            image.save(f"{outputDir}/{muOSSystemName}/{workingItem[2]}.png")

def getAlternateMenuNameDict():
    if os.path.exists(global_config.alt_text_path):
        try:
            
            with open(global_config.alt_text_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            data = {key.lower(): value for key, value in data.items()}
            return data
        except:
            return getDefaultAlternateMenuNameData()
    elif os.path.exists(os.path.join(script_dir,global_config.alt_text_path)):
        try:
            with open(os.path.join(script_dir,global_config.alt_text_path), 'r', encoding='utf-8') as file:
                data = json.load(file)
            data = {key.lower(): value for key, value in data.items()}
            return data
        except:
            return getDefaultAlternateMenuNameData()
    
    return getDefaultAlternateMenuNameData()

def getDefaultAlternateMenuNameData():
    defaultMenuNameMap = {}
    for section in menus2405_2:
        if section[0].startswith("mux"):
            for n in section[1]:
                defaultMenuNameMap[n[0].lower()] = n[0]
    
    defaultMenuNameMap["content explorer"] = "Games"
    defaultMenuNameMap["applications"] = "Utilities"
    defaultMenuNameMap["power"] = "POWER"
    defaultMenuNameMap["sleep"] = "SLEEP"
    defaultMenuNameMap["menu"] = "MENU"
    defaultMenuNameMap["help"] = "HELP"
    defaultMenuNameMap["back"] = "BACK"
    defaultMenuNameMap["okay"] = "OKAY"
    defaultMenuNameMap["confirm"] = "CONFIRM"
    defaultMenuNameMap["launch"] = "LAUNCH"
    defaultMenuNameMap["charging..."] = "Charging..."
    defaultMenuNameMap["loading..."] = "Loading..."
    defaultMenuNameMap["rebooting..."] = "Rebooting..."
    defaultMenuNameMap["shutting down..."] = "Shutting Down..."
    return defaultMenuNameMap


def copy_contents(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)
        
        if os.path.isdir(src_path):
            if not os.path.exists(dst_path):
                shutil.copytree(src_path, dst_path)
            else:
                copy_contents(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)


def delete_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    else:
        raise FileNotFoundError(f"Folder {folder_path} does not exist")

def select_theme_directory():
    theme_directory_path.set(filedialog.askdirectory())

def select_background_image_path():
    # File dialog to select a file, with specific types of files allowed
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png"),("Image Files", "*.jpg"),("Image Files", "*.jpeg"),("Image Files", "*.webp"),("Image Files", "*.gif"),("Image Files", "*.bmp")],  # Only show .png files
        title="Select background image file"
    )
    background_image_path.set(file_path)

def select_bootlogo_image_path():
    # File dialog to select a file, with specific types of files allowed
    file_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png"),("Image Files", "*.jpg"),("Image Files", "*.jpeg"),("Image Files", "*.webp"),("Image Files", "*.gif"),("Image Files", "*.bmp")],  # Only show .png files
        title="Select bootlogo image file"
    )
    bootlogo_image_path.set(file_path)

def select_alt_font_path():
    # File dialog to select a file, with specific types of files allowed
    file_path = filedialog.askopenfilename(
        filetypes=[("Font Files", "*.ttf"), ("Font Files", "*.otf")],  # Only show font files
        title="Select font file"
    )
    alt_font_path.set(file_path)

def select_alt_text_path():
    file_path = filedialog.askopenfilename(
        filetypes=[("JSON", "*.json")],  # Only show font files
        title="Select Text Replacement file"
    )
    alt_text_path.set(file_path)


# INFO FOR BELOW LIST
#        FOLDER NAME      DISPLAYED NAME     FILE NAME

menus2405 = [["muxapps",[["Archive Manager","archive"],
                     ["Backup Manager","backup"],
                     ["Portmaster","portmaster"],
                     ["Retroarch","retroarch"],
                     ["Dingux Commander","dingux"],
                     ["Gmu Music Player","gmu"]]],
         ["muxconfig",[["General Settings","general"],
                     ["Theme Picker","theme"],
                     ["Wi-Fi Settings","network"],
                     ["Web Services","service"],
                     ["Date and Time","clock"],
                     ["Device Type","device"],
                     ["System Refresh","refresh"]]],
         ["muxdevice",[["RG35XX - H","rg35xx-h"],
                     ["RG35XX - Plus","rg35xx-plus"],
                     ["RG35XX - 2024","rg35xx-2024"]]],
         ["muxinfo",[["Input Tester","tester"],
                     ["System Details","system"],
                     ["Supporters","credit"]]],
         ["muxlaunch",[["Content Explorer","explore"],
                     ["Collections","collection"],
                     ["History","history"],
                     ["Applications","apps"],
                     ["Information","info"],
                     ["Configuration","config"],
                     ["Reboot Device","reboot"],
                     ["Shutdown Device","shutdown"]]]]

menus2405_1 = [["muxapp",[["Archive Manager","Archive Manager"],
                     ["Dingux Commander","Dingux Commander"],
                     ["GMU Music Player","GMU Music Player"],
                     ["PortMaster","PortMaster"],
                     ["RetroArch","RetroArch"],
                     ["Simple Terminal","Simple Terminal"],
                     ["Task Toolkit","Task Toolkit"]]],
         ["muxconfig",[["General Settings","general"],
                     ["Theme Picker","theme"],
                     ["Wi-Fi Settings","network"],
                     ["Web Services","service"],
                     ["Date and Time","clock"],
                     ["Device Type","device"]]],
         ["muxdevice",[["RG35XX - H","rg35xx-h"],
                     ["RG35XX - Plus","rg35xx-plus"],
                     ["RG35XX - SP","rg35xx-sp"],
                     ["RG35XX - 2024","rg35xx-2024"]]],
         ["muxinfo",[["Input Tester","tester"],
                     ["System Details","system"],
                     ["Supporters","credit"]]],
         ["muxlaunch",[["Content Explorer","explore"],
                     ["Collections","collection"],
                     ["History","history"],
                     ["Applications","apps"],
                     ["Information","info"],
                     ["Configuration","config"],
                     ["Reboot Device","reboot"],
                     ["Shutdown Device","shutdown"]]]]
menus2405_2 = [["muxapp",[["Archive Manager","Archive Manager"],
                     ["Dingux Commander","Dingux Commander"],
                     ["Flip Clock","Flip Clock"],
                     ["GMU Music Player","GMU Music Player"],
                     ["Moonlight","Moonlight"],
                     ["PortMaster","PortMaster"],
                     ["PPSSPP","PPSSPP"],
                     ["RetroArch","RetroArch"],
                     ["Simple Terminal","Simple Terminal"],
                     ["Task Toolkit","Task Toolkit"]]],
         ["muxconfig",[["General Settings","general"],
                     ["Theme Picker","theme"],
                     ["Wi-Fi Settings","network"],
                     ["Web Services","service"],
                     ["Date and Time","clock"],
                     ["Device Type","device"]]],
         ["muxdevice",[["RG35XX - H","rg35xx-h"],
                     ["RG35XX - Plus","rg35xx-plus"],
                     ["RG35XX - SP","rg35xx-sp"],
                     ["RG35XX - 2024","rg35xx-2024"]]],
         ["muxinfo",[["Input Tester","tester"],
                     ["System Details","system"],
                     ["Supporters","credit"]]],
         ["muxlaunch",[["Content Explorer","explore"],
                     ["Collections","collection"],
                     ["History","history"],
                     ["Applications","apps"],
                     ["Information","info"],
                     ["Configuration","config"],
                     ["Reboot Device","reboot"],
                     ["Shutdown Device","shutdown"]]]]
menus2405_3 = [["muxapp",[["Archive Manager","Archive Manager"],
                     ["Dingux Commander","Dingux Commander"],
                     ["Flip Clock","Flip Clock"],
                     ["GMU Music Player","GMU Music Player"],
                     ["Moonlight","Moonlight"],
                     ["PortMaster","PortMaster"],
                     ["PPSSPP","PPSSPP"],
                     ["RetroArch","RetroArch"],
                     ["Simple Terminal","Simple Terminal"],
                     ["Task Toolkit","Task Toolkit"]]],
         ["muxconfig",[["General Settings","general"],
                     ["Theme Picker","theme"],
                     ["Wi-Fi Settings","network"],
                     ["Web Services","service"],
                     ["Date and Time","clock"],
                     ["Device Type","device"]]],
         ["muxdevice",[["RG35XX - H","rg35xx-h"],
                     ["RG35XX - Plus","rg35xx-plus"],
                     ["RG35XX - SP","rg35xx-sp"],
                     ["RG35XX - 2024","rg35xx-2024"]]],
         ["muxinfo",[["Input Tester","tester"],
                     ["System Details","system"],
                     ["Supporters","credit"]]],
         ["muxlaunch",[["Content Explorer","explore"],
                     ["Collections","collection"],
                     ["History","history"],
                     ["Applications","apps"],
                     ["Information","info"],
                     ["Configuration","config"],
                     ["Reboot Device","reboot"],
                     ["Shutdown Device","shutdown"]]]]

def replace_in_file(file_path, search_string, replace_string):
    # Read the content of the file in binary mode
    with open(file_path, 'rb') as file:
        file_contents = file.read()
    
    # Replace the occurrences of the search_string with replace_string in binary data
    search_bytes = search_string.encode()
    replace_bytes = replace_string.encode()
    new_contents = file_contents.replace(search_bytes, replace_bytes)
    
    # Write the new content back to the file in binary mode
    with open(file_path, 'wb') as file:
        file.write(new_contents)


def hex_to_rgb(hex_color,alpha = 1.0):
    # Convert hex to RGB
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (rgb[0], rgb[1], rgb[2], int(alpha * 255))

def rgb_to_hex(rgb_color):
    # Convert RGB to hex
    return '{:02x}{:02x}{:02x}'.format(*rgb_color)

def interpolate_color_component(c1, c2, factor):
    # Interpolate a single color component
    return int(c1 + (c2 - c1) * factor)

def percentage_color(hex1, hex2, percentage):
    # Convert hex colors to RGB
    rgb1 = hex_to_rgb(hex1)
    rgb2 = hex_to_rgb(hex2)
    
    # Calculate the interpolated color for each component
    interp_rgb = tuple(interpolate_color_component(c1, c2, percentage) for c1, c2 in zip(rgb1, rgb2))
    
    # Convert interpolated RGB back to hex
    return rgb_to_hex(interp_rgb)

def round_to_nearest_odd(number):
    high_odd = (number // 2) * 2 + 1
    low_odd = high_odd - 2
    return int(high_odd) if abs(number - high_odd) < abs(number-low_odd) else int(low_odd)

def generate_theme(progress_bar, loading_window, threadNumber, config: Config,barrier, resolutions, assumed_res):
    try:
        progress_bar['value'] = 0
        if config.main_menu_style_var == "Alt-Horizontal" or config.main_menu_style_var == "Horizontal":
            progress_bar['maximum'] = 44*len(resolutions)
        elif config.main_menu_style_var == "Vertical":
            progress_bar['maximum'] = 36*len(resolutions)
        else:
            raise ValueError("Something went wrong with your Main Menu Style")

        if threadNumber != -1:
            themeName = config.theme_name_entry + f" {config.main_menu_style_var}"
        else:
            themeName = config.theme_name_entry

        assumed_items_per_screen = int(config.items_per_screen_entry)
        height_items_per_screen_map = {}
        for width, height in resolutions:
            height_items_per_screen_map[height] = round_to_nearest_odd(assumed_items_per_screen * (height / assumed_res[1]))


        for width, height in resolutions:
            res_config = copy.deepcopy(config)
            res_config.deviceScreenWidthVar = width
            res_config.deviceScreenHeightVar = height
            if height != assumed_res[1]:
                res_config.items_per_screen_entry = height_items_per_screen_map[height]
                res_config.itemsPerScreenVar = height_items_per_screen_map[height]
                if res_config.clock_alignment_var == "Centre":
                    res_config.clockHorizontalLeftPaddingVar = str(int(int(res_config.clockHorizontalLeftPaddingVar) * (width / assumed_res[0])))
                    res_config.clockHorizontalRightPaddingVar = str(int(int(res_config.clockHorizontalRightPaddingVar) * (width / assumed_res[0])))
                if res_config.header_glyph_alignment_var == "Centre":
                    res_config.header_glyph_horizontal_left_padding_var = str(int(int(res_config.header_glyph_horizontal_left_padding_var) * (width / assumed_res[0])))
                    res_config.header_glyph_horizontal_right_padding_var = str(int(int(res_config.header_glyph_horizontal_right_padding_var) * (width / assumed_res[0])))
                if res_config.page_title_alignment_var == "Centre":
                    res_config.pageTitlePaddingVar = str(int(int(res_config.pageTitlePaddingVar) * (width / assumed_res[0])))
                    res_config.pageTitlePaddingVar = str(int(int(res_config.pageTitlePaddingVar) * (width / assumed_res[0])))
            FillTempThemeFolder(progress_bar, threadNumber,config=res_config)
            shutil.move(os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}", "font"),
                        os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}", f"{width}x{height}", "font"))
            shutil.move(os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}", "glyph"),
                        os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}", f"{width}x{height}", "glyph"))
            shutil.move(os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}", "image"),
                        os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}", f"{width}x{height}", "image"))
            shutil.move(os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}", "scheme"),
                        os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}", f"{width}x{height}", "scheme"))
            shutil.move(os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}", "preview.png"),
                        os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}", f"{width}x{height}", "preview.png"))
            if config.enable_grid_view_explore_var:
                if config.theme_directory_path == "":
                    theme_dir = os.path.join(script_dir, "Generated Theme")
                else:
                    theme_dir = config.theme_directory_path
                os.makedirs(os.path.join(internal_files_dir, f".TempBuildSystemIconsAMFile{threadNumber}", "opt"), exist_ok=True)
                shutil.copy2(os.path.join(internal_files_dir, "Assets", "AM - Scripts", "System Logo Load", "update.sh"),
                            os.path.join(internal_files_dir, f".TempBuildSystemIconsAMFile{threadNumber}", "opt", "update.sh"))
        if config.enable_grid_view_explore_var:
            if config.theme_directory_path == "":
                theme_dir = os.path.join(script_dir, "Generated Theme")
            else:
                theme_dir = config.theme_directory_path
            shutil.make_archive(os.path.join(theme_dir, "MinUIfied AM System Icons"), "zip", os.path.join(internal_files_dir, f".TempBuildSystemIconsAMFile{threadNumber}"))
            if os.path.exists(os.path.join(theme_dir, "MinUIfied AM System Icons.muxzip")):
                os.remove(os.path.join(theme_dir, "MinUIfied AM System Icons.muxzip"))
            os.rename(os.path.join(theme_dir, "MinUIfied AM System Icons.zip"), os.path.join(theme_dir, "MinUIfied AM System Icons.muxzip"))
            delete_folder(os.path.join(internal_files_dir,f".TempBuildSystemIconsAMFile{threadNumber}"))

        if config.theme_directory_path == "":
            theme_dir = os.path.join(script_dir, "Generated Theme")
        else:
            theme_dir = config.theme_directory_path

        with open(os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}", "version.txt"), "w") as version_file:
            version_file.write(TargetMuOSVersion)

        shutil.make_archive(os.path.join(theme_dir, themeName),"zip", os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}"))
        if os.path.exists(os.path.join(theme_dir, f"{themeName}.muxthm")):
            os.remove(os.path.join(theme_dir, f"{themeName}.muxthm"))
        os.rename(os.path.join(theme_dir, f"{themeName}.zip"), os.path.join(theme_dir, f"{themeName}.muxthm"))

        if config.developer_preview_var:
            preview_dir = os.path.join(theme_dir)

            os.makedirs(preview_dir,exist_ok=True)
            for width,height in resolutions:
                temp_preview_path = os.path.join(preview_dir, f"TempPreview{threadNumber}[{width}x{height}].png")
                if os.path.exists(temp_preview_path):
                    os.remove(temp_preview_path)
                shutil.move(os.path.join(internal_files_dir, f"TempPreview{threadNumber}[{width}x{height}].png"), preview_dir)

                theme_preview_path = os.path.join(preview_dir, f"{themeName}[{width}x{height}].png")
                if os.path.exists(theme_preview_path):
                    os.remove(theme_preview_path)

                os.rename(os.path.join(preview_dir,f"TempPreview{threadNumber}[{width}x{height}].png"), theme_preview_path)

                if os.path.exists(os.path.join(internal_files_dir, f"TempPreview{threadNumber}[{width}x{height}].png")):
                    os.remove(os.path.join(internal_files_dir, f"TempPreview{threadNumber}[{width}x{height}].png"))
                if os.path.exists(os.path.join(theme_dir, "preview",f"TempPreview{threadNumber}[{width}x{height}].png")):
                    os.remove(os.path.join(theme_dir, "preview",f"TempPreview{threadNumber}[{width}x{height}].png"))
        

        delete_folder(os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}"))
        if threadNumber == -1:
            messagebox.showinfo("Success", "Theme generated successfully.")
        loading_window.destroy()
        barrier.wait()
    except Exception as e:
        loading_window.destroy()
        if config.theme_directory_path == "":
            theme_dir = os.path.join(script_dir, "Generated Theme")
        else:
            theme_dir = config.theme_directory_path

        if config.advanced_error_var:
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            messagebox.showerror("Error", f"An unexpected error occurred: {e}\n{tb_str}")
        else:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

        delete_folder(os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}"))
        if config.developer_preview_var:
            if os.path.exists(os.path.join(internal_files_dir, f"TempPreview{threadNumber}[{width}x{height}].png")):
                os.remove(os.path.join(internal_files_dir, f"TempPreview{threadNumber}[{width}x{height}].png"))
            if os.path.exists(os.path.join(theme_dir, "preview",f"TempPreview{threadNumber}[{width}x{height}].png")):
                os.remove(os.path.join(theme_dir, "preview",f"TempPreview{threadNumber}[{width}x{height}].png"))

def generate_themes(themes):
    if themes:
        barrier = threading.Barrier(len(themes) + 1)  # Create a barrier for all threads + the main thread
        
        for threadNumber, theme in enumerate(themes):
            thread_config = copy.deepcopy(Config())
            save_settings(thread_config)
            thread_config.apply_theme(theme)
            
            loading_window = tk.Toplevel(root)
            loading_window.title(f"Generating {thread_config.theme_name_entry}...")
            loading_window.geometry("600x100")

            progress_bar = ttk.Progressbar(loading_window, orient="horizontal", length=500, mode="determinate")
            progress_bar.pack(pady=20)

            # Start a thread for each theme generation
            match = re.search(r"\[(\d+)x(\d+)\]", thread_config.device_type_var)
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
            threading.Thread(target=generate_theme, args=(progress_bar, loading_window, threadNumber, thread_config, barrier,all_resolutions,assumed_res)).start()

        # Wait for all threads to finish
        barrier.wait()
        messagebox.showinfo("Success", "Themes generated successfully.")


def FillTempThemeFolder(progress_bar, threadNumber, config:Config):

    textPadding = int(config.text_padding_entry)
    rectanglePadding = int(config.rectangle_padding_entry)
    ItemsPerScreen = int(config.items_per_screen_entry)
    bg_hex = config.background_hex_entry
    selected_font_hex = config.selected_font_hex_entry
    deselected_font_hex = config.deselected_font_hex_entry
    bubble_hex = config.bubble_hex_entry
    icon_hex = config.icon_hex_entry

    if not config.use_alt_font_var:
        selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    else:
        if os.path.exists(config.alt_font_path):
            selected_font_path = config.alt_font_path
        else:
            selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")

    copy_contents(os.path.join(internal_files_dir, "Theme Shell"), os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}"))

    newSchemeDir = os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","scheme")
    os.makedirs(newSchemeDir, exist_ok=True)

    fontSize = int(config.font_size_var)
    
    # Theme Variables that wont change
    accent_hex = deselected_font_hex
    base_hex = bg_hex
    blend_hex = percentage_color(bubble_hex,selected_font_hex,0.5)
    muted_hex = percentage_color(bg_hex,bubble_hex,0.25)
    counter_alignment = "Right"
    datetime_alignment = config.clock_alignment_var
    header_glyph_alignment = config.header_glyph_alignment_var
    datetime_left_padding = config.clockHorizontalLeftPaddingVar
    datetime_right_padding = config.clockHorizontalRightPaddingVar
    status_padding_left = int(config.header_glyph_horizontal_left_padding_var)
    status_padding_right = int(config.header_glyph_horizontal_right_padding_var)

    default_radius = "10"
    header_height = str(config.headerHeightVar)
    counter_padding_top = str(config.contentPaddingTopVar)
    individualItemHeight = round((int(config.deviceScreenHeightVar)-int(config.approxFooterHeightVar)-int(config.contentPaddingTopVar))/int(config.itemsPerScreenVar))
    footerHeight = int(config.deviceScreenHeightVar)-(individualItemHeight*int(config.itemsPerScreenVar))-int(config.contentPaddingTopVar)

    
    templateSchemeFile = os.path.join(internal_files_dir,"Template Scheme","template.ini")

    stringsToReplace = []

    # Read the template file and search for all instances of strings enclosed in {}
    with open(templateSchemeFile, 'r') as file:
        content = file.read()
        # Find all occurrences of patterns like {some_string}
        matches = re.findall(r'\{[^}]+\}', content)
        # Convert matches to a set to keep only unique values, then back to a list
        stringsToReplace = list(set(matches))

    replacementStringMap = {}

    replacementStringMap["default"] = {}
    for n in stringsToReplace:
        replacementStringMap["default"][n] = None

    # Set up default colours that should be the same everywhere
    replacementStringMap["default"]["{accent_hex}"] = accent_hex
    replacementStringMap["default"]["{base_hex}"] = base_hex
    replacementStringMap["default"]["{blend_hex}"] = blend_hex
    replacementStringMap["default"]["{muted_hex}"] = muted_hex
    replacementStringMap["default"]["{battery_charging_hex}"] = config.batteryChargingHexVar
    replacementStringMap["default"]["{bubble_hex}"] = config.bubbleHexVar

    # More Global Settings
    glyph_width = 20
    glyph_to_text_pad = int(config.bubblePaddingVar)
    replacementStringMap["default"]["{boot_text_y_pos}"] = int(int(config.deviceScreenHeightVar)*(165/480))
    replacementStringMap["default"]["{glyph_padding_left}"] = int(int(config.bubblePaddingVar)+(glyph_width/2))
    replacementStringMap["default"]["{image_overlay}"] = config.include_overlay_var
    replacementStringMap["default"]["{footer_height}"] = footerHeight
    if config.show_console_name_var:
        replacementStringMap["default"]["{header_text_alpha}"] = 255
    else:
        replacementStringMap["default"]["{header_text_alpha}"] = 0
    page_title_alignment_map = {"Auto":0,"Left":1,"Centre":2,"Right":3}
    replacementStringMap["default"]["{page_title_text_align}"] = page_title_alignment_map[config.page_title_alignment_var]
    replacementStringMap["default"]["{page_title_padding}"] = int(config.pageTitlePaddingVar)

    replacementStringMap["default"]["{bar_height}"] = 42
    replacementStringMap["default"]["{bar_progress_width}"] = int(config.deviceScreenWidthVar) - 90
    replacementStringMap["default"]["{bar_y_pos}"] = int(config.deviceScreenHeightVar) - (30+getRealFooterHeight(config))
    replacementStringMap["default"]["{bar_width}"] = int(config.deviceScreenWidthVar) - 25
    replacementStringMap["default"]["{bar_progress_height}"] = 16

    content_height = individualItemHeight*int(config.itemsPerScreenVar)

    
    counter_alignment_map = {"Left":0,"Centre":1,"Right":2}
    replacementStringMap["default"]["{counter_alignment}"] = counter_alignment_map[counter_alignment]
    replacementStringMap["default"]["{counter_padding_top}"] = counter_padding_top
    replacementStringMap["default"]["{default_radius}"] = default_radius

    # Global Header Settings:
    datetime_alignment_map = {"Auto":0,"Left":1,"Centre":2,"Right":3}
    replacementStringMap["default"]["{datetime_align}"] = datetime_alignment_map[datetime_alignment]
    replacementStringMap["default"]["{datetime_padding_left}"] = datetime_left_padding
    replacementStringMap["default"]["{datetime_padding_right}"] = datetime_right_padding
    status_alignment_map = {"Left":0,
                            "Right":1,
                            "Centre":2,
                            "Icons spaced evenly across header":3,
                            "icons evenly distributed with equal space around them":4,
                            "First icon aligned left last icon aligned right all other icons evenly distributed":5}
    replacementStringMap["default"]["{status_align}"] = status_alignment_map[header_glyph_alignment]
    replacementStringMap["default"]["{status_padding_left}"] = status_padding_left
    replacementStringMap["default"]["{status_padding_right}"] = status_padding_right
    replacementStringMap["default"]["{header_height}"] = int(header_height)

    # Rest of the settings
    replacementStringMap["default"]["{content_height}"] =content_height
    replacementStringMap["default"]["{content_item_height}"] = individualItemHeight-2
    replacementStringMap["default"]["{content_item_count}"] = config.itemsPerScreenVar
    replacementStringMap["default"]["{background_alpha}"] = 0
    replacementStringMap["default"]["{selected_font_hex}"] = config.selectedFontHexVar
    replacementStringMap["default"]["{deselected_font_hex}"] = config.deselectedFontHexVar
    replacementStringMap["default"]["{bubble_alpha}"] = 255
    replacementStringMap["default"]["{bubble_padding_right}"] = config.bubblePaddingVar
    content_alignment_map = {"Left":0,"Centre":1,"Right":2}
    replacementStringMap["default"]["{content_alignment}"] = content_alignment_map[config.global_alignment_var] # TODO make this change for the different sections
    replacementStringMap["default"]["{list_default_label_long_mode}"] = 1
    content_padding_left = int(config.textPaddingVar)-int(config.bubblePaddingVar)
    if config.global_alignment_var == "Centre":
        content_padding_left = 0
    elif config.global_alignment_var == "Right":
        content_padding_left = -content_padding_left
    replacementStringMap["default"]["{content_padding_left}"] = content_padding_left
    if config.version_var == "muOS 2410.1 Banana":
        replacementStringMap["default"]["{content_width}"] = int(config.deviceScreenWidthVar)-10-2*(int(config.textPaddingVar)-int(config.bubblePaddingVar))
    else:
        replacementStringMap["default"]["{content_width}"] = int(config.deviceScreenWidthVar)-2*(int(config.textPaddingVar)-int(config.bubblePaddingVar))
    replacementStringMap["default"]["{footer_alpha}"] = 0
    replacementStringMap["default"]["{footer_background_alpha}"] = 0
    replacementStringMap["default"]["{footer_pad_top}"] = 0
    replacementStringMap["default"]["{footer_pad_bottom}"] = 0
    if config.show_glyphs_var:
        replacementStringMap["default"]["{bubble_padding_left}"] = int(int(config.bubblePaddingVar)+(glyph_width/2)+glyph_to_text_pad)
        replacementStringMap["default"]["{list_glyph_alpha}"] = 255
    else:
        replacementStringMap["default"]["{bubble_padding_left}"] = config.bubblePaddingVar
        replacementStringMap["default"]["{list_glyph_alpha}"] = 0
    replacementStringMap["default"]["{list_text_alpha}"] = 255
    replacementStringMap["default"]["{navigation_type}"] = 0
    replacementStringMap["default"]["{content_padding_top}"] = int(contentPaddingTop)-(int(header_height)+2)

    # Grid Settings

    replacementStringMap["default"]["{grid_navigation_type}"] = 4
    replacementStringMap["default"]["{grid_background}"] = config.bgHexVar
    replacementStringMap["default"]["{grid_background_alpha}"] = 0
    replacementStringMap["default"]["{grid_location_x}"] = 0
    replacementStringMap["default"]["{grid_location_y}"] = 0
    replacementStringMap["default"]["{grid_column_count}"] = 0
    replacementStringMap["default"]["{grid_row_count}"] = 0
    replacementStringMap["default"]["{grid_row_height}"] = 0
    replacementStringMap["default"]["{grid_column_width}"] = 0
    replacementStringMap["default"]["{grid_cell_width}"] = 200
    replacementStringMap["default"]["{grid_cell_height}"] = 200
    replacementStringMap["default"]["{grid_cell_radius}"] = 10
    replacementStringMap["default"]["{grid_cell_border_width}"] = 0
    replacementStringMap["default"]["{grid_cell_image_padding_top}"] = 0
    replacementStringMap["default"]["{grid_cell_text_padding_bottom}"] = 0
    replacementStringMap["default"]["{grid_cell_text_padding_side}"] = 0
    replacementStringMap["default"]["{grid_cell_text_line_spacing}"] = 0
    replacementStringMap["default"]["{grid_cell_default_background}"] = config.bgHexVar
    replacementStringMap["default"]["{grid_cell_default_background_alpha}"] = 0
    replacementStringMap["default"]["{grid_cell_default_border}"] = config.bgHexVar
    replacementStringMap["default"]["{grid_cell_default_border_alpha}"] = 0
    replacementStringMap["default"]["{grid_cell_default_image_alpha}"] = 255
    replacementStringMap["default"]["{grid_cell_default_image_recolour}"] = config.iconHexVar
    replacementStringMap["default"]["{grid_cell_default_image_recolour_alpha}"] = 255
    replacementStringMap["default"]["{grid_cell_default_text}"] = config.deselectedFontHexVar
    replacementStringMap["default"]["{grid_cell_default_text_alpha}"] = 0
    replacementStringMap["default"]["{grid_cell_focus_background}"] = config.deselectedFontHexVar
    replacementStringMap["default"]["{grid_cell_focus_background_alpha}"] = int(255*0.133)
    replacementStringMap["default"]["{grid_cell_focus_border}"] = config.deselectedFontHexVar
    replacementStringMap["default"]["{grid_cell_focus_border_alpha}"] = 0
    replacementStringMap["default"]["{grid_cell_focus_image_alpha}"] = 255
    replacementStringMap["default"]["{grid_cell_focus_image_recolour}"] = config.iconHexVar
    replacementStringMap["default"]["{grid_cell_focus_image_recolour_alpha}"] = 255
    replacementStringMap["default"]["{grid_cell_focus_text}"] = config.selected_font_hex_entry
    replacementStringMap["default"]["{grid_cell_focus_text_alpha}"] = 0
    
    missingValues = []

    for n in replacementStringMap["default"].keys():
        if replacementStringMap["default"][n] == None:
            missingValues.append(n)
    if missingValues:
        missingValuesString = ""
        for n in missingValues:
            missingValuesString += n+"\n"
        raise ValueError(f"Replacement string(s) \n{missingValuesString} not set")
    
    ## Overrides:

    # horizontal muxlaunch specific options - basically remove all text content and set naviagtion type
    if config.main_menu_style_var != "Vertical":
        replacementStringMap["muxlaunch"] = {}
        replacementStringMap["muxlaunch"]["{bubble_alpha}"] = 0
        replacementStringMap["muxlaunch"]["{list_glyph_alpha}"] = 0
        replacementStringMap["muxlaunch"]["{list_text_alpha}"] = 0
        if config.horizontal_menu_behaviour_var == "Wrap to Row":
            replacementStringMap["muxlaunch"]["{navigation_type}"] = 4
        else:
            replacementStringMap["muxlaunch"]["{navigation_type}"] = 2

    # muxnetwork Specific settings - account for status at the bottom and show footer
    if config.version_var == "muOS 2410.1 Banana":
        replacementStringMap["muxnetwork"] = {}
        replacementStringMap["muxnetwork"]["{content_height}"] = int((content_height/int(config.itemsPerScreenVar))*(int(config.itemsPerScreenVar)-2))
        replacementStringMap["muxnetwork"]["{content_item_count}"] = int(config.itemsPerScreenVar)-2
        replacementStringMap["muxnetwork"]["{footer_alpha}"] = 255
    else: ## muxnetwork - show the footer
        replacementStringMap["muxnetwork"] = {}
        replacementStringMap["muxnetwork"]["{footer_alpha}"] = 255
    
    # muxassign - Force Glyphs on and show footer
    replacementStringMap["muxassign"] = {}
    replacementStringMap["muxassign"]["{bubble_padding_left}"] = int(int(config.bubblePaddingVar)+(glyph_width/2)+glyph_to_text_pad) # for glyph support
    replacementStringMap["muxassign"]["{list_glyph_alpha}"] = 255 # for glyph support
    replacementStringMap["muxassign"]["{footer_alpha}"] = 255 ## Show footer in muxassign as can't generate custom one

    # muxgov - same as muxassign, but hide footer
    replacementStringMap["muxgov"] = replacementStringMap["muxassign"].copy()
    replacementStringMap["muxsearch"] = replacementStringMap["muxassign"].copy()
    replacementStringMap["muxsearch"]["{footer_alpha}"] = 0 
    replacementStringMap["muxgov"]["{footer_alpha}"] = 0

    # muxpicker - Cut text off before preview image
    if config.version_var != "muOS 2410.1 Banana": 
        replacementStringMap["muxpicker"] = {}
        max_preview_size = int(int(config.deviceScreenWidthVar)*0.45)
        if int(config.deviceScreenWidthVar) == 720:
            max_preview_size = 340
        replacementStringMap["muxpicker"]["{content_width}"] = int(config.deviceScreenWidthVar)-max_preview_size-(int(config.textPaddingVar)-int(config.bubblePaddingVar))
     
     # muxplore - cut off text if needed for box art
    if int(config.maxBoxArtWidth) > 0:
        replacementStringMap["muxplore"] = {}

        replacementStringMap["muxplore"]["{content_width}"] = int(config.deviceScreenWidthVar)-int(config.maxBoxArtWidth)-(int(config.textPaddingVar)-int(config.bubblePaddingVar))

        # muxcollect - same as muxplore
        replacementStringMap["muxcollect"] = replacementStringMap["muxplore"].copy()

    # muxhistory - make this more like a game switcher
    if config.enable_game_switcher_var and not "Generating new game switcher":
        replacementStringMap["muxhistory"] = {}

        bottom_bar_height_over_footer_percent = 0.1
        bottom_bar_height_over_footer = int((int(config.deviceScreenHeightVar) * bottom_bar_height_over_footer_percent))
        bottom_bar_total_height = int(getRealFooterHeight(config)) + bottom_bar_height_over_footer
        bottom_bar_height_over_footer += 2


        replacementStringMap["muxhistory"]["{content_height}"] =bottom_bar_height_over_footer
        replacementStringMap["muxhistory"]["{content_item_count}"] = 1
        replacementStringMap["muxhistory"]["{bubble_alpha}"] = "0"
        content_alignment_map = {"Left":0,"Centre":1,"Right":2}
        replacementStringMap["muxhistory"]["{content_alignment}"] = content_alignment_map["Centre"]
        replacementStringMap["muxhistory"]["{content_padding_left}"] = 0
        replacementStringMap["muxhistory"]["{content_width}"] = config.deviceScreenWidthVar
        replacementStringMap["muxhistory"]["{navigation_type}"] = "1"
        history_content_padding_top = int(config.deviceScreenHeightVar)- bottom_bar_total_height
        replacementStringMap["muxhistory"]["{content_padding_top}"] = int(history_content_padding_top)-(int(header_height)+2)
        replacementStringMap["muxhistory"]["{content_height}"] =bottom_bar_height_over_footer
    if config.enable_game_switcher_var:
        replacementStringMap["muxhistory"] = {}

        bottom_bar_height_over_footer_percent = 0.1
        bottom_bar_height_over_footer = int((int(config.deviceScreenHeightVar) * bottom_bar_height_over_footer_percent))
        bottom_bar_total_height = int(getRealFooterHeight(config)) + bottom_bar_height_over_footer
        bottom_bar_height_over_footer += 2


        replacementStringMap["muxhistory"]["{content_height}"] =bottom_bar_height_over_footer
        replacementStringMap["muxhistory"]["{content_item_count}"] = 1
        replacementStringMap["muxhistory"]["{bubble_alpha}"] = "0"
        replacementStringMap["muxhistory"]["{selected_font_hex}"] = accent_hex
        content_alignment_map = {"Left":0,"Centre":1,"Right":2}
        replacementStringMap["muxhistory"]["{content_alignment}"] = content_alignment_map["Centre"]
        replacementStringMap["muxhistory"]["{content_padding_left}"] = 0
        replacementStringMap["muxhistory"]["{content_width}"] = config.deviceScreenWidthVar
        replacementStringMap["muxhistory"]["{navigation_type}"] = "1"
        history_content_padding_top = int(config.deviceScreenHeightVar)- bottom_bar_total_height
        replacementStringMap["muxhistory"]["{content_padding_top}"] = int(history_content_padding_top)-(int(header_height)+2)
        replacementStringMap["muxhistory"]["{footer_background_alpha}"] = int(0) ## Could change to 255 * 0.866 later if content font is changed to render over footer
        replacementStringMap["muxhistory"]["{footer_alpha}"] = 255
        replacementStringMap["muxhistory"]["{footer_height}"] = bottom_bar_total_height
        replacementStringMap["muxhistory"]["{footer_pad_top}"] = int((bottom_bar_total_height - int(getRealFooterHeight(config)))/2)
        replacementStringMap["muxhistory"]["{footer_pad_bottom}"] = 0
    else: # muxhistory - if not making it onto game switcher, should be the same as muxplore
        if int(config.maxBoxArtWidth) > 0:
            replacementStringMap["muxhistory"] = replacementStringMap["muxplore"].copy()
    
    replacementStringMap["muxstorage"] = {}
    replacementStringMap["muxstorage"]["{footer_alpha}"] = 255
    
    

    if config.enable_grid_view_explore_var:
        grid_total_height = (int(config.deviceScreenHeightVar)-getRealFooterHeight(config)-int(config.headerHeightVar))
        grid_total_width = int(config.deviceScreenWidthVar)
        min_cell_size = min(160, int(grid_total_height/2), int(grid_total_width/4)) # 160 is the minimum size for a grid cell (excluding padding)

        diff_aspect_ratios = {}
        target_aspect_ratio = grid_total_width/grid_total_height
        columns = 0
        rows = 0
        while True:
            columns += 1
            rows = 0
            if grid_total_width/columns < min_cell_size:
                break
            while True:
                rows += 1
                if grid_total_height/rows < min_cell_size:
                    break
                if columns*rows >= 8:
                    aspect_ratio = columns/rows
                    diff_aspect_ratio = abs(aspect_ratio-target_aspect_ratio)
                    
                    diff_aspect_ratios[diff_aspect_ratio] = (columns,rows)
        closest_aspect_ratio = diff_aspect_ratios[min(diff_aspect_ratios.keys())]
        grid_column_count, grid_row_count = closest_aspect_ratio

        grid_row_height = int(grid_total_height/grid_row_count)
        grid_column_width = int(grid_total_width/grid_column_count)
        cell_inner_padding = 5
        grid_location_x = 0
        grid_location_y = int(config.headerHeightVar)
        grid_cell_width = grid_column_width-2*cell_inner_padding
        grid_cell_height = grid_row_height-2*cell_inner_padding
        grid_cell_size = min(grid_cell_width,grid_cell_height)
        if "muxplore" not in replacementStringMap:
            replacementStringMap["muxplore"] = {}
        replacementStringMap["muxplore"]["{grid_location_x}"] = grid_location_x
        replacementStringMap["muxplore"]["{grid_location_y}"] = grid_location_y
        replacementStringMap["muxplore"]["{grid_column_count}"] = grid_column_count
        replacementStringMap["muxplore"]["{grid_row_count}"] = grid_row_count
        replacementStringMap["muxplore"]["{grid_row_height}"] = grid_row_height
        replacementStringMap["muxplore"]["{grid_column_width}"] = grid_column_width
        replacementStringMap["muxplore"]["{grid_cell_width}"] = grid_cell_size
        replacementStringMap["muxplore"]["{grid_cell_height}"] = grid_cell_size
        replacementStringMap["muxplore"]["{grid_cell_radius}"] = math.ceil(grid_cell_size/2.0)

        grid_image_padding = 10

        system_logos_path = os.path.join(internal_files_dir,"Assets", "System Logos",f"png [5x]")

        output_system_logos_path = os.path.join(internal_files_dir,f".TempBuildSystemIconsAMFile{threadNumber}","run","muos","storage","info", "catalogue", "Folder", "grid", "resolutions", f"{config.deviceScreenWidthVar}x{config.deviceScreenHeightVar}")
        os.makedirs(output_system_logos_path, exist_ok=True)
        resize_system_logos(system_logos_path, output_system_logos_path,grid_cell_size,grid_image_padding,circular_grid=False)
    if not "Generating for lanuage on muxlaunch":
        horizontalLogoSize = getHorizontalLogoSize(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "explore.png"), 1, config)
        paddingBetweenLogos = (int(config.deviceScreenWidthVar)-(horizontalLogoSize[0]*4))/(4+1)

        bubble_height = min((int(config.deviceScreenHeightVar)*36.3)/480,(int(config.deviceScreenWidthVar)*36.3)/640)
        effective_text_padding_top = 4

        combined_height = bubble_height+horizontalLogoSize[1]
        heightAbove_logo = (int(config.deviceScreenHeightVar)-combined_height)/2

        grid_total_width = int(config.deviceScreenWidthVar)-paddingBetweenLogos

        grid_column_count = 4
        grid_row_count = 2

        grid_row_height = heightAbove_logo+combined_height+effective_text_padding_top
        grid_column_width = int(grid_total_width/grid_column_count)
        cell_inner_padding = 0
        grid_location_x = paddingBetweenLogos/2
        grid_location_y = 0
        grid_cell_width = grid_column_width-2*cell_inner_padding
        grid_cell_height = grid_row_height-2*cell_inner_padding
        replacementStringMap["muxlaunch"]["{grid_location_x}"] = grid_location_x
        replacementStringMap["muxlaunch"]["{grid_location_y}"] = grid_location_y
        replacementStringMap["muxlaunch"]["{grid_column_count}"] = grid_column_count
        replacementStringMap["muxlaunch"]["{grid_row_count}"] = grid_row_count
        replacementStringMap["muxlaunch"]["{grid_row_height}"] = grid_row_height
        replacementStringMap["muxlaunch"]["{grid_column_width}"] = grid_column_width
        replacementStringMap["muxlaunch"]["{grid_cell_width}"] = grid_cell_width
        replacementStringMap["muxlaunch"]["{grid_cell_height}"] = grid_cell_height
        replacementStringMap["muxlaunch"]["{grid_cell_radius}"] = 0
        replacementStringMap["muxlaunch"]["{grid_cell_focus_background_alpha}"] = 0
        replacementStringMap["muxlaunch"]["{grid_cell_default_image_alpha}"] = 0
        replacementStringMap["muxlaunch"]["{grid_cell_default_image_recolour_alpha}"] = 0
        replacementStringMap["muxlaunch"]["{grid_cell_default_text_alpha}"] = 255
        replacementStringMap["muxlaunch"]["{grid_cell_focus_image_alpha}"] = 0
        replacementStringMap["muxlaunch"]["{grid_cell_focus_image_recolour_alpha}"] = 0
        replacementStringMap["muxlaunch"]["{grid_cell_focus_text_alpha}"] = 255
        
    for fileName in replacementStringMap.keys():
        shutil.copy2(templateSchemeFile,os.path.join(newSchemeDir,f"{fileName}.ini"))
        for stringToBeReplaced in replacementStringMap["default"].keys():
            replacement = replacementStringMap[fileName].get(stringToBeReplaced,replacementStringMap["default"][stringToBeReplaced])
            replace_in_file(os.path.join(newSchemeDir,f"{fileName}.ini"), stringToBeReplaced, str(replacement))


    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall"), exist_ok=True)

    if config.include_overlay_var:
        shutil.copy2(os.path.join(internal_files_dir,"Assets", "Overlays",f"{config.deviceScreenWidthVar}x{config.deviceScreenHeightVar}",f"{config.selected_overlay_var}.png"),os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","overlay.png"))
    
    ## GLYPH STUFF
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","glyph","footer"), exist_ok=True)
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","glyph","header"), exist_ok=True)

    muosSpaceBetweenItems = 2
    footerHeight = int(config.deviceScreenHeightVar)-(individualItemHeight*int(config.itemsPerScreenVar))-int(config.contentPaddingTopVar)+muosSpaceBetweenItems
    button_height = int((footerHeight-(int(config.VBG_Vertical_Padding_entry)*2))*(2/3)) # Change this if overlayed
    in_bubble_font_size = round(button_height*(24/40))

    buttonsToGenerate = ["A","B","C","MENU","X","Y","Z"]
    for button in buttonsToGenerate:
        button_image = generateIndividualButtonGlyph(button,selected_font_path,accent_hex,render_factor, button_height,config.physical_controler_layout_var)
        button_image = button_image.resize((int(button_image.size[0]/render_factor),int(button_image.size[1]/render_factor)), Image.LANCZOS)
        button_image.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","glyph","footer",f"{button.lower()}.png"), format='PNG')
    capacities = [0,10,20,30,40,50,60,70,80,90,100]
    networkGlyphNames = ["network_active", "network_normal"]
    if float(config.header_glyph_height_var) < 10:
        raise ValueError("Header Glyph Height Too Small!")
    elif float(config.header_glyph_height_var) > int(config.headerHeightVar):
        raise ValueError("Header Glyph Height Too Large!")
    else:
        heightOfGlyph = int(float(config.header_glyph_height_var))

    for capacity in capacities:
        try:
            capacity_image_path = os.path.join(internal_files_dir,"Assets","glyphs",f"{BatteryStyleOptionsDict[config.battery_style_var]}{capacity}[5x].png") # auto works with options, like alternative 1 alternative 2 default etc...
        except:
            raise Exception("Battery Style not found")
        capacity_image = Image.open(capacity_image_path)
        capacity_image = capacity_image.resize((int(heightOfGlyph*(capacity_image.size[0]/capacity_image.size[1])),heightOfGlyph), Image.LANCZOS)
        capacity_image.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","glyph","header",f"capacity_{capacity}.png"), format='PNG')

        try:
            capacity_charging_image_path = os.path.join(internal_files_dir,"Assets","glyphs",f"{BatteryChargingStyleOptionsDict[config.battery_charging_style_var]}{capacity}[5x].png") # auto works with options, like alternative 1 alternative 2 default etc...
        except:
            raise Exception("Battery Charging Style not found")
        capacity_charging_image = Image.open(capacity_charging_image_path)
        capacity_charging_image = capacity_charging_image.resize((int(heightOfGlyph*(capacity_charging_image.size[0]/capacity_charging_image.size[1])),heightOfGlyph), Image.LANCZOS)
        capacity_charging_image.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","glyph","header",f"capacity_charging_{capacity}.png"), format='PNG')

    for networkGlyph in networkGlyphNames:
        input_image_path = os.path.join(internal_files_dir,"Assets","glyphs",f"{networkGlyph}[5x].png")
        image = Image.open(input_image_path)
        image = image.resize((int(heightOfGlyph*(image.size[0]/image.size[1])),heightOfGlyph), Image.LANCZOS)
        image.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","glyph","header",f"{networkGlyph}.png"), format='PNG')

    ## FONT STUFF
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","font","panel"), exist_ok=True) #Font binaries stuff
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","font","footer"), exist_ok=True) #Font binaries stuff
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","font","header"), exist_ok=True) #Font binaries stuff
    shutil.copy2(os.path.join(internal_files_dir,"Assets","Font","Binaries",f"BPreplayBold-unhinted-{int(fontSize)}.bin"),os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","font","panel","default.bin"))
    muxarchive_font_size_640 = 17
    muxarchive_font_size = math.floor(muxarchive_font_size_640*(int(config.deviceScreenWidthVar)/640))
    if fontSize > muxarchive_font_size:
        shutil.copy2(os.path.join(internal_files_dir,"Assets","Font","Binaries",f"BPreplayBold-unhinted-{int(muxarchive_font_size)}.bin"),os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","font","panel","muxarchive.bin"))
    muxpicker_font_size_640 = 18
    muxpicker_font_size = math.floor(muxpicker_font_size_640*(int(config.deviceScreenWidthVar)/640))
    if fontSize > muxpicker_font_size:
        shutil.copy2(os.path.join(internal_files_dir,"Assets","Font","Binaries",f"BPreplayBold-unhinted-{int(muxpicker_font_size)}.bin"),os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","font","panel","muxpicker.bin"))
    
    if config.enable_game_switcher_var:
        gameSwitcherFontSize = bottom_bar_height_over_footer * 0.55
        gameSwitcherFontSize = int(fontSize)
        shutil.copy2(os.path.join(internal_files_dir,"Assets","Font","Binaries",f"BPreplayBold-unhinted-{int(gameSwitcherFontSize)}.bin"),os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","font","panel","muxhistory.bin"))
    shutil.copy2(os.path.join(internal_files_dir,"Assets","Font","Binaries",f"BPreplayBold-unhinted-{int(20)}.bin"),os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","font","default.bin"))


    ## FOOTER FONT STUFF
    shutil.copy2(os.path.join(internal_files_dir,"Assets","Font","Binaries",f"BPreplayBold-unhinted-{in_bubble_font_size}.bin"),os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","font","footer","default.bin"))
    headerFontSize = int(int((int(int(config.header_text_height_var)*render_factor)*(4/3))/render_factor))
    ## HEADER FONT STUFF
    shutil.copy2(os.path.join(internal_files_dir,"Assets","Font","Binaries",f"BPreplayBold-unhinted-{headerFontSize}.bin"),os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","font","header","default.bin"))

    ## IMAGE STUFF
    bootlogoimage = generatePilImageBootLogo(config.bgHexVar,config.deselectedFontHexVar,config.bubbleHexVar,render_factor,config).resize((int(config.deviceScreenWidthVar),int(config.deviceScreenHeightVar)), Image.LANCZOS)
    bootlogoimage.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","bootlogo.bmp"), format='BMP')
    progress_bar['value'] +=1

    chargingimage = generatePilImageBootScreen(config.bgHexVar,
                                               config.deselectedFontHexVar,
                                               config.iconHexVar,
                                               "CHARGING...",
                                               render_factor,
                                               config,
                                               icon_path=os.path.join(internal_files_dir, "Assets", "ChargingLogo[5x].png")).resize((int(config.deviceScreenWidthVar),int(config.deviceScreenHeightVar)), Image.LANCZOS)
    chargingimage.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxcharge.png"), format='PNG')
    progress_bar['value'] +=1

    loadingimage = generatePilImageBootScreen(config.bgHexVar,
                                               config.deselectedFontHexVar,
                                               config.iconHexVar,
                                               "LOADING...",
                                               render_factor,
                                               config).resize((int(config.deviceScreenWidthVar),int(config.deviceScreenHeightVar)), Image.LANCZOS)
    loadingimage.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxstart.png"), format='PNG')
    progress_bar['value'] +=1

    shutdownimage = generatePilImageBootScreen(config.bgHexVar,
                                               config.deselectedFontHexVar,
                                               config.iconHexVar,
                                               "Shutting Down...",
                                               render_factor,
                                               config).resize((int(config.deviceScreenWidthVar),int(config.deviceScreenHeightVar)), Image.LANCZOS)
    shutdownimage.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","shutdown.png"), format='PNG')
    progress_bar['value'] +=1

    rebootimage = generatePilImageBootScreen(config.bgHexVar,
                                               config.deselectedFontHexVar,
                                               config.iconHexVar,
                                               "Rebooting...",
                                               render_factor,
                                               config).resize((int(config.deviceScreenWidthVar),int(config.deviceScreenHeightVar)), Image.LANCZOS)
    rebootimage.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","reboot.png"), format='PNG')
    progress_bar['value'] +=1

    defaultimage = generatePilImageDefaultScreen(config.bgHexVar,render_factor,config).resize((int(config.deviceScreenWidthVar),int(config.deviceScreenHeightVar)), Image.LANCZOS)
    defaultimage.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","default.png"), format='PNG')
    progress_bar['value'] +=1

    #TODO If implimented it would be great to only set these once as a default.png type thing, and then make it work in every menu

    notImplimented = ["muxnetwork", "muxassign", "muxstorage", "muxtester"] # Maybe Collections

    page_button_map = {"muxapp":        [["B", "BACK"],["A", "LAUNCH"]], # Applications
                       "muxarchive":    [["B", "BACK"],["A", "EXTRACT"]], # Archive Manager
                       "muxcollect":    [["MENU", "INFO"],["Y", "NEW"], ["X", "REMOVE"], ["B", "BACK"], ["A", "OPEN"]], # Collections
                       "muxconfig":     [["B", "BACK"],["A", "SELECT"]], # Configurations
                       "muxconnect":    [["B", "BACK"],["A", "SELECT"]], # Connectivitiy
                       "muxcustom":     [["B", "BACK"],["A", "SELECT"]], # Customisation
                       "muxgov":        [["Y", "RECURSIVE"],["X", "DIRECTORY"],["A", "INDIVIDUAL"],["B", "BACK"]], # Governor
                       "muxhdmi":       [["B", "SAVE"]], # HDMI SETTINGS
                       "muxhistory":    [["MENU", "INFO"],["Y", "COLLECT"], ["X", "REMOVE"], ["B", "BACK"], ["A", "OPEN"]], # History
                       "muxinfo":       [["B", "BACK"],["A", "SELECT"]], # Information
                       "muxlanguage":   [["B", "BACK"],["A", "SELECT"]], # Language
                       "muxnetprofile": [["Y", "REMOVE"],["X", "SAVE"],["B", "BACK"]], # Network Profile
                       "muxnetscan":    [["X", "RESCAN"], ["B", "BACK"],["A", "USE"]], # Network Scan
                       "muxoption":     [["B", "BACK"],["A", "SELECT"]], # Content Options
                       "muxpass":       [["B", "BACK"],["A", "SELECT"]], # TODO This is the password screen CHECK THIS IS CORRECT
                       "muxpicker":     [["Y", "SAVE"], ["B", "BACK"],["A", "SELECT"]], # Theme, Retroarch, and Catalogue Picker
                       "muxplore":      [["MENU","INFO"],["Y", "COLLECT"],["X", "REFRESH"],["B", "BACK"],["A", "OPEN"]], # Explore
                       "muxpower":      [["B", "SAVE"]], # Power Settings
                       "muxrtc":        [["B", "SAVE"]], # Date and Time
                       "muxsearch":     [["X", "CLEAR"],["B", "BACK"],["A", "SELECT"]], # Search Content
                       "muxshot":       [["X", "REMOVE"],["B", "BACK"],["A", "SELECT"]], # Screenshot
                       "muxsnapshot":   [["THIS", "SNAPSHOT"]], # Unknown
                       "muxspace":      [["B", "BACK"]], # Storage Space
                       "muxsysinfo":    [["B", "BACK"]], # System Details
                       "muxtask":       [["B", "BACK"],["A", "LAUNCH"]], # Task Toolkit
                       "muxtimezone":   [["B", "BACK"],["A", "SELECT"]], # Timezone
                       "muxtweakadv":   [["B", "SAVE"]], # Advanced Settings
                       "muxtweakgen":   [["B", "SAVE"]], # General Settings
                       "muxvisual":     [["B", "SAVE"]], # Interface Options
                       "muxwebserv":    [["B", "SAVE"]]} # Web Services
    if config.main_menu_style_var == "Vertical":
        page_button_map["muxlaunch"] = [["A", "SELECT"]]
    
    # allScreens = "Helper Scripts\MenuItemsGenerator\screen_items_output.txt"

    # page_button_map = {}
    # with open(allScreens, 'r') as f:
    #     lines = f.readlines()
    
    # current_screen = None
    # for line in lines:
    #     # Remove any whitespace or newline characters
    #     line = line.strip()
    #     # Check for a screen line. The expected format is "Screen: <screen_name>"
    #     if line.startswith("Screen:"):
    #         # Get the screen name (everything after "Screen:")
    #         current_screen = line.split("Screen:")[1].strip()
    #         # Immediately add the entry with the uppercase version of the screen name
    #         page_button_map[current_screen] = [["THIS", current_screen.upper()]]
                       
    imageCache = {}

    for page in page_button_map.keys():
        buttonsString = "".join(["".join([f"{button[0]}:{button[1]},"]) for button in page_button_map[page]])
        visualbuttonoverlay = imageCache.get(buttonsString, None)
        if visualbuttonoverlay is None:
            imageCache[buttonsString] = generateMuOSBackgroundOverlay(page_button_map[page],selected_font_path,config.footerBubbleHexVar,render_factor,config,lhsButtons=[["POWER","SLEEP"]]).resize((int(config.deviceScreenWidthVar), int(config.deviceScreenHeightVar)), Image.LANCZOS)
            visualbuttonoverlay = imageCache[buttonsString]
        visualbuttonoverlay.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall",f"{page}.png"), format='PNG')
        progress_bar['value'] +=1

    
    if False: ## Testing converting font in generator
        try:
            # Define the command
            command = [
                'lv_font_conv',
                '--bpp', '4',
                '--size', str(40),
                '--font', os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf"),
                '-r', '0x20-0x7F',
                '--format', 'bin',
                '--no-compress',
                '--no-prefilter',
                '-o', os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}", "Assets", "font","default.bin")
            ]

            # Execute the command
            result = subprocess.run(command,shell=True )
        except Exception as e:
            raise ValueError(f"Error converting font: {e}")
    
    itemsList = []
    if config.version_var[0:9] == "muOS 2410":
        workingMenus = menus2405_3

    else:
        raise ValueError("You Haven't Selected a muOS Version")
    
    workingMenus = [["muxlaunch",[["Content Explorer","explore"],
                                    ["Collections","collection"],
                                    ["History","history"],
                                    ["Applications","apps"],
                                    ["Information","info"],
                                    ["Configuration","config"],
                                    ["Reboot Device","reboot"],
                                    ["Shutdown Device","shutdown"]]]]

    for index, menu in enumerate(workingMenus):
        itemsList.append([])
        for item in menu[1]:
            itemsList[index].append([item[0],"Menu",item[1]]), 

    for index, menu in enumerate(workingMenus):
        if menu[0] == "muxdevice":
            ContinuousFolderImageGen(progress_bar,menu[0],itemsList[index],textPadding,rectanglePadding,ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}","image","static"),config, threadNumber=threadNumber)
        elif menu[0] == "muxlaunch":
            if config.main_menu_style_var == "Horizontal":
                HorizontalMenuGen(progress_bar,menu[0],itemsList[index], bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, icon_hex,render_factor, os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}","image","static"), variant = "Horizontal",config=config, threadNumber=threadNumber)
            elif config.main_menu_style_var == "Alt-Horizontal":
                HorizontalMenuGen(progress_bar,menu[0],itemsList[index], bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, icon_hex,render_factor, os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}","image","static"), variant = "Alt-Horizontal",config=config, threadNumber=threadNumber)

        else:
            ContinuousFolderImageGen(progress_bar,menu[0],itemsList[index],textPadding,rectanglePadding,ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}","image","static"),config, threadNumber=threadNumber)
    fakeprogressbar={'value':0}
    fakeprogressbar['maximum']=1
    if config.main_menu_style_var == "Horizontal":
        previewImage = generatePilImageHorizontal(fakeprogressbar,
                                            0,
                                            config.bgHexVar,
                                            config.selectedFontHexVar,
                                            config.deselectedFontHexVar,
                                            config.bubbleHexVar,
                                            config.iconHexVar,
                                            render_factor,
                                            config,
                                            transparent=False,
                                            forPreview=True)
    elif config.main_menu_style_var == "Alt-Horizontal":
        previewImage = generatePilImageAltHorizontal(fakeprogressbar,
                                            0,
                                            config.bgHexVar,
                                            config.selectedFontHexVar,
                                            config.deselectedFontHexVar,
                                            config.bubbleHexVar,
                                            config.iconHexVar,
                                            render_factor,
                                            config,
                                            transparent=False,
                                            forPreview=True)
    elif config.main_menu_style_var == "Vertical":
        previewImage = generatePilImageVertical(fakeprogressbar,0,
                                        "muxlaunch",
                                        itemsList[index][0:int(config.items_per_screen_entry)],
                                        int(config.textPaddingVar),
                                        int(config.bubblePaddingVar),
                                        int(config.items_per_screen_entry),
                                        config.bgHexVar,
                                        config.selectedFontHexVar,
                                        config.deselectedFontHexVar,
                                        config.bubbleHexVar
                                        ,render_factor,config,transparent=False,
                                        forPreview=True)
    preview_size = (int(0.45*int(config.deviceScreenWidthVar)), int(0.45*int(config.deviceScreenHeightVar)))
    if int(config.deviceScreenWidthVar) == 720 and int(config.deviceScreenHeightVar) == 720:
        preview_size = (340,340)
    smallPreviewImage = previewImage.resize(preview_size, Image.LANCZOS)
    smallPreviewImage.save(os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}","preview.png"))
    if config.developer_preview_var:
        developerPreviewImage = previewImage.resize((int(config.deviceScreenWidthVar),int(config.deviceScreenHeightVar)), Image.LANCZOS)
        developerPreviewImage.save(os.path.join(internal_files_dir,f"TempPreview{threadNumber}[{config.deviceScreenWidthVar}x{config.deviceScreenHeightVar}].png"))
def select_alternate_menu_names():
    if os.path.exists(global_config.alt_text_path):
        menu_names_grid = MenuNamesGrid(root, menuNameMap, global_config.alt_text_path)
    elif os.path.exists(os.path.join(script_dir,global_config.alt_text_path)):
        menu_names_grid = MenuNamesGrid(root, menuNameMap, os.path.join(script_dir,global_config.alt_text_path))
    else:
        menu_names_grid = MenuNamesGrid(root, menuNameMap, os.path.join(script_dir,"AlternateMenuNames.json"))
    root.wait_window(menu_names_grid)
    on_change()


class GridHelper:
    def __init__(self, root):
        self.root = root
        self.row = 0
        self.column = 0

    def add(self, widget, colspan=1, rowspan=1, next_row=False, **kwargs):
        widget.grid(row=self.row, column=self.column, columnspan=colspan, rowspan=rowspan, **kwargs)
        if next_row:
            self.row += 1
            self.column = 0
        else:
            self.column += colspan

class MenuNamesGrid(tk.Toplevel):
    def __init__(self, parent, data, AlternateMenuNamesPath):
        super().__init__(parent)
        self.title("Alternate Menu Names Editor")

        self.data = data
        self.entries = {}
        self.create_widgets()
        self.centre_on_parent(parent)
        self.grab_set()

    def create_widgets(self):        
        # Split data into two halves
        items = list(self.data.items())
        half_index = len(items) // 2
        first_half = items[:half_index]
        second_half = items[half_index:]        

        # Populate the first half
        for i, (key, value) in enumerate(first_half):
            # Create read-only key label
            key_label = ttk.Label(self, text=key)
            key_label.grid(row=i, column=0, padx=5, pady=5, sticky='w')

            # Create editable value entry
            value_entry = ttk.Entry(self, width="50")
            value_entry.insert(0, value)
            value_entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            self.entries[key] = value_entry

        # Add space between the two halves
        spacer_label = ttk.Label(self, text="")
        spacer_label.grid(row=0, column=2, padx=20, pady=5)

        # Populate the second half
        for i, (key, value) in enumerate(second_half):
            # Create read-only key label
            key_label = ttk.Label(self, text=key)
            key_label.grid(row=i, column=3, padx=5, pady=5, sticky='w')

            # Create editable value entry
            value_entry = ttk.Entry(self, width="50")
            value_entry.insert(0, value)
            value_entry.grid(row=i, column=4, padx=5, pady=5, sticky='w')
            self.entries[key] = value_entry
            
        # Save button
        save_button = ttk.Button(self, text="Save", command=self.save)
        save_button.grid(row=max(len(first_half), len(second_half)), column=0, columnspan=5, pady=10)
    
    def centre_on_parent(self, parent):
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2

        self.geometry(f'{self.winfo_width()}x{self.winfo_height()}+{x}+{y}')
    
    def save(self):
        for key, entry in self.entries.items():
            self.data[key] = entry.get()
        if os.path.exists(alt_text_path.get()):
            with open(alt_text_path.get(), 'w', newline='\n',encoding='utf-8') as json_file:
                json.dump(menuNameMap, json_file, indent=2)
        elif os.path.exists(os.path.join(script_dir,alt_text_path.get())):
            with open(os.path.join(script_dir,alt_text_path.get()), 'w', newline='\n',encoding='utf-8') as json_file:
                json.dump(menuNameMap, json_file, indent=2)
        else:
            with open(os.path.join(script_dir,"AlternateMenuNames.json"), 'w', newline='\n',encoding='utf-8') as json_file:
                json.dump(menuNameMap, json_file, indent=2)        
        
        self.grab_release()
        self.destroy()

def on_mousewheel(event,canvas):
    if platform.system() == 'Windows':
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    elif platform.system() == 'Darwin':
        canvas.yview_scroll(int(-1 * event.delta), "units")
    else:
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")

def on_shiftmousewheel(event, canvas):
    if platform.system() == 'Windows':
        canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
    elif platform.system() == 'Darwin':
        canvas.xview_scroll(int(-1 * event.delta), "units")
    else:
        if event.num == 4:
            canvas.xview_scroll(-1, "units")
        elif event.num == 5:
            canvas.xview_scroll(1, "units")
def update_slider_label():
    pass


def start_theme_task():
    save_settings(global_config)
    barrier = threading.Barrier(2)
        # Create a new Toplevel window for the loading bar
    loading_window = tk.Toplevel(root)
    loading_window.title("Generating...")
    loading_window.geometry("300x100")
    
    # Create a Progressbar widget in the loading window
    progress_bar = ttk.Progressbar(loading_window, orient="horizontal", length=280, mode="determinate")
    progress_bar.pack(pady=20)

    match = re.search(r"\[(\d+)x(\d+)\]", global_config.device_type_var)
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
    threading.Thread(target=generate_theme, args=(progress_bar, loading_window,-1,global_config,barrier,all_resolutions,assumed_res)).start()

def start_bulk_theme_task():
    save_settings(global_config)
        # Create a new Toplevel window for the loading bar
    themes = global_config.load_premade_themes(os.path.join(script_dir,"PremadeThemes.json"))

    threading.Thread(target=generate_themes, args=(themes,)).start()



def on_resize(event):
    right_pane_width = image_frame.winfo_width()

def select_color(entry):
    """Opens a color picker and sets the selected color to the given entry."""
    current_color = "#"+entry.get()  # Get the current color from the entry
    try:
        # Validate the current color to ensure it's a valid hex color
        if current_color:
            color_code = colorchooser.askcolor(initialcolor=current_color, title="Choose Color")[1]
        else:
            color_code = colorchooser.askcolor(title="Choose Color")[1]
    except Exception:
        # Fallback in case the initial color is invalid
        color_code = colorchooser.askcolor(title="Choose Color")[1]

    if color_code:  # If a color was selected
        entry.delete(0, tk.END)
        entry.insert(0, color_code[1:])


root = tk.Tk()
root.title("MinUI Theme Generator")
root.minsize(1080, 500)  # Set a minimum size for the window

# Get the screen height
screen_height = root.winfo_screenheight()
window_height = int(min(screen_height*0.9, 1720))

root.geometry(f"1280x{window_height}")  # Set a default size for the window

subtitle_font = font.Font(family="Helvetica", size=14, weight="bold")
title_font = font.Font(family="Helvetica", size=20, weight="bold")

# Variables for user input
roms_directory_path = tk.StringVar()
application_directory_path = tk.StringVar()
name_json_path = tk.StringVar()
background_image_path = tk.StringVar()
bootlogo_image_path = tk.StringVar()
alt_font_path =  tk.StringVar()
alt_text_path = tk.StringVar()
box_art_directory_path = tk.StringVar()
catalogue_directory_path = tk.StringVar()
theme_directory_path = tk.StringVar()
am_theme_directory_path = tk.StringVar()
version_var = tk.StringVar()
device_type_var = tk.StringVar()
global_alignment_var = tk.StringVar()
selected_overlay_var = tk.StringVar()
physical_controler_layout_var = tk.StringVar()
muos_button_swap_var = tk.StringVar()
main_menu_style_var = tk.StringVar()
horizontal_menu_behaviour_var = tk.StringVar()
battery_charging_style_var = tk.StringVar()
battery_style_var = tk.StringVar()
clock_format_var = tk.StringVar()
clock_alignment_var = tk.StringVar()
header_glyph_alignment_var = tk.StringVar()
page_title_alignment_var = tk.StringVar()
show_file_counter_var = tk.IntVar()
show_console_name_var = tk.IntVar()
show_charging_battery_var = tk.IntVar()
show_hidden_files_var = tk.IntVar()
include_overlay_var = tk.IntVar()
show_glyphs_var = tk.IntVar()
show_clock_bubbles_var = tk.IntVar()
show_glyphs_bubbles_var = tk.IntVar()
join_header_bubbles_var = tk.IntVar()
enable_game_switcher_var = tk.IntVar()
enable_grid_view_explore_var = tk.IntVar()
alternate_menu_names_var = tk.IntVar()
remove_right_menu_guides_var = tk.IntVar()
remove_left_menu_guides_var = tk.IntVar()
page_by_page_var = tk.IntVar()
transparent_text_var = tk.IntVar()
override_folder_box_art_padding_var = tk.IntVar()
use_alt_font_var = tk.IntVar()
use_custom_background_var=tk.IntVar()
use_custom_bootlogo_var = tk.IntVar()
am_ignore_theme_var = tk.IntVar()
am_ignore_cd_var = tk.IntVar()
advanced_error_var = tk.IntVar()
developer_preview_var = tk.IntVar()

# Create a PanedWindow to divide the window into left and right sections
paned_window = PanedWindow(root, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED,bg = "#ff0000", bd = 0)
paned_window.pack(fill=tk.BOTH, expand=True)

# Left side - scrollable section
left_frame = tk.Frame(paned_window)
canvas = tk.Canvas(left_frame)
scrollbar = Scrollbar(left_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Add left_frame to the PanedWindow
paned_window.add(left_frame)

# Bind mouse wheel events based on the platform
if platform.system() == 'Darwin':
    canvas.bind_all("<MouseWheel>", lambda event: on_mousewheel(event, canvas))
    canvas.bind_all("<Shift-MouseWheel>", lambda event: on_shiftmousewheel(event, canvas))
else:
    canvas.bind_all("<MouseWheel>", lambda event: on_mousewheel(event, canvas))
    canvas.bind_all("<Shift-MouseWheel>", lambda event: on_shiftmousewheel(event, canvas))
    canvas.bind_all("<Button-4>", lambda event: on_mousewheel(event, canvas))  # For Linux
    canvas.bind_all("<Button-5>", lambda event: on_mousewheel(event, canvas))  # For Linux

# Create the grid helper
grid_helper = GridHelper(scrollable_frame)

# Create the GUI components
grid_helper.add(tk.Label(scrollable_frame, text="Configurations", font=title_font), colspan=3, sticky="w", next_row=True)
grid_helper.add(tk.Label(scrollable_frame, text="Device Configurations", font=subtitle_font), colspan=3, sticky="w", next_row=True)
deviceScreenWidthVar = tk.StringVar()
deviceScreenHeightVar = tk.StringVar()

grid_helper.add(tk.Label(scrollable_frame, text="Device Type"), sticky="w")

deviceTypeOptions = ["Other [640x480]",
                     "RG CubeXX [720x720]",
                     "RG34XX [720x480]",
                     "576p [720x576]",
                     "TrimUI Brick [1024x768]",
                     "HD [1280x720]",
                     "Full HD [1920x1080]"]

device_type_option_menu = tk.OptionMenu(scrollable_frame, device_type_var, *deviceTypeOptions)
grid_helper.add(device_type_option_menu, colspan=3, sticky="w", next_row=True)


grid_helper.add(tk.Label(scrollable_frame, text="muOS Version"), sticky="w")
options = ["muOS 2410.1 Banana", "muOS 2410.3 AW BANANA"]
option_menu = tk.OptionMenu(scrollable_frame, version_var, *options)
grid_helper.add(option_menu, colspan=3, sticky="w", next_row=True)


# Define the StringVar variables
textPaddingVar = tk.StringVar()
VBG_Horizontal_Padding_var = tk.StringVar()
header_glyph_horizontal_left_padding_var = tk.StringVar()
header_glyph_horizontal_right_padding_var = tk.StringVar()
header_glyph_height_var = tk.StringVar()
header_text_height_var = tk.StringVar()
header_glyph_bubble_height_var = tk.StringVar()
header_text_bubble_height_var = tk.StringVar()
clockHorizontalLeftPaddingVar = tk.StringVar()
clockHorizontalRightPaddingVar = tk.StringVar()
pageTitlePaddingVar = tk.StringVar()
VBG_Vertical_Padding_var = tk.StringVar()
bubblePaddingVar = tk.StringVar()
itemsPerScreenVar = tk.StringVar()
approxFooterHeightVar = tk.StringVar()
contentPaddingTopVar = tk.StringVar()
headerHeightVar = tk.StringVar()
boxArtPaddingVar = tk.StringVar()
folderBoxArtPaddingVar = tk.StringVar()
font_size_var = tk.StringVar()
bgHexVar = tk.StringVar()
selectedFontHexVar = tk.StringVar()
deselectedFontHexVar = tk.StringVar()
bubbleHexVar = tk.StringVar()
footerBubbleHexVar = tk.StringVar()
iconHexVar = tk.StringVar()
batteryChargingHexVar = tk.StringVar()
maxBoxArtWidth = tk.StringVar()
previewConsoleNameVar = tk.StringVar()



# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="General Configurations", font=subtitle_font), sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Physical Controller Layout"), sticky="w")
physicalControllerLayout = ["Nintendo", 
           "Xbox",
           "PlayStation",
           "Universal"]
physical_controller_layout_menu = tk.OptionMenu(scrollable_frame, physical_controler_layout_var, *physicalControllerLayout)
grid_helper.add(physical_controller_layout_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="muOS Control Scheme"), sticky="w")
muosButtonSwap = ["Retro", 
           "Modern"]
muos_button_swap_menu = tk.OptionMenu(scrollable_frame, muos_button_swap_var, *muosButtonSwap)
grid_helper.add(muos_button_swap_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Use Game Switcher*", variable=enable_game_switcher_var), sticky="w", next_row=True)
grid_helper.add(tk.Label(scrollable_frame, text="*Not recommended Very Experimental",fg="#f00"), sticky="w",next_row=True)


grid_helper.add(tk.Checkbutton(scrollable_frame, text="Use Grid View in Explore*", variable=enable_grid_view_explore_var), sticky="w", next_row=True)
grid_helper.add(tk.Label(scrollable_frame, text="*Won't show in preview",fg="#f40"), sticky="w",next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Main Menu Style"), sticky="w")
MainMenuStyleOptions = ["Horizontal", "Vertical", "Alt-Horizontal"]
main_menu_style_option_menu = tk.OptionMenu(scrollable_frame, main_menu_style_var, *MainMenuStyleOptions)
grid_helper.add(main_menu_style_option_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Horizontal Menu Behaviour"), sticky="w")
HorizontalMenuBehaviourOptions = ["Wrap to Row", "Don't wrap to row"]
horizontal_menu_behaviour_option_menu = tk.OptionMenu(scrollable_frame, horizontal_menu_behaviour_var, *HorizontalMenuBehaviourOptions)
grid_helper.add(horizontal_menu_behaviour_option_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Include Overlay", variable=include_overlay_var), sticky="w")
overlayOptions = ["muOS Default CRT Overlay", 
           "Grid_2px_10",
           "Grid_2px_20", 
           "Grid_2px_30", 
           "Grid_Thin_2px_10", 
           "Grid_Thin_2px_20", 
           "Grid_Thin_2px_30", 
           "Perfect_CRT-noframe", 
           "Perfect_CRT"]
overlay_option_menu = tk.OptionMenu(scrollable_frame, selected_overlay_var, *overlayOptions)
grid_helper.add(overlay_option_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Use Custom Bootlogo Image*:", variable=use_custom_bootlogo_var), sticky="w")
grid_helper.add(tk.Entry(scrollable_frame, textvariable=bootlogo_image_path, width=50))
grid_helper.add(tk.Button(scrollable_frame, text="Browse...", command=select_bootlogo_image_path), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="*Will not show up in this programs preview yet",fg="#00f"), sticky="w",next_row=True)


# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

# Section title
grid_helper.add(tk.Label(scrollable_frame, text="Colour Configuration", font=subtitle_font), colspan=3, sticky="w", next_row=True)

# Option for Background Colour
grid_helper.add(tk.Label(scrollable_frame, text="Background Hex Colour: #"), sticky="w")
background_hex_entry = tk.Entry(scrollable_frame, width=50, textvariable=bgHexVar)
grid_helper.add(background_hex_entry)
grid_helper.add(tk.Button(scrollable_frame, text="Pick Color", command=lambda: select_color(background_hex_entry)), next_row=True)

# Option for Selected Font Hex Colour
grid_helper.add(tk.Label(scrollable_frame, text="Selected Font Hex Colour: #"), sticky="w")
selected_font_hex_entry = tk.Entry(scrollable_frame, width=50, textvariable=selectedFontHexVar)
grid_helper.add(selected_font_hex_entry)
grid_helper.add(tk.Button(scrollable_frame, text="Pick Color", command=lambda: select_color(selected_font_hex_entry)), next_row=True)

# Option for Deselected Font Hex Colour
grid_helper.add(tk.Label(scrollable_frame, text="Deselected Font Hex Colour: #"), sticky="w")
deselected_font_hex_entry = tk.Entry(scrollable_frame, width=50, textvariable=deselectedFontHexVar)
grid_helper.add(deselected_font_hex_entry)
grid_helper.add(tk.Button(scrollable_frame, text="Pick Color", command=lambda: select_color(deselected_font_hex_entry)), next_row=True)

# Option for Bubble Hex Colour
grid_helper.add(tk.Label(scrollable_frame, text="Bubble Hex Colour: #"), sticky="w")
bubble_hex_entry = tk.Entry(scrollable_frame, width=50, textvariable=bubbleHexVar)
grid_helper.add(bubble_hex_entry)
grid_helper.add(tk.Button(scrollable_frame, text="Pick Color", command=lambda: select_color(bubble_hex_entry)), next_row=True)

# Option for Footer Bubble Hex Colour
grid_helper.add(tk.Label(scrollable_frame, text="Footer Bubble Hex Colour: #"), sticky="w")
footer_bubble_hex_entry = tk.Entry(scrollable_frame, width=50, textvariable=footerBubbleHexVar)
grid_helper.add(footer_bubble_hex_entry)
grid_helper.add(tk.Button(scrollable_frame, text="Pick Color", command=lambda: select_color(footer_bubble_hex_entry)), next_row=True)

# Option for Icon Hex Colour
grid_helper.add(tk.Label(scrollable_frame, text="Icon Hex Colour: #"), sticky="w")
icon_hex_entry = tk.Entry(scrollable_frame, width=50, textvariable=iconHexVar)
grid_helper.add(icon_hex_entry)
grid_helper.add(tk.Button(scrollable_frame, text="Pick Color", command=lambda: select_color(icon_hex_entry)), next_row=True)

# Option for Battery Charging Colour
grid_helper.add(tk.Label(scrollable_frame, text="Battery Charging Colour: #"), sticky="w")
battery_charging_hex_entry = tk.Entry(scrollable_frame, width=50, textvariable=batteryChargingHexVar)
grid_helper.add(battery_charging_hex_entry)
grid_helper.add(tk.Button(scrollable_frame, text="Pick Color", command=lambda: select_color(battery_charging_hex_entry)), next_row=True)

# Additional options
grid_helper.add(tk.Checkbutton(scrollable_frame, text="[Optional] Override background colour with image", variable=use_custom_background_var), sticky="w")
grid_helper.add(tk.Entry(scrollable_frame, textvariable=background_image_path, width=50))
grid_helper.add(tk.Button(scrollable_frame, text="Browse...", command=select_background_image_path), next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Show Background Through Text on Launch Menu", variable=transparent_text_var), colspan=3, sticky="w", next_row=True)

# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Text Configuration", font=subtitle_font), colspan=3, sticky="w", next_row=True)


grid_helper.add(tk.Label(scrollable_frame, text="Global Text Alignment"), sticky="w")
globalAlignmentOptions = ["Left", "Centre", "Right"]
global_alignment_option_menu = tk.OptionMenu(scrollable_frame, global_alignment_var, *globalAlignmentOptions)
grid_helper.add(global_alignment_option_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Font size (10-55 inclusive):"), sticky="w")
custom_font_size_entry = tk.Entry(scrollable_frame, width=50, textvariable=font_size_var)
grid_helper.add(custom_font_size_entry, next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="*[Optional] Use Custom font:", variable=use_alt_font_var), sticky="w")
grid_helper.add(tk.Entry(scrollable_frame, textvariable=alt_font_path, width=50))
grid_helper.add(tk.Button(scrollable_frame, text="Browse...", command=select_alt_font_path), next_row=True)
grid_helper.add(tk.Label(scrollable_frame,text="*Use if text override characters not supported by default font\n!!!Currently Wont Work In Menus!!! left in as a reminder",fg="#00f"),sticky="w",next_row=True)



grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Header Configurations", font=subtitle_font), sticky="w", next_row=True)

# Option for headerHeight
grid_helper.add(tk.Label(scrollable_frame, text="Header Height (Usually same as padding from top):"), sticky="w")
header_height_entry = tk.Entry(scrollable_frame, width=50, textvariable=headerHeightVar)
grid_helper.add(header_height_entry, next_row=True)

# Option for ItemsPerScreen
grid_helper.add(tk.Label(scrollable_frame, text="Padding from top, for content list (Default 44):"), sticky="w")
content_padding_top_entry = tk.Entry(scrollable_frame, width=50, textvariable=contentPaddingTopVar)
grid_helper.add(content_padding_top_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Show Bubble Behind Clock", variable=show_clock_bubbles_var), sticky="w", next_row=True)
grid_helper.add(tk.Checkbutton(scrollable_frame, text="Show Bubble Behind Glyphs", variable=show_glyphs_bubbles_var), sticky="w", next_row=True)


grid_helper.add(tk.Label(scrollable_frame, text="Header Text Bubble Height:"), sticky="w")
header_text_bubble_height_entry = tk.Entry(scrollable_frame, width=50, textvariable=header_text_bubble_height_var)
grid_helper.add(header_text_bubble_height_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Header glyphs Bubble Height:"), sticky="w")
header_glyph_bubble_height_entry = tk.Entry(scrollable_frame, width=50, textvariable=header_glyph_bubble_height_var)
grid_helper.add(header_glyph_bubble_height_entry, next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Join Header Bubbles Together", variable=join_header_bubbles_var), sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)


grid_helper.add(tk.Label(scrollable_frame, text="Clock Format:"), sticky="w")
clockFormatOptions = ["12 Hour", "24 Hour"]
clock_format_option_menu = tk.OptionMenu(scrollable_frame, clock_format_var, *clockFormatOptions)
grid_helper.add(clock_format_option_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Clock Alignment:"), sticky="w")
alignmentOptions = ["Left", "Centre", "Right"]
clock_alignment_option_menu = tk.OptionMenu(scrollable_frame, clock_alignment_var, *alignmentOptions)
grid_helper.add(clock_alignment_option_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Header Text Height:"), sticky="w")
header_text_height_entry = tk.Entry(scrollable_frame, width=50, textvariable=header_text_height_var)
grid_helper.add(header_text_height_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Left Padding for Clock:"), sticky="w")
clock_horizontal_left_padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=clockHorizontalLeftPaddingVar)
grid_helper.add(clock_horizontal_left_padding_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Right Padding for Clock:"), sticky="w")
clock_horizontal_right_padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=clockHorizontalRightPaddingVar)
grid_helper.add(clock_horizontal_right_padding_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Show Title of page in header", variable=show_console_name_var), sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Page Title Alignment:"), sticky="w")
page_title_alignment_option_menu = tk.OptionMenu(scrollable_frame, page_title_alignment_var, *alignmentOptions)
grid_helper.add(page_title_alignment_option_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Horizontal Padding for Page Title:"), sticky="w")
page_title_padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=pageTitlePaddingVar)
grid_helper.add(page_title_padding_entry, next_row=True)

#grid_helper.add(tk.Label(scrollable_frame, text="[Tip] If you want the time to align left nicely \nwith the bubble you can set the clock alignment to centre,\nand make the left say 10, and set the right to\n640[screen width]-10[left value]-(70/114 depending on clock style)[set]",fg="#00f"), sticky="w",next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Header Glyph Alignment:"), sticky="w")
header_glyph_alignment_option_menu = tk.OptionMenu(scrollable_frame, header_glyph_alignment_var, *alignmentOptions)
grid_helper.add(header_glyph_alignment_option_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Header glyphs Height:"), sticky="w")
header_glyph_height_entry = tk.Entry(scrollable_frame, width=50, textvariable=header_glyph_height_var)
grid_helper.add(header_glyph_height_entry, next_row=True)


grid_helper.add(tk.Label(scrollable_frame, text="Horizontal Left Padding for header glyphs:"), sticky="w")
header_items_horizontal_left_padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=header_glyph_horizontal_left_padding_var)
grid_helper.add(header_items_horizontal_left_padding_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Horizontal Right Padding for header glyphs:"), sticky="w")
header_items_horizontal_right_padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=header_glyph_horizontal_right_padding_var)
grid_helper.add(header_items_horizontal_right_padding_entry, next_row=True)
# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Battery Glyph Style"), sticky="w")
BatteryStyleOptionsDict = {"Default": "capacity_","Percentage":"percentage_capacity_","Alt Percentage":"alt_percentage_capacity_"}
BatteryStyleOptions = list(BatteryStyleOptionsDict.keys())
battery_style_option_menu = tk.OptionMenu(scrollable_frame, battery_style_var, *BatteryStyleOptions)
grid_helper.add(battery_style_option_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Show Charging battery in preview", variable=show_charging_battery_var), sticky="w", next_row=True)


grid_helper.add(tk.Label(scrollable_frame, text="Battery Charging Glyph Style"), sticky="w")
BatteryChargingStyleOptionsDict = {"Default": "capacity_","Percentage":"percentage_capacity_", "Percentage Lightning":"percentage_capacity_charging_", "Alt Percentage":"alt_percentage_capacity_", "Alt Percentage Lightning":"alt_percentage_capacity_charging_", "Lightning 1":"capacity_charging_", "Lightning 2":"alt1_capacity_charging_", "Lightning 3":"alt2_capacity_charging_"}
BatteryChargingStyleOptions = list(BatteryChargingStyleOptionsDict.keys())
battery_charging_style_option_menu = tk.OptionMenu(scrollable_frame, battery_charging_style_var, *BatteryChargingStyleOptions)
grid_helper.add(battery_charging_style_option_menu, colspan=3, sticky="w", next_row=True)

# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)


grid_helper.add(tk.Label(scrollable_frame, text="Content List Configuration", font=subtitle_font), colspan=3, sticky="w", next_row=True)


grid_helper.add(tk.Checkbutton(scrollable_frame, text="Show Glyphs*", variable=show_glyphs_var), sticky="w",next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="*Will not show up in this programs preview yet",fg="#00f"), sticky="w",next_row=True)

# Option for ItemsPerScreen
grid_helper.add(tk.Label(scrollable_frame, text="Items Per Screen (Better if Odd) [5-13 Inclusive]:"), sticky="w")
items_per_screen_entry = tk.Entry(scrollable_frame, width=50, textvariable=itemsPerScreenVar)
grid_helper.add(items_per_screen_entry, next_row=True)

# Option for textPadding
grid_helper.add(tk.Label(scrollable_frame, text="Text Padding:"), sticky="w")
text_padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=textPaddingVar)
grid_helper.add(text_padding_entry, next_row=True)

# Option for rectanglePadding
grid_helper.add(tk.Label(scrollable_frame, text="Bubble Padding:"), sticky="w")
rectangle_padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=bubblePaddingVar)
grid_helper.add(rectangle_padding_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Box Art Max Width (px):"), sticky="w")
max_games_bubble_length_entry = tk.Entry(scrollable_frame, width=50, textvariable=maxBoxArtWidth)
grid_helper.add(max_games_bubble_length_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text=" - This is used to make text not go over your Box Art",fg="#00f"), colspan=3, sticky="w", next_row=True)

# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)
grid_helper.add(tk.Label(scrollable_frame, text="Footer Configurations", font=subtitle_font), sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Approximate Footer Height:"), sticky="w")
individual_item_height_entry = tk.Entry(scrollable_frame, width=50, textvariable=approxFooterHeightVar)
grid_helper.add(individual_item_height_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Horizontal Padding for Visual Button Guides:"), sticky="w")
VBG_Horizontal_Padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=VBG_Horizontal_Padding_var)
grid_helper.add(VBG_Horizontal_Padding_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Vertical Padding for Visual Button Guides:"), sticky="w")
VBG_Vertical_Padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=VBG_Vertical_Padding_var)
grid_helper.add(VBG_Vertical_Padding_entry, next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Remove Left Visual Button Guides", variable=remove_left_menu_guides_var), sticky="w")
grid_helper.add(tk.Checkbutton(scrollable_frame, text="Remove Right Visual Button Guides", variable=remove_right_menu_guides_var), colspan=3, sticky="w", next_row=True)


# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Generation", font=title_font), colspan=2, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Theme Name:"), sticky="w")
theme_name_entry = tk.Entry(scrollable_frame, width=50)
grid_helper.add(theme_name_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Themes Output Directory:"), sticky="w")
grid_helper.add(tk.Entry(scrollable_frame, textvariable=theme_directory_path, width=50))
grid_helper.add(tk.Button(scrollable_frame, text="Browse...", command=select_theme_directory), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Should be '[root]:\\MUOS\\theme' on your muOS SD Card, but it will let you select any folder."), colspan=3, sticky="w", next_row=True)

# Generate button
grid_helper.add(tk.Button(scrollable_frame, text="Generate Theme", command=start_theme_task), sticky="w", next_row=True)
# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)


grid_helper.add(tk.Label(scrollable_frame, text="Developer Options", font=subtitle_font), colspan=2, sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Developer Preview Image Generation [Optional]", variable=developer_preview_var), colspan=3, sticky="w", next_row=True)
# Generate button
grid_helper.add(tk.Button(scrollable_frame, text="Bulk generate themes in predetermined colours", command=start_bulk_theme_task), sticky="w", next_row=True)
# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)
# Spacer row

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Show Advanced Errors", variable=advanced_error_var), colspan=3, sticky="w", next_row=True)



# Create the right frame with canvas and scrollbars
image_frame = tk.Frame(paned_window, width=200)
image_frame.pack(side="right", fill="y")

image_label1 = tk.Label(image_frame)
image_label1.pack()

image_label2 = tk.Label(image_frame)
image_label2.pack()

image_label3 = tk.Label(image_frame)
image_label3.pack()

image_label4 = tk.Label(image_frame)
image_label4.pack()

image_label5 = tk.Label(image_frame)
image_label5.pack()

paned_window.add(image_frame)

paned_window.paneconfig(image_frame,minsize=230)



def update_image_label(image_label, pil_image):
    tk_image = ImageTk.PhotoImage(pil_image)
    image_label.config(image=tk_image)
    image_label.image = tk_image
    #image_label.clear()
def remove_image_from_label(image_label):
    image_label.config(image='')


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


def outline_image_with_inner_gap(image, outline_color=(255, 0, 0), outline_width=5, gap=5):
    # Calculate the size of the new image with the outline and the gap
    new_width = image.width + 2 * (outline_width + gap)
    new_height = image.height + 2 * (outline_width + gap)
    
    # Create a new image with the appropriate size and background color (optional)
    outlined_image = Image.new('RGB', (new_width, new_height), (0, 0, 0))
    
    # Create a drawing context for the new image
    draw = ImageDraw.Draw(outlined_image)
    
    # Draw the outer rectangle for the red outline
    draw.rectangle(
        [0, 0, new_width - 1, new_height - 1],
        outline=outline_color,
        width=outline_width
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

def on_change(*args):
    
    global menuNameMap
    menuNameMap = getAlternateMenuNameDict()
    try:
        preview_overlay_image = Image.open(os.path.join(internal_files_dir, "Assets", "Overlays", f"{global_config.deviceScreenWidthVar}x{global_config.deviceScreenHeightVar}",f"{global_config.selected_overlay_var}.png")).convert("RGBA")
    except:
        pass
    global contentPaddingTop
    try:
        contentPaddingTop = int(global_config.content_padding_top_entry)
    except:
        contentPaddingTop = 40
    
    global background_image

    if (global_config.use_custom_background_var) and os.path.exists(global_config.background_image_path):
        background_image = Image.open(global_config.background_image_path)
    else:
        background_image = None

    global menus2405
    global menus2405_1 ## NOT GLOBALS AHH SORRY HACKY SHOULD REMOVE
    global menus2405_2
    global menus2405_3

    previewApplicationList = []
    if global_config.version_var[0:9] == "muOS 2410":
        index = None
        for i, n in enumerate(menus2405_3):
            if n[0] == "muxapp":
                index = i
                break
        if index!=None:
            previewApplicationList = [[x[0],"menu",x[0]] for x in menus2405_3[index][1]]

    global valid_params
    
    fakeprogressbar={'value':0}
    fakeprogressbar['maximum']=1

    previewRenderFactor = 1
    current_image_size = [640,480]
    if get_current_image(image_label1) is not None:
        current_image_size = get_current_image(image_label1).size
    preview_size = [current_image_size[0]/2,current_image_size[1]/2]
    if image_frame.winfo_width() > 100:
        previewRenderFactor = math.ceil(image_frame.winfo_width()/current_image_size[1])+1 # Affectively anti aliasing in the preview

        preview_size = [int(image_frame.winfo_width()),int(image_frame.winfo_width()*(current_image_size[1]/current_image_size[0]))]
    try:
        if int(global_config.deviceScreenHeightVar) < 240:
            raise ValueError("Device Screen Height must be at least 240")
        if int(global_config.deviceScreenWidthVar) < 320:
            raise ValueError("Device Screen Width must be at least 320")
        if int(global_config.deviceScreenHeightVar) > 4320:
            raise ValueError("Device Screen Height must be at most 4320")
        if int(global_config.deviceScreenWidthVar) > 7680:
            raise ValueError("Device Screen Width must be at most 7680")

        if image_frame.winfo_width() < 100:
            preview_size = [int(int(global_config.deviceScreenWidthVar)/2),int(int(global_config.deviceScreenHeightVar)/2)]
        else:
            
            previewRenderFactor = math.ceil(image_frame.winfo_width()/int(global_config.deviceScreenWidthVar))+1 # Affectively anti aliasing in the preview

            preview_size = [int(image_frame.winfo_width()),int(image_frame.winfo_width()*(int(global_config.deviceScreenHeightVar)/int(global_config.deviceScreenWidthVar)))]
        #preview_size = [int(640/2),int(480/2)]

        # This function will run whenever any traced variable changes
    
        previewItemList = [['Content Explorer', 'Menu', 'explore'], ['Collections', 'Menu', 'collection'], ['History', 'Menu', 'history'], ['Applications', 'Menu', 'apps'], ['Information', 'Menu', 'info'], ['Configuration', 'Menu', 'config'], ['Reboot Device', 'Menu', 'reboot'], ['Shutdown Device', 'Menu', 'shutdown']]
        
        if global_config.main_menu_style_var == "Horizontal":
            image1 = generatePilImageHorizontal(fakeprogressbar,
                                                0,
                                                global_config.bgHexVar,
                                                global_config.selectedFontHexVar,
                                                global_config.deselectedFontHexVar,
                                                global_config.bubbleHexVar,
                                                global_config.iconHexVar,
                                                previewRenderFactor,
                                                global_config,
                                                transparent=False,
                                                forPreview=True).resize(preview_size, Image.LANCZOS)
        elif global_config.main_menu_style_var == "Alt-Horizontal":
            image1 = generatePilImageAltHorizontal(fakeprogressbar,
                                                0,
                                                global_config.bgHexVar,
                                                global_config.selectedFontHexVar,
                                                global_config.deselectedFontHexVar,
                                                global_config.bubbleHexVar,
                                                global_config.iconHexVar,
                                                previewRenderFactor,
                                                global_config,
                                                transparent=False,
                                                forPreview=True).resize(preview_size, Image.LANCZOS)
        elif global_config.main_menu_style_var == "Vertical":
            image1 = generatePilImageVertical(fakeprogressbar,0,
                                            "muxlaunch",
                                            previewItemList[0:int(global_config.items_per_screen_entry)],
                                            int(global_config.textPaddingVar),
                                            int(global_config.bubblePaddingVar),
                                            int(global_config.items_per_screen_entry),
                                            global_config.bgHexVar,
                                            global_config.selectedFontHexVar,
                                            global_config.deselectedFontHexVar,
                                            global_config.bubbleHexVar
                                            ,previewRenderFactor,global_config,transparent=False,
                                            forPreview=True).resize(preview_size, Image.LANCZOS)

        image2 = generatePilImageVertical(fakeprogressbar,0,
                                        "muxapp",
                                        previewApplicationList[0:int(global_config.items_per_screen_entry)],
                                        int(global_config.textPaddingVar),
                                        int(global_config.bubblePaddingVar),
                                        int(global_config.items_per_screen_entry),
                                        global_config.bgHexVar,
                                        global_config.selectedFontHexVar,
                                        global_config.deselectedFontHexVar,
                                        global_config.bubbleHexVar,
                                        previewRenderFactor,
                                        global_config,
                                        fileCounter="1 / " + global_config.items_per_screen_entry,
                                        transparent=False,
                                        forPreview=True).resize(preview_size, Image.LANCZOS)
        
        gameSwitcherOverlay = generateGameSwitcherOverlay(global_config,previewRenderFactor,gameNameForPreview="Goodboy Galaxy", generatingForPreview=True).resize(preview_size, Image.LANCZOS)
        if global_config.enable_game_switcher_var:
            image3 = gameSwitcherOverlay
        else:
            if global_config.main_menu_style_var == "Horizontal":
                image3 = generatePilImageHorizontal(fakeprogressbar,
                                                    4,
                                                    global_config.bgHexVar,
                                                    global_config.selectedFontHexVar,
                                                    global_config.deselectedFontHexVar,
                                                    global_config.bubbleHexVar,
                                                    global_config.iconHexVar,
                                                    previewRenderFactor,
                                                    global_config,
                                                    transparent=False,
                                                    forPreview=True).resize(preview_size, Image.LANCZOS)
            
            elif global_config.main_menu_style_var == "Alt-Horizontal":
                image3 = generatePilImageAltHorizontal(fakeprogressbar,
                                                    4,
                                                    global_config.bgHexVar,
                                                    global_config.selectedFontHexVar,
                                                    global_config.deselectedFontHexVar,
                                                    global_config.bubbleHexVar,
                                                    global_config.iconHexVar,
                                                    previewRenderFactor,
                                                    global_config,
                                                    transparent=False,
                                                    forPreview=True).resize(preview_size, Image.LANCZOS)

        if global_config.include_overlay_var and global_config.selected_overlay_var != "":
            preview_overlay_resized = preview_overlay_image.resize(image1.size, Image.LANCZOS)
            image1.paste(preview_overlay_resized,(0,0),preview_overlay_resized)
            image2.paste(preview_overlay_resized,(0,0),preview_overlay_resized)
            if global_config.main_menu_style_var != "Vertical":
                image3.paste(preview_overlay_resized,(0,0),preview_overlay_resized)
    
        update_image_label(image_label1, image1)
        update_image_label(image_label2, image2)
        if global_config.main_menu_style_var != "Vertical":
            update_image_label(image_label3, image3)
        else:
            remove_image_from_label(image_label3)
        valid_params = True
    except Exception:
        traceback.print_exc()
        if get_current_image(image_label1) != None and get_current_image(image_label2) != None and get_current_image(image_label3):
            if valid_params:
                redOutlineImage1 = outline_image_with_inner_gap(get_current_image(image_label1)).resize(preview_size, Image.LANCZOS)
                redOutlineImage2 = outline_image_with_inner_gap(get_current_image(image_label2)).resize(preview_size, Image.LANCZOS)
                if global_config.main_menu_style_var != "Vertical":
                    redOutlineImage3 = outline_image_with_inner_gap(get_current_image(image_label3)).resize(preview_size, Image.LANCZOS)
                update_image_label(image_label1, redOutlineImage1)
                update_image_label(image_label2, redOutlineImage2)
                if global_config.main_menu_style_var != "Vertical":
                    update_image_label(image_label3, redOutlineImage3)
                valid_params = False
        else:
            raise


def save_settings(config: Config):
    config.device_type_var = device_type_var.get()
    match = re.search(r"\[(\d+)x(\d+)\]", config.device_type_var)
    if match:
        config.deviceScreenWidthVar = int(match.group(1))
        config.deviceScreenHeightVar = int(match.group(2))
    else:
        raise ValueError("Invalid device type format, cannot find screen dimensions")
    config.textPaddingVar = textPaddingVar.get()
    config.header_glyph_horizontal_left_padding_var = header_glyph_horizontal_left_padding_var.get()
    config.header_glyph_horizontal_right_padding_var = header_glyph_horizontal_right_padding_var.get()
    config.header_glyph_height_var = header_glyph_height_var.get()
    config.header_text_height_var = header_text_height_var.get()
    config.header_glyph_bubble_height_var = header_glyph_bubble_height_var.get()
    config.header_text_bubble_height_var = header_text_bubble_height_var.get()
    config.clockHorizontalLeftPaddingVar = clockHorizontalLeftPaddingVar.get()
    config.clockHorizontalRightPaddingVar = clockHorizontalRightPaddingVar.get()
    config.pageTitlePaddingVar = pageTitlePaddingVar.get()
    config.text_padding_entry = text_padding_entry.get()
    config.VBG_Horizontal_Padding_entry = VBG_Horizontal_Padding_entry.get()
    config.VBG_Vertical_Padding_entry = VBG_Vertical_Padding_entry.get()
    config.bubblePaddingVar = bubblePaddingVar.get()
    config.rectangle_padding_entry = rectangle_padding_entry.get()
    config.itemsPerScreenVar = itemsPerScreenVar.get()
    config.approxFooterHeightVar = approxFooterHeightVar.get()
    config.items_per_screen_entry = items_per_screen_entry.get()
    config.content_padding_top_entry = content_padding_top_entry.get()
    config.contentPaddingTopVar = contentPaddingTopVar.get()
    config.headerHeightVar = headerHeightVar.get()
    config.custom_font_size_entry = custom_font_size_entry.get()
    config.font_size_var = font_size_var.get()
    config.bgHexVar = bgHexVar.get()
    config.background_hex_entry = background_hex_entry.get()
    config.selectedFontHexVar = selectedFontHexVar.get()
    config.selected_font_hex_entry = selected_font_hex_entry.get()
    config.deselectedFontHexVar = deselectedFontHexVar.get()
    config.deselected_font_hex_entry = deselected_font_hex_entry.get()
    config.bubbleHexVar = bubbleHexVar.get()
    config.footerBubbleHexVar = footerBubbleHexVar.get()
    config.bubble_hex_entry = bubble_hex_entry.get()
    config.iconHexVar = iconHexVar.get()
    config.batteryChargingHexVar =batteryChargingHexVar.get()
    config.icon_hex_entry = icon_hex_entry.get()
    config.include_overlay_var = include_overlay_var.get()
    config.show_glyphs_var = show_glyphs_var.get()
    config.show_glyphs_bubbles_var = show_glyphs_bubbles_var.get()
    config.show_clock_bubbles_var = show_clock_bubbles_var.get()
    config.join_header_bubbles_var = join_header_bubbles_var.get()
    config.enable_game_switcher_var = enable_game_switcher_var.get()
    config.enable_grid_view_explore_var = enable_grid_view_explore_var.get()
    config.alternate_menu_names_var = alternate_menu_names_var.get()
    config.remove_right_menu_guides_var = remove_right_menu_guides_var.get()
    config.remove_left_menu_guides_var = remove_left_menu_guides_var.get()
    config.box_art_directory_path = box_art_directory_path.get()
    config.maxBoxArtWidth = maxBoxArtWidth.get()
    config.roms_directory_path = roms_directory_path.get()
    config.application_directory_path = application_directory_path.get()
    config.previewConsoleNameVar = previewConsoleNameVar.get()
    config.show_hidden_files_var = show_hidden_files_var.get()
    config.page_by_page_var = page_by_page_var.get()
    config.transparent_text_var = transparent_text_var.get()
    config.override_folder_box_art_padding_var = override_folder_box_art_padding_var.get()
    config.boxArtPaddingVar = boxArtPaddingVar.get()
    config.folderBoxArtPaddingVar = folderBoxArtPaddingVar.get()
    config.main_menu_style_var = main_menu_style_var.get()
    config.horizontal_menu_behaviour_var = horizontal_menu_behaviour_var.get()
    config.battery_charging_style_var = battery_charging_style_var.get()
    config.battery_style_var = battery_style_var.get()
    config.clock_format_var = clock_format_var.get()
    config.clock_alignment_var = clock_alignment_var.get()
    config.header_glyph_alignment_var = header_glyph_alignment_var.get()
    config.page_title_alignment_var = page_title_alignment_var.get()
    config.version_var = version_var.get()
    config.global_alignment_var = global_alignment_var.get()
    config.selected_overlay_var = selected_overlay_var.get()
    config.physical_controler_layout_var = physical_controler_layout_var.get()
    config.muos_button_swap_var = muos_button_swap_var.get()
    config.am_theme_directory_path = am_theme_directory_path.get()
    config.theme_directory_path = theme_directory_path.get()
    config.catalogue_directory_path = catalogue_directory_path.get()
    config.name_json_path = name_json_path.get()
    config.background_image_path = background_image_path.get()
    config.bootlogo_image_path = bootlogo_image_path.get()
    config.alt_font_path = alt_font_path.get()
    config.alt_text_path = alt_text_path.get()
    config.use_alt_font_var = use_alt_font_var.get()
    config.use_custom_background_var = use_custom_background_var.get()
    config.use_custom_bootlogo_var = use_custom_bootlogo_var.get()
    config.theme_name_entry = theme_name_entry.get()
    config.am_ignore_theme_var = am_ignore_theme_var.get()
    config.am_ignore_cd_var = am_ignore_cd_var.get()
    config.advanced_error_var = advanced_error_var.get()
    config.developer_preview_var = developer_preview_var.get()
    config.show_file_counter_var = show_file_counter_var.get()
    config.show_console_name_var = show_console_name_var.get()
    config.show_charging_battery_var = show_charging_battery_var.get()
    config.save_config()
    on_change()

def load_settings(config: Config):
    device_type_var.set(config.device_type_var)
    deviceScreenHeightVar.set(config.deviceScreenHeightVar)
    deviceScreenWidthVar.set(config.deviceScreenWidthVar)
    textPaddingVar.set(config.textPaddingVar)
    header_glyph_horizontal_left_padding_var.set(config.header_glyph_horizontal_left_padding_var)
    header_glyph_horizontal_right_padding_var.set(config.header_glyph_horizontal_right_padding_var)
    header_glyph_height_var.set(config.header_glyph_height_var)
    header_text_height_var.set(config.header_text_height_var)
    header_glyph_bubble_height_var.set(config.header_glyph_bubble_height_var)
    header_text_bubble_height_var.set(config.header_text_bubble_height_var)
    clockHorizontalLeftPaddingVar.set(config.clockHorizontalLeftPaddingVar)
    clockHorizontalRightPaddingVar.set(config.clockHorizontalRightPaddingVar)
    pageTitlePaddingVar.set(config.pageTitlePaddingVar)
    VBG_Horizontal_Padding_entry.delete(0, tk.END)
    VBG_Horizontal_Padding_entry.insert(0, config.VBG_Horizontal_Padding_entry)
    VBG_Vertical_Padding_entry.delete(0, tk.END)
    VBG_Vertical_Padding_entry.insert(0, config.VBG_Vertical_Padding_entry)
    text_padding_entry.delete(0, tk.END)
    text_padding_entry.insert(0, config.text_padding_entry)
    rectangle_padding_entry.delete(0, tk.END)
    rectangle_padding_entry.insert(0, config.rectangle_padding_entry)
    items_per_screen_entry.delete(0, tk.END)
    items_per_screen_entry.insert(0, config.items_per_screen_entry)
    background_hex_entry.delete(0, tk.END)
    background_hex_entry.insert(0, config.background_hex_entry)
    selected_font_hex_entry.delete(0, tk.END)
    selected_font_hex_entry.insert(0, config.selected_font_hex_entry)
    deselected_font_hex_entry.delete(0, tk.END)
    deselected_font_hex_entry.insert(0, config.deselected_font_hex_entry)
    bubble_hex_entry.delete(0, tk.END)
    bubble_hex_entry.insert(0, config.bubble_hex_entry)
    icon_hex_entry.delete(0, tk.END)
    icon_hex_entry.insert(0, config.icon_hex_entry)
    content_padding_top_entry.delete(0, tk.END)
    content_padding_top_entry.insert(0, config.content_padding_top_entry)
    bubblePaddingVar.set(config.bubblePaddingVar)
    itemsPerScreenVar.set(config.itemsPerScreenVar)
    approxFooterHeightVar.set(config.approxFooterHeightVar)
    contentPaddingTopVar.set(config.contentPaddingTopVar)
    headerHeightVar.set(config.headerHeightVar)
    boxArtPaddingVar.set(config.boxArtPaddingVar)
    folderBoxArtPaddingVar.set(config.folderBoxArtPaddingVar)
    font_size_var.set(config.font_size_var)
    custom_font_size_entry.delete(0, tk.END)
    custom_font_size_entry.insert(0, config.custom_font_size_entry)
    bgHexVar.set(config.bgHexVar)
    selectedFontHexVar.set(config.selectedFontHexVar)
    deselectedFontHexVar.set(config.deselectedFontHexVar)
    bubbleHexVar.set(config.bubbleHexVar)
    footerBubbleHexVar.set(config.footerBubbleHexVar)
    iconHexVar.set(config.iconHexVar)
    batteryChargingHexVar.set(config.batteryChargingHexVar)
    include_overlay_var.set(config.include_overlay_var)
    show_glyphs_var.set(config.show_glyphs_var)
    show_glyphs_bubbles_var.set(config.show_glyphs_bubbles_var)
    show_clock_bubbles_var.set(config.show_clock_bubbles_var)
    join_header_bubbles_var.set(config.join_header_bubbles_var)
    enable_game_switcher_var.set(config.enable_game_switcher_var)
    enable_grid_view_explore_var.set(config.enable_grid_view_explore_var)
    alternate_menu_names_var.set(config.alternate_menu_names_var)
    remove_right_menu_guides_var.set(config.remove_right_menu_guides_var)
    remove_left_menu_guides_var.set(config.remove_left_menu_guides_var)
    box_art_directory_path.set(config.box_art_directory_path)
    maxBoxArtWidth.set(config.maxBoxArtWidth)
    roms_directory_path.set(config.roms_directory_path)
    application_directory_path.set(config.application_directory_path)
    previewConsoleNameVar.set(config.previewConsoleNameVar)
    show_hidden_files_var.set(config.show_hidden_files_var)
    override_folder_box_art_padding_var.set(config.override_folder_box_art_padding_var)
    page_by_page_var.set(config.page_by_page_var)
    transparent_text_var.set(config.transparent_text_var)
    version_var.set(config.version_var)
    global_alignment_var.set(config.global_alignment_var)
    selected_overlay_var.set(config.selected_overlay_var)
    physical_controler_layout_var.set(config.physical_controler_layout_var)
    muos_button_swap_var.set(config.muos_button_swap_var)
    main_menu_style_var.set(config.main_menu_style_var)
    horizontal_menu_behaviour_var.set(config.horizontal_menu_behaviour_var)
    battery_charging_style_var.set(config.battery_charging_style_var)
    battery_style_var.set(config.battery_style_var)
    clock_format_var.set(config.clock_format_var)
    clock_alignment_var.set(config.clock_alignment_var)
    header_glyph_alignment_var.set(config.header_glyph_alignment_var)
    page_title_alignment_var.set(config.page_title_alignment_var)
    am_theme_directory_path.set(config.am_theme_directory_path)
    theme_directory_path.set(config.theme_directory_path)
    catalogue_directory_path.set(config.catalogue_directory_path)
    name_json_path.set(config.name_json_path)
    background_image_path.set(config.background_image_path)
    bootlogo_image_path.set(config.bootlogo_image_path)
    alt_font_path.set(config.alt_font_path)
    alt_text_path.set(config.alt_text_path)
    use_alt_font_var.set(config.use_alt_font_var)
    use_custom_background_var.set(config.use_custom_background_var)
    use_custom_bootlogo_var.set(config.use_custom_bootlogo_var)
    theme_name_entry.delete(0, tk.END)
    theme_name_entry.insert(0, config.theme_name_entry)
    am_ignore_theme_var.set(config.am_ignore_theme_var)
    am_ignore_cd_var.set(config.am_ignore_cd_var)
    advanced_error_var.set(config.advanced_error_var)
    developer_preview_var.set(config.developer_preview_var)
    show_file_counter_var.set(config.show_file_counter_var)
    show_console_name_var.set(config.show_console_name_var)
    show_charging_battery_var.set(config.show_charging_battery_var)



load_settings(global_config)
menuNameMap = getAlternateMenuNameDict()

# Attach trace callbacks to the variables
deviceScreenWidthVar.trace_add("write", lambda *args: save_settings(global_config))
deviceScreenHeightVar.trace_add("write", lambda *args: save_settings(global_config))
textPaddingVar.trace_add("write", lambda *args: save_settings(global_config))
VBG_Horizontal_Padding_var.trace_add("write",lambda *args: save_settings(global_config))
header_glyph_horizontal_left_padding_var.trace_add("write",lambda *args: save_settings(global_config))
header_glyph_horizontal_right_padding_var.trace_add("write",lambda *args: save_settings(global_config))
header_glyph_height_var.trace_add("write",lambda *args: save_settings(global_config))
header_text_height_var.trace_add("write",lambda *args: save_settings(global_config))
header_glyph_bubble_height_var.trace_add("write",lambda *args: save_settings(global_config))
header_text_bubble_height_var.trace_add("write",lambda *args: save_settings(global_config))
clockHorizontalLeftPaddingVar.trace_add("write",lambda *args: save_settings(global_config))
clockHorizontalRightPaddingVar.trace_add("write",lambda *args: save_settings(global_config))
pageTitlePaddingVar.trace_add("write",lambda *args: save_settings(global_config))
VBG_Vertical_Padding_var.trace_add("write",lambda *args: save_settings(global_config))
bubblePaddingVar.trace_add("write", lambda *args: save_settings(global_config))
itemsPerScreenVar.trace_add("write", lambda *args: save_settings(global_config))
approxFooterHeightVar.trace_add("write", lambda *args: save_settings(global_config))
contentPaddingTopVar.trace_add("write",lambda *args: save_settings(global_config))
headerHeightVar.trace_add("write",lambda *args: save_settings(global_config))
boxArtPaddingVar.trace_add("write", lambda *args: save_settings(global_config))
folderBoxArtPaddingVar.trace_add("write", lambda *args: save_settings(global_config))
font_size_var.trace_add("write", lambda *args: save_settings(global_config))
bgHexVar.trace_add("write", lambda *args: save_settings(global_config))
selectedFontHexVar.trace_add("write", lambda *args: save_settings(global_config))
deselectedFontHexVar.trace_add("write", lambda *args: save_settings(global_config))
bubbleHexVar.trace_add("write", lambda *args: save_settings(global_config))
footerBubbleHexVar.trace_add("write", lambda *args: save_settings(global_config))
iconHexVar.trace_add("write", lambda *args: save_settings(global_config))
batteryChargingHexVar.trace_add("write", lambda *args: save_settings(global_config))
show_file_counter_var.trace_add("write", lambda *args: save_settings(global_config))
show_console_name_var.trace_add("write", lambda *args: save_settings(global_config))
show_charging_battery_var.trace_add("write", lambda *args: save_settings(global_config))
include_overlay_var.trace_add("write", lambda *args: save_settings(global_config))
show_glyphs_var.trace_add("write", lambda *args: save_settings(global_config))
show_clock_bubbles_var.trace_add("write", lambda *args: save_settings(global_config))
show_glyphs_bubbles_var.trace_add("write", lambda *args: save_settings(global_config))
join_header_bubbles_var.trace_add("write", lambda *args: save_settings(global_config))
enable_game_switcher_var.trace_add("write", lambda *args: save_settings(global_config))
enable_grid_view_explore_var.trace_add("write", lambda *args: save_settings(global_config))
alternate_menu_names_var.trace_add("write", lambda *args: save_settings(global_config))
remove_right_menu_guides_var.trace_add("write", lambda *args: save_settings(global_config))
remove_left_menu_guides_var.trace_add("write", lambda *args: save_settings(global_config))
box_art_directory_path.trace_add("write", lambda *args: save_settings(global_config))
maxBoxArtWidth.trace_add("write", lambda *args: save_settings(global_config))
roms_directory_path.trace_add("write", lambda *args: save_settings(global_config))
application_directory_path.trace_add("write", lambda *args: save_settings(global_config))
previewConsoleNameVar.trace_add("write", lambda *args: save_settings(global_config))
show_hidden_files_var.trace_add("write", lambda *args: save_settings(global_config))
override_folder_box_art_padding_var.trace_add("write", lambda *args: save_settings(global_config))
page_by_page_var.trace_add("write", lambda *args: save_settings(global_config))
transparent_text_var.trace_add("write", lambda *args: save_settings(global_config))
version_var.trace_add("write", lambda *args: save_settings(global_config))
device_type_var.trace_add("write", lambda *args: save_settings(global_config))
global_alignment_var.trace_add("write", lambda *args: save_settings(global_config))
selected_overlay_var.trace_add("write",lambda *args: save_settings(global_config))
physical_controler_layout_var.trace_add("write",lambda *args: save_settings(global_config))
muos_button_swap_var.trace_add("write",lambda *args: save_settings(global_config))
main_menu_style_var.trace_add("write",lambda *args: save_settings(global_config))
horizontal_menu_behaviour_var.trace_add("write",lambda *args: save_settings(global_config))
battery_charging_style_var.trace_add("write",lambda *args: save_settings(global_config))
battery_style_var.trace_add("write",lambda *args: save_settings(global_config))
clock_format_var.trace_add("write",lambda *args: save_settings(global_config))
clock_alignment_var.trace_add("write",lambda *args: save_settings(global_config))
header_glyph_alignment_var.trace_add("write",lambda *args: save_settings(global_config))
page_title_alignment_var.trace_add("write",lambda *args: save_settings(global_config))
am_theme_directory_path.trace_add("write", lambda *args: save_settings(global_config))
theme_directory_path.trace_add("write", lambda *args: save_settings(global_config))
catalogue_directory_path.trace_add("write", lambda *args: save_settings(global_config))
name_json_path.trace_add("write", lambda *args: save_settings(global_config))
background_image_path.trace_add("write", lambda *args: save_settings(global_config))
bootlogo_image_path.trace_add("write", lambda *args: save_settings(global_config))
am_ignore_theme_var.trace_add("write", lambda *args: save_settings(global_config))
am_ignore_cd_var.trace_add("write", lambda *args: save_settings(global_config))
advanced_error_var.trace_add("write", lambda *args: save_settings(global_config))
developer_preview_var.trace_add("write", lambda *args: save_settings(global_config))
use_alt_font_var.trace_add("write", lambda *args: save_settings(global_config))
use_custom_background_var.trace_add("write",lambda *args: save_settings(global_config))
use_custom_bootlogo_var.trace_add("write", lambda *args: save_settings(global_config))
alt_font_path.trace_add("write", lambda *args: save_settings(global_config))
alt_text_path.trace_add("write",lambda *args: save_settings(global_config))

resize_event_id = None

# Function to call after resizing is finished
def on_resize_complete():
    on_change()

def on_resize(event):
    global resize_event_id

    # Cancel the previous event, if any
    if resize_event_id is not None:
        root.after_cancel(resize_event_id)
    
    # Set a new delayed call to the resize complete function
    resize_event_id = root.after(100, on_resize_complete)

root.bind("<Configure>", on_resize)       # Bind the window resize event
paned_window.bind("<Configure>", on_resize)  # Bind the paned window resize event



save_settings(global_config)

# Run the main loop
root.mainloop()