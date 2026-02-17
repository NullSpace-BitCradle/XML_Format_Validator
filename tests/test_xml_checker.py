"""Unit tests for xml_checker module."""

import os
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xml_checker import check_xml_format, check_files_in_directory


class TestCheckXmlFormat(unittest.TestCase):
    """Tests for check_xml_format function."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)

    def _write_file(self, name, content):
        path = os.path.join(self.temp_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_valid_xml(self):
        """Valid XML should return True."""
        path = self._write_file("valid.xml", "<root><child>text</child></root>")
        self.assertTrue(check_xml_format(path))

    def test_invalid_xml_unclosed_tag(self):
        """Unclosed tag should return False."""
        path = self._write_file("bad.xml", "<root><child>text</root>")
        with patch("sys.stdout", new_callable=StringIO):
            self.assertFalse(check_xml_format(path))

    def test_invalid_xml_malformed(self):
        """Malformed XML should return False."""
        path = self._write_file("bad.xml", "<root><unclosed>")
        with patch("sys.stdout", new_callable=StringIO):
            self.assertFalse(check_xml_format(path))

    def test_invalid_xml_empty(self):
        """Empty file should return False."""
        path = self._write_file("empty.xml", "")
        with patch("sys.stdout", new_callable=StringIO):
            self.assertFalse(check_xml_format(path))

    def test_invalid_xml_not_xml(self):
        """Non-XML content should return False."""
        path = self._write_file("notxml.xml", "this is not xml at all")
        with patch("sys.stdout", new_callable=StringIO):
            self.assertFalse(check_xml_format(path))

    def test_nonexistent_file(self):
        """Nonexistent file should return False."""
        path = os.path.join(self.temp_dir, "nonexistent.xml")
        with patch("sys.stdout", new_callable=StringIO):
            self.assertFalse(check_xml_format(path))


class TestCheckFilesInDirectory(unittest.TestCase):
    """Tests for check_files_in_directory function."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        os.rmdir(self.temp_dir)

    def _write_file(self, name, content):
        path = os.path.join(self.temp_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_all_valid(self):
        """All valid XML should print success message."""
        self._write_file("a.xml", "<a/>")
        self._write_file("b.xml", "<b><c/></b>")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            check_files_in_directory(self.temp_dir)
            self.assertIn("All XML files are well-formed", mock_stdout.getvalue())

    def test_some_invalid(self):
        """Invalid files should be reported."""
        self._write_file("good.xml", "<root/>")
        self._write_file("bad.xml", "<root><unclosed>")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            check_files_in_directory(self.temp_dir)
            output = mock_stdout.getvalue()
            self.assertIn("bad.xml", output)
            self.assertIn("not well-formed", output)

    def test_case_insensitive_extension(self):
        """Files with .XML extension should be checked."""
        self._write_file("test.XML", "<root/>")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            check_files_in_directory(self.temp_dir)
            self.assertIn("All XML files are well-formed", mock_stdout.getvalue())

    def test_skips_non_xml(self):
        """Non-.xml files should be ignored."""
        self._write_file("data.txt", "not xml")
        self._write_file("config.xml", "<config/>")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            check_files_in_directory(self.temp_dir)
            self.assertIn("All XML files are well-formed", mock_stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
