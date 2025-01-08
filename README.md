# MinUIfied Theme Generator for muOS Systems
This script helps you create and customize themes for your muOS system, creating a consistent look and feel across your system. This tool should work on Windows, MacOS and Linux.

<div style="display: flex; justify-content: space-between; gap: 0%; width: 100%;">
  <img src="https://github.com/user-attachments/assets/68cfb45d-b260-4fa0-bab1-b13a6d7d282a" alt="Themes Example Image" style="width: 61%; object-fit: contain;"/>
  <img src="https://github.com/user-attachments/assets/e3c42ffc-cba3-4898-bc8e-86fe90e24204" alt="Program Example Image" style="width: 38%; object-fit: contain;"/>
</div>





## If you just want a Pre-made Theme and don't want to customise it with the script:
[Follow this link for a page of themes **Without** grid mode](https://hmcneill46.github.io/muOS-MinUIfied-Theme-Generator/Theme-Gallery/)

[Follow this link for a page of themes **With** grid mode](https://hmcneill46.github.io/muOS-MinUIfied-Theme-Generator/Grid-Theme-Gallery/)

## Prerequisites for running from Downloaded Binary [Windows]:
 - None

## Prerequisites for running the script from source
Before running this script, ensure you have the following installed:
 - Python (Tested with version 3.12)
 - All Required Required Python Libraries
 
       python3 -m pip install -r requirements.txt 

Individual Libraries:
 - Pillow library
   
       pip install pillow
 - Tkinter library
   
       pip install tk

 - python-bidi library
   
       pip install python-bidi

 - numpy library
   
       pip install numpy
   
 ### For Debian Linux:
```
apt install python3-pil.imagetk python3-pil python3-bidi python3-tk python3-numpy
```


## Getting Started
 - To run the program from the prebuilt binaries, go to the [latest release](https://github.com/hmcneill46/muOS-MinUIfied-Theme-Generator/releases/latest) and download the program from the assets. [Windows Only]
 - To run the program from source you must download this repo as a zip, unzip it, (or clone it), and then run the .py file with python

# Configuration

## Global Configurations
Customize the overall look and feel of the theme. A visual preview will be available to help you see the changes in real-time.

## Theme Specific Configurations
More Visual changes for the theme.

## Box Art Specific Configurations
This is not implimented yet (16/10/2024) but it will be to set a size of your box art so that the text wont go behind it.

## Content Explorer Specific Configurations
This is not implimented yet (16/10/2024) but it will be so that you can do something like having your game names show centerally justified, and everything else left.

# Generation
After configuring your settings, you can generate the theme.

Specify the theme output directory (can be on the SD card, your computer, or **leave blank to generate in the script's directory**).

**click "Generate" and the program will handle the rest.**


Choose a different theme in muOS.

# In case of bricked system due to broken theme
Please go into your MUOS/theme/active folder and remove everything in there, your system should now boot and you can choose a different (not broken) theme

# Build instructions

 - Install pyinstaller


       pip install pyinstaller
 - To build, run*:


       pyinstaller ".\Custom MinUI Theme Generator for muOS.spec"
*where the .spec file is the one in the github page, modify the .spec file to work on macOS and Linux if you are able to/want to, and put it on a PR.

## Credits and thanks
 - Thanks to [Shaun Inman](https://github.com/shauninman) for creating [MinUI](https://github.com/shauninman/MinUI), which this muOS theme is trying to emulate the look of
 - Thanks to [@JCR64](https://github.com/JCR64) for the inspiration for the theme and horizontal logo
 - Credits and thanks to [@GrumpyGopher](https://github.com/GrumpyGopher) for the work he's put into making the project better
 - Thanks to [@damagedspline](https://github.com/damagedspline) for the Hebrew translation file

**muOS Discord Server:** https://discord.gg/USS5ybVtDz

**Where to talk about this project:** https://discord.com/channels/1152022492001603615/1253933788078014586
