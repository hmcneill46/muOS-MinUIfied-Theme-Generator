import requests
import os
try:
    from githubToken import GITHUB_TOKEN
except ImportError:
    raise ImportError("Please create a githubToken.py file with your GITHUB_TOKEN.")



GITHUB_USER = "MustardOS"
REPO_NAME = "internal"
BRANCH = "main"
FOLDER_PATH = "init/MUOS/info/assign"

def get_console_names_from_github():
    # GitHub API URL to get the contents of the folder
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/{FOLDER_PATH}?ref={BRANCH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # Send the request to the GitHub API
    response = requests.get(url, headers=headers)

    # Check if the response is successful
    if response.status_code == 200:
        # Parse the JSON response
        contents = response.json()
        
        # Collect .ini filenames
        console_names = [file_info['name'][:-4] for file_info in contents if file_info['name'].endswith(".ini")]

        # Display the filenames
        return(console_names)
    else:
        raise Exception(f"Failed to retrieve data: {response.status_code} - {response.text}")
# Run the function to get the latest filenames

def main():
    console_names = get_console_names_from_github()
    directory_path = os.path.join("Assets", "System Logos", "png [5x]")
    console_name_status = {}

    # ANSI color codes for Found (green) and Missing (red)
    color_found = "\033[92m"  # Green
    color_missing = "\033[91m"  # Red
    reset_color = "\033[0m"  # Reset to default

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


if __name__ == "__main__":
    main()