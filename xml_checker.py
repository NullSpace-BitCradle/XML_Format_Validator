import argparse
import os
import sys
import xml.etree.ElementTree as ET
from tkinter import Tk
from tkinter.filedialog import askdirectory


def check_xml_format(file_path):
    """
    Check if an XML file is well-formed.
    """
    try:
        # Attempt to parse the XML file
        ET.parse(file_path)
        return True
    except ET.ParseError as e:
        print(f"{file_path}: XML is not well-formed. Error: {e}")
        return False
    except Exception as e:
        print(f"{file_path}: Unexpected error: {e}")
        return False

def check_files_in_directory(directory):
    """
    Recursively check all XML files in a directory and its subdirectories.
    """
    bad_files = []
    
    # Traverse the directory and subdirectories
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.lower().endswith('.xml'):
                file_path = os.path.join(root, file_name)
                if not check_xml_format(file_path):
                    bad_files.append(file_path)
    
    if bad_files:
        print("\nThe following files are not well-formed:")
        for bad_file in bad_files:
            print(bad_file)
    else:
        print("All XML files are well-formed.")

def select_directory():
    """
    Open a folder browser window to select a directory.
    """
    root = Tk()
    root.withdraw()
    try:
        directory = askdirectory(title="Select Directory to Check XML Files")
        return directory or ""
    finally:
        root.destroy()


def main():
    parser = argparse.ArgumentParser(
        description="Validate XML well-formedness in a directory."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        help="Directory to scan (opens folder browser if not provided)",
    )
    args = parser.parse_args()

    if args.directory:
        if not os.path.isdir(args.directory):
            print(f"Error: '{args.directory}' is not a valid directory.", file=sys.stderr)
            sys.exit(1)
        check_files_in_directory(args.directory)
    else:
        directory = select_directory()
        if directory:
            check_files_in_directory(directory)
        else:
            print("No directory was selected.")


if __name__ == "__main__":
    main()
