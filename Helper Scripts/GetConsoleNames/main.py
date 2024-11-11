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

def get_filenames_from_github():
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
        ini_files = [file_info['name'][:-4] for file_info in contents if file_info['name'].endswith(".ini")]

        # Display the filenames
        print("List of .ini files in the specified directory:")
        for filename in ini_files:
            print(filename)

        # Optionally, save to a file
        output_file_path = os.path.join('Helper Scripts','GetConsoleNames' ,'system_ini_files.txt')
        with open(output_file_path, "w") as file:
            file.write("\n".join(ini_files))
        print(f"\nFilenames saved to {output_file_path}")
        
    else:
        print(f"Failed to retrieve data: {response.status_code} - {response.text}")

# Run the function to get the latest filenames
get_filenames_from_github()
