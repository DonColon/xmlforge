"""
Unit tests for the XMLParser class.
"""

import pytest
from lxml import etree

from xmlforge.parser import XMLParser


class TestXMLParser:
    """Test cases for XMLParser class."""

    def test_init_default_encoding(self):
        """Test parser initialization with default encoding."""
        parser = XMLParser()
        assert parser.encoding == "utf-8"

    def test_init_custom_encoding(self):
        """Test parser initialization with custom encoding."""
        parser = XMLParser(encoding="utf-16")
        assert parser.encoding == "utf-16"

    def test_parse_string_valid_xml(self):
        """Test parsing a valid XML string."""
        parser = XMLParser()
        xml_string = '<?xml version="1.0"?><root><child>value</child></root>'
        element = parser.parse_string(xml_string)
        assert element.tag == "root"
        assert element[0].tag == "child"
        assert element[0].text == "value"

    def test_parse_string_invalid_xml(self):
        """Test parsing an invalid XML string raises error."""
        parser = XMLParser()
        xml_string = "<root><child>value</root>"  # Mismatched tags
        with pytest.raises(etree.XMLSyntaxError):
            parser.parse_string(xml_string)

    def test_to_dict_simple(self):
        """Test converting simple XML element to dictionary."""
        parser = XMLParser()
        xml_string = "<root><child>value</child></root>"
        element = parser.parse_string(xml_string)
        result = parser.to_dict(element)
        assert "child" in result
        assert result["child"]["@text"] == "value"

    def test_to_dict_with_attributes(self):
        """Test converting XML element with attributes to dictionary."""
        parser = XMLParser()
        xml_string = '<root><child id="1" name="test">value</child></root>'
        element = parser.parse_string(xml_string)
        result = parser.to_dict(element)
        assert "@attributes" in result["child"]
        assert result["child"]["@attributes"]["id"] == "1"
        assert result["child"]["@attributes"]["name"] == "test"
        assert result["child"]["@text"] == "value"

    def test_to_dict_multiple_children(self):
        """Test converting XML element with multiple children to dictionary."""
        parser = XMLParser()
        xml_string = "<root><child>1</child><child>2</child></root>"
        element = parser.parse_string(xml_string)
        result = parser.to_dict(element)
        assert isinstance(result["child"], list)
        assert len(result["child"]) == 2
