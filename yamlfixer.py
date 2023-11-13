import re
import os

def adjust_comment_indentation(lines):
    new_lines = []
    for i, line in enumerate(lines):
        stripped_line = line.lstrip()
        if stripped_line.startswith("#"):
            next_line_index = i + 1
            # Find the next non-empty line to determine the indentation
            while next_line_index < len(lines) and not lines[next_line_index].strip():
                next_line_index += 1
            if next_line_index < len(lines):
                # Get the number of leading spaces in the next non-comment line
                next_line_indentation = len(lines[next_line_index]) - len(lines[next_line_index].lstrip())
                # Apply same indentation to comment
                line = " " * next_line_indentation + stripped_line
        new_lines.append(line)
    return new_lines

def process_yaml_files(directory, file_extension=".yaml"):
    for filename in os.listdir(directory):
        if filename.endswith(file_extension):
            filepath = os.path.join(directory, filename)
            
            # Read the contents of the file
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Normalize line endings to Unix style and strip trailing spaces
            lines = [line.rstrip() + '\n' for line in lines]

            # Ensure document start marker
            if lines and not lines[0].strip().startswith('---'):
                lines.insert(0, '---\n')

            # Adjust comment indentation
            lines = adjust_comment_indentation(lines)

            # Remove excess blank lines throughout the file
            lines = [line for i, line in enumerate(lines) if i == 0 or not (line.isspace() and lines[i - 1].isspace())]

            # Write the changes back to the file
            with open(filepath, 'w', encoding='utf-8') as file:
                file.writelines(lines)

            print(f"Processed {filename}")

# Define the path to your directory containing YAML files
yaml_directory = "/home/marc/Downloads/nodes/"  # Replace with your directory path

# Run the function on your directory
process_yaml_files(yaml_directory)

