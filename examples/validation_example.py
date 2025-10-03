"""
Example: XML validation
"""

from xmlforge import XMLValidator

# Create a validator
validator = XMLValidator()

# Check if XML is well-formed
xml_valid = """<?xml version="1.0"?>
<root>
    <child>value</child>
</root>
"""

xml_invalid = """<?xml version="1.0"?>
<root>
    <child>value</root>
</root>
"""

print("Checking well-formed XML:")
print(f"Valid XML: {validator.is_well_formed(xml_valid)}")
print(f"Invalid XML: {validator.is_well_formed(xml_invalid)}")

# Example of XSD validation (requires actual XSD file)
# try:
#     validator.validate_with_xsd("document.xml", "schema.xsd")
#     print("Document is valid according to schema!")
# except ValidationError as e:
#     print(f"Validation error: {e}")
