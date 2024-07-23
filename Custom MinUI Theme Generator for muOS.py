# -*- coding: utf-8 -*-
from PIL import ImageTk,Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from bidi import get_display as bidiGet_display
import os
import sys
import math
import tkinter as tk
from tkinter import font
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
class Config:
    def __init__(self, config_file=os.path.join(script_dir,'MinUIThemeGeneratorConfig.json')):
        self.config_file = config_file
        self.scrollBarWidthVar = 10
        self.textPaddingVar = 25
        self.bubblePaddingVar = 20
        self.itemsPerScreenVar = 9
        self.footerHeightVar = 55
        self.override_font_size_var = False
        self.customFontSizeVar = ""
        self.bgHexVar = "000000"
        self.selectedFontHexVar = "000000"
        self.deselectedFontHexVar = "ffffff"
        self.bubbleHexVar = "ffffff"
        self.iconHexVar = "ffffff"
        self.remove_brackets_var = False
        self.remove_square_brackets_var = False
        self.replace_hyphen_var = False
        self.also_games_var = False
        self.move_the_var = False
        self.crt_overlay_var = False
        self.alternate_menu_names_var = False
        self.remove_right_menu_guides_var = False
        self.remove_left_menu_guides_var = False
        self.overlay_box_art_var = False
        self.boxArtPaddingVar = 0
        self.folderBoxArtPaddingVar = 0
        self.box_art_directory_path = ""
        self.maxBubbleLengthVar = deviceScreenWidth
        self.roms_directory_path = ""
        self.application_directory_path = ""
        self.previewConsoleNameVar = "Nintendo Game Boy"
        self.show_hidden_files_var = False
        self.vertical_var = False
        self.override_bubble_cut_var = False
        self.override_folder_box_art_padding_var = False
        self.page_by_page_var = False
        self.version_var = "Select a version"
        self.global_alignment_var = "Left"
        self.theme_alignment_var = "Global"
        self.content_alignment_var = "Global"
        self.am_theme_directory_path = ""
        self.theme_directory_path = ""
        self.catalogue_directory_path = ""
        self.name_json_path = ""
        self.background_image_path = ""
        self.alt_font_path = ""
        self.use_alt_font_var = False
        self.themeName = "MinUIfied - Default Theme"
        self.amThemeName = "MinUIfied - Default AM Theme"
        self.am_ignore_theme_var = False
        self.am_ignore_cd_var = False
        self.advanced_error_var = False
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

background_image = None

# Define constants
render_factor = 5


AlternateMenuNamesPath = os.path.join(script_dir,"AlternateMenuNames.json")

ConsoleAssociationsPath = os.path.join(script_dir,"ConsoleAssociations.json")
defaultConsoleAssociationsPath = os.path.join(internal_files_dir,"_ConsoleAssociations.json")

headerHeight = 40
footerHeight = 55
textMF = 0.7
additions_Blank = "Blank"
additions_PowerHelpBackOkay = "PowerHelpBackOkay"
additions_powerHelpOkay = "PowerHelpOkay"
additions_Preview = "Preview"


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

def applyMenuHelperGuides(muOSSystemName,image,selected_font_path,primary_colour_hex,secondary_colour_hex,render_factor):
    draw = ImageDraw.Draw(image)
    
    
    menu_helper_guide_height = (9/11)*footerHeight
        
    in_smaller_bubble_font_size = menu_helper_guide_height*(16/45)*render_factor
    inSmallerBubbleFont = ImageFont.truetype(selected_font_path, in_smaller_bubble_font_size)

    in_bubble_font_size = menu_helper_guide_height*(19/45)*render_factor
    inBubbleFont = ImageFont.truetype(selected_font_path, in_bubble_font_size)

    single_letter_font_size = menu_helper_guide_height*(23/45)*render_factor
    singleLetterFont = ImageFont.truetype(selected_font_path, single_letter_font_size)

    powerText = "POWER"
    sleepText = "SLEEP"
    menuText = "MENU"
    helpText = "HELP"
    backText = "BACK"
    okayText = "OKAY"
    confirmText = "CONFIRM"
    launchText = "LAUNCH"
    aText = "A"
    bText = "B"
    if alternate_menu_names_var.get():
        powerText = bidiGet_display(menuNameMap.get("power", "POWER"))
        sleepText = bidiGet_display(menuNameMap.get("sleep","SLEEP"))
        menuText = bidiGet_display(menuNameMap.get("menu","MENU"))
        helpText = bidiGet_display(menuNameMap.get("help","HELP"))
        backText = bidiGet_display(menuNameMap.get("back","BACK"))
        okayText = bidiGet_display(menuNameMap.get("okay","OKAY"))
        confirmText = bidiGet_display(menuNameMap.get("confirm","CONFIRM"))
        launchText = bidiGet_display(menuNameMap.get("launch","LAUNCH"))
    
    horizontal_small_padding = menu_helper_guide_height*(5/45)
    horizontal_padding = menu_helper_guide_height*(6.5/45)
    horizontal_large_padding = menu_helper_guide_height*(8.5/45)
    
    bottom_guide_middle_y = deviceScreenHeight-horizontal_small_padding-(menu_helper_guide_height/2)

    
    #guide_bubble_height = 80
    guide_small_bubble_height = menu_helper_guide_height-(horizontal_padding*2)

    isb_ascent, isb_descent = inSmallerBubbleFont.getmetrics()
    isb_text_height = isb_ascent + isb_descent
    in_smaller_bubble_text_y = bottom_guide_middle_y*render_factor - (isb_text_height / 2)

    ib_ascent, ib_descent = inBubbleFont.getmetrics()
    ib_text_height = ib_ascent + ib_descent
    in_bubble_text_y = bottom_guide_middle_y*render_factor - (ib_text_height / 2)

    sl_ascent, sl_descent = singleLetterFont.getmetrics()
    sl_text_height = sl_ascent + sl_descent
    single_letter_text_y = bottom_guide_middle_y*render_factor - (sl_text_height / 2)

    


    if not remove_left_menu_guides_var.get():
        powerTextBbox = draw.textbbox((0, 0), powerText, font=inSmallerBubbleFont)
        powerTextWidth = powerTextBbox[2] - powerTextBbox[0]
        sleepTextBbox = draw.textbbox((0, 0), sleepText, font=inBubbleFont)
        sleepTextWidth = sleepTextBbox[2] - sleepTextBbox[0]
        totalWidth = horizontal_padding+horizontal_large_padding+(powerTextWidth/render_factor)+horizontal_large_padding+horizontal_small_padding+(sleepTextWidth/render_factor)+horizontal_large_padding
        smallerBubbleWidth = horizontal_large_padding+(powerTextWidth/render_factor)+horizontal_large_padding
        draw.rounded_rectangle( ## Power Behind Bubble
                [(horizontal_small_padding*render_factor, (bottom_guide_middle_y-menu_helper_guide_height/2)*render_factor), ((totalWidth+horizontal_small_padding)*render_factor, (bottom_guide_middle_y+menu_helper_guide_height/2)*render_factor)],
                radius=(menu_helper_guide_height/2)*render_factor,
                fill=f"#{percentage_color(primary_colour_hex,secondary_colour_hex,0.133)}"
            )
        
        draw.rounded_rectangle( # Power infront Bubble
                [((horizontal_small_padding+horizontal_padding)*render_factor, (bottom_guide_middle_y-guide_small_bubble_height/2)*render_factor), ((horizontal_small_padding+horizontal_padding+smallerBubbleWidth)*render_factor, (bottom_guide_middle_y+guide_small_bubble_height/2)*render_factor)],
                radius=(guide_small_bubble_height/2)*render_factor,
                fill=f"#{secondary_colour_hex}"
            )
        powerTextX = horizontal_small_padding+horizontal_padding+horizontal_large_padding
        sleepTextX = horizontal_small_padding+horizontal_padding+horizontal_large_padding+(powerTextWidth/render_factor)+horizontal_large_padding+horizontal_small_padding
        draw.text(( powerTextX*render_factor,in_smaller_bubble_text_y), powerText, font=inSmallerBubbleFont, fill=f"#{percentage_color(primary_colour_hex,secondary_colour_hex,0.593)}")
        draw.text(( sleepTextX*render_factor,in_bubble_text_y), sleepText, font=inBubbleFont, fill=f"#{secondary_colour_hex}")
    if not remove_right_menu_guides_var.get():
        circleWidth = guide_small_bubble_height
        confirmTextBbox = draw.textbbox((0, 0), confirmText, font=inBubbleFont)
        confirmTextWidth = confirmTextBbox[2] - confirmTextBbox[0]
        backTextBbox = draw.textbbox((0, 0), backText, font=inBubbleFont)
        backTextWidth = backTextBbox[2] - backTextBbox[0]
        launchTextBbox = draw.textbbox((0, 0), launchText, font=inBubbleFont)
        launchTextWidth = launchTextBbox[2] - launchTextBbox[0]
        aTextBbox = draw.textbbox((0, 0), aText, font=singleLetterFont)
        aTextWidth = aTextBbox[2] - aTextBbox[0]
        bTextBbox = draw.textbbox((0, 0), bText, font=singleLetterFont)
        bTextWidth = bTextBbox[2] - bTextBbox[0]

        RHM_Len = 0
        if muOSSystemName == "muxdevice" or muOSSystemName == "muxlaunch": # Just A and Confirm ( One Circle and confirmText plus padding )
            RHM_Len = horizontal_padding+circleWidth+horizontal_large_padding+(confirmTextWidth/render_factor)+horizontal_large_padding
        elif muOSSystemName == "muxconfig" or muOSSystemName == "muxinfo": # B and Back, A and Confirm ( Two Circle and confirmText and backText plus padding )
            RHM_Len = horizontal_padding+circleWidth+horizontal_large_padding+(backTextWidth/render_factor)+horizontal_large_padding+circleWidth+horizontal_large_padding+(confirmTextWidth/render_factor)+horizontal_large_padding
        elif muOSSystemName == "muxapp": # B and Back, A and Launch ( Two Circle and launchText and backText plus padding )
            RHM_Len = horizontal_padding+circleWidth+horizontal_large_padding+(backTextWidth/render_factor)+horizontal_large_padding+circleWidth+horizontal_large_padding+(launchTextWidth/render_factor)+horizontal_large_padding

        draw.rounded_rectangle( ## Left hand behind bubble
                [((deviceScreenWidth-horizontal_small_padding-RHM_Len)*render_factor, (bottom_guide_middle_y-menu_helper_guide_height/2)*render_factor), ((deviceScreenWidth-horizontal_small_padding)*render_factor, (bottom_guide_middle_y+menu_helper_guide_height/2)*render_factor)],
                radius=(menu_helper_guide_height/2)*render_factor,
                fill=f"#{percentage_color(primary_colour_hex,secondary_colour_hex,0.133)}"
            )
        if muOSSystemName != "muxapp": ## Draw Confirm
            aConfirmCircleCenterX = deviceScreenWidth-horizontal_small_padding-((circleWidth/2)+horizontal_large_padding+(confirmTextWidth/render_factor)+horizontal_large_padding)
            draw.ellipse(((aConfirmCircleCenterX-(circleWidth/2))*render_factor, (bottom_guide_middle_y-(circleWidth/2))*render_factor,(aConfirmCircleCenterX+(circleWidth/2))*render_factor, (bottom_guide_middle_y+(circleWidth/2))*render_factor),fill=f"#{secondary_colour_hex}") # A Bubble
            
            aConfirmTextX = aConfirmCircleCenterX - ((aTextWidth/2)/render_factor)
            confimTextX = deviceScreenWidth-horizontal_small_padding-((confirmTextWidth/render_factor)+horizontal_large_padding)
            draw.text(( aConfirmTextX*render_factor,single_letter_text_y), aText, font=singleLetterFont, fill=f"#{percentage_color(primary_colour_hex,secondary_colour_hex,0.593)}")
            draw.text(( confimTextX*render_factor,in_bubble_text_y), confirmText, font=inBubbleFont, fill=f"#{secondary_colour_hex}")
            
            if muOSSystemName == "muxconfig" or muOSSystemName == "muxinfo": # Draw Back
                bBackCircleCenterX = deviceScreenWidth-horizontal_small_padding-((circleWidth/2)+horizontal_large_padding+(backTextWidth/render_factor)+horizontal_large_padding+circleWidth+horizontal_large_padding+(confirmTextWidth/render_factor)+horizontal_large_padding)
                draw.ellipse(((bBackCircleCenterX-(circleWidth/2))*render_factor, (bottom_guide_middle_y-(circleWidth/2))*render_factor,(bBackCircleCenterX+(circleWidth/2))*render_factor, (bottom_guide_middle_y+(circleWidth/2))*render_factor),fill=f"#{secondary_colour_hex}") # B Bubble

                bBackTextX = bBackCircleCenterX - ((bTextWidth/2)/render_factor)
                backTextX = deviceScreenWidth-horizontal_small_padding-((backTextWidth/render_factor)+horizontal_large_padding+circleWidth+horizontal_large_padding+(confirmTextWidth/render_factor)+horizontal_large_padding)
                draw.text(( bBackTextX*render_factor,single_letter_text_y), bText, font=singleLetterFont, fill=f"#{percentage_color(primary_colour_hex,secondary_colour_hex,0.593)}")
                draw.text(( backTextX*render_factor,in_bubble_text_y), backText, font=inBubbleFont, fill=f"#{secondary_colour_hex}")

        else: # Draw Launch
            aLaunchCircleCenterX = deviceScreenWidth-horizontal_small_padding-((circleWidth/2)+horizontal_large_padding+(launchTextWidth/render_factor)+horizontal_large_padding)
            draw.ellipse(((aLaunchCircleCenterX-(circleWidth/2))*render_factor, (bottom_guide_middle_y-(circleWidth/2))*render_factor,(aLaunchCircleCenterX+(circleWidth/2))*render_factor, (bottom_guide_middle_y+(circleWidth/2))*render_factor),fill=f"#{secondary_colour_hex}") # A Bubble

            aLaunchTextX = aLaunchCircleCenterX - ((aTextWidth/2)/render_factor)
            launchTextX = deviceScreenWidth-horizontal_small_padding-((launchTextWidth/render_factor)+horizontal_large_padding)
            draw.text(( aLaunchTextX*render_factor,single_letter_text_y), aText, font=singleLetterFont, fill=f"#{percentage_color(primary_colour_hex,secondary_colour_hex,0.593)}")
            draw.text(( launchTextX*render_factor,in_bubble_text_y), launchText, font=inBubbleFont, fill=f"#{secondary_colour_hex}")

            bBackCircleCenterX = deviceScreenWidth-horizontal_small_padding-((circleWidth/2)+horizontal_large_padding+(backTextWidth/render_factor)+horizontal_large_padding+circleWidth+horizontal_large_padding+(launchTextWidth/render_factor)+horizontal_large_padding)
            draw.ellipse(((bBackCircleCenterX-(circleWidth/2))*render_factor, (bottom_guide_middle_y-(circleWidth/2))*render_factor,(bBackCircleCenterX+(circleWidth/2))*render_factor, (bottom_guide_middle_y+(circleWidth/2))*render_factor),fill=f"#{secondary_colour_hex}") # B Bubble

            bBackTextX = bBackCircleCenterX - ((bTextWidth/2)/render_factor)
            backTextX = deviceScreenWidth-horizontal_small_padding-((backTextWidth/render_factor)+horizontal_large_padding+circleWidth+horizontal_large_padding+(launchTextWidth/render_factor)+horizontal_large_padding)
            draw.text(( bBackTextX*render_factor,single_letter_text_y), bText, font=singleLetterFont, fill=f"#{percentage_color(primary_colour_hex,secondary_colour_hex,0.593)}")
            draw.text(( backTextX*render_factor,in_bubble_text_y), backText, font=inBubbleFont, fill=f"#{secondary_colour_hex}")
    return image


