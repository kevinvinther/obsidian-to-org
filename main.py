#!/usr/bin/env python3
"""Convert your Obsidian vault to Org-roam compatible org-files."""
# For command - line argument parsing
import argparse
# Multiprocessing
import multiprocessing as mp
# Traverse all files
import os
# Regular expressions, for finding when the YAML begins and ends in markdown
import re

# Convert from markdown to org
import pypandoc
# For yaml in markdown files
import yaml


def get_yaml_data(file_path):
    """Get the YAML data from a Markdown file."""
    with open(file_path, "r") as file:
        content = file.read()
        yaml_data = re.findall(r"(?<=---\n).*?(?=\n---)", content, re.DOTALL)[0]
        return yaml.load(yaml_data, Loader=yaml.FullLoader)


def get_org_roam_file_name(yaml_data, file_name):
    """Convert datetime.date to proper org-roam format."""
    return (
        yaml_data["created"].strftime("%Y%m%d%H%M%S")
        + "-"
        + file_name.replace(" ", "_").lower().replace(".md", "")
        + ".org"
    )


def construct_header(yaml):
    """Construct the header for the org file."""
    if yaml["aliases"] is not None and None not in yaml["aliases"]:
        if len(yaml["aliases"]) >= 1:
            alias = get_aliases_roam_format(yaml["aliases"])
        else:
            alias = ""
    else:
        alias = ""

    result = """:PROPERTIES:
:ID:    {}
:ROAM_ALIASES: {}
:END:\n""".format(
        yaml["title"].lower().replace(" ", "-").rstrip(".md"), alias
    )
    return result


def convert_to_org(file_path, output_path):
    """Convert file from markdown to org and print location."""
    pypandoc.convert_file(
        file_path, "org", outputfile=output_path, extra_args=["--wrap=none"]
    )
    print(file_path + " -> " + output_path)


def convert_dict_to_string(alias_dict):
    """Convert a dictionary to a string."""
    return ", ".join(f'"{key}: {value}"' for key, value in alias_dict.items())


def get_aliases_roam_format(aliases):
    """Create a string for aliases property."""
    # I apologize for these lines
    # If the alias is a dictionary, convert it to a string
    # If the alias is a string, check if it has spaces, if so, add quotes
    # If the alias is a string without spaces, leave it as is
    formatted_aliases = [
        convert_dict_to_string(alias)
        if isinstance(alias, dict)
        else (f'"{alias}"' if " " in alias else alias)
        for alias in aliases
    ]
    print(formatted_aliases)
    return f'{" ".join(formatted_aliases)}'


def add_math(org_file):
    """Add #+STARTUP: latexpreview to org_file header."""
    with open(org_file, "r") as f:
        lines = f.readlines()
    with open(org_file, "w") as f:
        for i, line in enumerate(lines):
            if line.startswith(":END:"):
                lines.insert(i + 1, "#+STARTUP: latexpreview\n")
                break
        f.write("".join(lines))


def add_tags(org_file, yaml):
    """Add tags to org_file header."""
    if yaml is None or yaml["tags"] is None or not yaml["tags"] or None in yaml["tags"]:
        return
    with open(org_file, "r") as f:
        lines = f.readlines()
    with open(org_file, "w") as f:
        for i, line in enumerate(lines):
            if line.startswith(":END:"):
                output = "#+filetags: :" + ":".join(yaml["tags"]) + ":"
                print(output)
                lines.insert(i + 1, f"{output}\n")
                break
        f.write("".join(lines))


def parse_commandline_arguments():
    """Parse the commandline arguments."""
    parser = argparse.ArgumentParser(
        description="""Convert your Obsidian vault to
                        Org-roam compatible org-files."""
    )
    parser.add_argument(
        "input_folder",
        help="Your Obsidian Vault (Remember to Backup)",
    )
    parser.add_argument(
        "output_folder", help="The Folder which The Org Files will Output To"
    )
    parser.add_argument(
        "--math",
        help="Adds #+STARTUP: latexpreview to headers of all files.",
        action="store_true",
    )
    # Maybe sometime add a --math-all, such that we take all, otherwise only
    # those with math equations?

    return parser.parse_args()


def is_markdown_file(filename):
    """Return true if file is a markdown file."""
    _, ext = os.path.splitext(filename)
    return ext.lower() in [".md", ".markdown"]


def remove_properties(file_path):
    """Remove properties from org file."""
    with open(file_path, "r") as f:
        file_text = f.read()
    # find all occurrences of :PROPERTIES: and :END:
    start = file_text.find(":PROPERTIES:")
    end = file_text.find(":END:")
    while start != -1 and end != -1:
        # remove the text between :PROPERTIES: and :END:
        file_text = file_text[:start] + file_text[end + 5 :]
        # find the next occurrence of :PROPERTIES: and :END:
        start = file_text.find(":PROPERTIES:")
        end = file_text.find(":END:")
    with open(file_path, "w") as f:
        f.write(file_text)


def add_string_to_file_start(file_path, new_string):
    """Add string to start of file."""
    with open(file_path, "r") as f:
        file_text = f.read()

    file_text = file_text.strip()
    # Concatenate the new string with the contents of the file
    updated_text = new_string + file_text
    with open(file_path, "w") as f:
        f.write(updated_text)


def convert_wikilinks_to_org_links(file_path):
    """Convert wikilinks to org links."""
    with open(file_path, "r") as f:
        file_text = f.read()

    # Regular expression pattern for wikilinks with and without aliases
    pattern = r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]"

    def link_replacer(match):
        link_id = match.group(1).replace(" ", "-").lower()
        link_text = match.group(2) if match.group(2) else match.group(1)
        return f"[[id:{link_id}][{link_text}]]"

    # Replace wikilinks with org links using a custom replacement function
    file_text = re.sub(pattern, link_replacer, file_text)

    # Write the updated file text back to the file
    with open(file_path, "w") as f:
        f.write(file_text)


def process_file(filename, args):
    """Process a file."""
    filepath = os.path.join(args.input_folder, filename)
    if os.path.isfile(filepath):
        # Convert!
        if is_markdown_file(filename):
            file_yaml = get_yaml_data(filepath)
            new_path = args.output_folder + get_org_roam_file_name(file_yaml, filename)
            convert_to_org(filepath, new_path)
            remove_properties(new_path)
            add_string_to_file_start(
                new_path, ("#+title: " + file_yaml["title"] + "\n")
            )
            add_string_to_file_start(new_path, construct_header(file_yaml))
            add_tags(new_path, file_yaml)
            if args.math:
                add_math(new_path)
            convert_wikilinks_to_org_links(new_path)

    elif os.path.isdir(filepath):
        # Recursively traverse subdirectories
        for subfilename in os.listdir(filepath):
            process_file(subfilename, args)


def process_file_wrapper(args):
    """Wrap process_file to allow for multiprocessing."""
    return process_file(*args)


if __name__ == "__main__":
    args = parse_commandline_arguments()
    filenames = os.listdir(args.input_folder)

    # Using multiprocessing Pool
    with mp.Pool(processes=mp.cpu_count()) as pool:
        pool.map(process_file_wrapper, [(filename, args) for filename in filenames])
