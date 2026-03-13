# XML Format Validator

A Python tool that recursively scans directories and validates XML files for well-formedness, with optional XSD schema validation.

[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- **Recursive directory scanning** through all subdirectories
- **XML well-formedness validation** using Python's built-in `xml.etree.ElementTree`
- **XSD schema validation** using `lxml` (optional dependency)
- **GUI or CLI** -- folder browser dialog or command-line path for headless/scripting use
- **Error reporting** with specific error messages, line numbers, and file counts
- **Cross-platform** -- works on Windows, macOS, and Linux

## Installation

```bash
git clone https://github.com/NullSpace-BitCradle/XML_Format_Validator.git
cd XML_Format_Validator
```

Python 3.x is required. No additional dependencies are needed for well-formedness checks.

For XSD schema validation, install `lxml`:

```bash
pip install lxml
```

GUI mode requires `tkinter` (included with most Python installations).

## Usage

**Well-formedness check (CLI):**

```bash
python xml_checker.py /path/to/directory
```

**XSD schema validation:**

```bash
python xml_checker.py /path/to/directory --schema schema.xsd
```

**GUI mode (folder browser):**

```bash
python xml_checker.py
```

If no path is provided, a folder browser dialog opens. The script recursively scans all `.xml` files (case-insensitive) and reports results.

### Output Examples

All files valid (well-formedness):

```text
All 12 XML files are well-formed.
```

All files valid (schema):

```text
All 12 XML files are schema-valid.
```

Failures found:

```text
/path/to/bad_file.xml: XML is not well-formed. Error: mismatched tag: line 5, column 10

2 of 12 files failed validation:
  /path/to/bad_file.xml
  /path/to/another_bad.xml
```

## Functions

| Function | Description | Returns |
|----------|-------------|---------|
| `check_xml_format(file_path)` | Validates a single XML file for well-formedness | `True` if valid, `False` otherwise |
| `validate_xml_schema(file_path, schema)` | Validates an XML file against a compiled XSD schema | `True` if valid, `False` otherwise |
| `load_schema(schema_path)` | Loads and compiles an XSD schema file | Compiled `lxml.etree.XMLSchema` object |
| `check_files_in_directory(directory, schema=None)` | Recursively scans and validates all XML files | Prints results to console |
| `select_directory()` | Opens a GUI folder selection dialog | Directory path string, or empty string if cancelled |

## Testing

```bash
python -m unittest discover -s tests -v
```

18 tests total: 13 core tests (no dependencies) + 5 schema validation tests (require `lxml`, auto-skipped if not installed).

## Limitations

- Limited to files with `.xml` extension (case-insensitive)
- XSD schema validation requires the `lxml` package
- GUI mode requires `tkinter` (install with `sudo apt-get install python3-tk` on Linux if missing)
- DTD validation is not supported

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