def generatePilImageVertical(progress_bar,workingIndex, muOSSystemName,listItems,additions,textPadding, rectanglePadding, ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor,scrollBarWidth = 0, showScrollBar=False,numScreens=0,screenIndex=0,fileCounter=""):
    progress_bar['value'] +=1
    #print(f"progress_bar Max = {progress_bar['maximum']} | progress_bar Value = {progress_bar['value']} | {100*(int(progress_bar['value'])/int(progress_bar['maximum']))}%")
    bg_rgb = hex_to_rgb(bg_hex)

    image = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), bg_rgb)

    if background_image != None:
        image.paste(background_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))

    topText = str(muOSSystemName)
    #if topText == "Folder":
    #    topText = None

    draw = ImageDraw.Draw(image)   

    boxArtDrawn = False
    boxArtWidth = 0
    if len(listItems) == 0:
        return(image)
    if not use_alt_font_var.get():
        selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    else:
        if os.path.exists(alt_font_path.get()):
            selected_font_path = alt_font_path.get()
        else:
            selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")

    
    if additions != "Blank" and version_var.get() == "muOS 2405 BEANS" and not remove_right_menu_guides_var.get(): ## muOS Beans shit
        in_smaller_bubble_font_size = 16*render_factor
        inSmallerBubbleFont = ImageFont.truetype(selected_font_path, in_smaller_bubble_font_size)

        in_bubble_font_size = 19*render_factor 
        inBubbleFont = ImageFont.truetype(selected_font_path, in_bubble_font_size)

        single_letter_font_size = 23*render_factor
        singleLetterFont = ImageFont.truetype(selected_font_path, single_letter_font_size)
        RHM_Len = 340
        if additions == "PowerHelpOkay":
            RHM_Len = 240

        draw.rounded_rectangle(
                [(5*render_factor, 430*render_factor), (150*render_factor, 475*render_factor)],
                radius=22.5*render_factor,
                fill=f"#{percentage_color(bg_hex,bubble_hex,0.133)}"
            )
        draw.rounded_rectangle(
                [((deviceScreenWidth-5-RHM_Len)*render_factor, 430*render_factor), ((deviceScreenWidth-5)*render_factor, 475*render_factor)],
                radius=22.5*render_factor,
                fill=f"#{percentage_color(bg_hex,bubble_hex,0.133)}"
            )
        draw.rounded_rectangle(
                [(11.5*render_factor, 436.5*render_factor), (83*render_factor, 468.5*render_factor)],
                radius=22.5*render_factor,
                fill=f"#{bubble_hex}"
            )
        if additions == "PowerHelpOkay":
            draw.rounded_rectangle(
                    [(402.5*render_factor, 436.5*render_factor), (466.5*render_factor, 468.5*render_factor)],
                    radius=22.5*render_factor,
                    fill=f"#{bubble_hex}"
                )
        else:
            draw.rounded_rectangle(
                    [(302.5*render_factor, 436.5*render_factor), (366.5*render_factor, 468.5*render_factor)],
                    radius=22.5*render_factor,
                    fill=f"#{bubble_hex}"
                )
        draw.ellipse((535*render_factor, 436.5*render_factor,567*render_factor, 468.5*render_factor),fill=f"#{bubble_hex}")
        draw.ellipse((430.6*render_factor, 436.5*render_factor,462.6*render_factor, 468.5*render_factor),fill=f"#{bubble_hex}")

        draw.text(( 20*render_factor,441*render_factor), "POWER", font=inSmallerBubbleFont, fill=f"#{percentage_color(bg_hex,bubble_hex,0.593)}")
        draw.text(( 88*render_factor,439*render_factor), "SLEEP", font=inBubbleFont, fill=f"#{bubble_hex}")
        
        if additions == "PowerHelpOkay":
            draw.text(( 411.5*render_factor,441*render_factor), "MENU", font=inSmallerBubbleFont, fill=f"#{percentage_color(bg_hex,bubble_hex,0.593)}")
            draw.text(( 473*render_factor,439*render_factor), "HELP", font=inBubbleFont, fill=f"#{bubble_hex}")
        else:
            draw.text(( 311.5*render_factor,441*render_factor), "MENU", font=inSmallerBubbleFont, fill=f"#{percentage_color(bg_hex,bubble_hex,0.593)}")
            draw.text(( 373*render_factor,439*render_factor), "HELP", font=inBubbleFont, fill=f"#{bubble_hex}")

            draw.text(( 439.8*render_factor,436.2*render_factor), "B", font=singleLetterFont, fill=f"#{percentage_color(bg_hex,bubble_hex,0.593)}")
            draw.text(( 471.6*render_factor,439*render_factor), "BACK", font=inBubbleFont, fill=f"#{bubble_hex}")

        
        draw.text(( 543.6*render_factor,435.5*render_factor), "A", font=singleLetterFont, fill=f"#{percentage_color(bg_hex,bubble_hex,0.593)}")
        draw.text(( 573*render_factor,439*render_factor), "OKAY", font=inBubbleFont, fill=f"#{bubble_hex}")
    elif (muOSSystemName == "muxdevice" or muOSSystemName == "muxlaunch" or muOSSystemName == "muxconfig" or muOSSystemName == "muxinfo" or muOSSystemName == "muxapp"):
        image = applyMenuHelperGuides(muOSSystemName,image,selected_font_path,bg_hex,bubble_hex,render_factor)
        
    elif show_file_counter_var.get() == 1:
        in_bubble_font_size = 19*render_factor
        inBubbleFont = ImageFont.truetype(selected_font_path, in_bubble_font_size)
        bbox = draw.textbbox((0, 0), fileCounter, font=inBubbleFont)
        text_width = bbox[2] - bbox[0]
        right_aligned_position = 620 * render_factor
        x = right_aligned_position - text_width
        y = 447 * render_factor
        draw.text(( x, y ), fileCounter, font=inBubbleFont, fill=f"#{bubble_hex}")    

    if topText != None and show_console_name_var.get():
        
        topTextFont = ImageFont.truetype(selected_font_path, 27*render_factor)

        bbox = draw.textbbox((0, 0), topText, font=topTextFont)
        text_width = bbox[2] - bbox[0]

        text_x = (deviceScreenWidth*render_factor - text_width) / 2

        draw.text(( text_x,0*render_factor), topText, font=topTextFont, fill=f"#{bubble_hex}")
    
    if muOSSystemName != "Folder" or not override_folder_box_art_padding_var.get():
        boxArtPadding = int(box_art_padding_entry.get()) * render_factor
    else:
        boxArtPadding = int(folder_box_art_padding_entry.get()) * render_factor

    textAlignment = None
    if muOSSystemName.startswith("mux"):
        if theme_alignment_var.get() == "Global":
            textAlignment = global_alignment_var.get()
        else:
            textAlignment = theme_alignment_var.get()
    else:
        if content_alignment_var.get() == "Global":
            textAlignment = global_alignment_var.get()
        else:
            textAlignment = content_alignment_var.get()

    if overlay_box_art_var.get() and textAlignment != "Centre":
        if listItems[workingIndex][1] == "File":
            if os.path.exists(os.path.join(box_art_directory_path.get(),muOSSystemName,"box",listItems[workingIndex][2]+".png")):
                originalBoxArtImage = Image.open(os.path.join(box_art_directory_path.get(),muOSSystemName,"box",listItems[workingIndex][2]+".png")).convert("RGBA")
                boxArtImage = originalBoxArtImage.resize((originalBoxArtImage.width*render_factor, originalBoxArtImage.height*render_factor), Image.LANCZOS)
                if textAlignment == "Left":
                    pasteLocation = (int((deviceScreenWidth*render_factor)-boxArtImage.width)-boxArtPadding,int(((deviceScreenHeight*render_factor)-boxArtImage.height)/2))
                else:
                    pasteLocation = (boxArtPadding,int(((deviceScreenHeight*render_factor)-boxArtImage.height)/2))
                
                boxArtWidth = originalBoxArtImage.width

                image.paste(boxArtImage,pasteLocation,boxArtImage)
                boxArtDrawn = True
        else:
            if os.path.exists(os.path.join(box_art_directory_path.get(),"Folder","box",listItems[workingIndex][2]+".png")):
                originalBoxArtImage = Image.open(os.path.join(box_art_directory_path.get(),"Folder","box",listItems[workingIndex][2]+".png")).convert("RGBA")
                boxArtImage = originalBoxArtImage.resize((originalBoxArtImage.width*render_factor, originalBoxArtImage.height*render_factor), Image.LANCZOS)
                
                pasteLocation = (int((deviceScreenWidth*render_factor)-boxArtImage.width)-boxArtPadding,int(((deviceScreenHeight*render_factor)-boxArtImage.height)/2))

                boxArtWidth = originalBoxArtImage.width


                image.paste(boxArtImage,pasteLocation,boxArtImage)
                boxArtDrawn = True

    font_size = (((deviceScreenHeight - footerHeight - headerHeight) * render_factor) / ItemsPerScreen) * textMF
    if override_font_size_var.get():
        try:
            font_size = int(custom_font_size_entry.get()) * render_factor
        except:
            font_size = (((deviceScreenHeight - footerHeight - headerHeight) * render_factor) / ItemsPerScreen) * textMF
    
    font = ImageFont.truetype(selected_font_path, font_size)

    availableHeight = ((deviceScreenHeight - headerHeight - footerHeight) * render_factor) / ItemsPerScreen
    for index, item in enumerate(listItems):
        noLettersCut = 0
        text_width = 2000*render_factor
        if alternate_menu_names_var.get() and muOSSystemName.startswith("mux"):
            text = bidiGet_display(menuNameMap.get(item[0][:].lower(),item[0][:]))
        else:
            text = item[0][:]
        text_color = f"#{selected_font_hex}" if index == workingIndex else f"#{deselected_font_hex}"
        if boxArtDrawn and override_bubble_cut_var.get():
            maxBubbleLength = maxBubbleLengthVar.get()
        elif boxArtDrawn:
            maxBubbleLength = deviceScreenWidth - boxArtWidth - boxArtPadding
        else:
            maxBubbleLength = deviceScreenWidth
        if workingIndex == index:
            totalCurrentLength = (textPadding * render_factor + text_width + rectanglePadding * render_factor)
        else:
            totalCurrentLength = (textPadding * render_factor + text_width)
        while totalCurrentLength > (int(maxBubbleLength)*render_factor):
            if alternate_menu_names_var.get() and muOSSystemName.startswith("mux"):
                text = bidiGet_display(menuNameMap.get(item[0][:].lower(),item[0][:]))
            else:
                text = item[0][:]

            if remove_brackets_var.get():
                text = remove_brackets_and_contents(text)
            if remove_square_brackets_var.get():
                text = remove_square_brackets_and_contents(text)
            if replace_hyphen_var.get():
                text = replace_hyphen_with_colon(text)
            if move_the_var.get():
                text = changeLocationOfThe(text)
            if noLettersCut>0:
                text = text[:-(noLettersCut+3)]
                text = text+"..."
            
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            if workingIndex == index:
                totalCurrentLength = (textPadding * render_factor + text_width + rectanglePadding * render_factor)
            else:
                totalCurrentLength = (textPadding * render_factor + text_width)
            noLettersCut +=1
            if text  == "...":
                raise ValueError("'Cut bubble off at' too low")
        
        if textAlignment == "Left":
            text_x = textPadding * render_factor
        elif textAlignment == "Right":
            text_x = (deviceScreenWidth-textPadding-text_width) * render_factor
        elif textAlignment == "Centre":
            text_x = ((deviceScreenWidth-text_width)/2) * render_factor
        #text_y = headerHeight * render_factor + availableHeight * index

        
        rectangle_x0 = text_x - (rectanglePadding * render_factor)
        rectangle_y0 = headerHeight * render_factor + availableHeight * index
        rectangle_x1 = rectangle_x0 + rectanglePadding * render_factor + text_width + rectanglePadding * render_factor
        rectangle_y1 = headerHeight * render_factor + availableHeight * (index+1)
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
    if showScrollBar:
        scrollBarHeight = (deviceScreenHeight - footerHeight - headerHeight) // numScreens
        rectangle_x0 = (deviceScreenWidth - scrollBarWidth) * render_factor
        rectangle_y0 = (headerHeight) * render_factor
        rectangle_x1 = (deviceScreenWidth) * render_factor
        rectangle_y1 = (deviceScreenHeight - footerHeight) * render_factor
        corner_radius = (scrollBarWidth // 2) * render_factor 

        draw.rounded_rectangle(
            [(rectangle_x0, rectangle_y0), (rectangle_x1, rectangle_y1)],
            radius=corner_radius,
            fill="darkgrey"
        )

        rectangle_x0 = (deviceScreenWidth - scrollBarWidth) * render_factor
        rectangle_y0 = (headerHeight + scrollBarHeight * screenIndex) * render_factor
        rectangle_x1 = (deviceScreenWidth) * render_factor
        rectangle_y1 = rectangle_y0 + scrollBarHeight * render_factor
        corner_radius = (scrollBarWidth // 2) * render_factor
        draw.rounded_rectangle(
            [(rectangle_x0, rectangle_y0), (rectangle_x1, rectangle_y1)],
            radius=corner_radius,
            fill=f"white"
        )
           
    return(image)


def ContinuousFolderImageGen(progress_bar,muOSSystemName, listItems, additions, scrollBarWidth, textPadding, rectanglePadding, ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, outputDir):
    totalItems = len(listItems)
    scrollBarHeight = (deviceScreenHeight - footerHeight - headerHeight)

    

    for workingIndex, workingItem in enumerate(listItems):
        
        if workingItem[1] == "Directory" or also_games_var.get() or workingItem[1] == "Menu" or workingItem[1] == "ThemePreview":

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
            image = generatePilImageVertical(progress_bar,focusIndex,muOSSystemName,listItems[startIndex:endIndex],additions,textPadding,rectanglePadding,ItemsPerScreen,bg_hex,selected_font_hex,deselected_font_hex,bubble_hex,render_factor,fileCounter=fileCounter)
                

            if muOSSystemName != "ThemePreview":
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
                    directory = os.path.dirname(f"{outputDir}/{muOSSystemName}/{workingItem[2]}.png")
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    image.save(f"{outputDir}/{muOSSystemName}/{workingItem[2]}.png")
            else:
                if workingIndex == 0:
                    image = image.resize((288, 216), Image.LANCZOS)
                    if workingItem[1] == "Menu":
                        image.save(os.path.join(internal_files_dir, "TempPreview.png"))


def PageFolderImageGen(progress_bar,muOSSystemName, listItems, additions, scrollBarWidth, textPadding, rectanglePadding, ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, outputDir):
    
    totalItems = len(listItems)
    numScreens = math.ceil(totalItems / ItemsPerScreen)
    

    bg_rgb = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))

    for screenIndex in range(numScreens):
        startIndex = screenIndex * ItemsPerScreen
        endIndex = min(startIndex + ItemsPerScreen, totalItems)

        for workingIndex in range(startIndex, endIndex):
            workingItem = listItems[workingIndex]
            if workingItem[1] == "Directory" or also_games_var.get() or workingItem[1] == "Menu" or workingItem[1] == "ThemePreview":
                showScrollBar = False
                if numScreens > 1:  # Display Scroll Bar
                    showScrollBar = True
                fileCounter = str(workingIndex + 1) + " / " + str(totalItems)
                image = generatePilImageVertical(progress_bar,workingIndex%ItemsPerScreen,muOSSystemName,listItems[startIndex:endIndex],additions,textPadding,rectanglePadding,ItemsPerScreen,bg_hex,selected_font_hex,deselected_font_hex,bubble_hex,render_factor,scrollBarWidth=scrollBarWidth,showScrollBar=showScrollBar,numScreens=numScreens,screenIndex=screenIndex,fileCounter=fileCounter)
                if muOSSystemName != "ThemePreview":
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
                        directory = os.path.dirname(f"{outputDir}/{muOSSystemName}/{workingItem[2]}.png")
                        if not os.path.exists(directory):
                            os.makedirs(directory)
                        image.save(f"{outputDir}/{muOSSystemName}/{workingItem[2]}.png")
                else:
                    if workingIndex == 0:
                        image = image.resize((288, 216), Image.LANCZOS)
                        if workingItem[1] == "Menu":
                            image.save(os.path.join(internal_files_dir, "TempPreview.png"))

