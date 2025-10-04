"""
XML Transformer module for transforming XML documents.
"""

import uuid
from pathlib import Path
from typing import Dict, List, Optional, Union

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

    def transform_file_with_xslt(
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
            result = self.transform(doc, **xslt_params)  # type: ignore[arg-type]
        else:
            result = self.transform(doc)

        if output_file:
            result.write(str(output_file), encoding="utf-8", xml_declaration=True)

        return result

    def transform_element_with_xslt(
        self, element: etree._Element, **params: str
    ) -> etree._ElementTree:
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
            return self.transform(element, **xslt_params)  # type: ignore[arg-type]
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
        nsmap[prefix or ""] = namespace

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

    def flatten_hierarchy(
        self,
        element: etree._Element,
        target_tag: str,
        id_attr: str = "id",
        parent_attr: str = "parent_id",
    ) -> List[etree._Element]:
        """
        Flatten nested elements only when parent and child have the same tag name.
        This is perfect for recursive structures like Product containing Product.

        Args:
            element: The root element to process.
            target_tag: The tag name to flatten (only same-tag nesting).
            id_attr: Attribute name for unique IDs (default: "id").
            parent_attr: Attribute name for parent references (default: "parent_id").

        Returns:
            List of flattened elements with same tag name.
        """
        result = []

        def _flatten_recursive(
            elem: etree._Element, parent_id: Optional[str] = None
        ) -> etree._Element:
            # Generate or use existing ID for target elements
            if elem.tag == target_tag:
                elem_id = elem.get(id_attr)
                if not elem_id:
                    elem_id = str(uuid.uuid4())[:8]
                    elem.set(id_attr, elem_id)
            else:
                elem_id = None

            # Create copy of current element
            attrib_dict = {str(k): str(v) for k, v in elem.attrib.items()}
            new_elem = etree.Element(elem.tag, attrib=attrib_dict)
            new_elem.text = elem.text
            new_elem.tail = elem.tail

            # Set parent reference if this is a target element with a parent
            if parent_id and elem.tag == target_tag:
                new_elem.set(parent_attr, parent_id)

            # Collect children to be flattened (same tag nesting)
            children_to_flatten = []

            # Process children
            for child in elem:
                if child.tag == target_tag and elem.tag == target_tag:
                    # Same tag nesting detected - collect for flattening
                    children_to_flatten.append(child)
                else:
                    # Different tag or not target tag - keep in hierarchy
                    processed_child = _flatten_recursive(
                        child, elem_id if elem.tag == target_tag else parent_id
                    )
                    new_elem.append(processed_child)

            # Process children to flatten in order
            for child in children_to_flatten:
                flattened_child = _flatten_recursive(child, elem_id)
                result.append(flattened_child)

            return new_elem

        # Process root element
        root_copy = _flatten_recursive(element)

        # Return root first, then flattened children in order
        return [root_copy] + result

    def rebuild_hierarchy(
        self,
        elements: List[etree._Element],
        target_tag: str,
        id_attr: str = "id",
        parent_attr: str = "parent_id",
    ) -> etree._Element:
        """
        Rebuild a hierarchical XML structure from a flat list of elements.

        Args:
            elements: List of XML elements to rebuild.
            target_tag: The tag name that was flattened.
            id_attr: Attribute name for unique IDs (default: "id").
            parent_attr: Attribute name for parent references (default: "parent_id").

        Returns:
            The root element of the rebuilt hierarchy.
        """
        elem_dict = {elem.get(id_attr): elem for elem in elements if elem.get(id_attr)}
        root = None

        for elem in elements:
            parent_id = elem.get(parent_attr)
            if parent_id and parent_id in elem_dict:
                parent_elem = elem_dict[parent_id]
                parent_elem.append(elem)
            elif not parent_id and elem.tag == target_tag:
                # This is a top-level element
                if root is None:
                    root = etree.Element("root")
                root.append(elem)

        if root is None:
            raise ValueError("No top-level element found to serve as root.")

        return root
