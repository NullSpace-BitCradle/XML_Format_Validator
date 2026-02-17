# XML Format Validator

A Python script that recursively scans directories and validates the well-formedness of XML files using a simple GUI folder selection interface.

## Features

- **Recursive Directory Scanning**: Automatically searches through all subdirectories
- **XML Well-formedness Validation**: Uses Python's built-in `xml.etree.ElementTree` parser to validate XML structure
- **GUI or CLI**: Folder browser dialog or command-line path for headless/scripting use
- **Comprehensive Error Reporting**: Lists all malformed XML files with specific error messages
- **Cross-platform Compatibility**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.x
- Standard library modules (no additional installations required):
  - `xml.etree.ElementTree`
  - `os`
  - `tkinter`

## Installation

1. Download the script file
2. Ensure Python 3.x is installed on your system
3. No additional dependencies need to be installed

## Usage

### Running the Script

**With GUI (folder browser):**

```bash
python xml_checker.py
```

**With CLI (specify directory directly):**

```bash
python xml_checker.py /path/to/directory
```

This mode works in headless environments and for scripting/automation.

### How It Works

1. **Select Directory**: If no path is provided, a folder browser dialog will open automatically
2. **Choose Target Folder**: Navigate to and select the directory containing XML files you want to validate
3. **Automatic Validation**: The script will:
   - Recursively scan the selected directory and all subdirectories
   - Check every `.xml` file for well-formedness
   - Display results in the console

### Output Examples

**When all XML files are valid:**

```text
All XML files are well-formed.
```

**When malformed XML files are found:**

```text
/path/to/bad_file.xml: XML is not well-formed. Error: mismatched tag: line 5, column 10
/path/to/another_bad_file.xml: XML is not well-formed. Error: not well-formed (invalid token): line 3, column 15

The following files are not well-formed:
/path/to/bad_file.xml
/path/to/another_bad_file.xml
```

## Functions

### `check_xml_format(file_path)`

Validates whether a single XML file is well-formed.

- **Parameters**: `file_path` (str) - Path to the XML file
- **Returns**: `True` if well-formed, `False` otherwise
- **Error Handling**: Catches parsing errors and unexpected exceptions

### `check_files_in_directory(directory)`

Recursively scans a directory and validates all XML files found.

- **Parameters**: `directory` (str) - Path to the root directory to scan
- **Output**: Prints validation results to console

### `select_directory()`

Opens a GUI folder selection dialog.

- **Returns**: Selected directory path as string, or empty string if cancelled
- **Interface**: Uses tkinter's `askdirectory` dialog

## Error Handling

The script handles several types of errors gracefully:

- **XML Parse Errors**: Malformed XML syntax, unclosed tags, invalid characters
- **File Access Errors**: Permission issues, missing files, corrupted files
- **Directory Selection**: Handles cases where no directory is selected

## Use Cases

- **Quality Assurance**: Validate XML files before processing or deployment
- **Data Migration**: Ensure XML data integrity during transfers
- **Development**: Quick validation of XML configuration files
- **Batch Processing**: Validate large collections of XML documents

## Limitations

- Only checks for well-formedness, not schema validation
- Does not validate against specific DTD or XSD schemas
- Limited to files with `.xml` extension (case-insensitive: `.xml`, `.XML`, etc.)
- Requires GUI environment for folder selection (uses tkinter)

## Troubleshooting

**Issue**: "No module named 'tkinter'"

- **Solution**: Install tkinter (usually included with Python installations)
- **Linux**: `sudo apt-get install python3-tk`

**Issue**: Script runs but no dialog appears

- **Solution**: Ensure you're running in a GUI environment, not a headless server

**Issue**: Permission denied errors

- **Solution**: Run with appropriate permissions or select a different directory

## Testing

Run the test suite with:

```bash
python -m pytest tests/ -v
```

Or with unittest:

```bash
python -m unittest discover -s tests -v
```

## License

This script uses only Python standard library modules and can be freely used and modified.
