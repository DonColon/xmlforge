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

    def test_flatten_hierarchy_simple_products(self):
        """Test flattening nested Product elements."""
        transformer = XMLTransformer()

        # Create nested Product structure
        xml_string = """
        <Product id="12345">
            <Name>Sample Product</Name>
            <Price>19.99</Price>
            <Category>Books</Category>
            <Product id="67890">
                <Name>Another Product</Name>
                <Price>29.99</Price>
                <Category>Electronics</Category>
            </Product>
            <Product id="54321">
                <Name>Third Product</Name>
                <Price>9.99</Price>
                <Category>Stationery</Category>
            </Product>
        </Product>
        """

        element = etree.fromstring(xml_string.encode("utf-8"))

        # Flatten the hierarchy
        flattened = transformer.flatten_hierarchy(element, "Product")

        # Should have 3 elements: root + 2 children
        assert len(flattened) == 3

        # Check root element
        root = flattened[0]
        assert root.tag == "Product"
        assert root.get("id") == "12345"
        name_elem = root.find("Name")
        assert name_elem is not None
        assert name_elem.text == "Sample Product"
        # Root should not have nested Product children anymore
        assert len([child for child in root if child.tag == "Product"]) == 0

        # Check flattened children
        child1 = flattened[1]
        assert child1.tag == "Product"
        assert child1.get("id") == "67890"
        assert child1.get("parent_id") == "12345"
        name_elem1 = child1.find("Name")
        assert name_elem1 is not None
        assert name_elem1.text == "Another Product"

        child2 = flattened[2]
        assert child2.tag == "Product"
        assert child2.get("id") == "54321"
        assert child2.get("parent_id") == "12345"
        name_elem2 = child2.find("Name")
        assert name_elem2 is not None
        assert name_elem2.text == "Third Product"

    def test_flatten_hierarchy_deeply_nested(self):
        """Test flattening deeply nested Product elements."""
        transformer = XMLTransformer()

        xml_string = """
        <Product id="1">
            <Name>Level 1</Name>
            <Product id="2">
                <Name>Level 2</Name>
                <Product id="3">
                    <Name>Level 3</Name>
                </Product>
            </Product>
        </Product>
        """

        element = etree.fromstring(xml_string.encode("utf-8"))
        flattened = transformer.flatten_hierarchy(element, "Product")

        # Should have 3 elements: all levels flattened
        assert len(flattened) == 3

        # Check hierarchy is flattened correctly
        root = flattened[0]
        assert root.get("id") == "1"
        assert root.get("parent_id") is None

        # Find level2 and level3 by ID (order may vary due to depth-first processing)
        level2 = None
        level3 = None
        for elem in flattened[1:]:
            if elem.get("id") == "2":
                level2 = elem
            elif elem.get("id") == "3":
                level3 = elem

        assert level2 is not None
        assert level2.get("parent_id") == "1"

        assert level3 is not None
        assert level3.get("parent_id") == "2"

    def test_flatten_hierarchy_mixed_content(self):
        """Test flattening with mixed content (non-target tags preserved)."""
        transformer = XMLTransformer()

        xml_string = """
        <Product id="1">
            <Name>Parent Product</Name>
            <Description>
                <Text>Some description</Text>
            </Description>
            <Product id="2">
                <Name>Child Product</Name>
                <Category>Electronics</Category>
            </Product>
        </Product>
        """

        element = etree.fromstring(xml_string.encode("utf-8"))
        flattened = transformer.flatten_hierarchy(element, "Product")

        assert len(flattened) == 2

        # Root should keep non-Product children
        root = flattened[0]
        name_elem = root.find("Name")
        assert name_elem is not None
        assert name_elem.text == "Parent Product"
        desc_elem = root.find("Description/Text")
        assert desc_elem is not None
        assert desc_elem.text == "Some description"
        # But no nested Product
        assert len([child for child in root if child.tag == "Product"]) == 0

        # Child Product should be flattened
        child = flattened[1]
        assert child.get("id") == "2"
        assert child.get("parent_id") == "1"

    def test_flatten_hierarchy_no_ids_generates_ids(self):
        """Test that missing IDs are automatically generated."""
        transformer = XMLTransformer()

        xml_string = """
        <Product>
            <Name>Parent</Name>
            <Product>
                <Name>Child</Name>
            </Product>
        </Product>
        """

        element = etree.fromstring(xml_string.encode("utf-8"))
        flattened = transformer.flatten_hierarchy(element, "Product")

        assert len(flattened) == 2

        # Both elements should have generated IDs
        root = flattened[0]
        child = flattened[1]

        root_id = root.get("id")
        child_id = child.get("id")

        assert root_id is not None
        assert child_id is not None
        assert len(root_id) == 8  # UUID[:8]
        assert len(child_id) == 8
        assert child.get("parent_id") == root_id

    def test_rebuild_hierarchy_simple_products(self):
        """Test rebuilding flattened Product elements back to hierarchy."""
        transformer = XMLTransformer()

        # Create flattened elements
        root_elem = etree.Element("Product", attrib={"id": "12345"})
        etree.SubElement(root_elem, "Name").text = "Sample Product"
        etree.SubElement(root_elem, "Price").text = "19.99"

        child1_elem = etree.Element("Product", attrib={"id": "67890", "parent_id": "12345"})
        etree.SubElement(child1_elem, "Name").text = "Another Product"
        etree.SubElement(child1_elem, "Price").text = "29.99"

        child2_elem = etree.Element("Product", attrib={"id": "54321", "parent_id": "12345"})
        etree.SubElement(child2_elem, "Name").text = "Third Product"
        etree.SubElement(child2_elem, "Price").text = "9.99"

        flattened = [root_elem, child1_elem, child2_elem]

        # Rebuild hierarchy
        rebuilt = transformer.rebuild_hierarchy(flattened, "Product")

        # Should have one root Product with two nested Products
        assert rebuilt.tag == "root"
        root_products = [child for child in rebuilt if child.tag == "Product"]
        assert len(root_products) == 1

        root_product = root_products[0]
        assert root_product.get("id") == "12345"
        name_elem = root_product.find("Name")
        assert name_elem is not None
        assert name_elem.text == "Sample Product"

        # Check nested products
        nested_products = [child for child in root_product if child.tag == "Product"]
        assert len(nested_products) == 2

        # Verify children are correctly nested
        child_ids = {child.get("id") for child in nested_products}
        assert child_ids == {"67890", "54321"}

    def test_rebuild_hierarchy_deeply_nested(self):
        """Test rebuilding deeply nested hierarchy."""
        transformer = XMLTransformer()

        # Create elements: 1 -> 2 -> 3
        elem1 = etree.Element("Product", attrib={"id": "1"})
        etree.SubElement(elem1, "Name").text = "Level 1"

        elem2 = etree.Element("Product", attrib={"id": "2", "parent_id": "1"})
        etree.SubElement(elem2, "Name").text = "Level 2"

        elem3 = etree.Element("Product", attrib={"id": "3", "parent_id": "2"})
        etree.SubElement(elem3, "Name").text = "Level 3"

        flattened = [elem1, elem2, elem3]
        rebuilt = transformer.rebuild_hierarchy(flattened, "Product")

        # Navigate the rebuilt hierarchy
        root_product = rebuilt.find("Product")
        assert root_product is not None
        assert root_product.get("id") == "1"

        level2 = root_product.find("Product")
        assert level2 is not None
        assert level2.get("id") == "2"

        level3 = level2.find("Product")
        assert level3 is not None
        assert level3.get("id") == "3"

    def test_flatten_and_rebuild_roundtrip(self):
        """Test that flatten -> rebuild produces equivalent structure."""
        transformer = XMLTransformer()

        # Original nested structure
        xml_string = """
        <Product id="root">
            <Name>Root Product</Name>
            <Price>100.00</Price>
            <Product id="child1">
                <Name>Child 1</Name>
                <Price>50.00</Price>
                <Product id="grandchild">
                    <Name>Grandchild</Name>
                    <Price>25.00</Price>
                </Product>
            </Product>
            <Product id="child2">
                <Name>Child 2</Name>
                <Price>75.00</Price>
            </Product>
        </Product>
        """

        original = etree.fromstring(xml_string.encode("utf-8"))

        # Flatten and rebuild
        flattened = transformer.flatten_hierarchy(original, "Product")
        rebuilt = transformer.rebuild_hierarchy(flattened, "Product")

        # Verify structure is preserved
        root_product = rebuilt.find("Product")
        assert root_product is not None
        assert root_product.get("id") == "root"
        name_elem = root_product.find("Name")
        assert name_elem is not None
        assert name_elem.text == "Root Product"

        children = [child for child in root_product if child.tag == "Product"]
        assert len(children) == 2

        # Verify one child has a grandchild
        child_with_grandchild = None
        for child in children:
            if child.find("Product") is not None:
                child_with_grandchild = child
                break

        assert child_with_grandchild is not None
        grandchild = child_with_grandchild.find("Product")
        assert grandchild is not None
        assert grandchild.get("id") == "grandchild"
        gc_name_elem = grandchild.find("Name")
        assert gc_name_elem is not None
        assert gc_name_elem.text == "Grandchild"