def generatePilImageHorizontal(progress_bar,workingIndex, bg_hex, selected_font_hex,deselected_font_hex, bubble_hex,icon_hex,render_factor):
    progress_bar['value']+=1
    #print(f"progress_bar Max = {progress_bar['maximum']} | progress_bar Value = {progress_bar['value']} | {100*(int(progress_bar['value'])/int(progress_bar['maximum']))}%")
    bg_rgb = hex_to_rgb(bg_hex)

    # Create image
    image = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), bg_rgb)
    if background_image != None:
        image.paste(background_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))

    

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

    if not use_alt_font_var.get():
        selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    else:
        if os.path.exists(alt_font_path.get()):
            selected_font_path = alt_font_path.get()
        else:
            selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    image = applyMenuHelperGuides("muxlaunch",image,selected_font_path,bg_hex,bubble_hex,render_factor)
        
    

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
    
    if alternate_menu_names_var.get():
        textString = bidiGet_display(menuNameMap.get("content explorer", "Content"))
    else:
        textString = "Content"
    text_bbox = draw.textbbox((0, 0), textString, font=font)
    text_width = (text_bbox[2] - text_bbox[0])
    ascent, descent = font.getmetrics()
    text_height = ascent + descent

    text_y = top_row_bubble_middle - (text_height / 2)


    bubble_center_x =  explore_middle
    textColour = selected_font_hex if workingIndex == 0 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
    if workingIndex == 0 :
        bubbleLength = text_width+horizontalBubblePadding
        draw.rounded_rectangle(
            [((current_x_midpoint-(bubbleLength/2)), int(top_row_bubble_middle-bubble_height/2)), ((current_x_midpoint+(bubbleLength/2)), int(top_row_bubble_middle+bubble_height/2))],
            radius=(bubble_height/2),
            fill=f"#{bubble_hex}"
        )
    draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    if alternate_menu_names_var.get():
        textString = bidiGet_display(menuNameMap.get("favourites", "Favourites"))
    else:
        textString = "Favourites"
    text_bbox = draw.textbbox((0, 0), textString, font=font)
    text_width = (text_bbox[2] - text_bbox[0])
    bubble_center_x =  favourite_middle
    textColour = selected_font_hex if workingIndex == 1 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
    if workingIndex == 1 :
        bubbleLength = text_width+horizontalBubblePadding
        draw.rounded_rectangle(
            [((current_x_midpoint-(bubbleLength/2)), int(top_row_bubble_middle-bubble_height/2)), ((current_x_midpoint+(bubbleLength/2)), int(top_row_bubble_middle+bubble_height/2))],
            radius=(bubble_height/2),
            fill=f"#{bubble_hex}"
        )
    draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    if alternate_menu_names_var.get():
        textString = bidiGet_display(menuNameMap.get("history", "History"))
    else:
        textString = "History"
    text_bbox = draw.textbbox((0, 0), textString, font=font)
    text_width = (text_bbox[2] - text_bbox[0])
    bubble_center_x =  history_middle
    textColour = selected_font_hex if workingIndex == 2 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
    if workingIndex == 2 :
        bubbleLength = text_width+horizontalBubblePadding
        draw.rounded_rectangle(
            [((current_x_midpoint-(bubbleLength/2)), int((top_row_bubble_middle-bubble_height/2))), ((current_x_midpoint+(bubbleLength/2)), int((top_row_bubble_middle+bubble_height/2)))],
            radius=(bubble_height/2),
            fill=f"#{bubble_hex}"
        )
    draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")
    if alternate_menu_names_var.get():
        textString = bidiGet_display(menuNameMap.get("applications", "Utilities"))
    else:
        textString = "Utilities"
    text_bbox = draw.textbbox((0, 0), textString, font=font)
    text_width = (text_bbox[2] - text_bbox[0])
    bubble_center_x =  apps_middle
    textColour = selected_font_hex if workingIndex == 3 else deselected_font_hex
    text_x = bubble_center_x - (text_width / 2)
    if workingIndex == 3 :
        bubbleLength = text_width+horizontalBubblePadding
        draw.rounded_rectangle(
            [((current_x_midpoint-(bubbleLength/2)), int((top_row_bubble_middle-bubble_height/2))), ((current_x_midpoint+(bubbleLength/2)), int((top_row_bubble_middle+bubble_height/2)))],
            radius=(bubble_height/2),
            fill=f"#{bubble_hex}"
        )
    draw.text((text_x, text_y), textString, font=font, fill=f"#{textColour}")

    

    if workingIndex == 4:
        infoLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "info.png"),selected_font_hex)
    else:
        infoLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "info.png"),icon_hex)
    if workingIndex == 5:
        configLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "config.png"),selected_font_hex)
    else:
        configLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "config.png"),icon_hex)
    if workingIndex == 6:
        rebootLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "reboot.png"),selected_font_hex)
    else:
        rebootLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "reboot.png"),icon_hex)
    if workingIndex == 7:
        shutdownLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "shutdown.png"),selected_font_hex)
    else:
        shutdownLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "Horizontal Logos", "shutdown.png"),icon_hex)
    
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
        draw.ellipse((int(center_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(center_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
    elif workingIndex == 5:
        center_x = config_middle
        draw.ellipse((int(center_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(center_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
    elif workingIndex == 6:
        center_x = reboot_middle
        draw.ellipse((int(center_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(center_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")
    elif workingIndex == 7:
        center_x = shutdown_middle
        draw.ellipse((int(center_x-circle_radius),int(bottom_row_middle_y-circle_radius),int(center_x+circle_radius),int(bottom_row_middle_y+circle_radius)),fill=f"#{bubble_hex}")

    info_logo_y = int(bottom_row_middle_y-(infoLogoColoured.size[1]/2))
    config_logo_y = int(bottom_row_middle_y-(configLogoColoured.size[1]/2))
    reboot_logo_y = int(bottom_row_middle_y-(rebootLogoColoured.size[1]/2))
    shutdown_logo_y = int(bottom_row_middle_y-(shutdownLogoColoured.size[1]/2))

    image.paste(infoLogoColoured,(info_logo_x,info_logo_y),infoLogoColoured)
    image.paste(configLogoColoured,(config_logo_x,config_logo_y),configLogoColoured)
    image.paste(rebootLogoColoured,(reboot_logo_x,reboot_logo_y),rebootLogoColoured)
    image.paste(shutdownLogoColoured,(shutdown_logo_x,shutdown_logo_y),shutdownLogoColoured)
    
    return(image)

def generatePilImageBootLogo(bg_hex,selected_font_hex,deselected_font_hex,bubble_hex,render_factor):
    bg_rgb = hex_to_rgb(bg_hex)
    image = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), bg_rgb)
    if background_image != None:
        image.paste(background_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))

    draw = ImageDraw.Draw(image)

    if not use_alt_font_var.get():
        selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    else:
        if os.path.exists(alt_font_path.get()):
            selected_font_path = alt_font_path.get()
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
    
    draw.rounded_rectangle(
        [(bubble_x_mid_point-(bubble_width/2), screen_y_middle-(bubble_height/2)), (bubble_x_mid_point+(bubble_width/2), screen_y_middle+(bubble_height/2))],
        radius=bubble_height/2,
        fill=f"#{bubble_hex}"
    )

    draw.text((mu_x_location,mu_y_location), muText,font=mu_font, fill=f"#{deselected_font_hex}")
    draw.text((os_x_location,os_y_location),osText,font=os_font,fill=f"#{selected_font_hex}")
    

    return image

def generatePilImageChargeScreen(bg_hex,deselected_font_hex,icon_hex,render_factor):
    bg_rgb = hex_to_rgb(bg_hex)
    image = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), bg_rgb)
    if background_image != None:
        image.paste(background_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))
    
    draw = ImageDraw.Draw(image)

    if not use_alt_font_var.get():
        selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    else:
        if os.path.exists(alt_font_path.get()):
            selected_font_path = alt_font_path.get()
        else:
            selected_font_path = os.path.join(internal_files_dir, "Assets", "Font", "BPreplayBold-unhinted.otf")
    
    screen_x_middle, screen_y_middle = int((deviceScreenWidth/2)*render_factor),int((deviceScreenHeight/2)*render_factor)

    from_middle_padding = 50*render_factor

    chargingLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "ChargingLogo[5x].png"),icon_hex)
    chargingLogoColoured = chargingLogoColoured.resize((int((chargingLogoColoured.size[0]/5)*render_factor),int((chargingLogoColoured.size[1]/5)*render_factor)), Image.LANCZOS)
    
    charging_logo_y_location = int(screen_y_middle-chargingLogoColoured.size[1]/2-from_middle_padding)
    charging_logo_x_location = int(screen_x_middle-chargingLogoColoured.size[0]/2)

    image.paste(chargingLogoColoured,(charging_logo_x_location,charging_logo_y_location),chargingLogoColoured)

    charging_font_size = int(57.6 * render_factor)
    charging_font = ImageFont.truetype(selected_font_path, charging_font_size)

    chargingText = "CHARGING..."
    if alternate_menu_names_var.get():
        chargingText = bidiGet_display(menuNameMap.get("charging...", "CHARGING..."))

    

    chargingTextBbox = charging_font.getbbox(chargingText)

    chargingTextWidth = int(chargingTextBbox[2] - chargingTextBbox[0])
    chargingTextHeight = int(chargingTextBbox[3]-chargingTextBbox[1])
    charging_y_location = int(screen_y_middle-chargingTextHeight/2-chargingTextBbox[1]+from_middle_padding)
    charging_x_location = int(screen_x_middle - chargingTextWidth/2)

    draw.text((charging_x_location,charging_y_location), chargingText, font=charging_font, fill=f"#{deselected_font_hex}")

    
    return (image)

def generatePilImageLoadingScreen(bg_hex,icon_hex,render_factor):
    bg_rgb = hex_to_rgb(bg_hex)
    image = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), bg_rgb)
    if background_image != None:
        image.paste(background_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))
    
    draw = ImageDraw.Draw(image)
    
    screen_x_middle, screen_y_middle = (deviceScreenWidth/2)*render_factor,(deviceScreenHeight/2)*render_factor

    loadingLogoColoured = change_logo_color(os.path.join(internal_files_dir, "Assets", "LoadingLogo[5x].png"),icon_hex)
    loadingLogoColoured = loadingLogoColoured.resize((int((loadingLogoColoured.size[0]/5)*render_factor),int((loadingLogoColoured.size[1]/5)*render_factor)), Image.LANCZOS)
    
    loading_logo_y_location = int(screen_y_middle-loadingLogoColoured.size[1]/2)
    loading_logo_x_location = int(screen_x_middle-loadingLogoColoured.size[0]/2)

    image.paste(loadingLogoColoured,(loading_logo_x_location,loading_logo_y_location),loadingLogoColoured)
    return (image)

def generatePilImageDefaultScreen(bg_hex,render_factor):
    bg_rgb = hex_to_rgb(bg_hex)
    image = Image.new("RGBA", (deviceScreenWidth * render_factor, deviceScreenHeight * render_factor), bg_rgb)
    if background_image != None:
        image.paste(background_image.resize((deviceScreenWidth * render_factor, deviceScreenHeight * render_factor)), (0,0))
    return (image)

def HorizontalMenuGen(progress_bar,muOSSystemName, listItems, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex,icon_hex, render_factor, outputDir):
    startIndex = 0
    endIndex = 8
    for workingIndex in range(startIndex, endIndex):
        workingItem = listItems[workingIndex]
        #image.save(os.path.join(script_dir,"Images for testing horizontal",f"{workingIndex}.png"))
        image = generatePilImageHorizontal(progress_bar,workingIndex,bg_hex, selected_font_hex,deselected_font_hex,bubble_hex,icon_hex,render_factor)

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
            image = image.resize((288, 216), Image.LANCZOS)
            if workingItem[1] == "Menu":
                image.save(os.path.join(internal_files_dir, "TempPreview.png"))

def remove_brackets_and_contents(text):
    # Remove contents within parentheses ()
    text = re.sub(r'\([^)]*\)', '', text)
    # Remove extra whitespace left by removal
    text = re.sub(r'\s+', ' ', text).strip()
    return text
def remove_square_brackets_and_contents(text):
    # Remove contents within square brackets []
    text = re.sub(r'\[[^\]]*\]', '', text)
    # Remove extra whitespace left by removal
    text = re.sub(r'\s+', ' ', text).strip()
    return text



def changeLocationOfThe(name):
    # Check if the name contains ', The'
    if ', The' in name:
        # Split the name into parts
        name = name.replace(', The', '')
        # Rearrange the parts with 'The ' at the beginning
        formatted_name = 'The ' + name
    else:
        formatted_name = name
    return formatted_name

def replace_hyphen_with_colon(text):
    return text.replace(' - ', ': ')

def getNameConvertionList(file_path):
    if os.path.exists(name_json_path.get()):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data
        except:
            return []
    return []

def getConsoleAssociationList():
    if os.path.exists(defaultConsoleAssociationsPath) and not os.path.exists(ConsoleAssociationsPath):
        shutil.copy(defaultConsoleAssociationsPath, ConsoleAssociationsPath)
    if os.path.exists(ConsoleAssociationsPath):
        try:
            with open(ConsoleAssociationsPath, 'r') as file:
                data = json.load(file)
            data = {key.lower(): value for key, value in data.items()}
            return data
        except:
            return []
    return []

def saveConsoleAssociationDict():
    with open(ConsoleAssociationsPath, 'w', newline='\n',encoding='utf-8') as json_file:
        json.dump(consoleMap, json_file, indent=2)         

def getAlternateMenuNameDict():
    if os.path.exists(AlternateMenuNamesPath):
        try:
            with open(AlternateMenuNamesPath, 'r', encoding='utf-8') as file:
                data = json.load(file)
            data = {key.lower(): value for key, value in data.items()}
            return data
        except:
            return getDefaultAlternateMenuNameData()
    return getDefaultAlternateMenuNameData()

def getDefaultAlternateMenuNameData():
    defaultMenuNamemap = {}
    for section in menus2405_2:
        if section[0].startswith("mux"):
            for n in section[1]:
                defaultMenuNamemap[n[0].lower()] = n[0]
    
    defaultMenuNamemap["content explorer"] = "Games"
    defaultMenuNamemap["applications"] = "Utilites"
    defaultMenuNamemap["power"] = "POWER"
    defaultMenuNamemap["sleep"] = "SLEEP"
    defaultMenuNamemap["menu"] = "MENU"
    defaultMenuNamemap["help"] = "HELP"
    defaultMenuNamemap["back"] = "BACK"
    defaultMenuNamemap["okay"] = "OKAY"
    defaultMenuNamemap["confirm"] = "CONFIRM"
    defaultMenuNamemap["launch"] = "LAUNCH"
    defaultMenuNamemap["charging..."] = "CHARGING..."
    return defaultMenuNamemap

def list_directory_contents(directory_path):
    names_data = getNameConvertionList(name_json_path.get())
    fileItemList = []
    directoryItemList = []
    itemList = []
    try:
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            item_name, item_extension = os.path.splitext(item)
            item_type = "Directory" if os.path.isdir(item_path) else "File"
            if item_type == "Directory":
                if not(item_name[0] == "." or item_name[0] == "_") or show_hidden_files_var.get():
                    directoryItemList.append([item_name, item_type,item_name])
            else:
                if not(item_extension.lower() == ".pcm" or item_extension.lower() == ".msu" or item_extension.lower() == ".ips") and (not(item_name[0] == "." or item_name[0] == "_") or show_hidden_files_var.get()):
                    sort_name = names_data[item_name.lower()] if item_name.lower() in names_data else item_name+item_extension
                    display_name = names_data[item_name.lower()] if item_name.lower() in names_data else item_name
                    fileItemList.append([item_name, item_type, display_name, sort_name])
        if len(directoryItemList)+len(fileItemList):
            directoryItemList.sort(key=lambda x: x[0].lower())
            fileItemList.sort(key=lambda x: (x[3].lower()))

            for n in directoryItemList:
                itemList.append(n) # Display Name, File Type, File Name
            for n in fileItemList:
                itemList.append([n[2], n[1],n[0]])  # Display Name, File Type, File Name
            return itemList
        else:
            return []
    except Exception as e:
        if advanced_error_var.get():
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            return f"ERROR: {e}\n{tb_str}"
        else:
            return f"ERROR: {e}"


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

def remove_image_files_in_directory(directory):
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.splitext(file)[1].lower() in image_extensions:
                os.remove(file_path)

def get_console_name(file_path, directory_path):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith(directory_path + ':='):
                return line.split('=')[1].strip()
    return None

def count_files_and_folders(directory):
    try:
        total_count = 0

        # Recursively walk through the directory
        for root, dirs, files in os.walk(directory):
            if not show_hidden_files_var.get():
                dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]
                files = [f for f in files if not f.startswith('.') and not f.startswith('_')]
            #print(f"show hidden files: {show_hidden_files_var.get()} | Len dirs {len(dirs)} | Len files {len(files)}")
            total_count += len(dirs) + len(files)


        return total_count

    except FileNotFoundError:
        return "Directory not found."
    except PermissionError:
        return "Permission denied."
    except Exception as e:
        return f"An error occurred: {e}"

