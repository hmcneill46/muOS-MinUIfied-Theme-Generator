import requests
import os
import time
import shutil
try:
    from githubToken import GITHUB_TOKEN
except ImportError:
    raise ImportError("Please create a githubToken.py file with your GITHUB_TOKEN.")

def get_console_names_from_github(GITHUB_USER, REPO_NAME, BRANCH, FOLDER_PATH):
    # GitHub API URL to get the contents of the folder
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/{FOLDER_PATH}?ref={BRANCH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # Send the request to the GitHub API
    response = requests.get(url, headers=headers)

    # Check if the response is successful
    if response.status_code == 200:
        # Parse the JSON response
        contents = response.json()
        
        console_names = []

        ini_files = [file_info['name'] for file_info in contents if file_info['name'].endswith(".ini")]
        no_ini_files = len(ini_files)

        # Loop through each .ini file
        current_ini_file = 0
        for file_info in contents:
            if file_info['name'].endswith(".ini"):
                # Get the file content URL
                file_url = file_info['download_url']
                file_response = requests.get(file_url, headers=headers)
                
                # Check if the file content is successfully retrieved
                if file_response.status_code == 200:
                    # Look for the line with "catalogue="
                    for line in file_response.text.splitlines():
                        if line.startswith("catalogue="):
                            console_name = line.split("=", 1)[1].strip()
                            console_names.append(console_name)
                            break
                    current_ini_file += 1
                    print(f"Successfully Processed {file_info['name']}")
                    print(f"Progress: {round(100*(current_ini_file/no_ini_files),2)}% Done")
                else:
                    print(f"Failed to retrieve file content for {file_info['name']}: {file_response.status_code}")
                    print(f"Progress: {round(100*(current_ini_file/no_ini_files),2)}% Done")
        
        return console_names
    else:
        raise Exception(f"Failed to retrieve data: {response.status_code} - {response.text}")
    
def FillRomsFolder(consoles, base_path):
    for console in consoles:
        console_path = os.path.join(base_path, console)
        os.makedirs(console_path, exist_ok=True)
        # add test file to each console folder
        with open(os.path.join(console_path, 'content.txt'), 'w') as f:
            f.write('content')

def main():
    GITHUB_USER = "MustardOS"
    REPO_NAME = "internal"
    BRANCH = "main"
    FOLDER_PATH = "init/MUOS/info/assign"

    console_names = get_console_names_from_github(GITHUB_USER, REPO_NAME, BRANCH, FOLDER_PATH)
    directory_path = os.path.join("Assets", "System Logos", "png [5x]")
    console_name_status = {}

    # ANSI color codes for Found (green) and Missing (red)
    color_found = "\033[92m"  # Green
    color_missing = "\033[91m"  # Red
    reset_color = "\033[0m"  # Reset to default

    base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ROMS')
    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    FillRomsFolder(console_names, base_path)

    # Check the existence of each console's logo
    for console in console_names:
        console_name_status[console] = os.path.exists(os.path.join(directory_path, f"{console}.png"))

    # Separate found and missing consoles
    found_consoles = [n for n, status in console_name_status.items() if status]
    missing_consoles = [n for n, status in console_name_status.items() if not status]

    # Print found consoles with green color
    for n in found_consoles:
        print(f"{n}: {color_found}Found{reset_color}")

    # Print missing consoles with red color
    for n in missing_consoles:
        print(f"{n}: {color_missing}Missing{reset_color}")
    print("Percentage of logos found: ", len(found_consoles) / len(console_names) * 100, "%", "of", len(console_names), "logos found.")

if __name__ == "__main__":
    main()
