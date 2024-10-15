import re
import os

def find_unique_brackets(file_path):
    # Read the contents of the file
    with open(file_path, 'r') as file:
        content = file.read()

    # Use regex to find all occurrences of text within curly brackets
    items_in_brackets = re.findall(r'\{(.*?)\}', content)

    # Convert to a set to get unique items, then sort them alphabetically
    unique_items = sorted(set(items_in_brackets))

    return unique_items

# Example usage:
if __name__ == "__main__":
    file_path = os.path.join("Template Scheme","template.txt")
    unique_items = find_unique_brackets(file_path)
    
    # Print the unique items
    for item in unique_items:
        print(f"{{{item}}}")