def count_folders(directory):
    try:
        total_count = 0

        # Recursively walk through the directory
        for root, dirs, files in os.walk(directory):
            if not show_hidden_files_var.get():
                dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('_')]
                files = [f for f in files if not f.startswith('.') and not f.startswith('_')]
            if len(files)==0:
                total_count += len(dirs)


        return total_count

    except FileNotFoundError:
        return "Directory not found."
    except PermissionError:
        return "Permission denied."
    except Exception as e:
        return f"An error occurred: {e}"

def traverse_and_generate_images(progress_bar, directory_path, additions, scrollBarWidth, textPadding, rectanglePadding, ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, outputDirectory, input_queue, output_queue):
    items = list_directory_contents(directory_path)
    fileFound = False
    
    for item in items:
        if item[1] == "File":
            fileFound = True
    consoleName = "Folder"
    if fileFound and also_games_var.get() == 1: 
        folderName = os.path.basename(directory_path).lower()
        consoleName = consoleMap.get(folderName, None)
        if consoleName is None:
            input_queue.put(directory_path)
            consoleName = output_queue.get()
            consoleMap[folderName] = consoleName
            saveConsoleAssociationDict()

    if len(items) > 0 and consoleName != "SKIP":
        if not (fileFound and also_games_var.get() == 0):
            if page_by_page_var.get():
                PageFolderImageGen(progress_bar,consoleName, items, additions, scrollBarWidth, textPadding, rectanglePadding, ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, outputDirectory)
            else:
                ContinuousFolderImageGen(progress_bar, consoleName, items, additions, scrollBarWidth, textPadding, rectanglePadding, ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, outputDirectory)

    for item in items:
        item_name = item[0]
        item_type = item[1]
        if item_type == "Directory":
            new_path = os.path.join(directory_path, item_name)
            traverse_and_generate_images(progress_bar, new_path, additions, scrollBarWidth, textPadding, rectanglePadding, ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, outputDirectory, input_queue, output_queue)

