# XML Format Validator

A Python tool that recursively scans directories and validates XML files for well-formedness, with optional XSD schema validation.

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- **Recursive directory scanning** through all subdirectories
- **XML well-formedness validation** using Python's built-in `xml.etree.ElementTree`
- **XSD schema validation** using `lxml` (optional dependency)
- **GUI or CLI** -- folder browser dialog or command-line path for headless/scripting use
- **Exit codes** -- 0 when every file passes, 1 when any file fails or a directory cannot be read, so it works in scripts and CI
- **Error reporting** with specific error messages, line numbers, and file counts
- **Portable** -- standard library only for well-formedness checks; tested on Windows (Python 3.15), not yet on macOS or Linux

## Installation

```bash
git clone https://github.com/NullSpace-BitCradle/XML_Format_Validator.git
cd XML_Format_Validator
```

Python 3.7 or newer is required (tested on 3.15). No additional dependencies are needed for well-formedness checks.

For XSD schema validation, install `lxml` 5.0 or newer:

```bash
pip install "lxml>=5.0"
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

**Large files in schema mode:**

libxml2 refuses single text nodes over about 10 MB. Such a file fails with a message that points at `--huge-tree`. Add the flag to lift the limit, and only on files you trust.

```bash
python xml_checker.py /path/to/directory --schema schema.xsd --huge-tree
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

Failures found. The per-file error goes to stderr and the summary to stdout:

```text
/path/to/bad_file.xml: XML is not well-formed. Error: mismatched tag: line 5, column 10

2 of 12 files failed validation:
  /path/to/bad_file.xml
  /path/to/another_bad.xml
```

A directory that cannot be read is reported and counted as a failure, so a partial scan is never reported as "all well-formed":

```text
/path/to/locked: Cannot read directory: Permission denied

1 directories could not be read (their files were not checked):
  /path/to/locked
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Every XML file passed, or none were found |
| 1 | A file failed, a directory could not be read, or a path argument was invalid (missing directory, missing or bad schema, `lxml` not installed) |
| 2 | Invalid command-line usage, such as an unknown option (argparse's own exit code) |

Exiting 1 on failure is a change from earlier versions, which always exited 0. See [CHANGELOG.md](CHANGELOG.md).

## Functions

| Function | Description | Returns |
|----------|-------------|---------|
| `check_xml_format(file_path)` | Validates a single XML file for well-formedness | `True` if valid, `False` otherwise |
| `validate_xml_schema(file_path, schema, huge_tree=False)` | Validates an XML file against a compiled XSD schema | `True` if valid, `False` otherwise |
| `load_schema(schema_path)` | Loads and compiles an XSD schema file | Compiled `lxml.etree.XMLSchema` object |
| `check_files_in_directory(directory, schema=None, huge_tree=False)` | Recursively scans and validates all XML files | Prints the summary; returns the number of problems (failed files plus unreadable directories) |
| `select_directory()` | Opens a GUI folder selection dialog | Directory path string, or empty string if cancelled |

## Testing

```bash
python -m unittest discover -s tests -v
```

34 tests total: 25 core tests (no dependencies) + 9 schema validation tests (require `lxml`, auto-skipped if not installed). They cover exit codes, unreadable directories and the command line as well as the helper functions.

## Limitations

- Limited to files with `.xml` extension (case-insensitive)
- XSD schema validation requires the `lxml` package (5.0 or newer)
- Schema mode expands internal entities only and never reads external entities or the network
- GUI mode requires `tkinter` (install with `sudo apt-get install python3-tk` on Linux if missing)
- DTD validation is not supported

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
