MinUI Theme Generator

This script helps you create and customize themes for your MUOS system, creating a consistent look and feel across your gaming library.
Prerequisites

Before running this script, ensure you have the following installed:

    Python
    Pillow library (pip install pillow)
    Tkinter library (pip install tk)

Getting Started

    Insert your SD card into your computer.
    Copy the Folder:
        If you want to keep the box art, copy the MUOS/info/catalogue folder from the SD card.
        To use the tool without the SD card, copy your ROMS folder from the card for future use.

Configuration
Global Configurations

Customize the overall look and feel of the theme. A visual preview will be available to help you see the changes in real-time.
Theme Specific Configurations

Adjust settings that only affect the theme, excluding the content explorer.
Box Art Specific Configurations

    Specify the box art folder copied from your card.
    Adjust text placement to prevent it from overlapping with the box art.
    Set the MUOS console name to see the box art in the preview.

Content Explorer Specific Configurations

    Modify settings specific to the content explorer menus (e.g., removing brackets from game names, generating themes for games and folders).

Generation

After configuring your settings, you can generate the theme. There are three methods to do this:

    Archive Manager [Recommended for refried beans or later]
        Set the output directory for the Archive Manager (leave blank to generate files in the script's directory).
        Optionally, choose to generate only the theme or content explorer files.

    Theme Only
        Specify the theme output directory (can be on the SD card, your computer, or leave blank to generate in the script's directory).

    Content Explorer Only
        Select the catalogue folder where the image files will be generated (recommended to back up the folder before this step).

For all methods, click "Generate" and the program will handle the rest.
Removing MinUI Theming

To remove all MinUI theming from your system:

    Choose a different theme in MUOS.
    Use this tool, input your catalogue folder, and press 'Remove all images in Selected Catalogue Folder'.
        Note: This will also remove any box art, so make sure to copy your backup back onto the card afterwards.

Experimental Settings

Generating images for the game list is experimental. It may not work with arcade names and can sometimes cause sorting issues.
