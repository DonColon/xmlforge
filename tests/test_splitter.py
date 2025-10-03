"""
Unit tests for the XMLSplitter class.
"""

import pytest
import tempfile
import zipfile
from pathlib import Path
from lxml import etree

from xmlforge.splitter import XMLSplitter


class TestXMLSplitter:
    """Test cases for XMLSplitter class."""

    def test_init(self):
        """Test splitter initialization."""
        splitter = XMLSplitter(target_tag="item", chunk_size=100)
        assert splitter.target_tag == "item"
        assert splitter.chunk_size == 100

    def test_init_default_chunk_size(self):
        """Test splitter initialization with default chunk size."""
        splitter = XMLSplitter(target_tag="item")
        assert splitter.chunk_size == 1000

    def test_init_with_pattern_and_recursive(self):
        """Test splitter initialization with pattern and recursive parameters."""
        splitter = XMLSplitter(
            target_tag="product", chunk_size=500, pattern="data_*.xml", recursive=True
        )
        assert splitter.target_tag == "product"
        assert splitter.chunk_size == 500
        assert splitter.pattern == "data_*.xml"
        assert splitter.recursive is True

    def test_init_default_pattern_and_recursive(self):
        """Test splitter initialization with default pattern and recursive."""
        splitter = XMLSplitter(target_tag="item")
        assert splitter.pattern == "*.xml"
        assert splitter.recursive is False

    def test_split_file_nonexistent_path(self):
        """Test split_file with non-existent path raises FileNotFoundError."""
        splitter = XMLSplitter(target_tag="item")
        with pytest.raises(FileNotFoundError, match="Path not found"):
            list(splitter.split_file("nonexistent.xml"))

    def test_split_file_invalid_path_type(self):
        """Test split_file with invalid path type raises ValueError."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        # Create a path that's neither file nor directory (e.g., broken symlink)
        temp_path.unlink()  # Remove the file but keep the path

        splitter = XMLSplitter(target_tag="item")
        with pytest.raises((FileNotFoundError, ValueError)):
            list(splitter.split_file(temp_path))

    def test_split_directory_no_xml_files(self):
        """Test split_file with directory containing no XML files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a non-XML file
            (Path(temp_dir) / "test.txt").write_text("not xml")

            splitter = XMLSplitter(target_tag="item")
            with pytest.raises(ValueError, match="No files matching '\\*.xml' found in directory"):
                list(splitter.split_file(temp_dir))

    def test_split_directory_with_pattern(self):
        """Test split_file with directory and custom pattern."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create files with different patterns
            (temp_path / "data_001.xml").write_text("<root><item>1</item></root>")
            (temp_path / "data_002.xml").write_text("<root><item>2</item></root>")
            (temp_path / "other.xml").write_text("<root><item>3</item></root>")

            splitter = XMLSplitter(target_tag="item", pattern="data_*.xml")
            chunks = list(splitter.split_file(temp_dir))

            # Should only process data_*.xml files (2 files = 2 items)
            assert len(chunks) == 1  # All items in one chunk
            assert len(chunks[0]) == 2  # 2 items from data_*.xml files

    def test_split_directory_recursive(self):
        """Test split_file with recursive directory search."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create nested directory structure
            (temp_path / "file1.xml").write_text("<root><item>1</item></root>")

            subdir = temp_path / "subdir"
            subdir.mkdir()
            (subdir / "file2.xml").write_text("<root><item>2</item></root>")

            # Test without recursive
            splitter = XMLSplitter(target_tag="item", recursive=False)
            chunks = list(splitter.split_file(temp_dir))
            assert len(chunks) == 1
            assert len(chunks[0]) == 1  # Only top-level file

            # Test with recursive
            splitter = XMLSplitter(target_tag="item", recursive=True)
            chunks = list(splitter.split_file(temp_dir))
            assert len(chunks) == 1
            assert len(chunks[0]) == 2  # Both files found

    def test_split_zip_file(self):
        """Test split_file with ZIP file containing XML files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "test.zip"

            # Create ZIP file with XML content
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr("file1.xml", "<root><item>1</item><item>2</item></root>")
                zf.writestr("file2.xml", "<root><item>3</item></root>")

            splitter = XMLSplitter(target_tag="item", chunk_size=2)
            chunks = list(splitter.split_file(zip_path))

            assert len(chunks) == 2  # 3 items, chunk_size=2 -> 2 chunks
            assert len(chunks[0]) == 2  # First chunk has 2 items
            assert len(chunks[1]) == 1  # Second chunk has 1 item

    def test_split_zip_file_no_xml(self):
        """Test split_file with ZIP file containing no XML files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "test.zip"

            # Create ZIP file without XML content
            with zipfile.ZipFile(zip_path, "w") as zf:
                zf.writestr("file1.txt", "not xml")

            splitter = XMLSplitter(target_tag="item")
            with pytest.raises(ValueError, match="No XML files found in ZIP"):
                list(splitter.split_file(zip_path))

    def test_split_invalid_zip_file(self):
        """Test split_file with invalid ZIP file."""
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
            temp_file.write(b"not a zip file")
            temp_path = Path(temp_file.name)

        try:
            splitter = XMLSplitter(target_tag="item")
            with pytest.raises(ValueError, match="Invalid ZIP file"):
                list(splitter.split_file(temp_path))
        finally:
            temp_path.unlink()

    def test_create_chunk_tree(self):
        """Test _create_chunk_tree method."""
        splitter = XMLSplitter(target_tag="item")

        # Create test elements
        elem1 = etree.Element("item")
        elem1.text = "test1"
        elem2 = etree.Element("item")
        elem2.text = "test2"

        chunk_tree = splitter._create_chunk_tree([elem1, elem2])

        assert chunk_tree.tag == "chunk"
        assert len(chunk_tree) == 2
        assert chunk_tree[0].text == "test1"
        assert chunk_tree[1].text == "test2"

    def test_write_chunk(self):
        """Test _write_chunk method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"

            splitter = XMLSplitter(target_tag="item")

            # Create test elements
            elem1 = etree.Element("item")
            elem1.text = "test1"
            elem2 = etree.Element("item")
            elem2.text = "test2"

            splitter._write_chunk([elem1, elem2], output_dir, 0)

            # Check if file was created
            output_file = output_dir / "chunk_0000.xml"
            assert output_file.exists()

            # Check file content
            tree = etree.parse(str(output_file))
            root = tree.getroot()
            assert root.tag == "chunk"
            assert len(root) == 2
