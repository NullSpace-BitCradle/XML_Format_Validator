"""Unit tests for xml_checker module."""

import os
import subprocess
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import xml_checker
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
        with patch("sys.stderr", new_callable=StringIO):
            self.assertFalse(check_xml_format(path))

    def test_invalid_xml_malformed(self):
        """Malformed XML should return False."""
        path = self._write_file("bad.xml", "<root><unclosed>")
        with patch("sys.stderr", new_callable=StringIO):
            self.assertFalse(check_xml_format(path))

    def test_invalid_xml_empty(self):
        """Empty file should return False."""
        path = self._write_file("empty.xml", "")
        with patch("sys.stderr", new_callable=StringIO):
            self.assertFalse(check_xml_format(path))

    def test_invalid_xml_not_xml(self):
        """Non-XML content should return False."""
        path = self._write_file("notxml.xml", "this is not xml at all")
        with patch("sys.stderr", new_callable=StringIO):
            self.assertFalse(check_xml_format(path))

    def test_nonexistent_file(self):
        """Nonexistent file should return False."""
        path = os.path.join(self.temp_dir, "nonexistent.xml")
        with patch("sys.stderr", new_callable=StringIO):
            self.assertFalse(check_xml_format(path))

    def test_large_file_is_well_formed(self):
        """A large valid file passes (it is parsed incrementally)."""
        path = self._write_file("large.xml", "<root>" + "<item>x</item>" * 100000 + "</root>")
        self.assertTrue(check_xml_format(path))


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
            self.assertIn("well-formed", mock_stdout.getvalue())

    def test_some_invalid(self):
        """Invalid files should be reported."""
        self._write_file("good.xml", "<root/>")
        self._write_file("bad.xml", "<root><unclosed>")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout, \
                patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            check_files_in_directory(self.temp_dir)
            self.assertIn("bad.xml", mock_stdout.getvalue())
            self.assertIn("not well-formed", mock_stderr.getvalue())

    def test_case_insensitive_extension(self):
        """Files with .XML extension should be checked."""
        self._write_file("test.XML", "<root/>")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            check_files_in_directory(self.temp_dir)
            self.assertIn("well-formed", mock_stdout.getvalue())

    def test_skips_non_xml(self):
        """Non-.xml files should be ignored."""
        self._write_file("data.txt", "not xml")
        self._write_file("config.xml", "<config/>")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            check_files_in_directory(self.temp_dir)
            self.assertIn("well-formed", mock_stdout.getvalue())

    def test_no_xml_files(self):
        """Directory with no XML files should report none found."""
        self._write_file("data.txt", "not xml")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            check_files_in_directory(self.temp_dir)
            self.assertIn("No XML files found", mock_stdout.getvalue())

    def test_file_count_in_output(self):
        """Output should include count of files checked."""
        self._write_file("a.xml", "<a/>")
        self._write_file("b.xml", "<b/>")
        self._write_file("c.xml", "<c/>")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            check_files_in_directory(self.temp_dir)
            self.assertIn("3 XML files", mock_stdout.getvalue())

    def test_failure_count_in_output(self):
        """Output should include count of failed files."""
        self._write_file("good.xml", "<root/>")
        self._write_file("bad1.xml", "<root><unclosed>")
        self._write_file("bad2.xml", "not xml")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout, \
                patch("sys.stderr", new_callable=StringIO):
            check_files_in_directory(self.temp_dir)
            self.assertIn("2 of 3", mock_stdout.getvalue())


