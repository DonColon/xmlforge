"""
XML Parser module for parsing XML documents.
"""

from pathlib import Path
from typing import Any, Dict, Union

from lxml import etree


class XMLParser:
    """
    A class for parsing XML documents with support for various input formats.

    Attributes:
        encoding (str): The encoding to use when parsing XML files.
    """

    def __init__(self, encoding: str = "utf-8") -> None:
        """
        Initialize the XMLParser.

        Args:
            encoding: The encoding to use for parsing. Defaults to 'utf-8'.
        """
        self.encoding = encoding

    def parse_file(self, filepath: Union[str, Path]) -> etree._ElementTree:
        """
        Parse an XML file and return an ElementTree object.

        Args:
            filepath: Path to the XML file to parse.

        Returns:
            An lxml ElementTree object representing the parsed XML.

        Raises:
            FileNotFoundError: If the file does not exist.
            etree.XMLSyntaxError: If the XML is malformed.
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        parser = etree.XMLParser(encoding=self.encoding, remove_blank_text=True)
        return etree.parse(str(filepath), parser)

    def parse_string(self, xml_string: str) -> etree._Element:
        """
        Parse an XML string and return an Element object.

        Args:
            xml_string: The XML string to parse.

        Returns:
            An lxml Element object representing the root of the parsed XML.

        Raises:
            etree.XMLSyntaxError: If the XML is malformed.
        """
        parser = etree.XMLParser(encoding=self.encoding, remove_blank_text=True)
        return etree.fromstring(xml_string.encode(self.encoding), parser)

    def to_dict(self, element: etree._Element) -> Dict[str, Any]:
        """
        Convert an XML element to a dictionary representation.

        Args:
            element: The XML element to convert.

        Returns:
            A dictionary representation of the XML element.
        """
        result: Dict[str, Any] = {}

        # Add attributes
        if element.attrib:
            result["@attributes"] = dict(element.attrib)

        # Add text content
        if element.text and element.text.strip():
            result["@text"] = element.text.strip()

        # Add children
        for child in element:
            child_dict = self.to_dict(child)
            tag = child.tag

            if tag in result:
                if not isinstance(result[tag], list):
                    result[tag] = [result[tag]]
                result[tag].append(child_dict)
            else:
                result[tag] = child_dict

        return result
