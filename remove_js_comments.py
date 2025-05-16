import os
import re


def remove_js_comments(input_path, output_path):
    # Read the original JS file
    with open(input_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Regex to remove single-line and multi-line comments
    comment_pattern = r'//.*?$|/\*.*?\*/'
    cleaned_content = re.sub(comment_pattern, '', content,
                             flags=re.DOTALL | re.MULTILINE)

    # Ensure that there is at most one empty line between code lines
    cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)

    # Write the cleaned content to the new file
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_content)

    print(f"File saved to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Remove comments from a JS file and ensure single spacing between code lines.")
    parser.add_argument("input_file", help="Path to the input JS file")
    parser.add_argument("output_file", help="Path to the output JS file")

    args = parser.parse_args()

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)

    remove_js_comments(args.input_file, args.output_file)
