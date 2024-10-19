# -*- coding: utf-8 -*-
from PIL import ImageTk,Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageColor
try:
    from bidi import get_display as bidi_get_display
except:
    from bidi.algorithm import get_display as bidi_get_display
import os
import sys
import math
import tkinter as tk
from tkinter import font, PanedWindow, Scrollbar
from tkinter import filedialog, simpledialog, messagebox, ttk
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

## TODO look into center align and left align
## TODO make header resizable

deviceScreenWidth, deviceScreenHeight = 640, 480

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
        self.textPaddingVar = 40
        self.text_padding_entry = 40
        self.VBG_Vertical_Padding_entry = 15
        self.VBG_Horizontal_Padding_entry = 15
        self.bubblePaddingVar = 20
        self.rectangle_padding_entry = 20
        self.itemsPerScreenVar = 7
        self.items_per_screen_entry = 7
        self.footerHeightVar = 75
        self.footer_height_entry = 75
        self.contentPaddingTopVar = 44
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
        self.icon_hex_entry = "ffffff"
        self.include_overlay_var = False
        self.alternate_menu_names_var = False
        self.remove_right_menu_guides_var = False
        self.remove_left_menu_guides_var = False
        self.boxArtPaddingVar = 0
        self.folderBoxArtPaddingVar = 0
        self.box_art_directory_path = ""
        self.maxGamesBubbleLengthVar = deviceScreenWidth
        self.maxFoldersBubbleLengthVar = deviceScreenWidth
        self.roms_directory_path = ""
        self.application_directory_path = ""
        self.previewConsoleNameVar = "Nintendo Game Boy"
        self.show_hidden_files_var = False
        self.override_bubble_cut_var = False
        self.override_folder_box_art_padding_var = False
        self.page_by_page_var = False
        self.transparent_text_var = False
        self.version_var = "Select a version"
        self.global_alignment_var = "Left"
        self.selected_overlay_var = "muOS Default CRT Overlay"
        self.theme_alignment_var = "Global"
        self.main_menu_style_var = "Horizontal"
        self.content_alignment_var = "Global"
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
    
    def loop_through_themes(self, themes_file='PremadeThemes.json', action=None):
        themes = self.load_premade_themes(themes_file)
        if themes:
            for theme in themes:
                self.apply_theme(theme)
                if action:
                    action(self)  # Perform the action using the current config

config = Config()

background_image = None

# Define constants
render_factor = 5

contentPaddingTop = 44
footerHeight = 55
textMF = 0.7


def change_logo_color(input_path, hex_color):
    # Load the image
    img = Image.open(input_path).convert("RGBA")
    
    # Convert hex_color to RGBA
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Create a new image with the same size and the specified color
    color_image = Image.new("RGBA", img.size, (r, g, b, 255))
    
    # Get the alpha channel from the original image
    alpha = img.split()[3]
    
    # Composite the color image with the alpha channel
    result_image = Image.composite(color_image, Image.new("RGBA", img.size, (0, 0, 0, 0)), alpha)
    
    return result_image

def generateMenuHelperGuides(rhsButtons,selected_font_path,colour_hex,render_factor,lhsButtons=[["POWER","SLEEP"]]):
    image = Image.new("RGBA", (deviceScreenWidth*render_factor, deviceScreenHeight*render_factor), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    if not( config.remove_left_menu_guides_var and config.remove_right_menu_guides_var):
        required_padding_between_sides=15
        lhsTotalWidth = deviceScreenWidth
        rhsTotalWidth = deviceScreenWidth
        iterations = 0
        from_sides_padding = int(config.VBG_Horizontal_Padding_entry)
        while from_sides_padding+lhsTotalWidth+required_padding_between_sides+rhsTotalWidth+from_sides_padding>deviceScreenWidth:
            if iterations==0:
                from_sides_padding = int(config.VBG_Horizontal_Padding_entry)
            elif from_sides_padding>5:
                from_sides_padding=5
            from_bottom_padding = int(config.VBG_Vertical_Padding_entry)+iterations

            menu_helper_guide_height = footerHeight-(from_bottom_padding*2) # Change this if overlayed

            in_smaller_bubble_font_size = menu_helper_guide_height*(16/45)*render_factor
            inSmallerBubbleFont = ImageFont.truetype(selected_font_path, in_smaller_bubble_font_size)

            in_bubble_font_size = menu_helper_guide_height*(19/45)*render_factor
            inBubbleFont = ImageFont.truetype(selected_font_path, in_bubble_font_size)

            single_letter_font_size = menu_helper_guide_height*(23/45)*render_factor
            singleLetterFont = ImageFont.truetype(selected_font_path, single_letter_font_size)

            horizontal_small_padding = menu_helper_guide_height*(5/45)
            horizontal_padding = menu_helper_guide_height*(6.5/45)
            horizontal_large_padding = menu_helper_guide_height*(8.5/45)
            
            bottom_guide_middle_y = deviceScreenHeight-from_bottom_padding-(menu_helper_guide_height/2)

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

            if not config.remove_left_menu_guides_var:
                lhsTotalWidth += getTotalBubbleWidth(lhsButtons,inSmallerBubbleFont,inBubbleFont,horizontal_padding,horizontal_large_padding,horizontal_small_padding,guide_small_bubble_height,render_factor)
                combined_width += lhsTotalWidth

            if not config.remove_right_menu_guides_var:
                rhsTotalWidth += getTotalBubbleWidth(rhsButtons,inSmallerBubbleFont,inBubbleFont,horizontal_padding,horizontal_large_padding,horizontal_small_padding,guide_small_bubble_height,render_factor)
                combined_width += rhsTotalWidth
            iterations +=1

        if not config.remove_left_menu_guides_var:
            realLhsPointer = from_sides_padding*render_factor
            ## Make the main long bubble
            draw.rounded_rectangle([(realLhsPointer,(bottom_guide_middle_y-menu_helper_guide_height/2)*render_factor), #bottom left point
                                    (realLhsPointer+(lhsTotalWidth*render_factor),(bottom_guide_middle_y+menu_helper_guide_height/2)*render_factor)], # Top right point
                                    radius=(menu_helper_guide_height/2)*render_factor,
                                    fill = hex_to_rgb(colour_hex,alpha=0.133)
                                    )
            realLhsPointer+=horizontal_padding*render_factor
            for pair in lhsButtons:
                if len(pair[0]) == 1:
                    circleCenterX = realLhsPointer+((guide_small_bubble_height*render_factor)/2)
                    draw.ellipse((circleCenterX-((guide_small_bubble_height*render_factor)/2), (bottom_guide_middle_y-(guide_small_bubble_height/2))*render_factor,circleCenterX+((guide_small_bubble_height*render_factor)/2), (bottom_guide_middle_y+(guide_small_bubble_height/2))*render_factor),fill=f"#{colour_hex}")
                    smallerTextBbox = singleLetterFont.getbbox(pair[0])
                    smallerTextWidth = smallerTextBbox[2]-smallerTextBbox[0]
                    smallerTextX = circleCenterX-(smallerTextWidth/2)
                    draw.text(( smallerTextX,single_letter_text_y), pair[0], font=singleLetterFont, fill=(*ImageColor.getrgb(f"#{colour_hex}"), int(255*0.593)))
                    realLhsPointer+=(guide_small_bubble_height+horizontal_small_padding)*render_factor

                else:
                    ## Make the smaller bubble
                    smallerTextBbox = inSmallerBubbleFont.getbbox(pair[0])
                    smallerTextWidth = smallerTextBbox[2]-smallerTextBbox[0]
                    smallerBubbleWidth = horizontal_large_padding+smallerTextWidth/render_factor+horizontal_large_padding
                    draw.rounded_rectangle([(realLhsPointer,(bottom_guide_middle_y-guide_small_bubble_height/2)*render_factor), #bottom left point
                                    (realLhsPointer+(smallerBubbleWidth*render_factor),(bottom_guide_middle_y+guide_small_bubble_height/2)*render_factor)], # Top right point
                                    radius=(guide_small_bubble_height/2)*render_factor,
                                    fill = hex_to_rgb(colour_hex,alpha=1)
                                    )
                    smallerTextX = realLhsPointer + horizontal_large_padding*render_factor
                    draw.text((smallerTextX,in_smaller_bubble_text_y),pair[0],font=inSmallerBubbleFont,fill=(*ImageColor.getrgb(f"#{colour_hex}"), int(255*0.593)))
                    realLhsPointer+=(smallerBubbleWidth+horizontal_small_padding)*render_factor
                textBbox = inBubbleFont.getbbox(pair[1])
                textWidth = textBbox[2]-textBbox[0]
                draw.text((realLhsPointer,in_bubble_text_y),pair[1],font=inBubbleFont,fill=f"#{colour_hex}")
                realLhsPointer+=textWidth
                realLhsPointer += horizontal_large_padding*render_factor
        if not config.remove_right_menu_guides_var:
            realRhsPointer = (deviceScreenWidth-from_sides_padding-rhsTotalWidth)*render_factor
            ## Make the main long bubble
            draw.rounded_rectangle([(realRhsPointer,(bottom_guide_middle_y-menu_helper_guide_height/2)*render_factor), #bottom left point
                                    (realRhsPointer+(rhsTotalWidth*render_factor),(bottom_guide_middle_y+menu_helper_guide_height/2)*render_factor)], # Top right point
                                    radius=(menu_helper_guide_height/2)*render_factor,
                                    fill = hex_to_rgb(colour_hex,alpha=0.133)
                                    )
            realRhsPointer+=horizontal_padding*render_factor
            for pair in rhsButtons:
                if len(pair[0]) == 1:
                    circleCenterX = realRhsPointer+((guide_small_bubble_height*render_factor)/2)
                    draw.ellipse((circleCenterX-((guide_small_bubble_height*render_factor)/2), (bottom_guide_middle_y-(guide_small_bubble_height/2))*render_factor,circleCenterX+((guide_small_bubble_height*render_factor)/2), (bottom_guide_middle_y+(guide_small_bubble_height/2))*render_factor),fill=f"#{colour_hex}")
                    smallerTextBbox = singleLetterFont.getbbox(pair[0])
                    smallerTextWidth = smallerTextBbox[2]-smallerTextBbox[0]
                    smallerTextX = circleCenterX-(smallerTextWidth/2)
                    draw.text(( smallerTextX,single_letter_text_y), pair[0], font=singleLetterFont, fill=(*ImageColor.getrgb(f"#{colour_hex}"), int(255*0.593)))
                    realRhsPointer+=(guide_small_bubble_height+horizontal_small_padding)*render_factor

                else:
                    ## Make the smaller bubble
                    smallerTextBbox = inSmallerBubbleFont.getbbox(pair[0])
                    smallerTextWidth = smallerTextBbox[2]-smallerTextBbox[0]
                    smallerBubbleWidth = horizontal_large_padding+smallerTextWidth/render_factor+horizontal_large_padding
                    draw.rounded_rectangle([(realRhsPointer,(bottom_guide_middle_y-guide_small_bubble_height/2)*render_factor), #bottom left point
                                    (realRhsPointer+(smallerBubbleWidth*render_factor),(bottom_guide_middle_y+guide_small_bubble_height/2)*render_factor)], # Top right point
                                    radius=(guide_small_bubble_height/2)*render_factor,
                                    fill = hex_to_rgb(colour_hex,alpha=1)
                                    )
                    smallerTextX = realRhsPointer + horizontal_large_padding*render_factor
                    draw.text((smallerTextX,in_smaller_bubble_text_y),pair[0],font=inSmallerBubbleFont,fill=(*ImageColor.getrgb(f"#{colour_hex}"), int(255*0.593)))
                    realRhsPointer+=(smallerBubbleWidth+horizontal_small_padding)*render_factor
                textBbox = inBubbleFont.getbbox(pair[1])
                textWidth = textBbox[2]-textBbox[0]
                draw.text((realRhsPointer,in_bubble_text_y),pair[1],font=inBubbleFont,fill=f"#{colour_hex}")
                realRhsPointer+=textWidth
                realRhsPointer += horizontal_large_padding*render_factor
    return(image)

def getTotalBubbleWidth(buttons,internalBubbleFont,bubbleFont,initalPadding,largerPadding,smallerPadding,circleWidth,render_factor):
    totalWidth = initalPadding
    for pair in buttons:
        #pair[0] might be MENU, POWER, or ABXY
        if len(pair[0]) == 1:
            totalWidth+=circleWidth
        else:
            totalWidth+=largerPadding
            smallerTextBbox = internalBubbleFont.getbbox(pair[0])
            smallerTextWidth = smallerTextBbox[2]-smallerTextBbox[0]
            totalWidth+=(smallerTextWidth/render_factor)
            totalWidth+=largerPadding
        totalWidth+=smallerPadding
        #pair[1] might be something like INFO, FAVOURITE, REFRESH etc...
        textBbox = bubbleFont.getbbox(pair[1])
        textWidth = textBbox[2]-textBbox[0]
        totalWidth += (textWidth/render_factor)
        totalWidth+=largerPadding
    return(totalWidth)


def generatePilImageVertical(progress_bar,workingIndex, muOSSystemName,listItems,textPadding, rectanglePadding, ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor,numScreens=0,screenIndex=0,fileCounter="",folderName = None,transparent=False):
    progress_bar['value'] +=1
    #print(f"progress_bar Max = {progress_bar['maximum']} | progress_bar Value = {progress_bar['value']} | {100*(int(progress_bar['value'])/int(progress_bar['maximum']))}%")
    bg_rgb = hex_to_rgb(bg_hex)
    if not transparent:
        image = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), bg_rgb)

        if background_image != None:
            image.paste(background_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))
    else:
        image = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), (0,0,0,0))

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
        menuHelperGuides = generateMenuHelperGuides([["A", "SELECT"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]])
    elif muOSSystemName == "muxconfig" or muOSSystemName == "muxinfo":
        menuHelperGuides = generateMenuHelperGuides([["B", "BACK"],["A", "SELECT"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]])
    elif muOSSystemName == "muxapp":
        menuHelperGuides = generateMenuHelperGuides([["B", "BACK"],["A", "LAUNCH"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]])
    elif muOSSystemName == "muxplore":
        menuHelperGuides = generateMenuHelperGuides([["MENU", "INFO"],["Y", "FAVOURITE"],["X", "REFRESH"],["B", "BACK"],["A", "OPEN"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]])
    elif muOSSystemName == "muxfavourite":
        menuHelperGuides = generateMenuHelperGuides([["MENU", "INFO"],["X", "REMOVE"],["B", "BACK"],["A", "OPEN"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]])
    elif muOSSystemName == "muxhistory":
        menuHelperGuides = generateMenuHelperGuides([["MENU", "INFO"],["Y", "FAVOURITE"],["X", "REMOVE"],["B", "BACK"],["A", "OPEN"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]])

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
    if muOSSystemName.startswith("mux"):
        if config.theme_alignment_var == "Global":
            textAlignment = config.global_alignment_var
        else:
            textAlignment = config.theme_alignment_var
    else:
        if config.content_alignment_var == "Global":
            textAlignment = config.global_alignment_var
        else:
            textAlignment = config.content_alignment_var

    try:
        font_size = int(config.custom_font_size_entry) * render_factor
    except:
        font_size = (((deviceScreenHeight - footerHeight - contentPaddingTop) * render_factor) / ItemsPerScreen) * textMF
    
    font = ImageFont.truetype(selected_font_path, font_size)

    availableHeight = ((deviceScreenHeight - contentPaddingTop - footerHeight) * render_factor) / ItemsPerScreen

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
        if config.override_bubble_cut_var:
            if muOSSystemName == "Folder":
                maxBubbleLength = int(config.maxFoldersBubbleLengthVar)
            else:
                maxBubbleLength = int(config.maxGamesBubbleLengthVar)
        else:
            maxBubbleLength = deviceScreenWidth
        if maxBubbleLength*render_factor < textPadding*render_factor+smallestValidTest_width+rectanglePadding*render_factor+5*render_factor: #Make sure there won't be a bubble error
            maxBubbleLength = deviceScreenWidth

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
            text_x = (deviceScreenWidth-textPadding) * render_factor-text_width
        elif textAlignment == "Centre":
            text_x = ((deviceScreenWidth* render_factor-text_width)/2) 
        #text_y = contentPaddingTop * render_factor + availableHeight * index

        
        rectangle_x0 = text_x - (rectanglePadding * render_factor)
        rectangle_y0 = contentPaddingTop * render_factor + availableHeight * index
        rectangle_x1 = rectangle_x0 + rectanglePadding * render_factor + text_width + rectanglePadding * render_factor
        rectangle_y1 = contentPaddingTop * render_factor + availableHeight * (index+1)
        middle_y = (rectangle_y0 + rectangle_y1) / 2
        ascent, descent = font.getmetrics()
        text_height = ascent + descent

        # Calculate the text's y-position by centering it vertically within the rectangle
        text_y = middle_y - (text_height / 2)

        corner_radius = availableHeight // 2

        if workingIndex == index:
            draw.rounded_rectangle(
                [(rectangle_x0, rectangle_y0), (rectangle_x1, rectangle_y1)],
                radius=corner_radius,
                fill=f"#{bubble_hex}"
            )   
        draw.text((text_x, text_y), text, font=font, fill=text_color)
            
    
    if (muOSSystemName == "muxdevice" or muOSSystemName == "muxlaunch" or muOSSystemName == "muxconfig" or muOSSystemName == "muxinfo" or muOSSystemName == "muxapp" or muOSSystemName == "muxplore" or muOSSystemName == "muxfavourite" or muOSSystemName == "muxhistory"):
        image = Image.alpha_composite(image, menuHelperGuides)
           
    return(image)


