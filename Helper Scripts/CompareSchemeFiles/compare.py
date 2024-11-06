import difflib
from colorama import init, Fore, Style
import os

# Initialize colorama for cross-platform color support
init(autoreset=True)

def strip_values(file_path):
    """Reads a file and returns a list of lines with values after '=' removed."""
    stripped_lines = []
    with open(file_path, 'r') as file:
        for line in file:
            if '=' in line:
                key = line.split('=')[0]
                stripped_line = f"{key}=\n"
                stripped_lines.append(stripped_line)
            else:
                stripped_lines.append(line)
    return stripped_lines

def compare_files(file1_path, file2_path):
    """Strips values after '=' and compares two files, outputting their diff with color."""
    stripped_file1 = strip_values(file1_path)
    stripped_file2 = strip_values(file2_path)
    
    # Generate the diff
    diff = difflib.unified_diff(
        stripped_file1, stripped_file2,
        fromfile=file1_path, tofile=file2_path,
        lineterm=''
    )

    # Display diff with colors
    for line in diff:
        if line.startswith('-'):
            print(Fore.RED + line)  # Red for removed lines
        elif line.startswith('+'):
            print(Fore.GREEN + line)  # Green for added lines
        elif line.startswith('@@'):
            print(Fore.CYAN + line)  # Cyan for line numbers
        else:
            print(Style.RESET_ALL + line)  # Normal text for unchanged lines

# Example usage
generatedSchemeFile = os.path.join('Helper Scripts','Generate Scheme File From Source','Default Scheme File.txt')
currentUsingSchemeFile = os.path.join('Template Scheme', 'template.txt')
compare_files(currentUsingSchemeFile,generatedSchemeFile)