def select_console(directory_path):
    def on_select():
        selected_console.set(listbox.get(listbox.curselection()))
        root.quit()
    def on_skip():
        selected_console.set("SKIP")
        root.quit()

    root = tk.Tk()
    root.geometry("800x400") 
    root.title("Select Console")
    consoleOptions = ['Amstrad', 'Arcade', 'Arduboy', 'Atari 2600', 'Atari 5200',
            'Atari 7800', 'Atari Jaguar', 'Atari Lynx', 'Atari ST-STE-TT-Falcon', 'Bandai WonderSwan-Color', 
            'Cannonball', 'Cave Story', 'ChaiLove', 'ColecoVision', 'Commodore Amiga', 
            'Commodore C128', 'Commodore C64', 'Commodore CBM-II', 'Commodore PET', 'Commodore VIC-20', 
            'Dinothawr', 'Doom', 'DOS', 'External - Ports', 'Fairchild ChannelF', 
            'Flashback', 'Folder', 'Game Music Emu', 'GCE-Vectrex', 'Handheld Electronic - Game and Watch', 
            'Lowres NX', 'Mattel - Intellivision', 'Microsoft - MSX', 'Mr', 'MSX-SVI-ColecoVision-SG1000', 
            'NEC PC Engine', 'NEC PC Engine SuperGrafx', 'NEC PC-8000 - PC-8800 series', 'NEC PC-FX', 'NEC PC98', 
            'Nintendo DS', 'Nintendo Game Boy', 'Nintendo Game Boy Advance', 'Nintendo Game Boy Color', 'Nintendo N64', 
            'Nintendo NES-Famicom', 'Nintendo Pokemon Mini', 'Nintendo SNES-SFC', 'Nintendo Virtual Boy', 'Palm OS', 
            'Philips CDi', 'PICO-8', 'Quake', 'Rick Dangerous', 'RPG Maker 2000 - 2003', 
            'ScummVM', 'Sega 32X', 'Sega Atomiswave Naomi', 'Sega Dreamcast', 'Sega Game Gear', 
            'Sega Master System', 'Sega Mega CD - Sega CD', 'Sega Mega Drive - Genesis', 'Sega Saturn', 'Sharp X1', 
            'Sharp X68000', 'Sinclair ZX 81', 'Sinclair ZX Spectrum', 'SNK Neo Geo', 'SNK Neo Geo CD', 
            'SNK Neo Geo Pocket - Color', 'Sony PlayStation', 'Sony Playstation Portable', 'Texas Instruments TI-83', 'TIC-80', 
            'Uzebox', 'VeMUlator', 'Video Player', 'WASM-4', 'Watara Supervision', 'Wolfenstein 3D']

    label = tk.Label(root, text=f"What console on muOS is this folder associated with: [{os.path.basename(directory_path)}]?")
    label.pack(pady=10)

    frame = tk.Frame(root)
    frame.pack(pady=10, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
    listbox = tk.Listbox(frame, selectmode=tk.SINGLE, yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    listbox.grid(row=0, column=0, sticky='nsew')
    scrollbar.grid(row=0, column=1, sticky='ns')

    for option in consoleOptions:
        listbox.insert(tk.END, option)

    selected_console = tk.StringVar()

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    skip_button = tk.Button(button_frame, text="SKIP", command=on_skip)
    skip_button.pack(side=tk.LEFT, padx=(0, 20))
    
    ok_button = tk.Button(button_frame, text="SELECT", command=on_select)
    ok_button.pack(side=tk.LEFT)
    
    root.mainloop()
    root.destroy()
    return selected_console.get()

def select_input_directory():
    roms_directory_path.set(filedialog.askdirectory())

def select_application_directory():
    application_directory_path.set(filedialog.askdirectory())

def select_box_art_directory():
    box_art_directory_path.set(filedialog.askdirectory())

def select_output_directory():
    catalogue_directory_path.set(filedialog.askdirectory())

def select_theme_directory():
    theme_directory_path.set(filedialog.askdirectory())
def select_am_theme_directory():
    am_theme_directory_path.set(filedialog.askdirectory())
def select_name_json_path():
    # File dialog to select a file, with specific types of files allowed
    file_path = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json")],  # Only show .ini files
        title="Select name.json file"
    )
    
    # Check if the selected file is name.ini
    if file_path.endswith("name.json"):
        name_json_path.set(file_path)
    else:
        # Optionally show a warning or take other action if the wrong file is selected
        tk.messagebox.showerror("Invalid file", "Please select a file named 'name.json'")
def select_background_image_path():
    # File dialog to select a file, with specific types of files allowed
    file_path = filedialog.askopenfilename(
        filetypes=[("PNG Files", "*.png")],  # Only show .ini files
        title="Select background image file"
    )
    background_image_path.set(file_path)

def select_alt_font_path():
    # File dialog to select a file, with specific types of files allowed
    file_path = filedialog.askopenfilename(
        filetypes=[("Font Files", "*.ttf"), ("Font Files", "*.otf")],  # Only show font files
        title="Select font file"
    )
    alt_font_path.set(file_path)


def remove_images():
    try:
        if catalogue_directory_path.get() != "":
            # Ask for confirmation before proceeding
            question = f"Are you sure you want to remove all images in this directory?\n{catalogue_directory_path.get()}"
            confirm = messagebox.askyesno("Confirmation", question)
            if confirm:
                remove_image_files_in_directory(catalogue_directory_path.get())
                messagebox.showinfo("Success", "Images successfully deleted.")
        else:
            raise ValueError("You Haven't Selected a Catalogue Folder")
    except Exception as e:
        if advanced_error_var.get():
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            messagebox.showerror("Error", f"An unexpected error occurred: {e}\n{tb_str}")
        else:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        


def generate_images(progress_bar, loading_window, input_queue, output_queue):
    try:
        input_directory = roms_directory_path.get()
        output_directory = catalogue_directory_path.get()

        if not input_directory or not output_directory:
            raise ValueError("Input and output directory paths cannot be empty.")

        if not os.path.isdir(input_directory):
            raise ValueError(f"Invalid input directory: {input_directory}")
        
        progress_bar['value'] = 0
        progress_bar_max =0
        if also_games_var.get():
            totalRoms = count_files_and_folders(input_directory)
            progress_bar_max += totalRoms
        else:
            totalDirectories = count_folders(input_directory)
            progress_bar_max += totalDirectories
        progress_bar['maximum'] = progress_bar_max

        scrollBarWidth = int(scroll_bar_width_entry.get())
        textPadding = int(text_padding_entry.get())
        rectanglePadding = int(rectangle_padding_entry.get())
        bg_hex = background_hex_entry.get()
        selected_font_hex = selected_font_hex_entry.get()
        deselected_font_hex = deselected_font_hex_entry.get()
        bubble_hex = bubble_hex_entry.get()
        ItemsPerScreen = int(items_per_screen_entry.get())
        
        traverse_and_generate_images(progress_bar,input_directory, additions_Blank, scrollBarWidth, textPadding, rectanglePadding, ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor,  output_directory,input_queue,output_queue)
        messagebox.showinfo("Success", "Images generated successfully.\nMake sure your box art setting is set to Fullscreen+Front!")
        loading_window.destroy()
    except ValueError as ve:
        loading_window.destroy()
        messagebox.showerror("Error", str(ve))

    except Exception as e:
        loading_window.destroy()
        if advanced_error_var.get():
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            messagebox.showerror("Error", f"An unexpected error occurred: {e}\n{tb_str}")
        else:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

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
                     ["Shutdown Device","shutdown"]]],
         ["ThemePreview",[["Content Explorer","explore"],
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
                     ["Shutdown Device","shutdown"]]],
         ["ThemePreview",[["Content Explorer","explore"],
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
                     ["Shutdown Device","shutdown"]]],
         ["ThemePreview",[["Content Explorer","explore"],
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
        if advanced_error_var.get():
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            messagebox.showerror("Error", f"An unexpected error occurred: {e}\n{tb_str}")
        else:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

# Example usage:
# replace_in_file('path/to/your/file.txt', 'old_string', 'new_string')
def hex_to_rgb(hex_color):
    # Convert hex to RGB
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

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

def generate_theme(progress_bar, loading_window):
    try:

        progress_bar['value'] = 0
        if vertical_var.get():
            progress_bar['maximum'] = 36
        else:
            progress_bar['maximum'] = 28


        themeName = theme_name_entry.get()
        FillTempThemeFolder(progress_bar)
        if theme_directory_path.get() == "":
            theme_dir = os.path.join(script_dir, "Generated Theme")
        else:
            theme_dir = theme_directory_path.get()

        preview_dir = os.path.join(theme_dir,"preview")

        os.makedirs(preview_dir,exist_ok=True)

        shutil.make_archive(os.path.join(theme_dir, themeName),"zip", os.path.join(internal_files_dir, ".TempBuildTheme"))

        temp_preview_path = os.path.join(preview_dir, "TempPreview.png")
        if os.path.exists(temp_preview_path):
            os.remove(temp_preview_path)
        shutil.move(os.path.join(internal_files_dir, "TempPreview.png"), preview_dir)

        theme_preview_path = os.path.join(preview_dir, f"{themeName}.png")
        if os.path.exists(theme_preview_path):
            os.remove(theme_preview_path)

        os.rename(os.path.join(preview_dir,"TempPreview.png"), theme_preview_path)


        

        delete_folder(os.path.join(internal_files_dir, ".TempBuildTheme"))
        if os.path.exists(os.path.join(internal_files_dir, "TempPreview.png")):
            os.remove(os.path.join(internal_files_dir, "TempPreview.png"))
        if os.path.exists(os.path.join(theme_dir, "preview","TempPreview.png")):
            os.remove(os.path.join(theme_dir, "preview","TempPreview.png"))
        messagebox.showinfo("Success", "Theme generated successfully.")
        loading_window.destroy()
    except Exception as e:
        loading_window.destroy()
        if theme_directory_path.get() == "":
            theme_dir = os.path.join(script_dir, "Generated Theme")
        else:
            theme_dir = theme_directory_path.get()
        if advanced_error_var.get():
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            messagebox.showerror("Error", f"An unexpected error occurred: {e}\n{tb_str}")
        else:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        delete_folder(os.path.join(internal_files_dir, ".TempBuildTheme"))
        if os.path.exists(os.path.join(internal_files_dir, "TempPreview.png")):
            os.remove(os.path.join(internal_files_dir, "TempPreview.png"))
        if os.path.exists(os.path.join(theme_dir, "preview","TempPreview.png")):
            os.remove(os.path.join(theme_dir, "preview","TempPreview.png"))

def FillTempThemeFolder(progress_bar):
    scrollBarWidth = int(scroll_bar_width_entry.get())
    textPadding = int(text_padding_entry.get())
    rectanglePadding = int(rectangle_padding_entry.get())
    ItemsPerScreen = int(items_per_screen_entry.get())
    bg_hex = background_hex_entry.get()
    selected_font_hex = selected_font_hex_entry.get()
    deselected_font_hex = deselected_font_hex_entry.get()
    bubble_hex = bubble_hex_entry.get()
    icon_hex = icon_hex_entry.get()
    
    copy_contents(os.path.join(internal_files_dir, "Theme Shell"), os.path.join(internal_files_dir, ".TempBuildTheme"))
    
    dst_dir = os.path.join(internal_files_dir,".TempBuildTheme","scheme")
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copy2(os.path.join(internal_files_dir,"Template Scheme","default.txt"),dst_dir)
    replace_in_file(os.path.join(internal_files_dir,".TempBuildTheme","scheme","default.txt"), "{bg_hex}", str(bg_hex))
    replace_in_file(os.path.join(internal_files_dir,".TempBuildTheme","scheme","default.txt"), "{selected_font_hex}", str(bubble_hex))
    replace_in_file(os.path.join(internal_files_dir,".TempBuildTheme","scheme","default.txt"), "{deselected_font_hex}", str(percentage_color(bubble_hex,selected_font_hex,0.5)))
    replace_in_file(os.path.join(internal_files_dir,".TempBuildTheme","scheme","default.txt"), "{disabled_font_hex}", str(percentage_color(bg_hex,bubble_hex,0.25)))
    replace_in_file(os.path.join(internal_files_dir,".TempBuildTheme","scheme","default.txt"), "{ImageOverlay}", str(crt_overlay_var.get()))
    
    shutil.copy2(os.path.join(internal_files_dir,"Template Scheme","mux.txt"),os.path.join(internal_files_dir,".TempBuildTheme","scheme","tempmux.txt"))
    replace_in_file(os.path.join(internal_files_dir,".TempBuildTheme","scheme","tempmux.txt"), "{bg_hex}", str(bg_hex))
    replace_in_file(os.path.join(internal_files_dir,".TempBuildTheme","scheme","tempmux.txt"), "{selected_font_hex}", str(bubble_hex))
    replace_in_file(os.path.join(internal_files_dir,".TempBuildTheme","scheme","tempmux.txt"), "{deselected_font_hex}", str(percentage_color(bubble_hex,bg_hex,0.5)))
    replace_in_file(os.path.join(internal_files_dir,".TempBuildTheme","scheme","tempmux.txt"), "{disabled_font_hex}", str(percentage_color(bg_hex,bubble_hex,0.25)))
    replace_in_file(os.path.join(internal_files_dir,".TempBuildTheme","scheme","tempmux.txt"), "{ImageOverlay}", str(crt_overlay_var.get()))


    shutil.copy2(os.path.join(internal_files_dir,".TempBuildTheme","scheme","tempmux.txt"),os.path.join(internal_files_dir,".TempBuildTheme","scheme","muxlaunch.txt"))
    replace_in_file(os.path.join(internal_files_dir,".TempBuildTheme","scheme","tempmux.txt"),"{ScrollDirection}", "0")
    if version_var.get() == "muOS 2405 BEANS":
        shutil.copy2(os.path.join(internal_files_dir,".TempBuildTheme","scheme","tempmux.txt"),os.path.join(internal_files_dir,".TempBuildTheme","scheme","muxapps.txt"))
    else:
        shutil.copy2(os.path.join(internal_files_dir,".TempBuildTheme","scheme","tempmux.txt"),os.path.join(internal_files_dir,".TempBuildTheme","scheme","muxapp.txt"))
    shutil.copy2(os.path.join(internal_files_dir,".TempBuildTheme","scheme","tempmux.txt"),os.path.join(internal_files_dir,".TempBuildTheme","scheme","muxconfig.txt"))
    shutil.copy2(os.path.join(internal_files_dir,".TempBuildTheme","scheme","tempmux.txt"),os.path.join(internal_files_dir,".TempBuildTheme","scheme","muxdevice.txt"))
    shutil.copy2(os.path.join(internal_files_dir,".TempBuildTheme","scheme","tempmux.txt"),os.path.join(internal_files_dir,".TempBuildTheme","scheme","muxinfo.txt"))

    if crt_overlay_var.get():
        shutil.copy2(os.path.join(internal_files_dir,"Assets", "Overlays","CRT Overlay.png"),os.path.join(internal_files_dir,".TempBuildTheme","image","overlay.png"))

    os.remove(os.path.join(internal_files_dir,".TempBuildTheme","scheme","tempmux.txt"))

    if not vertical_var.get():
        replace_in_file(os.path.join(internal_files_dir,".TempBuildTheme","scheme","muxlaunch.txt"), "{ScrollDirection}", "1") ## ONLY DIFFERENCE BETWEEN THEMES IS MUXLAUNCH

    else:
        replace_in_file(os.path.join(internal_files_dir,".TempBuildTheme","scheme","muxlaunch.txt"), "{ScrollDirection}", "0") ## ONLY DIFFERENCE BETWEEN THEMES IS MUXLAUNCH
    
    os.makedirs(os.path.join(internal_files_dir,".TempBuildTheme","image","wall"), exist_ok=True)

    bootlogoimage = generatePilImageBootLogo(bgHexVar.get(),selectedFontHexVar.get(),deselectedFontHexVar.get(),bubbleHexVar.get(),render_factor).resize((deviceScreenWidth,deviceScreenHeight), Image.LANCZOS)
    bootlogoimage.save(os.path.join(internal_files_dir,".TempBuildTheme","image","bootlogo.bmp"), format='BMP')

    chargingimage = generatePilImageChargeScreen(bgHexVar.get(),deselectedFontHexVar.get(),iconHexVar.get(),render_factor).resize((deviceScreenWidth,deviceScreenHeight), Image.LANCZOS)
    chargingimage.save(os.path.join(internal_files_dir,".TempBuildTheme","image","wall","muxcharge.png"), format='PNG')

    loadingimage = generatePilImageLoadingScreen(bgHexVar.get(),iconHexVar.get(),render_factor).resize((deviceScreenWidth,deviceScreenHeight), Image.LANCZOS)
    loadingimage.save(os.path.join(internal_files_dir,".TempBuildTheme","image","wall","muxstart.png"), format='PNG')

    defaultimage = generatePilImageDefaultScreen(bgHexVar.get(),render_factor).resize((deviceScreenWidth,deviceScreenHeight), Image.LANCZOS)
    defaultimage.save(os.path.join(internal_files_dir,".TempBuildTheme","image","wall","default.png"), format='PNG')
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
                '-o', os.path.join(internal_files_dir, ".TempBuildTheme", "Assets", "font","default.bin")
            ]

            # Execute the command
            result = subprocess.run(command,shell=True )

        except FileNotFoundError as e:
            print(f"FileNotFoundError: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    itemsList = []
    if version_var.get() == "muOS 2405 BEANS":
        workingMenus = menus2405
    elif version_var.get() == "muOS 2405.1 REFRIED BEANS":
        workingMenus = menus2405_1
    elif version_var.get() == "muOS 2405.2 BAKED BEANS":
        workingMenus = menus2405_2
    else:
        raise ValueError("You Haven't Selected a muOS Version")
    for index, menu in enumerate(workingMenus):
        itemsList.append([])
        for item in menu[1]:
            itemsList[index].append([item[0],"Menu",item[1]]), 
    
    for index, menu in enumerate(workingMenus):
        if menu[0] == "muxdevice":
            if page_by_page_var.get():
                PageFolderImageGen(progress_bar,menu[0],itemsList[index],additions_powerHelpOkay,scrollBarWidth,textPadding,rectanglePadding,ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, os.path.join(internal_files_dir, ".TempBuildTheme","image","static"))
            else:
                ContinuousFolderImageGen(progress_bar,menu[0],itemsList[index],additions_powerHelpOkay,scrollBarWidth,textPadding,rectanglePadding,ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, os.path.join(internal_files_dir, ".TempBuildTheme","image","static"))
        elif menu[0] == "muxlaunch":
            if vertical_var.get():
                if page_by_page_var.get():
                    PageFolderImageGen(progress_bar,menu[0],itemsList[index],additions_PowerHelpBackOkay,scrollBarWidth,textPadding,rectanglePadding,ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, os.path.join(internal_files_dir, ".TempBuildTheme","image","static"))
                else:
                    ContinuousFolderImageGen(progress_bar,menu[0],itemsList[index],additions_PowerHelpBackOkay,scrollBarWidth,textPadding,rectanglePadding,ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, os.path.join(internal_files_dir, ".TempBuildTheme","image","static"))
            else:
                HorizontalMenuGen(progress_bar,menu[0],itemsList[index], bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, icon_hex,render_factor, os.path.join(internal_files_dir, ".TempBuildTheme","image","static"))
        elif menu[0] == "ThemePreview":
                if vertical_var.get():
                    if page_by_page_var.get():
                        PageFolderImageGen(progress_bar,menu[0],itemsList[index],additions_Preview,scrollBarWidth,textPadding,rectanglePadding,ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, os.path.join(internal_files_dir, ".TempBuildTheme","image","static"))
                    else:
                        ContinuousFolderImageGen(progress_bar,menu[0],itemsList[index],additions_Preview,scrollBarWidth,textPadding,rectanglePadding,ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, os.path.join(internal_files_dir, ".TempBuildTheme","image","static"))
        else:
            if page_by_page_var.get():
                PageFolderImageGen(progress_bar,menu[0],itemsList[index],additions_PowerHelpBackOkay,scrollBarWidth,textPadding,rectanglePadding,ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, os.path.join(internal_files_dir, ".TempBuildTheme","image","static"))
            else:
                ContinuousFolderImageGen(progress_bar,menu[0],itemsList[index],additions_PowerHelpBackOkay,scrollBarWidth,textPadding,rectanglePadding,ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor, os.path.join(internal_files_dir, ".TempBuildTheme","image","static"))

def select_alternate_menu_names():
    menu_names_grid = MenuNamesGrid(root, menuNameMap, AlternateMenuNamesPath)
    root.wait_window(menu_names_grid)
    on_change()

def generate_archive_manager(progress_bar, loading_window, input_queue, output_queue):
    try:
        # Your existing code before the main task loop...
        scrollBarWidth = int(scroll_bar_width_entry.get())
        textPadding = int(text_padding_entry.get())
        rectanglePadding = int(rectangle_padding_entry.get())
        ItemsPerScreen = int(items_per_screen_entry.get())
        bg_hex = background_hex_entry.get()
        selected_font_hex = selected_font_hex_entry.get()
        deselected_font_hex = deselected_font_hex_entry.get()
        bubble_hex = bubble_hex_entry.get()
        amThemeName = am_theme_name_entry.get()
        roms_directory = roms_directory_path.get()
        

        progress_bar['value'] = 0
        progress_bar_max = 0
        if not am_ignore_cd_var.get():
            if also_games_var.get():
                totalRoms = count_files_and_folders(roms_directory)
                progress_bar_max += totalRoms
            else:
                totalRoms = count_folders(roms_directory)
                progress_bar_max += totalRoms
        
        if not am_ignore_theme_var.get():
            progress_bar_max += 28
        progress_bar['maximum'] = progress_bar_max

        if not am_ignore_cd_var.get():
            if not roms_directory:
                raise ValueError("ROMS directory paths cannot be empty.")

            if not os.path.isdir(roms_directory):
                raise ValueError(f"Invalid ROMS directory: {roms_directory}")
        
        if not am_ignore_theme_var.get():
            FillTempThemeFolder(progress_bar)
                    
        if not am_ignore_cd_var.get():
            if not os.path.exists(os.path.join(internal_files_dir, ".TempBuildAM","mnt","mmc","MUOS","info","catalogue")):
                os.makedirs(os.path.join(internal_files_dir, ".TempBuildAM","mnt","mmc","MUOS","info","catalogue"))
            output_directory = os.path.join(internal_files_dir, ".TempBuildAM","mnt","mmc","MUOS","info","catalogue")
            
            traverse_and_generate_images(progress_bar, roms_directory, additions_Blank, scrollBarWidth, textPadding, rectanglePadding, ItemsPerScreen, bg_hex, selected_font_hex, deselected_font_hex, bubble_hex, render_factor,  output_directory, input_queue, output_queue)

        if am_theme_directory_path.get() == "":
            am_theme_dir = os.path.join(script_dir, "Generated Archive Manager Files")
        else:
            am_theme_dir = am_theme_directory_path.get()

        if not am_ignore_theme_var.get():
            copy_contents(os.path.join(internal_files_dir, ".TempBuildTheme"),os.path.join(internal_files_dir, ".TempBuildAM","mnt","mmc","MUOS","theme","active"))

        if os.path.exists(os.path.join(internal_files_dir, ".TempBuildAM")):
            shutil.make_archive(os.path.join(am_theme_dir, amThemeName),"zip", os.path.join(internal_files_dir, ".TempBuildAM"))

        if os.path.exists(os.path.join(internal_files_dir, ".TempBuildTheme")):
            delete_folder(os.path.join(internal_files_dir, ".TempBuildTheme"))
        if os.path.exists(os.path.join(internal_files_dir, ".TempBuildAM")):
            delete_folder(os.path.join(internal_files_dir, ".TempBuildAM"))
        if os.path.exists(os.path.join(internal_files_dir, "TempPreview.png")):
            os.remove(os.path.join(internal_files_dir, "TempPreview.png"))
        if not am_ignore_cd_var.get() or not am_ignore_theme_var.get():
            loading_window.destroy()
            messagebox.showinfo("Success", "Archive Manager File generated successfully.\nYou can now Activate the theme through Archive Manager")
    except Exception as e:
        loading_window.destroy()
        if theme_directory_path.get() == "":
            theme_dir = os.path.join(script_dir, "Generated Theme")
        else:
            theme_dir = theme_directory_path.get()
        delete_folder(os.path.join(internal_files_dir, ".TempBuildTheme"))
        delete_folder(os.path.join(internal_files_dir, ".TempBuildAM"))
        if os.path.exists(os.path.join(internal_files_dir, "TempPreview.png")):
            os.remove(os.path.join(internal_files_dir, "TempPreview.png"))
        if os.path.exists(os.path.join(theme_dir, "preview","TempPreview.png")):
            os.remove(os.path.join(theme_dir, "preview","TempPreview.png"))
        if advanced_error_var.get():
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            messagebox.showerror("Error", f"An unexpected error occurred: {e}\n{tb_str}")
        else:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def check_queue(root, input_queue, output_queue):
    try:
        directory_path = input_queue.get_nowait()
        consoleName = select_console(directory_path)
        output_queue.put(consoleName)
    except queue.Empty:
        pass
    root.after(100, check_queue, root, input_queue, output_queue)

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
        with open(AlternateMenuNamesPath, 'w', newline='\n',encoding='utf-8') as json_file:
            json.dump(menuNameMap, json_file, indent=2)
        self.grab_release()
        self.destroy()

def on_mousewheel(event):
    if platform.system() == 'Windows':
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    elif platform.system() == 'Darwin':
        canvas.yview_scroll(int(-1 * event.delta), "units")
    else:
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")

def on_shiftmousewheel(event):
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

def start_AM_task():
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
    threading.Thread(target=generate_archive_manager, args=(progress_bar, loading_window, input_queue, output_queue)).start()

    # Check the queue periodically
    root.after(100, check_queue, root, input_queue, output_queue)

def start_images_task():
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
    threading.Thread(target=generate_images, args=(progress_bar, loading_window, input_queue, output_queue)).start()

    # Check the queue periodically
    root.after(100, check_queue, root, input_queue, output_queue)

def start_theme_task():
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
    threading.Thread(target=generate_theme, args=(progress_bar, loading_window)).start()

    # Check the queue periodically
    root.after(100, check_queue, root, input_queue, output_queue)


def on_resize(event):
    global resize_id
    if resize_id is not None:
        root.after_cancel(resize_id)
    resize_id = root.after(0, on_change)  # Adjust the delay as needed

root = tk.Tk()
root.title("MinUI Theme Generator")
root.minsize(1080, 500)  # Set a minimum size for the window

# Get the screen height
screen_height = root.winfo_screenheight()
window_height = int(min(screen_height*0.9, 1720))

root.geometry(f"1280x{window_height}")  # Set a default size for the window

resize_id = None

root.bind("<Configure>", on_resize)

subtitle_font = font.Font(family="Helvetica", size=10, weight="bold")
title_font = font.Font(family="Helvetica", size=14, weight="bold")

# Variables for user input
roms_directory_path = tk.StringVar()
application_directory_path = tk.StringVar()
name_json_path = tk.StringVar()
background_image_path = tk.StringVar()
alt_font_path =  tk.StringVar()
box_art_directory_path = tk.StringVar()
catalogue_directory_path = tk.StringVar()
theme_directory_path = tk.StringVar()
am_theme_directory_path = tk.StringVar()
version_var = tk.StringVar()
global_alignment_var = tk.StringVar()
theme_alignment_var = tk.StringVar()
content_alignment_var = tk.StringVar()
also_games_var = tk.IntVar()
show_file_counter_var = tk.IntVar()
show_console_name_var = tk.IntVar()
show_hidden_files_var = tk.IntVar()
vertical_var = tk.IntVar()
crt_overlay_var = tk.IntVar()
alternate_menu_names_var = tk.IntVar()
remove_right_menu_guides_var = tk.IntVar()
remove_left_menu_guides_var = tk.IntVar()
override_bubble_cut_var = tk.IntVar()
page_by_page_var = tk.IntVar()
override_font_size_var = tk.IntVar()
override_folder_box_art_padding_var = tk.IntVar()
use_alt_font_var = tk.IntVar()
remove_brackets_var = tk.IntVar()
overlay_box_art_var = tk.IntVar(value=1)
remove_square_brackets_var = tk.IntVar()
replace_hyphen_var = tk.IntVar()
move_the_var = tk.IntVar()
am_ignore_theme_var = tk.IntVar()
am_ignore_cd_var = tk.IntVar()
advanced_error_var = tk.IntVar()

# Create a canvas and a vertical scrollbar
canvas = tk.Canvas(root)

scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Pack the canvas and scrollbar
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Bind mouse wheel events based on the platform
if platform.system() == 'Darwin':
    canvas.bind_all("<MouseWheel>", on_mousewheel)
    canvas.bind_all("<Shift-MouseWheel>", on_shiftmousewheel)
else:
    canvas.bind_all("<MouseWheel>", on_mousewheel)
    canvas.bind_all("<Shift-MouseWheel>", on_shiftmousewheel)
    canvas.bind_all("<Button-4>", on_mousewheel)  # For Linux
    canvas.bind_all("<Button-5>", on_mousewheel)  # For Linux

# Create the grid helper
grid_helper = GridHelper(scrollable_frame)

# Create the GUI components
grid_helper.add(tk.Label(scrollable_frame, text="[WARNING] PLEASE BACKUP YOUR WHOLE CATALOGUE FOLDER! CHOOSING SOME OPTIONS WILL OVERRIDE GAME BOX ART", fg='#f00'), colspan=3, sticky="w", next_row=True)
grid_helper.add(tk.Label(scrollable_frame, text="Configurations", font=title_font), colspan=3, sticky="w", next_row=True)
grid_helper.add(tk.Label(scrollable_frame, text="Global Configurations", font=subtitle_font), colspan=3, sticky="w", next_row=True)

# Define the StringVar variables
scrollBarWidthVar = tk.StringVar()
textPaddingVar = tk.StringVar()
bubblePaddingVar = tk.StringVar()
itemsPerScreenVar = tk.StringVar()
footerHeightVar = tk.StringVar()
boxArtPaddingVar = tk.StringVar()
folderBoxArtPaddingVar = tk.StringVar()
customFontSizeVar = tk.StringVar()
bgHexVar = tk.StringVar()
selectedFontHexVar = tk.StringVar()
deselectedFontHexVar = tk.StringVar()
bubbleHexVar = tk.StringVar()
iconHexVar = tk.StringVar()
maxBubbleLengthVar = tk.StringVar()
previewConsoleNameVar = tk.StringVar()


# Option for scrollBarWidth
grid_helper.add(tk.Label(scrollable_frame, text="Scroll Bar Width:"), sticky="w")
scroll_bar_width_entry = tk.Entry(scrollable_frame, width=50, textvariable=scrollBarWidthVar)
grid_helper.add(scroll_bar_width_entry, next_row=True)

# Option for textPadding
grid_helper.add(tk.Label(scrollable_frame, text="Text Padding:"), sticky="w")
text_padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=textPaddingVar)
grid_helper.add(text_padding_entry, next_row=True)

# Option for rectanglePadding
grid_helper.add(tk.Label(scrollable_frame, text="Bubble Padding:"), sticky="w")
rectangle_padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=bubblePaddingVar)
grid_helper.add(rectangle_padding_entry, next_row=True)

