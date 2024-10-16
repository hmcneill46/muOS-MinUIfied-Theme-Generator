import re
import os
from colorama import Fore, Style, init

# Initialize colorama (not needed for file output but kept for consistency)
init(autoreset=True)

def find_unique_brackets_with_examples(file_path, output_file_path):
    # Read the contents of the file and split it into lines
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Dictionary to store unique items and the first line where they appear
    unique_items_with_examples = {}
    item_occurrences = {}

    # Regex pattern to find items within curly brackets
    pattern = re.compile(r'\{(.*?)\}')

    # Iterate through each line and look for items in curly brackets
    for line_num, line in enumerate(lines, 1):
        items_in_line = pattern.findall(line)
        for item in items_in_line:
            # If the item is not already in the dictionary, add it with the current line
            if item not in unique_items_with_examples:
                unique_items_with_examples[item] = line.strip()

            # Store all occurrences of the item along with line number
            if item not in item_occurrences:
                item_occurrences[item] = []
            item_occurrences[item].append((line_num, line.strip()))

    # Sort the unique items alphabetically by their keys (i.e., the items in curly brackets)
    sorted_items = sorted(unique_items_with_examples.items())

    # Write the output to the specified file
    with open(output_file_path, 'w') as output_file:
        # Step 1: Write the unique items and the first line they appeared on
        output_file.write("Summary of unique items and an example:\n")
        for item, example in sorted_items:
            highlighted_example = example.replace(f"{{{item}}}", f"{{{item}}}")  # No color in file
            output_file.write(f"{highlighted_example}\n")
        
        # Step 2: Write each unique item and all lines where it appears
        output_file.write("\nDetailed occurrences for each item:\n")
        for item, occurrences in item_occurrences.items():
            # Write the item in curly brackets
            output_file.write(f"\n{{{item}}}\n")
            # Write each occurrence of the item in the file, with padded line numbers
            for line_num, line in occurrences:
                output_file.write(f"Line {str(line_num).zfill(3)}: {line}\n")

# Example usage:
if __name__ == "__main__":
    file_path = os.path.join("Template Scheme", "template.txt")  # Path to the input file
    output_file_path = os.path.join("Helper Scripts", "Curly Bracket Info.txt")  # Path to the output file
    
    # Call the function to process and write the results to the external file
    find_unique_brackets_with_examples(file_path, output_file_path)
