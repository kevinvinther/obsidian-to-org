#!/usr/bin/env python3
import argparse  # For command-line argument parsing
import re  # Regular expressions, for finding when the YAML begins and ends in markdown
import yaml  # For yaml in markdown files
import pypandoc  # Convert from markdown to org
import os  # Traverse all files


def get_yaml_data(file_path):
    """Get the YAML data from a Markdown file."""
    with open(file_path, "r") as file:
        content = file.read()
        yaml_data = re.findall(r"(?<=---\n).*(?=\n---)", content, re.DOTALL)[0]
        return yaml.load(yaml_data, Loader=yaml.FullLoader)


def get_org_roam_file_name(yaml_data, file_name):
    """Convert datetime.date to proper org-roam format."""
    return (
        yaml_data["created"].strftime("%Y%m%d%H%M%S")
        + "-"
        + file_name.replace(" ", "_").lower().rstrip(".md")
        + ".org"
    )


def convert_to_org(file_path, output_path):
    """Convert file from markdown to org and print location."""
    pypandoc.convert_file(file_path, "org", outputfile=output_path)
    print(file_path + " -> " + output_path)


def add_alias(aliases, org_file):
    """Add alias to org files."""
    formatted_aliases = [f'"{alias}"' for alias in aliases]

    with open(org_file, "r") as f:
        lines = f.readlines()
    with open(org_file, "w") as f:
        for i, line in enumerate(lines):
            if line.startswith(":ID:"):
                lines.insert(i + 1, f':ROAM_ALIASES: {" ".join(formatted_aliases)}\n')
                break
        f.write("".join(lines))


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
    print(org_file + " now has startup property latexpreview.")


def parse_commandline_arguments():
    """Parse the commandline arguments."""
    parser = argparse.ArgumentParser(
        description="Convert your Obsidian vault to Org-roam compatible org-files."
    )
    parser.add_argument("input_folder", help="Your Obsidian Vault (Remember to Backup)")
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


if __name__ == "__main__":
    args = parse_commandline_arguments()
    for filename in os.listdir(args.input_folder):
        filepath = os.path.join(args.input_folder, filename)
        if os.path.isfile(filepath):
            # Do something with the file
            if is_markdown_file(filename):
                file_yaml = get_yaml_data(filepath)
                new_path = args.output_folder + get_org_roam_file_name(
                    file_yaml, filename
                )
                convert_to_org(filepath, new_path)
                if hasattr(file_yaml, "aliases"):
                    if len(file_yaml.aliases) >= 1:
                        add_alias(file_yaml.aliases, new_path)
                if args.math:
                    add_math(new_path)

        elif os.path.isdir(filepath):
            # Recursively traverse subdirectories
            for subfilename in os.listdir(filepath):
                subfilepath = os.path.join(filepath, subfilename)
                if os.path.isfile(subfilepath):
                    # Do something with the file
                    if is_markdown_file(filename):
                        file_yaml = get_yaml_data(filepath)
                        new_path = args.output_folder + get_org_roam_file_name(
                            file_yaml, filename
                        )
                        convert_to_org(filepath, new_path)
                        add_alias(file_yaml.aliases, new_path)
                        if args.math:
                            add_math(new_path)