class TestReturnValueAndStreams(unittest.TestCase):
    """check_files_in_directory reports problems through its return value and stderr."""

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

    def _run(self, **kwargs):
        with patch("sys.stdout", new_callable=StringIO) as out, \
                patch("sys.stderr", new_callable=StringIO) as err:
            result = check_files_in_directory(self.temp_dir, **kwargs)
        return result, out.getvalue(), err.getvalue()

    def test_returns_zero_when_all_valid(self):
        self._write_file("a.xml", "<a/>")
        result, _, _ = self._run()
        self.assertEqual(result, 0)

    def test_returns_zero_when_no_xml_files(self):
        result, out, _ = self._run()
        self.assertEqual(result, 0)
        self.assertIn("No XML files found", out)

    def test_returns_failure_count(self):
        self._write_file("good.xml", "<a/>")
        self._write_file("bad1.xml", "<a>")
        self._write_file("bad2.xml", "nope")
        result, _, _ = self._run()
        self.assertEqual(result, 2)

    def test_failure_detail_goes_to_stderr_not_stdout(self):
        self._write_file("bad.xml", "<a>")
        _, out, err = self._run()
        self.assertIn("not well-formed", err)
        self.assertNotIn("not well-formed", out)
        self.assertIn("1 of 1 files failed validation", out)

    def test_unreadable_directory_is_a_failure(self):
        """A directory os.walk cannot read must not produce an 'all well-formed' result."""
        self._write_file("ok.xml", "<a/>")
        locked = os.path.join(self.temp_dir, "locked")

        def fake_walk(top, onerror=None):
            yield top, [], ["ok.xml"]
            onerror(PermissionError(13, "Permission denied", locked))

        with patch("xml_checker.os.walk", fake_walk):
            result, out, err = self._run()
        self.assertEqual(result, 1)
        self.assertNotIn("All 1 XML files", out)
        self.assertIn("could not be read", out)
        self.assertIn(locked, out)
        self.assertIn("Cannot read directory", err)


class TestCommandLine(unittest.TestCase):
    """Exit codes of the command line entry point."""

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

    def _main_exit_code(self, *argv):
        with patch("sys.argv", ["xml_checker.py", *argv]), \
                patch("sys.stdout", new_callable=StringIO), \
                patch("sys.stderr", new_callable=StringIO):
            with self.assertRaises(SystemExit) as ctx:
                xml_checker.main()
        return ctx.exception.code

    def test_exit_zero_when_all_valid(self):
        self._write_file("a.xml", "<a/>")
        self.assertEqual(self._main_exit_code(self.temp_dir), 0)

    def test_exit_one_when_a_file_fails(self):
        self._write_file("good.xml", "<a/>")
        self._write_file("bad.xml", "<a>")
        self.assertEqual(self._main_exit_code(self.temp_dir), 1)

    def test_exit_one_for_missing_directory(self):
        missing = os.path.join(self.temp_dir, "nope")
        self.assertEqual(self._main_exit_code(missing), 1)

    def test_exit_one_for_missing_schema_file(self):
        missing = os.path.join(self.temp_dir, "nope.xsd")
        self.assertEqual(self._main_exit_code(self.temp_dir, "--schema", missing), 1)

    def test_subprocess_exit_codes(self):
        """End to end: the real script returns the codes a shell or CI step sees."""
        script = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "xml_checker.py")
        self._write_file("good.xml", "<a/>")
        ok = subprocess.run([sys.executable, "-B", script, self.temp_dir],
                            capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0)
        self._write_file("bad.xml", "<a>")
        bad = subprocess.run([sys.executable, "-B", script, self.temp_dir],
                             capture_output=True, text=True)
        self.assertEqual(bad.returncode, 1)
        self.assertIn("1 of 2 files failed validation", bad.stdout)
        self.assertIn("not well-formed", bad.stderr)


try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False