def ContinuousFolderImageGen(progress_bar,muOSSystemName, listItems, textPadding, rectanglePadding, ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, outputDir, folderName = None, threadNumber = 0):
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
                                             fileCounter=fileCounter,
                                             folderName = folderName,transparent=True)
            image = image.resize((deviceScreenWidth, deviceScreenHeight), Image.LANCZOS)
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
            elif workingItem[1] == "Menu":
                # directory = os.path.dirname(f"{outputDir}/{muOSSystemName}/{workingItem[2]}.png")
                # if not os.path.exists(directory):
                #     os.makedirs(directory)
                # image.save(f"{outputDir}/{muOSSystemName}/{workingItem[2]}.png")
                if workingIndex == 0:
                    bg_rgb = hex_to_rgb(bg_hex)
                    background = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), bg_rgb)
                    if background_image != None:
                        background.paste(background_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))
                    background = background.resize(image.size, Image.LANCZOS)
                    background.paste(image, (0, 0), image)
                    if config.developer_preview_var:
                        background.save(os.path.join(internal_files_dir,f"TempPreview{threadNumber}.png"))
                    background = background.resize((int(0.45*deviceScreenWidth), int(0.45*deviceScreenHeight)), Image.LANCZOS)
                    background.save(os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}","preview.png"))
                

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

