"""
Unit tests for the XMLSplitter class.
"""

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
