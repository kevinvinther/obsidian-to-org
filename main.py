#!/usr/bin/env python3
import argparse  # For command-line argument parsing
import re  # Regular expressions, for finding when the YAML begins and ends in markdown
import yaml  # For yaml in markdown files


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
        + file_name.replace(" ", "_")
    )


def parse_commandline_arguments():
    parser = argparse.ArgumentParser(
        description="Program to parse command-line arguments."
    )
    parser.add_argument("input_folder", help="Your Obsidian Vault")
    parser.add_argument(
        "output_folder", help="The Folder which The Org Files will Output To"
    )
    parser.add_argument(
        "--print-output", help="Print the output of the files", action="store_true"
    )
    parser.add_argument(
        "--print-progress", help="Print progress of the files", action="store_true"
    )
    parser.add_argument(
        "--math",
        help="Give each Org file the option to automatically show math equations",
        action="store_true",
    )

    args = parser.parse_args()

    if args.print_output:
        print("Input folder:", args.input_folder)
        print("Output folder:", args.output_folder)
        print("Math equations option:", args.math)
        print("print-progress", args.print_progress)
        print("print-output:", args.print_output)


"""
obsidian-to-org
---------------

This program converts an obsidian vault to org-roam format org-mode files.

org-roam format
---------------
Filename will be: yyyymmddhhmmss-{obsidian-file-name}
Where yyyymmddhhmmss will be taken from markdown YAML data.


arguments
---------
TODO: set arguments
"""
if __name__ == "__main__":
    parse_commandline_arguments()
