# Changelog

## Unreleased (branch fix/audit-2026-11-18)

### Changed: exit codes (may break scripts)

- The command line now exits **1** when any file fails validation or any directory could not be read. It always exited 0 before. A clean run, or a directory with no XML files, still exits 0.
- Invalid command-line usage (an unknown option, for example) exits **2**, as argparse does. Missing directory, missing or bad schema and missing `lxml` exit 1, as before.

### Changed: behaviour

- Per-file failure details go to stderr; the summary stays on stdout.
- A directory that cannot be read is reported and counted instead of being skipped silently.
- Schema mode reports a file over libxml2's size limit as a limit, not as "not well-formed", and `--huge-tree` lifts the limit.
- Schema mode parses with an explicit parser (internal entities only, no network). `lxml` 5.0 or newer is now the documented requirement.
- `check_files_in_directory` returns the number of problems; `validate_xml_schema` takes an optional `huge_tree` argument.

### Added

- `--huge-tree` option.
- CLI, exit code and unreadable directory tests (18 tests became 34).
