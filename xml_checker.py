import argparse
import os
import sys
import xml.etree.ElementTree as ET


def _report(message):
    """Print a per-file failure to stderr so stdout carries only the summary."""
    print(message, file=sys.stderr)


def check_xml_format(file_path):
    """
    Check if an XML file is well-formed.

    Parses incrementally and discards each element once it has been seen, so
    memory use does not grow with file size.
    """
    try:
        with open(file_path, "rb") as f:
            for _, elem in ET.iterparse(f, events=("end",)):
                elem.clear()
        return True
    except ET.ParseError as e:
        _report(f"{file_path}: XML is not well-formed. Error: {e}")
        return False
    except Exception as e:
        _report(f"{file_path}: Unexpected error: {e}")
        return False


def _make_parser(huge_tree=False):
    """
    Build an lxml parser with explicit, version-independent entity handling:
    internal entities are expanded, external entities and network access are
    not. huge_tree lifts libxml2's size limits and is off unless asked for.
    """
    from lxml import etree

    return etree.XMLParser(
        resolve_entities="internal",
        no_network=True,
        huge_tree=huge_tree,
    )


def _is_libxml2_limit(error):
    """True if an lxml syntax error is a libxml2 safety limit, not bad syntax."""
    if "huge" in str(error).lower():
        return True
    return any(entry.type_name == "ERR_NO_MEMORY" for entry in error.error_log)


def validate_xml_schema(file_path, schema, huge_tree=False):
    """
    Validate an XML file against an XSD schema using lxml.
    Returns True if valid, False otherwise.
    """
    from lxml import etree

    try:
        doc = etree.parse(file_path, _make_parser(huge_tree))
        if schema.validate(doc):
            return True
        else:
            for error in schema.error_log:
                _report(f"{file_path}: Schema validation error: {error.message} (line {error.line})")
            return False
    except etree.XMLSyntaxError as e:
        if not huge_tree and _is_libxml2_limit(e):
            _report(
                f"{file_path}: File exceeds a libxml2 size limit and could not be "
                f"checked. Retry with --huge-tree. Error: {e}"
            )
        else:
            _report(f"{file_path}: XML is not well-formed. Error: {e}")
        return False
    except Exception as e:
        _report(f"{file_path}: Unexpected error: {e}")
        return False


def load_schema(schema_path):
    """
    Load an XSD schema file and return a compiled schema object.
    """
    from lxml import etree

    try:
        schema_doc = etree.parse(schema_path, _make_parser())
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


def check_files_in_directory(directory, schema=None, huge_tree=False):
    """
    Recursively check all XML files in a directory and its subdirectories.
    If a schema is provided, validates against it; otherwise checks well-formedness only.

    Returns the number of problems: files that failed plus directories that
    could not be read. Zero means everything was checked and passed.
    """
    bad_files = []
    unreadable_dirs = []
    file_count = 0

    def on_walk_error(error):
        path = error.filename or directory
        _report(f"{path}: Cannot read directory: {error.strerror or error}")
        unreadable_dirs.append(path)

    for root, _, files in os.walk(directory, onerror=on_walk_error):
        for file_name in files:
            if file_name.lower().endswith('.xml'):
                file_path = os.path.join(root, file_name)
                file_count += 1
                if schema:
                    if not validate_xml_schema(file_path, schema, huge_tree=huge_tree):
                        bad_files.append(file_path)
                else:
                    if not check_xml_format(file_path):
                        bad_files.append(file_path)

    if bad_files:
        print(f"\n{len(bad_files)} of {file_count} files failed validation:")
        for bad_file in bad_files:
            print(f"  {bad_file}")
    if unreadable_dirs:
        print(f"\n{len(unreadable_dirs)} directories could not be read (their files were not checked):")
        for bad_dir in unreadable_dirs:
            print(f"  {bad_dir}")
    if not bad_files and not unreadable_dirs:
        if file_count == 0:
            print("No XML files found in the specified directory.")
        else:
            mode = "schema-valid" if schema else "well-formed"
            print(f"All {file_count} XML files are {mode}.")

    return len(bad_files) + len(unreadable_dirs)


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
        description="Validate XML well-formedness and optionally check against an XSD schema. "
        "Exits 0 if every file passed, 1 if any file failed, a directory could not be "
        "read, or the arguments were invalid."
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
    parser.add_argument(
        "--huge-tree",
        action="store_true",
        help="With --schema, lift libxml2's size limits (for example text nodes over 10 MB). "
        "Only use on files you trust.",
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
        problems = check_files_in_directory(args.directory, schema=schema, huge_tree=args.huge_tree)
        sys.exit(1 if problems else 0)
    else:
        directory = select_directory()
        if directory:
            problems = check_files_in_directory(directory, schema=schema, huge_tree=args.huge_tree)
            sys.exit(1 if problems else 0)
        else:
            print("No directory was selected.")


if __name__ == "__main__":
    main()
