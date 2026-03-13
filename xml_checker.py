import argparse
import os
import sys
import xml.etree.ElementTree as ET


def check_xml_format(file_path):
    """
    Check if an XML file is well-formed.
    """
    try:
        ET.parse(file_path)
        return True
    except ET.ParseError as e:
        print(f"{file_path}: XML is not well-formed. Error: {e}")
        return False
    except Exception as e:
        print(f"{file_path}: Unexpected error: {e}")
        return False


def validate_xml_schema(file_path, schema):
    """
    Validate an XML file against an XSD schema using lxml.
    Returns True if valid, False otherwise.
    """
    from lxml import etree

    try:
        doc = etree.parse(file_path)
        if schema.validate(doc):
            return True
        else:
            for error in schema.error_log:
                print(f"{file_path}: Schema validation error: {error.message} (line {error.line})")
            return False
    except etree.XMLSyntaxError as e:
        print(f"{file_path}: XML is not well-formed. Error: {e}")
        return False
    except Exception as e:
        print(f"{file_path}: Unexpected error: {e}")
        return False


def load_schema(schema_path):
    """
    Load an XSD schema file and return a compiled schema object.
    """
    from lxml import etree

    try:
        schema_doc = etree.parse(schema_path)
        return etree.XMLSchema(schema_doc)
    except etree.XMLSyntaxError as e:
        print(f"Error: Schema file is not well-formed XML: {e}", file=sys.stderr)
        sys.exit(1)
    except etree.XMLSchemaParseError as e:
        print(f"Error: Invalid XSD schema: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading schema '{schema_path}': {e}", file=sys.stderr)
        sys.exit(1)


def check_files_in_directory(directory, schema=None):
    """
    Recursively check all XML files in a directory and its subdirectories.
    If a schema is provided, validates against it; otherwise checks well-formedness only.
    """
    bad_files = []
    file_count = 0

    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.lower().endswith('.xml'):
                file_path = os.path.join(root, file_name)
                file_count += 1
                if schema:
                    if not validate_xml_schema(file_path, schema):
                        bad_files.append(file_path)
                else:
                    if not check_xml_format(file_path):
                        bad_files.append(file_path)

    if file_count == 0:
        print("No XML files found in the specified directory.")
    elif bad_files:
        print(f"\n{len(bad_files)} of {file_count} files failed validation:")
        for bad_file in bad_files:
            print(f"  {bad_file}")
    else:
        mode = "schema-valid" if schema else "well-formed"
        print(f"All {file_count} XML files are {mode}.")


def select_directory():
    """
    Open a folder browser window to select a directory.
    """
    from tkinter import Tk
    from tkinter.filedialog import askdirectory

    root = Tk()
    root.withdraw()
    try:
        directory = askdirectory(title="Select Directory to Check XML Files")
        return directory or ""
    finally:
        root.destroy()


def main():
    parser = argparse.ArgumentParser(
        description="Validate XML well-formedness and optionally check against an XSD schema."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        help="Directory to scan (opens folder browser if not provided)",
    )
    parser.add_argument(
        "--schema",
        metavar="XSD_FILE",
        help="Path to an XSD schema file for validation",
    )
    args = parser.parse_args()

    schema = None
    if args.schema:
        try:
            from lxml import etree  # noqa: F401
        except ImportError:
            print("Error: XSD schema validation requires the 'lxml' package.", file=sys.stderr)
            print("Install it with: pip install lxml", file=sys.stderr)
            sys.exit(1)
        if not os.path.isfile(args.schema):
            print(f"Error: Schema file '{args.schema}' not found.", file=sys.stderr)
            sys.exit(1)
        schema = load_schema(args.schema)

    if args.directory:
        if not os.path.isdir(args.directory):
            print(f"Error: '{args.directory}' is not a valid directory.", file=sys.stderr)
            sys.exit(1)
        check_files_in_directory(args.directory, schema=schema)
    else:
        directory = select_directory()
        if directory:
            check_files_in_directory(directory, schema=schema)
        else:
            print("No directory was selected.")


if __name__ == "__main__":
    main()
