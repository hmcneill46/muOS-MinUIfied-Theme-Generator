![Example Image](https://private-user-images.githubusercontent.com/57508980/348826227-05b15255-9364-420f-a01d-78576d69cf52.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MjEwNzA5MTksIm5iZiI6MTcyMTA3MDYxOSwicGF0aCI6Ii81NzUwODk4MC8zNDg4MjYyMjctMDViMTUyNTUtOTM2NC00MjBmLWEwMWQtNzg1NzZkNjljZjUyLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA3MTUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwNzE1VDE5MTAxOVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTYzNDgxY2YwNTA3NzYyNDY1ZWU1ZmYyYmJmYWNmY2I3Mzk0OTY2OTY1NmUzYjgyNmFiMzJlZmRkNjQxNTgyZTEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.siXJDPHsTd0ES23V5l5q9T0KBe_PkHEc0RhgHI3RPfQ)
# MinUIfied Theme Generator
This script helps you create and customize themes for your muOS system, creating a consistent look and feel across your system. This tool should work on Windows, MacOS and Linux.
![Program Example Image](https://private-user-images.githubusercontent.com/57508980/348826232-77bc6905-69fa-428f-9f23-57de4671b58a.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MjEwNzEwMjMsIm5iZiI6MTcyMTA3MDcyMywicGF0aCI6Ii81NzUwODk4MC8zNDg4MjYyMzItNzdiYzY5MDUtNjlmYS00MjhmLTlmMjMtNTdkZTQ2NzFiNThhLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA3MTUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwNzE1VDE5MTIwM1omWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTVlNzA0NzMyMWY2MGRlMzM4MjI2OGRjOGZiOWJmZjkwMmVmOWVjZjhlNTA4M2NlMjhlZWZjY2Q4NmU3NWM2ZGQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.fUiFdVrXxxR9FXpwo20w-MsIPM6yK-l30sE7RPV2Z4M)

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
 - **Make sure** your box art on your device is set to **middle+front**, otherwise the content explorer UI can behave strangely
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

