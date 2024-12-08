import requests
import re
import os
try:
    from githubToken import GITHUB_TOKEN
except ImportError:
    raise ImportError("Please create a githubToken.py file with your GITHUB_TOKEN.")

# GitHub repository details

BANCH_MAP = {"Banana": "e81f65f9b883412ccaf9651a96dd921cbfd7df4b",
             "Current": "main"}

REPO_OWNER = "MustardOS"
REPO_NAME = "frontend"
BRANCH = BANCH_MAP["Current"]
BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/module"

# Regex pattern for capturing the last item
pattern = re.compile(r'apply_theme_list_glyph\(&theme, [^,]+, mux_module, "([^"]+)"\);')

def get_repo_contents(path=""):
    """Fetch the contents of a specified path in the repository."""
    url = f"{BASE_URL}/{path}?ref={BRANCH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    print(f"Fetching contents of: {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def process_main_c(file_url):
    """Process the main.c file to find matches using regex."""
    print(f"Processing main.c file at: {file_url}")
    response = requests.get(file_url)
    response.raise_for_status()
    content = response.text
    matches = pattern.findall(content)
    print(f"Found matches: {matches}")
    return matches

def main():
    output_file_path = os.path.join('Helper Scripts','MenuItemsGenerator' ,'screen_items_output.txt')

    with open(output_file_path, "w") as output_file:
        # Get the contents of the root of the repository
        root_contents = get_repo_contents()

        for item in root_contents:
            # Check if the item is a folder
            if item["type"] == "file":
                file_name = item["name"]
                print(f"Checking file: {file_name}")

                c_file =  file_name[-2:] == ".c"

                if c_file:
                    print(f"Found .c file: {file_name}")
                    
                    # Process main.c and find regex matches
                    matches = process_main_c(item["download_url"])

                    # Write the screen name and matched groups to the output file
                    print(f"Writing matches for {file_name[:-2]} to output file.")
                    output_file.write(f"Screen: {file_name[:-2]}\n")
                    output_file.write("Items:\n")
                    output_file.write("[")
                    for match in matches:
                        output_file.write(f'"{match}"')
                        if match != matches[-1]:
                            output_file.write(", ")
                    output_file.write("]\n")
                    output_file.write("\n")
                    if not matches:
                        print(f"No matches found in main.c for {file_name[:-2]}.")
                else:
                    print(f"No main.c file found in folder: {file_name[:-2]}")

    # Verify if output was successfully saved
    if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
        print(f"Output saved to {output_file_path}")
    else:
        print("No output generated; the file is empty.")

if __name__ == "__main__":
    main()