def generatePilImageHorizontal(progress_bar,workingIndex, bg_hex, selected_font_hex,deselected_font_hex, bubble_hex,icon_hex,render_factor,transparent=False):
    progress_bar['value']+=1
    #print(f"progress_bar Max = {progress_bar['maximum']} | progress_bar Value = {progress_bar['value']} | {100*(int(progress_bar['value'])/int(progress_bar['maximum']))}%")
    bg_rgb = hex_to_rgb(bg_hex)

    # Create image

    if not transparent:
        image = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), bg_rgb)

        if background_image != None:
            image.paste(background_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))
    else:
        image = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), (0,0,0,0))


    

    exploreLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "explore.png"),icon_hex)
    favouriteLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "favourite.png"),icon_hex)
    historyLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "history.png"),icon_hex)
    appsLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "apps.png"),icon_hex)
   
    top_logo_size = (int((exploreLogoColoured.size[0]*render_factor*min(deviceScreenHeight/480,deviceScreenWidth/640))/5),
                     int((exploreLogoColoured.size[1]*render_factor*min(deviceScreenHeight/480,deviceScreenWidth/640))/5))
    
    exploreLogoColoured = exploreLogoColoured.resize((top_logo_size), Image.LANCZOS)
    favouriteLogoColoured = favouriteLogoColoured.resize((top_logo_size), Image.LANCZOS)
    historyLogoColoured = historyLogoColoured.resize((top_logo_size), Image.LANCZOS)
    appsLogoColoured = appsLogoColoured.resize((top_logo_size), Image.LANCZOS)
    
    combined_top_logos_width = exploreLogoColoured.size[0]+favouriteLogoColoured.size[0]+historyLogoColoured.size[0]+appsLogoColoured.size[0]

    icons_to_bubble_padding = min((deviceScreenHeight*0)/480,(deviceScreenWidth*0)/640)*render_factor ## CHANGE for adjustment

    bubble_height = min((deviceScreenHeight*36.3)/480,(deviceScreenWidth*36.3)/640)*render_factor ## CHANGE for adjustment

    screen_y_middle = (deviceScreenHeight*render_factor)/2

    combined_top_row_height = max(exploreLogoColoured.size[1],favouriteLogoColoured.size[1],historyLogoColoured.size[1],appsLogoColoured.size[1])+icons_to_bubble_padding+bubble_height

    top_row_icon_y = int(screen_y_middle-(combined_top_row_height/2))

    top_row_bubble_middle = int(screen_y_middle+(combined_top_row_height/2)-(bubble_height)/2)

    padding_between_top_logos = (deviceScreenWidth*render_factor-combined_top_logos_width)/(4+1) # 4 logos plus 1

    explore_middle = int(padding_between_top_logos+(exploreLogoColoured.size[0])/2)
    favourite_middle = int(padding_between_top_logos+favouriteLogoColoured.size[0]+padding_between_top_logos+(favouriteLogoColoured.size[0])/2)
    history_middle = int(padding_between_top_logos+historyLogoColoured.size[0]+padding_between_top_logos+favouriteLogoColoured.size[0]+padding_between_top_logos+(historyLogoColoured.size[0])/2)
    apps_middle = int(padding_between_top_logos+appsLogoColoured.size[0]+padding_between_top_logos+favouriteLogoColoured.size[0]+padding_between_top_logos+historyLogoColoured.size[0]+padding_between_top_logos+(appsLogoColoured.size[0])/2)

    explore_logo_x = int(explore_middle-(exploreLogoColoured.size[0])/2)
    favourite_logo_x = int(favourite_middle-(favouriteLogoColoured.size[0])/2)
    history_logo_x = int(history_middle-(historyLogoColoured.size[0])/2)
    apps_logo_x = int(apps_middle-(appsLogoColoured.size[0])/2)

    image.paste(exploreLogoColoured,(explore_logo_x,top_row_icon_y),exploreLogoColoured)
    image.paste(favouriteLogoColoured,(favourite_logo_x,top_row_icon_y),favouriteLogoColoured)
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
    menuHelperGuides = generateMenuHelperGuides([["A", "SELECT"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]])
    
    

    font_size = min((deviceScreenHeight*24)/480,(deviceScreenWidth*24)/640) * render_factor  ## CHANGE for adjustment
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
        current_x_midpoint = 104+(144*workingIndex)

    

    horizontalBubblePadding = min((deviceScreenHeight*40)/480,(deviceScreenWidth*40)/640)*render_factor  ## CHANGE for adjustment
    
    if config.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("content explorer", "Content"))
    else:
        textString = "Content"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    ascent, descent = font.getmetrics()
    text_height = ascent + descent

    text_y = top_row_bubble_middle - (text_height / 2)


    bubble_center_x =  explore_middle
    textColour = selected_font_hex if workingIndex == 0 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
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
        textString = bidi_get_display(menuNameMap.get("favourites", "Favourites"))
    else:
        textString = "Favourites"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    bubble_center_x =  favourite_middle
    textColour = selected_font_hex if workingIndex == 1 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
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
    bubble_center_x =  history_middle
    textColour = selected_font_hex if workingIndex == 2 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
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
    bubble_center_x =  apps_middle
    textColour = selected_font_hex if workingIndex == 3 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
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
    
    bottom_logo_size = (int((infoLogoColoured.size[0]*render_factor*min(deviceScreenHeight/480,deviceScreenWidth/640))/5),
                     int((infoLogoColoured.size[1]*render_factor*min(deviceScreenHeight/480,deviceScreenWidth/640))/5))
    
    infoLogoColoured = infoLogoColoured.resize(bottom_logo_size, Image.LANCZOS)
    configLogoColoured = configLogoColoured.resize(bottom_logo_size, Image.LANCZOS)
    rebootLogoColoured = rebootLogoColoured.resize(bottom_logo_size, Image.LANCZOS)
    shutdownLogoColoured = shutdownLogoColoured.resize(bottom_logo_size, Image.LANCZOS)


    combined_bottom_logos_width = infoLogoColoured.size[0]+configLogoColoured.size[0]+rebootLogoColoured.size[0]+shutdownLogoColoured.size[0]

    circle_padding = min((deviceScreenHeight*15)/480,(deviceScreenWidth*15)/640)*render_factor ## CHANGE to adjust 

    combined_bottom_row_height = max(infoLogoColoured.size[1],configLogoColoured.size[1],rebootLogoColoured.size[1],shutdownLogoColoured.size[1])+circle_padding*2

    circle_radius = combined_bottom_row_height/2

    top_row_to_bottom_row_padding = min((deviceScreenHeight*20)/480,(deviceScreenWidth*20)/640)*render_factor ## CHANGE to adjust

    bottom_row_middle_y =  int(screen_y_middle+(combined_top_row_height/2)+top_row_to_bottom_row_padding+circle_radius)


    padding_from_screen_bottom_logos = deviceScreenWidth*(175/640)*render_factor ##CHANGE to adjust

    padding_between_bottom_logos = (deviceScreenWidth*render_factor-padding_from_screen_bottom_logos-combined_bottom_logos_width-padding_from_screen_bottom_logos)/(4-1) # 4 logos minus 1

    info_middle = int(padding_from_screen_bottom_logos+(infoLogoColoured.size[0])/2)
    config_middle = int(info_middle+(infoLogoColoured.size[0])/2+padding_between_bottom_logos+(configLogoColoured.size[0])/2)
    reboot_middle = int(config_middle+(configLogoColoured.size[0])/2+padding_between_bottom_logos+(rebootLogoColoured.size[0])/2)
    shutdown_middle = int(reboot_middle+(rebootLogoColoured.size[0])/2+padding_between_bottom_logos+(shutdownLogoColoured.size[0])/2)

    info_logo_x = int(info_middle-(infoLogoColoured.size[0])/2)
    config_logo_x = int(config_middle-(configLogoColoured.size[0])/2)
    reboot_logo_x = int(reboot_middle-(rebootLogoColoured.size[0])/2)
    shutdown_logo_x = int(shutdown_middle-(shutdownLogoColoured.size[0])/2)

    
    

    if workingIndex == 4:
        center_x = info_middle
        if config.transparent_text_var:
            draw_transparent.ellipse((int(center_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(center_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
        else:
            draw.ellipse((int(center_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(center_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
    elif workingIndex == 5:
        center_x = config_middle
        if config.transparent_text_var:
            draw_transparent.ellipse((int(center_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(center_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
        else:
            draw.ellipse((int(center_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(center_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
    elif workingIndex == 6:
        center_x = reboot_middle
        if config.transparent_text_var:
            draw_transparent.ellipse((int(center_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(center_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
        else:
            draw.ellipse((int(center_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(center_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
    elif workingIndex == 7:
        center_x = shutdown_middle
        if config.transparent_text_var:
            draw_transparent.ellipse((int(center_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(center_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
        else:
            draw.ellipse((int(center_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(center_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")

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
    
    return(image)

def generatePilImageAltHorizontal(progress_bar,workingIndex, bg_hex, selected_font_hex,deselected_font_hex, bubble_hex,icon_hex,render_factor,transparent=False):
    progress_bar['value']+=1
    #print(f"progress_bar Max = {progress_bar['maximum']} | progress_bar Value = {progress_bar['value']} | {100*(int(progress_bar['value'])/int(progress_bar['maximum']))}%")
    bg_rgb = hex_to_rgb(bg_hex)

    # Create image

    if not transparent:
        image = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), bg_rgb)

        if background_image != None:
            image.paste(background_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))
    else:
        image = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), (0,0,0,0))


    top_to_bottom_row_padding = min((deviceScreenHeight*30)/480,(deviceScreenWidth*30)/640) * render_factor  ## CHANGE for adjustment
    

    exploreLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "explore.png"),icon_hex)
    favouriteLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "favourite.png"),icon_hex)
    historyLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "history.png"),icon_hex)
    appsLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "apps.png"),icon_hex)
   
    top_logo_size = (int((exploreLogoColoured.size[0]*render_factor*min(deviceScreenHeight/480,deviceScreenWidth/640))/5),
                     int((exploreLogoColoured.size[1]*render_factor*min(deviceScreenHeight/480,deviceScreenWidth/640))/5))
    
    exploreLogoColoured = exploreLogoColoured.resize((top_logo_size), Image.LANCZOS)
    favouriteLogoColoured = favouriteLogoColoured.resize((top_logo_size), Image.LANCZOS)
    historyLogoColoured = historyLogoColoured.resize((top_logo_size), Image.LANCZOS)
    appsLogoColoured = appsLogoColoured.resize((top_logo_size), Image.LANCZOS)
    
    combined_top_logos_width = exploreLogoColoured.size[0]+favouriteLogoColoured.size[0]+historyLogoColoured.size[0]+appsLogoColoured.size[0]

    icons_to_bubble_padding = min((deviceScreenHeight*0)/480,(deviceScreenWidth*0)/640)*render_factor ## CHANGE for adjustment

    bubble_height = min((deviceScreenHeight*36.3)/480,(deviceScreenWidth*36.3)/640)*render_factor ## CHANGE for adjustment

    screen_y_middle = (deviceScreenHeight*render_factor)/2

    combined_top_row_height = max(exploreLogoColoured.size[1],favouriteLogoColoured.size[1],historyLogoColoured.size[1],appsLogoColoured.size[1])+icons_to_bubble_padding+bubble_height

    top_row_icon_y = int(screen_y_middle-combined_top_row_height-(top_to_bottom_row_padding/2))

    top_row_bubble_middle = int(screen_y_middle-(bubble_height)/2-(top_to_bottom_row_padding/2))

    padding_between_top_logos = (deviceScreenWidth*render_factor-combined_top_logos_width)/(4+1) # 4 logos plus 1

    explore_middle_x = int(padding_between_top_logos+(exploreLogoColoured.size[0])/2)
    favourite_middle_x = int(padding_between_top_logos+favouriteLogoColoured.size[0]+padding_between_top_logos+(favouriteLogoColoured.size[0])/2)
    history_middle_x = int(padding_between_top_logos+historyLogoColoured.size[0]+padding_between_top_logos+favouriteLogoColoured.size[0]+padding_between_top_logos+(historyLogoColoured.size[0])/2)
    apps_middle_x = int(padding_between_top_logos+appsLogoColoured.size[0]+padding_between_top_logos+favouriteLogoColoured.size[0]+padding_between_top_logos+historyLogoColoured.size[0]+padding_between_top_logos+(appsLogoColoured.size[0])/2)

    explore_logo_x = int(explore_middle_x-(exploreLogoColoured.size[0])/2)
    favourite_logo_x = int(favourite_middle_x-(favouriteLogoColoured.size[0])/2)
    history_logo_x = int(history_middle_x-(historyLogoColoured.size[0])/2)
    apps_logo_x = int(apps_middle_x-(appsLogoColoured.size[0])/2)

    image.paste(exploreLogoColoured,(explore_logo_x,top_row_icon_y),exploreLogoColoured)
    image.paste(favouriteLogoColoured,(favourite_logo_x,top_row_icon_y),favouriteLogoColoured)
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
    menuHelperGuides = generateMenuHelperGuides([["A", "SELECT"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]])
    

    font_size = min((deviceScreenHeight*24)/480,(deviceScreenWidth*24)/640) * render_factor  ## CHANGE for adjustment
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
        current_x_midpoint = 104+(144*workingIndex)

    

    horizontalBubblePadding = min((deviceScreenHeight*40)/480,(deviceScreenWidth*40)/640)*render_factor  ## CHANGE for adjustment
    
    if config.alternate_menu_names_var:
        textString = bidi_get_display(menuNameMap.get("content explorer", "Content"))
    else:
        textString = "Content"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    ascent, descent = font.getmetrics()
    text_height = ascent + descent

    text_y = top_row_bubble_middle - (text_height / 2)


    bubble_center_x =  explore_middle_x
    textColour = selected_font_hex if workingIndex == 0 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
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
        textString = bidi_get_display(menuNameMap.get("favourites", "Favourites"))
    else:
        textString = "Favourites"
    text_bbox = font.getbbox(textString)
    text_width = (text_bbox[2] - text_bbox[0])
    bubble_center_x =  favourite_middle_x
    textColour = selected_font_hex if workingIndex == 1 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
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
    bubble_center_x =  history_middle_x
    textColour = selected_font_hex if workingIndex == 2 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
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
    bubble_center_x =  apps_middle_x
    textColour = selected_font_hex if workingIndex == 3 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
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
   
    bottom_logo_size = (int((infoLogoColoured.size[0]*render_factor*min(deviceScreenHeight/480,deviceScreenWidth/640))/5),
                     int((infoLogoColoured.size[1]*render_factor*min(deviceScreenHeight/480,deviceScreenWidth/640))/5))
    
    infoLogoColoured = infoLogoColoured.resize((bottom_logo_size), Image.LANCZOS)
    configLogoColoured = configLogoColoured.resize((bottom_logo_size), Image.LANCZOS)
    rebootLogoColoured = rebootLogoColoured.resize((bottom_logo_size), Image.LANCZOS)
    shutdownLogoColoured = shutdownLogoColoured.resize((bottom_logo_size), Image.LANCZOS)
    
    combined_bottom_logos_width = infoLogoColoured.size[0]+configLogoColoured.size[0]+rebootLogoColoured.size[0]+shutdownLogoColoured.size[0]

    combined_bottom_row_height = max(infoLogoColoured.size[1],configLogoColoured.size[1],rebootLogoColoured.size[1],shutdownLogoColoured.size[1])+icons_to_bubble_padding+bubble_height

    bottom_row_icon_y = int(screen_y_middle+(top_to_bottom_row_padding/2))

    bottom_row_bubble_middle = int(screen_y_middle+(combined_bottom_row_height)-(bubble_height)/2+(top_to_bottom_row_padding/2))

    padding_between_bottom_logos = (deviceScreenWidth*render_factor-combined_bottom_logos_width)/(4+1) # 4 logos plus 1

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


    bubble_center_x =  info_middle_x
    textColour = selected_font_hex if workingIndex == 4 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
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
    bubble_center_x =  config_middle_x
    textColour = selected_font_hex if workingIndex == 5 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
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
    bubble_center_x =  reboot_middle_x
    textColour = selected_font_hex if workingIndex == 6 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
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
    bubble_center_x =  shutdown_middle_x
    textColour = selected_font_hex if workingIndex == 7 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
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
    
    return(image)


def generatePilImageBootLogo(bg_hex,deselected_font_hex,bubble_hex,render_factor):
    bg_rgb = hex_to_rgb(bg_hex)
    image = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), bg_rgb)
    if config.use_custom_bootlogo_var:
        if os.path.exists(config.bootlogo_image_path):
            bootlogo_image = Image.open(config.bootlogo_image_path)
            image.paste(bootlogo_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))
            return image
    elif background_image != None:
        image.paste(background_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))

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

    screen_x_middle, screen_y_middle = (deviceScreenWidth/2)*render_factor,(deviceScreenHeight/2)*render_factor

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

def generatePilImageBootScreen(bg_hex,deselected_font_hex,icon_hex,display_text,render_factor,icon_path=None):
    bg_rgb = hex_to_rgb(bg_hex)
    image = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), bg_rgb)
    if background_image != None:
        image.paste(background_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))
    
    draw = ImageDraw.Draw(image)

    if not config.use_alt_font_var:
        selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    else:
        if os.path.exists(config.alt_font_path):
            selected_font_path = config.alt_font_path
        else:
            selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    
    screen_x_middle, screen_y_middle = int((deviceScreenWidth/2)*render_factor),int((deviceScreenHeight/2)*render_factor)

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

def generatePilImageDefaultScreen(bg_hex,render_factor):
    bg_rgb = hex_to_rgb(bg_hex)
    image = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), bg_rgb)
    if background_image != None:
        image.paste(background_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))
    return (image)

def HorizontalMenuGen(progress_bar,muOSSystemName, listItems, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex,icon_hex, render_factor, outputDir,variant, threadNumber = 0):
    startIndex = 0
    endIndex = 8
    for workingIndex in range(startIndex, endIndex):
        workingItem = listItems[workingIndex]
        #image.save(os.path.join(script_dir,"Images for testing horizontal",f"{workingIndex}.png"))
        if variant == "Horizontal":
            image = generatePilImageHorizontal(progress_bar,workingIndex,bg_hex, selected_font_hex,deselected_font_hex,bubble_hex,icon_hex,render_factor,transparent=True)
        elif variant == "Alt-Horizontal":
           image = generatePilImageAltHorizontal(progress_bar,workingIndex,bg_hex, selected_font_hex,deselected_font_hex,bubble_hex,icon_hex,render_factor,transparent=True)
        else:
            raise ValueError("Something went wrong with your Main Menu Style")
        image = image.resize((deviceScreenWidth, deviceScreenHeight), Image.LANCZOS)
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
            if workingIndex == 0:
                bg_rgb = hex_to_rgb(bg_hex)
                background = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), bg_rgb)
                if background_image != None:
                    background.paste(background_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))
                background = background.resize(image.size, Image.LANCZOS)
                background.paste(image, (0, 0), image)  
                if config.developer_preview_var: 
                    background.save(os.path.join(internal_files_dir,f"TempPreview{threadNumber}.png"))
                background = background.resize((int(0.45*deviceScreenWidth), int(0.45*deviceScreenHeight)), Image.LANCZOS)
                background.save(os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}","preview.png"))

def getAlternateMenuNameDict():
    if os.path.exists(config.alt_text_path):
        try:
            
            with open(config.alt_text_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            data = {key.lower(): value for key, value in data.items()}
            return data
        except:
            return getDefaultAlternateMenuNameData()
    elif os.path.exists(os.path.join(script_dir,config.alt_text_path)):
        try:
            with open(os.path.join(script_dir,config.alt_text_path), 'r', encoding='utf-8') as file:
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
        print(f"The folder {folder_path} does not exist.")

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
                     ["Favourites","favourite"],
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
                     ["Favourites","favourite"],
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
                     ["Favourites","favourite"],
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
                     ["Favourites","favourite"],
                     ["History","history"],
                     ["Applications","apps"],
                     ["Information","info"],
                     ["Configuration","config"],
                     ["Reboot Device","reboot"],
                     ["Shutdown Device","shutdown"]]]]

def replace_in_file(file_path, search_string, replace_string):
    try:
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
    except Exception as e:
        if config.advanced_error_var:
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            messagebox.showerror("Error", f"An unexpected error occurred: {e}\n{tb_str}")
        else:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


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

def generate_theme(progress_bar, loading_window, threadNumber):
    try:

        progress_bar['value'] = 0
        if config.main_menu_style_var == "Vertical":
            progress_bar['maximum'] = 8
        elif config.main_menu_style_var == "Horizontal":
            progress_bar['maximum'] = 8
        elif config.main_menu_style_var == "Alt-Horizontal":
            progress_bar['maximum'] = 8
        else:
            raise ValueError("Something went wrong with your Main Menu Style")

        if threadNumber != -1:
            themeName = config.theme_name_entry + f" {config.main_menu_style_var}"
        else:
            themeName = config.theme_name_entry
        FillTempThemeFolder(progress_bar, threadNumber)
        if config.theme_directory_path == "":
            theme_dir = os.path.join(script_dir, "Generated Theme")
        else:
            theme_dir = config.theme_directory_path

        shutil.make_archive(os.path.join(theme_dir, themeName),"zip", os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}"))

        if config.developer_preview_var:
            preview_dir = os.path.join(theme_dir)

            os.makedirs(preview_dir,exist_ok=True)

            temp_preview_path = os.path.join(preview_dir, f"TempPreview{threadNumber}.png")
            if os.path.exists(temp_preview_path):
                os.remove(temp_preview_path)
            shutil.move(os.path.join(internal_files_dir, f"TempPreview{threadNumber}.png"), preview_dir)

            theme_preview_path = os.path.join(preview_dir, f"{themeName}.png")
            if os.path.exists(theme_preview_path):
                os.remove(theme_preview_path)

            os.rename(os.path.join(preview_dir,f"TempPreview{threadNumber}.png"), theme_preview_path)

            if os.path.exists(os.path.join(internal_files_dir, f"TempPreview{threadNumber}.png")):
                os.remove(os.path.join(internal_files_dir, f"TempPreview{threadNumber}.png"))
            if os.path.exists(os.path.join(theme_dir, "preview",f"TempPreview{threadNumber}.png")):
                os.remove(os.path.join(theme_dir, "preview",f"TempPreview{threadNumber}.png"))
        

        delete_folder(os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}"))
        if threadNumber == -1:
            messagebox.showinfo("Success", "Theme generated successfully.")
        loading_window.destroy()
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
            if os.path.exists(os.path.join(internal_files_dir, f"TempPreview{threadNumber}.png")):
                os.remove(os.path.join(internal_files_dir, f"TempPreview{threadNumber}.png"))
            if os.path.exists(os.path.join(theme_dir, "preview",f"TempPreview{threadNumber}.png")):
                os.remove(os.path.join(theme_dir, "preview",f"TempPreview{threadNumber}.png"))

def generate_themes(themes):
    if themes:
        threadNumber =0
        for theme in themes:
            config.apply_theme(theme)
            loading_window = tk.Toplevel(root)
            loading_window.title(f"Generating {config.theme_name_entry}...")
            loading_window.geometry("600x100")
            
            # Create a Progressbar widget in the loading window
            progress_bar = ttk.Progressbar(loading_window, orient="horizontal", length=280, mode="determinate")
            progress_bar.pack(pady=20)

            input_queue = queue.Queue()
            output_queue = queue.Queue()
            # Start the long-running task in a separate thread
            generate_theme(progress_bar,loading_window,threadNumber)
            #threading.Thread(target=generate_theme, args=(progress_bar, loading_window,threadNumber)).start() # TODO Fix this, doesnt work because config doesn't support multithreading
            threadNumber +=1
        messagebox.showinfo("Success", "Themes generated successfully.")


def FillTempThemeFolder(progress_bar, threadNumber):

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
    datetime_alignment = "Auto"
    datetime_padding = "10"
    status_alignment = "Right"
    status_padding = "10"
    default_radius = "10"
    header_height = "44"
    counter_padding_top = header_height

    shutil.copy2(os.path.join(internal_files_dir,"Template Scheme","template.txt"),os.path.join(newSchemeDir,"default.txt"))

    # Set up default colours that should be the same everywhere
    replace_in_file(os.path.join(newSchemeDir,"default.txt"), "{accent_hex}", str(accent_hex))
    replace_in_file(os.path.join(newSchemeDir,"default.txt"), "{base_hex}", str(base_hex))
    replace_in_file(os.path.join(newSchemeDir,"default.txt"), "{blend_hex}", str(blend_hex))
    replace_in_file(os.path.join(newSchemeDir,"default.txt"), "{muted_hex}", str(muted_hex))

    # More Global Settings
    glyph_width = 20
    glyph_to_text_pad = int(config.bubblePaddingVar)
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{glyph_padding_left}", str(int(int(config.bubblePaddingVar)+(glyph_width/2))))
    replace_in_file(os.path.join(newSchemeDir,"default.txt"), "{image_overlay}", str(config.include_overlay_var))
    replace_in_file(os.path.join(newSchemeDir,"default.txt"), "{footer_height}", config.footerHeightVar)
    content_height = deviceScreenHeight-contentPaddingTop-int(config.footerHeightVar)
    
    counter_alignment_map = {"Left":0,"Centre":1,"Right":2}
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{counter_alignment}", str(counter_alignment_map[counter_alignment]))
    replace_in_file(os.path.join(newSchemeDir,"default.txt"), "{counter_padding_top}", counter_padding_top)
    replace_in_file(os.path.join(newSchemeDir,"default.txt"), "{default_radius}", default_radius)

    # Global Header Settings:
    datetime_alignment_map = {"Auto":0,"Left":1,"Center":2,"Right":3}
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{datetime_align}", str(datetime_alignment_map[datetime_alignment]))
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{datetime_padding_left}", datetime_padding)
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{datetime_padding_right}", datetime_padding)
    status_alignment_map = {"Left":0,
                            "Right":1,
                            "Center":2,
                            "Icons spaced evenly across header":3,
                            "icons evenly distributed with equal space around them":4,
                            "First icon aligned left last icon aligned right all other icons evenly distributed":5}
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{status_align}", str(status_alignment_map[status_alignment]))
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{status_padding_left}", status_padding)
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{status_padding_right}", status_padding)
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{header_height}", header_height)
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{content_padding_top}", str(contentPaddingTop-44))

    if config.main_menu_style_var != "Vertical":
    # muxlaunch Specific settings
        shutil.copy2(os.path.join(newSchemeDir,"default.txt"),os.path.join(newSchemeDir,"muxlaunch.txt"))
        replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{content_height}",str(content_height))
        replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{content_item_count}", str(config.itemsPerScreenVar))
        replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{background_alpha}", "0")
        replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{selected_font_hex}", "ff0000")
        replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{deselected_font_hex}", "ff0000")
        replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{bubble_alpha}", "0")
        replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{bubble_padding_left}", "0")
        replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{bubble_padding_right}", "0")
        replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{content_alignment}", "0")
        replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{footer_alpha}", "0")
        replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{list_glyph_alpha}", "0")
        replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{list_text_alpha}", "0")
        replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{content_padding_left}", "0")
        replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{content_width}", str(deviceScreenWidth-10-2*(int(config.textPaddingVar)-int(config.bubblePaddingVar))))
        if "You want to wrap": #TODO Make this an actual option
            replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{navigation_type}", "4")
        else:
            replace_in_file(os.path.join(newSchemeDir,"muxlaunch.txt"),"{navigation_type}", "2")

    # muxnetwork Specific settings
    shutil.copy2(os.path.join(newSchemeDir,"default.txt"),os.path.join(newSchemeDir,"muxnetwork.txt"))
    replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{content_height}",str(int((content_height/int(config.itemsPerScreenVar))*(int(config.itemsPerScreenVar)-2))))
    replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{content_item_count}", str(int(config.itemsPerScreenVar)-2))
    replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{background_alpha}", "0")
    replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{selected_font_hex}", base_hex)
    replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{deselected_font_hex}", accent_hex)
    replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{bubble_alpha}", "255")
    replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{bubble_padding_left}", config.bubblePaddingVar)
    replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{bubble_padding_right}", config.bubblePaddingVar)
    content_alignment_map = {"Left":0,"Centre":1,"Right":2}
    replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{content_alignment}", str(content_alignment_map[config.global_alignment_var])) # TODO make this change for the different sections
    replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{content_padding_left}", str(int(config.textPaddingVar)-int(config.bubblePaddingVar)))
    replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{content_width}", str(deviceScreenWidth-10-2*(int(config.textPaddingVar)-int(config.bubblePaddingVar))))
    replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{footer_alpha}", "255")
    if "Not Show GLYPHS":
        replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{list_glyph_alpha}", "0")
    else:
        replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{list_glyph_alpha}", "255")
    replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{list_text_alpha}", "255")
    replace_in_file(os.path.join(newSchemeDir,"muxnetwork.txt"),"{navigation_type}", "0")

    # muxassign, muxgov Specific settings -  Content options, System govenor
    shutil.copy2(os.path.join(newSchemeDir,"default.txt"),os.path.join(newSchemeDir,"muxassign.txt"))
    replace_in_file(os.path.join(newSchemeDir,"muxassign.txt"),"{content_height}",str(content_height))
    replace_in_file(os.path.join(newSchemeDir,"muxassign.txt"),"{content_item_count}", str(config.itemsPerScreenVar))
    replace_in_file(os.path.join(newSchemeDir,"muxassign.txt"),"{background_alpha}", "0")
    replace_in_file(os.path.join(newSchemeDir,"muxassign.txt"),"{selected_font_hex}", base_hex)
    replace_in_file(os.path.join(newSchemeDir,"muxassign.txt"),"{deselected_font_hex}", accent_hex)
    replace_in_file(os.path.join(newSchemeDir,"muxassign.txt"),"{bubble_alpha}", "255")
    replace_in_file(os.path.join(newSchemeDir,"muxassign.txt"),"{bubble_padding_left}", str(int(int(config.bubblePaddingVar)+(glyph_width/2)+glyph_to_text_pad)))
    replace_in_file(os.path.join(newSchemeDir,"muxassign.txt"),"{bubble_padding_right}", config.bubblePaddingVar)
    content_alignment_map = {"Left":0,"Centre":1,"Right":2}
    replace_in_file(os.path.join(newSchemeDir,"muxassign.txt"),"{content_alignment}", str(content_alignment_map[config.global_alignment_var])) # TODO make this change for the different sections
    replace_in_file(os.path.join(newSchemeDir,"muxassign.txt"),"{content_padding_left}", str(int(config.textPaddingVar)-int(config.bubblePaddingVar)))
    replace_in_file(os.path.join(newSchemeDir,"muxassign.txt"),"{content_width}", str(deviceScreenWidth-10-2*(int(config.textPaddingVar)-int(config.bubblePaddingVar))))
    replace_in_file(os.path.join(newSchemeDir,"muxassign.txt"),"{list_glyph_alpha}", "255")
    replace_in_file(os.path.join(newSchemeDir,"muxassign.txt"),"{list_text_alpha}", "255")
    replace_in_file(os.path.join(newSchemeDir,"muxassign.txt"),"{navigation_type}", "0")
    shutil.copy2(os.path.join(newSchemeDir,"muxassign.txt"),os.path.join(newSchemeDir,"muxgov.txt"))
    replace_in_file(os.path.join(newSchemeDir,"muxassign.txt"),"{footer_alpha}", "255") ## Show footer in muxassign as can't generate custom one
    replace_in_file(os.path.join(newSchemeDir,"muxgov.txt"),"{footer_alpha}", "0") ## Don't in muxassign as can generate custom one



    # muxtheme Specific settings
    if False: # TODO Look into this later to see if muOS added support for "..."
        shutil.copy2(os.path.join(newSchemeDir,"default.txt"),os.path.join(newSchemeDir,"muxtheme.txt"))
        replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{content_height}",str(content_height))
        replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{content_item_count}", str(config.itemsPerScreenVar))
        replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{background_alpha}", "0")
        replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{selected_font_hex}", base_hex)
        replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{deselected_font_hex}", accent_hex)
        replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{bubble_alpha}", "255")
        replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{bubble_padding_left}", config.bubblePaddingVar)
        replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{bubble_padding_right}", config.bubblePaddingVar)
        content_alignment_map = {"Left":0,"Centre":1,"Right":2}
        replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{content_alignment}", str(content_alignment_map[config.global_alignment_var])) # TODO make this change for the different sections
        replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{content_padding_left}", str(int(config.textPaddingVar)-int(config.bubblePaddingVar)))
        previewArtWidth = 288
        replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{content_width}", str(deviceScreenWidth-10-previewArtWidth-5-(int(config.textPaddingVar)-int(config.bubblePaddingVar))))
        replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{footer_alpha}", "0")
        if "Not Show GLYPHS":
            replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{list_glyph_alpha}", "0")
        else:
            replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{list_glyph_alpha}", "255")
        replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{list_text_alpha}", "255")
        replace_in_file(os.path.join(newSchemeDir,"muxtheme.txt"),"{navigation_type}", "0")

    # rest of the default Specific settings
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{content_height}",str(content_height))
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{content_item_count}", str(config.itemsPerScreenVar))
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{background_alpha}", "0")
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{selected_font_hex}", base_hex)
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{deselected_font_hex}", accent_hex)
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{bubble_alpha}", "255")
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{bubble_padding_left}", config.bubblePaddingVar)
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{bubble_padding_right}", config.bubblePaddingVar)
    content_alignment_map = {"Left":0,"Centre":1,"Right":2}
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{content_alignment}", str(content_alignment_map[config.global_alignment_var])) # TODO make this change for the different sections
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{content_padding_left}", str(int(config.textPaddingVar)-int(config.bubblePaddingVar)))
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{content_width}", str(deviceScreenWidth-10-2*(int(config.textPaddingVar)-int(config.bubblePaddingVar))))
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{footer_alpha}", "0")
    if "Not Show GLYPHS":
        replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{list_glyph_alpha}", "0")
    else:
        replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{list_glyph_alpha}", "255")
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{list_text_alpha}", "255")
    replace_in_file(os.path.join(newSchemeDir,"default.txt"),"{navigation_type}", "0")

    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall"), exist_ok=True)

    if config.include_overlay_var:
        shutil.copy2(os.path.join(internal_files_dir,"Assets", "Overlays",f"{config.selected_overlay_var}.png"),os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","overlay.png"))

    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","font","panel"), exist_ok=True) #Font binaries stuff
    shutil.copy2(os.path.join(internal_files_dir,"Assets","Font","Binaries",f"BPreplayBold-unhinted-{int(fontSize)}.bin"),os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","font","panel","default.bin"))
    shutil.copy2(os.path.join(internal_files_dir,"Assets","Font","Binaries",f"BPreplayBold-unhinted-{int(20)}.bin"),os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","font","default.bin"))

    bootlogoimage = generatePilImageBootLogo(config.bgHexVar,config.deselectedFontHexVar,config.bubbleHexVar,render_factor).resize((deviceScreenWidth,deviceScreenHeight), Image.LANCZOS)
    bootlogoimage.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","bootlogo.bmp"), format='BMP')

    rotated_bootlogoimage = generatePilImageBootLogo(config.bgHexVar,config.deselectedFontHexVar,config.bubbleHexVar,render_factor).resize((deviceScreenWidth,deviceScreenHeight), Image.LANCZOS).rotate(90,expand=True)
    rotated_bootlogoimage.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","bootlogo-alt.bmp"), format='BMP')

    chargingimage = generatePilImageBootScreen(config.bgHexVar,
                                               config.deselectedFontHexVar,
                                               config.iconHexVar,
                                               "CHARGING...",
                                               render_factor,
                                               icon_path=os.path.join(internal_files_dir, "Assets", "ChargingLogo[5x].png")).resize((deviceScreenWidth,deviceScreenHeight), Image.LANCZOS)
    chargingimage.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxcharge.png"), format='PNG')

    loadingimage = generatePilImageBootScreen(config.bgHexVar,
                                               config.deselectedFontHexVar,
                                               config.iconHexVar,
                                               "LOADING...",
                                               render_factor).resize((deviceScreenWidth,deviceScreenHeight), Image.LANCZOS)
    loadingimage.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxstart.png"), format='PNG')

    shutdownimage = generatePilImageBootScreen(config.bgHexVar,
                                               config.deselectedFontHexVar,
                                               config.iconHexVar,
                                               "Shutting Down...",
                                               render_factor).resize((deviceScreenWidth,deviceScreenHeight), Image.LANCZOS)
    shutdownimage.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","shutdown.png"), format='PNG')

    rebootimage = generatePilImageBootScreen(config.bgHexVar,
                                               config.deselectedFontHexVar,
                                               config.iconHexVar,
                                               "Rebooting...",
                                               render_factor).resize((deviceScreenWidth,deviceScreenHeight), Image.LANCZOS)
    rebootimage.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","reboot.png"), format='PNG')

    defaultimage = generatePilImageDefaultScreen(config.bgHexVar,render_factor).resize((deviceScreenWidth,deviceScreenHeight), Image.LANCZOS)
    defaultimage.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","default.png"), format='PNG')

    #TODO If implimented it would be great to only set these once as a default.png type thing, and then make it work in every menu
    
    visualbuttonoverlay_B_BACK_A_SELECT = generateMenuHelperGuides([["B", "BACK"],["A", "SELECT"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]]).resize((deviceScreenWidth, deviceScreenHeight), Image.LANCZOS)
    
    muxconfig_items = ["clock","language","general","network","service","theme"]
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxconfig"), exist_ok=True)
    for item in muxconfig_items:
        visualbuttonoverlay_B_BACK_A_SELECT.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxconfig",f"{item}.png"), format='PNG')

    muxinfo_items = ["credit","system","tester"]
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxinfo"), exist_ok=True)
    for item in muxinfo_items:
        visualbuttonoverlay_B_BACK_A_SELECT.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxinfo",f"{item}.png"), format='PNG')

    muxoption_items = ["core","governor"]
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxoption"), exist_ok=True)
    for item in muxoption_items:
        visualbuttonoverlay_B_BACK_A_SELECT.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxoption",f"{item}.png"), format='PNG')


    
    visualbuttonoverlay_A_SELECT = generateMenuHelperGuides([["A", "SELECT"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]]).resize((deviceScreenWidth, deviceScreenHeight), Image.LANCZOS)

    muxlaunch_items = ["apps","config","explore","favourite","history","info","reboot","shutdown"]
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxlaunch"), exist_ok=True)
    for item in muxlaunch_items:
        visualbuttonoverlay_A_SELECT.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxlaunch",f"{item}.png"), format='PNG')
    

    visualbuttonoverlay_B_BACK = generateMenuHelperGuides([["B", "BACK"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]]).resize((deviceScreenWidth, deviceScreenHeight), Image.LANCZOS)

    muxtweakgen_items = ["hidden","bgm","sound","startup","colour","brightness","hdmi","power","shutdown","battery","sleep","interface","storage","advanced"]
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxtweakgen"), exist_ok=True)
    for item in muxtweakgen_items:
        visualbuttonoverlay_B_BACK.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxtweakgen",f"{item}.png"), format='PNG')

    muxpower_items = ["shutdown","battery","idle_display","idle_sleep"]
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxpower"), exist_ok=True)
    for item in muxpower_items:
        visualbuttonoverlay_B_BACK.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxpower",f"{item}.png"), format='PNG')

    muxvisual_items = ["battery","network","bluetooth","clock","boxart","boxartalign","name","dash","friendlyfolder","thetitleformat","titleincluderootdrive","folderitemcount","counterfolder","counterfile","backgroundanimation"]
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxvisual"), exist_ok=True)
    for item in muxvisual_items:
        visualbuttonoverlay_B_BACK.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxvisual",f"{item}.png"), format='PNG')
    
    muxtweakadv_items = ["accelerate","swap","thermal","font","volume","brightness","offset","lock","led","theme","retrowait","usbfunction","state","verbose","rumble","hdmi","storage"]
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxtweakadv"), exist_ok=True)
    for item in muxtweakadv_items:
        visualbuttonoverlay_B_BACK.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxtweakadv",f"{item}.png"), format='PNG')
    
    muxstorage_items = ["bios","catalogue","name","retroarch","config","core","favourite","history","music","save","screenshot","theme","language","network","syncthing","content"]
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxstorage"), exist_ok=True)
    for item in muxstorage_items:
        visualbuttonoverlay_B_BACK.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxstorage",f"{item}.png"), format='PNG')

    muxwebserv_items = ["shell","browser","terminal","sync","resilio","ntp"]
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxwebserv"), exist_ok=True)
    for item in muxwebserv_items:
        visualbuttonoverlay_B_BACK.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxwebserv",f"{item}.png"), format='PNG')
    
    muxrtc_items = ["year","month","day","hour","minute","notation","timezone"]
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxrtc"), exist_ok=True)
    for item in muxrtc_items:
        visualbuttonoverlay_B_BACK.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxrtc",f"{item}.png"), format='PNG')
    
    muxsysinfo_items = ["version","device","kernel","uptime","cpu","speed","governor","memory","temp","service","capacity","voltage"]
    os.makedirs(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxsysinfo"), exist_ok=True)
    for item in muxsysinfo_items:
        visualbuttonoverlay_B_BACK.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","static","muxsysinfo",f"{item}.png"), format='PNG')
    
    #TODO REMOVE THIS AS IT DOESNT ALLOW BACKGROUND REPLACEMENT (When Alternative is avaliable)
    #TODO wifi would be cool to have footers for once its possible

    bg_rgb = hex_to_rgb(bg_hex)
    background = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), bg_rgb)
    if background_image != None:
        background.paste(background_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))
    background = background.resize((deviceScreenWidth,deviceScreenHeight), Image.LANCZOS)
    

    visualbuttonoverlay_muxapp = generateMenuHelperGuides([["B", "BACK"],["A", "LAUNCH"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]]).resize((deviceScreenWidth, deviceScreenHeight), Image.LANCZOS)
    altered_background = Image.alpha_composite(background, visualbuttonoverlay_muxapp)
    altered_background.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxapp.png"), format='PNG')
    altered_background.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxtask.png"), format='PNG')

    visualbuttonoverlay_muxplore = generateMenuHelperGuides([["MENU", "INFO"],["Y", "FAVOURITE"],["X", "REFRESH"],["B", "BACK"],["A", "OPEN"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]]).resize((deviceScreenWidth, deviceScreenHeight), Image.LANCZOS)
    altered_background = Image.alpha_composite(background, visualbuttonoverlay_muxplore)
    altered_background.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxplore.png"), format='PNG')

    visualbuttonoverlay_muxfavourite = generateMenuHelperGuides([["MENU", "INFO"],["X", "REMOVE"],["B", "BACK"],["A", "OPEN"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]]).resize((deviceScreenWidth, deviceScreenHeight), Image.LANCZOS)
    altered_background = Image.alpha_composite(background, visualbuttonoverlay_muxfavourite)
    altered_background.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxfavourite.png"), format='PNG')

    visualbuttonoverlay_muxhistory = generateMenuHelperGuides([["MENU", "INFO"],["Y", "FAVOURITE"],["X", "REMOVE"],["B", "BACK"],["A", "OPEN"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]]).resize((deviceScreenWidth, deviceScreenHeight), Image.LANCZOS)
    altered_background = Image.alpha_composite(background, visualbuttonoverlay_muxhistory)
    altered_background.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxhistory.png"), format='PNG')

    visualbuttonoverlay_muxtimezone = generateMenuHelperGuides([["A", "SELECT"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]]).resize((deviceScreenWidth, deviceScreenHeight), Image.LANCZOS)
    altered_background = Image.alpha_composite(background, visualbuttonoverlay_muxtimezone)
    altered_background.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxtimezone.png"), format='PNG')

    visualbuttonoverlay_muxtheme_muxlanguage = generateMenuHelperGuides([["B", "BACK"],["A", "SELECT"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]]).resize((deviceScreenWidth, deviceScreenHeight), Image.LANCZOS)
    altered_background = Image.alpha_composite(background, visualbuttonoverlay_muxtheme_muxlanguage)
    altered_background.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxtheme.png"), format='PNG')
    altered_background.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxlanguage.png"), format='PNG')

    visualbuttonoverlay_muxarchive = generateMenuHelperGuides([["B", "BACK"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]]).resize((deviceScreenWidth, deviceScreenHeight), Image.LANCZOS)
    altered_background = Image.alpha_composite(background, visualbuttonoverlay_muxarchive)
    altered_background.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxarchive.png"), format='PNG')

    visualbuttonoverlay_muxnetprofile = generateMenuHelperGuides([["Y", "REMOVE"],["X", "SAVE"],["B", "BACK"],["A", "LOAD"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]]).resize((deviceScreenWidth, deviceScreenHeight), Image.LANCZOS)
    altered_background = Image.alpha_composite(background, visualbuttonoverlay_muxnetprofile)
    altered_background.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxnetprofile.png"), format='PNG')

    visualbuttonoverlay_muxnetscan = generateMenuHelperGuides([["X", "RESCAN"],["B", "BACK"],["A", "USE"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]]).resize((deviceScreenWidth, deviceScreenHeight), Image.LANCZOS)
    altered_background = Image.alpha_composite(background, visualbuttonoverlay_muxnetscan)
    altered_background.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxnetscan.png"), format='PNG')

    visualbuttonoverlay_muxgov = generateMenuHelperGuides([["Y", "RECURSIVE"],["X", "DIRECTORY"],["A", "INDIVIDUAL"],["B", "BACK"]],selected_font_path,bubble_hex,render_factor,lhsButtons=[["POWER","SLEEP"]]).resize((deviceScreenWidth, deviceScreenHeight), Image.LANCZOS)
    altered_background = Image.alpha_composite(background, visualbuttonoverlay_muxgov)
    altered_background.save(os.path.join(internal_files_dir,f".TempBuildTheme{threadNumber}","image","wall","muxgov.png"), format='PNG')

    
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

        except FileNotFoundError as e:
            print(f"FileNotFoundError: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    itemsList = []
    if config.version_var == "muOS 2410.1 Banana":
        workingMenus = menus2405_3

    else:
        raise ValueError("You Haven't Selected a muOS Version")
    
    workingMenus = [["muxlaunch",[["Content Explorer","explore"],
                                    ["Favourites","favourite"],
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
            ContinuousFolderImageGen(progress_bar,menu[0],itemsList[index],textPadding,rectanglePadding,ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}","image","static"), threadNumber=threadNumber)
        elif menu[0] == "muxlaunch":
            if config.main_menu_style_var == "Vertical":
                ContinuousFolderImageGen(progress_bar,menu[0],itemsList[index],textPadding,rectanglePadding,ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}","image","static"), threadNumber=threadNumber)
            elif config.main_menu_style_var == "Horizontal":
                HorizontalMenuGen(progress_bar,menu[0],itemsList[index], bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, icon_hex,render_factor, os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}","image","static"), variant = "Horizontal", threadNumber=threadNumber)
            elif config.main_menu_style_var == "Alt-Horizontal":
                HorizontalMenuGen(progress_bar,menu[0],itemsList[index], bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, icon_hex,render_factor, os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}","image","static"), variant = "Alt-Horizontal", threadNumber=threadNumber)

        else:
            ContinuousFolderImageGen(progress_bar,menu[0],itemsList[index],textPadding,rectanglePadding,ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, os.path.join(internal_files_dir, f".TempBuildTheme{threadNumber}","image","static"), threadNumber=threadNumber)


def select_alternate_menu_names():
    if os.path.exists(config.alt_text_path):
        menu_names_grid = MenuNamesGrid(root, menuNameMap, config.alt_text_path)
    elif os.path.exists(os.path.join(script_dir,config.alt_text_path)):
        menu_names_grid = MenuNamesGrid(root, menuNameMap, os.path.join(script_dir,config.alt_text_path))
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
        self.center_on_parent(parent)
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
    
    def center_on_parent(self, parent):
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
    save_settings()
        # Create a new Toplevel window for the loading bar
    loading_window = tk.Toplevel(root)
    loading_window.title("Loading...")
    loading_window.geometry("300x100")
    
    # Create a Progressbar widget in the loading window
    progress_bar = ttk.Progressbar(loading_window, orient="horizontal", length=280, mode="determinate")
    progress_bar.pack(pady=20)

    input_queue = queue.Queue()
    output_queue = queue.Queue()

    # Start the long-running task in a separate thread
    threading.Thread(target=generate_theme, args=(progress_bar, loading_window,-1)).start()

def start_bulk_theme_task():
    save_settings()
        # Create a new Toplevel window for the loading bar
    themes = config.load_premade_themes(os.path.join(script_dir,"PremadeThemes.json"))

    threading.Thread(target=generate_themes, args=(themes,)).start()


def on_resize(event):
    right_pane_width = image_frame.winfo_width()

root = tk.Tk()
root.title("MinUI Theme Generator")
root.minsize(1080, 500)  # Set a minimum size for the window

# Get the screen height
screen_height = root.winfo_screenheight()
window_height = int(min(screen_height*0.9, 1720))

root.geometry(f"1280x{window_height}")  # Set a default size for the window

subtitle_font = font.Font(family="Helvetica", size=10, weight="bold")
title_font = font.Font(family="Helvetica", size=14, weight="bold")

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
global_alignment_var = tk.StringVar()
selected_overlay_var = tk.StringVar()
theme_alignment_var = tk.StringVar()
main_menu_style_var = tk.StringVar()
content_alignment_var = tk.StringVar()
show_file_counter_var = tk.IntVar()
show_console_name_var = tk.IntVar()
show_hidden_files_var = tk.IntVar()
include_overlay_var = tk.IntVar()
alternate_menu_names_var = tk.IntVar()
remove_right_menu_guides_var = tk.IntVar()
remove_left_menu_guides_var = tk.IntVar()
override_bubble_cut_var = tk.IntVar()
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
grid_helper.add(tk.Label(scrollable_frame, text="Global Configurations", font=subtitle_font), colspan=3, sticky="w", next_row=True)

# Define the StringVar variables
textPaddingVar = tk.StringVar()
VBG_Horizontal_Padding_var = tk.StringVar()
VBG_Vertical_Padding_var = tk.StringVar()
bubblePaddingVar = tk.StringVar()
itemsPerScreenVar = tk.StringVar()
footerHeightVar = tk.StringVar()
contentPaddingTopVar = tk.StringVar()
boxArtPaddingVar = tk.StringVar()
folderBoxArtPaddingVar = tk.StringVar()
font_size_var = tk.StringVar()
bgHexVar = tk.StringVar()
selectedFontHexVar = tk.StringVar()
deselectedFontHexVar = tk.StringVar()
bubbleHexVar = tk.StringVar()
iconHexVar = tk.StringVar()
maxGamesBubbleLengthVar = tk.StringVar()
maxFoldersBubbleLengthVar = tk.StringVar()
previewConsoleNameVar = tk.StringVar()

# Option for textPadding
grid_helper.add(tk.Label(scrollable_frame, text="Text Padding:"), sticky="w")
text_padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=textPaddingVar)
grid_helper.add(text_padding_entry, next_row=True)

# Option for rectanglePadding
grid_helper.add(tk.Label(scrollable_frame, text="Bubble Padding:"), sticky="w")
rectangle_padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=bubblePaddingVar)
grid_helper.add(rectangle_padding_entry, next_row=True)

# Option for ItemsPerScreen
grid_helper.add(tk.Label(scrollable_frame, text="Items Per Screen (Better if Odd) [5-13 Inclusive]:"), sticky="w")
items_per_screen_entry = tk.Entry(scrollable_frame, width=50, textvariable=itemsPerScreenVar)
grid_helper.add(items_per_screen_entry, next_row=True)

# Option for ItemsPerScreen
grid_helper.add(tk.Label(scrollable_frame, text="Padding from top, for list content (Default 44):"), sticky="w")
content_padding_top_entry = tk.Entry(scrollable_frame, width=50, textvariable=contentPaddingTopVar)
grid_helper.add(content_padding_top_entry, next_row=True)

# Option for ItemsPerScreen
grid_helper.add(tk.Label(scrollable_frame, text="Footer Height:"), sticky="w")
footer_height_entry = tk.Entry(scrollable_frame, width=50, textvariable=footerHeightVar)
grid_helper.add(footer_height_entry, next_row=True)

# Option for Background Colour
grid_helper.add(tk.Label(scrollable_frame, text="Background Hex Colour: #"), sticky="w")
background_hex_entry = tk.Entry(scrollable_frame, width=50, textvariable=bgHexVar)
grid_helper.add(background_hex_entry, next_row=True)

# Option for Selected Font Hex Colour
grid_helper.add(tk.Label(scrollable_frame, text="Selected Font Hex Colour: #"), sticky="w")
selected_font_hex_entry = tk.Entry(scrollable_frame, width=50, textvariable=selectedFontHexVar)
grid_helper.add(selected_font_hex_entry, next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Show Background Through Text on Launch Menu", variable=transparent_text_var), colspan=3, sticky="w", next_row=True)

# Option for Deselected Font Hex Colour
grid_helper.add(tk.Label(scrollable_frame, text="Deselected Font Hex Colour: #"), sticky="w")
deselected_font_hex_entry = tk.Entry(scrollable_frame, width=50, textvariable=deselectedFontHexVar)
grid_helper.add(deselected_font_hex_entry, next_row=True)

# Option for Bubble Hex Colour
grid_helper.add(tk.Label(scrollable_frame, text="Bubble Hex Colour: #"), sticky="w")
bubble_hex_entry = tk.Entry(scrollable_frame, width=50, textvariable=bubbleHexVar)
grid_helper.add(bubble_hex_entry, next_row=True)

# Option for Icon Hex Colour
grid_helper.add(tk.Label(scrollable_frame, text="Icon Hex Colour: #"), sticky="w")
icon_hex_entry = tk.Entry(scrollable_frame, width=50, textvariable=iconHexVar)
grid_helper.add(icon_hex_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Global Text Alignment"), sticky="w")
globalAlignmentOptions = ["Left", "Centre", "Right"]
global_alignment_option_menu = tk.OptionMenu(scrollable_frame, global_alignment_var, *globalAlignmentOptions)
grid_helper.add(global_alignment_option_menu, colspan=3, sticky="w", next_row=True)
grid_helper.add(tk.Label(scrollable_frame, text="Text alignment might be a bit buggy, not recommended to change off Left yet",fg="#f00"), colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="[Optional] Override background colour with image", variable=use_custom_background_var), sticky="w")
grid_helper.add(tk.Entry(scrollable_frame, textvariable=background_image_path, width=50))
grid_helper.add(tk.Button(scrollable_frame, text="Browse...", command=select_background_image_path), next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="*[Optional] Use Custom font:", variable=use_alt_font_var), sticky="w")
grid_helper.add(tk.Entry(scrollable_frame, textvariable=alt_font_path, width=50))
grid_helper.add(tk.Button(scrollable_frame, text="Browse...", command=select_alt_font_path), next_row=True)
grid_helper.add(tk.Label(scrollable_frame,text="*Use if text override characters not supported by default font\n!!!Currently Wont Work In Menus!!! left in as a reminder",fg="#00f"),sticky="w",next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Font size (10-55 inclusive):"), sticky="w")
custom_font_size_entry = tk.Entry(scrollable_frame, width=50, textvariable=font_size_var)
grid_helper.add(custom_font_size_entry, next_row=True)

# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Theme Specific Configurations", font=subtitle_font), sticky="w", next_row=True)


grid_helper.add(tk.Label(scrollable_frame, text="Main Menu Style"), sticky="w")
MainMenuStyleOptions = ["Horizontal", "Vertical", "Alt-Horizontal"]
main_menu_style_option_menu = tk.OptionMenu(scrollable_frame, main_menu_style_var, *MainMenuStyleOptions)
grid_helper.add(main_menu_style_option_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="muOS Version"), sticky="w")
OLDoptions = ["muOS 2405 BEANS", "muOS 2405.1 REFRIED BEANS", "muOS 2405.2 BAKED BEANS", "muOS 2405.3 COOL BEANS"]
options = ["muOS 2410.1 Banana"]
option_menu = tk.OptionMenu(scrollable_frame, version_var, *options)
grid_helper.add(option_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Use Custom Bootlogo Image:", variable=use_custom_bootlogo_var), sticky="w")
grid_helper.add(tk.Entry(scrollable_frame, textvariable=bootlogo_image_path, width=50))
grid_helper.add(tk.Button(scrollable_frame, text="Browse...", command=select_bootlogo_image_path), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Theme Text Alignment - Not seperated from global yet"), sticky="w")
themeAlignmentOptions = ["Global", "Left", "Centre", "Right"]
theme_alignment_option_menu = tk.OptionMenu(scrollable_frame, theme_alignment_var, *themeAlignmentOptions)
grid_helper.add(theme_alignment_option_menu, colspan=3, sticky="w", next_row=True)

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


grid_helper.add(tk.Checkbutton(scrollable_frame, text="Remove Left Visual Button Guides", variable=remove_left_menu_guides_var), sticky="w")
grid_helper.add(tk.Checkbutton(scrollable_frame, text="Remove Right Visual Button Guides", variable=remove_right_menu_guides_var), colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Horizontal Padding for Visual Button Guides:"), sticky="w")
VBG_Horizontal_Padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=VBG_Horizontal_Padding_var)
grid_helper.add(VBG_Horizontal_Padding_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Vertical Padding for Visual Button Guides:"), sticky="w")
VBG_Vertical_Padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=VBG_Vertical_Padding_var)
grid_helper.add(VBG_Vertical_Padding_entry, next_row=True)




# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Box Art Specific Configurations", font=subtitle_font), colspan=3, sticky="w", next_row=True)
grid_helper.add(tk.Label(scrollable_frame, text="SECTION NOT IMPLIMENTED YET",fg="#f00"), colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Override Auto Cut Bubble off [Might want to use for fading box art]", variable=override_bubble_cut_var),colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text=" - [Games] Cut bubble off at (px):"), sticky="w")

max_games_bubble_length_entry = tk.Entry(scrollable_frame, width=50, textvariable=maxGamesBubbleLengthVar)
grid_helper.add(max_games_bubble_length_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text=" - [Folders] Cut bubble off at (px):"), sticky="w")

max_folders_bubble_length_entry = tk.Entry(scrollable_frame, width=50, textvariable=maxFoldersBubbleLengthVar)
grid_helper.add(max_folders_bubble_length_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text=" - This would usually be 640-width of your boxart",fg="#00f"), colspan=3, sticky="w", next_row=True)

# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Content Explorer Specific Configurations", font=subtitle_font), colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="SECTION NOT IMPLIMENTED YET",fg="#f00"), colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Content Explorer Text Alignment"), sticky="w")
contentAlignmentOptions = ["Global", "Left", "Centre", "Right"]
content_alignment_option_menu = tk.OptionMenu(scrollable_frame, content_alignment_var, *contentAlignmentOptions)
grid_helper.add(content_alignment_option_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Show Console Name at top", variable=show_console_name_var), sticky="w", next_row=True)

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
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)
# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

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
    
    # Paste the original image at the center of the new image, accounting for the outline width and gap
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
        if old_selected_overlay_var != config.selected_overlay_var:
            preview_overlay_image = Image.open(os.path.join(internal_files_dir, "Assets", "Overlays", f"{config.selected_overlay_var}.png")).convert("RGBA")
    except:
        preview_overlay_image = Image.open(os.path.join(internal_files_dir, "Assets", "Overlays", f"{config.selected_overlay_var}.png")).convert("RGBA")
    old_selected_overlay_var = config.selected_overlay_var
    gameFolderName = "Game Boy"
    global footerHeight
    global contentPaddingTop
    try:
        footerHeight = int(config.footer_height_entry)
    except:
        footerHeight = 55
    try:
        contentPaddingTop = int(config.content_padding_top_entry)
    except:
        contentPaddingTop = 40
    
    global background_image

    if (config.use_custom_background_var) and os.path.exists(config.background_image_path):
        background_image = Image.open(config.background_image_path)
    else:
        background_image = None

    global menus2405
    global menus2405_1 ## NOT GLOBALS AHH SORRY HACKY SHOULD REMOVE
    global menus2405_2
    global menus2405_3

    previewApplicationList = []
    if config.version_var == "muOS 2410.1 Banana":
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

    if image_frame.winfo_width() < 100:
        preview_size = [int(deviceScreenWidth/2),int(deviceScreenHeight/2)]
    else:
        
        previewRenderFactor = math.ceil(image_frame.winfo_width()/deviceScreenWidth)+1 # Affectively anti aliasing in the preview

        preview_size = [int(image_frame.winfo_width()),int(image_frame.winfo_width()*(deviceScreenHeight/deviceScreenWidth))]
    #preview_size = [int(640/2),int(480/2)]

    # This function will run whenever any traced variable changes
    try:
        previewItemList = [['Content Explorer', 'Menu', 'explore'], ['Favourites', 'Menu', 'favourite'], ['History', 'Menu', 'history'], ['Applications', 'Menu', 'apps'], ['Information', 'Menu', 'info'], ['Configuration', 'Menu', 'config'], ['Reboot Device', 'Menu', 'reboot'], ['Shutdown Device', 'Menu', 'shutdown']]
        
        if config.main_menu_style_var == "Horizontal":
            image1 = generatePilImageHorizontal(fakeprogressbar,
                                                0,
                                                config.bgHexVar,
                                                config.selectedFontHexVar,
                                                config.deselectedFontHexVar,
                                                config.bubbleHexVar,
                                                config.iconHexVar,
                                                previewRenderFactor,
                                                transparent=False).resize(preview_size, Image.LANCZOS)
        elif config.main_menu_style_var == "Alt-Horizontal":
            image1 = generatePilImageAltHorizontal(fakeprogressbar,
                                                0,
                                                config.bgHexVar,
                                                config.selectedFontHexVar,
                                                config.deselectedFontHexVar,
                                                config.bubbleHexVar,
                                                config.iconHexVar,
                                                previewRenderFactor,
                                                transparent=False).resize(preview_size, Image.LANCZOS)
        elif config.main_menu_style_var == "Vertical":
            image1 = generatePilImageVertical(fakeprogressbar,0,
                                            "muxlaunch",
                                            previewItemList[0:int(config.items_per_screen_entry)],
                                            int(config.textPaddingVar),
                                            int(config.bubblePaddingVar),
                                            int(config.items_per_screen_entry),
                                            config.bgHexVar,
                                            config.selectedFontHexVar,
                                            config.deselectedFontHexVar,
                                            config.bubbleHexVar
                                            ,previewRenderFactor,transparent=False).resize(preview_size, Image.LANCZOS)

        image2 = generatePilImageVertical(fakeprogressbar,0,
                                        "muxapp",
                                        previewApplicationList[0:int(config.items_per_screen_entry)],
                                        int(config.textPaddingVar),
                                        int(config.bubblePaddingVar),
                                        int(config.items_per_screen_entry),
                                        config.bgHexVar,
                                        config.selectedFontHexVar,
                                        config.deselectedFontHexVar,
                                        config.bubbleHexVar,
                                        previewRenderFactor,
                                        fileCounter="1 / " + config.items_per_screen_entry,
                                        transparent=False).resize(preview_size, Image.LANCZOS)

        if config.main_menu_style_var == "Horizontal":
            image3 = generatePilImageHorizontal(fakeprogressbar,
                                                4,
                                                config.bgHexVar,
                                                config.selectedFontHexVar,
                                                config.deselectedFontHexVar,
                                                config.bubbleHexVar,
                                                config.iconHexVar,
                                                previewRenderFactor,
                                                transparent=False).resize(preview_size, Image.LANCZOS)
        
        elif config.main_menu_style_var == "Alt-Horizontal":
            image3 = generatePilImageAltHorizontal(fakeprogressbar,
                                                4,
                                                config.bgHexVar,
                                                config.selectedFontHexVar,
                                                config.deselectedFontHexVar,
                                                config.bubbleHexVar,
                                                config.iconHexVar,
                                                previewRenderFactor,
                                                transparent=False).resize(preview_size, Image.LANCZOS)

        if config.include_overlay_var and config.selected_overlay_var != "":
            preview_overlay_resized = preview_overlay_image.resize(image1.size, Image.LANCZOS)
            image1.paste(preview_overlay_resized,(0,0),preview_overlay_resized)
            image2.paste(preview_overlay_resized,(0,0),preview_overlay_resized)
            if config.main_menu_style_var != "Vertical":
                image3.paste(preview_overlay_resized,(0,0),preview_overlay_resized)
    
        update_image_label(image_label1, image1)
        update_image_label(image_label2, image2)
        if config.main_menu_style_var != "Vertical":
            update_image_label(image_label3, image3)
        else:
            remove_image_from_label(image_label3)
        valid_params = True
    except:
        if get_current_image(image_label1) != None and get_current_image(image_label2) != None and get_current_image(image_label3):
            if valid_params:
                redOutlineImage1 = outline_image_with_inner_gap(get_current_image(image_label1)).resize(preview_size, Image.LANCZOS)
                redOutlineImage2 = outline_image_with_inner_gap(get_current_image(image_label2)).resize(preview_size, Image.LANCZOS)
                if config.main_menu_style_var != "Vertical":
                    redOutlineImage3 = outline_image_with_inner_gap(get_current_image(image_label3)).resize(preview_size, Image.LANCZOS)
                update_image_label(image_label1, redOutlineImage1)
                update_image_label(image_label2, redOutlineImage2)
                if config.main_menu_style_var != "Vertical":
                    update_image_label(image_label3, redOutlineImage3)
                valid_params = False


def save_settings(*args):
    config.textPaddingVar = textPaddingVar.get()
    config.text_padding_entry = text_padding_entry.get()
    config.VBG_Horizontal_Padding_entry = VBG_Horizontal_Padding_entry.get()
    config.VBG_Vertical_Padding_entry = VBG_Vertical_Padding_entry.get()
    config.bubblePaddingVar = bubblePaddingVar.get()
    config.rectangle_padding_entry = rectangle_padding_entry.get()
    config.itemsPerScreenVar = itemsPerScreenVar.get()
    config.items_per_screen_entry = items_per_screen_entry.get()
    config.footerHeightVar = footerHeightVar.get()
    config.content_padding_top_entry = content_padding_top_entry.get()
    config.contentPaddingTopVar = contentPaddingTopVar.get()
    config.custom_font_size_entry = custom_font_size_entry.get()
    config.font_size_var = font_size_var.get()
    config.footer_height_entry = footer_height_entry.get()
    config.bgHexVar = bgHexVar.get()
    config.background_hex_entry = background_hex_entry.get()
    config.selectedFontHexVar = selectedFontHexVar.get()
    config.selected_font_hex_entry = selected_font_hex_entry.get()
    config.deselectedFontHexVar = deselectedFontHexVar.get()
    config.deselected_font_hex_entry = deselected_font_hex_entry.get()
    config.bubbleHexVar = bubbleHexVar.get()
    config.bubble_hex_entry = bubble_hex_entry.get()
    config.iconHexVar = iconHexVar.get()
    config.icon_hex_entry = icon_hex_entry.get()
    config.include_overlay_var = include_overlay_var.get()
    config.alternate_menu_names_var = alternate_menu_names_var.get()
    config.remove_right_menu_guides_var = remove_right_menu_guides_var.get()
    config.remove_left_menu_guides_var = remove_left_menu_guides_var.get()
    config.box_art_directory_path = box_art_directory_path.get()
    config.maxGamesBubbleLengthVar = maxGamesBubbleLengthVar.get()
    config.maxFoldersBubbleLengthVar = maxFoldersBubbleLengthVar.get()
    config.roms_directory_path = roms_directory_path.get()
    config.application_directory_path = application_directory_path.get()
    config.previewConsoleNameVar = previewConsoleNameVar.get()
    config.show_hidden_files_var = show_hidden_files_var.get()
    config.override_bubble_cut_var = override_bubble_cut_var.get()
    config.page_by_page_var = page_by_page_var.get()
    config.transparent_text_var = transparent_text_var.get()
    config.override_folder_box_art_padding_var = override_folder_box_art_padding_var.get()
    config.boxArtPaddingVar = boxArtPaddingVar.get()
    config.folderBoxArtPaddingVar = folderBoxArtPaddingVar.get()
    config.content_alignment_var = content_alignment_var.get()
    config.theme_alignment_var = theme_alignment_var.get()
    config.main_menu_style_var = main_menu_style_var.get()
    config.version_var = version_var.get()
    config.global_alignment_var = global_alignment_var.get()
    config.selected_overlay_var = selected_overlay_var.get()
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
    config.save_config()
    on_change()

def load_settings():
    textPaddingVar.set(config.textPaddingVar)
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
    footer_height_entry.delete(0, tk.END)
    footer_height_entry.insert(0, config.footer_height_entry)
    content_padding_top_entry.delete(0, tk.END)
    content_padding_top_entry.insert(0, config.content_padding_top_entry)
    bubblePaddingVar.set(config.bubblePaddingVar)
    itemsPerScreenVar.set(config.itemsPerScreenVar)
    footerHeightVar.set(config.footerHeightVar)
    contentPaddingTopVar.set(config.contentPaddingTopVar)
    boxArtPaddingVar.set(config.boxArtPaddingVar)
    folderBoxArtPaddingVar.set(config.folderBoxArtPaddingVar)
    font_size_var.set(config.font_size_var)
    custom_font_size_entry.delete(0, tk.END)
    custom_font_size_entry.insert(0, config.custom_font_size_entry)
    bgHexVar.set(config.bgHexVar)
    selectedFontHexVar.set(config.selectedFontHexVar)
    deselectedFontHexVar.set(config.deselectedFontHexVar)
    bubbleHexVar.set(config.bubbleHexVar)
    iconHexVar.set(config.iconHexVar)
    include_overlay_var.set(config.include_overlay_var)
    alternate_menu_names_var.set(config.alternate_menu_names_var)
    remove_right_menu_guides_var.set(config.remove_right_menu_guides_var)
    remove_left_menu_guides_var.set(config.remove_left_menu_guides_var)
    box_art_directory_path.set(config.box_art_directory_path)
    maxGamesBubbleLengthVar.set(config.maxGamesBubbleLengthVar)
    maxFoldersBubbleLengthVar.set(config.maxFoldersBubbleLengthVar)
    roms_directory_path.set(config.roms_directory_path)
    application_directory_path.set(config.application_directory_path)
    previewConsoleNameVar.set(config.previewConsoleNameVar)
    show_hidden_files_var.set(config.show_hidden_files_var)
    override_bubble_cut_var.set(config.override_bubble_cut_var)
    override_folder_box_art_padding_var.set(config.override_folder_box_art_padding_var)
    page_by_page_var.set(config.page_by_page_var)
    transparent_text_var.set(config.transparent_text_var)
    version_var.set(config.version_var)
    global_alignment_var.set(config.global_alignment_var)
    selected_overlay_var.set(config.selected_overlay_var)
    theme_alignment_var.set(config.theme_alignment_var)
    main_menu_style_var.set(config.main_menu_style_var)
    content_alignment_var.set(config.content_alignment_var)
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



load_settings()
menuNameMap = getAlternateMenuNameDict()

# Attach trace callbacks to the variables
textPaddingVar.trace_add("write", save_settings)
VBG_Horizontal_Padding_var.trace_add("write",save_settings)
VBG_Vertical_Padding_var.trace_add("write",save_settings)
bubblePaddingVar.trace_add("write", save_settings)
itemsPerScreenVar.trace_add("write", save_settings)
footerHeightVar.trace_add("write", save_settings)
contentPaddingTopVar.trace_add("write",save_settings)
boxArtPaddingVar.trace_add("write", save_settings)
folderBoxArtPaddingVar.trace_add("write", save_settings)
font_size_var.trace_add("write", save_settings)
bgHexVar.trace_add("write", save_settings)
selectedFontHexVar.trace_add("write", save_settings)
deselectedFontHexVar.trace_add("write", save_settings)
bubbleHexVar.trace_add("write", save_settings)
iconHexVar.trace_add("write", save_settings)
show_file_counter_var.trace_add("write", save_settings)
show_console_name_var.trace_add("write", save_settings)
include_overlay_var.trace_add("write", save_settings)
alternate_menu_names_var.trace_add("write", save_settings)
remove_right_menu_guides_var.trace_add("write", save_settings)
remove_left_menu_guides_var.trace_add("write", save_settings)
box_art_directory_path.trace_add("write", save_settings)
maxGamesBubbleLengthVar.trace_add("write", save_settings)
maxFoldersBubbleLengthVar.trace_add("write", save_settings)
roms_directory_path.trace_add("write", save_settings)
application_directory_path.trace_add("write", save_settings)
previewConsoleNameVar.trace_add("write", save_settings)
show_hidden_files_var.trace_add("write", save_settings)
override_bubble_cut_var.trace_add("write", save_settings)
override_folder_box_art_padding_var.trace_add("write", save_settings)
page_by_page_var.trace_add("write", save_settings)
transparent_text_var.trace_add("write", save_settings)
version_var.trace_add("write", save_settings)
global_alignment_var.trace_add("write", save_settings)
selected_overlay_var.trace_add("write",save_settings)
content_alignment_var.trace_add("write", save_settings)
theme_alignment_var.trace_add("write", save_settings)
main_menu_style_var.trace_add("write",save_settings)
am_theme_directory_path.trace_add("write", save_settings)
theme_directory_path.trace_add("write", save_settings)
catalogue_directory_path.trace_add("write", save_settings)
name_json_path.trace_add("write", save_settings)
background_image_path.trace_add("write", save_settings)
bootlogo_image_path.trace_add("write", save_settings)
am_ignore_theme_var.trace_add("write", save_settings)
am_ignore_cd_var.trace_add("write", save_settings)
advanced_error_var.trace_add("write", save_settings)
developer_preview_var.trace_add("write", save_settings)
use_alt_font_var.trace_add("write", save_settings)
use_custom_background_var.trace_add("write",save_settings)
use_custom_bootlogo_var.trace_add("write", save_settings)
alt_font_path.trace_add("write", save_settings)
alt_text_path.trace_add("write",save_settings)

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



save_settings()

# Run the main loop
root.mainloop()