# Option for ItemsPerScreen
grid_helper.add(tk.Label(scrollable_frame, text="Items Per Screen:"), sticky="w")
items_per_screen_entry = tk.Entry(scrollable_frame, width=50, textvariable=itemsPerScreenVar)
grid_helper.add(items_per_screen_entry, next_row=True)

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

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Page by Page Scrolling", variable=page_by_page_var), colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="[Optional] Override background colour with image"), sticky="w")
grid_helper.add(tk.Entry(scrollable_frame, textvariable=background_image_path, width=50))
grid_helper.add(tk.Button(scrollable_frame, text="Browse...", command=select_background_image_path), next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="*[Optional] Use Custom font:", variable=use_alt_font_var), sticky="w")
grid_helper.add(tk.Entry(scrollable_frame, textvariable=alt_font_path, width=50))
grid_helper.add(tk.Button(scrollable_frame, text="Browse...", command=select_alt_font_path), next_row=True)
grid_helper.add(tk.Label(scrollable_frame,text="*Use if text override characters not supported by default font",fg="#00f"),sticky="w",next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="[Optional] Override font size:", variable=override_font_size_var), sticky="w")
custom_font_size_entry = tk.Entry(scrollable_frame, width=50, textvariable=customFontSizeVar)
grid_helper.add(custom_font_size_entry, next_row=True)

# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Theme Specific Configurations", font=subtitle_font), sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="[Optional] Custom Application Directory:"), sticky="w")
grid_helper.add(tk.Entry(scrollable_frame, textvariable=application_directory_path, width=50))
grid_helper.add(tk.Button(scrollable_frame, text="Browse...", command=select_application_directory), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Should be '[root]:\\MUOS\\application' on your muOS SD Card, but it will let you select any folder."), colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="muOS Version"), sticky="w")
options = ["muOS 2405 BEANS", "muOS 2405.1 REFRIED BEANS", "muOS 2405.2 BAKED BEANS"]
option_menu = tk.OptionMenu(scrollable_frame, version_var, *options)
grid_helper.add(option_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Theme Text Alignment"), sticky="w")
themeAlignmentOptions = ["Global", "Left", "Centre", "Right"]
theme_alignment_option_menu = tk.OptionMenu(scrollable_frame, theme_alignment_var, *themeAlignmentOptions)
grid_helper.add(theme_alignment_option_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Vertical Main Menu (Like Original MinUI)", variable=vertical_var), sticky="w")
grid_helper.add(tk.Checkbutton(scrollable_frame, text="Include CRT Overlay", variable=crt_overlay_var), sticky="w", next_row=True)
grid_helper.add(tk.Checkbutton(scrollable_frame, text="Override text in menus [Can be used for Translations]", variable=alternate_menu_names_var), sticky="w")
grid_helper.add(tk.Button(scrollable_frame, text="Select new menu item names", command=select_alternate_menu_names), sticky="w", next_row=True)
grid_helper.add(tk.Checkbutton(scrollable_frame, text="Remove Left Menu Helper Guides", variable=remove_left_menu_guides_var), sticky="w")
grid_helper.add(tk.Checkbutton(scrollable_frame, text="Remove Right Menu Helper Guides", variable=remove_right_menu_guides_var), colspan=3, sticky="w", next_row=True)

# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Box Art Specific Configurations", font=subtitle_font), colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Catalogue Directory with Box Art:"), sticky="w")
grid_helper.add(tk.Entry(scrollable_frame, textvariable=box_art_directory_path, width=50))
grid_helper.add(tk.Button(scrollable_frame, text="Browse...", command=select_box_art_directory), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text=" - This can be your catalogue folder on your device, but I would recommend copying it off the device so you can use this tool multiple times.",fg="#00f"), colspan=3, sticky="w", next_row=True)

##BoxArtPadding
grid_helper.add(tk.Label(scrollable_frame, text="Box Art Right Padding:"), sticky="w")
box_art_padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=boxArtPaddingVar)
grid_helper.add(box_art_padding_entry, next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="[Optional] Folder Art Specific Padding:", variable=override_folder_box_art_padding_var), sticky="w")
folder_box_art_padding_entry = tk.Entry(scrollable_frame, width=50, textvariable=folderBoxArtPaddingVar)
grid_helper.add(folder_box_art_padding_entry, next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Override Auto Cut Bubble off [Might want to use for fading box art]", variable=override_bubble_cut_var),colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text=" - Cut bubble off at (px):"), sticky="w")

max_bubble_length_entry = tk.Entry(scrollable_frame, width=50, textvariable=maxBubbleLengthVar)
grid_helper.add(max_bubble_length_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text=" - This would usually be 640-width of your boxart",fg="#00f"), colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Preview muOS Console name [Just for preview on the right]:"), sticky="w")
preview_console_name_entry = tk.Entry(scrollable_frame, width=50, textvariable=previewConsoleNameVar)
grid_helper.add(preview_console_name_entry, next_row=True)

# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Content Explorer Specific Configurations", font=subtitle_font), colspan=3, sticky="w", next_row=True)
grid_helper.add(tk.Label(scrollable_frame, text="Roms Input Directory:"), sticky="w")
grid_helper.add(tk.Entry(scrollable_frame, textvariable=roms_directory_path, width=50))
grid_helper.add(tk.Button(scrollable_frame, text="Browse...", command=select_input_directory), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Should be '[root]:\\ROMS' on your muOS SD Card, but it will let you select any folder."), colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="name.json file Directory:"), sticky="w")
grid_helper.add(tk.Entry(scrollable_frame, textvariable=name_json_path, width=50))
grid_helper.add(tk.Button(scrollable_frame, text="Browse...", command=select_name_json_path), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Should be '[root]:\\MUOS\\info\\name.json' on your muOS SD Card, but it will let you select any folder."), colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Content Explorer Text Alignment"), sticky="w")
contentAlignmentOptions = ["Global", "Left", "Centre", "Right"]
content_alignment_option_menu = tk.OptionMenu(scrollable_frame, content_alignment_var, *contentAlignmentOptions)
grid_helper.add(content_alignment_option_menu, colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="[Experimental] Also Generate Images for Game List *", variable=also_games_var), sticky="w")

grid_helper.add(tk.Checkbutton(scrollable_frame, text="[Experimental] Show hidden Content", variable=show_hidden_files_var), sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Merge with Box Art", variable=overlay_box_art_var), sticky="w")

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Replace ' - ' with ': '", variable=replace_hyphen_var), sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Remove ()", variable=remove_brackets_var), sticky="w")
grid_helper.add(tk.Checkbutton(scrollable_frame, text="Remove []", variable=remove_square_brackets_var), sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Put 'The' At the start, instead of the end ', The'", variable=move_the_var), sticky="w")

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Show File Counter **", variable=show_file_counter_var), sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Show Console Name at top", variable=show_console_name_var), sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="* [IMPORTANT] THIS WILL OVERRIDE YOUR GAME BOX ART... MAKE A BACKUP OF THE WHOLE CATALOGUE FOLDER.", fg='#f00'), colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="* [IMPORTANT] Note selecting this option will make favourite and history messed up.\nOnly use this if you don't use Favourites and History, or you just want to experiment.", fg='#f00'), colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="* Games may also appear in the wrong order", fg='#0000ff'), colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="** In order for File Counter to be visible box art must be set to 'Fullscreen + Front'", fg='#0000ff'), colspan=3, sticky="w", next_row=True)

# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Generation", font=title_font), colspan=2, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Combined generation for Archive manager install [Recommended]", font=subtitle_font), colspan=2, sticky="w", next_row=True)
grid_helper.add(tk.Label(scrollable_frame, text="Make sure your box art setting is set to Fullscreen+Front for this!", font=subtitle_font,fg="#00f"), colspan=2, sticky="w", next_row=True)


grid_helper.add(tk.Label(scrollable_frame, text="Archive Manager Theme Name:"), sticky="w")
am_theme_name_entry = tk.Entry(scrollable_frame, width=50)
grid_helper.add(am_theme_name_entry, next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Archive Manager Output Directory:"), sticky="w")
grid_helper.add(tk.Entry(scrollable_frame, textvariable=am_theme_directory_path, width=50))
grid_helper.add(tk.Button(scrollable_frame, text="Browse...", command=select_am_theme_directory), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Should be '[root]:\\ARCHIVE' on your muOS SD Card, but it will let you select any folder."), colspan=3, sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Don't Generate Theme", variable=am_ignore_theme_var), colspan=1, sticky="w", next_row=False)
grid_helper.add(tk.Checkbutton(scrollable_frame, text="Don't Generate Content Explorer Theme", variable=am_ignore_cd_var), colspan=1, sticky="w", next_row=True)

# Generate button
grid_helper.add(tk.Button(scrollable_frame, text="Generate Archive Manager File", command=start_AM_task), sticky="w", next_row=True)

# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Theme only generation", font=subtitle_font), colspan=2, sticky="w", next_row=True)
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

grid_helper.add(tk.Label(scrollable_frame, text="Content explorer only generation", font=subtitle_font), colspan=2, sticky="w", next_row=True)
grid_helper.add(tk.Label(scrollable_frame, text="Make sure your box art setting is set to Fullscreen+Front for this!", font=subtitle_font,fg="#00f"), colspan=2, sticky="w", next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Catalogue Directory on device:"), sticky="w")
grid_helper.add(tk.Entry(scrollable_frame, textvariable=catalogue_directory_path, width=50))
grid_helper.add(tk.Button(scrollable_frame, text="Browse...", command=select_output_directory), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="Should be '[root]:\\MUOS\\info\\catalogue' on your muOS SD Card, but it will let you select any folder."), colspan=3, sticky="w", next_row=True)

# Spacer row
grid_helper.add(tk.Label(scrollable_frame, text=""), next_row=True)

grid_helper.add(tk.Label(scrollable_frame, text="If you choose to generate the Game and Console Image files, to remove them you will need to", fg='#00f'), colspan=3, sticky="w", next_row=True)
grid_helper.add(tk.Label(scrollable_frame, text="remove all the files in your catalogue folder you can do this with the red button below.", fg='#00f'), colspan=2, sticky="w", next_row=True)

# Generate button
grid_helper.add(tk.Button(scrollable_frame, text="Generate Images", command=start_images_task), sticky="w")
grid_helper.add(tk.Button(scrollable_frame, text="Remove all images in Selected Catalogue Folder", command=remove_images, fg="#f00"), sticky="w", next_row=True)

grid_helper.add(tk.Checkbutton(scrollable_frame, text="Show Advanced Errors", variable=advanced_error_var), colspan=3, sticky="w", next_row=True)


image_frame = tk.Frame(root)
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

def update_image_label(image_label, pil_image):
    tk_image = ImageTk.PhotoImage(pil_image)
    image_label.config(image=tk_image)
    image_label.image = tk_image
    #image_label.clear()
def remove_image_from_label(image_label):
    image_label.config(image='')


def get_current_image(image_label):
    # Retrieve the PhotoImage object from the label
    tk_image = image_label.image
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

crt_overlay_image = Image.open(os.path.join(internal_files_dir, "Assets", "Overlays", "CRT Overlay.png")).convert("RGBA")

def updateMenusList(menusList, defaultList):
    if application_directory_path.get()!="" and os.path.exists(application_directory_path.get()): # muOS 2405.2
        newApplicationList = [[x[0],x[0]] for x in list_directory_contents(application_directory_path.get())]
        index = None
        for i, n in enumerate(menusList):
            if n[0] == "muxapp":
                index = i
                break
        if index!=None:
            menusList[index][1] = newApplicationList
    else:
        index = None
        for i, n in enumerate(menusList):
            if n[0] == "muxapp":
                index = i
                break
        if index!=None:
            menusList[index][1] = defaultList

