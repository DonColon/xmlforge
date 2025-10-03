"""
Example: Namespace handling
"""

from lxml import etree

from xmlforge import XMLTransformer

transformer = XMLTransformer()

# XML with namespace
xml_with_ns = """<?xml version="1.0"?>
<root xmlns="http://example.com/namespace">
    <child>value</child>
</root>
"""

# Parse XML
element = etree.fromstring(xml_with_ns.encode("utf-8"))

print("Original element tag:", element.tag)
print("Original child tag:", element[0].tag)

# Remove namespace
clean_element = transformer.remove_namespace(element)

print("\nAfter removing namespace:")
print("Element tag:", clean_element.tag)
print("Child tag:", clean_element[0].tag)

# Pretty print the result
result = etree.tostring(clean_element, pretty_print=True, encoding="unicode")
print("\nCleaned XML:")
print(result)
