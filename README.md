# XML Format Validator

A Python script that recursively scans directories and validates the well-formedness of XML files, with optional GUI folder selection or direct CLI path input.

[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- **Recursive directory scanning** through all subdirectories
- **XML well-formedness validation** using Python's built-in `xml.etree.ElementTree`
- **GUI or CLI** -- folder browser dialog or command-line path for headless/scripting use
- **Error reporting** with specific error messages and line numbers for each malformed file
- **Cross-platform** -- works on Windows, macOS, and Linux
- **No dependencies** -- uses only the Python standard library

## Installation

```bash
git clone https://github.com/NullSpace-BitCradle/XML_Format_Validator.git
cd XML_Format_Validator
```

No additional dependencies are required. Python 3.x must be installed. The GUI mode requires `tkinter` (included with most Python installations).

## Usage

**CLI (specify directory):**

```bash
python xml_checker.py /path/to/directory
```

**GUI (folder browser):**

```bash
python xml_checker.py
```

If no path is provided, a folder browser dialog opens. The script then recursively scans all `.xml` files (case-insensitive) and reports results.

### Output Examples

When all files are valid:

```text
All XML files are well-formed.
```

When malformed files are found:

```text
/path/to/bad_file.xml: XML is not well-formed. Error: mismatched tag: line 5, column 10

The following files are not well-formed:
/path/to/bad_file.xml
```

## Functions

| Function | Description | Returns |
|----------|-------------|---------|
| `check_xml_format(file_path)` | Validates a single XML file for well-formedness | `True` if valid, `False` otherwise |
| `check_files_in_directory(directory)` | Recursively scans a directory and validates all XML files | Prints results to console |
| `select_directory()` | Opens a GUI folder selection dialog | Directory path string, or empty string if cancelled |

## Testing

```bash
python -m unittest discover -s tests -v
```

Or with pytest:

```bash
python -m pytest tests/ -v
```

## Limitations

- Checks well-formedness only, not schema validation (DTD/XSD)
- Limited to files with `.xml` extension (case-insensitive)
- GUI mode requires `tkinter` (install with `sudo apt-get install python3-tk` on Linux if missing)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
