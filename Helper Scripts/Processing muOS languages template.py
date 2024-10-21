import requests
import json

# GitHub API base URL for the repository
REPO_OWNER = "MustardOS"
REPO_NAME = "internal"
BRANCH = "main"
FOLDER_PATH = "init/MUOS/language"

# GitHub API URL for listing contents of the 'language' folder
BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FOLDER_PATH}?ref={BRANCH}"

def get_json_files_from_github():
    # Send a GET request to fetch the contents of the folder
    response = requests.get(BASE_URL)
    
    # Raise an error if the request was not successful
    response.raise_for_status()
    
    # Parse the response JSON
    files = response.json()

    # Loop through the files and filter for .json files
    json_files = [file for file in files if file['name'].endswith('.json')]
    
    return json_files

def process_json_file(file_url):
    # Send a request to fetch the raw content of the JSON file
    response = requests.get(file_url)
    
    # Raise an error if the request was not successful
    response.raise_for_status()
    
    # Parse the JSON content
    json_content = response.json()
    
    # Example processing: print the file name and content
    print(f"Processing {file_url}...")
    print(json.dumps(json_content, indent=2))  # Pretty print the JSON

def main():
    # Get the list of JSON files from the GitHub repository
    json_files = get_json_files_from_github()
    
    print(f"Found {len(json_files)} JSON files.")

    for file in json_files:
        file_url = file['download_url']
        file_name = file['name']
        print(f"{file_name}: {file_url}")
    
    # Loop through each file and process it
    """for file in json_files:
        file_url = file['download_url']  # Get the direct URL to download the file
        process_json_file(file_url)"""

if __name__ == "__main__":
    main()
