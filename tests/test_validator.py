"""
Unit tests for the XMLValidator class.
"""

from xmlforge.validator import XMLValidator


class TestXMLValidator:
    """Test cases for XMLValidator class."""

    def test_init(self):
        """Test validator initialization."""
        validator = XMLValidator()
        assert validator is not None

    def test_is_well_formed_valid_xml_string(self):
        """Test checking well-formed XML string."""
        validator = XMLValidator()
        xml_string = '<?xml version="1.0"?><root><child>value</child></root>'
        assert validator.is_well_formed(xml_string) is True

    def test_is_well_formed_invalid_xml_string(self):
        """Test checking malformed XML string."""
        validator = XMLValidator()
        xml_string = "<root><child>value</root>"  # Mismatched tags
        assert validator.is_well_formed(xml_string) is False

    def test_is_well_formed_empty_string(self):
        """Test checking empty string."""
        validator = XMLValidator()
        assert validator.is_well_formed("") is False
