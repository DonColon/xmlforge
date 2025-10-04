"""
XML Parser module for parsing XML documents.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from lxml import etree
from xmlforge.dataframe import DataFrameLibrary, DataFrameLike, create_dataframe, get_detector


class EntityParser(ABC):
    """Abstract base class for entity parsers."""

    def __init__(self, dataframe_library: Optional[Union[str, DataFrameLibrary]] = None) -> None:
        """Initialize the EntityParser."""
        super().__init__()

        self.detector = get_detector()

        if dataframe_library is None:
            self.preferred_library = self.detector.get_preferred_library()
        else:
            if isinstance(dataframe_library, str):
                dataframe_library = DataFrameLibrary(dataframe_library)

            self.preferred_library = dataframe_library

    def parse(self, chunk: etree._Element, **kwargs) -> DataFrameLike:
        """Parse the input data and return a structured representation."""
        entities = []

        for element in chunk:
            data = self.parse_entity(element)
            entities.extend(data)

        return create_dataframe(entities, library=self.preferred_library, **kwargs)

    @abstractmethod
    def parse_entity(self, element: etree._Element) -> List[Dict[str, Any]]:
        """Parse a single XML element into a dictionary."""
        pass


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
        self.parser = etree.XMLParser(encoding=self.encoding, remove_blank_text=True)

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

        return etree.parse(str(filepath), self.parser)

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
        return etree.fromstring(xml_string.encode(self.encoding), self.parser)

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
