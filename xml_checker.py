import xml.etree.ElementTree as ET
import os
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
            if file_name.endswith(('.xml')):
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
    Tk().withdraw()  # Hide the root Tkinter window
    directory = askdirectory(title="Select Directory to Check XML Files")
    return directory

if __name__ == "__main__":
    # Open a file browser to select the directory
    directory = select_directory()
    
    if directory:
        check_files_in_directory(directory)
    else:
        print("No directory was selected.")
