"""
XML Transformer module for transforming XML documents.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

from lxml import etree


class XMLTransformer:
    """
    A class for transforming XML documents using XSLT or custom transformations.

    Attributes:
        xslt_file (Optional[Path]): Path to XSLT stylesheet if provided.
        transform (Optional[etree.XSLT]): Compiled XSLT transformation.
    """

    def __init__(self, xslt_file: Optional[Union[str, Path]] = None) -> None:
        """
        Initialize the XMLTransformer.

        Args:
            xslt_file: Optional path to an XSLT stylesheet file.
        """
        self.xslt_file = Path(xslt_file) if xslt_file else None
        self.transform: Optional[etree.XSLT] = None

        if self.xslt_file:
            self._load_xslt()

    def _load_xslt(self) -> None:
        """
        Load and compile the XSLT stylesheet.

        Raises:
            FileNotFoundError: If the XSLT file does not exist.
        """
        if not self.xslt_file or not self.xslt_file.exists():
            raise FileNotFoundError(f"XSLT file not found: {self.xslt_file}")

        xslt_doc = etree.parse(str(self.xslt_file))
        self.transform = etree.XSLT(xslt_doc)

    def transform_file(
        self,
        input_file: Union[str, Path],
        output_file: Optional[Union[str, Path]] = None,
        **params: str,
    ) -> etree._ElementTree:
        """
        Transform an XML file using the loaded XSLT stylesheet.

        Args:
            input_file: Path to the input XML file.
            output_file: Optional path to write the transformed XML.
            **params: Additional parameters to pass to the XSLT transformation.

        Returns:
            The transformed XML as an ElementTree.

        Raises:
            ValueError: If no XSLT stylesheet is loaded.
            FileNotFoundError: If the input file does not exist.
        """
        if not self.transform:
            raise ValueError("No XSLT stylesheet loaded")

        input_file = Path(input_file)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        doc = etree.parse(str(input_file))
        # Convert string params to proper XSLT parameters
        if params:
            xslt_params = {k: etree.XSLT.strparam(v) for k, v in params.items()}
            result = self.transform(doc, **xslt_params)  # type: ignore[misc]
        else:
            result = self.transform(doc)

        if output_file:
            result.write(str(output_file), encoding="utf-8", xml_declaration=True)

        return result

    def transform_element(self, element: etree._Element, **params: str) -> etree._ElementTree:
        """
        Transform an XML element using the loaded XSLT stylesheet.

        Args:
            element: The XML element to transform.
            **params: Additional parameters to pass to the XSLT transformation.

        Returns:
            The transformed XML as an ElementTree.

        Raises:
            ValueError: If no XSLT stylesheet is loaded.
        """
        if not self.transform:
            raise ValueError("No XSLT stylesheet loaded")

        # Convert string params to proper XSLT parameters
        if params:
            xslt_params = {k: etree.XSLT.strparam(v) for k, v in params.items()}
            return self.transform(element, **xslt_params)  # type: ignore[misc]
        else:
            return self.transform(element)

    def add_namespace(
        self, element: etree._Element, namespace: str, prefix: Optional[str] = None
    ) -> etree._Element:
        """
        Add a namespace to an XML element.

        Args:
            element: The XML element to modify.
            namespace: The namespace URI.
            prefix: Optional namespace prefix.

        Returns:
            The modified element.
        """
        # Handle nsmap - filter out None keys
        nsmap: Dict[str, str] = {}
        if element.nsmap:
            nsmap = {k: v for k, v in element.nsmap.items() if k is not None}
        nsmap[prefix or ''] = namespace

        # Convert attrib to proper string dict
        attrib_dict: Dict[str, str] = {}
        if element.attrib is not None:
            attrib_dict = {str(k): str(v) for k, v in element.attrib.items()}

        new_element = etree.Element(element.tag, nsmap=nsmap, attrib=attrib_dict)
        new_element.text = element.text
        new_element.tail = element.tail

        for child in element:
            new_element.append(child)

        return new_element

    def remove_namespace(self, element: etree._Element) -> etree._Element:
        """
        Remove all namespaces from an XML element and its children.

        Args:
            element: The XML element to modify.

        Returns:
            The modified element without namespaces.
        """
        for elem in element.iter():
            if isinstance(elem.tag, str):
                elem.tag = etree.QName(elem).localname

        etree.cleanup_namespaces(element)
        return element