@unittest.skipUnless(HAS_LXML, "lxml not installed")
class TestSchemaValidation(unittest.TestCase):
    """Tests for XSD schema validation."""

    SAMPLE_XSD = '''\
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="book">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="title" type="xs:string"/>
        <xs:element name="author" type="xs:string"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>'''

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.schema_path = self._write_file("schema.xsd", self.SAMPLE_XSD)

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

    def test_valid_against_schema(self):
        """XML matching schema should pass validation."""
        from xml_checker import validate_xml_schema, load_schema
        self._write_file("book.xml",
            "<book><title>Test</title><author>Author</author></book>")
        schema = load_schema(self.schema_path)
        self.assertTrue(validate_xml_schema(
            os.path.join(self.temp_dir, "book.xml"), schema))

    def test_invalid_against_schema(self):
        """XML not matching schema should fail validation."""
        from xml_checker import validate_xml_schema, load_schema
        self._write_file("bad_book.xml",
            "<book><title>Test</title></book>")
        schema = load_schema(self.schema_path)
        with patch("sys.stderr", new_callable=StringIO):
            self.assertFalse(validate_xml_schema(
                os.path.join(self.temp_dir, "bad_book.xml"), schema))

    def test_malformed_xml_with_schema(self):
        """Malformed XML should fail schema validation."""
        from xml_checker import validate_xml_schema, load_schema
        self._write_file("broken.xml", "<book><unclosed>")
        schema = load_schema(self.schema_path)
        with patch("sys.stderr", new_callable=StringIO):
            self.assertFalse(validate_xml_schema(
                os.path.join(self.temp_dir, "broken.xml"), schema))

    def test_directory_with_schema(self):
        """check_files_in_directory should use schema when provided."""
        from xml_checker import load_schema
        self._write_file("valid.xml",
            "<book><title>T</title><author>A</author></book>")
        self._write_file("invalid.xml",
            "<book><title>T</title></book>")
        schema = load_schema(self.schema_path)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout, \
                patch("sys.stderr", new_callable=StringIO):
            check_files_in_directory(self.temp_dir, schema=schema)
            output = mock_stdout.getvalue()
            self.assertIn("1 of 2", output)
            self.assertIn("invalid.xml", output)

    def test_all_valid_with_schema_output(self):
        """All schema-valid files should show schema-valid message."""
        from xml_checker import load_schema
        self._write_file("book.xml",
            "<book><title>T</title><author>A</author></book>")
        schema = load_schema(self.schema_path)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            check_files_in_directory(self.temp_dir, schema=schema)
            self.assertIn("schema-valid", mock_stdout.getvalue())

    def test_huge_text_node_gets_a_clear_message(self):
        """A valid file over libxml2's text limit is reported as a limit, not as bad syntax."""
        from xml_checker import validate_xml_schema, load_schema
        path = self._write_file("big.xml",
            "<book><title>" + "x" * 11000000 + "</title><author>A</author></book>")
        schema = load_schema(self.schema_path)
        with patch("sys.stderr", new_callable=StringIO) as err:
            self.assertFalse(validate_xml_schema(path, schema))
        self.assertIn("--huge-tree", err.getvalue())
        self.assertNotIn("is not well-formed", err.getvalue())

    def test_huge_tree_option_validates_large_file(self):
        """With huge_tree=True the same file is checked against the schema and passes."""
        from xml_checker import validate_xml_schema, load_schema
        path = self._write_file("big.xml",
            "<book><title>" + "x" * 11000000 + "</title><author>A</author></book>")
        schema = load_schema(self.schema_path)
        self.assertTrue(validate_xml_schema(path, schema, huge_tree=True))

    def test_external_entity_is_not_read(self):
        """The parser must not pull local file content in through an external entity."""
        from xml_checker import _make_parser
        marker = self._write_file("secret.txt", "TOPSECRETMARKER")
        uri = "file:///" + marker.replace("\\", "/").lstrip("/")
        doc = ('<?xml version="1.0"?><!DOCTYPE book [<!ENTITY x SYSTEM "%s">]>'
               '<book><title>&x;</title><author>A</author></book>' % uri)
        path = self._write_file("xxe.xml", doc)
        try:
            tree = etree.parse(path, _make_parser())
            text = etree.tostring(tree).decode()
        except etree.XMLSyntaxError:
            text = ""
        self.assertNotIn("TOPSECRETMARKER", text)

    def test_exit_code_with_schema(self):
        """main() exits 1 in schema mode when a file fails the schema."""
        self._write_file("invalid.xml", "<book><title>T</title></book>")
        with patch("sys.argv", ["xml_checker.py", self.temp_dir, "--schema", self.schema_path]), \
                patch("sys.stdout", new_callable=StringIO), \
                patch("sys.stderr", new_callable=StringIO):
            with self.assertRaises(SystemExit) as ctx:
                xml_checker.main()
        self.assertEqual(ctx.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