def on_change(*args):
    global footerHeight
    try:
        footerHeight = int(footer_height_entry.get())
    except:
        footerHeight = 55
    save_settings()
    config.save_config()
    global background_image

    if ("" != background_image_path.get()) and os.path.exists(background_image_path.get()):
        background_image = Image.open(background_image_path.get())
    else:
        background_image = None

    global menus2405
    global menus2405_1 ## NOT GLOBALS AHH SORRY HACKY SHOULD REMOVE
    global menus2405_2

    menus2405_1_Default_list = [['Archive Manager', 'Archive Manager'], ['Dingux Commander', 'Dingux Commander'], ['GMU Music Player', 'GMU Music Player'], ['PortMaster', 'PortMaster'], ['RetroArch', 'RetroArch'], ['Simple Terminal', 'Simple Terminal'], ['Task Toolkit', 'Task Toolkit']]
    updateMenusList(menus2405_1, menus2405_1_Default_list)

    menus2405_2_Default_list = [['Archive Manager', 'Archive Manager'], ['Dingux Commander', 'Dingux Commander'], ['Flip Clock', 'Flip Clock'], ['GMU Music Player', 'GMU Music Player'], ['Moonlight', 'Moonlight'], ['PortMaster', 'PortMaster'], ['PPSSPP', 'PPSSPP'], ['RetroArch', 'RetroArch'], ['Simple Terminal', 'Simple Terminal'], ['Task Toolkit', 'Task Toolkit']]
    updateMenusList(menus2405_2, menus2405_2_Default_list)

    previewApplicationList = []
    if version_var.get() == "muOS 2405 BEANS":
        index = None
        for i, n in enumerate(menus2405):
            if n[0] == "muxapps":
                index = i
                break
        if index!=None:
            previewApplicationList = [[x[0],"menu",x[0]] for x in menus2405[index][1]]
    elif version_var.get() == "muOS 2405.1 REFRIED BEANS":
        index = None
        for i, n in enumerate(menus2405_1):
            if n[0] == "muxapp":
                index = i
                break
        if index!=None:
            previewApplicationList = [[x[0],"menu",x[0]] for x in menus2405_1[index][1]]
    elif version_var.get() == "muOS 2405.2 BAKED BEANS":
        index = None
        for i, n in enumerate(menus2405_2):
            if n[0] == "muxapp":
                index = i
                break
        if index!=None:
            previewApplicationList = [[x[0],"menu",x[0]] for x in menus2405_2[index][1]]

    global valid_params
    
    fakeprogressbar={'value':0}
    fakeprogressbar['maximum']=1

    if vertical_var.get():
        preview_multiplier = (root.winfo_height()/4.1)/deviceScreenHeight
    else:
        preview_multiplier = (root.winfo_height()/5.2)/deviceScreenHeight
    preview_size = (int(deviceScreenWidth*preview_multiplier),int(deviceScreenHeight*preview_multiplier))
    # This function will run whenever any traced variable changes
    try:
        consoleName = consoleMap.get(previewConsoleNameVar.get().lower(), previewConsoleNameVar.get())
        previewItemList = [['Content Explorer', 'Menu', 'explore'], ['Favourites', 'Menu', 'favourite'], ['History', 'Menu', 'history'], ['Applications', 'Menu', 'apps'], ['Information', 'Menu', 'info'], ['Configuration', 'Menu', 'config'], ['Reboot Device', 'Menu', 'reboot'], ['Shutdown Device', 'Menu', 'shutdown']]
        previewGameItemList = [['4-in-1 Fun Pak [Version 1] (USA, Europe)', 'File', '4-in-1 Fun Pak [Version 1] (USA, Europe)'], ['4-in-1 Funpak - Volume II (USA, Europe)', 'File', '4-in-1 Funpak - Volume II (USA, Europe)'], ['A-mazing Tater (USA)', 'File', 'A-mazing Tater (USA)'], ['Addams Family, The (USA)', 'File', 'Addams Family, The (USA)'], ["Addams Family, The - Pugsley's Scavenger Hunt (USA, Europe) [Revision]", 'File', "Addams Family, The - Pugsley's Scavenger Hunt (USA, Europe) [Revision]"], ['Adventure Island (USA, Europe)', 'File', 'Adventure Island (USA, Europe)'], ['Adventure Island II - Aliens in Paradise (USA, Europe)', 'File', 'Adventure Island II - Aliens in Paradise (USA, Europe)'], ['Adventures of Rocky and Bullwinkle and Friends, The (USA)', 'File', 'Adventures of Rocky and Bullwinkle and Friends, The (USA)'], ['Adventures of Star Saver, The (USA, Europe)', 'File', 'Adventures of Star Saver, The (USA, Europe)'], ['Aerostar (USA, Europe)', 'File', 'Aerostar (USA, Europe)'], ['Aladdin (USA) (SGB Enhanced)', 'File', 'Aladdin (USA) (SGB Enhanced)'], ['Alfred Chicken (USA)', 'File', 'Alfred Chicken (USA)'], ['Alien 3 (USA, Europe)', 'File', 'Alien 3 (USA, Europe)'], ['Alien vs Predator - The Last of His Clan (USA)', 'File', 'Alien vs Predator - The Last of His Clan (USA)'], ['All-Star Baseball 99 (USA)', 'File', 'All-Star Baseball 99 (USA)'], ['Altered Space - A 3-D Alien Adventure (USA)', 'File', 'Altered Space - A 3-D Alien Adventure (USA)'], ['Amazing Penguin (USA, Europe)', 'File', 'Amazing Penguin (USA, Europe)'], ['Amazing Spider-Man, The (USA, Europe)', 'File', 'Amazing Spider-Man, The (USA, Europe)'], ['Animaniacs (USA) (SGB Enhanced)', 'File', 'Animaniacs (USA) (SGB Enhanced)'], ['Arcade Classic No. 1 - Asteroids & Missile Command (USA, Europe) (SGB Enhanced)', 'File', 'Arcade Classic No. 1 - Asteroids & Missile Command (USA, Europe) (SGB Enhanced)'], ['Arcade Classic No. 2 - Centipede & Millipede (USA, Europe) (SGB Enhanced)', 'File', 'Arcade Classic No. 2 - Centipede & Millipede (USA, Europe) (SGB Enhanced)'], ['Arcade Classic No. 3 - Galaga & Galaxian (USA) (SGB Enhanced)', 'File', 'Arcade Classic No. 3 - Galaga & Galaxian (USA) (SGB Enhanced)'], ['Arcade Classic No. 4 - Defender & Joust (USA, Europe) (SGB Enhanced)', 'File', 'Arcade Classic No. 4 - Defender & Joust (USA, Europe) (SGB Enhanced)'], ['Arcade Classics - Super Breakout & Battlezone (USA, Europe) (SGB Enhanced)', 'File', 'Arcade Classics - Super Breakout & Battlezone (USA, Europe) (SGB Enhanced)'], ['Asteroids (USA, Europe)', 'File', 'Asteroids (USA, Europe)'], ['Atomic Punk (USA)', 'File', 'Atomic Punk (USA)'], ['Attack of the Killer Tomatoes (USA, Europe)', 'File', 'Attack of the Killer Tomatoes (USA, Europe)'], ['Avenging Spirit (USA, Europe)', 'File', 'Avenging Spirit (USA, Europe)'], ['Balloon Kid (USA, Europe)', 'File', 'Balloon Kid (USA, Europe)'], ['Barbie - Game Girl (USA, Europe)', 'File', 'Barbie - Game Girl (USA, Europe)'], ["Bart Simpson's Escape from Camp Deadly (USA, Europe)", 'File', "Bart Simpson's Escape from Camp Deadly (USA, Europe)"], ['Bases Loaded for Game Boy (USA)', 'File', 'Bases Loaded for Game Boy (USA)'], ['Batman - Return of the Joker (USA, Europe)', 'File', 'Batman - Return of the Joker (USA, Europe)'], ['Batman - The Animated Series (USA, Europe)', 'File', 'Batman - The Animated Series (USA, Europe)'], ['Batman Forever (USA, Europe)', 'File', 'Batman Forever (USA, Europe)'], ['Battle Arena Toshinden (USA) (SGB Enhanced)', 'File', 'Battle Arena Toshinden (USA) (SGB Enhanced)'], ['Battle Bull (USA)', 'File', 'Battle Bull (USA)'], ['Battle Unit Zeoth (USA, Europe)', 'File', 'Battle Unit Zeoth (USA, Europe)'], ['Battleship (USA, Europe)', 'File', 'Battleship (USA, Europe)'], ['Battletoads (USA, Europe)', 'File', 'Battletoads (USA, Europe)'], ["Battletoads in Ragnarok's World (USA)", 'File', "Battletoads in Ragnarok's World (USA)"], ['Battletoads-Double Dragon (USA)', 'File', 'Battletoads-Double Dragon (USA)'], ['Beavis and Butt-Head (USA, Europe)', 'File', 'Beavis and Butt-Head (USA, Europe)'], ['Beetlejuice (USA)', 'File', 'Beetlejuice (USA)'], ['Best of the Best - Championship Karate (USA)', 'File', 'Best of the Best - Championship Karate (USA)'], ["Bill & Ted's Excellent Game Boy Adventure - A Bogus Journey! (USA, Europe)", 'File', "Bill & Ted's Excellent Game Boy Adventure - A Bogus Journey! (USA, Europe)"], ["Bill Elliott's NASCAR Fast Tracks (USA)", 'File', "Bill Elliott's NASCAR Fast Tracks (USA)"], ['Bionic Battler (USA)', 'File', 'Bionic Battler (USA)'], ['Bionic Commando (USA)', 'File', 'Bionic Commando (USA)'], ['Black Bass - Lure Fishing (USA)', 'File', 'Black Bass - Lure Fishing (USA)'], ['Blades of Steel (USA)', 'File', 'Blades of Steel (USA)'], ['Blaster Master Boy (USA)', 'File', 'Blaster Master Boy (USA)'], ['Blues Brothers, The (USA, Europe)', 'File', 'Blues Brothers, The (USA, Europe)'], ['Bo Jackson - Two Games in One (USA)', 'File', 'Bo Jackson - Two Games in One (USA)'], ['Boggle Plus (USA)', 'File', 'Boggle Plus (USA)'], ['Bomberman GB (USA, Europe) (SGB Enhanced)', 'File', 'Bomberman GB (USA, Europe) (SGB Enhanced)'], ["Bonk's Adventure (USA)", 'File', "Bonk's Adventure (USA)"], ["Bonk's Revenge (USA) (SGB Enhanced)", 'File', "Bonk's Revenge (USA) (SGB Enhanced)"]]

        if not os.path.exists(roms_directory_path.get()):
            previewConsolesItemList = [['Game Boy', 'Directory', 'Game Boy'], ['Game Boy Advance', 'Directory', 'Game Boy Advance'], ['Game Boy Color', 'Directory', 'Game Boy Color'], ['game-boy-romset-ultra-us', 'Directory', 'game-boy-romset-ultra-us'], ['Nintendo 64', 'Directory', 'Nintendo 64'], ['Nintendo DS', 'Directory', 'Nintendo DS'], ['Nintendo Entertainment System', 'Directory', 'Nintendo Entertainment System'], ['PICO-8', 'Directory', 'PICO-8'], ['Ports', 'Directory', 'Ports'], ['SEGA Mega Drive', 'Directory', 'SEGA Mega Drive'], ['Super Nintendo Entertainment System', 'Directory', 'Super Nintendo Entertainment System']]
        else:
            previewConsolesItemList = list_directory_contents(roms_directory_path.get())

            if os.path.exists(os.path.join(roms_directory_path.get(),previewConsolesItemList[0][0])):
                previewGameItemList = list_directory_contents(os.path.join(roms_directory_path.get(),previewConsolesItemList[0][0]))
            else:
                previewGameItemList = [['4-in-1 Fun Pak [Version 1] (USA, Europe)', 'File', '4-in-1 Fun Pak [Version 1] (USA, Europe)'], ['4-in-1 Funpak - Volume II (USA, Europe)', 'File', '4-in-1 Funpak - Volume II (USA, Europe)'], ['A-mazing Tater (USA)', 'File', 'A-mazing Tater (USA)'], ['Addams Family, The (USA)', 'File', 'Addams Family, The (USA)'], ["Addams Family, The - Pugsley's Scavenger Hunt (USA, Europe) [Revision]", 'File', "Addams Family, The - Pugsley's Scavenger Hunt (USA, Europe) [Revision]"], ['Adventure Island (USA, Europe)', 'File', 'Adventure Island (USA, Europe)'], ['Adventure Island II - Aliens in Paradise (USA, Europe)', 'File', 'Adventure Island II - Aliens in Paradise (USA, Europe)'], ['Adventures of Rocky and Bullwinkle and Friends, The (USA)', 'File', 'Adventures of Rocky and Bullwinkle and Friends, The (USA)'], ['Adventures of Star Saver, The (USA, Europe)', 'File', 'Adventures of Star Saver, The (USA, Europe)'], ['Aerostar (USA, Europe)', 'File', 'Aerostar (USA, Europe)'], ['Aladdin (USA) (SGB Enhanced)', 'File', 'Aladdin (USA) (SGB Enhanced)'], ['Alfred Chicken (USA)', 'File', 'Alfred Chicken (USA)'], ['Alien 3 (USA, Europe)', 'File', 'Alien 3 (USA, Europe)'], ['Alien vs Predator - The Last of His Clan (USA)', 'File', 'Alien vs Predator - The Last of His Clan (USA)'], ['All-Star Baseball 99 (USA)', 'File', 'All-Star Baseball 99 (USA)'], ['Altered Space - A 3-D Alien Adventure (USA)', 'File', 'Altered Space - A 3-D Alien Adventure (USA)'], ['Amazing Penguin (USA, Europe)', 'File', 'Amazing Penguin (USA, Europe)'], ['Amazing Spider-Man, The (USA, Europe)', 'File', 'Amazing Spider-Man, The (USA, Europe)'], ['Animaniacs (USA) (SGB Enhanced)', 'File', 'Animaniacs (USA) (SGB Enhanced)'], ['Arcade Classic No. 1 - Asteroids & Missile Command (USA, Europe) (SGB Enhanced)', 'File', 'Arcade Classic No. 1 - Asteroids & Missile Command (USA, Europe) (SGB Enhanced)'], ['Arcade Classic No. 2 - Centipede & Millipede (USA, Europe) (SGB Enhanced)', 'File', 'Arcade Classic No. 2 - Centipede & Millipede (USA, Europe) (SGB Enhanced)'], ['Arcade Classic No. 3 - Galaga & Galaxian (USA) (SGB Enhanced)', 'File', 'Arcade Classic No. 3 - Galaga & Galaxian (USA) (SGB Enhanced)'], ['Arcade Classic No. 4 - Defender & Joust (USA, Europe) (SGB Enhanced)', 'File', 'Arcade Classic No. 4 - Defender & Joust (USA, Europe) (SGB Enhanced)'], ['Arcade Classics - Super Breakout & Battlezone (USA, Europe) (SGB Enhanced)', 'File', 'Arcade Classics - Super Breakout & Battlezone (USA, Europe) (SGB Enhanced)'], ['Asteroids (USA, Europe)', 'File', 'Asteroids (USA, Europe)'], ['Atomic Punk (USA)', 'File', 'Atomic Punk (USA)'], ['Attack of the Killer Tomatoes (USA, Europe)', 'File', 'Attack of the Killer Tomatoes (USA, Europe)'], ['Avenging Spirit (USA, Europe)', 'File', 'Avenging Spirit (USA, Europe)'], ['Balloon Kid (USA, Europe)', 'File', 'Balloon Kid (USA, Europe)'], ['Barbie - Game Girl (USA, Europe)', 'File', 'Barbie - Game Girl (USA, Europe)'], ["Bart Simpson's Escape from Camp Deadly (USA, Europe)", 'File', "Bart Simpson's Escape from Camp Deadly (USA, Europe)"], ['Bases Loaded for Game Boy (USA)', 'File', 'Bases Loaded for Game Boy (USA)'], ['Batman - Return of the Joker (USA, Europe)', 'File', 'Batman - Return of the Joker (USA, Europe)'], ['Batman - The Animated Series (USA, Europe)', 'File', 'Batman - The Animated Series (USA, Europe)'], ['Batman Forever (USA, Europe)', 'File', 'Batman Forever (USA, Europe)'], ['Battle Arena Toshinden (USA) (SGB Enhanced)', 'File', 'Battle Arena Toshinden (USA) (SGB Enhanced)'], ['Battle Bull (USA)', 'File', 'Battle Bull (USA)'], ['Battle Unit Zeoth (USA, Europe)', 'File', 'Battle Unit Zeoth (USA, Europe)'], ['Battleship (USA, Europe)', 'File', 'Battleship (USA, Europe)'], ['Battletoads (USA, Europe)', 'File', 'Battletoads (USA, Europe)'], ["Battletoads in Ragnarok's World (USA)", 'File', "Battletoads in Ragnarok's World (USA)"], ['Battletoads-Double Dragon (USA)', 'File', 'Battletoads-Double Dragon (USA)'], ['Beavis and Butt-Head (USA, Europe)', 'File', 'Beavis and Butt-Head (USA, Europe)'], ['Beetlejuice (USA)', 'File', 'Beetlejuice (USA)'], ['Best of the Best - Championship Karate (USA)', 'File', 'Best of the Best - Championship Karate (USA)'], ["Bill & Ted's Excellent Game Boy Adventure - A Bogus Journey! (USA, Europe)", 'File', "Bill & Ted's Excellent Game Boy Adventure - A Bogus Journey! (USA, Europe)"], ["Bill Elliott's NASCAR Fast Tracks (USA)", 'File', "Bill Elliott's NASCAR Fast Tracks (USA)"], ['Bionic Battler (USA)', 'File', 'Bionic Battler (USA)'], ['Bionic Commando (USA)', 'File', 'Bionic Commando (USA)'], ['Black Bass - Lure Fishing (USA)', 'File', 'Black Bass - Lure Fishing (USA)'], ['Blades of Steel (USA)', 'File', 'Blades of Steel (USA)'], ['Blaster Master Boy (USA)', 'File', 'Blaster Master Boy (USA)'], ['Blues Brothers, The (USA, Europe)', 'File', 'Blues Brothers, The (USA, Europe)'], ['Bo Jackson - Two Games in One (USA)', 'File', 'Bo Jackson - Two Games in One (USA)'], ['Boggle Plus (USA)', 'File', 'Boggle Plus (USA)'], ['Bomberman GB (USA, Europe) (SGB Enhanced)', 'File', 'Bomberman GB (USA, Europe) (SGB Enhanced)'], ["Bonk's Adventure (USA)", 'File', "Bonk's Adventure (USA)"], ["Bonk's Revenge (USA) (SGB Enhanced)", 'File', "Bonk's Revenge (USA) (SGB Enhanced)"]]

        if not(vertical_var.get()):
            image1 = generatePilImageHorizontal(fakeprogressbar,0,bgHexVar.get(),selectedFontHexVar.get(),deselectedFontHexVar.get(),bubbleHexVar.get(),iconHexVar.get(),1).resize(preview_size, Image.LANCZOS)
        else:
            if not page_by_page_var.get():
                image1 = generatePilImageVertical(fakeprogressbar,0,
                                                "muxlaunch",
                                                previewItemList[0:int(items_per_screen_entry.get())],
                                                additions_Blank,
                                                int(textPaddingVar.get()),
                                                int(bubblePaddingVar.get()),
                                                int(items_per_screen_entry.get()),
                                                bgHexVar.get(),
                                                selectedFontHexVar.get(),
                                                deselectedFontHexVar.get(),
                                                bubbleHexVar.get()
                                                ,1).resize(preview_size, Image.LANCZOS)
            else:
                image1 = generatePilImageVertical(fakeprogressbar,0,
                                "muxlaunch",
                                previewItemList[0:int(items_per_screen_entry.get())],
                                additions_Blank,
                                int(textPaddingVar.get()),
                                int(bubblePaddingVar.get()),
                                int(items_per_screen_entry.get()),
                                bgHexVar.get(),
                                selectedFontHexVar.get(),
                                deselectedFontHexVar.get(),
                                bubbleHexVar.get()
                                ,1,
                                scrollBarWidth=int(scrollBarWidthVar.get()),
                                showScrollBar=(len(previewItemList)/int(items_per_screen_entry.get()))>1,
                                numScreens=math.ceil(len(previewItemList)/int(items_per_screen_entry.get())),
                                screenIndex=0).resize(preview_size, Image.LANCZOS)
        if not page_by_page_var.get():
            image2 = generatePilImageVertical(fakeprogressbar,0,
                                            "Folder",
                                            previewConsolesItemList[0:int(items_per_screen_entry.get())],
                                            additions_Blank,
                                            int(textPaddingVar.get()),
                                            int(bubblePaddingVar.get()),
                                            int(items_per_screen_entry.get()),
                                            bgHexVar.get(),
                                            selectedFontHexVar.get(),
                                            deselectedFontHexVar.get(),
                                            bubbleHexVar.get()
                                            ,1,fileCounter="1 / " + items_per_screen_entry.get()).resize(preview_size, Image.LANCZOS)
            image3 = generatePilImageVertical(fakeprogressbar,0,
                                            consoleName, 
                                            previewGameItemList[0:int(items_per_screen_entry.get())],
                                            additions_Blank,
                                            int(textPaddingVar.get()),
                                            int(bubblePaddingVar.get()),
                                            int(items_per_screen_entry.get()),
                                            bgHexVar.get(),
                                            selectedFontHexVar.get(),
                                            deselectedFontHexVar.get(),
                                            bubbleHexVar.get()
                                            ,1,fileCounter="1 / " + items_per_screen_entry.get()).resize(preview_size, Image.LANCZOS)
            image4 = generatePilImageVertical(fakeprogressbar,0,
                                            "muxapp",
                                            previewApplicationList[0:int(items_per_screen_entry.get())],
                                            additions_Blank,
                                            int(textPaddingVar.get()),
                                            int(bubblePaddingVar.get()),
                                            int(items_per_screen_entry.get()),
                                            bgHexVar.get(),
                                            selectedFontHexVar.get(),
                                            deselectedFontHexVar.get(),
                                            bubbleHexVar.get()
                                            ,1,fileCounter="1 / " + items_per_screen_entry.get()).resize(preview_size, Image.LANCZOS)
        else:
            image2 = generatePilImageVertical(fakeprogressbar,0,
                                            "Folder",
                                            previewConsolesItemList[0:int(items_per_screen_entry.get())],
                                            additions_Blank,
                                            int(textPaddingVar.get()),
                                            int(bubblePaddingVar.get()),
                                            int(items_per_screen_entry.get()),
                                            bgHexVar.get(),
                                            selectedFontHexVar.get(),
                                            deselectedFontHexVar.get(),
                                            bubbleHexVar.get()
                                            ,1,scrollBarWidth=int(scrollBarWidthVar.get()),
                                            showScrollBar=(len(previewConsolesItemList)/int(items_per_screen_entry.get()))>1,
                                            numScreens=math.ceil(len(previewConsolesItemList)/int(items_per_screen_entry.get())),
                                            screenIndex=0,fileCounter="1 / " + items_per_screen_entry.get()).resize(preview_size, Image.LANCZOS)
            image3 = generatePilImageVertical(fakeprogressbar,0,
                                            consoleName,
                                            previewGameItemList[0:int(items_per_screen_entry.get())],
                                            additions_Blank,
                                            int(textPaddingVar.get()),
                                            int(bubblePaddingVar.get()),
                                            int(items_per_screen_entry.get()),
                                            bgHexVar.get(),
                                            selectedFontHexVar.get(),
                                            deselectedFontHexVar.get(),
                                            bubbleHexVar.get()
                                            ,1,scrollBarWidth=int(scrollBarWidthVar.get()),
                                            showScrollBar=(len(previewGameItemList)/int(items_per_screen_entry.get()))>1,
                                            numScreens=math.ceil(len(previewGameItemList)/int(items_per_screen_entry.get())),
                                            screenIndex=0,fileCounter="1 / " + items_per_screen_entry.get()).resize(preview_size, Image.LANCZOS)
            image4 = generatePilImageVertical(fakeprogressbar,0,
                                            "muxapp",
                                            previewApplicationList[0:int(items_per_screen_entry.get())],
                                            additions_Blank,
                                            int(textPaddingVar.get()),
                                            int(bubblePaddingVar.get()),
                                            int(items_per_screen_entry.get()),
                                            bgHexVar.get(),
                                            selectedFontHexVar.get(),
                                            deselectedFontHexVar.get(),
                                            bubbleHexVar.get()
                                            ,1,scrollBarWidth=int(scrollBarWidthVar.get()),
                                            showScrollBar=(len(previewApplicationList)/int(items_per_screen_entry.get()))>1,
                                            numScreens=math.ceil(len(previewApplicationList)/int(items_per_screen_entry.get())),
                                            screenIndex=0,fileCounter="1 / " + items_per_screen_entry.get()).resize(preview_size, Image.LANCZOS)
        if not(vertical_var.get()):
            image5 = generatePilImageHorizontal(fakeprogressbar,4,bgHexVar.get(),selectedFontHexVar.get(),deselectedFontHexVar.get(),bubbleHexVar.get(),iconHexVar.get(),1).resize(preview_size, Image.LANCZOS)

        if crt_overlay_var.get():
            crt_overlay_resized = crt_overlay_image.resize(image1.size, Image.LANCZOS)
            image1.paste(crt_overlay_resized,(0,0),crt_overlay_resized)
            image2.paste(crt_overlay_resized,(0,0),crt_overlay_resized)
            image3.paste(crt_overlay_resized,(0,0),crt_overlay_resized)
            image4.paste(crt_overlay_resized,(0,0),crt_overlay_resized)
            if not(vertical_var.get()):
                image5.paste(crt_overlay_resized,(0,0),crt_overlay_resized)

        update_image_label(image_label1, image1)
        update_image_label(image_label2, image2)
        update_image_label(image_label3, image3)
        update_image_label(image_label4, image4)
        if not(vertical_var.get()):
            update_image_label(image_label5, image5)
        else:
            remove_image_from_label(image_label5)
        valid_params = True
    except:
        if valid_params:
            redOutlineImage1 = outline_image_with_inner_gap(get_current_image(image_label1)).resize(preview_size, Image.LANCZOS)
            redOutlineImage2 = outline_image_with_inner_gap(get_current_image(image_label2)).resize(preview_size, Image.LANCZOS)
            redOutlineImage3 = outline_image_with_inner_gap(get_current_image(image_label3)).resize(preview_size, Image.LANCZOS)
            redOutlineImage4 = outline_image_with_inner_gap(get_current_image(image_label4)).resize(preview_size, Image.LANCZOS)
            if not(vertical_var.get()):
                redOutlineImage5 = outline_image_with_inner_gap(get_current_image(image_label5)).resize(preview_size, Image.LANCZOS)
            update_image_label(image_label1, redOutlineImage1)
            update_image_label(image_label2, redOutlineImage2)
            update_image_label(image_label3, redOutlineImage3)
            update_image_label(image_label4, redOutlineImage4)
            if not(vertical_var.get()):
                update_image_label(image_label5, redOutlineImage5)
            valid_params = False
    #update_image2()
    # Add your code here to handle the changes


