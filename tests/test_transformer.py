"""
Unit tests for the XMLTransformer class.
"""

from lxml import etree

from xmlforge.transformer import XMLTransformer


class TestXMLTransformer:
    """Test cases for XMLTransformer class."""

    def test_init_without_xslt(self):
        """Test transformer initialization without XSLT file."""
        transformer = XMLTransformer()
        assert transformer.xslt_file is None
        assert transformer.transform is None

    def test_remove_namespace(self):
        """Test removing namespaces from XML element."""
        transformer = XMLTransformer()
        xml_string = '<root xmlns="http://example.com"><child>value</child></root>'
        element = etree.fromstring(xml_string.encode("utf-8"))

        result = transformer.remove_namespace(element)
        assert result.tag == "root"
        assert "{http://example.com}" not in result.tag
