# MinUIfied Theme Generator for muOS Systems
This script helps you create and customize themes for your muOS system, creating a consistent look and feel across your system. This tool should work on Windows, MacOS and Linux.

![Themes Example Image](https://github.com/user-attachments/assets/68cfb45d-b260-4fa0-bab1-b13a6d7d282a)

![Program Example Image](https://github.com/user-attachments/assets/e3c42ffc-cba3-4898-bc8e-86fe90e24204)
## Prerequisites

Before running this script, ensure you have the following installed:

 

 - Python (Tested with version 3.12)
 - Pillow library
   
       pip install pillow
 - Tkinter library
   
       pip install tk

  

## Getting Started

 - Insert your SD card into your computer.
 - If you want to keep the **box art**, copy the **MUOS/info/catalogue** folder from the SD card to your computers local storage
   
 - To use the tool without the SD card, copy your **ROMS** folder from the card to your computers local storage for future use.
 - **Make sure** your box art on your device is set to **fullscreen+front**, otherwise the content explorer UI can behave strangely
 - To run the program you must download this repo as a zip, unzip it, and then run the .py file with python

# Configuration

## Global Configurations
Customize the overall look and feel of the theme. A visual preview will be available to help you see the changes in real-time.

## Theme Specific Configurations
Adjust settings that only affect the theme (excluding the content explorer).

## Box Art Specific Configurations
Specify the box art folder copied from your card.

Adjust text placement to prevent it from overlapping with the box art.

Set the muOS console name to see the box art in the preview.

## Content Explorer Specific Configurations
Modify settings specific to the content explorer menus (e.g., removing brackets from game names, generating themes for games and folders).

  

# Generation
After configuring your settings, you can generate the theme. There are three methods to do this:

## Archive Manager [Recommended for refried beans or later]

 1. Set the output directory for the Archive Manager (leave blank to generate files in the script's directory).
    
 2. Optionally, choose to generate only the theme or content explorer files.

  

## Theme Only

Specify the theme output directory (can be on the SD card, your computer, or **leave blank to generate in the script's directory**).

  

## Content Explorer Only

Select the catalogue folder where the image files will be generated (recommended to back up the folder before this step).

  

**For all methods, click "Generate" and the program will handle the rest.**

## Removing MinUI Theming

  

To remove all MinUI theming from your system:

 - Choose a different theme in muOS.
 - Use this tool, input your catalogue folder, and press 'Remove all images in Selected Catalogue Folder'.

**Note: This will also remove any box art, so make sure to copy your backup back onto the card afterwards.**

  

## Experimental Settings
 - Show hidden files is experimental as I'm not sure how it should work if you don't select to generate game list as well
 - Also Generate Images for Game List is experimental as it will mess up your favourites and history menus