def save_settings():
    config.scrollBarWidthVar = scrollBarWidthVar.get()
    config.textPaddingVar = textPaddingVar.get()
    config.bubblePaddingVar = bubblePaddingVar.get()
    config.itemsPerScreenVar = itemsPerScreenVar.get()
    config.footerHeightVar = footerHeightVar.get()
    config.customFontSizeVar = customFontSizeVar.get()
    config.bgHexVar = bgHexVar.get()
    config.selectedFontHexVar = selectedFontHexVar.get()
    config.deselectedFontHexVar = deselectedFontHexVar.get()
    config.bubbleHexVar = bubbleHexVar.get()
    config.iconHexVar = iconHexVar.get()
    config.remove_brackets_var = remove_brackets_var.get()
    config.remove_square_brackets_var = remove_square_brackets_var.get()
    config.replace_hyphen_var = replace_hyphen_var.get()
    config.also_games_var = also_games_var.get()
    config.move_the_var = move_the_var.get()
    config.crt_overlay_var = crt_overlay_var.get()
    config.alternate_menu_names_var = alternate_menu_names_var.get()
    config.remove_right_menu_guides_var = remove_right_menu_guides_var.get()
    config.remove_left_menu_guides_var = remove_left_menu_guides_var.get()
    config.overlay_box_art_var = overlay_box_art_var.get()
    config.box_art_directory_path = box_art_directory_path.get()
    config.maxBubbleLengthVar = maxBubbleLengthVar.get()
    config.roms_directory_path = roms_directory_path.get()
    config.application_directory_path = application_directory_path.get()
    config.previewConsoleNameVar = previewConsoleNameVar.get()
    config.show_hidden_files_var = show_hidden_files_var.get()
    config.vertical_var = vertical_var.get()
    config.override_bubble_cut_var = override_bubble_cut_var.get()
    config.page_by_page_var = page_by_page_var.get()
    config.override_font_size_var = override_font_size_var.get()
    config.override_folder_box_art_padding_var = override_folder_box_art_padding_var.get()
    config.boxArtPaddingVar = boxArtPaddingVar.get()
    config.folderBoxArtPaddingVar = folderBoxArtPaddingVar.get()
    config.content_alignment_var = content_alignment_var.get()
    config.theme_alignment_var = theme_alignment_var.get()
    config.version_var = version_var.get()
    config.global_alignment_var = global_alignment_var.get()
    config.am_theme_directory_path = am_theme_directory_path.get()
    config.theme_directory_path = theme_directory_path.get()
    config.catalogue_directory_path = catalogue_directory_path.get()
    config.name_json_path = name_json_path.get()
    config.background_image_path = background_image_path.get()
    config.alt_font_path = alt_font_path.get()
    config.use_alt_font_var = use_alt_font_var.get()
    config.themeName = theme_name_entry.get()
    config.amThemeName = am_theme_name_entry.get()
    config.am_ignore_theme_var = am_ignore_theme_var.get()
    config.am_ignore_cd_var = am_ignore_cd_var.get()
    config.advanced_error_var = advanced_error_var.get()
    config.show_file_counter_var = show_file_counter_var.get()
    config.show_console_name_var = show_console_name_var.get()

def load_settings():
    scrollBarWidthVar.set(config.scrollBarWidthVar)
    textPaddingVar.set(config.textPaddingVar)
    bubblePaddingVar.set(config.bubblePaddingVar)
    itemsPerScreenVar.set(config.itemsPerScreenVar)
    footerHeightVar.set(config.footerHeightVar)
    boxArtPaddingVar.set(config.boxArtPaddingVar)
    folderBoxArtPaddingVar.set(config.folderBoxArtPaddingVar)
    customFontSizeVar.set(config.customFontSizeVar)
    bgHexVar.set(config.bgHexVar)
    selectedFontHexVar.set(config.selectedFontHexVar)
    deselectedFontHexVar.set(config.deselectedFontHexVar)
    bubbleHexVar.set(config.bubbleHexVar)
    iconHexVar.set(config.iconHexVar)
    remove_brackets_var.set(config.remove_brackets_var)
    remove_square_brackets_var.set(config.remove_square_brackets_var)
    replace_hyphen_var.set(config.replace_hyphen_var)
    also_games_var.set(config.also_games_var)
    move_the_var.set(config.move_the_var)
    crt_overlay_var.set(config.crt_overlay_var)
    alternate_menu_names_var.set(config.alternate_menu_names_var)
    remove_right_menu_guides_var.set(config.remove_right_menu_guides_var)
    remove_left_menu_guides_var.set(config.remove_left_menu_guides_var)
    overlay_box_art_var.set(config.overlay_box_art_var)
    box_art_directory_path.set(config.box_art_directory_path)
    maxBubbleLengthVar.set(config.maxBubbleLengthVar)
    roms_directory_path.set(config.roms_directory_path)
    application_directory_path.set(config.application_directory_path)
    previewConsoleNameVar.set(config.previewConsoleNameVar)
    show_hidden_files_var.set(config.show_hidden_files_var)
    vertical_var.set(config.vertical_var)
    override_bubble_cut_var.set(config.override_bubble_cut_var)
    override_folder_box_art_padding_var.set(config.override_folder_box_art_padding_var)
    page_by_page_var.set(config.page_by_page_var)
    override_font_size_var.set(config.override_font_size_var)
    version_var.set(config.version_var)
    global_alignment_var.set(config.global_alignment_var)
    theme_alignment_var.set(config.theme_alignment_var)
    content_alignment_var.set(config.content_alignment_var)
    am_theme_directory_path.set(config.am_theme_directory_path)
    theme_directory_path.set(config.theme_directory_path)
    catalogue_directory_path.set(config.catalogue_directory_path)
    name_json_path.set(config.name_json_path)
    background_image_path.set(config.background_image_path)
    alt_font_path.set(config.alt_font_path)
    use_alt_font_var.set(config.use_alt_font_var)
    theme_name_entry.delete(0, tk.END)
    theme_name_entry.insert(0, config.themeName)
    am_theme_name_entry.delete(0, tk.END)
    am_theme_name_entry.insert(0, config.amThemeName)
    am_ignore_theme_var.set(config.am_ignore_theme_var)
    am_ignore_cd_var.set(config.am_ignore_cd_var)
    advanced_error_var.set(config.advanced_error_var)
    show_file_counter_var.set(config.show_file_counter_var)
    show_console_name_var.set(config.show_console_name_var)


config = Config()
load_settings()
consoleMap = getConsoleAssociationList()
menuNameMap = getAlternateMenuNameDict()

# Attach trace callbacks to the variables
scrollBarWidthVar.trace_add("write", on_change)
textPaddingVar.trace_add("write", on_change)
bubblePaddingVar.trace_add("write", on_change)
itemsPerScreenVar.trace_add("write", on_change)
footerHeightVar.trace_add("write", on_change)
boxArtPaddingVar.trace_add("write", on_change)
folderBoxArtPaddingVar.trace_add("write", on_change)
customFontSizeVar.trace_add("write", on_change)
bgHexVar.trace_add("write", on_change)
selectedFontHexVar.trace_add("write", on_change)
deselectedFontHexVar.trace_add("write", on_change)
bubbleHexVar.trace_add("write", on_change)
iconHexVar.trace_add("write", on_change)
remove_brackets_var.trace_add("write", on_change)
remove_square_brackets_var.trace_add("write", on_change)
replace_hyphen_var.trace_add("write", on_change)
also_games_var.trace_add("write", on_change)
show_file_counter_var.trace_add("write", on_change)
show_console_name_var.trace_add("write", on_change)
move_the_var.trace_add("write", on_change)
crt_overlay_var.trace_add("write", on_change)
alternate_menu_names_var.trace_add("write", on_change)
remove_right_menu_guides_var.trace_add("write", on_change)
remove_left_menu_guides_var.trace_add("write", on_change)
overlay_box_art_var.trace_add("write", on_change)
box_art_directory_path.trace_add("write", on_change)
maxBubbleLengthVar.trace_add("write", on_change)
roms_directory_path.trace_add("write", on_change)
application_directory_path.trace_add("write", on_change)
previewConsoleNameVar.trace_add("write", on_change)
show_hidden_files_var.trace_add("write", on_change)
vertical_var.trace_add("write", on_change)
override_bubble_cut_var.trace_add("write", on_change)
override_folder_box_art_padding_var.trace_add("write", on_change)
page_by_page_var.trace_add("write", on_change)
override_font_size_var.trace_add("write", on_change)
version_var.trace_add("write", on_change)
global_alignment_var.trace_add("write", on_change)
content_alignment_var.trace_add("write", on_change)
theme_alignment_var.trace_add("write", on_change)
am_theme_directory_path.trace_add("write", on_change)
theme_directory_path.trace_add("write", on_change)
catalogue_directory_path.trace_add("write", on_change)
name_json_path.trace_add("write", on_change)
background_image_path.trace_add("write", on_change)
am_ignore_theme_var.trace_add("write", on_change)
am_ignore_cd_var.trace_add("write", on_change)
advanced_error_var.trace_add("write", on_change)
use_alt_font_var.trace_add("write", on_change)
alt_font_path.trace_add("write", on_change)



on_change()

# Run the main loop
root.mainloop()